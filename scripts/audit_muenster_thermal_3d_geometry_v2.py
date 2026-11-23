#!/usr/bin/env python3
"""Source-authenticated real bat XYZ *geometry QC*, not a source ecology fit.

Only original Zenodo numeric DLTdv5 XYZ rows are read after the V2
pre-outcome coordinate-QC freeze. Coordinate units, camera reference/AGL and
absolute transformation to NRW ALS are NOT assumed; no clutter preference
or bat behaviour effect is inferred.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import md5,sha256
from io import BytesIO,StringIO
from pathlib import Path,PurePosixPath
from urllib.request import urlopen,Request
from zipfile import ZipFile
import csv,json,math,re

RECORD="7797077"
ZIP_URL=f"https://zenodo.org/records/{RECORD}/files/3DTracks.zip?download=1"
README_URL=f"https://zenodo.org/records/{RECORD}/files/README.md?download=1"
ZIP_MD5="648c3effc18d43731f6ac267493046b9"
ZIP_SHA256="1f30d61e66eec1ad078ad114070ae25a543fc7fb86cbae03e52f9a0ee6ff0010"
README_MD5="b91d8cb9113e470af3108c4b6c5eb0b6"
README_SHA256="649314b28364bb99794a49962f33ff9b6e88f9919ebc8d84f62d05e25ef51746"
BASENAME=re.compile(
    r"^DLTdv5_night(?P<night>18|19)_(?P<id>bat[0-9]+|lamp)"
    r"(?P<variant>_uninterrupted)?_xyzpts\.csv$"
)


def verified_get(url,md5_expected,sha_expected):
    with urlopen(Request(url,headers={"User-Agent":"batter-public-track-geometry-v2/1.0"}),
                 timeout=120) as response:
        blob=response.read(150_001)
    if md5(blob).hexdigest()!=md5_expected or sha256(blob).hexdigest()!=sha_expected:
        raise ValueError("Original Zenodo bat source hash disagreement")
    return blob


def read_3d_numeric_rows(source:bytes):
    """Fail closed on unlabeled 4-col tables, nonnumeric text, bad row counts.

    A DLTdv5 xyzpts table is admitted ONLY as 3 columns, all finite.
    Nonfinite values (e.g. MATLAB NaN) represent missing localisation and
    are counted, not interpolated or converted to a bat observation at zero.
    """
    text=source.decode("utf-8-sig",errors="strict").strip()
    if not text:
        raise ValueError("empty source XYZ table")
    first=text.splitlines()[0]
    delim=max((",", "\t", ";"),key=first.count)
    if first.count(delim)<2:
        raise ValueError("original XYZ input has no unambiguous 3-column delimiter")
    reader=csv.reader(StringIO(text,newline=""),delimiter=delim)
    rows=list(reader)
    if not rows:
        raise ValueError("empty 3d file")
    header=rows[0]
    named=False
    if len(header)==3:
        normalized=[v.strip().casefold() for v in header]
        if normalized==["x","y","z"] or normalized==["x [m]","y [m]","z [m]"]:
            named=True
            rows=rows[1:]
    if not rows:
        raise ValueError("no original coordinate rows")
    positions=[]
    missing=0
    for fields in rows:
        if len(fields)!=3:
            raise ValueError("source format STOP: numeric XYZ rows must have exactly 3 columns")
        try:
            nums=tuple(float(field.strip()) for field in fields)
        except ValueError as exc:
            raise ValueError("source format STOP: unexpected nonnumeric XYZ values") from exc
        if not all(math.isfinite(value) for value in nums):
            missing+=1
        else:
            positions.append(nums)
    if not positions:
        raise ValueError("source format STOP: no finite original XYZ")
    mins=[min(row[j] for row in positions) for j in range(3)]
    maxs=[max(row[j] for row in positions) for j in range(3)]
    return {
        "row_count":len(rows),
        "finite_three_coordinate_rows":len(positions),
        "nonfinite_rows_not_interpolated":missing,
        "named_XYZ_header":named,
        "column_count":3,
        "original_local_axes_min_source_units":mins,
        "original_local_axes_max_source_units":maxs,
        "axes_are_Not_yet_verified_AGL_or_world_EPSG":True,
    }


def audit_archive(source:bytes,readme:bytes):
    with ZipFile(BytesIO(source)) as zip_:
        entries=[s for s in zip_.infolist() if not s.is_dir()]
        if len(entries)!=18:
            raise ValueError("18 original source member files expected from frozen v1")
        tracks=[]
        lamps=[]
        names_seen=set()
        for member in entries:
            path=PurePosixPath(member.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in member.filename:
                raise ValueError("source ZIP unsafe member name")
            if path.suffix.lower()!=".csv":
                if path.suffix.lower()!=".png":
                    raise ValueError("unknown published source member extension")
                continue
            if "coordinates_tracks" not in path.parts:
                raise ValueError("original XYZ not in expected source directory")
            match=BASENAME.fullmatch(path.name)
            if not match:
                raise ValueError("unexpected tracking member name")
            name=path.name
            if name in names_seen:
                raise ValueError("duplicate original tracking filename")
            names_seen.add(name)
            descriptor=match.groupdict()
            night=descriptor["night"]
            tag=descriptor["id"]
            variant=bool(descriptor["variant"])
            # Numeric source fields first opened here under the prewritten v2
            # coordinate-QC contract; no modelling with any ecological labels.
            source_geometry=read_3d_numeric_rows(zip_.read(member))
            record={"member_name":member.filename,"night":night,
                    "source_flight_or_lamp_ID":tag,
                    "uninterrupted_duplicate_track_variant":variant,
                    "input_numeric_local_coordinates_units":"original source unspecified",
                    **source_geometry}
            if tag=="lamp":
                lamps.append(record)
            else:
                tracks.append(record)
        distinct_flights={(r["night"],r["source_flight_or_lamp_ID"]) for r in tracks}
        per_night=Counter(n for n,b in distinct_flights)
        duplicate_flights=Counter((r["night"],r["source_flight_or_lamp_ID"])
                                 for r in tracks)
        duplicated=[{"night":k[0],"batID":k[1],"source_variant_file_count":v}
                    for k,v in sorted(duplicate_flights.items()) if v>1]

        text=readme.decode("utf-8-sig",errors="replace")
        # Technical co-registration requires author-provided absolute
        # positioning and >=3 noncollinear control tie points, not one
        # photogrammetric lamp point cloud in an unknown local frame.
        has_georef=bool(re.search(r"\bEPSG[: ]\d{4,6}\b|\bWGS.?84\b|"
                                   r"\bUTM\b|\bGNSS\b|\bRTK\b",text,re.I))
        return {
            "status":"local_real_bat_XYZ_QC_admitted__independent_LiDAR_colocation_NOT_identified",
            "source_original_sha256":ZIP_SHA256,
            "readme_original_sha256":README_SHA256,
            "original_source_member_count":len(entries),
            "original_source_numeric_flight_CSV_files":len(tracks),
            "original_source_lamp_CSV_files":len(lamps),
            "unique_original_night_bat_flight_IDs":len(distinct_flights),
            "unique_flights_by_night":dict(per_night),
            "author_paper_reported_9_3_flight_count":[9,3],
            "published_flight_vs_file_unique_count_discrepancy":(
                per_night.get("18")!=9 or per_night.get("19")!=3),
            "duplicated_uninterrupted_variant_flights":duplicated,
            "bat_tracks_coordinate_structure":tracks,
            "lamp_local_landmark_coordinate_structure":lamps,
            "source_readme_explicit_EPSG_UTM_or_GNSS":has_georef,
            "source_matched_lidar_origin_and_rotation_available":False,
            "known_transform_to_NRW_georeferenced_LAZ":False,
            "source_independent_forest_sites_for_3D_holdout_verified":0,
            "3D_point_process_real_bat_clutter_sdm_admitted":False,
            "3D_flight_values_opened_for_source_QC_only":True,
            "no_bat_clutter_niche_or_ecological_model_fitted":True,
        }


def main():
    output=Path("results/muenster_thermal_3D_tracks_geometry_v2.json")
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        zipdata=verified_get(ZIP_URL,ZIP_MD5,ZIP_SHA256)
        readme=verified_get(README_URL,README_MD5,README_SHA256)
        receipt=audit_archive(zipdata,readme)
    except Exception as exc:
        receipt={"status":"original_3D_source_coordinate_format_or_access_STOP",
                 "source_stop_exception":type(exc).__name__,
                 "source_stop_reason":str(exc)[:400],
                 "no_bat_clutter_niche_or_ecological_model_fitted":True}
    output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    # Output is technical source QC, not biology model, and contains no source
    # individual XYZ sequences or user-identifying GPS.
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
