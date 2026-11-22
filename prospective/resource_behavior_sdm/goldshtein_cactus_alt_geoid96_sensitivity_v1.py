"""Source-only original GPS vs source cactus alt + public EGM96 datum sensitivity.

A source-locked, strictly aggregate-only, NON-BIOLOGICAL diagnostic. It does
not estimate AGL and does not reproduce the author's EGM2008 + Google Maps
Elevation pipeline. Original heights are accessed only to compare vertical
reference systems, not to score resource-conditioned bat distributions.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from math import cos, isfinite, radians
from pathlib import Path
from tempfile import NamedTemporaryFile
import json
import re
import zipfile

ORIGINAL_SHA = "069b12e6383fa7d84a1f7164fcfe16b0ce693469a7661262ce1a0ed73e423ebb"
EGM96_GRID_SHA = "c02a6eb70a7a78efebe5adf3ade626eb75390e170bb8b3f36136a2c28f5326a0"
LOCAL_REFERENCE_LATITUDE = 31.97
RADIUS_M = (15., 50.)
RMC_RE = re.compile(r"GPS data/Bat [0-9]+/nmea-GeoTag[12]?\.txt$")
CACTUS_RE = re.compile(r"GPS data/Bat [0-9]+/cacti\.xlsx$")


def _digest(path):
    h = sha256()
    with Path(path).open("rb") as stream:
        while True:
            part = stream.read(1 << 20)
            if not part:
                return h.hexdigest()
            h.update(part)


def _nmea_coordinate(value, hemisphere):
    if not value or hemisphere not in ("N", "S", "E", "W"):
        return None
    try:
        raw = float(value)
        deg = int(raw // 100)
        minute = raw - 100 * deg
        if not 0 <= minute < 60:
            return None
        signed = deg + minute / 60
        if hemisphere in ("S", "W"):
            signed = -signed
        if hemisphere in ("N", "S") and abs(signed) > 90:
            return None
        if hemisphere in ("E", "W") and abs(signed) > 180:
            return None
        return signed
    except (ValueError, TypeError):
        return None


def _original_map(z, member):
    from artifact_tool import Blob, SpreadsheetFile
    import numpy as np
    with NamedTemporaryFile(suffix=".xlsx") as tmp:
        with z.open(member) as source:
            while True:
                chunk = source.read(1 << 16)
                if not chunk:
                    break
                tmp.write(chunk)
        tmp.flush()
        wb = SpreadsheetFile.import_xlsx(Blob.load(tmp.name))
        values = wb.worksheets.get_item_at(0).get_range("A1:M1500").values
    header = [str(v).strip().lower() if v is not None else "" for v in values[0]]
    if "lat" not in header or "lon" not in header:
        raise ValueError("STOP_SOURCE_CACTUS_XY_HEADER_CHANGED")
    i, j = header.index("lat"), header.index("lon")
    k = header.index("alt") if "alt" in header else None
    rows = []
    for row in values[1:]:
        lat, lon = row[i], row[j]
        if type(lat) not in (int, float) or type(lon) not in (int, float):
            continue
        alt = row[k] if k is not None else None
        alt = float(alt) if type(alt) in (int, float) and isfinite(alt) else float("nan")
        rows.append((float(lat), float(lon), alt))
    if len(rows) < 3:
        raise ValueError("STOP_EMPTY_CACTUS_XY")
    return np.asarray(rows, dtype=float)


def _quantiles(xs):
    """NumPy-compatible linear quantiles, with NO optional dependencies."""
    if not xs:
        raise ValueError("STOP_EMPTY_ALTITUDE_DISTRIBUTION")
    values = sorted(float(v) for v in xs)
    n = len(values)
    def one(q):
        pos = (n - 1) * q
        lo = int(pos)
        hi = min(n - 1, lo + 1)
        return round(values[lo] + (values[hi] - values[lo]) * (pos - lo), 2)
    return [one(q) for q in (0.05, 0.25, 0.5, 0.75, 0.95)]


def _source_GGA_near_cactus_alt(z, maps):
    """Original RMC XY and quality-positive same-time GGA; no response-based cut."""
    import numpy as np
    from scipy.spatial import cKDTree
    factor = np.array([111195., 111195. * cos(radians(LOCAL_REFERENCE_LATITUDE))])
    kd = {key: cKDTree(matrix[:, :2] * factor) for key, matrix in maps.items()
          if np.isfinite(matrix[:, 2]).any()}
    gathered = defaultdict(list)
    n_files = defaultdict(int)
    for member in z.namelist():
        if not RMC_RE.fullmatch(member):
            continue
        animal = member.rsplit("/", 1)[0]
        if animal not in kd:
            continue
        n_files[animal] += 1
        seen = set()
        pending = {}
        with z.open(member) as f:
            for ix, raw in enumerate(f):
                if not (raw.startswith(b"$GPRMC,") or raw.startswith(b"$GPGGA,")):
                    continue
                fields = raw.decode("ascii", "replace").split(",")
                if fields[0] == "$GPGGA":
                    if (len(fields) < 13 or not fields[6].isdigit() or
                            int(fields[6]) <= 0 or fields[10] != "M"):
                        continue
                    try:
                        alt = float(fields[9])
                    except ValueError:
                        continue
                    record = pending.setdefault(fields[1], {})
                    record["gga"] = (ix, tuple(fields[2:6]), alt)
                else:
                    if len(fields) < 10 or fields[2] != "A":
                        continue
                    lat = _nmea_coordinate(fields[3], fields[4])
                    lon = _nmea_coordinate(fields[5], fields[6])
                    if lat is None or lon is None:
                        continue
                    record = pending.setdefault(fields[1], {})
                    record["rmc"] = (ix, tuple(fields[3:7]), lat, lon, fields[9])
                gga, rmc = record.get("gga"), record.get("rmc")
                if not gga or not rmc:
                    continue
                if abs(gga[0] - rmc[0]) > 8 or gga[1] != rmc[1]:
                    continue
                fix_key = (fields[1], rmc[1], rmc[4])
                if fix_key in seen:
                    continue
                seen.add(fix_key)
                xy = (rmc[2] * factor[0], rmc[3] * factor[1])
                distance, rowidx = kd[animal].query(xy, k=1)
                if distance > 50:
                    continue
                ref = maps[animal][rowidx, 2]
                if not isfinite(ref):
                    continue
                difference = gga[2] - ref
                gathered["50m"].append(difference)
                if distance <= 15:
                    gathered["15m"].append(difference)
                    gathered[animal].append(difference)
    if len(kd) != 4 or len(gathered["15m"]) != 36082:
        raise ValueError("STOP_SOURCE_ALTITUDE_REFERENCE_COUNTS_CHANGED")
    animal_medians = [float(np.median(gathered[animal]))
                      for animal in kd if gathered[animal]]
    return gathered, sorted(animal_medians)


def audit_original(source_zip, egm96_grid, source_drone_points=None):
    """Aggregate-only. source_drone_points: list of (lat,lon) from pinned XLS source."""
    # Reject untrusted bytes BEFORE importing optional geospatial libraries.
    # The pure-stdlib CI intentionally has no numpy/scipy/pyproj/artifact_tool.
    if _digest(source_zip) != ORIGINAL_SHA or _digest(egm96_grid) != EGM96_GRID_SHA:
        raise ValueError("STOP_SOURCE_OR_REFERENCE_GRID_SHA256_MISMATCH")
    from pyproj import Transformer
    import numpy as np
    grid_transform = Transformer.from_pipeline(
        "+proj=vgridshift +grids=" + str(Path(egm96_grid).resolve()) + " +multiplier=1")
    with zipfile.ZipFile(source_zip) as source:
        entries = source.namelist()
        if len(entries) != 55:
            raise ValueError("STOP_ORIGINAL_SOURCE_MANIFEST_DRIFT")
        cactus_members = sorted(f for f in entries if CACTUS_RE.fullmatch(f))
        if len(cactus_members) != 8:
            raise ValueError("STOP_8_SOURCE_CACTUS_TABLES_CHANGED")
        maps = {m.rsplit("/", 1)[0]: _original_map(source, m) for m in cactus_members}
        source_alt = [r for mat in maps.values() for r in mat if isfinite(r[2])]
        if len(source_alt) != 1951:
            raise ValueError("STOP_SOURCE_CACTUS_ALT_ROWS_CHANGED")
        gga, animal_medians = _source_GGA_near_cactus_alt(source, maps)
        source_grid_shift = [
            grid_transform.transform(lon, lat, 0)[2] for lat, lon, alt in source_alt]
        if source_drone_points is None:
            from goldshtein_legacy_biff_source_gate_v1 import (
                XLS_NAME, read_pinned_source_tables)
            second = read_pinned_source_tables(source.read(XLS_NAME))["1-6-2016"]
            source_drone_points = [(second[i, 1], second[i, 2])
                                   for i in range(1, 333)]
        if len(source_drone_points) != 332:
            raise ValueError("STOP_ORIGINAL_DRONE_REFERENCE_POINT_COUNT_CHANGED")
        drone_grid_shift = [
            grid_transform.transform(lon, lat, 0)[2]
            for lat, lon in source_drone_points]
    return {
        "schema":"batter.original_GGA_cactus_reference_altitude_and_EGM96_QC.v1",
        "status":"SOURCE_LOCAL_ALTITUDE_REFERENCE_SENSITIVITY_NOT_VALIDATED_AGL",
        "source_upload_sha256":ORIGINAL_SHA,
        "PROJ_EGM96_grid_sha256":EGM96_GRID_SHA,
        "grid_is_EGM96_not_original_published_EGM2008":True,
        "n_source_animal_cactus_maps":8,
        "n_cactus_maps_with_altitude":4,
        "n_cactus_map_altitude_rows":len(source_alt),
        "n_matched_altitude_references_within_15m":len(gga["15m"]),
        "n_matched_altitude_references_within_50m":len(gga["50m"]),
        "raw_GGA_minus_source_cactus_alt_quantiles_15m":_quantiles(gga["15m"]),
        "raw_GGA_minus_source_cactus_alt_quantiles_50m":_quantiles(gga["50m"]),
        "min_max_anonymous_bat_median_raw_offset_m":[
            round(animal_medians[0],2),round(animal_medians[-1],2)],
        "anonymous_bat_median_spread_m":round(
            animal_medians[-1]-animal_medians[0],2),
        "source_cactus_map_EGM96_grid_shift_quantiles_m":_quantiles(source_grid_shift),
        "source_drone_332_EGM96_grid_shift_quantiles_m":_quantiles(drone_grid_shift),
        "source_GGA_raw_orthometric_ellipsoidal_reference_confirmed":False,
        "source_cactus_alt_reference_confirmed":False,
        "source_drone_alt_reference_confirmed":False,
        "single_constant_offset_validated":False,
        "source_author_original_AGL_reconstructed":False,
        "source_GGA_height_values_are_not_observed_resource_height_gain":True,
        "observed_food_conditional_altitude_gain":None,
        "no_animal_ids_source_XY_or_perfix_altitude_emitted":True,
    }


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("source_zip")
    p.add_argument("--egm96-grid",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    receipt=audit_original(args.source_zip,args.egm96_grid)
    Path(args.out).write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print("SOURCE_ALT_DATUM_SENSITIVITY_NO_CALIBRATED_AGL")
