"""Source-free, outcome-blind input-support audit for field bat/resource joins.

The caller must provide ORIGINAL-SOURCE-NORMALIZED tables and separate evidence
for their provenance. This module does not authenticate the tables, estimate a
model, compute causal effects, or read GPS heights. It reports only safe totals.

Stage A: independent plant layout and coverage. Stage B: direct same-night
observed full-layout flower census (strict sub-design), not statistical flower
imputation. Partial random surveys need a separate prespecified estimand.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
import json
from typing import Mapping, Sequence


FORBIDDEN_GPS_KEYS = frozenset({
    "height", "altitude", "agl", "z", "height_m", "altitude_m",
    "recorded_agl_m", "visit", "visited", "cactus_visit",
    "foraging_label", "core_cactus", "target_relative_z",
})


def _string(row: Mapping, key: str) -> str:
    x = row.get(key)
    if not isinstance(x, str) or not x.strip():
        raise ValueError("STOP_MISSING_OR_INVALID_" + key.upper())
    return x.strip()


def _night(row: Mapping) -> str:
    s = _string(row, "night")
    try:
        if date.fromisoformat(s).isoformat() != s:
            raise ValueError()
    except ValueError:
        raise ValueError("STOP_NIGHT_NOT_EXACT_ISO_DATE") from None
    return s


def audit_support(
    gps_height_blind_rows: Sequence[Mapping],
    cactus_layout_rows: Sequence[Mapping],
    field_coverage_rows: Sequence[Mapping],
    dated_flower_rows: Sequence[Mapping],
) -> dict:
    """Audit exact joins without seeing height, visit labels or spatial raw IDs.

    Normalized inputs are NOT themselves proof of publication source identity.
    Fields must be assigned using a documented *independent* survey polygon;
    any downstream model must independently verify that provenance, bat GPS
    altitude datum/error, survey sampling and availability definition.
    """
    if not gps_height_blind_rows or not cactus_layout_rows or not field_coverage_rows:
        raise ValueError("STOP_MISSING_TRACK_LAYOUT_OR_COVERAGE")
    coverage = set()
    for row in field_coverage_rows:
        fid = _string(row, "field")
        area = row.get("surveyed_area_m2")
        if (isinstance(area, bool) or not isinstance(area, (int, float))
                or not 0 < area < float("inf")):
            raise ValueError("STOP_MISSING_INDEPENDENT_SURVEY_AREA")
        # Schema-level evidence only; original method independent audit remains required.
        if row.get("independent_field_polygon") is not True:
            raise ValueError("STOP_FIELD_SUPPORT_NOT_INDEPENDENTLY_DECLARED")
        if fid in coverage:
            raise ValueError("STOP_DUPLICATE_FIELD_COVERAGE")
        coverage.add(fid)

    cactus_to_field = {}
    cacti_by_field = defaultdict(set)
    for row in cactus_layout_rows:
        cid, fid = _string(row, "cactus"), _string(row, "field")
        if cid in cactus_to_field:
            raise ValueError("STOP_DUPLICATE_CACTUS_LAYOUT")
        if fid not in coverage:
            raise ValueError("STOP_CACTUS_OUTSIDE_DECLARED_COVERAGE")
        cactus_to_field[cid] = fid
        cacti_by_field[fid].add(cid)

    gps = []
    for row in gps_height_blind_rows:
        if set(map(str.lower, row)) & FORBIDDEN_GPS_KEYS:
            raise ValueError("STOP_ALTITUDE_OR_HEIGHT_DERIVED_VISIT_LEAKAGE")
        bat, night, fid = _string(row, "bat"), _night(row), _string(row, "field")
        gps.append((bat, night, fid))

    flower_by_field_night = defaultdict(set)
    seen_flower_keys = set()
    for row in dated_flower_rows:
        cid, night = _string(row, "cactus"), _night(row)
        if cid not in cactus_to_field:
            raise ValueError("STOP_FLOWER_CACTUS_NOT_IN_ORIGINAL_LAYOUT")
        key = (cid, night)
        if key in seen_flower_keys:
            raise ValueError("STOP_DUPLICATE_CACTUS_NIGHT_CENSUS")
        seen_flower_keys.add(key)
        count, effort = row.get("open_flowers"), row.get("survey_effort")
        if (isinstance(count, bool) or not isinstance(count, int) or count < 0
                or isinstance(effort, bool) or not isinstance(effort, int) or effort <= 0):
            raise ValueError("STOP_UNOBSERVED_OR_NONINTEGER_FLOWER_COUNTS")
        if row.get("direct_observation") is not True or row.get("simulated") is not False:
            raise ValueError("STOP_SIMULATED_OR_UNVERIFIED_FLOWER_CENSUS")
        flower_by_field_night[(cactus_to_field[cid], night)].add(cid)

    full = {
        key for key, observed in flower_by_field_night.items()
        if observed == cacti_by_field[key[0]] and observed
    }
    a_rows = [(bat, night, f) for bat, night, f in gps if f in cacti_by_field]
    b_rows = [(bat, night, f) for bat, night, f in a_rows if (f, night) in full]
    a_batnights = {(b, n) for b, n, _ in a_rows}
    b_batnights = {(b, n) for b, n, _ in b_rows}
    relevant_fieldnights = {(f, n) for _, n, f in a_rows}
    missing_cactus_night_cells = sum(
        len(cacti_by_field[f] - flower_by_field_night.get((f, n), set()))
        for f, n in relevant_fieldnights
    )

    return {
        "schema": "batter.fruit_flower_source_support_gate.v1",
        "status": "OUTCOME_BLIND_SCHEMA_COVERAGE_ONLY_NOT_ORIGINAL_SOURCE_AUTHENTICATION",
        "n_input_gps_records": len(gps),
        "n_input_independent_layout_cacti": len(cactus_to_field),
        "n_input_survey_fields": len(coverage),
        "n_input_direct_cactus_night_counts": len(seen_flower_keys),
        "stage_a": {
            "estimand": "static mapped cactus opportunity, NOT observed flower quantity",
            "n_eligible_gps_records": len(a_rows),
            "n_eligible_bat_nights": len(a_batnights),
            "n_eligible_bats": len({r[0] for r in a_rows}),
            "n_eligible_fields": len({r[2] for r in a_rows}),
            "potential_only": bool(a_rows),
        },
        "stage_b_strict_full_field_night_census": {
            "estimand": "independently observed same-night flower counts for ALL mapped cacti in field",
            "n_eligible_gps_records": len(b_rows),
            "n_eligible_bat_nights": len(b_batnights),
            "n_eligible_bats": len({r[0] for r in b_rows}),
            "n_fully_surveyed_field_nights_with_gps": len(full & relevant_fieldnights),
            "n_missing_mapped_cactus_night_counts_on_gps_support": missing_cactus_night_cells,
            "potential_only": bool(b_rows),
        },
        "publisher_byte_identity_verified_here": False,
        "field_polygon_provenance_independently_verified_here": False,
        "gps_height_datum_or_error_verified_here": False,
        "behavior_labels_independent_of_height_verified_here": False,
        "sampling_detection_calibrated_here": False,
        "measured_resource_height_field_gain": None,
        "regional_species_sdm_gain": None,
        "no_animal_or_field_ids_emitted": True,
    }


def report_json(*args) -> str:
    return json.dumps(audit_support(*args), sort_keys=True, indent=2)
