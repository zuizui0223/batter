#!/usr/bin/env python3
"""Real thermal bat source stereo reconstruction with independent drone GPS PnP.

This calls ORIGINAL AUTHOR point correspondence code from pinned GitHub v1.0.1,
without editing its thresholds. Only aggregates geometry/QC are released.
It does not claim verified bat GPS accuracy, species identity, 3D AGL, LiDAR
registration, plant clutter or an ecological point-process result.

V3 contract: docs/HAPP_REAL_BAT_THERMAL_STEREO_V3_PRE_SOURCE_OPEN_20261124.md
"""
from __future__ import annotations
from collections import Counter
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout
import hashlib,importlib,json,math,sys
from types import SimpleNamespace

import cv2
import numpy as np
import pandas as pd

from scripts.happ_GPS_stereo_wholeflight_transfer_v2 import (
    verify_files,source_camera,original_drone_stereo,fit_stereo_cameras,
)

RECORDING="data/Turbine2_Setup4_2022-06-23_21-41/images/bat_recording"
FIXED_BLOBS={
    "IM_PTS_cam1.csv":"3d35611b65d790f8a4ecda01e2cc7600ee242e4a",
    "IM_PTS_cam2.csv":"1f7fddc6b2aa14c13b49bfd5be1dfd109c7c696b",
    "imagelist.csv":"00a0dece532b3e350fc4c8cb8679a6c6863be797",
}
READ_COLUMNS=("x","y","area","max_scoreImg","max_innerToRing","nr")


def git_blob_hash(data:bytes):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()


def fundamental_from_known_source_projections(P1,P2,K1,K2):
    """R, t derived from original source P=K[R|t], no bat data used."""
    a=np.linalg.inv(K1)@np.asarray(P1,dtype=float)
    b=np.linalg.inv(K2)@np.asarray(P2,dtype=float)
    r1,t1=a[:,:3],a[:,3]
    r2,t2=b[:,:3],b[:,3]
    if not np.isclose(np.linalg.det(r1),1.,atol=1e-5):
        raise ValueError("source fitted first camera is not rigid")
    if not np.isclose(np.linalg.det(r2),1.,atol=1e-5):
        raise ValueError("source fitted second camera is not rigid")
    R=r2@r1.T
    T=t2-R@t1
    skew=np.array([[0,-T[2],T[1]],
                   [T[2],0,-T[0]],
                   [-T[1],T[0],0]])
    f=np.linalg.inv(K2).T@skew@R@np.linalg.inv(K1)
    norm=np.linalg.norm(f)
    if not np.isfinite(f).all() or norm==0 or np.linalg.matrix_rank(f)!=2:
        raise ValueError("source stereo fundamental matrix cannot be calculated")
    return f/norm


def source_candidate_metadata(path:Path):
    data=path.read_bytes()
    if git_blob_hash(data)!=FIXED_BLOBS[path.name]:
        raise ValueError("author original bat 2D source file identity mismatch")
    raw=pd.read_csv(path)
    if not set(READ_COLUMNS).issubset(raw.columns):
        raise ValueError("author original bat 2D source columns changed")
    columns=list(READ_COLUMNS)
    selected=raw[columns].copy()
    for c in columns:
        selected[c]=pd.to_numeric(selected[c],errors="coerce")
    mask=np.isfinite(selected.to_numpy(dtype=float)).all(axis=1)
    mask &= selected["area"].to_numpy()>0
    return selected.loc[mask].copy(),{
        "original_source_rows":len(raw),
        "source_candidate_rows_finite_positive_area":int(mask.sum()),
        "source_missing_or_nonpositive_area_rows":int((~mask).sum()),
        "source_git_blob_sha1":git_blob_hash(data),
        "original_numeric_bat_2d_pixels_used_for_matching_only":True,
    }


def source_image_times(path:Path):
    data=path.read_bytes()
    if git_blob_hash(data)!=FIXED_BLOBS["imagelist.csv"]:
        raise ValueError("author original frame clock source identity mismatch")
    table=pd.read_csv(path)
    if not {"nr","datetime"}.issubset(table.columns):
        raise ValueError("author original frame timestamp structure changed")
    if table["nr"].duplicated().any():
        raise ValueError("duplicate original source frame ID")
    return table


def reprojection_residual_px(points_xyz, image_matches, P1,P2):
    pts=np.asarray(points_xyz,dtype=np.float64)
    pix=np.asarray(image_matches,dtype=np.float64)
    if pts.ndim!=2 or pts.shape[1]!=3 or pix.shape!=(len(pts),4):
        raise ValueError("bat stereo matches and XYZ points do not align")
    homog=np.column_stack([pts,np.ones(len(pts))])
    errors=[]
    valid=[]
    for P,cols in ((P1,(0,1)),(P2,(2,3))):
        projected=homog@np.asarray(P).T
        denom=projected[:,2]
        good=np.isfinite(projected).all(axis=1)&(abs(denom)>1e-12)
        xy=np.full((len(pts),2),np.nan)
        xy[good]=projected[good,:2]/denom[good,None]
        errs=np.linalg.norm(xy-pix[:,cols],axis=1)
        errors.append(errs)
        valid.append(good&np.isfinite(errs))
    final=valid[0]&valid[1]
    # Geometric error in pixels; DOES NOT independently measure true 3D error
    combined=np.sqrt((errors[0]**2+errors[1]**2)/2)
    return combined,final


def reconstruct_source(root:Path):
    verified=verify_files(root)
    intr,dist,ref=source_camera(verified["camera"])
    # Only original earlier drone flight A is in the TRAIN set.
    camera_fit=original_drone_stereo(verified["A"],ref,role="A")
    P1,P2=fit_stereo_cameras(camera_fit,intr,dist)
    F=fundamental_from_known_source_projections(P1,P2,*intr)
    batdir=root/RECORDING
    left,meta_l=source_candidate_metadata(batdir/"IM_PTS_cam1.csv")
    right,meta_r=source_candidate_metadata(batdir/"IM_PTS_cam2.csv")
    frames=source_image_times(batdir/"imagelist.csv")

    # Unmodified original published correspondence function and thresholds.
    # Original modules import pandas/scikit-image/scikit-learn and utm.
    sys.path.insert(0,str(root.resolve()))
    author=importlib.import_module("batflight3d")
    author.load_config_json(str(root/"data/parameters_Turbine2.json"))
    if (float(author.config["maxDistFromEpiline"])!=6.0 or
        float(author.config["areaRatio"])!=4.0):
        raise ValueError("author published original stereo pairing thresholds changed")
    author.load_CSV_Imagelist_path(str(batdir/"imagelist.csv"))
    author_calib=SimpleNamespace(F=F,Pr1=P1,Pr2=P2)
    with redirect_stdout(StringIO()):
        matching=author.load_and_correspond_PTS(author_calib,left,right)
    if len(matching)==0:
        raise ValueError("SOURCE_BAT_3D_RECONSTRUCTION_STOP: no original author stereo correspondences")
    pixel=matching[["x1","y1","x2","y2"]].to_numpy(dtype=float)
    if not np.isfinite(pixel).all():
        raise ValueError("bat source image pairing produced nonfinite pixels")
    triangulated=cv2.triangulatePoints(P1,P2,pixel[:,:2].T,pixel[:,2:].T)
    if triangulated.shape!=(4,len(matching)):
        raise ValueError("wrong bat 3D triangulation dimensions")
    den=triangulated[3]
    good=np.isfinite(triangulated).all(axis=0)&(abs(den)>1e-12)
    xyz=np.full((len(matching),3),np.nan)
    xyz[good]= (triangulated[:3,good]/den[good][None,:]).T
    pixerr,goodreproj=reprojection_residual_px(xyz,pixel,P1,P2)
    valid=good&goodreproj
    if int(valid.sum())==0:
        raise ValueError("SOURCE_BAT_3D_RECONSTRUCTION_STOP: no valid original bat world stereo positions")
    per_frame=matching["nr"].to_numpy()[valid]
    return {
        "status":"REAL_PUBLIC_BAT_STEREO_GPS_REFERENCED_GEOMETRY_QC_ONLY",
        "source_original_tag":"v1.0.1",
        "original_source_author":"christofhapp/batflight3D_publication",
        "original_source_commit":"34d2f56bcee1eab9207890938aedd90a079bfcde",
        "original_publication":"Happ et al. 2024 Remote Sensing 16:4682",
        "camera_A_only_train_drone_GPS_rows":len(camera_fit["gps_xyz_ref_m"]),
        "source_bat_left_precomputed_candidate_metadata":meta_l,
        "source_bat_right_precomputed_candidate_metadata":meta_r,
        "original_source_image_frame_timestamps":len(frames),
        "stereo_2d_correspondence_pairs_published_algorithm":len(matching),
        "valid_reconstructed_source_bat_xyz_points":int(valid.sum()),
        "original_stereo_pairs_failed_triangular_reconstruction":int((~valid).sum()),
        "source_unique_image_frames_with_valid_XYZ":len(set(per_frame)),
        "bat_stereo_reprojection_error_median_px":float(np.median(pixerr[valid])),
        "bat_stereo_reprojection_error_p90_px":float(np.quantile(pixerr[valid],.9)),
        "coordinate_source_horizontal":"source GPS-referenced EPSG:32632 XY relative to author ref",
        "coordinate_source_vertical":"author drone GPS height channel, NOT independently surveyed bat AGL",
        "camera_pairing_parameters":{"maxDistFromEpiline_px":6.0,
                                     "source_areaRatio":4.0},
        "source_bat_xyz_independently_measured_with_GPS":False,
        "source_bat_species_identity_confirmed":False,
        "source_3D_detection_q_calibrated":False,
        "vegetation_LiDAR_overlaid_or_real_3D_SDM_fitted":False,
        "all_result_xyz_raw_rows_redacted":True,
    }


def main():
    path=Path("results/happ_GPS_bat_stereo_localisation_v3.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=reconstruct_source(Path("external/happ"))
    except Exception as exc:
        result={
            "status":"SOURCE_REAL_BAT_STEREO_RECONSTRUCTION_OR_FORMAT_STOP",
            "error_type":type(exc).__name__,
            "reason":str(exc)[:400],
            "vegetation_LiDAR_overlaid_or_real_3D_SDM_fitted":False,
        }
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
