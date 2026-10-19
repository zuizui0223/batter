#!/usr/bin/env python3
"""Reproduce anonymous, descriptive source-month 2D GPS overlap (NOT resource partition).

Source files must be obtained separately from their original Movebank DOI under
the applicable source rights. Never publish original tracking rows or IDs.
Requires only Python standard library.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PROFILES = {
    "wolf": {"doi": "10.5441/001/1.7vr1k987", "min_fixes": 10, "fastloc": False},
    "elephant": {"doi": "10.5441/001/1.403h24q5", "min_fixes": 40, "fastloc": False},
    "green_turtle": {"doi": "10.5441/001/1.313", "min_fixes": 10, "fastloc": True},
}


def haversine_km(a, b):
    a1, a2 = math.radians(a["lat"]), math.radians(b["lat"])
    dl = math.radians(b["lon"] - a["lon"])
    h = math.sin((a2 - a1) / 2) ** 2 + math.cos(a1) * math.cos(a2) * math.sin(dl / 2) ** 2
    return 12742 * math.asin(min(1.0, math.sqrt(h)))


def source_events(path: Path, profile):
    groups = defaultdict(list)
    counts = Counter()
    sha256 = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(block)
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        for rec in csv.DictReader(f):
            counts["source_rows"] += 1
            if rec.get("sensor-type", "").strip().lower() != "gps":
                counts["non_gps"] += 1
                continue
            if rec.get("visible", "").strip().lower() != "true":
                counts["invisible"] += 1
                continue
            ident, when = rec.get("individual-local-identifier", ""), rec.get("timestamp", "")
            try:
                latitude = float(rec["location-lat"])
                longitude = float(rec["location-long"])
                assert -90 <= latitude <= 90 and -180 <= longitude <= 180
                assert ident and when
                dt = datetime.strptime(when[:19], "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError, KeyError, AssertionError):
                counts["invalid_position_or_time_or_id"] += 1
                continue
            if profile["fastloc"]:
                try:
                    n_sat = float(rec["gps:satellite-count"])
                    residual = float(rec["wc:residual"])
                except (ValueError, TypeError, KeyError):
                    counts["missing_fastloc_quality"] += 1
                    continue
                if n_sat < 5 or residual >= 35:
                    counts["failed_fastloc_quality"] += 1
                    continue
            groups[ident].append({"dt": dt, "day": when[:10],
                                  "month": when[:7], "lat": latitude, "lon": longitude})
            counts["quality_pass_before_speed"] += 1
    retained = []
    for ident, values in groups.items():
        values.sort(key=lambda x: x["dt"])
        last = None
        for v in values:
            if last is not None:
                hours = (v["dt"] - last["dt"]).total_seconds() / 3600
                if hours <= 0:
                    counts["duplicate_or_backward_timestamp"] += 1
                    continue
                if profile["fastloc"] and haversine_km(last, v) / hours > 10:
                    counts["fastloc_speed_over_10_kmh"] += 1
                    continue
            retained.append((ident, v))
            last = v
    counts["retained_gps_fixes"] = len(retained)
    counts["retained_individuals"] = len(set(i for i, _ in retained))
    return retained, dict(counts), sha256.hexdigest()


def distribution(fixes, width_km, lat_cos, offset_x=0.0, offset_y=0.0):
    by_day = defaultdict(list)
    for x in fixes:
        by_day[x["day"]].append(x)
    histogram = defaultdict(float)
    for day in by_day.values():
        fix_weight = 1.0 / (len(by_day) * len(day))
        for v in day:
            x = math.floor((v["lon"] * 111.32 * lat_cos + offset_x) / width_km)
            y = math.floor((v["lat"] * 111.32 + offset_y) / width_km)
            histogram[(x, y)] += fix_weight
    return histogram


def overlap(hist_a, hist_b):
    return sum(min(p, hist_b[c]) for c, p in hist_a.items() if c in hist_b)


def month_statistics(fixes, lat_cos, min_fixes, min_days=5, min_pair_days=3):
    month_animals = defaultdict(lambda: defaultdict(list))
    for ident, v in fixes:
        month_animals[v["month"]][ident].append(v)
    monthly = []
    for month in sorted(month_animals):
        animals = [(ident, v) for ident, v in month_animals[month].items()
                   if len(v) >= min_fixes and len(set(q["day"] for q in v)) >= min_days]
        if len(animals) < 2:
            continue
        days = [set(q["day"] for q in seq) for ident, seq in animals]
        valid_pairs = [(i, j) for i in range(len(animals)) for j in range(i + 1, len(animals))
                       if len(days[i] & days[j]) >= min_pair_days]
        if not valid_pairs:
            continue
        item = {"month": month, "n_animals": len(animals), "n_pair_month_units": len(valid_pairs)}
        for km in (5, 10, 20):
            offsets = [(0.0, 0.0), (km / 2, 0.0), (0.0, km / 2), (km / 2, km / 2)]
            means = []
            for dx, dy in offsets:
                hist = [distribution(v, km, lat_cos, dx, dy) for ident, v in animals]
                score = [overlap(hist[i], hist[j]) for i, j in valid_pairs]
                val = sum(score) / len(score)
                means.append(val)
                if dx == 0 and dy == 0:
                    item["mean_O" + str(km)] = val
                    item["zero_pair_O" + str(km)] = sum(x == 0 for x in score)
            item["grid_shift_range_O" + str(km)] = [min(means), max(means)]
        monthly.append(item)
    return monthly


def analyze_csv(path: Path, label: str):
    profile = PROFILES[label]
    fixes, counts, sha = source_events(path, profile)
    if not fixes:
        raise ValueError("No valid GPS event records after source-specific checks")
    mean_lat = sum(q["lat"] for _, q in fixes) / len(fixes)
    months = month_statistics(fixes, math.cos(math.radians(mean_lat)), profile["min_fixes"])
    by_year = defaultdict(lambda: {"months": 0, "pair_month_units": 0,
                                   "sum_O10": 0.0, "zero_pair_O10": 0})
    for item in months:
        s = by_year[item["month"][:4]]
        s["months"] += 1
        s["pair_month_units"] += item["n_pair_month_units"]
        s["sum_O10"] += item["mean_O10"] * item["n_pair_month_units"]
        s["zero_pair_O10"] += item["zero_pair_O10"]
    annual = [{"year": year, "n_months": r["months"],
               "pair_month_units": r["pair_month_units"],
               "mean_O10": r["sum_O10"] / r["pair_month_units"],
               "zero_pair_O10": r["zero_pair_O10"]}
              for year, r in sorted(by_year.items())]
    return {
        "scope": "DESCRIPTIVE_2D_SPATIAL_USE_ONLY",
        "source": {"doi": profile["doi"], "original_event_sha256": sha, "label": label},
        "counts": counts,
        "method": {"season": "original UTC YYYY-MM", "min_month_fixes": profile["min_fixes"],
                   "min_month_dates": 5, "min_pair_shared_dates": 3,
                   "weight": "equal weight per observed individual date",
                   "projection": "source-mean-latitude fixed equirectangular, km approximation",
                   "grid_km": [5, 10, 20], "shift": "zero or half-grid offsets",
                   "fastloc_filter": ">=5 satellites, residual <35, next fix <=10km/h"
                   if profile["fastloc"] else "GPS row and visible flag only"},
        "annual": annual, "monthly": months,
        "limitations": [
            "R individual movement predictability, temporal encounters and independent resources are NOT measured.",
            "Pair-month records are repeatedly dependent within animals and studies; no p values.",
            "Same source or park need not mean same accessible ecological opportunities.",
            "2D UD overlap is not realized synchronous co-presence, competition or dietary overlap.",
            "Shared nesting origins and migration stage can dominate overlap; do not infer persistent personality.",
            "No identifiers, coordinates or original timestamps are exported in output.",
        ],
    }


def self_test():
    # Twelve records per animal, across six dates, share a common tile.
    base = datetime(2020, 1, 1)
    from datetime import timedelta
    a = [{"dt": base + timedelta(days=d, hours=h), "day": (base + timedelta(days=d)).strftime("%Y-%m-%d"),
          "month": "2020-01", "lat": 0.01, "lon": 0.01}
         for d in range(6) for h in range(2)]
    b = [dict(x) for x in a]
    same = month_statistics([("A", x) for x in a] + [("B", x) for x in b], 1.0, 10)
    assert len(same) == 1 and abs(same[0]["mean_O10"] - 1.0) < 1e-12
    for x in b:
        x["lat"], x["lon"] = 20.0, 20.0
    different = month_statistics([("A", x) for x in a] + [("B", x) for x in b], 1.0, 10)
    assert different[0]["mean_O10"] == 0.0
    assert different[0]["zero_pair_O10"] == 1
    print("PASS: same-place O=1, disjoint-place O=0; no raw IDs exported")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=list(PROFILES))
    parser.add_argument("--input", type=Path, help="Locally authorized original Movebank event CSV")
    parser.add_argument("--output", type=Path, help="Derived anonymized JSON file (default stdout)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.source or not args.input:
        parser.error("--source and --input are required except for --self-test")
    data = analyze_csv(args.input, args.source)
    msg = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(msg, encoding="utf-8")
    else:
        print(msg, end="")


if __name__ == "__main__":
    main()
