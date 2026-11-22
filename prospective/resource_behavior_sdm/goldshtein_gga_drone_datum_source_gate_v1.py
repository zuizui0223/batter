"""Frozen original Goldshtein GPS-GGA vs drone-reference vertical datum QC.

Outputs only anonymous aggregate distributions; NEVER interprets GGA-minus-
drone ground altitude as AGL. User source ZIP SHA locked. No original animal
or flower positions, numeric per-fix heights or dates are emitted.
Predeclared method: GOLDSHTEIN_DRONE_GGA_DATUM_DIAGNOSTIC_FREEZE_20261122.md.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import zipfile

from goldshtein_legacy_biff_source_gate_v1 import (
    XLS_NAME, ZIP_SHA, read_pinned_source_tables
)
from goldshtein_drone_bloom_xy_morning_gate_v1 import (
    GRID_M_PER_DEG, REFERENCE_LAT, nmea_coordinate
)


def _date_from_rmc_fields(fields):
    if len(fields) < 10 or fields[2] != "A" or not re.fullmatch(r"[0-9]{6}", fields[9]):
        return None
    try:
        return datetime.strptime(fields[9] + fields[1][:6], "%d%m%y%H%M%S")
    except ValueError:
        return None


def _nmea_source_pair(gg, rm):
    """GGA and RMC records in same original file, same time, exact lat/lon."""
    if gg is None or rm is None or abs(gg[0] - rm[0]) > 8:
        return False
    return gg[1] == rm[1] and gg[2:6] == rm[2:6]


def _percentiles(data):
    import numpy as np
    if not data:
        return []
    return [round(float(x), 2) for x in np.quantile(
        data, [0.05, 0.25, 0.5, 0.75, 0.95])]


def audit_original_GGA(source_zip):
    import numpy as np
    from scipy.spatial import cKDTree

    path = Path(source_zip)
    digest = sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    if digest.hexdigest() != ZIP_SHA:
        raise ValueError("STOP_UNTRUSTED_SOURCE_ZIP_DIGEST")
    with zipfile.ZipFile(path) as z:
        tables = read_pinned_source_tables(z.read(XLS_NAME))
        flowers, positions = tables["Sheet1"], tables["1-6-2016"]
        factor = (GRID_M_PER_DEG,
                  GRID_M_PER_DEG * math.cos(math.radians(REFERENCE_LAT)))
        xyz = []
        for row in range(1, 333):
            lat, lon, altitude = (positions.get((row, col)) for col in (1, 2, 3))
            if any(type(v) not in (int, float) or not math.isfinite(v)
                   for v in (lat, lon, altitude)):
                raise ValueError("STOP_MISSING_OR_INVALID_DRONE_ALTITUDE_SOURCE")
            xyz.append((lat * factor[0], lon * factor[1], altitude))
        pointcloud = np.asarray(xyz)
        tree = cKDTree(pointcloud[:, :2])
        start = datetime(1899, 12, 30)
        census_dates = set()
        for row in range(1, 415):
            if flowers.get((row, 1)) != "drone 30m":
                continue
            t = flowers.get((row, 2))
            if type(t) not in (float, int):
                raise ValueError("STOP_MISSING_FLOWER_START_DATE")
            for day in range(1, 18):
                if type(flowers.get((row, 9 + day))) in (float, int):
                    census_dates.add((start + timedelta(days=t + day - 1)).date())
        if len(xyz) != 332 or len(census_dates) != 13:
            raise ValueError("STOP_SOURCE_DATE_OR_DRONE_GROUND_DRIFT")
        groups = defaultdict(list)
        for member in z.namelist():
            if member.startswith("GPS data/Bat ") and "/nmea-" in member and member.endswith(".txt"):
                groups[member.rsplit("/", 1)[0]].append(member)
        if len(groups) != 17 or sum(map(len, groups.values())) != 19:
            raise ValueError("STOP_GPS_SOURCE_FILE_ROSTER_CHANGED")
        controls, rows = Counter(), []
        for bat, members in groups.items():
            seen = set()
            for member in members:
                pending_gg = {}
                pending_rm = {}
                with z.open(member) as stream:
                    for line_number, raw in enumerate(stream):
                        if not(raw.startswith(b"$GPGGA,") or raw.startswith(b"$GPRMC,")):
                            continue
                        data = raw.decode("ascii", "replace").split(",")
                        candidate = None
                        if data[0] == "$GPGGA":
                            controls["raw_GGA_sentences"] += 1
                            if (len(data) < 13 or not data[6].isdigit()
                                    or int(data[6]) <= 0 or data[10] != "M"):
                                continue
                            try:
                                altitude = float(data[9])
                            except ValueError:
                                continue
                            geoid = None
                            if data[11]:
                                try:
                                    geoid = float(data[11])
                                except ValueError:
                                    continue
                            gg = (line_number, data[1], data[2], data[3],
                                  data[4], data[5], altitude, geoid)
                            pending_gg[data[1]] = gg
                            rm = pending_rm.get(data[1])
                            if _nmea_source_pair(gg, rm):
                                candidate = (gg, rm)
                        else:
                            if len(data) < 10:
                                continue
                            utc = _date_from_rmc_fields(data)
                            if utc is None:
                                continue
                            rm = (line_number, data[1], data[3], data[4],
                                  data[5], data[6], data[9])
                            pending_rm[data[1]] = rm
                            gg = pending_gg.get(data[1])
                            if _nmea_source_pair(gg, rm):
                                candidate = (gg, rm)
                        if candidate is None:
                            continue
                        gg, rm = candidate
                        utc = _date_from_rmc_fields([
                            "$GPRMC", rm[1], "A", rm[2], rm[3],
                            rm[4], rm[5], "", "", rm[6]])
                        if utc is None:
                            continue
                        localdate = (utc - timedelta(hours=7)).date()
                        if utc.date() not in census_dates and localdate not in census_dates:
                            continue
                        lat = nmea_coordinate(rm[2], rm[3])
                        lon = nmea_coordinate(rm[4], rm[5])
                        if lat is None or lon is None:
                            continue
                        key = (rm[6], rm[1], rm[2], rm[3], rm[4], rm[5])
                        if key in seen:
                            continue
                        seen.add(key)
                        controls["eligible_matched_GGA_RMC_pairs"] += 1
                        controls["geoid_sep_missing"] += gg[7] is None
                        distance, index = tree.query(
                            (lat * factor[0], lon * factor[1]), k=1)
                        if distance > 50:
                            continue
                        rows.append((bat, utc, distance,
                                     gg[6] - pointcloud[index, 2]))
    summary = {}
    for date_match in ("same_UTC_day", "same_local_day"):
        for radius in (15.0, 50.0):
            valid = []
            bats, nights = set(), set()
            for bat, utc, distance, delta in rows:
                if distance > radius:
                    continue
                d = utc.date() if date_match == "same_UTC_day" else (
                    utc - timedelta(hours=7)).date()
                if d not in census_dates:
                    continue
                valid.append(delta)
                bats.add(bat)
                nights.add((bat, d))
            key = date_match + "_" + str(int(radius)) + "m"
            summary[key] = {
                "n_source_GGA_RMC_pairs": len(valid),
                "n_bats": len(bats),
                "n_bat_calendar_dates": len(nights),
                "raw_GGA_alt_minus_drone_alt_m_05_25_50_75_95": _percentiles(valid),
                "not_validated_AGL": True,
            }
    return {
        "schema": "batter.goldshtein_original_GGA_drone_alt_QC.v1",
        "status": "SOURCE_HEIGHT_DATUM_INCOMPATIBLE_UNVERIFIED_AGL_NO_MODEL",
        "source_zip_sha256": ZIP_SHA,
        "n_original_GGA_sentences": controls["raw_GGA_sentences"],
        "n_eligible_matched_GGA_RMC_pairs": controls["eligible_matched_GGA_RMC_pairs"],
        "n_eligible_missing_NMEA_geoid_separation": controls["geoid_sep_missing"],
        "reference_drone_cactus_alt_points": 332,
        "census_candidate_dates": len(census_dates),
        "paired_altitude_differences_not_true_flight_height": True,
        "ground_and_GPS_vertical_reference_compatible_verified": False,
        "source_GPS_ALT_semantics_only_NMEA_metre_not_AGL": True,
        "model_height_response_opened_but_no_ecological_fit": True,
        "source_data_ids_or_coordinates_exported": False,
        "resource_height_model_gain": None,
        "results": summary,
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("source_zip")
    p.add_argument("--out", required=True)
    opts = p.parse_args()
    Path(opts.out).write_text(
        json.dumps(audit_original_GGA(opts.source_zip), indent=2) + "\n",
        encoding="utf-8")
    print("AGL_SOURCE_DATUM_STOP_NEVER_TREAT_GGA_MINUS_DRONE_ALT_AS_AGL")
