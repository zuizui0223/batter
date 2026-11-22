#!/usr/bin/env python3
"""Outcome-blind lunar-exposure support audit for pinned public Movebank GPS panels.

Reads GPS XY, timestamps, IDs, source outlier flags, and non-empty native-height
presence only. NEVER reads the numeric value of height or an animal response.
This script tests data support; it does not estimate a lunar biological effect.
"""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import urllib.request

import swisseph as swe

PINNED_DOIS = {
    "10.5441/001/1.278", "10.5441/001/1.282", "10.5441/001/1.321",
    "10.5441/001/1.322", "10.5441/001/1.52nn82r9", "10.5441/001/1.k8n02jn8",
}
HEIGHT_FIELDS = (
    "height_above_msl", "height_above_ellipsoid", "height_raw",
    "height_above_ground", "height_above_ground_level",
)
OUTLIERS = ("manually_marked_outlier", "import_marked_outlier", "algorithm_marked_outlier")
NIGHT_FIX_MIN = 30
EXPOSURE_FIX_MIN = 20

def canon(x):
    return re.sub(r"_+", "_", str(x).strip().lower().replace("-", "_").replace(" ", "_").replace(":", "_")).strip("_")

def truthy(x):
    return str(x).strip().lower() in {"1", "true", "t", "yes", "y"}

def as_utc(x):
    dt = datetime.fromisoformat(str(x).strip().replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def local_solar_night(dt, lon):
    """Approximate local solar clock; shift by 12h so dusk/dawn share a night."""
    return (dt + timedelta(hours=lon / 15 - 12)).date().isoformat()

def moon_sun_state(dt, lat, lon):
    """Geometry-only screening; no clouds, sky brightness, vegetation or lux."""
    dt = as_utc(dt.isoformat())
    h = dt.hour + dt.minute / 60 + dt.second / 3600
    jd = swe.julday(dt.year, dt.month, dt.day, h)
    flag = swe.FLG_MOSEPH | swe.FLG_EQUATORIAL
    moon = swe.calc_ut(jd, swe.MOON, flag)[0]
    sun = swe.calc_ut(jd, swe.SUN, flag)[0]
    pos = (lon, lat, 0.0)
    moon_alt = swe.azalt(jd, swe.EQU2HOR, pos, 0.0, 10.0, moon[:3])[1]
    sun_alt = swe.azalt(jd, swe.EQU2HOR, pos, 0.0, 10.0, sun[:3])[1]
    illuminated_fraction = swe.pheno_ut(jd, swe.MOON, swe.FLG_MOSEPH)[1]
    if sun_alt >= -12:
        return "twilight", illuminated_fraction
    if illuminated_fraction >= .80 and moon_alt >= 10:
        return "bright", illuminated_fraction
    if illuminated_fraction <= .20 or moon_alt <= -5:
        return "dark", illuminated_fraction
    return "intermediate", illuminated_fraction

def classify_fix(dt, lat, lon, cache):
    # 15-minute, 0.25-degree grid for source-only screening, not model exposure.
    b = int(dt.timestamp()) // 900
    key = (b, round(lat * 4) / 4, round(lon * 4) / 4)
    if key not in cache:
        dt_bin = datetime.fromtimestamp(b * 900 + 450, tz=timezone.utc)
        cache[key] = moon_sun_state(dt_bin, key[1], key[2])[0]
    return cache[key]

def source_rows(spec):
    req = urllib.request.Request(spec["content_url"], headers={"User-Agent": "batter-lunar-source-gate-v1/1.0"})
    with urllib.request.urlopen(req, timeout=240) as resp:
        raw = resp.read()
    if len(raw) != spec["size_bytes"] or hashlib.md5(raw).hexdigest() != spec["checksum"]:
        raise RuntimeError("pinned source size/hash mismatch")
    return csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace"), newline=""))

def evaluate_source(spec, rows):
    original_headers = list(rows.fieldnames or [])
    names = [canon(k) for k in original_headers]
    if len(set(names)) != len(names):
        raise ValueError("source header collision")
    height = next((x for x in HEIGHT_FIELDS if x in names), None)
    if not height:
        return {"doi": spec["doi"], "status": "no_native_height", "outcome_opened": False}
    has_outliers = any(n in names for n in OUTLIERS)
    per_animal_night = defaultdict(Counter)
    cache = {}
    n_usable = 0
    for source_row in rows:
        row = {canon(k): v for k, v in source_row.items() if k is not None}
        if has_outliers and any(truthy(row.get(n)) for n in OUTLIERS):
            continue
        if not has_outliers and "visible" in row and str(row.get("visible") or "").strip() and not truthy(row["visible"]):
            continue
        # Critical: only test height field presence as a string; DO NOT parse it.
        if not str(row.get(height) or "").strip():
            continue
        animal = str(row.get("individual_local_identifier") or row.get("animal_id") or row.get("individual_id") or row.get("tag_local_identifier") or "").strip()
        if not animal:
            continue
        try:
            lat = float(row["location_lat"])
            lon = float(row["location_long"])
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                continue
            dt = as_utc(row["timestamp"])
        except (KeyError, ValueError, TypeError, OverflowError):
            continue
        night = local_solar_night(dt, lon)
        exposure = classify_fix(dt, lat, lon, cache)
        per_animal_night[(animal, night)][exposure] += 1
        n_usable += 1
    by_animal = defaultdict(lambda: {"bright": set(), "dark": set()})
    by_night = defaultdict(Counter)
    n_transition = 0
    n_eligible = 0
    for (animal, night), c in per_animal_night.items():
        n_dark = c["dark"]
        n_bright = c["bright"]
        if sum(c.values()) < NIGHT_FIX_MIN:
            continue
        n_eligible += 1
        for exposure in ("bright", "dark"):
            if c[exposure] >= EXPOSURE_FIX_MIN:
                by_animal[animal][exposure].add(night)
                by_night[night][exposure] += 1
        if n_dark >= EXPOSURE_FIX_MIN and n_bright >= EXPOSURE_FIX_MIN:
            n_transition += 1
    dual_bats = sum(bool(v["dark"] and v["bright"]) for v in by_animal.values())
    replicated_bats = sum(len(v["dark"]) >= 2 and len(v["bright"]) >= 2 for v in by_animal.values())
    eligible_dates = sorted(by_night)
    span = (datetime.fromisoformat(eligible_dates[-1]) - datetime.fromisoformat(eligible_dates[0])).days if len(eligible_dates) > 1 else 0
    qualified = replicated_bats >= 5 and span >= 35
    return {
        "doi": spec["doi"], "title": spec["title"], "source_checksum_md5": spec["checksum"],
        "native_height_field": height, "outcome_opened": False,
        "status": "support_pass" if qualified else "insufficient_within_animal_lunar_replication",
        "usable_fix_presence_count": n_usable, "eligible_individual_nights": n_eligible,
        "distinct_eligible_nights": len(eligible_dates), "night_span_days": span,
        "animals_with_both_exposures": dual_bats,
        "animals_with_at_least_two_bright_and_two_dark_nights": replicated_bats,
        "individual_nights_with_within_night_bright_dark_transition": n_transition,
        "moon_geometry_cache_cells": len(cache), "supports_confirmatory_within_animal_test": qualified,
    }

def main():
    cfg = json.loads(Path("config/bat_panel_sources_v1.json").read_text(encoding="utf-8"))
    sources = [s for s in cfg["sources"] if s["doi"] in PINNED_DOIS]
    if len(sources) != 6:
        raise SystemExit("expected six pinned public panel sources")
    reports = []
    for s in sources:
        try:
            reports.append(evaluate_source(s, source_rows(s)))
        except Exception as e:
            reports.append({"doi": s["doi"], "status": "source_failure", "reason": f"{type(e).__name__}: {e}", "outcome_opened": False})
    dest = Path("results/lunar_source_exposure_support_v1.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"audit": "lunar_source_exposure_v1", "outcomes_opened": False, "results": reports}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"results": reports, "outcomes_opened": False}, indent=2))
    return 0 if all(r["status"] != "source_failure" for r in reports) else 2

if __name__ == "__main__":
    raise SystemExit(main())
