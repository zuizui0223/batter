"""Conservative source-join gate for an empirical higher-dimensional bat SDM.

False means UNVERIFIED, not ecological absence. No source data fetched here.
Eligibility requires *the same* population and event-level spatial-temporal
join, independently measured resource supply, height, behavior and effort.
"""
from __future__ import annotations
import json
from pathlib import Path

FIELDS = (
    ("same_population", "STOP_STUDY_POPULATION_MISMATCH"),
    ("original_bat_rows_authenticated_and_opened", "STOP_SOURCE_BYTES_UNVERIFIED"),
    ("verified_same_event_join", "STOP_NO_EVENT_LEVEL_JOIN"),
    ("vertical_height_verified", "STOP_NO_VERIFIED_HEIGHT"),
    ("independent_time_aligned_food_supply", "STOP_NO_INDEPENDENT_FOOD_SUPPLY"),
    ("behavior_label_independent_of_height", "STOP_NO_INDEPENDENT_BEHAVIOR_LABEL"),
    ("observation_sampling_calibrated", "STOP_NO_EFFORT_CALIBRATION"),
)
READY = "READY_TO_PREREGISTER_HELDOUT_FIT_NOT_EVIDENCE_OF_GAIN"


def gate_source(candidate):
    if not isinstance(candidate, dict) or not isinstance(candidate.get("flags"), dict):
        raise ValueError("candidate must provide source metadata flags")
    flags = candidate["flags"]
    if set(flags) != {key for key, _ in FIELDS}:
        raise ValueError("candidate flags must match the frozen schema exactly")
    if any(type(flags[key]) is not bool for key, _ in FIELDS):
        raise TypeError("source flags must be independently verified booleans")
    missing = [reason for key, reason in FIELDS if not flags[key]]
    return {"id": candidate.get("id"), "eligible": not bool(missing),
            "status": READY if not missing else missing[0],
            "all_stop_reasons": missing}


def audit_registry(registry):
    if registry.get("schema") != "batter.resource_behavior_sdm.original_source_join_registry.v2":
        raise ValueError("incorrect source registry version")
    if registry.get("real_joint_3d_resource_effect", "missing") is not None:
        raise ValueError("unfitted ecological outcome must remain null")
    rows = registry.get("sources")
    if not isinstance(rows, list) or not rows:
        raise ValueError("empty source registry")
    ids = [row.get("id") for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate original source candidate")
    decisions = [gate_source(r) for r in rows]
    return {"candidate_count":len(decisions),
            "strict_ready_count":sum(d["eligible"] for d in decisions),
            "decisions":decisions,
            "claimed_ecological_gain":None}


if __name__ == "__main__":
    path = Path(__file__).with_name("source_join_registry_v2.json")
    print(json.dumps(audit_registry(json.loads(path.read_text(encoding="utf-8"))),
                     indent=2, ensure_ascii=False))
