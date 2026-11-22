"""Goldshtein source-only RMC XY × drone morning flower census eligibility.

Original user ZIP SHA pinned. Never reads GPS GGA altitude, modifies source,
creates model scores, executes author code or exports bat/cactus locations.
Requires numpy/scipy for the *source-only* KD-tree; pure-stdlib CI tests only
the source-free date/time/coordinate contracts.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timedelta
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import zipfile

from goldshtein_legacy_biff_source_gate_v1 import (
    ZIP_SHA, XLS_NAME, read_pinned_source_tables
)

LOCAL_UTC_OFFSET_HOURS = -7
GRID_M_PER_DEG = 111195.0
REFERENCE_LAT = 31.97
NEAR_M = 15.0


def nmea_coordinate(source, hemisphere):
    if hemisphere not in ("N", "S", "E", "W") or not source:
        return None
    try:
        value = float(source)
        degrees = int(value // 100)
        minutes = value - 100 * degrees
        if not 0 <= minutes < 60:
            return None
        out = degrees + minutes / 60
        if hemisphere in ("S", "W"):
            out = -out
        if not (-90 <= out <= 90 if hemisphere in ("N", "S")
                else -180 <= out <= 180):
            return None
        return out
    except (TypeError, ValueError):
        return None


def source_following_morning(utc):
    local = utc + timedelta(hours=LOCAL_UTC_OFFSET_HOURS)
    if 6 <= local.hour < 18:
        return None
    return (local.date() + timedelta(days=1)) if local.hour >= 18 else local.date()


def count_gap60_episodes(events):
    """Event: private tuple (bat, morning_date, UTC_datetime, source_row, count)."""
    ordered = sorted(events, key=lambda x: (x[0], x[1], x[2]))
    recent = {}
    count = total_positive = 0
    for bat, morning, utc, cactus_row, flowering in ordered:
        key = (bat, morning, cactus_row)
        if key not in recent or (utc - recent[key]).total_seconds() > 60:
            count += 1
            total_positive += bool(flowering > 0)
        recent[key] = utc
    return count, total_positive


def source_spatiotemporal_qc(source_zip):
    import numpy as np
    from scipy.spatial import cKDTree

    path = Path(source_zip)
    h = sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    if h.hexdigest() != ZIP_SHA:
        raise ValueError("STOP_ORIGINAL_SOURCE_ZIP_HASH_CHANGED")
    factor = (
        GRID_M_PER_DEG,
        GRID_M_PER_DEG * math.cos(math.radians(REFERENCE_LAT))
    )
    with zipfile.ZipFile(path) as archive:
        t = read_pinned_source_tables(archive.read(XLS_NAME))["Sheet1"]
        byday = defaultdict(lambda: ([], [], []))
        origin = datetime(1899, 12, 30)
        for row in range(1, 415):
            if t.get((row, 1)) != "drone 30m":
                continue
            lat, lon, start = (t.get((row, j)) for j in (8, 9, 2))
            if any(type(v) not in (float, int) for v in (lat, lon, start)):
                raise ValueError("STOP_MISSING_ORIGINAL_DRONE_FIELD_GEOMETRY")
            for day in range(1, 18):
                flowering = t.get((row, day + 9))
                if type(flowering) not in (int, float):
                    continue
                census = (origin + timedelta(days=start + day - 1)).date()
                xy, flowers, original_rows = byday[census]
                xy.append((lat * factor[0], lon * factor[1]))
                flowers.append(float(flowering))
                original_rows.append(row)
        if len(byday) != 13 or sum(len(v[0]) for v in byday.values()) != 1016:
            raise ValueError("STOP_ORIGINAL_DRONE_CENSUS_SCHEMA_DRIFT")
        tree = {day: cKDTree(np.asarray(vals[0])) for day, vals in byday.items()}
        grouped = defaultdict(list)
        for name in archive.namelist():
            if "/nmea-" in name and name.endswith(".txt") and name.startswith("GPS data/Bat "):
                grouped[name.rsplit("/", 1)[0]].append(name)
        if len(grouped) != 17 or sum(map(len, grouped.values())) != 19:
            raise ValueError("STOP_ORIGINAL_GPS_FILES_CHANGED")
        qualifying_positions, matched = 0, []
        for bat, files in grouped.items():
            seen = set()
            for filename in files:
                with archive.open(filename) as stream:
                    for raw in stream:
                        if not raw.startswith(b"$GPRMC,"):
                            continue
                        fields = raw.decode("ascii", "replace").split(",")
                        if (len(fields) < 10 or fields[2] != "A" or
                                re.fullmatch(r"[0-9]{6}", fields[9]) is None):
                            continue
                        lat = nmea_coordinate(fields[3], fields[4])
                        lon = nmea_coordinate(fields[5], fields[6])
                        if lat is None or lon is None:
                            continue
                        key = (fields[9], fields[1],
                               fields[3], fields[4], fields[5], fields[6])
                        if key in seen:
                            continue
                        seen.add(key)
                        try:
                            utc = datetime.strptime(fields[9] + fields[1][:6],
                                                    "%d%m%y%H%M%S")
                        except ValueError:
                            continue
                        morning = source_following_morning(utc)
                        if morning not in tree:
                            continue
                        qualifying_positions += 1
                        dist, closest = tree[morning].query(
                            (lat * factor[0], lon * factor[1]), k=1)
                        if dist <= NEAR_M:
                            xy, flower, original_rows = byday[morning]
                            matched.append((bat, morning, utc, original_rows[closest],
                                            flower[closest]))
    episodes, positive_episodes = count_gap60_episodes(matched)
    return {
        "schema": "batter.goldshtein_original_drone_cactus_morning_GPS_XY.v1",
        "status": "PRELIMINARY_SAME_PROGRAMME_SPATIOTEMPORAL_SUPPORT_NOT_FEEDING",
        "source_zip_sha256": ZIP_SHA,
        "local_UTC_offset_hours": LOCAL_UTC_OFFSET_HOURS,
        "source_assumed_night": "18:00-05:59 local, next morning census",
        "source_calendar_day_offset_author_verified": False,
        "n_source_drone_daily_numeric_cactus_counts": 1016,
        "n_candidate_drone_census_dates": len(tree),
        "n_valid_GPS_RMC_on_candidate_census_nights": qualifying_positions,
        "n_GPS_XY_fixes_within_15m_of_a_directly_counted_cactus": len(matched),
        "n_matched_GPS_fixes_nearest_cactus_positive_count":
            sum(v[4] > 0 for v in matched),
        "n_distinct_bats": len({m[0] for m in matched}),
        "n_bat_night_mornings": len({(m[0], m[1]) for m in matched}),
        "n_distinct_source_cacti": len({m[3] for m in matched}),
        "n_cactus_morning_pairs": len({(m[1], m[3]) for m in matched}),
        "n_15m_GPS_proximity_episodes_gap60s": episodes,
        "n_15m_positive_flower_proximity_episodes_gap60s": positive_episodes,
        "original_GGA_altitude_values_read": False,
        "source_survey_selection_and_detection_calibrated": False,
        "actual_nectar_consumption_observed_at_GPS": False,
        "resource_conditional_height_effect": None,
        "raw_animal_plant_XY_dates_not_exported": True
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("source_zip")
    p.add_argument("--out", required=True)
    args = p.parse_args()
    Path(args.out).write_text(
        json.dumps(source_spatiotemporal_qc(args.source_zip), indent=2) + "\n",
        encoding="utf-8")
    print("ORIGINAL_DRONE_GPS_XY_DATE_SOURCE_QC_ONLY_NO_GPS_HEIGHT")
