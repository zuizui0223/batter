#!/usr/bin/env python3
"""Real original Münster DLTdv5 local XYZ technical QC, not bat niche effects.

Frozen after SOURCE-ONLY discovery of pt1_X/Y/Z and bat8 pt2_X/Y/Z
headers; see docs/MUENSTER_THERMAL_3D_TRACKS_V2_3_SCHEMA_CORRECTED_PREOUTCOME_20261124.md

The source contains no verified local→NRW ALS world transform, local height
datum, detector q or certified forest air. No clutter selection is inferred.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from io import BytesIO,StringIO
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
import csv,json,math

from scripts.audit_muenster_thermal_3d_geometry_v2 import (
    ZIP_URL,ZIP_MD5,ZIP_SHA256,
    README_URL,README_MD5,README_SHA256,
    BASENAME,verified_get
)

EXPECTED3=("pt1_X","pt1_Y","pt1_Z")
EXPECTED6=EXPECTED3+("pt2_X","pt2_Y","pt2_Z")


def parse_real_source_point_streams(raw:bytes):
    """Read a single authored DLTdv5 CSV. No timestamps, no world CRS inferred.

    3- and 6-column headers must match the actual original source field names.
    NaN/blank is missing, a partially observed XYZ is NOT an event.
    """
    source=raw.decode("utf-8-sig",errors="strict")
    rows=source.splitlines()
    if len(rows)<2:
        raise ValueError("original tracking file missing source position rows")
    delimiter=max((",", "\t", ";"),key=rows[0].count)
    if rows[0].count(delimiter)<2:
        raise ValueError("3D tracking header has no recognized delimiter")
    reader=csv.reader(StringIO(source,newline=""),delimiter=delimiter)
    header=tuple(s.strip() for s in next(reader))
    if header not in (EXPECTED3,EXPECTED6):
        raise ValueError("original data header not exactly approved pt1 or pt1+pt2 XYZ")
    stream_names=("pt1",) if header==EXPECTED3 else ("pt1","pt2")
    data=list(reader)
    if not data:
        raise ValueError("source data rows absent")
    records={name:{"all_source_rows":len(data),"full_valid_xyz":0,
                   "all_missing_xyz":0,"partially_missing_xyz":0,
                   "bounds_min":[float("inf")]*3,
                   "bounds_max":[float("-inf")]*3}
             for name in stream_names}
    for row in data:
        if not row or (len(row)==1 and not row[0].strip()):
            continue  # explicit empty physical trailing row, not a zero event
        if len(row)!=len(header):
            raise ValueError("original XYZ data row width mismatch")
        for j,name in enumerate(stream_names):
            vals=[]
            for rawval in row[j*3:(j+1)*3]:
                s=rawval.strip()
                if not s:
                    vals.append(float("nan"))
                else:
                    try:
                        vals.append(float(s))
                    except ValueError as exc:
                        raise ValueError("unexpected nonnumeric original source XYZ token") from exc
            finite=[math.isfinite(v) for v in vals]
            rec=records[name]
            if all(finite):
                rec["full_valid_xyz"]+=1
                for axis,val in enumerate(vals):
                    rec["bounds_min"][axis]=min(rec["bounds_min"][axis],val)
                    rec["bounds_max"][axis]=max(rec["bounds_max"][axis],val)
            elif not any(finite):
                rec["all_missing_xyz"]+=1
            else:
                rec["partially_missing_xyz"]+=1
    for rec in records.values():
        if rec["full_valid_xyz"]==0:
            rec["bounds_min"]=None
            rec["bounds_max"]=None
        if rec["full_valid_xyz"]+rec["all_missing_xyz"]+rec["partially_missing_xyz"]>rec["all_source_rows"]:
            raise ValueError("invalid source coordinate count")
        rec["physical_axis_units"]="source coordinate units, not yet documented metre AGL"
        rec["zero_substitution_or_missing_track_interpolation_used"]=False
    return {"source_original_column_headers":list(header),
            "source_numeric_point_streams":records,
            "source_has_second_pt2_stream":header==EXPECTED6}


def run_real_source_QC(raw:bytes,readme_raw:bytes):
    with ZipFile(BytesIO(raw)) as archive:
        members=[p for p in archive.namelist() if not p.endswith("/")]
        if len(members)!=18:
            raise ValueError("original ZIP source member count differs from V1")
        files=[]
        stream_counts=Counter()
        variant_pairs=defaultdict(list)
        lamp_by_night=Counter()
        for name in members:
            p=PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts or "\\" in name:
                raise ValueError("unsafe original ZIP member path")
            if p.suffix==".png":
                continue
            if p.suffix!=".csv" or "coordinates_tracks" not in p.parts:
                raise ValueError("original ZIP new/unexpected coordinate file")
            m=BASENAME.fullmatch(p.name)
            if m is None:
                raise ValueError("original source track member filename unexpected")
            meta=m.groupdict()
            numeric=parse_real_source_point_streams(archive.read(name))
            night=meta["night"]; marker=meta["id"]
            is_variant=bool(meta["variant"])
            row={
                "source_member":name,
                "original_night":night,
                "published_source_batID_or_lamp":marker,
                "is_duplicate_uninterrupted_source_variant":is_variant,
                **numeric,
            }
            files.append(row)
            if marker=="lamp":
                lamp_by_night[night]+=1
                continue
            # Only the NORMAL original source file is the canonical source.
            # "_uninterrupted" files are technical variants, not new bat IDs.
            variant_pairs[(night,marker)].append(is_variant)
            if not is_variant:
                for target,info in numeric["source_numeric_point_streams"].items():
                    stream_counts[(night,marker,target)]=info["full_valid_xyz"]

        if set(lamp_by_night)!={"18","19"} or set(lamp_by_night.values())!={1}:
            raise ValueError("both original lamp local source records expected")
        for key,variants in variant_pairs.items():
            if variants.count(False)!=1:
                raise ValueError("one canonical non-uninterrupted file per original bat ID required")
        positive_streams={k:v for k,v in stream_counts.items() if v>0}
        by_night=Counter(n for n,b,t in positive_streams)
        source_filenames=Counter(n for (n,b) in variant_pairs)
        source_dual=[x for x in files if (
            x["source_has_second_pt2_stream"] and
            x["published_source_batID_or_lamp"]!="lamp"
        )]
        return {
            "status":"NUMERIC_LOCAL_XYZ_SOURCE_VALIDATED__COLLOCATION_STOP_NO_ABSOLUTE_CONTROL",
            "original_public_source":"https://zenodo.org/records/7797077",
            "original_3dtracks_sha256":ZIP_SHA256,
            "original_README_sha256":README_SHA256,
            "source_geometry_csv_files":len(files),
            "source_duplicated_flight_variants":sum(
                1 for x in files if x["is_duplicate_uninterrupted_source_variant"]),
            "canonical_source_bat_filename_IDs_by_night":dict(source_filenames),
            "observed_numerically_valid_target_streams_by_night":dict(by_night),
            "canonical_source_target_streams_present":len(stream_counts),
            "canonical_source_target_streams_with_ge1_valid_xyz":len(positive_streams),
            "source_pt2_additional_streams_nonzero":len([
                value for (night,bat,pt),value in positive_streams.items() if pt=="pt2"]),
            "author_abstract_9_and_3_flights":"potentially consistent only if pt2 denotes a distinct animal; requires original author confirmation",
            "canonical_observed_valid_xyz_local_points_total":sum(positive_streams.values()),
            "individual_original_source_geometry_QC":files,
            "original_geographic_XYZ_or_EPSG_control_ties_verified":False,
            "single_local_lamp_landmark_not_enough_to_solve_world_rigid_transform":True,
            "NRW_LiDAR_same_site_point_cloud_downloaded_or_registered":False,
            "field_bat_flight_xyz_source_admitted_for_local_geometry_QC":True,
            "field_bat_height_AGL_derived":False,
            "original_species_labels_in_thermal_tracks_verified":False,
            "field_clutter_niche_or_3D_SDM_fitted":False,
        }


def main():
    output=Path("results/muenster_real_3d_local_geometry_v2_3.json")
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        source=verified_get(ZIP_URL,ZIP_MD5,ZIP_SHA256)
        readme=verified_get(README_URL,README_MD5,README_SHA256)
        receipt=run_real_source_QC(source,readme)
    except Exception as exc:
        receipt={
            "status":"ORIGINAL_LOCAL_SOURCE_FORMAT_OR_CONTENT_STOP",
            "source_error_type":type(exc).__name__,
            "source_error":str(exc)[:350],
            "field_clutter_niche_or_3D_SDM_fitted":False,
        }
    output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if receipt.get("status","").startswith("NUMERIC"):
        print(json.dumps({
            "status":receipt["status"],
            "original_3dtracks_sha256":receipt["original_3dtracks_sha256"],
            "canonical_source_bat_filename_IDs_by_night":receipt["canonical_source_bat_filename_IDs_by_night"],
            "observed_numerically_valid_target_streams_by_night":receipt["observed_numerically_valid_target_streams_by_night"],
            "canonical_source_target_streams_present":receipt["canonical_source_target_streams_present"],
            "canonical_source_target_streams_with_ge1_valid_xyz":receipt["canonical_source_target_streams_with_ge1_valid_xyz"],
            "source_pt2_additional_streams_nonzero":receipt["source_pt2_additional_streams_nonzero"],
            "canonical_observed_valid_xyz_local_points_total":receipt["canonical_observed_valid_xyz_local_points_total"],
            "original_geographic_XYZ_or_EPSG_control_ties_verified":False,
            "NRW_LiDAR_same_site_point_cloud_downloaded_or_registered":False,
            "field_clutter_niche_or_3D_SDM_fitted":False,
        },indent=2))
    else:
        print(json.dumps(receipt,indent=2))
    return 0


if __name__=="__main__":
    main()
