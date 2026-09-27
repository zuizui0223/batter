#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import sys

import numpy as np
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_biological_effect_translation as eff

CONTRACT = Path("contract/effect_translation_null_calibration_v1.json")
MIN_SCORED = 50
AGL_CELL = 5000.0


def load_contract():
    cfg = json.loads(CONTRACT.read_text(encoding="utf-8"))
    return cfg, {p["id"]: p for p in cfg["pairwise_self_win_null"]["panels"]}


def pairwise_session_rows(A, labels):
    counts = A["counts"]
    cell_tot = A["cell_tot"]
    sess_cond = A["sess_cond"]
    S, _C, _K = counts.shape
    L = len(A["label_names"])
    idx = np.arange(S)
    rows = []

    for t in range(S):
        lab = int(labels[t])
        self_sel = np.flatnonzero((labels == lab) & (idx != t))
        if len(self_sel) == 0:
            continue
        p_self = cal.mean_nan_axis0(sess_cond[self_sel])

        pair_rows = []
        for alt in range(L):
            if alt == lab:
                continue
            alt_sel = np.flatnonzero(labels == alt)
            if len(alt_sel) == 0:
                continue
            p_alt = cal.mean_nan_axis0(sess_cond[alt_sel])
            supported = (
                (cell_tot[t] > 0)
                & (~np.isnan(p_self[:, 0]))
                & (~np.isnan(p_alt[:, 0]))
            )
            scored = int(cell_tot[t, supported].sum())
            if scored < MIN_SCORED:
                continue
            supported_idx = np.flatnonzero(supported)
            w = eff.self_weights(cell_tot, self_sel, supported_idx)
            if w is None:
                continue
            m_self = np.sum(
                p_self[supported_idx, :] * w[:, None], axis=0
            )
            m_alt = np.sum(
                p_alt[supported_idx, :] * w[:, None], axis=0
            )
            tz = counts[t, supported, :].sum(axis=0).astype(float)
            gain = float(
                np.sum(tz * (np.log(m_self) - np.log(m_alt))) / scored
            )
            pair_rows.append((gain, float(gain > 0)))

        if pair_rows:
            rows.append(
                {
                    "individual": A["label_names"][lab],
                    "session": A["sessions"][t],
                    "alternatives": len(pair_rows),
                    "win_fraction": float(np.mean([x[1] for x in pair_rows])),
                    "mean_pairwise_gain": float(np.mean([x[0] for x in pair_rows])),
                }
            )
    return rows


def aggregate_pairwise(session_rows):
    per_ind = {}
    for iid in sorted({r["individual"] for r in session_rows}):
        rs = [r for r in session_rows if r["individual"] == iid]
        if not rs:
            continue
        per_ind[iid] = {
            "win_fraction": float(np.mean([r["win_fraction"] for r in rs])),
            "mean_pairwise_gain": float(
                np.mean([r["mean_pairwise_gain"] for r in rs])
            ),
            "evaluable_sessions": len(rs),
        }
    vals = [v["win_fraction"] for v in per_ind.values()]
    return {
        "equal_individual_self_win_fraction": (
            float(np.mean(vals)) if vals else None
        ),
        "evaluable_individuals": len(vals),
        "individual_results": per_ind,
        "session_results": session_rows,
    }


def pairwise_panel(arrays, label_maps=None):
    rows = []
    for cohort, A in sorted(arrays.items()):
        labels = (
            A["orig_labels"]
            if label_maps is None
            else label_maps[cohort]
        )
        rr = pairwise_session_rows(A, labels)
        for r in rr:
            r["cohort"] = cohort
        rows.extend(rr)
    return aggregate_pairwise(rows)


def pairwise_null(panel_id):
    cfg, panels = load_contract()
    spec = panels[panel_id]
    events_by_cohort, k, source = eff.load_panel(panel_id)
    arrays = eff.make_arrays(events_by_cohort, k)

    observed = pairwise_panel(arrays)
    target = float(spec["observed"])
    if abs(observed["equal_individual_self_win_fraction"] - target) > 1e-12:
        raise RuntimeError(
            f"pairwise observed mismatch {panel_id}: "
            f"{observed['equal_individual_self_win_fraction']} != {target}"
        )

    rng = np.random.default_rng(int(spec["seed"]))
    null = []
    null_n = []
    invalid = 0
    for _ in range(int(spec["permutations"])):
        label_maps = {
            cohort: rng.permutation(A["orig_labels"])
            for cohort, A in sorted(arrays.items())
        }
        s = pairwise_panel(arrays, label_maps)
        value = s["equal_individual_self_win_fraction"]
        if value is None:
            invalid += 1
            continue
        null.append(value)
        null_n.append(s["evaluable_individuals"])

    summary = cal.tail_summary(null, target)
    n = np.asarray(null_n, dtype=float)
    payload = {
        "study_id": cfg["study_id"],
        "contract": str(CONTRACT),
        "analysis": "pairwise_self_win_null",
        "panel_id": panel_id,
        "source": source,
        "observed": observed,
        "permutation": {
            "B": int(spec["permutations"]),
            "seed": int(spec["seed"]),
            "source_null": spec["source_null"],
            "calibration": summary,
            "invalid_replicates": invalid,
            "evaluable_individual_count": {
                "observed": observed["evaluable_individuals"],
                "mean": float(n.mean()) if len(n) else None,
                "q025": float(np.quantile(n, 0.025)) if len(n) else None,
                "q50": float(np.quantile(n, 0.5)) if len(n) else None,
                "q975": float(np.quantile(n, 0.975)) if len(n) else None,
            },
        },
        "interpretation": {
            "calibrated_excess_positive": summary["observed_minus_null_mean"] > 0,
            "upper_tail_le_0_05": summary["p_null_ge_observed"] <= 0.05,
            "may_use_as_calibrated_main_text_translation": (
                summary["observed_minus_null_mean"] > 0
                and summary["p_null_ge_observed"] <= 0.05
            ),
            "reference_0_5_is_intuitive_only": True,
        },
    }
    out = Path(f"results/effect_null_pairwise_{panel_id}_v1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "panel": panel_id,
                "observed": target,
                "null": summary,
                "main_text_translation": payload["interpretation"][
                    "may_use_as_calibrated_main_text_translation"
                ],
            },
            sort_keys=True,
        )
    )


def agl_session_data():
    rows = eff.get_tad_rows()
    tr = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
    parsed = []
    session_counts = Counter()
    for row in rows:
        iid = str(row.get("animal-id", "")).strip()
        day = str(row.get("BatDay", "")).strip()
        lon = eff.finite_float(row.get("location-long"))
        lat = eff.finite_float(row.get("location-lat"))
        h = eff.finite_float(row.get("height_true"))
        if not iid or not day or lon is None or lat is None or h is None:
            continue
        x, y = tr.transform(lon, lat)
        sid = f"{iid}::{day}"
        cell = (math.floor(x / AGL_CELL), math.floor(y / AGL_CELL))
        session_counts[sid] += 1
        parsed.append((iid, sid, cell, float(h)))

    retained = {s for s, n in session_counts.items() if n >= 50}
    parsed = [r for r in parsed if r[1] in retained]
    sessions = sorted(retained)
    session_index = {s: i for i, s in enumerate(sessions)}
    label_names = sorted({iid for iid, sid, _c, _h in parsed if sid in retained})
    label_index = {iid: i for i, iid in enumerate(label_names)}
    orig_labels = np.empty(len(sessions), dtype=np.int16)

    cell_counts = []
    cell_sums = []
    cell_means = []
    for sid in sessions:
        sr = [r for r in parsed if r[1] == sid]
        iid = sr[0][0]
        orig_labels[session_index[sid]] = label_index[iid]
        counts = Counter(r[2] for r in sr)
        sums = defaultdict(float)
        for _iid, _sid, cell, h in sr:
            sums[cell] += h
        means = {c: sums[c] / counts[c] for c in counts}
        cell_counts.append(dict(counts))
        cell_sums.append(dict(sums))
        cell_means.append(means)

    return {
        "sessions": sessions,
        "label_names": label_names,
        "orig_labels": orig_labels,
        "cell_counts": cell_counts,
        "cell_sums": cell_sums,
        "cell_means": cell_means,
    }


def pooled_label_cell_mean(D, labels, lab):
    sel = np.flatnonzero(labels == lab)
    sums = defaultdict(float)
    counts = Counter()
    for s in sel:
        for c, value in D["cell_sums"][s].items():
            sums[c] += value
        for c, value in D["cell_counts"][s].items():
            counts[c] += value
    return {c: sums[c] / counts[c] for c in counts if counts[c] > 0}


def agl_separation_eval(D, labels):
    S = len(D["sessions"])
    L = len(D["label_names"])
    idx = np.arange(S)
    label_cell = {
        lab: pooled_label_cell_mean(D, labels, lab)
        for lab in range(L)
    }
    rows = []

    for t in range(S):
        lab = int(labels[t])
        self_sel = np.flatnonzero((labels == lab) & (idx != t))
        if len(self_sel) == 0:
            continue

        self_cells = defaultdict(list)
        for s in self_sel:
            for c, value in D["cell_means"][s].items():
                self_cells[c].append(value)

        other_cells = defaultdict(list)
        for alt in range(L):
            if alt == lab:
                continue
            for c, value in label_cell[alt].items():
                other_cells[c].append(value)

        target_counts = D["cell_counts"][t]
        support = sorted(set(target_counts) & set(self_cells) & set(other_cells))
        scored = sum(target_counts[c] for c in support)
        if scored < MIN_SCORED:
            continue

        weights = []
        for s in self_sel:
            w = np.asarray(
                [D["cell_counts"][s].get(c, 0) for c in support], dtype=float
            )
            if w.sum() > 0:
                weights.append(w / w.sum())
        if not weights:
            continue
        w = np.mean(np.stack(weights), axis=0)
        w = w / w.sum()

        self_cell = np.asarray(
            [np.mean(self_cells[c]) for c in support], dtype=float
        )
        other_cell = np.asarray(
            [np.mean(other_cells[c]) for c in support], dtype=float
        )
        self_exp = float(np.sum(w * self_cell))
        other_exp = float(np.sum(w * other_cell))
        rows.append(
            {
                "individual": D["label_names"][lab],
                "session": D["sessions"][t],
                "absolute_separation_m": abs(self_exp - other_exp),
            }
        )

    per_ind = {}
    for iid in sorted({r["individual"] for r in rows}):
        vals = [r["absolute_separation_m"] for r in rows if r["individual"] == iid]
        if vals:
            per_ind[iid] = float(np.mean(vals))
    values = list(per_ind.values())
    return {
        "equal_individual_mean_absolute_separation_m": (
            float(np.mean(values)) if values else None
        ),
        "median_individual_separation_m": (
            float(np.median(values)) if values else None
        ),
        "evaluable_individuals": len(values),
        "evaluable_sessions": len(rows),
        "individual_results": per_ind,
        "session_results": rows,
    }


def agl_separation_null():
    cfg, _panels = load_contract()
    spec = cfg["tadarida_agl_absolute_separation_null"]
    D = agl_session_data()
    observed = agl_separation_eval(D, D["orig_labels"])
    target = float(spec["observed_mean_absolute_separation_m"])
    if abs(observed["equal_individual_mean_absolute_separation_m"] - target) > 1e-9:
        raise RuntimeError(
            "AGL separation observed mismatch: "
            f"{observed['equal_individual_mean_absolute_separation_m']} != {target}"
        )
    if observed["evaluable_sessions"] != int(spec["evaluable_sessions"]):
        raise RuntimeError(
            f"AGL evaluable session mismatch: {observed['evaluable_sessions']} "
            f"!= {spec['evaluable_sessions']}"
        )

    rng = np.random.default_rng(int(spec["seed"]))
    null = []
    null_n = []
    invalid = 0
    for _ in range(int(spec["permutations"])):
        labels = rng.permutation(D["orig_labels"])
        s = agl_separation_eval(D, labels)
        value = s["equal_individual_mean_absolute_separation_m"]
        if value is None:
            invalid += 1
            continue
        null.append(value)
        null_n.append(s["evaluable_individuals"])

    summary = cal.tail_summary(null, target)
    payload = {
        "study_id": cfg["study_id"],
        "contract": str(CONTRACT),
        "analysis": "tadarida_agl_absolute_separation_null",
        "observed": observed,
        "permutation": {
            "B": int(spec["permutations"]),
            "seed": int(spec["seed"]),
            "calibration": summary,
            "invalid_replicates": invalid,
            "evaluable_individual_counts": {
                "observed": observed["evaluable_individuals"],
                "null_mean": float(np.mean(null_n)) if null_n else None,
            },
        },
        "interpretation": {
            "calibrated_excess_positive": summary["observed_minus_null_mean"] > 0,
            "upper_tail_le_0_05": summary["p_null_ge_observed"] <= 0.05,
            "retain_as_headline_main_text_magnitude": (
                summary["observed_minus_null_mean"] > 0
                and summary["p_null_ge_observed"] <= 0.05
            ),
        },
    }
    out = Path("results/effect_null_tadarida_agl_separation_v1.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "observed": target,
                "null": summary,
                "retain_headline": payload["interpretation"][
                    "retain_as_headline_main_text_magnitude"
                ],
            },
            sort_keys=True,
        )
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["pairwise", "agl-separation"])
    ap.add_argument(
        "--panel",
        choices=[
            "tadarida",
            "eidolon",
            "hypsignathus",
            "phyllostomus_2022",
            "phyllostomus_2023",
            "phyllostomus_2016",
        ],
    )
    args = ap.parse_args()

    if args.mode == "pairwise":
        if not args.panel:
            raise SystemExit("--panel is required for --mode pairwise")
        pairwise_null(args.panel)
    else:
        agl_separation_null()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
