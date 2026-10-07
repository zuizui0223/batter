#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape

CONTRACT = ROOT / "post_freeze_extensions/collective_3d_persistence_preflight/contract_v1.json"
OUT = ROOT / "post_freeze_extensions/collective_3d_persistence_preflight/result_v1.json"


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def median_time(vals):
    xs = sorted(vals)
    n = len(xs)
    if n % 2:
        return xs[n // 2]
    return xs[n // 2 - 1] + (xs[n // 2] - xs[n // 2 - 1]) / 2


def session_table(panel, c):
    records, source = shape.panel_raw(panel)
    grid = float(c["shared_preprocessing"]["horizontal_grid_m"])
    min_fixes = int(c["shared_preprocessing"]["session_min_fixes"])

    by = defaultdict(list)
    for r in records:
        by[(r["cohort"], r["session"], r["iid"])].append(r)

    sessions = []
    for (cohort, sid, iid), vals in sorted(by.items()):
        if len(vals) < min_fixes:
            continue
        mt = median_time([r["t"] for r in vals])
        cell_counts = Counter(
            (math.floor(r["x"] / grid), math.floor(r["y"] / grid))
            for r in vals
        )
        night = (mt - timedelta(hours=12)).date().isoformat()
        sessions.append({
            "cohort": cohort,
            "session": sid,
            "individual": iid,
            "n": len(vals),
            "mid_time": mt,
            "night": night,
            "cell_counts": cell_counts,
        })
    return sessions, source


def common_support_count(target, histories):
    if not histories:
        return 0
    hcells = set()
    for h in histories:
        hcells.update(h["cell_counts"])
    return int(sum(n for cell, n in target["cell_counts"].items() if cell in hcells))


def predictive_lane(sessions, c):
    lag = timedelta(days=float(c["shared_preprocessing"]["minimum_temporal_separation_days"]))
    min_other = int(c["lane_B_cross_individual_prediction"]["minimum_other_history_individuals"])
    min_scored = int(c["lane_B_cross_individual_prediction"]["target_common_horizontal_support_min_fixes"])

    rows = []
    for t in sessions:
        cutoff = t["mid_time"] - lag
        prior = [
            s for s in sessions
            if s["cohort"] == t["cohort"] and s["mid_time"] <= cutoff
        ]
        self_hist = [s for s in prior if s["individual"] == t["individual"]]
        other_hist = [s for s in prior if s["individual"] != t["individual"]]
        other_ids = sorted({s["individual"] for s in other_hist})
        if not self_hist or len(other_ids) < min_other:
            continue

        self_cells = set().union(*(set(s["cell_counts"]) for s in self_hist))
        other_cells = set().union(*(set(s["cell_counts"]) for s in other_hist))
        common_cells = self_cells & other_cells
        scored = int(sum(n for cell, n in t["cell_counts"].items() if cell in common_cells))
        if scored < min_scored:
            continue

        rows.append({
            "cohort": t["cohort"],
            "session": t["session"],
            "individual": t["individual"],
            "night": t["night"],
            "target_fixes": t["n"],
            "common_support_target_fixes": scored,
            "prior_self_sessions": len(self_hist),
            "prior_other_individuals": len(other_ids),
            "prior_other_sessions": len(other_hist),
            "earliest_self_lag_days": min(
                (t["mid_time"] - s["mid_time"]).total_seconds() / 86400.0
                for s in self_hist
            ),
        })

    ids = sorted({r["individual"] for r in rows})
    min_ids = int(c["lane_B_cross_individual_prediction"]["panel_gate_minimum_evaluable_target_individuals"])
    return {
        "evaluable_target_sessions": len(rows),
        "evaluable_target_individuals": len(ids),
        "individuals": ids,
        "cohorts": sorted({r["cohort"] for r in rows}),
        "gate_pass": len(ids) >= min_ids,
        "session_rows": rows,
    }


def pooled_nights(sessions, c):
    min_ind = int(c["lane_A_natural_turnover"]["night_min_individuals"])
    by = defaultdict(list)
    for s in sessions:
        by[(s["cohort"], s["night"])].append(s)

    out = []
    for (cohort, night), ss in sorted(by.items()):
        ids = sorted({s["individual"] for s in ss})
        if len(ids) < min_ind:
            continue
        counts = Counter()
        for s in ss:
            counts.update(s["cell_counts"])
        mt = median_time([s["mid_time"] for s in ss])
        out.append({
            "cohort": cohort,
            "night": night,
            "mid_time": mt,
            "individuals": ids,
            "cell_counts": counts,
            "fixes": int(sum(counts.values())),
        })
    return out


def turnover_lane(sessions, c):
    nights = pooled_nights(sessions, c)
    lag = timedelta(days=float(c["shared_preprocessing"]["minimum_temporal_separation_days"]))
    min_common = int(c["lane_A_natural_turnover"]["pair_common_horizontal_support_min_fixes_each"])
    pairs = []

    by_cohort = defaultdict(list)
    for n in nights:
        by_cohort[n["cohort"]].append(n)

    for cohort, ns in sorted(by_cohort.items()):
        ns = sorted(ns, key=lambda x: x["mid_time"])
        for i, a in enumerate(ns):
            for b in ns[i + 1:]:
                if b["mid_time"] - a["mid_time"] < lag:
                    continue
                if set(a["individuals"]) & set(b["individuals"]):
                    continue
                common = set(a["cell_counts"]) & set(b["cell_counts"])
                fa = int(sum(a["cell_counts"][x] for x in common))
                fb = int(sum(b["cell_counts"][x] for x in common))
                if fa < min_common or fb < min_common:
                    continue
                pairs.append({
                    "cohort": cohort,
                    "night_a": a["night"],
                    "night_b": b["night"],
                    "lag_days": (b["mid_time"] - a["mid_time"]).total_seconds() / 86400.0,
                    "individuals_a": a["individuals"],
                    "individuals_b": b["individuals"],
                    "shared_horizontal_cells": len(common),
                    "common_support_fixes_a": fa,
                    "common_support_fixes_b": fb,
                })

    unique_nights = sorted({(r["cohort"], r["night_a"]) for r in pairs} | {(r["cohort"], r["night_b"]) for r in pairs})
    gate = c["lane_A_natural_turnover"]["panel_gate"]
    passed = (
        len(pairs) >= int(gate["minimum_eligible_night_pairs"])
        and len(unique_nights) >= int(gate["minimum_unique_nights_participating"])
    )
    return {
        "eligible_multiindividual_nights": len(nights),
        "eligible_zero_identity_overlap_night_pairs": len(pairs),
        "unique_nights_in_eligible_pairs": len(unique_nights),
        "cohorts_with_eligible_pairs": sorted({r["cohort"] for r in pairs}),
        "gate_pass": passed,
        "pair_rows": pairs,
        "night_membership": [
            {
                "cohort": n["cohort"],
                "night": n["night"],
                "individuals": n["individuals"],
                "fixes": n["fixes"],
            }
            for n in nights
        ],
    }


def run_panel(panel, c):
    sessions, source = session_table(panel, c)
    pred = predictive_lane(sessions, c)
    turn = turnover_lane(sessions, c)
    return {
        "panel": panel,
        "source": source,
        "eligible_sessions": len(sessions),
        "eligible_individuals": len({s["individual"] for s in sessions}),
        "cohorts": sorted({s["cohort"] for s in sessions}),
        "lane_A_natural_turnover": turn,
        "lane_B_cross_individual_prediction": pred,
    }


def main():
    c = load_contract()
    panels = {p: run_panel(p, c) for p in c["source_universe"]}
    payload = {
        "schema_version": 1,
        "study_id": c["study_id"],
        "preflight_only": True,
        "collective_3d_outcome_opened": False,
        "panels": panels,
        "summary": {
            "lane_A_pass_panels": [p for p, v in panels.items() if v["lane_A_natural_turnover"]["gate_pass"]],
            "lane_B_pass_panels": [p for p, v in panels.items() if v["lane_B_cross_individual_prediction"]["gate_pass"]],
        },
        "claim_boundary": c["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "lane_A_pass_panels": payload["summary"]["lane_A_pass_panels"],
        "lane_B_pass_panels": payload["summary"]["lane_B_pass_panels"],
        "panels": {
            p: {
                "A_pairs": v["lane_A_natural_turnover"]["eligible_zero_identity_overlap_night_pairs"],
                "A_unique_nights": v["lane_A_natural_turnover"]["unique_nights_in_eligible_pairs"],
                "A_pass": v["lane_A_natural_turnover"]["gate_pass"],
                "B_target_sessions": v["lane_B_cross_individual_prediction"]["evaluable_target_sessions"],
                "B_target_individuals": v["lane_B_cross_individual_prediction"]["evaluable_target_individuals"],
                "B_pass": v["lane_B_cross_individual_prediction"]["gate_pass"],
            }
            for p, v in panels.items()
        }
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
