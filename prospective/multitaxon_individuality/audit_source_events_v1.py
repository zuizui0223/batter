#!/usr/bin/env python3
"""Screen original public animal movement CSV files without reporting positions/IDs.

Usage: python3 audit_source_events_v1.py /authorized/original_tracking.csv
       --doi 10.5441/001/1.foo [--output aggregate.json]

This is NOT individual specialization or niche partitioning inference.
Minimum coverage is diagnostic only: at least 30 unique animal/timestamp
position records on at least 3 distinct calendar days for at least 8 animals.
Sensor sources are separated: Argos-only is NOT promoted as high-accuracy GPS.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

MIN_RECORDS = 30
MIN_DAYS = 3
MIN_ANIMALS = 8
GPS_SENSOR_NAMES = {"gps", "gps-gsm", "fastloc-gps", "gps-logger", "gps logger"}


def numeric_coordinate(lon: str, lat: str) -> bool:
    try:
        a, b = float(lon), float(lat)
        return math.isfinite(a) and math.isfinite(b) and abs(a) <= 180 and abs(b) <= 90
    except (ValueError, TypeError):
        return False


def summarize_csv(source: Path, doi: str, label: str = "") -> dict:
    ids = {}
    raw = 0
    excluded = 0
    missing = 0
    collisions = 0
    types = Counter()
    sensor_animal_days = defaultdict(lambda: defaultdict(set))
    with source.open("r", newline="", encoding="utf-8-sig") as inp:
        read = csv.DictReader(inp)
        required = {
            "individual-local-identifier", "timestamp",
            "location-long", "location-lat"
        }
        assert required <= set(read.fieldnames or ()), "Missing required original timestamp, ID or coordinate fields"
        for line in read:
            raw += 1
            if str(line.get("visible", "")).lower().strip() == "false" or (
                str(line.get("algorithm-marked-outlier", "")).lower().strip() == "true"
            ):
                excluded += 1
                continue
            animal = str(line["individual-local-identifier"] or "").strip()
            timestamp = str(line["timestamp"] or "").strip()
            if not animal or len(timestamp) < 10 or not numeric_coordinate(
                line.get("location-long", ""), line.get("location-lat", "")
            ):
                missing += 1
                continue
            sensor = str(line.get("sensor-type", "") or "unreported").strip().lower()
            types[sensor] += 1
            r = ids.setdefault(animal, {"unique_times": set(), "calendar_days": set(), "sensor_types": set()})
            if timestamp in r["unique_times"]:
                collisions += 1
                continue
            r["unique_times"].add(timestamp)
            r["calendar_days"].add(timestamp[:10])
            r["sensor_types"].add(sensor)
            sensor_animal_days[sensor][animal].add(timestamp)
    n = len(ids)
    if n == 0:
        status = "NO_VERIFIED_POSITION_ANIMAL_ID"
    elif n < 2:
        status = "FAIL_SINGLE_INDIVIDUAL"
    elif all("argos" in x for x in types) and types:
        status = "ARGOS_ONLY_NOT_FINE_GPS_PRIMARY"
    else:
        num_potential = sum(
            len(o["unique_times"]) >= MIN_RECORDS and
            len(o["calendar_days"]) >= MIN_DAYS for o in ids.values()
        )
        has_gps = any(
            s in GPS_SENSOR_NAMES or s.startswith("gps-") for s in types
        )
        status = (
            "GPS_TEMPORAL_PREFLIGHT_POSSIBLE_NEEDS_COHORT_CONTEXT"
            if has_gps and num_potential >= MIN_ANIMALS
            else "DEFER_PRECISION_OR_SAMPLE_SUPPORT"
        )
    counts = sorted(len(r["unique_times"]) for r in ids.values())
    days = sorted(len(r["calendar_days"]) for r in ids.values())
    eligible_coverage = sum(
        len(o["unique_times"]) >= MIN_RECORDS and
        len(o["calendar_days"]) >= MIN_DAYS for o in ids.values()
    )
    return {
        "schema_version": 1,
        "source_doi": doi,
        "source_file_label": label or source.name,
        "audit_kind": "original positional event screening only; NO hypothesis test",
        "raw_source_rows": raw,
        "visible_outlier_excluded": excluded,
        "missing_id_time_coordinate": missing,
        "valid_observation_row_sensor_counts": dict(sorted(types.items())),
        "individual_ids_with_valid_position_rows": n,
        "unique_individual_timestamp_positions": sum(counts),
        "within_individual_same_timestamp_collisions": collisions,
        "animal_record_count_min_median_max": (
            [counts[0], counts[n//2], counts[-1]] if n else []
        ),
        "animal_calendar_day_count_min_median_max": (
            [days[0], days[n//2], days[-1]] if n else []
        ),
        "possible_individuals_with_ge_30_time_records_on_ge_3_days": eligible_coverage,
        "diagnostic_thresholds": {
            "unique_timestamp_positions_per_animal": MIN_RECORDS,
            "distinct_calendar_days_per_animal": MIN_DAYS,
            "animals_for_possible_primary_cohort": MIN_ANIMALS,
        },
        "stage3_precision_coverage_status": status,
        "cohort_or_site_overlap_verified": False,
        "source_error_calibration_verified": False,
        "individual_identity_effect_fitted": False,
        "explicit_note": (
            "Collisions are distinct source event rows with the same animal/timestamp, "
            "NOT proof they share coordinates or are duplicate sensor fixes. "
            "No GPS/Argos error harmonization or bat-like 3D partition inference attempted."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("source_csv", type=Path)
    p.add_argument("--doi", required=True)
    p.add_argument("--label", default="")
    p.add_argument("--output", type=Path)
    x = p.parse_args()
    if not x.source_csv.is_file():
        p.error("Original CSV does not exist; no downloaded tracking file was fabricated")
    result = summarize_csv(x.source_csv, x.doi, x.label)
    if x.output:
        x.output.parent.mkdir(parents=True, exist_ok=True)
        x.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    else:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
