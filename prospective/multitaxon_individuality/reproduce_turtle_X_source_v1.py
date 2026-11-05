#!/usr/bin/env python3
"""Reproduce X-only 2018 green turtle exploratory geographic overlap, without IDs.

NOT a test of ecological niche or resource sharing, R identity, T synchrony
or E habitat divergence. DOI 10.5441/001/1.313; source licensed CC0 in the
published Movebank package. User supplies legitimate original Movebank CSVs.

Model: all independently source-identified Chelonia mydas deployments in
2018-07 at original source study site Diego Garcia, first 30 days after
deployment, animal×timestamp uniqueness, GPS fixes only, source UTC assumed.
Daily-balanced observed XY grid occupancy with no pseudocount smoothing;
Lambert cylindrical equal area; 0.1/0.25/0.5/1/2/5/10/25 km. No ID/coordinates
in outputs. Coarse nominal 25 km was inspected before finer exploratory grids.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from datetime import datetime
from pathlib import Path

EARTH_KM = 6371.0088
GRID_KM = (.1, .25, .5, 1, 2, 5, 10, 25)
DAY_SECONDS = 86400


def parse_time(value: str) -> datetime:
    value = value.strip().replace("Z", "+00:00")
    t = datetime.fromisoformat(value)
    # Convert timezone-aware timestamps to UTC; original naive Movebank
    # source timestamps follow documented UTC source convention.
    if t.tzinfo:
        from datetime import timezone
        t = t.astimezone(timezone.utc).replace(tzinfo=None)
    return t


def source_deployments(reference_csv: Path, year_month: str = "2018-07") -> dict[str, datetime]:
    known = {}
    sites = set()
    with reference_csv.open(newline="", encoding="utf-8-sig") as inp:
        for row in csv.DictReader(inp):
            day = (row.get("deploy-on-date") or "").strip()
            if not day.startswith(year_month):
                continue
            if (row.get("animal-taxon") or "").strip() != "Chelonia mydas":
                continue
            site = (row.get("study-site") or "").strip()
            sites.add(site)
            tag = (row.get("animal-id") or "").strip()
            if not tag:
                continue
            if tag in known:
                raise ValueError("Multiple release records for one original source ID in the selected original month")
            known[tag] = parse_time(day)
    assert sites == {"Diego Garcia"}, "Original source site or subgroup changed"
    assert len(known) == 12, "Original July 2018 reference cohort n changed"
    return known


def source_tracks(reference: dict[str, datetime], events_csv: Path) -> dict[str, dict[str, list[tuple[float,float]]]]:
    histories: dict[str, dict[str,list[tuple[float,float]]]] = {}
    seen = set()
    with events_csv.open(newline="", encoding="utf-8-sig") as inp:
        reader = csv.DictReader(inp)
        required = {"individual-local-identifier", "timestamp", "location-long",
                    "location-lat", "sensor-type"}
        if not required <= set(reader.fieldnames or ()):
            raise ValueError("Source is missing original GPS time/id/location/sensor columns")
        for record in reader:
            tag = (record.get("individual-local-identifier") or "").strip()
            start = reference.get(tag)
            if start is None:
                continue
            if str(record.get("visible", "")).lower() == "false" or (
                    str(record.get("algorithm-marked-outlier", "")).lower() == "true"
            ):
                continue
            if (record.get("sensor-type") or "").lower().strip() != "gps":
                continue
            timestamp = (record.get("timestamp") or "").strip()
            try:
                time = parse_time(timestamp)
                elapsed = (time-start).total_seconds()/DAY_SECONDS
                lon, lat = float(record["location-long"]), float(record["location-lat"])
            except (TypeError,ValueError,KeyError):
                continue
            if not(0 <= elapsed < 30 and math.isfinite(lon) and math.isfinite(lat)
                   and abs(lon) <= 180 and abs(lat) <= 90):
                continue
            key = (tag, timestamp)
            if key in seen:
                continue
            seen.add(key)
            # Lambert cylindrical equal-area standard parallel 0; kilometers.
            lon_rad = math.radians(lon)
            lat_rad = math.radians(lat)
            xy = (EARTH_KM*lon_rad, EARTH_KM*math.sin(lat_rad))
            histories.setdefault(tag,{}).setdefault(time.date().isoformat(),[]).append(xy)
    return histories


def profiles(histories: dict, grid_km: float) -> list[dict[tuple[int,int],float]]:
    output = []
    for days in histories.values():
        cellmass: dict[tuple[int,int],float] = {}
        for xy in days.values():
            weight = 1/(len(days)*len(xy))
            for x,y in xy:
                cell = (math.floor(x/grid_km), math.floor(y/grid_km))
                cellmass[cell] = cellmass.get(cell,0.0)+weight
        assert abs(sum(cellmass.values())-1) < 1e-9
        output.append(cellmass)
    return output


def pair_overlaps(pp: list[dict]) -> list[float]:
    values = []
    for i in range(len(pp)):
        for j in range(i+1,len(pp)):
            a,b = pp[i],pp[j]
            if len(a)>len(b):
                a,b = b,a
            mass = sum(min(x, b.get(k,0.0)) for k,x in a.items())
            values.append(max(0.0,min(1.0,mass)))
    return values


def calculate(reference_csv: Path, original_gps_csv: Path) -> dict:
    reference = source_deployments(reference_csv)
    observations = source_tracks(reference, original_gps_csv)
    assert len(observations) == 12, "Original 2018 source cohort GPS individual n drift"
    # Stable ordering; identities discarded after group aggregation.
    observations = dict(sorted(observations.items()))
    recs = [sum(map(len,days.values())) for days in observations.values()]
    days_per = [len(days) for days in observations.values()]
    assert sum(recs)==2762 and min(recs)>=30 and min(days_per)>=3
    out = {}
    for km in GRID_KM:
        vals = sorted(pair_overlaps(profiles(observations,km)))
        assert len(vals)==66
        out[str(km)] = {
            "n_animals":12, "n_dependent_pairs":66,
            "mean":statistics.mean(vals),
            "upper_median":vals[len(vals)//2],
            "minimum":vals[0], "maximum":vals[-1],
            "n_pairs_positive":sum(z>0 for z in vals),
        }
    return {
        "cohort":"Chelonia mydas Diego Garcia; original 2018-07 release month",
        "source_doi":"10.5441/001/1.313",
        "original_gps_positions_first30days":sum(recs),
        "source_animals":len(observations),
        "dependent_animal_pairs":66,
        "position_counts_min_median_max": [min(recs), sorted(recs)[len(recs)//2], max(recs)],
        "distinct_calendar_days_min_median_max":[min(days_per), sorted(days_per)[len(days_per)//2], max(days_per)],
        "source_overlap_X_by_grid_km":out,
        "independent_resource_or_diet_E":None,
        "temporal_physical_encounter_T":None,
        "heldout_movement_identity_R":None,
        "original_animal_ids_or_locations_exported":False,
    }


def check_fixed_audit(computed: dict, snapshot: Path) -> None:
    original = json.loads(snapshot.read_text(encoding="utf8"))
    assert original["schema_version"] == 1
    expected = original["grid_sensitivity"]["scales"]
    assert original["source_cohort"]["unique_georeferenced_individual_timestamp_events"] == (
        computed["original_gps_positions_first30days"] == 2762
    )
    assert len(expected) == len(GRID_KM)
    for item in expected:
        key = str(item["km"])
        assert key in computed["source_overlap_X_by_grid_km"]
        new = computed["source_overlap_X_by_grid_km"][key]
        assert abs(new["mean"] - item["mean_pair_overlap"]) < 1e-8
        assert abs(new["upper_median"] - item["median_pair_overlap"]) < 1e-8
        assert abs(new["minimum"] - item["min_pair_overlap"]) < 1e-8
        assert abs(new["maximum"] - item["max_pair_overlap"]) < 1e-8
        assert new["n_pairs_positive"] == item["n_pairs_with_positive_overlap"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--reference", type=Path, required=True)
    p.add_argument("--events", type=Path, required=True)
    p.add_argument("--audit", type=Path, default=Path(__file__).with_name("EXPLORATORY_GREEN_TURTLE_2018_SOURCE_X_SCALE_V1.json"))
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    x = calculate(a.reference,a.events)
    check_fixed_audit(x,a.audit)
    if a.out:
        a.out.write_text(json.dumps(x,indent=2)+"\n",encoding="utf8")
    else:
        print(json.dumps(x,indent=2))
    print("PASS original 2018 turtle X source-replay; NOT ecological resource use, R, T, E, significance, or macro generality")


if __name__=="__main__":
    main()
