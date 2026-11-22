#!/usr/bin/env python3
"""Post-v1, pre-height matched lunar-exposure support audit.

Inputs: IDs, source outlier flags, timestamps, GPS XY, height-string presence.
No numeric GPS heights are ever parsed, modeled or reported.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
import math
from pathlib import Path

from prospective.lunar_3d.lunar_source_gate_v1 import (
    PINNED_DOIS, HEIGHT_FIELDS, OUTLIERS, canon, truthy, as_utc,
    local_solar_night, classify_fix, source_rows,
)

CELL_DEG = 0.05  # ~5.5 km latitude, approximate longitude; not a meter-exact grid.
CLOCK_HOURS = 2
MIN_FIX_PER_EXPOSURE = 20
MIN_NIGHT_PER_EXPOSURE = 2
MAX_DAYS_BETWEEN_EXPOSURES = 45
MIN_BATS_MATCHED = 5

def summarize(counts):
    eligible = []
    for key, values in counts.items():
        dark, bright = values["dark"], values["bright"]
        if len(dark) < MIN_NIGHT_PER_EXPOSURE or len(bright) < MIN_NIGHT_PER_EXPOSURE:
            continue
        if sum(dark.values()) < MIN_FIX_PER_EXPOSURE or sum(bright.values()) < MIN_FIX_PER_EXPOSURE:
            continue
        ddates = [datetime.fromisoformat(d) for d in dark]
        bdates = [datetime.fromisoformat(d) for d in bright]
        closest = min(abs((d-b).days) for d in ddates for b in bdates)
        if closest > MAX_DAYS_BETWEEN_EXPOSURES:
            continue
        eligible.append((key, closest, len(dark), len(bright)))
    return {
        "matched_strata": len(eligible),
        "matched_individuals": len({k[0] for k,_,_,_ in eligible}),
        "minimum_cross_exposure_night_gap_days": min((x[1] for x in eligible), default=None),
        "max_nights_per_exposure_in_any_matched_stratum": max(
            (min(x[2],x[3]) for x in eligible), default=0
        ),
        "matched_support_pass": len({k[0] for k,_,_,_ in eligible}) >= MIN_BATS_MATCHED,
    }

def evaluate_source(spec, rows):
    headers = [canon(c) for c in rows.fieldnames or []]
    if len(set(headers)) != len(headers):
        raise ValueError("header name collision")
    height = next((h for h in HEIGHT_FIELDS if h in headers), None)
    if height is None:
        return {"doi": spec["doi"], "status": "missing_native_height_presence", "height_values_opened": False}
    has_outliers = any(h in headers for h in OUTLIERS)
    counts = defaultdict(lambda: {"bright": Counter(), "dark": Counter()})
    cache = {}
    used = 0
    for raw in rows:
        row = {canon(k): v for k, v in raw.items() if k is not None}
        if has_outliers and any(truthy(row.get(h)) for h in OUTLIERS):
            continue
        if not has_outliers and "visible" in row and str(row.get("visible") or "").strip() and not truthy(row["visible"]):
            continue
        if not str(row.get(height) or "").strip():
            continue  # no numeric height evaluation
        animal = str(row.get("individual_local_identifier") or row.get("animal_id") or
                     row.get("individual_id") or row.get("tag_local_identifier") or "").strip()
        if not animal:
            continue
        try:
            lat, lon = float(row["location_lat"]), float(row["location_long"])
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                continue
            dt = as_utc(row["timestamp"])
        except (KeyError, ValueError, TypeError, OverflowError):
            continue
        exposure = classify_fix(dt, lat, lon, cache)
        if exposure not in {"bright", "dark"}:
            continue
        local_hour = (dt + timedelta(hours=lon / 15)).hour
        clock_band = local_hour // CLOCK_HOURS
        cell = (math.floor(lat / CELL_DEG), math.floor(lon / CELL_DEG))
        key = (animal, *cell, clock_band)
        counts[key][exposure][local_solar_night(dt, lon)] += 1
        used += 1
    summary = summarize(counts)
    return {"doi": spec["doi"], "title": spec["title"], "height_values_opened": False,
            "source_checksum_md5": spec["checksum"], "classified_bright_or_dark_fixes": used,
            "matching_grid_degrees": CELL_DEG, "clock_band_hours": CLOCK_HOURS,
            "max_gap_days": MAX_DAYS_BETWEEN_EXPOSURES,
            **summary, "status": "matched_support_pass" if summary["matched_support_pass"] else "matched_support_stop"}

def main():
    cfg = json.loads(Path("config/bat_panel_sources_v1.json").read_text(encoding="utf-8"))
    sources = [s for s in cfg["sources"] if s["doi"] in PINNED_DOIS]
    if len(sources) != 6:
        raise SystemExit("Six pinned public GPS sources required")
    results = []
    for spec in sources:
        try:
            results.append(evaluate_source(spec, source_rows(spec)))
        except Exception as exc:
            results.append({"doi": spec["doi"], "status": "source_failure",
                            "error": f"{type(exc).__name__}: {exc}", "height_values_opened": False})
    path = Path("results/lunar_3d_common_support_v2.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"audit": "lunar_3d_common_support_v2", "height_values_opened": False,
                                "results": results}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"results": results, "height_values_opened": False}, indent=2))
    return 0 if all(r["status"] != "source_failure" for r in results) else 2

if __name__ == "__main__":
    raise SystemExit(main())
