#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape

CFG = Path("post_freeze_extensions/3d_niche_partition/contract_v1.json")
OUTDIR = Path("post_freeze_extensions/3d_niche_partition/results")

METRICS = ("oxy", "oxyz", "ozxy", "l3d", "r3d")


def load_cfg():
    return json.loads(CFG.read_text(encoding="utf-8"))


def exact_centered_audit_sessions(panel, records):
    events_by_cohort, _ = shape.centered_events(records)
    k = len(shape.EDGES) - 1
    arrays = {c: cal.make_cohort_arrays(e, k) for c, e in sorted(events_by_cohort.items())}
    _, _, rows = cal.observed_eval(arrays)
    return {(r["cohort"], r["session"], r["individual"]) for r in rows}


def build_session_distributions(panel):
    cfg = load_cfg()
    cell = float(cfg["preprocessing"]["horizontal_grid_m"])
    alpha = float(cfg["preprocessing"]["alpha"])
    edges = tuple(
        -math.inf if x == "-inf" else math.inf if x == "inf" else float(x)
        for x in cfg["preprocessing"]["centered_height_edges_m"]
    )
    k = len(edges) - 1

    records, source = shape.panel_raw(panel)
    allowed = exact_centered_audit_sessions(panel, records)

    by_session = defaultdict(list)
    for r in records:
        key = (r["cohort"], r["session"], r["iid"])
        if key in allowed:
            by_session[key].append(r)

    sessions_by_cohort = defaultdict(list)
    for (cohort, sid, iid), vals in sorted(by_session.items()):
        med = float(np.median([r["h"] for r in vals]))
        counts = defaultdict(lambda: np.zeros(k, dtype=np.int64))
        for r in vals:
            c = (math.floor(r["x"] / cell), math.floor(r["y"] / cell))
            resid = float(r["h"] - med)
            z = shape.z_bin(resid, edges=edges)
            counts[c][z] += 1

        cell_n = {c: int(v.sum()) for c, v in counts.items()}
        total = int(sum(cell_n.values()))
        if total <= 0:
            continue

        pxy = {c: n / total for c, n in cell_n.items()}
        pz = {
            c: (v.astype(float) + alpha) / (float(v.sum()) + alpha * k)
            for c, v in counts.items()
        }
        joint = {c: pxy[c] * pz[c] for c in counts}

        sessions_by_cohort[cohort].append({
            "cohort": cohort,
            "session": sid,
            "individual": iid,
            "n": total,
            "cell_n": cell_n,
            "pxy": pxy,
            "pz": pz,
            "joint": joint,
        })

    for cohort in sessions_by_cohort:
        sessions_by_cohort[cohort].sort(key=lambda s: s["session"])

    got = {
        (s["cohort"], s["session"], s["individual"])
        for ss in sessions_by_cohort.values() for s in ss
    }
    if got != allowed:
        missing = sorted(allowed - got)
        extra = sorted(got - allowed)
        raise RuntimeError(f"{panel}: session reconstruction mismatch missing={missing[:3]} extra={extra[:3]}")

    return dict(sessions_by_cohort), source


def pair_metrics(a, b, min_common):
    common = sorted(set(a["cell_n"]) & set(b["cell_n"]))
    if not common:
        return None
    na = sum(a["cell_n"][c] for c in common)
    nb = sum(b["cell_n"][c] for c in common)
    if na < min_common or nb < min_common:
        return None

    oxy = float(sum(min(a["pxy"][c], b["pxy"][c]) for c in common))
    if oxy <= 0:
        return None

    oxyz = 0.0
    ozxy = 0.0
    for c in common:
        oxyz += float(np.minimum(a["joint"][c], b["joint"][c]).sum())
        w = min(a["pxy"][c], b["pxy"][c]) / oxy
        ozxy += w * float(np.minimum(a["pz"][c], b["pz"][c]).sum())

    l3d = oxy - oxyz
    r3d = 1.0 - (oxyz / oxy)

    return {
        "oxy": oxy,
        "oxyz": float(oxyz),
        "ozxy": float(ozxy),
        "l3d": float(l3d),
        "r3d": float(r3d),
        "shared_cells": len(common),
        "shared_fixes_a": int(na),
        "shared_fixes_b": int(nb),
    }


def pair_cache(sessions, min_common):
    n = len(sessions)
    out = {}
    for i in range(n):
        for j in range(i + 1, n):
            m = pair_metrics(sessions[i], sessions[j], min_common)
            if m is not None:
                out[(i, j)] = m
    return out


def get_pair(cache, i, j):
    if i == j:
        return None
    return cache.get((i, j) if i < j else (j, i))


def eval_cohort(sessions, cache, labels):
    rows = []
    unique_labels = sorted(set(labels))
    for t in range(len(sessions)):
        lab = labels[t]

        self_ms = []
        other_by_label = defaultdict(list)
        for j in range(len(sessions)):
            if j == t:
                continue
            m = get_pair(cache, t, j)
            if m is None:
                continue
            if labels[j] == lab:
                self_ms.append(m)
            else:
                other_by_label[labels[j]].append(m)

        if not self_ms or len(other_by_label) < 2:
            continue

        self_mean = {m: float(np.mean([x[m] for x in self_ms])) for m in METRICS}
        other_label_means = {
            olab: {m: float(np.mean([x[m] for x in xs])) for m in METRICS}
            for olab, xs in other_by_label.items()
        }
        other_mean = {
            m: float(np.mean([x[m] for x in other_label_means.values()]))
            for m in METRICS
        }

        row = {
            "cohort": sessions[t]["cohort"],
            "session": sessions[t]["session"],
            "individual": lab,
            "self_pair_count": len(self_ms),
            "other_individual_count": len(other_by_label),
            "d_ozxy": self_mean["ozxy"] - other_mean["ozxy"],
        }
        for m in METRICS:
            row[f"self_{m}"] = self_mean[m]
            row[f"other_{m}"] = other_mean[m]
            row[f"d_{m}"] = self_mean[m] - other_mean[m]
        rows.append(row)
    return rows


def aggregate_panel(rows):
    per_ind = {}
    for iid in sorted({r["individual"] for r in rows}):
        rs = [r for r in rows if r["individual"] == iid]
        if not rs:
            continue
        d = {
            "evaluable_sessions": len(rs),
            "cohorts": sorted({r["cohort"] for r in rs}),
        }
        for key in ["d_ozxy"] + [
            f"{prefix}_{m}" for prefix in ("self", "other", "d") for m in METRICS
        ]:
            d[key] = float(np.mean([r[key] for r in rs]))
        per_ind[iid] = d

    vals = list(per_ind.values())
    out = {
        "eligible_individuals": len(vals),
        "d_panel": float(np.mean([v["d_ozxy"] for v in vals])) if vals else None,
    }
    for prefix in ("self", "other", "d"):
        for m in METRICS:
            out[f"{prefix}_{m}"] = (
                float(np.mean([v[f"{prefix}_{m}"] for v in vals])) if vals else None
            )
    return out, per_ind


def evaluate(sessions_by_cohort, caches, labels_by_cohort):
    rows = []
    for cohort, sessions in sessions_by_cohort.items():
        rows.extend(eval_cohort(sessions, caches[cohort], labels_by_cohort[cohort]))
    return aggregate_panel(rows) + (rows,)


def descriptive_identity_matrices(sessions_by_cohort, caches):
    result = {}
    between_ozxy = []
    for cohort, sessions in sessions_by_cohort.items():
        ids = sorted({s["individual"] for s in sessions})
        matrices = {m: {} for m in ("oxy", "oxyz", "ozxy")}
        for ia, a in enumerate(ids):
            for b in ids[ia:]:
                vals = {m: [] for m in matrices}
                for i, si in enumerate(sessions):
                    if si["individual"] != a:
                        continue
                    for j, sj in enumerate(sessions):
                        if sj["individual"] != b:
                            continue
                        if a == b and j <= i:
                            continue
                        pm = get_pair(caches[cohort], i, j)
                        if pm is None:
                            continue
                        for m in vals:
                            vals[m].append(pm[m])
                        if a != b:
                            between_ozxy.append(pm["ozxy"])
                key = f"{a}|||{b}"
                for m in matrices:
                    matrices[m][key] = float(np.mean(vals[m])) if vals[m] else None
        result[cohort] = {"individuals": ids, "matrices": matrices}
    return result, between_ozxy


def run(panel):
    cfg = load_cfg()
    if panel not in cfg["source_universe"]:
        raise RuntimeError(f"panel not in fixed source universe: {panel}")

    min_common = int(cfg["preprocessing"]["pair_common_support_min_fixes_each"])
    min_ind = int(cfg["structural_gate"]["panel_min_evaluable_individuals"])
    sessions_by_cohort, source = build_session_distributions(panel)
    caches = {c: pair_cache(s, min_common) for c, s in sessions_by_cohort.items()}

    orig_labels = {
        c: np.array([s["individual"] for s in sessions], dtype=object)
        for c, sessions in sessions_by_cohort.items()
    }
    observed, per_ind, session_rows = evaluate(sessions_by_cohort, caches, orig_labels)
    matrices, between_ozxy = descriptive_identity_matrices(sessions_by_cohort, caches)

    seed = int(cfg["permutation"]["seeds"][panel])
    B = int(cfg["permutation"]["B"])
    rng = np.random.default_rng(seed)
    null = []
    null_n = []
    invalid = 0

    if observed["eligible_individuals"] >= min_ind:
        for _ in range(B):
            perm_labels = {c: rng.permutation(v) for c, v in orig_labels.items()}
            s, _, _ = evaluate(sessions_by_cohort, caches, perm_labels)
            if s["eligible_individuals"] < min_ind or s["d_panel"] is None:
                invalid += 1
                continue
            null.append(float(s["d_panel"]))
            null_n.append(int(s["eligible_individuals"]))

    if observed["eligible_individuals"] >= min_ind and not null:
        raise RuntimeError("no valid permutation replicates")

    calibration = (
        cal.tail_summary(null, float(observed["d_panel"]))
        if observed["eligible_individuals"] >= min_ind else None
    )
    supported = bool(
        calibration is not None
        and calibration["observed_minus_null_mean"] > 0
        and calibration["p_null_ge_observed"] <= 0.05
    )

    payload = {
        "study_id": cfg["study_id"],
        "panel": panel,
        "inferential_class": cfg["inferential_class"],
        "source": source,
        "contract": str(CFG),
        "preprocessing": cfg["preprocessing"],
        "session_counts": {c: len(v) for c, v in sessions_by_cohort.items()},
        "pair_counts": {c: len(caches[c]) for c in caches},
        "observed": {
            **observed,
            "individual_results": per_ind,
            "session_results": session_rows,
            "between_session_ozxy": {
                "n": len(between_ozxy),
                "mean": float(np.mean(between_ozxy)) if between_ozxy else None,
                "q025": float(np.quantile(between_ozxy, 0.025)) if between_ozxy else None,
                "q50": float(np.quantile(between_ozxy, 0.5)) if between_ozxy else None,
                "q975": float(np.quantile(between_ozxy, 0.975)) if between_ozxy else None,
            },
        },
        "individual_overlap_matrices": matrices,
        "permutation": {
            "B_requested": B,
            "seed": seed,
            "valid_replicates": len(null),
            "invalid_replicates": invalid,
            "eligible_individuals_null": {
                "mean": float(np.mean(null_n)) if null_n else None,
                "min": int(np.min(null_n)) if null_n else None,
                "max": int(np.max(null_n)) if null_n else None,
            },
            "primary_d_panel": calibration,
        },
        "decision": {
            "structural_gate_met": observed["eligible_individuals"] >= min_ind,
            "supported": supported,
            "interpretation": (
                "repeatable individual-specific vertical configuration within shared 500-m horizontal space"
                if supported else
                "primary 3D-overlap criterion not supported or structurally non-evaluable"
            ),
        },
        "claim_boundary": cfg["claim_ceiling"],
    }

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = OUTDIR / f"{panel}_result_v1.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "panel": panel,
        "eligible_individuals": observed["eligible_individuals"],
        "d_panel": observed["d_panel"],
        "self_ozxy": observed.get("self_ozxy"),
        "other_ozxy": observed.get("other_ozxy"),
        "self_oxy": observed.get("self_oxy"),
        "other_oxy": observed.get("other_oxy"),
        "self_oxyz": observed.get("self_oxyz"),
        "other_oxyz": observed.get("other_oxyz"),
        "calibrated_excess": calibration["observed_minus_null_mean"] if calibration else None,
        "p_upper": calibration["p_null_ge_observed"] if calibration else None,
        "supported": supported,
    }, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", required=True)
    args = ap.parse_args()
    run(args.panel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
