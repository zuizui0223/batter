#!/usr/bin/env python3
"""Privacy-preserving Movebank event CSV/GZIP source preflight.

This runs only on an explicitly authorized operator-provided event file.
The script does not download data, infer taxa/colonies/resources from raw
coordinates, or produce a biological individuality/partitioning result.
Original individual IDs and positions are held in process memory but NEVER
written to the output or console.

Examples:
  python3 preflight_movebank_events_v1.py --events /authorized/event.csv.gz \
    --source-doi 10.5441/001/1.123 --json-output stage1_summary.json
  python3 -m unittest discover -s prospective/multitaxon_individuality/tests -v
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone, date
from pathlib import Path

ALIASES = {
    "timestamp": ("timestamp", "event-timestamp", "event_timestamp", "date-time", "datetime"),
    "lat": ("location-lat", "location_lat", "latitude", "lat"),
    "lon": ("location-long", "location_lon", "location_long", "longitude", "lon"),
    "animal": ("individual-local-identifier", "individual_local_identifier",
               "individual-id", "individual_id", "animal-id", "animal_id"),
    "tag": ("tag-local-identifier", "tag_local_identifier", "tag-id", "tag_id"),
    "sensor": ("sensor-type", "sensor_type", "sensor", "sensor-name"),
    "accuracy": ("eobs:horizontal-accuracy", "horizontal-accuracy",
                 "gps:hdop", "gps-hdop", "location-error", "location_error"),
}
CUTOFFS = [1, 5, 30, 60, 180, 1440]
STATUS = {
    "NO_ID": "STOP_STABLE_ANIMAL_ID_FIELD_MISSING",
    "NO_COORD": "STOP_REQUIRED_GPS_TIME_COORD_COLUMNS_MISSING",
    "NO_EVENTS": "STOP_NO_VALID_GPS_EVENTS",
    "NOT_ENOUGH_ANIMALS": "STOP_INSUFFICIENT_REPEATED_INDIVIDUALS",
    "NOT_OVERLAP": "STOP_INSUFFICIENT_OVERLAPPING_TRACK_DAYS",
    "PASS": "STAGE1_COUNTS_PASS_PENDING_POPULATION_SENSOR_PRECISION_AND_COMMON_SUPPORT"
}


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")


def detect_columns(headers: list[str]) -> dict[str, str | None]:
    canonical = {norm(h): h for h in headers}
    fields = {}
    for role, candidates in ALIASES.items():
        fields[role] = next((canonical[norm(s)] for s in candidates if norm(s) in canonical), None)
    return fields


def time_utc(value: str, assume_utc: bool) -> datetime | None:
    v = value.strip()
    if not v:
        return None
    try:
        # Movebank timestamps normally use an ISO timestamp with UTC offset/Z.
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            if not assume_utc:
                return None
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def geoval(value: str, minv: float, maxv: float) -> float | None:
    try:
        x = float(value)
        return x if math.isfinite(x) and minv <= x <= maxv else None
    except (ValueError, TypeError):
        return None


def open_stream(path: Path):
    return gzip.open(path, "rt", encoding="utf-8-sig", newline="") if path.suffix == ".gz" else path.open(
        "r", encoding="utf-8-sig", newline=""
    )


def interval_bucket(minutes: float) -> str:
    for n in CUTOFFS:
        if minutes <= n:
            return f"<= {n} minutes"
    return "> 1440 minutes"


def preflight(path: Path, source_doi: str, *, min_animals: int = 8,
              min_days: int = 4, min_fixes_day: int = 50,
              min_span_days: int = 7, min_shared_dates: int = 3,
              assume_utc: bool = False, max_rows: int | None = None) -> dict:
    if not path.is_file():
        raise ValueError("Operator-provided source event path missing; no automatic downloads")
    if path.suffix not in (".csv", ".tsv", ".txt", ".gz"):
        raise ValueError("Expected extracted CSV/TSV event file or GZIP, not ZIP/GeoTIFF/other raw data")
    if max_rows is not None and max_rows < 1:
        raise ValueError("max_rows must be positive")
    if not source_doi.strip():
        raise ValueError("Source DOI required for provenance, not animal-identifying data")
    counters = Counter()
    animal_day_counts: dict[str, Counter[date]] = defaultdict(Counter)
    animal_first: dict[str, date] = {}
    animal_last: dict[str, date] = {}
    animal_last_utc: dict[str, datetime] = {}
    interval_hist = Counter()
    fields = {}
    sensor_column = False
    accuracy_column = False
    with open_stream(path) as file:
        head = file.readline()
        if not head:
            return {"schema_version": 1, "source_doi": source_doi,
                    "preflight_status": STATUS["NO_EVENTS"],
                    "observations_scanned": 0, "raw_identifiers_exported": False}
        delimiter = "\t" if (path.suffix == ".tsv" or head.count("\t") > head.count(",")) else ","
        file.seek(0)
        reader = csv.DictReader(file, delimiter=delimiter)
        fields = detect_columns(reader.fieldnames or [])
        sensor_column = bool(fields["sensor"])
        accuracy_column = bool(fields["accuracy"])
        if not all(fields[k] for k in ("timestamp", "lat", "lon")):
            status = STATUS["NO_COORD"]
        elif not fields["animal"]:
            status = STATUS["NO_ID"]
        else:
            status = None
        if status:
            return {"schema_version": 1, "source_doi": source_doi,
                    "preflight_status": status, "observations_scanned": 0,
                    "animal_id_column_present": bool(fields["animal"]),
                    "tag_only_id_not_accepted": bool(fields["tag"] and not fields["animal"]),
                    "raw_identifiers_exported": False}
        for row in reader:
            if max_rows is not None and counters["rows_scanned"] >= max_rows:
                break
            counters["rows_scanned"] += 1
            if sensor_column:
                sensor = (row.get(fields["sensor"]) or "").strip()
                if sensor and "gps" not in sensor.lower():
                    counters["non_GPS_sensor_excluded"] += 1
                    continue
                if not sensor:
                    counters["sensor_type_missing_within_row"] += 1
            else:
                counters["sensor_column_absent"] += 1
            ident = (row.get(fields["animal"]) or "").strip()
            if not ident:
                counters["rows_missing_individual_identifier"] += 1
                continue
            dt = time_utc(row.get(fields["timestamp"]) or "", assume_utc)
            lat = geoval(row.get(fields["lat"]) or "", -90, 90)
            lon = geoval(row.get(fields["lon"]) or "", -180, 180)
            if dt is None:
                counters["timestamp_invalid_or_timezone_unresolved"] += 1
                continue
            if lat is None or lon is None:
                counters["coordinates_invalid"] += 1
                continue
            counters["valid_GPS_like_events"] += 1
            if accuracy_column and (row.get(fields["accuracy"]) or "").strip():
                counters["accuracy_field_nonempty"] += 1
            day = dt.date()
            animal_day_counts[ident][day] += 1
            if ident not in animal_first or day < animal_first[ident]:
                animal_first[ident] = day
            if ident not in animal_last or day > animal_last[ident]:
                animal_last[ident] = day
            prev = animal_last_utc.get(ident)
            if prev is not None:
                mins = (dt - prev).total_seconds()/60
                if mins > 0:
                    interval_hist[interval_bucket(mins)] += 1
                elif mins == 0:
                    counters["nonunique_consecutive_time_within_animal"] += 1
                else:
                    counters["out_of_order_time_within_animal"] += 1
            animal_last_utc[ident] = dt
    elapsed = {
        animal: (animal_last[animal] - animal_first[animal]).days
        for animal in animal_day_counts
    }
    qualified: set[str] = set()
    for ident, day_count in animal_day_counts.items():
        days_with_enough = sum(n >= min_fixes_day for n in day_count.values())
        if days_with_enough >= min_days and elapsed[ident] >= min_span_days:
            qualified.add(ident)
    overlapping_days = Counter()
    for animal in qualified:
        for dt, n in animal_day_counts[animal].items():
            if n >= min_fixes_day:
                overlapping_days[dt] += 1
    shared_date_count = sum(n >= 2 for n in overlapping_days.values())
    eligible_n = len(qualified)
    if counters["valid_GPS_like_events"] == 0:
        status = STATUS["NO_EVENTS"]
    elif eligible_n < min_animals:
        status = STATUS["NOT_ENOUGH_ANIMALS"]
    elif shared_date_count < min_shared_dates:
        status = STATUS["NOT_OVERLAP"]
    else:
        status = STATUS["PASS"]
    if max_rows is not None and counters["rows_scanned"] >= max_rows:
        status = "PARTIAL_SCAN_UNDECIDED_NOT_ELIGIBLE"
    return {
        "schema_version": 1,
        "source_doi": source_doi,
        "preflight_status": status,
        "parameters": {"min_animals":min_animals, "min_qualified_days":min_days,
                       "min_fixes_per_qualified_day":min_fixes_day,
                       "min_timespan_calendar_days":min_span_days,
                       "min_overlapping_dates_with_2_qualified_animals":min_shared_dates,
                       "assume_missing_timestamp_timezone_is_UTC":assume_utc},
        "observations_scanned": counters["rows_scanned"],
        "valid_GPS_like_events": counters["valid_GPS_like_events"],
        "n_distinct_animal_id_strings": len(animal_day_counts),
        "n_repeated_animals_passing_simple_day_and_span_gate": eligible_n,
        "n_source_dates_with_2_or_more_passing_animals": shared_date_count,
        "sensor_type_column_present": sensor_column,
        "GPS_event_sensor_type_verified": bool(sensor_column and counters["valid_GPS_like_events"] and
                                              counters["sensor_type_missing_within_row"] == 0),
        "accuracy_measure_column_present": accuracy_column,
        "accuracy_populated_fixes": counters["accuracy_field_nonempty"],
        "timestamp_timezone_assumption_enabled": assume_utc,
        "time_step_histogram": dict(sorted(interval_hist.items())),
        "row_exclusion_counts": {k: v for k,v in sorted(counters.items()) if k not in
                                 ("rows_scanned","valid_GPS_like_events","accuracy_field_nonempty")},
        "raw_identifiers_exported": False,
        "animal_id_list_exported": False,
        "coordinates_or_exact_track_dates_exported": False,
        "real_individuality_or_partition_effect_estimated": False,
        "eligibility_limits": [
            "A passing source-wide animal/day count is NOT a verified species×site×season population.",
            "GPS sensor type may be unverified and GPS horizontal accuracy may be unknown.",
            "No within-same-cohort common geographical cells, kinematics or spatial exclusivity tested.",
            "Tag redeployment and source-identifier aliasing require reference-data inspection.",
            "No GPS or raw animal record is included in this output."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", required=True, type=Path, help="Authorized source event CSV/TSV or GZIP path")
    parser.add_argument("--source-doi", required=True)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--assume-utc", action="store_true", help="Explicitly interpret tz-naive source time as UTC")
    parser.add_argument("--max-rows", type=int, help="Debug only, status forced undecided")
    ns = parser.parse_args()
    result = preflight(ns.events, ns.source_doi, assume_utc=ns.assume_utc,
                       max_rows=ns.max_rows)
    payload = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
    if ns.json_output:
        ns.json_output.write_text(payload+"\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
