#!/usr/bin/env python3
"""Acquire two ORIGINAL Movebank sources; emit aggregate availability only.

Stdlib only. Full GPS sources are selected by total published byte size under
one 150 MB download budget. No identity, location, day, or movement effect is
emitted. Reference deployment dates are not evidence of valid tracking events.
"""
import argparse
from array import array
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import urllib.request

BASE = "https://datarepository.movebank.org/server/api/core/"
SOURCES = {
    "mule_deer": ("0e3a4577-b063-47d9-9d6b-edec949aa5fa", "10.5441/001/1.708", "Odocoileus hemionus"),
    "white_stork": ("520a64ae-2047-445d-af5f-7b961caeef79", "10.5441/001/1.4192t2j4_2", "Ciconia ciconia"),
}


def digest(path, algorithm="md5"):
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(url, path, offline):
    if not offline:
        with urllib.request.urlopen(url, timeout=60) as response:
            path.write_bytes(response.read())
    return json.loads(path.read_text())


def download(entry, cache, offline):
    path = cache / (entry["uuid"] + ".bin")
    if not path.exists() and not offline:
        with urllib.request.urlopen(entry["content_url"], timeout=120) as response, path.open("wb") as f:
            for block in iter(lambda: response.read(1024 * 1024), b""):
                f.write(block)
    if not path.exists():
        raise FileNotFoundError("Required original file absent: " + entry["uuid"])
    assert path.stat().st_size == entry["size_bytes"], "Original size mismatch"
    assert digest(path) == entry["publisher_md5"], "Original checksum mismatch"
    entry["downloaded_and_md5_verified"] = True
    entry["download_sha256"] = digest(path, "sha256")
    return path


def quantiles(values):
    v = sorted(values)
    if not v:
        return {"n": 0}
    out = {"n": len(v)}
    for label, q in [("min", 0), ("p05", .05), ("p25", .25), ("p50", .5), ("p75", .75), ("p95", .95), ("max", 1)]:
        x = (len(v) - 1) * q
        lo = math.floor(x)
        hi = math.ceil(x)
        out[label] = v[lo] + (v[hi] - v[lo]) * (x - lo)
    return out


def reference_summary(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = list(reader.fieldnames or [])
        rows = list(reader)
    animals = {r["animal-id"].strip() for r in rows if r.get("animal-id", "").strip()}
    tag_animals = defaultdict(set)
    for row in rows:
        if row.get("tag-id", "").strip():
            tag_animals[row["tag-id"].strip()].add(row.get("animal-id", "").strip())
    return {
        "rows": len(rows), "distinct_animals": len(animals),
        "distinct_tags": len(tag_animals),
        "tags_assigned_to_multiple_animals": sum(len(v) > 1 for v in tag_animals.values()),
        "distinct_deployments": len({r.get("deployment-id", "").strip() for r in rows} - {""}),
        "taxon_row_counts": dict(Counter(r.get("animal-taxon", "").strip() for r in rows)),
        "sex_row_counts": dict(Counter(r.get("animal-sex", "").strip() or "missing" for r in rows)),
        "deployment_start_year_row_counts": dict(sorted(Counter(r.get("deploy-on-date", "")[:4] or "missing" for r in rows).items())),
        "distinct_nonempty_site_labels": len({r.get("study-site", "").strip() for r in rows} - {""}),
        "distinct_nonempty_group_labels": len({r.get("animal-group-id", "").strip() for r in rows} - {""}),
        "columns": columns,
    }, animals


def event_summary(paths, reference_animals, expected_taxon):
    counts = Counter()
    sensor_counts, visible_counts, taxon_counts = Counter(), Counter(), Counter()
    times, days, tags = defaultdict(lambda: array("d")), defaultdict(set), defaultdict(set)
    raw_animals, unknown_animals = set(), set()
    all_columns = set()
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            required = {"sensor-type", "visible", "individual-local-identifier", "individual-taxon-canonical-name", "location-long", "location-lat", "timestamp", "tag-local-identifier"}
            assert required.issubset(reader.fieldnames or []), "Required original GPS columns missing"
            all_columns.update(reader.fieldnames or [])
            for row in reader:
                counts["all_rows"] += 1
                sensor = row.get("sensor-type", "").strip()
                visible = row.get("visible", "").strip().lower()
                taxon = row.get("individual-taxon-canonical-name", "").strip()
                animal = row.get("individual-local-identifier", "").strip()
                sensor_counts[sensor or "missing"] += 1
                visible_counts[visible or "missing"] += 1
                taxon_counts[taxon or "missing"] += 1
                if animal:
                    raw_animals.add(animal)
                if sensor.lower() != "gps":
                    counts["excluded_non_gps"] += 1
                    continue
                if visible not in {"true", "1"}:
                    counts["excluded_not_explicitly_visible"] += 1
                    continue
                if not animal:
                    counts["excluded_missing_animal"] += 1
                    continue
                if taxon != expected_taxon:
                    counts["excluded_nonmatching_or_missing_taxon"] += 1
                    continue
                try:
                    lon, lat = float(row["location-long"]), float(row["location-lat"])
                    assert math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90
                except (ValueError, KeyError, AssertionError, TypeError):
                    counts["excluded_invalid_coordinates"] += 1
                    continue
                try:
                    dt = datetime.fromisoformat(row["timestamp"].strip().replace("Z", "+00:00"))
                    if dt.tzinfo:
                        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                    epoch = (dt - datetime(1970, 1, 1)).total_seconds()
                except (ValueError, KeyError, TypeError):
                    counts["excluded_invalid_timestamp"] += 1
                    continue
                counts["valid_visible_gps_rows"] += 1
                if animal not in reference_animals:
                    unknown_animals.add(animal)
                key = (dt.year, animal)
                times[key].append(epoch)
                days[key].add(dt.date().toordinal())
                tag = row.get("tag-local-identifier", "").strip()
                if tag:
                    tags[key].add(tag)
    years = []
    for year in sorted({y for y, _ in times}):
        keys = [key for key in times if key[0] == year]
        daily = Counter(d for key in keys for d in days[key])
        intervals, within_day_intervals = array("d"), array("d")
        duplicate_times = 0
        individual_median_cadences = []
        for key in keys:
            t = sorted(times[key])
            gaps = [b - a for a, b in zip(t, t[1:]) if b > a]
            intervals.extend(gaps)
            duplicate_times += sum(b == a for a, b in zip(t, t[1:]))
            within_day_intervals.extend(b - a for a, b in zip(t, t[1:]) if b > a and math.floor(a / 86400) == math.floor(b / 86400))
            if gaps:
                individual_median_cadences.append(quantiles(gaps)["p50"])
        pair_days = [len(days[a] & days[b]) for a, b in combinations(keys, 2)]
        years.append({
            "calendar_year": year, "animals": len(keys),
            "valid_visible_gps_rows": sum(len(times[key]) for key in keys),
            "distinct_tags": len(set().union(*(tags[key] for key in keys))),
            "animals_with_multiple_tags": sum(len(tags[key]) > 1 for key in keys),
            "animals_at_least_100_rows_7_observed_days": sum(len(times[key]) >= 100 and len(days[key]) >= 7 for key in keys),
            "observed_days_per_animal": quantiles(len(days[key]) for key in keys),
            "daily_animals_on_observed_calendar_days": quantiles(daily.values()),
            "calendar_days_with_at_least_n_animals": {str(n): sum(v >= n for v in daily.values()) for n in [1, 2, 5, 10, 20, 50, 100]},
            "pairwise_shared_calendar_days_all_pairs_including_zero": quantiles(pair_days),
            "animal_pairs_with_at_least_7_shared_days": sum(v >= 7 for v in pair_days),
            "animal_pairs_with_at_least_28_shared_days": sum(v >= 28 for v in pair_days),
            "within_animal_year_positive_interfix_seconds": quantiles(intervals),
            "within_animal_same_day_positive_interfix_seconds": quantiles(within_day_intervals),
            "across_animal_median_positive_interfix_seconds": quantiles(individual_median_cadences),
            "duplicate_animal_timestamps": duplicate_times,
        })
    return {
        "filter_counts": dict(counts), "source_sensor_row_counts": dict(sensor_counts),
        "source_visible_row_counts": dict(visible_counts), "source_taxon_row_counts": dict(taxon_counts),
        "source_columns": sorted(all_columns), "raw_distinct_animals": len(raw_animals),
        "valid_distinct_animals_all_years": len({animal for _, animal in times}),
        "valid_animals_absent_from_reference": len(unknown_animals), "cohorts": years,
    }


def valid_events(paths, expected_taxon):
    """Repeat the declared non-effect filter without emitting source records."""
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                animal = row.get("individual-local-identifier", "").strip()
                if (row.get("sensor-type", "").strip().lower() != "gps"
                    or row.get("visible", "").strip().lower() not in {"true", "1"}
                    or not animal or row.get("individual-taxon-canonical-name", "").strip() != expected_taxon):
                    continue
                try:
                    lon, lat = float(row["location-long"]), float(row["location-lat"])
                    if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
                        continue
                    dt = datetime.fromisoformat(row["timestamp"].strip().replace("Z", "+00:00"))
                    if dt.tzinfo:
                        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
                except (ValueError, KeyError, TypeError):
                    continue
                yield animal, dt, lon, lat


def common_place_summary(paths, expected_taxon):
    """All 36 months, fixed coarse context support; no movement outcomes."""
    total_lat, count = 0.0, 0
    for _, _, _, lat in valid_events(paths, expected_taxon):
        total_lat += lat
        count += 1
    if not count:
        return {"status": "no_valid_source_events"}
    xscale = 111320.0 * math.cos(math.radians(total_lat / count))
    contexts = defaultdict(lambda: defaultdict(Counter))
    raw_animals = defaultdict(set)
    for animal, dt, lon, lat in valid_events(paths, expected_taxon):
        if not 2018 <= dt.year <= 2020:
            continue
        month = (dt.year, dt.month)
        raw_animals[month].add(animal)
        cell = (math.floor(lon * xscale / 5000), math.floor(lat * 111320.0 / 5000), dt.hour // 6)
        contexts[month][(animal, cell)][dt.date().toordinal()] += 1
    monthly = []
    for year in range(2018, 2021):
        for month_number in range(1, 13):
            month = (year, month_number)
            by_context = defaultdict(dict)
            for (animal, cell), date_counts in contexts[month].items():
                if sum(date_counts.values()) >= 15 and len(date_counts) >= 2:
                    by_context[cell][animal] = date_counts
            shared = {cell: animals for cell, animals in by_context.items() if len(animals) >= 2}
            fixes, observed_dates, cotagged_dates = Counter(), defaultdict(set), defaultdict(set)
            for animals in shared.values():
                date_participants = Counter(date for counts in animals.values() for date in counts)
                for animal, date_counts in animals.items():
                    fixes[animal] += sum(date_counts.values())
                    observed_dates[animal].update(date_counts)
                    cotagged_dates[animal].update(date for date in date_counts if date_participants[date] >= 2)
            supported = {animal for animal in fixes if fixes[animal] >= 15 and len(observed_dates[animal]) >= 3}
            monthly.append({"calendar_year": year, "calendar_month": month_number,
                "n_raw_animals": len(raw_animals[month]), "n_shared_place_supported_animals": len(supported),
                "n_common_contexts": len(shared),
                "shared_context_observed_dates_per_supported_animal": quantiles(len(observed_dates[animal]) for animal in supported),
                "cotagged_dates_per_supported_animal": quantiles(len(cotagged_dates[animal]) for animal in supported)})
    return {"status": "fixed_all_months_coarse_common_place_support_audited", "monthly": monthly,
        "rules": {"calendar_years": [2018, 2019, 2020], "calendar_months": list(range(1, 13)),
            "grid": "Equirectangular, 111320 m/degree, longitude scaled by cosine of the all-valid-source-row mean latitude, origin (0 degrees, 0 degrees). Mean latitude is not emitted.",
            "grid_m": 5000, "clock_bin_hours": 6,
            "clock_basis": "UTC-like source clock; timezone-aware times normalized to UTC, naive source timestamps retained. Source README allows UTC or GPS time; GPS/UTC offset unresolved.",
            "animal_context_min_original_fixes": 15, "animal_context_min_distinct_dates": 2,
            "shared_context_min_qualifying_animals": 2, "final_animal_min_fixes_in_own_qualifying_shared_contexts": 15,
            "final_animal_min_distinct_dates_in_own_qualifying_shared_contexts": 3,
            "cotagged_dates": "For each supported animal, distinct dates with another context-qualified animal in at least one same 5 km/6 h context. Other animal need not pass the final 3-date condition. This is not exact fix simultaneity.",
            "selection": "All 36 calendar months retained, including zero-supported months; no favorable-month or effect selection."},
        "source_mean_latitude_valid_rows": count, "site_population_verified": False,
        "prediction_or_movement_effects_computed": False, "biological_gate_pass_claimed": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache", type=Path, default=Path("/tmp/stork_deer_preflight_20261020"))
    p.add_argument("--offline", action="store_true", help="Recompute from checksum-verified original files and cached API responses")
    p.add_argument("--out", type=Path, default=Path(__file__).with_name("NEXT_SOURCE_STORK_DEER_RECEIPT_2026_10_20.json"))
    args = p.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": 1, "as_of": "2026-10-20", "script_sha256": digest(Path(__file__), "sha256"),
        "scope": "Two pre-existing candidates; original source acquisition and aggregate temporal availability only",
        "gps_download_budget_bytes": 150000000, "gps_bytes_downloaded": 0, "sources": [],
        "methods": {"gps_selection": "Complete source GPS sets only, under a total 150 MB budget; deer before stork. File size is the only source acquisition criterion.",
            "event_filter": "Source GPS sensor, explicit visible TRUE/1, nonempty animal ID, source expected taxon, finite in-range coordinates and parseable timestamp; no movement or effect filter.",
            "calendar_basis": "Native source timestamps. README defines timestamp units as UTC or GPS time; naive timestamps are not silently asserted to be verified UTC. No GPS/UTC leap-second correction.",
            "concurrency": "Same recorded calendar day anywhere in the source, not simultaneous fixes or shared habitat/site.",
            "cadence": "Sorted adjacent timestamps within animal and year; positive gaps only, duplicate timestamps separately counted; row-weighted and animal-median summaries both reported.",
            "quantiles": "Linear interpolation at (n-1)*q.",
            "privacy": "No animal IDs, tag IDs, positions, exact dates, or per-animal rows emitted."},
        "same_site_common_space_verified": False, "identity_or_partitioning_effect_computed": False,
        "primary_inference_eligible": False,
        "interpretation_limits": [
            "Calendar-year animals can recur across years and are not independent animals when year counts are summed.",
            "The 100-row/7-day count describes temporal coverage only; it is not a replacement admission threshold for any frozen analysis.",
            "Simultaneous-day source participation does not verify shared locations, a common resource pool, social association, or ecological partitioning.",
            "Source visible and valid coordinate ranges do not establish location error, behavioral comparability, or biological independence.",
            "Reference sex/site/deployment coverage and tag reuse must inform any later cohort design before movement effects are inspected.",
        ]}
    for label, (uid, doi, taxon) in SOURCES.items():
        item_url = BASE + "items/" + uid
        item = read_json(item_url, args.cache / (label + "_item.json"), args.offline)
        bundles = read_json(item_url + "/bundles?size=100", args.cache / (label + "_bundles.json"), args.offline)
        assert bundles["page"]["totalPages"] == 1, "Bundle pagination requires explicit review"
        original = next(b for b in bundles["_embedded"]["bundles"] if b["name"] == "ORIGINAL")
        original_url = original["_links"]["bitstreams"]["href"] + "?size=100"
        listing = read_json(original_url, args.cache / (label + "_original.json"), args.offline)
        assert listing["page"]["totalPages"] == 1, "Original manifest pagination requires explicit review"
        manifest = []
        for b in listing["_embedded"]["bitstreams"]:
            assert b["checkSum"]["checkSumAlgorithm"].upper() == "MD5"
            role = "reference" if "reference-data" in b["name"].lower() else "readme" if b["name"].lower() == "readme.txt" else "gps" if ("-gps-" in b["name"].lower() or (label == "mule_deer" and b["name"].lower().endswith(".csv"))) else "other_sensor"
            manifest.append({"uuid": b["uuid"], "filename": b["name"], "role": role, "size_bytes": b["sizeBytes"],
                "publisher_md5": b["checkSum"]["value"], "content_url": b["_links"]["content"]["href"], "downloaded_and_md5_verified": False})
        source = {"label": label, "doi": doi, "package_uuid": uid, "title": item["name"], "item_api_url": item_url,
            "original_bundle_uuid": original["uuid"], "original_manifest_url": original_url,
            "item_response_sha256": digest(args.cache / (label + "_item.json"), "sha256"),
            "original_manifest_response_sha256": digest(args.cache / (label + "_original.json"), "sha256"),
            "rights": [v["value"] for v in item["metadata"].get("dc.rights", [])],
            "rights_urls": [v["value"] for v in item["metadata"].get("dc.rights.uri", [])], "original_file_manifest": manifest}
        assert sum(entry["role"] == "reference" for entry in manifest) == 1, "Require one original reference file"
        for entry in manifest:
            if entry["role"] in {"reference", "readme"}:
                path = download(entry, args.cache, args.offline)
                if entry["role"] == "reference":
                    source["reference"], reference_animals = reference_summary(path)
        gps = [entry for entry in manifest if entry["role"] == "gps"]
        total = sum(entry["size_bytes"] for entry in gps)
        source["complete_gps_set_size_bytes"] = total
        if gps and total <= result["gps_download_budget_bytes"] - result["gps_bytes_downloaded"]:
            paths = [download(entry, args.cache, args.offline) for entry in gps]
            assert all(path.suffix == ".bin" for path in paths)
            assert all(entry["filename"].lower().endswith(".csv") for entry in gps), "Compressed GPS needs an explicit parser"
            source["event_availability"] = event_summary(paths, reference_animals, taxon)
            source["common_place_support"] = common_place_summary(paths, taxon)
            source["status"] = "original_gps_verified_and_aggregate_temporal_availability_computed"
            result["gps_bytes_downloaded"] += total
        else:
            source["status"] = "original_reference_verified_full_gps_deferred_size_budget"
            source["event_availability"] = None
        source["same_site_common_space_verified"] = False
        source["primary_inference_eligible"] = False
        result["sources"].append(source)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"receipt": str(args.out), "sources": [{"label": s["label"], "status": s["status"], "reference_animals": s["reference"]["distinct_animals"], "gps_bytes": s["complete_gps_set_size_bytes"]} for s in result["sources"]]}))


if __name__ == "__main__":
    main()
