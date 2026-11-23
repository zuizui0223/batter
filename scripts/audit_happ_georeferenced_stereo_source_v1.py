#!/usr/bin/env python3
"""Happ 2024 publicly georeferenced thermal source V1 metadata only.

No original drone GPS or stereo image point values opened here. No original
bat video data or 3D flight outcome is reconstructed. This pre-score gate
checks published source file identities, headers, and source row structure.
"""
from __future__ import annotations
from collections import Counter
import csv,hashlib,json,subprocess
from pathlib import Path

AUTHOR="christofhapp/batflight3D_publication"
TAG="v1.0.1"
COMMIT="34d2f56bcee1eab9207890938aedd90a079bfcde"
STUDIES={
    "trainA":"data/Turbine2_Setup4_2022-06-23_21-29/DRONE_SIM_PTS.csv",
    "trainB":"data/Turbine2_Setup4_2022-06-23_21-41/DRONE_SIM_PTS.csv",
    "camera":"data/parameters_Turbine2.json"
}
EXPECTED_BLOBS={
    "trainA":"9114254bde93b1ecae3d2a4df45b9219216fac0c",
    "trainB":"ec6435a2cc8370696a68892e839a5b387d9d64e1",
    "camera":"60315eacc821d266ebebe373b348bcb125cb3ad3",
}
EXPECTED_FIELDS=("nr","datetime","x1","y1","x2","y2","lat","lon","height")


def git_blob(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()


def flight_header_structure(raw:bytes)->dict:
    reader=csv.reader(raw.decode("utf-8-sig").splitlines())
    head=next(reader)
    if len(head)<len(EXPECTED_FIELDS):
        raise ValueError("source header missing original stereo/GPS fields")
    normalized=[x.strip() for x in head]
    if len(set(normalized))!=len(normalized):
        raise ValueError("original header fields duplicated")
    if any(field not in normalized for field in EXPECTED_FIELDS):
        raise ValueError("original flight does not contain the exact published position and image labels")
    widths=Counter()
    for row in reader:
        if row:widths[len(row)]+=1
    if not widths or set(widths)!={len(head)}:
        raise ValueError("source CSV data row grammar inconsistent")
    if sum(widths.values())<20:
        raise ValueError("independent calibration flight has insufficient source rows")
    return {
        "column_headers":normalized,
        "source_data_rows":sum(widths.values()),
        "columns_per_row":len(head),
        "raw_numeric_drone_GPS_or_pixels_inspected":False,
    }


def camera_source_structure(raw:bytes)->dict:
    x=json.loads(raw)
    if not isinstance(x,dict) or "ref" not in x or len(x["ref"])!=2:
        raise ValueError("original reference GPS metadata not present")
    for name in ("camintrinsicMatrix1","camintrinsicMatrix2"):
        mat=x.get(name)
        if len(mat)!=3 or any(len(row)!=3 for row in mat):
            raise ValueError("source camera intrinsic matrix shape")
    return {
        "source_intrinsic_array_shapes":{"cam1":[3,3],"cam2":[3,3]},
        "source_ref_coordinate_present":True,
        "source_reference_EPSG_or_vertical_datum_stated_by_json":False,
        "source_intrinsic_numeric_parameters_used":False,
    }


def audit(root:Path)->dict:
    head=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if head!=COMMIT:raise ValueError("source Git commit differs from published v1.0.1")
    checked={}
    for role,path in STUDIES.items():
        raw=(root/path).read_bytes()
        sha=git_blob(raw)
        if sha!=EXPECTED_BLOBS[role]:
            raise ValueError("original Git blob mismatch: "+role)
        info={"path":path,"original_git_blob_sha1":sha,
              "original_file_sha256":hashlib.sha256(raw).hexdigest(),
              "bytes":len(raw)}
        if role!="camera":
            info.update(flight_header_structure(raw))
        else:
            info.update(camera_source_structure(raw))
        checked[role]=info
    bat_source=root/"data/Turbine2_Setup4_2022-06-23_21-41/images/bat_recording"
    if not bat_source.is_dir():
        raise ValueError("author real bat stereo recording example missing")
    key_files=("imagelist.csv","IM_PTS_cam1.csv","IM_PTS_cam2.csv")
    if not all((bat_source/name).is_file() for name in key_files):
        raise ValueError("original bat stereo image source schematic files missing")
    return {
        "status":"original_geodetic_drone_stereo_source_structure_admitted",
        "author":AUTHOR,"original_git_tag":TAG,"original_commit":COMMIT,
        "calibration_flight_files":checked,
        "original_camera_example_precomputed_image_point_file_names":list(key_files),
        "original_bat_xyz_coordinates_computed":False,
        "source_camera_calibration_outcomes_opened":False,
        "independent_forest_or_LiDAR_scanned_sites_admitted":False,
        "source_survey_method":"independent GNSS drone calibration + synchronized stereo thermal pixel locations",
        "location_source": "wind-farm camera deployment, NOT forest"
    }


def main():
    out=Path("results/happ_georeferenced_thermal_source_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    try:
        r=audit(Path("external/happ"))
    except Exception as e:
        r={"status":"original_public_georeferenced_stereo_source_STOP",
           "error":str(e)[:350],"exception":type(e).__name__,
           "source_camera_calibration_outcomes_opened":False}
    out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
