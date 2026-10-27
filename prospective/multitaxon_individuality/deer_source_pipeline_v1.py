#!/usr/bin/env python3
"""Pinned-source preprocessing for Wyoming Sublette mule deer, 2018–2020.

Original identifiers, tag/group labels, dates, and positions are internal
inputs only. Event/Step objects deliberately do not print their fields. The
returned audit and receipt dictionaries contain only aggregate information.
This module computes no individuality, overlap, or ecological effect.

The native source timestamp is retained as a naive datetime: its clock is
not verified as UTC. Steps use origin covariates, remain within the same
source date/month, and connect adjacent same-animal/tag/deployment fixes at
108–132 minutes inclusive. No movement-speed threshold is applied.
"""
from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from pathlib import Path

SOURCE_DOI = "10.5441/001/1.708"
EXPECTED_TAXON = "Odocoileus hemionus"
EARTH_RADIUS_KM = 6371.0
SOURCE_RECEIPT_FILE = "NEXT_SOURCE_STORK_DEER_RECEIPT_2026_10_20.json"
PINNED_RECEIPTS = {
    "events": {"uuid": "de7b956a-f5b6-4727-a2cc-a119a1217a68", "bytes": 134497843,
               "sha256": "4dbed25db77c4da9eea328ff8f41725d1cced1c4a8ee87227f537a7217eafd4e",
               "md5": "a8563f71fa6213919812dc0f2da30c26"},
    "reference": {"uuid": "b7d477e8-bf33-4cd0-9f49-c9617a99b2f3", "bytes": 13150,
                  "sha256": "84eb3131c847c03f48b790e0388f4408cbc0a26f6852f5346d579bdd35fffff2",
                  "md5": "fe3dcb4fd281b0d9c62a4e3f10bf9324"},
}
OUTLIER_FIELDS = ("manually-marked-outlier", "algorithm-marked-outlier", "automatically-marked-outlier", "outlier")
QUALITY_FIELDS = ("gps:hdop", "gps:satellite-count", "gps:vdop", "gps:pdop",
                  "location-error-numerical", "location-error-text", "gps:fix-type-raw")
TRUE_VALUES = frozenset(("true", "1"))


@dataclass(frozen=True, slots=True, repr=False)
class Event:
    """Internal source observation; calendar properties use its native clock."""
    animal: str
    tag: str
    group: str
    sex: str
    life_stage: str
    deployment: int
    dt: datetime
    lat: float
    lon: float

    @property
    def day(self) -> int:
        return self.dt.toordinal()

    @property
    def year(self) -> int:
        return self.dt.year

    @property
    def month(self) -> int:
        return self.dt.month

    @property
    def hour_bin(self) -> int:
        return self.dt.hour // 6


@dataclass(frozen=True, slots=True, repr=False)
class Step(Event):
    """Internal step whose inherited fields are all anchored at the origin."""
    dt_end: datetime
    distance_km: float
    speed_kmh: float
    duration_minutes: float


@dataclass(frozen=True, slots=True, repr=False)
class _Reference:
    animal: str
    tag: str
    group: str
    sex: str
    life_stage: str
    deployment: int
    start: datetime | None
    end: datetime | None


def _receipt(path: Path) -> dict:
    sha, md5 = hashlib.sha256(), hashlib.md5(usedforsecurity=False)
    size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
            md5.update(block)
            size += len(block)
    return {"sha256": sha.hexdigest(), "md5": md5.hexdigest(), "bytes": size}


def _source_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip())
    if parsed.tzinfo is not None:
        raise ValueError("Expected an unlabelled native source timestamp")
    return parsed


def _finite(value) -> float | None:
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) else None


def _load_reference(path: Path):
    records = {}
    animals, tags, groups = set(), set(), set()
    by_animal, by_tag = defaultdict(set), defaultdict(set)
    group_sizes = Counter()
    sex_counts, life_counts = Counter(), Counter()
    counts = Counter({"rows": 0, "missing_deploy_on_date": 0, "missing_deploy_off_date": 0,
                      "missing_group": 0, "exact_duplicate_reference_rows": 0})
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for index, row in enumerate(csv.DictReader(stream)):
            counts["rows"] += 1
            animal, tag = row.get("animal-id", "").strip(), row.get("tag-id", "").strip()
            if not animal or not tag or row.get("animal-taxon", "").strip() != EXPECTED_TAXON:
                raise ValueError("Invalid reference animal, tag, or taxon metadata")
            start_value, end_value = row.get("deploy-on-date", "").strip(), row.get("deploy-off-date", "").strip()
            try:
                start = _source_datetime(start_value) if start_value else None
                end = _source_datetime(end_value) if end_value else None
            except ValueError:
                raise ValueError("Invalid reference deployment timestamp") from None
            if start is not None and end is not None and start > end:
                raise ValueError("Invalid reference deployment interval")
            group = row.get("animal-group-id", "").strip()
            sex = row.get("animal-sex", "").strip().lower() or "unknown"
            stage = row.get("animal-life-stage", "").strip().lower() or "unknown"
            current = _Reference(animal, tag, group, sex, stage, index, start, end)
            pair = (animal, tag)
            if pair in records:
                previous = records[pair]
                if ((previous.group, previous.sex, previous.life_stage, previous.start, previous.end)
                        != (group, sex, stage, start, end)):
                    raise ValueError("Conflicting reference metadata for an animal/tag pair")
                counts["exact_duplicate_reference_rows"] += 1
                continue
            records[pair] = current
            counts["missing_deploy_on_date"] += start is None
            counts["missing_deploy_off_date"] += end is None
            counts["missing_group"] += not group
            animals.add(animal)
            tags.add(tag)
            if group:
                groups.add(group)
                group_sizes[group] += 1
            by_animal[animal].add(tag)
            by_tag[tag].add(animal)
            sex_counts[sex] += 1
            life_counts[stage] += 1
    if not records:
        raise ValueError("Reference table has no valid records")
    summary = dict(counts)
    summary.update({"distinct_animals": len(animals), "distinct_tags": len(tags),
                    "distinct_animal_tag_pairs": len(records), "distinct_nonempty_groups": len(groups),
                    "unlabelled_group_sizes": sorted(group_sizes.values()),
                    "animals_with_multiple_tags": sum(len(values) > 1 for values in by_animal.values()),
                    "tags_assigned_to_multiple_animals": sum(len(values) > 1 for values in by_tag.values()),
                    "sex_counts": dict(sorted(sex_counts.items())),
                    "life_stage_counts": dict(sorted(life_counts.items()))})
    return records, summary


def load_source(event_path, reference_path, *, verify_receipts: bool = True):
    """Return ``(events, aggregate_audit, receipts)`` for 2018–2020.

    Default checksum validation pins both complete files to the earlier
    acquisition receipt. ``verify_receipts=False`` is intended for synthetic
    contract tests, and is recorded in receipts. Source outlier flags (when
    present), explicit GPS/visibility, expected taxon, finite coordinate
    ranges, source timestamps, and the declared years determine retention.

    Both animal and tag must match reference metadata. Available reference
    deployment dates are enforced; missing dates are audited, not invented.
    Exact repeated positions at one animal timestamp collapse to one row.
    Conflicting positions or tags at one animal timestamp remove every row
    in that timestamp group, avoiding an arbitrary choice among locations.
    """
    event_path, reference_path = Path(event_path), Path(reference_path)
    receipts = {"events": _receipt(event_path), "reference": _receipt(reference_path)}
    for role in receipts:
        verified = all(receipts[role][key] == PINNED_RECEIPTS[role][key] for key in ("sha256", "md5", "bytes"))
        if verify_receipts and not verified:
            raise ValueError("Source checksum does not match the pinned acquisition receipt")
        receipts[role]["matches_pinned_source"] = verified
        receipts[role]["validation_required"] = verify_receipts
    references, reference_audit = _load_reference(reference_path)
    counts = Counter({"original_rows": 0, "source_outlier_removed": 0, "non_gps_removed": 0,
                      "not_explicitly_visible_removed": 0, "unexpected_taxon_removed": 0,
                      "missing_animal_or_tag_removed": 0, "invalid_position_removed": 0,
                      "invalid_timestamp_removed": 0, "outside_2018_2020_removed": 0,
                      "events_with_unverifiable_deployment_interval": 0,
                      "source_order_backward_rows": 0,
                      "identical_duplicate_rows_removed": 0, "conflicting_timestamp_groups": 0,
                      "conflicting_timestamp_rows_removed": 0, "conflicting_tag_timestamp_groups": 0,
                      "rows_with_unrecognized_outlier_flag": 0})
    candidate_events = []
    last_seen = {}
    with event_path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = tuple(reader.fieldnames or ())
        outlier_fields = tuple(name for name in OUTLIER_FIELDS if name in fields)
        quality_fields = tuple(name for name in QUALITY_FIELDS if name in fields)
        for row in reader:
            counts["original_rows"] += 1
            flags = [row.get(name, "").strip().lower() for name in outlier_fields]
            if any(value in TRUE_VALUES for value in flags):
                counts["source_outlier_removed"] += 1
                continue
            if any(value not in ("", "false", "0", "true", "1") for value in flags):
                counts["rows_with_unrecognized_outlier_flag"] += 1
            if row.get("sensor-type", "").strip().lower() != "gps":
                counts["non_gps_removed"] += 1
                continue
            if row.get("visible", "").strip().lower() not in TRUE_VALUES:
                counts["not_explicitly_visible_removed"] += 1
                continue
            if row.get("individual-taxon-canonical-name", "").strip() != EXPECTED_TAXON:
                counts["unexpected_taxon_removed"] += 1
                continue
            animal = row.get("individual-local-identifier", "").strip()
            tag = row.get("tag-local-identifier", "").strip()
            if not animal or not tag:
                counts["missing_animal_or_tag_removed"] += 1
                continue
            lat, lon = _finite(row.get("location-lat")), _finite(row.get("location-long"))
            if lat is None or lon is None or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                counts["invalid_position_removed"] += 1
                continue
            try:
                dt = _source_datetime(row.get("timestamp", ""))
            except (ValueError, TypeError):
                counts["invalid_timestamp_removed"] += 1
                continue
            if not 2018 <= dt.year <= 2020:
                counts["outside_2018_2020_removed"] += 1
                continue
            ref = references.get((animal, tag))
            if ref is None:
                raise ValueError("Source animal/tag pair is absent from reference metadata")
            if ((ref.start is not None and dt < ref.start)
                    or (ref.end is not None and dt > ref.end)):
                raise ValueError("Source event lies outside its reference deployment interval")
            if ref.start is None or ref.end is None:
                counts["events_with_unverifiable_deployment_interval"] += 1
            if ref.animal in last_seen and dt < last_seen[ref.animal]:
                counts["source_order_backward_rows"] += 1
            last_seen[ref.animal] = dt
            candidate_events.append(Event(ref.animal, ref.tag, ref.group, ref.sex, ref.life_stage,
                                          ref.deployment, dt, lat, lon))
    candidate_events.sort(key=lambda event: (event.animal, event.dt, event.tag, event.deployment))
    events = []
    for _, grouped in groupby(candidate_events, key=lambda event: (event.animal, event.dt)):
        values = list(grouped)
        if len(values) > 1:
            signatures = {(event.tag, event.deployment, event.lat, event.lon) for event in values}
            if len(signatures) > 1:
                counts["conflicting_timestamp_groups"] += 1
                counts["conflicting_timestamp_rows_removed"] += len(values)
                counts["conflicting_tag_timestamp_groups"] += len({event.tag for event in values}) > 1
                continue
            counts["identical_duplicate_rows_removed"] += len(values) - 1
        events.append(values[0])
    audit = dict(counts)
    audit.update({"source_doi": SOURCE_DOI, "source_clock": "native naive timestamps; UTC versus GPS clock not independently verified",
                  "source_columns": list(fields), "present_source_outlier_fields": list(outlier_fields),
                  "present_accuracy_quality_fields": list(quality_fields),
                  "retained_events": len(events), "retained_animals": len({event.animal for event in events}),
                  "retained_tags": len({event.tag for event in events}),
                  "retained_rows_by_year": dict(sorted(Counter(event.year for event in events).items())),
                  "reference": reference_audit,
                  "limitations": ["A single reference group label does not establish social association, shared locations, or a common resource pool.",
                                  "Missing deployment dates prevent independent interval validation even when animal/tag pairs match uniquely.",
                                  "Absent HDOP, satellite counts, and error estimates prevent quantitative GPS accuracy gating.",
                                  "Only recorded source outlier flags are honored; no movement-speed exclusions or movement-effect filters are used.",
                                  "Year cohorts reuse biological individuals and must not be treated as independent animals."]})
    return events, audit, receipts


def haversine_km(origin: Event, end: Event) -> float:
    lat_a, lat_b = math.radians(origin.lat), math.radians(end.lat)
    delta_lon = math.radians(end.lon - origin.lon)
    h = (math.sin((lat_b - lat_a) / 2) ** 2
         + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2)
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(max(0.0, h))))


def make_steps(events):
    """Return origin-anchored adjacent 108–132-minute steps and aggregate counts.

    Sorting is within animal, followed by explicit same-tag/deployment/date/
    month checks. Rejected pairs do not replace endpoints or produce longer
    synthetic connections. No speed threshold is applied, including to fast
    steps that might merit a later, separately specified quality sensitivity.
    """
    ordered = sorted(events, key=lambda event: (event.animal, event.dt, event.tag, event.deployment))
    counts = Counter({"candidate_adjacent_pairs": 0, "tag_or_deployment_boundary_removed": 0,
                      "nonpositive_duration_removed": 0, "cross_source_month_removed": 0,
                      "cross_source_date_removed": 0, "outside_108_132_minutes_removed": 0,
                      "outside_2018_2020_removed": 0, "retained_steps": 0})
    steps = []
    for origin, end in zip(ordered, ordered[1:]):
        if origin.animal != end.animal:
            continue
        counts["candidate_adjacent_pairs"] += 1
        if origin.tag != end.tag or origin.deployment != end.deployment:
            counts["tag_or_deployment_boundary_removed"] += 1
            continue
        seconds = (end.dt - origin.dt).total_seconds()
        if seconds <= 0:
            counts["nonpositive_duration_removed"] += 1
            continue
        if not 2018 <= origin.year <= 2020 or not 2018 <= end.year <= 2020:
            counts["outside_2018_2020_removed"] += 1
            continue
        if (origin.year, origin.month) != (end.year, end.month):
            counts["cross_source_month_removed"] += 1
            continue
        if origin.day != end.day:
            counts["cross_source_date_removed"] += 1
            continue
        if not 108 * 60 <= seconds <= 132 * 60:
            counts["outside_108_132_minutes_removed"] += 1
            continue
        distance = haversine_km(origin, end)
        steps.append(Step(origin.animal, origin.tag, origin.group, origin.sex, origin.life_stage,
                          origin.deployment, origin.dt, origin.lat, origin.lon, end.dt,
                          distance, distance / (seconds / 3600), seconds / 60))
    counts["retained_steps"] = len(steps)
    audit = dict(counts)
    audit.update({"retained_animals": len({step.animal for step in steps}),
                  "retained_steps_by_year": dict(sorted(Counter(step.year for step in steps).items())),
                  "step_origin": "source timestamp, date, month, hour bin, and position",
                  "source_clock_verified_utc": False, "high_speed_filter_applied": False,
                  "hour_bin_width_hours": 6})
    return steps, audit


def source_lat_cos(events) -> float:
    """Internal projection cosine from all retained 2018–2020 source events."""
    if not events:
        raise ValueError("Cannot determine projection from an empty source")
    return math.cos(math.radians(math.fsum(event.lat for event in events) / len(events)))


def group_steps_by_month(steps):
    """Return internal ``(calendar_year, calendar_month) -> list[Step]``."""
    grouped = defaultdict(list)
    for step in steps:
        grouped[(step.year, step.month)].append(step)
    return dict(sorted(grouped.items()))
