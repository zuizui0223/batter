#!/usr/bin/env python3
"""Reproducible fox preprocessing and the retrospective common-place pilot.

Source event and reference CSVs must be obtained separately. Original animal
identifiers, tags, timestamps, coordinates, and grid cells remain internal.
Only aggregate reports and cryptographic receipts may be serialized. This
module uses the standard library and has no network or module-level state.

The retrospective pilot JSON does not specify every implementation detail.
This implementation fixes those details explicitly: consecutive accepted GPS
fixes within animal; no tag/deployment crossing; origin location/time/activity;
111.32 km per degree on both axes; one cosine of the quality-retained source
mean latitude; first floor(n_dates/2) observed dates per animal-month; and
pooled counts restricted to animals satisfying the common-context threshold.
These choices are not tuned to reproduce the historical outcome values.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_DOI = "10.5441/001/1.304"
SOURCE_EVENT_UUID = "47d876a1-a81a-4cd7-8c5e-809ccd56195a"
SOURCE_REFERENCE_UUID = "b40c60e4-ce7f-4bd0-a88a-5ff2112cca4a"
KM_PER_DEGREE = 111.32
EARTH_RADIUS_KM = 6371.0
DEFAULT_PILOT = Path(__file__).with_name("FOX_COMMON_PLACE_HELDOUT_R_PILOT_2026_10_19.json")


def _utc(value: str) -> datetime:
    """Interpret the source's unlabelled timestamps as UTC."""
    dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _receipt(path: Path) -> dict[str, Any]:
    sha256, md5 = hashlib.sha256(), hashlib.md5(usedforsecurity=False)
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha256.update(block)
            md5.update(block)
            size += len(block)
    return {"sha256": sha256.hexdigest(), "md5": md5.hexdigest(), "bytes": size}


def load_source(event_path: str | Path, reference_path: str | Path):
    """Return ``(internal_events, aggregate_audit, file_receipts)``.

    Manual outliers are removed first, then missing/nonfinite quality values,
    HDOP > 5 or satellites < 4. Rows must then explicitly declare the GPS
    sensor and visibility as true; missing declarations are excluded. Both
    animal and tag must match a deployment whose inclusive source interval
    contains the event. An ambiguous or absent
    deployment raises an identifier-free error; it is never silently assigned.
    Original identifiers and locations in the returned records are internal
    analysis inputs, not anonymized records suitable for export.
    """
    event_path, reference_path = Path(event_path), Path(reference_path)
    receipts = {"events": _receipt(event_path), "reference": _receipt(reference_path)}
    deployments = defaultdict(list)
    reference_animals, reference_tags = set(), set()
    reference_count = 0
    with reference_path.open(newline="", encoding="utf-8-sig") as stream:
        for index, row in enumerate(csv.DictReader(stream)):
            reference_count += 1
            animal, tag = row.get("animal-id", "").strip(), row.get("tag-id", "").strip()
            site = row.get("study-site", "").strip()
            try:
                start, end = _utc(row["deploy-on-date"]), _utc(row["deploy-off-date"])
            except (ValueError, TypeError, KeyError):
                raise ValueError("Invalid reference deployment date") from None
            if not animal or not tag or not site or start > end:
                raise ValueError("Invalid reference deployment metadata")
            deployments[(animal, tag)].append({"start": start, "end": end, "site": site,
                                               "year": start.year, "deployment": index,
                                               "sex": row.get("animal-sex", "").strip().lower() or "unknown"})
            reference_animals.add(animal)
            reference_tags.add(tag)
    if not deployments:
        raise ValueError("Reference table has no deployments")

    audit = Counter({"original_rows": 0, "source_manual_outlier_removed": 0,
                     "retained_after_source_outlier": 0,
                     "additional_hdop_gt5_sat_below4_or_missing_removed": 0,
                     "after_quality": 0, "non_gps_after_quality_removed": 0,
                     "invisible_or_missing_visibility_after_quality_removed": 0,
                     "after_gps_visible": 0, "invalid_position_time_or_id_removed": 0,
                     "source_order_nonincreasing_within_animal": 0,
                     "outside_reference_deployment_interval": 0})
    events, last_seen = [], {}
    with event_path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            audit["original_rows"] += 1
            if row.get("manually-marked-outlier", "").strip().lower() == "true":
                audit["source_manual_outlier_removed"] += 1
                continue
            audit["retained_after_source_outlier"] += 1
            hdop, satellites = _number(row.get("gps:hdop")), _number(row.get("gps:satellite-count"))
            if hdop is None or satellites is None or hdop > 5 or satellites < 4:
                audit["additional_hdop_gt5_sat_below4_or_missing_removed"] += 1
                continue
            audit["after_quality"] += 1
            if row.get("sensor-type", "").strip().lower() != "gps":
                audit["non_gps_after_quality_removed"] += 1
                continue
            if row.get("visible", "").strip().lower() != "true":
                audit["invisible_or_missing_visibility_after_quality_removed"] += 1
                continue
            audit["after_gps_visible"] += 1
            animal = row.get("individual-local-identifier", "").strip()
            tag = row.get("tag-local-identifier", "").strip()
            lat, lon = _number(row.get("location-lat")), _number(row.get("location-long"))
            try:
                dt = _utc(row.get("timestamp", ""))
            except (ValueError, TypeError):
                dt = None
            if (not animal or not tag or dt is None or lat is None or lon is None
                    or not -90 <= lat <= 90 or not -180 <= lon <= 180):
                audit["invalid_position_time_or_id_removed"] += 1
                continue
            matches = [d for d in deployments.get((animal, tag), ()) if d["start"] <= dt <= d["end"]]
            if len(matches) > 1:
                raise ValueError("Ambiguous reference deployment mapping")
            if not matches:
                raise ValueError("No reference deployment interval matches a retained source event")
            deployment = matches[0]
            if animal in last_seen and dt <= last_seen[animal]:
                audit["source_order_nonincreasing_within_animal"] += 1
            last_seen[animal] = dt
            events.append({"animal": animal, "tag": tag, "deployment": deployment["deployment"],
                           "site": deployment["site"], "year": deployment["year"],
                           "sex": deployment["sex"], "dt": dt, "day": dt.date().isoformat(),
                           "month": dt.strftime("%Y-%m"), "lat": lat, "lon": lon,
                           "hdop": hdop, "satellites": satellites,
                           "activity_x": _number(row.get("activity-x")),
                           "activity_y": _number(row.get("activity-y"))})
    events.sort(key=lambda row: (row["animal"], row["dt"], row["tag"]))
    audit.update({"retained_valid_events": len(events),
                  "n_original_individuals": len({e["animal"] for e in events}),
                  "reference_rows": reference_count, "reference_individuals": len(reference_animals),
                  "reference_tags": len(reference_tags),
                  "retained_source_site_year_cohorts": len({(e["site"], e["year"]) for e in events}),
                  "missing_activity_x": sum(e["activity_x"] is None for e in events),
                  "missing_activity_y": sum(e["activity_y"] is None for e in events)})
    return events, dict(audit), receipts


def haversine_km(a, b) -> float:
    lat_a, lat_b = math.radians(a["lat"]), math.radians(b["lat"])
    delta_lon = math.radians(b["lon"] - a["lon"])
    h = (math.sin((lat_b - lat_a) / 2) ** 2
         + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2)
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(max(0.0, h))))


def speed_mode(speed_kmh: float) -> int:
    return 0 if speed_kmh < 0.05 else 1 if speed_kmh < 0.5 else 2


def make_steps(events):
    """Return ``(internal_steps, aggregate_audit)`` using origin covariates.

    Consecutive quality-retained fixes are sorted within animal. A rejected
    pair does not remove either endpoint or create a replacement long step.
    No pair crosses tags, deployments, site-year cohorts, or UTC dates.
    """
    animals = defaultdict(list)
    for event in events:
        animals[event["animal"]].append(event)
    audit = Counter({"candidate_adjacent_pairs": 0, "tag_or_deployment_boundary_removed": 0,
                     "nonpositive_duration_removed": 0, "cross_utc_date_removed": 0,
                     "outside_9to15minute_cadence_removed": 0,
                     "same_day_9to15minute_pairs_before_speed": 0, "speed_gt10_kmh_removed": 0,
                     "source_9to15minute_same_day_steps": 0})
    steps = []
    for animal in sorted(animals):
        values = sorted(animals[animal], key=lambda row: (row["dt"], row["tag"]))
        for origin, end in zip(values, values[1:]):
            audit["candidate_adjacent_pairs"] += 1
            if any(origin.get(key) != end.get(key) for key in ("tag", "deployment", "site", "year")):
                audit["tag_or_deployment_boundary_removed"] += 1
                continue
            seconds = (end["dt"] - origin["dt"]).total_seconds()
            if seconds <= 0:
                audit["nonpositive_duration_removed"] += 1
                continue
            if origin["dt"].date() != end["dt"].date():
                audit["cross_utc_date_removed"] += 1
                continue
            if not 540 <= seconds <= 900:
                audit["outside_9to15minute_cadence_removed"] += 1
                continue
            audit["same_day_9to15minute_pairs_before_speed"] += 1
            distance = haversine_km(origin, end)
            speed = distance / (seconds / 3600)
            if speed > 10:
                audit["speed_gt10_kmh_removed"] += 1
                continue
            step = dict(origin)
            step.update({"dt_end": end["dt"], "duration_minutes": seconds / 60,
                         "distance_km": distance, "speed": speed, "speed_kmh": speed,
                         "mode": speed_mode(speed), "activity_x_end": end.get("activity_x"),
                         "activity_y_end": end.get("activity_y"), "hdop_end": end.get("hdop"),
                         "satellites_end": end.get("satellites")})
            steps.append(step)
    audit["source_9to15minute_same_day_steps"] = len(steps)
    return steps, dict(audit)


def source_lat_cos(events) -> float:
    """Internal fixed projection cosine; never include this in public reports."""
    if not events:
        raise ValueError("Cannot define source projection without retained events")
    return math.cos(math.radians(math.fsum(e["lat"] for e in events) / len(events)))


def context(step, width_km: float, clock: bool = True, *, lat_cos: float):
    """Return an internal geographic grid cell, optionally with a UTC 6h bin."""
    if not math.isfinite(width_km) or width_km <= 0:
        raise ValueError("Grid width must be positive and finite")
    if not math.isfinite(lat_cos) or not 0 < lat_cos <= 1:
        raise ValueError("Source latitude cosine must lie in (0, 1]")
    cell = (math.floor(step["lon"] * KM_PER_DEGREE * lat_cos / width_km),
            math.floor(step["lat"] * KM_PER_DEGREE / width_km))
    return cell + (step["dt"].hour // 6,) if clock else cell


def split_animal_days(steps, min_steps: int = 80, min_dates: int = 6):
    """Legacy first-half observed-date split, for one site/year/month only."""
    groups = defaultdict(list)
    units = {(s["site"], s["year"], s["month"]) for s in steps}
    if len(units) > 1:
        raise ValueError("Legacy split requires one source site/year/month")
    for step in steps:
        groups[step["animal"]].append(step)
    train, test, eligible = [], [], set()
    for animal in sorted(groups):
        rows = groups[animal]
        days = sorted({row["day"] for row in rows})
        if len(rows) < min_steps or len(days) < min_dates:
            continue
        eligible.add(animal)
        train_days = set(days[:len(days) // 2])
        train.extend(row for row in rows if row["day"] in train_days)
        test.extend(row for row in rows if row["day"] not in train_days)
    return train, test, eligible


@dataclass
class CommonContextModel:
    """Internal fit object: contains identifiers and geographic cells."""
    width_km: float
    clock: bool
    lat_cos: float
    shrinkage: float
    pooled: dict
    personal: dict
    allowed: dict


def fit(training_steps, width_km: float = 1.0, clock: bool = True, *, lat_cos: float,
        shrinkage: float = 15.0, min_context_steps: int = 15, min_context_days: int = 2):
    """Fit pooled Jeffreys and personal shrinkage distributions on shared support."""
    if shrinkage <= 0:
        raise ValueError("Shrinkage must be positive")
    counts, dates = defaultdict(lambda: defaultdict(Counter)), defaultdict(lambda: defaultdict(set))
    for step in training_steps:
        cell, animal = context(step, width_km, clock, lat_cos=lat_cos), step["animal"]
        mode = step["mode"]
        if mode not in (0, 1, 2):
            raise ValueError("Legacy speed mode must be 0, 1, or 2")
        counts[cell][animal][mode] += 1
        dates[cell][animal].add(step["day"])
    pooled, personal, allowed = {}, {}, {}
    for cell in sorted(counts):
        animals = {animal for animal, values in counts[cell].items()
                   if sum(values.values()) >= min_context_steps
                   and len(dates[cell][animal]) >= min_context_days}
        if len(animals) < 2:
            continue
        total = [sum(counts[cell][animal][mode] for animal in animals) for mode in range(3)]
        denominator = sum(total) + 1.5
        pooled[cell] = tuple((value + 0.5) / denominator for value in total)
        allowed[cell] = animals
        for animal in sorted(animals):
            values = counts[cell][animal]
            n = sum(values.values())
            personal[(cell, animal)] = tuple((values[mode] + shrinkage * pooled[cell][mode])
                                             / (n + shrinkage) for mode in range(3))
    return CommonContextModel(width_km, clock, lat_cos, shrinkage, pooled, personal, allowed)


def predict(model: CommonContextModel, step):
    """Return ``(pooled_probability, personal_probability)`` or None off support."""
    cell = context(step, model.width_km, model.clock, lat_cos=model.lat_cos)
    key = (cell, step["animal"])
    if key not in model.personal:
        return None
    mode = step["mode"]
    return model.pooled[cell][mode], model.personal[key][mode]


def score_heldout(model: CommonContextModel, test_steps, min_steps: int = 15,
                  min_dates: int = 3, return_internal: bool = False):
    """Score common-support observations, then equally weight days and animals."""
    gains = defaultdict(lambda: defaultdict(list))
    for step in test_steps:
        probabilities = predict(model, step)
        if probabilities is not None:
            pooled, personal = probabilities
            gains[step["animal"]][step["day"]].append(math.log(personal / pooled))
    animal_day_gains, animal_gains, kept_steps = {}, {}, 0
    for animal in sorted(gains):
        days = gains[animal]
        n = sum(map(len, days.values()))
        if n < min_steps or len(days) < min_dates:
            continue
        day_means = {day: math.fsum(values) / len(values) for day, values in sorted(days.items())}
        animal_day_gains[animal] = day_means
        animal_gains[animal] = math.fsum(day_means.values()) / len(day_means)
        kept_steps += n
    report = {"n_evaluable_holdout_animals": len(animal_gains),
              "n_common_training_contexts": len(model.pooled), "heldout_step_count": kept_steps,
              "heldout_animal_days": sum(map(len, animal_day_gains.values())),
              "n_individuals_with_positive_personal_vs_pooled_gain": sum(v > 0 for v in animal_gains.values()),
              "gain_nats_per_step_equal_animal_day":
                  math.fsum(animal_gains.values()) / len(animal_gains) if animal_gains else None}
    if return_internal:
        return report, {"animal_day_gains": animal_day_gains, "animal_gains": animal_gains}
    return report


def reproduce_pilot(event_path, reference_path, pilot_path=DEFAULT_PILOT):
    """Return an aggregate, auditable reconstruction against the historical JSON.

    The historical list fixes which ten cohorts are compared; it does not
    select new results by their magnitude. Numerical disagreement is reported,
    not hidden by trying alternative conventions.
    """
    events, audit, receipts = load_source(event_path, reference_path)
    steps, step_audit = make_steps(events)
    audit.update(step_audit)
    lat_cos = source_lat_cos(events)
    pilot = json.loads(Path(pilot_path).read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for step in steps:
        groups[(step["site"], step["year"], step["month"])].append(step)
    variants = [(1.0, True, "B_1km_with_6h_nats_per_step_equal_animal_day"),
                (2.0, True, "B_2km_with_6h_nats_per_step_equal_animal_day"),
                (1.0, False, "B_1km_without_hour_control_nats_per_step_equal_animal_day")]
    rows, comparisons = [], []
    count_fields = ("individuals_source_month_with_sufficient_day_records", "n_evaluable_holdout_animals",
                    "n_common_training_contexts", "heldout_step_count", "heldout_animal_days",
                    "n_individuals_with_positive_personal_vs_pooled_gain")
    for original in pilot["results"]:
        key = (original["source_site"], original["source_reference_deploy_year"], original["month"])
        train, test, eligible = split_animal_days(groups.get(key, []))
        row = {"source_site": key[0], "source_reference_deploy_year": key[1], "month": key[2],
               "individuals_source_month_with_sufficient_day_records": len(eligible)}
        for width, clock, label in variants:
            report = score_heldout(fit(train, width, clock, lat_cos=lat_cos), test)
            row[label] = report.pop("gain_nats_per_step_equal_animal_day")
            if width == 1 and clock:
                row.update(report)
        rows.append(row)
        differences = {field: row[field] - original[field] for field in count_fields}
        for _, _, label in variants:
            differences[label] = None if row[label] is None else row[label] - original[label]
        comparisons.append({"source_site": key[0], "source_reference_deploy_year": key[1],
                            "month": key[2], "reconstruction_minus_pilot": differences})
    exact_counts = all(all(c["reconstruction_minus_pilot"][field] == 0 for field in count_fields)
                       for c in comparisons)
    max_difference = max((abs(c["reconstruction_minus_pilot"][label]) for c in comparisons
                          for _, _, label in variants if c["reconstruction_minus_pilot"][label] is not None),
                         default=None)
    return {"schema_version": 1, "source_doi": SOURCE_DOI, "source_receipts": receipts,
            "historical_pilot_receipt": _receipt(Path(pilot_path)), "observation_audit": audit,
            "status": "RETROSPECTIVE_PILOT_RECONSTRUCTION_NOT_NULL_CALIBRATED",
            "method": {"step_anchor": "origin location, UTC timestamp, and activity",
                       "projection": "fixed geographic origin; 111.32 km/degree both axes; longitude multiplied by cosine of mean quality-retained event latitude",
                       "split": "first floor(n_observed_dates/2) dates separately within eligible animal-month",
                       "common_pool": "only animals with >=15 training steps over >=2 dates in context",
                       "eligibility": ">=80 steps and >=6 observed dates per source animal-month",
                       "test_eligibility": ">=15 common-support heldout steps and >=3 heldout dates",
                       "models": "3 speed modes; pooled Jeffreys 0.5/class; individual lambda15 shrinkage",
                       "weight": "equal within animal-day, then equal days, then equal animals",
                       "selection": "the same ten cohort keys already listed in the historical pilot",
                       "ambiguity": "Historical JSON does not fix origin versus endpoint, projection constants, rounding of odd date counts, or inclusion of below-threshold animals in the pooled model. No variants were searched to match historical outcomes."},
            "results": rows, "historical_comparison": comparisons,
            "historical_count_fields_identical": exact_counts,
            "maximum_absolute_gain_difference_from_historical": max_difference,
            "limitations": ["Observed-date splits can place animals' training and testing dates on different calendar dates.",
                            "This reproduction is descriptive and provides no exchangeability null or causal interpretation.",
                            "Original identities, coordinates, cells, dates, tags, and per-animal results are not exported."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--pilot", type=Path, default=DEFAULT_PILOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = reproduce_pilot(args.events, args.reference, args.pilot)
    serialized = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
