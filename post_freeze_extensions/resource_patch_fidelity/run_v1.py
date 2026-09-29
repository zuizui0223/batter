#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape
CONTRACT = ROOT / "post_freeze_extensions/resource_patch_fidelity/contract_v1.json"
OUT_JSON = ROOT / "post_freeze_extensions/resource_patch_fidelity/result_v1.json"
OUT_MD = ROOT / "post_freeze_extensions/resource_patch_fidelity/RESULT_V1.md"
SHAPE_CONTRACT = ROOT / "contract/tag_altitude_bias_audit_v1.json"

PRIMARY_PANELS = [
    "eidolon",
    "hypsignathus",
    "phyllostomus_2022",
    "phyllostomus_2023",
    "phyllostomus_2016",
]
BOUNDARY_PANEL = "tadarida"
CENTERED_K = 10


def rankdata(x):
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    i = 0
    while i < len(x):
        j = i + 1
        while j < len(x) and x[order[j]] == x[order[i]]:
            j += 1
        rank = 0.5 * ((i + 1) + j)
        ranks[order[i:j]] = rank
        i = j
    return ranks


def spearman(x, y):
    x = rankdata(x)
    y = rankdata(y)
    x = x - x.mean()
    y = y - y.mean()
    den = math.sqrt(float(np.dot(x, x) * np.dot(y, y)))
    if den <= 0:
        return None
    return float(np.dot(x, y) / den)


def schoener(p, q):
    keys = set(p) | set(q)
    return 1.0 - 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def session_patch_profiles(records, fine_grid_m):
    by = defaultdict(list)
    for r in records:
        by[(r["cohort"], r["session"])].append(r)

    profiles = {}
    meta = {}
    for (cohort, session), rows in by.items():
        iid = rows[0]["iid"]
        coarse_counts = defaultdict(lambda: defaultdict(int))
        for r in rows:
            coarse = (math.floor(r["x"] / 5000.0), math.floor(r["y"] / 5000.0))
            fine = (math.floor(r["x"] / fine_grid_m), math.floor(r["y"] / fine_grid_m))
            coarse_counts[coarse][fine] += 1
        cond = {}
        for coarse, counts in coarse_counts.items():
            total = float(sum(counts.values()))
            if total > 0:
                cond[coarse] = {k: v / total for k, v in counts.items()}
        profiles[(cohort, session)] = cond
        meta[(cohort, session)] = iid
    return profiles, meta


def pair_similarity(a, b):
    common = sorted(set(a) & set(b))
    if not common:
        return None
    vals = [schoener(a[c], b[c]) for c in common]
    return float(np.mean(vals)) if vals else None


def patch_fidelity(records, fine_grid_m):
    profiles, meta = session_patch_profiles(records, fine_grid_m)
    sessions_by = defaultdict(list)
    individuals_by_cohort = defaultdict(set)
    for key, iid in meta.items():
        cohort, session = key
        sessions_by[(cohort, iid)].append((cohort, session))
        individuals_by_cohort[cohort].add(iid)

    cohort_rows = []
    per_ind_cohort = defaultdict(list)
    for (cohort, iid), sessions in sorted(sessions_by.items()):
        sessions = sorted(sessions)
        if len(sessions) < 2:
            continue

        self_vals = []
        for a, b in itertools.combinations(sessions, 2):
            v = pair_similarity(profiles[a], profiles[b])
            if v is not None:
                self_vals.append(v)
        if not self_vals:
            continue
        self_sim = float(np.mean(self_vals))

        other_by_ind = []
        for other in sorted(individuals_by_cohort[cohort] - {iid}):
            other_sessions = sorted(sessions_by.get((cohort, other), []))
            vals = []
            for a in sessions:
                for b in other_sessions:
                    v = pair_similarity(profiles[a], profiles[b])
                    if v is not None:
                        vals.append(v)
            if vals:
                other_by_ind.append(float(np.mean(vals)))
        if not other_by_ind:
            continue
        other_sim = float(np.mean(other_by_ind))
        row = {
            "cohort": cohort,
            "individual": iid,
            "session_count": len(sessions),
            "self_similarity": self_sim,
            "other_similarity": other_sim,
            "patch_fidelity_excess": self_sim - other_sim,
            "self_pair_count": len(self_vals),
            "other_individual_count": len(other_by_ind),
        }
        cohort_rows.append(row)
        per_ind_cohort[iid].append(row)

    per_ind = {}
    for iid, rows in sorted(per_ind_cohort.items()):
        per_ind[iid] = {
            "eligible_cohorts": len(rows),
            "self_similarity": float(np.mean([r["self_similarity"] for r in rows])),
            "other_similarity": float(np.mean([r["other_similarity"] for r in rows])),
            "patch_fidelity_excess": float(np.mean([r["patch_fidelity_excess"] for r in rows])),
        }
    return per_ind, cohort_rows


def original_target_map(arrays):
    out = {}
    for cohort, A in arrays.items():
        for idx, session in enumerate(A["sessions"]):
            lab = int(A["orig_labels"][idx])
            out[(cohort, session)] = A["label_names"][lab]
    return out


def per_original_target(rows, target_map, metric="common_cell_marginal"):
    by = defaultdict(list)
    for r in rows:
        iid = target_map[(r["cohort"], r["session"])]
        by[iid].append(float(r[metric]))
    return {iid: float(np.mean(vals)) for iid, vals in sorted(by.items()) if vals}


def centered_identity(panel, records, B, seed):
    events_by_cohort, _ = shape.centered_events(records)
    arrays = {c: cal.make_cohort_arrays(e, CENTERED_K) for c, e in sorted(events_by_cohort.items())}
    target_map = original_target_map(arrays)

    observed_rows = []
    for cohort, A in arrays.items():
        observed_rows.extend(cal.eval_cohort(A, A["orig_labels"], cohort))
    observed = per_original_target(observed_rows, target_map)

    sums = defaultdict(float)
    sums2 = defaultdict(float)
    counts = defaultdict(int)
    rng = np.random.default_rng(int(seed))

    for _ in range(int(B)):
        rows = []
        for cohort, A in arrays.items():
            labels = rng.permutation(A["orig_labels"])
            rows.extend(cal.eval_cohort(A, labels, cohort))
        cur = per_original_target(rows, target_map)
        for iid, value in cur.items():
            sums[iid] += value
            sums2[iid] += value * value
            counts[iid] += 1

    out = {}
    for iid, obs in sorted(observed.items()):
        n = counts[iid]
        if n == 0:
            continue
        mean = sums[iid] / n
        var = (sums2[iid] - n * mean * mean) / (n - 1) if n > 1 else 0.0
        out[iid] = {
            "observed_common_cell_centered_identity": obs,
            "null_valid_replicates": n,
            "null_mean": mean,
            "null_sd": math.sqrt(max(var, 0.0)),
            "calibrated_centered_identity": obs - mean,
        }
    return out


def panel_dataset(panel, fine_grid_m, shape_settings):
    records, source = shape.panel_raw(panel)
    patch, patch_rows = patch_fidelity(records, fine_grid_m)
    setting = shape_settings[panel]
    vert = centered_identity(panel, records, int(setting["B"]), int(setting["seed"]))

    ids = sorted(set(patch) & set(vert))
    rows = []
    for iid in ids:
        rows.append({
            "individual": iid,
            **patch[iid],
            **vert[iid],
        })
    if len(rows) < 2:
        rho = None
    else:
        rho = spearman(
            [r["patch_fidelity_excess"] for r in rows],
            [r["calibrated_centered_identity"] for r in rows],
        )
    return {
        "panel": panel,
        "fine_grid_m": fine_grid_m,
        "source": source,
        "n_matched_individuals": len(rows),
        "spearman_rho": rho,
        "individuals": rows,
        "cohort_patch_rows": patch_rows,
    }


def stratified_permutation(panel_results, B, seed):
    prepared = []
    panel_rhos = {}
    for panel, res in panel_results.items():
        rows = res["individuals"]
        x = np.asarray([r["patch_fidelity_excess"] for r in rows], dtype=float)
        y = np.asarray([r["calibrated_centered_identity"] for r in rows], dtype=float)
        if len(x) < 5:
            raise RuntimeError(f"{panel}: only {len(x)} matched individuals; primary requires >=5")
        xr = rankdata(x)
        yr = rankdata(y)
        xc = xr - xr.mean()
        yc = yr - yr.mean()
        den = math.sqrt(float(np.dot(xc, xc) * np.dot(yc, yc)))
        if den <= 0:
            raise RuntimeError(f"{panel}: zero rank variance")
        rho = float(np.dot(xc, yc) / den)
        panel_rhos[panel] = rho
        prepared.append((panel, xc, yc, den))

    obs = float(np.mean(list(panel_rhos.values())))
    rng = np.random.default_rng(int(seed))
    ge = 0
    null_sum = 0.0
    null_sum2 = 0.0
    batch = 1000
    done = 0
    while done < int(B):
        n_batch = min(batch, int(B) - done)
        stats = np.zeros(n_batch, dtype=float)
        for _, xc, yc, den in prepared:
            n = len(yc)
            perms = np.empty((n_batch, n), dtype=int)
            for i in range(n_batch):
                perms[i] = rng.permutation(n)
            stats += np.sum(xc[None, :] * yc[perms], axis=1) / den
        stats /= len(prepared)
        ge += int(np.sum(stats >= obs - 1e-15))
        null_sum += float(stats.sum())
        null_sum2 += float(np.dot(stats, stats))
        done += n_batch

    mean = null_sum / B
    var = (null_sum2 - B * mean * mean) / (B - 1) if B > 1 else 0.0
    return {
        "panel_rhos": panel_rhos,
        "observed_equal_panel_mean_rho": obs,
        "B": int(B),
        "seed": int(seed),
        "null_mean": mean,
        "null_sd": math.sqrt(max(var, 0.0)),
        "one_sided_p": (1 + ge) / (B + 1),
        "positive_panel_count": int(sum(v > 0 for v in panel_rhos.values())),
    }


def analyze_grid(grid, shape_settings, assoc_contract):
    panel_results = {
        panel: panel_dataset(panel, grid, shape_settings)
        for panel in PRIMARY_PANELS
    }
    assoc = stratified_permutation(
        panel_results,
        int(assoc_contract["B"]),
        int(assoc_contract["seed"]) + int(grid),
    )
    return panel_results, assoc


def markdown(payload):
    p = payload["primary"]
    a = p["association"]
    verdict = p["verdict"]
    lines = [
        "# Resource-patch fidelity mechanism test v1",
        "",
        "## Status",
        "",
        "**POST-FREEZE EXPLORATORY MECHANISM TEST. This result does not alter the frozen v0.3.8 submission claim set.**",
        "",
        "## Primary prediction",
        "",
        "If persistent reuse of individually characteristic fine-scale movement/resource patches contributes to repeatable vertical organization, individuals with stronger x-y-only patch-fidelity excess should have stronger individually null-calibrated centered vertical identity.",
        "",
        "The x-y proxy is conditioned pairwise on shared 5-km cells; its primary fine grid is 1 km. It is a movement-patch proxy, not a direct measure of food resources.",
        "",
        "## Primary result",
        "",
        f"- equal-panel mean Spearman rho: **{a['observed_equal_panel_mean_rho']:+.3f}**",
        f"- stratified one-sided permutation p: **{a['one_sided_p']:.5f}**",
        f"- panels with positive rho: **{a['positive_panel_count']}/5**",
        f"- frozen support verdict: **{'PASS' if verdict['pass'] else 'FAIL'}**",
        "",
        "| panel | n | Spearman rho |",
        "|---|---:|---:|",
    ]
    for panel in PRIMARY_PANELS:
        res = p["panels"][panel]
        lines.append(f"| {panel} | {res['n_matched_individuals']} | {res['spearman_rho']:+.3f} |")
    lines += [
        "",
        "## Interpretation boundary",
        "",
        payload["interpretation"],
        "",
        "Sensitivity grids (500 m and 2 km) are reported in the JSON result and cannot replace the frozen 1-km primary result.",
        "",
    ]
    return "\n".join(lines)


def main():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    shape_contract = json.loads(SHAPE_CONTRACT.read_text(encoding="utf-8"))
    shape_settings = {
        x["panel"]: x for x in shape_contract["primary_shift_invariant_shape_test"]["permutation"]["settings"]
    }

    primary_grid = int(contract["exposure"]["primary_fine_grid_m"])
    panels, assoc = analyze_grid(primary_grid, shape_settings, contract["primary_association"])
    rule = contract["primary_association"]["support_rule"]
    verdict = {
        "mean_rho_positive": assoc["observed_equal_panel_mean_rho"] > 0,
        "one_sided_p_le_0_05": assoc["one_sided_p"] <= float(rule["one_sided_p_max"]),
        "positive_panel_count_met": assoc["positive_panel_count"] >= int(rule["minimum_panels_with_positive_rho"]),
    }
    verdict["pass"] = all(verdict.values())

    sensitivity = {}
    for grid in contract["exposure"]["sensitivities_fine_grid_m"]:
        pr, ar = analyze_grid(int(grid), shape_settings, contract["primary_association"])
        sensitivity[str(grid)] = {
            "panels": pr,
            "association": ar,
            "cannot_replace_primary": True,
        }

    # Descriptive boundary comparator only.
    t_records, t_source = shape.panel_raw(BOUNDARY_PANEL)
    t_patch, t_patch_rows = patch_fidelity(t_records, primary_grid)
    t_setting = shape_settings[BOUNDARY_PANEL]
    t_vert = centered_identity(BOUNDARY_PANEL, t_records, int(t_setting["B"]), int(t_setting["seed"]))
    t_ids = sorted(set(t_patch) & set(t_vert))
    t_rows = [{"individual": iid, **t_patch[iid], **t_vert[iid]} for iid in t_ids]
    t_rho = spearman(
        [r["patch_fidelity_excess"] for r in t_rows],
        [r["calibrated_centered_identity"] for r in t_rows],
    ) if len(t_rows) >= 2 else None

    if verdict["pass"]:
        interpretation = contract["interpretation_matrix"]["supported"]
    elif assoc["observed_equal_panel_mean_rho"] < 0:
        interpretation = contract["interpretation_matrix"]["negative"]
    else:
        interpretation = contract["interpretation_matrix"]["unsupported"]

    payload = {
        "schema_version": 1,
        "study_id": contract["study_id"],
        "contract": str(CONTRACT.relative_to(ROOT)),
        "submission_claims_unchanged": True,
        "primary": {
            "fine_grid_m": primary_grid,
            "panels": panels,
            "association": assoc,
            "verdict": verdict,
        },
        "sensitivities": sensitivity,
        "tadarida_descriptive_boundary": {
            "source": t_source,
            "n_matched_individuals": len(t_rows),
            "spearman_rho": t_rho,
            "individuals": t_rows,
            "cohort_patch_rows": t_patch_rows,
            "excluded_from_primary_meta_statistic": True,
        },
        "interpretation": interpretation,
        "claim_boundary": contract["exposure"]["claim_boundary"],
        "stop_rule": contract["stop_rule"],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps({
        "primary_mean_rho": assoc["observed_equal_panel_mean_rho"],
        "primary_p": assoc["one_sided_p"],
        "positive_panels": assoc["positive_panel_count"],
        "primary_pass": verdict["pass"],
        "panel_rhos": assoc["panel_rhos"],
        "sensitivity_mean_rho": {
            k: v["association"]["observed_equal_panel_mean_rho"] for k, v in sensitivity.items()
        },
        "tadarida_rho_descriptive": t_rho,
    }, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
