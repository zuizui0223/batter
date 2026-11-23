#!/usr/bin/env python3
"""Heldout *drone GPS* geographic stereo camera reproduction from public field data.

Source-open engineering verification, not a bat ecological endpoint.
Happ et al. 2024 authors already developed the underlying 3D georeferenced
thermal bat workflow. No LiDAR, source Bat XYZ, wildlife event intensity,
bat detection probability or forest clutter parameter is fitted here.

Frozen: docs/HAPP_GPS_STEREO_V2_WHOLE_FLIGHT_HOLDOUT_PREOUTCOME_20261124.md
"""
from __future__ import annotations

from collections import Counter
import csv,hashlib,json,math,subprocess
from pathlib import Path
import numpy as np
import cv2
from pyproj import Transformer

AUTHOR_COMMIT="34d2f56bcee1eab9207890938aedd90a079bfcde"
SOURCE_FILES={
    "A":("data/Turbine2_Setup4_2022-06-23_21-29/DRONE_SIM_PTS.csv",
          "09193748e2dc21fedffb6f2749cdc251d94f0bd615336cdf52e20f6ee5e87802"),
    "B":("data/Turbine2_Setup4_2022-06-23_21-41/DRONE_SIM_PTS.csv",
          "1d35a3c167012e779f8ae3a95c5dcb4fbf4c5652ba7c9988bd12782172b1a5b0"),
    "camera":("data/parameters_Turbine2.json",
          "74a65726d47b677009168e1c8252e6e4e6e19028c46d9bd5792337bc6c572ec5")
}
EXPECTED_ROWS={"A":4987,"B":6018}
ORIGINAL_FIELDS=("nr","x1","y1","x2","y2","lat","lon","height")
PROJECTION_CRS="EPSG:32632"


def verify_files(root:Path):
    commit=subprocess.check_output(
        ["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if commit!=AUTHOR_COMMIT:
        raise ValueError("original public author tag changed")
    raw={}
    for role,(name,hash_) in SOURCE_FILES.items():
        data=(root/name).read_bytes()
        if hashlib.sha256(data).hexdigest()!=hash_:
            raise ValueError("source original SHA256 mismatch: "+role)
        raw[role]=data
    return raw


def source_camera(data:bytes):
    doc=json.loads(data)
    K=[]
    D=[]
    for i in (1,2):
        k=np.asarray(doc[f"camintrinsicMatrix{i}"],dtype=np.float64)
        d=np.asarray(doc[f"distortion{i}"],dtype=np.float64)
        if k.shape!=(3,3) or d.ndim!=1 or len(d) not in (4,5,8):
            raise ValueError("original source intrinsics/distortion unsupported")
        if not np.isfinite(k).all() or not np.isfinite(d).all():
            raise ValueError("invalid original intrinsic values")
        K.append(k)
        D.append(d)
    ref=np.asarray(doc["ref"],dtype=np.float64)
    if ref.shape!=(2,) or not np.isfinite(ref).all():
        raise ValueError("source reference latitude longitude invalid")
    return (K[0],K[1]),(D[0],D[1]),ref


def original_drone_stereo(data:bytes,ref:np.ndarray, *, role:str):
    text=data.decode("utf-8-sig")
    reader=csv.DictReader(text.splitlines())
    if not set(ORIGINAL_FIELDS).issubset(reader.fieldnames or []):
        raise ValueError("source original calibration header differs")
    rows=list(reader)
    if len(rows)!=EXPECTED_ROWS.get(role,len(rows)):
        raise ValueError("source original flight row count changed")
    xys1=[];xys2=[];ll=[];z=[]
    excluded=Counter()
    seen=set()
    for row in rows:
        nr=row["nr"].strip()
        if nr in seen:
            raise ValueError("source duplicate synchronized camera frame nr")
        seen.add(nr)
        try:
            nums=[float(row[v]) for v in ("x1","y1","x2","y2","lat","lon","height")]
        except (ValueError,TypeError):
            excluded["nonnumeric_or_blank"]+=1
            continue
        if not all(math.isfinite(v) for v in nums):
            excluded["nonfinite"]+=1
            continue
        if not (-90<nums[4]<90 and -180<nums[5]<180):
            raise ValueError("original drone GPS latlon invalid")
        xys1.append(nums[:2])
        xys2.append(nums[2:4])
        ll.append((nums[5],nums[4]))
        z.append(nums[6])
    if len(xys1)<20:
        raise ValueError("SOURCE_SUPPORT_STOP: fewer than 20 matched source stereo GPS rows")
    if (len(xys1)+sum(excluded.values()))!=len(rows):
        raise ValueError("source matched row support did not reconcile")
    transformer=Transformer.from_crs("EPSG:4326",PROJECTION_CRS,always_xy=True)
    refx,refy=transformer.transform(float(ref[1]),float(ref[0]))
    ll=np.asarray(ll,dtype=float)
    e,n=transformer.transform(ll[:,0],ll[:,1])
    xyz=np.column_stack([e-refx,n-refy,z]).astype(np.float64)
    if not np.isfinite(xyz).all():
        raise ValueError("projected source GPS coordinates invalid")
    return {
        "pixels1":np.asarray(xys1,dtype=np.float64),
        "pixels2":np.asarray(xys2,dtype=np.float64),
        "gps_xyz_ref_m":xyz,
        "source_total_rows":len(rows),
        "source_fully_matched_rows":len(xys1),
        "source_nonnumeric_or_nonfinite_rows_not_imputed":dict(excluded),
        "projected_horizontal":PROJECTION_CRS,
        "original_source_GPS_z_datum":"source reported height, NOT independently validated AGL or orthometric",
    }


def fit_stereo_cameras(train, intrinsics, distortions):
    """Only the source TRAIN flight GPS and camera pixels are used for PnP."""
    xyz=np.asarray(train["gps_xyz_ref_m"],dtype=np.float64)
    if xyz.ndim!=2 or xyz.shape[1]!=3 or len(xyz)<20:
        raise ValueError("invalid original train source point support")
    singular=np.linalg.svd(xyz-xyz.mean(axis=0),compute_uv=False)
    if singular[0]<=0 or singular[1]/singular[0]<.01:
        raise ValueError("train source 3D drone geometry nearly collinear")
    projections=[]
    for pix,K,D in zip((train["pixels1"],train["pixels2"]),intrinsics,distortions):
        if pix.shape!=(len(xyz),2):
            raise ValueError("camera training pixel records do not correspond to source GPS")
        retval,rvec,tvec=cv2.solvePnP(
            xyz.reshape(-1,1,3),pix.reshape(-1,1,2),K,D,
            flags=cv2.SOLVEPNP_SQPNP)
        if not retval or not np.isfinite(rvec).all() or not np.isfinite(tvec).all():
            raise ValueError("OpenCV fixed SQPNP source camera fit failed")
        R,_=cv2.Rodrigues(rvec)
        if not np.isclose(np.linalg.det(R),1.,rtol=0,atol=1e-5):
            raise ValueError("source camera rotation not proper")
        P=K@np.column_stack([R,tvec])
        projections.append(P)
    return projections


def reconstruct_flight_pixels(test,projections):
    pix1=np.asarray(test["pixels1"],dtype=np.float64)
    pix2=np.asarray(test["pixels2"],dtype=np.float64)
    p=cv2.triangulatePoints(
        np.asarray(projections[0],dtype=np.float64),
        np.asarray(projections[1],dtype=np.float64),
        pix1.T,pix2.T)
    if p.shape!=(4,len(pix1)):
        raise ValueError("stereo triangulation output shape mismatch")
    den=p[3,:]
    if not np.isfinite(den).all() or np.any(np.abs(den)<1e-12):
        raise ValueError("stereo triangulation produced unlocalized heldout positions")
    xyz=(p[:3,:]/den[None,:]).T
    if not np.isfinite(xyz).all():
        raise ValueError("stereo triangulation produced nonfinite heldout points")
    return xyz


def evaluate_direction(training,heldout,intrinsics,distortions):
    camera=fit_stereo_cameras(training,intrinsics,distortions)
    xyz=reconstruct_flight_pixels(heldout,camera)
    gps=heldout["gps_xyz_ref_m"]
    if xyz.shape!=gps.shape:
        raise ValueError("predicted heldout drone XYZ dimension differs")
    delta=xyz-gps
    distances=np.linalg.norm(delta,axis=1)
    if not np.isfinite(distances).all():
        raise ValueError("source prediction has nonfinite errors")
    # Pseudo-independent frames must never become a biological p-value.
    return {
        "source_train_matched_GPS_stereo_frames":len(training["gps_xyz_ref_m"]),
        "source_heldout_matched_GPS_stereo_frames":len(gps),
        "heldout_source_reported_GPS_3D_median_error_m":float(np.median(distances)),
        "heldout_source_reported_GPS_3D_mean_error_m":float(np.mean(distances)),
        "heldout_source_reported_GPS_3D_RMSE_m":float(np.sqrt(np.mean(distances**2))),
        "heldout_source_reported_GPS_3D_p90_error_m":float(np.quantile(distances,.9)),
        "heldout_source_reported_GPS_horizontal_mean_error_m":float(
            np.mean(np.linalg.norm(delta[:,:2],axis=1))),
        "heldout_source_reported_GPS_z_mean_absolute_error_source_units":float(
            np.mean(np.abs(delta[:,2]))),
        "original_observations_are_Drone_GPS_not_bat_XYZ":True,
    }


def evaluate_original_source(root:Path):
    raw=verify_files(root)
    intrinsics,distortions,ref=source_camera(raw["camera"])
    trainA=original_drone_stereo(raw["A"],ref,role="A")
    trainB=original_drone_stereo(raw["B"],ref,role="B")
    a_to_b=evaluate_direction(trainA,trainB,intrinsics,distortions)
    b_to_a=evaluate_direction(trainB,trainA,intrinsics,distortions)
    both=[a_to_b,b_to_a]
    admitted=all(s["heldout_source_reported_GPS_3D_median_error_m"]<=3.0
                 and s["heldout_source_reported_GPS_3D_p90_error_m"]<=10.0
                 for s in both)
    return {
        "status":"LOCKED_ORIGINAL_TECHNICAL_TRANSFER_PASS" if admitted else
                  "LOCKED_ORIGINAL_TECHNICAL_CALIBRATION_NOT_TRANSFERABLE",
        "original_source_tag":"v1.0.1",
        "original_author_commit":AUTHOR_COMMIT,
        "original_publication":"Happ et al. 2024 Remote Sensing DOI 10.3390/rs16244682",
        "original_site":"Turbine2 Setup4 wind farm only, two distinct GPS drone flights",
        "source_flight_A_rows":trainA["source_total_rows"],
        "source_flight_B_rows":trainB["source_total_rows"],
        "original_observation_support_A":trainA["source_fully_matched_rows"],
        "original_observation_support_B":trainB["source_fully_matched_rows"],
        "source_GPS_missingness_A":trainA["source_nonnumeric_or_nonfinite_rows_not_imputed"],
        "source_GPS_missingness_B":trainB["source_nonnumeric_or_nonfinite_rows_not_imputed"],
        "holdout_A_to_B":a_to_b,
        "holdout_B_to_A":b_to_a,
        "equal_flight_mean_median_error_m":float(
            np.mean([s["heldout_source_reported_GPS_3D_median_error_m"] for s in both])),
        "max_direction_median_error_m":float(
            max(s["heldout_source_reported_GPS_3D_median_error_m"] for s in both)),
        "predeclared_median_threshold_m":3.0,
        "predeclared_p90_threshold_m":10.0,
        "original_source_vertical_datum_verified_as_AGL":False,
        "actual_bat_flight_XYZ_reconstructed":False,
        "same_site_forest_LiDAR_calibrated":False,
        "not_new_ecological_SDM_or_bat_result":True,
        "independent_forest_field_site_count":0,
    }


def main():
    out=Path("results/happ_GPS_stereo_flight_holdout_v2.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=evaluate_original_source(Path("external/happ"))
    except Exception as exc:
        result={
            "status":"ORIGINAL_GPS_STEREO_SOURCE_OR_CALIBRATION_STOP",
            "reason":str(exc)[:350],
            "exception":type(exc).__name__,
            "no_original_drone_or_bat_scientific_gain_reported":True,
            "actual_bat_flight_XYZ_reconstructed":False,
        }
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
