#!/usr/bin/env python3
"""Independent original bat stereo matching replay (post-open arithmetic).

Camera projections are fitted only from the earlier original drone-A flight,
but stereo candidate matching uses a NEW stdlib CSV implementation, not the
original author's batflight3d matching module nor V3's wrapper. This is
algorithmic reproduction on the same published source, not new field ecology.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha1
import csv,json,math
from pathlib import Path
import cv2
import numpy as np

from scripts.happ_GPS_stereo_wholeflight_transfer_v2 import (
    verify_files,source_camera,original_drone_stereo,fit_stereo_cameras
)

BATROOT="data/Turbine2_Setup4_2022-06-23_21-41/images/bat_recording"
BLOBS={
    "IM_PTS_cam1.csv":"3d35611b65d790f8a4ecda01e2cc7600ee242e4a",
    "IM_PTS_cam2.csv":"1f7fddc6b2aa14c13b49bfd5be1dfd109c7c696b",
    "imagelist.csv":"00a0dece532b3e350fc4c8cb8679a6c6863be797",
}
EXPECTED_MATCHES=243
EXPECTED_FRAMES=198
EXPECTED_REPROJECT_MEDIAN=0.5133967673039493
EXPECTED_REPROJECT_P90=1.1312282545741084
EPIPOLAR_PX=6.
AREA_RATIO=4.


def source_blob(path:Path):
    b=path.read_bytes()
    sha=sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if sha!=BLOBS[path.name]:
        raise ValueError("original 2D source file Git hash mismatched")
    return b


def independent_candidate_rows(data:bytes):
    fields=("x","y","area","max_scoreImg","max_innerToRing","nr")
    reader=csv.DictReader(data.decode("utf-8-sig").splitlines())
    if not set(fields).issubset(set(reader.fieldnames or [])):
        raise ValueError("not an original author thermal image point schema")
    out=defaultdict(list)
    row_count=0
    for d in reader:
        row_count+=1
        try:
            vals=[float(d[k]) for k in fields]
        except (ValueError,TypeError):
            continue
        if not all(math.isfinite(v) for v in vals) or vals[2]<=0:
            continue
        if vals[-1]!=int(vals[-1]):
            raise ValueError("original source frame IDs must be integer")
        out[int(vals[-1])].append(tuple(vals[:5]))
    return out,row_count


def independent_source_frames(data:bytes):
    reader=csv.DictReader(data.decode("utf-8-sig").splitlines())
    if not {"nr","datetime"}.issubset(set(reader.fieldnames or [])):
        raise ValueError("original author frame list source missing nr or timestamp")
    seq=[]
    for r in reader:
        n=int(float(r["nr"]))
        if n in seq:
            raise ValueError("original image frame ID repeated")
        seq.append(n)
    return seq


def independent_fundamental(P1:np.ndarray,P2:np.ndarray):
    """F = skew(P2*C1) P2 pinv(P1), independent of V3 camera-extrinsics F."""
    first=np.asarray(P1,dtype=float)
    second=np.asarray(P2,dtype=float)
    if first.shape!=(3,4) or second.shape!=(3,4):
        raise ValueError("projection matrices must be 3×4")
    _,_,V=np.linalg.svd(first)
    c=V[-1]
    if abs(c[-1])<1e-12:
        raise ValueError("camera centre lies at infinity")
    c=c/c[-1]
    e=second@c
    epipolar=np.array([[0,-e[2],e[1]],
                       [e[2],0,-e[0]],
                       [-e[1],e[0],0]])
    F=epipolar@second@np.linalg.pinv(first)
    norm=np.linalg.norm(F)
    if not np.isfinite(F).all() or norm==0 or np.linalg.matrix_rank(F)!=2:
        raise ValueError("independent camera projection has no valid epipolar matrix")
    return F/norm


def independent_original_style_pairs(left,right,F):
    """Replicate author fixed line/area uniqueness without importing V3 code."""
    candidates=[]
    for i,lp in enumerate(left):
        x,y,area,*_=lp
        line=F@np.array([x,y,1.])
        denominator=math.hypot(float(line[0]),float(line[1]))
        if denominator<=0 or not math.isfinite(denominator):
            continue
        for j,rp in enumerate(right):
            u,v,other_area,*_=rp
            if not (1./AREA_RATIO < area/other_area < AREA_RATIO):
                continue
            distance=abs(float(line@np.array([u,v,1.])))/denominator
            if math.isfinite(distance) and distance<=EPIPOLAR_PX:
                candidates.append((i,j))
    if len(candidates)>=2:
        ct_left=Counter(i for i,j in candidates)
        candidates=[(i,j) for i,j in candidates if ct_left[i]==1]
        ct_right=Counter(j for i,j in candidates)
        candidates=[(i,j) for i,j in candidates if ct_right[j]==1]
    return [tuple(left[i][:2])+tuple(right[j][:2]) for i,j in candidates]


def independent_reprojection(source_pairs,world_xyz,P1,P2):
    s=np.asarray(source_pairs,dtype=float)
    xyz=np.asarray(world_xyz,dtype=float)
    if s.shape!=(len(xyz),4):
        raise ValueError("original pixel stereo and independent world coordinates disagree")
    hom=np.column_stack([xyz,np.ones(len(xyz))])
    errs=[]
    for P,col0 in ((P1,0),(P2,2)):
        xyzw=hom@np.asarray(P).T
        if np.any(~np.isfinite(xyzw)) or np.any(abs(xyzw[:,2])<1e-12):
            raise ValueError("unprojectable original stereo bat XYZ candidate")
        uv=xyzw[:,:2]/xyzw[:,2,None]
        errs.append(((uv-s[:,col0:col0+2])**2).sum(axis=1))
    return np.sqrt((errs[0]+errs[1])/2)


def independent_replay(root:Path):
    originals=verify_files(root)
    K,D,ref=source_camera(originals["camera"])
    droneA=original_drone_stereo(originals["A"],ref,role="A")
    P1,P2=fit_stereo_cameras(droneA,K,D)
    F=independent_fundamental(P1,P2)
    batdir=root/BATROOT
    left,ln=independent_candidate_rows(source_blob(batdir/"IM_PTS_cam1.csv"))
    right,rn=independent_candidate_rows(source_blob(batdir/"IM_PTS_cam2.csv"))
    frames=independent_source_frames(source_blob(batdir/"imagelist.csv"))
    all_pairs=[]
    source_frames=[]
    for number in frames:
        for values in independent_original_style_pairs(
            left.get(number,[]),right.get(number,[]),F):
            all_pairs.append(values)
            source_frames.append(number)
    if not all_pairs:
        raise ValueError("independent source author-style stereo matches absent")
    pixels=np.asarray(all_pairs,dtype=float)
    pts=cv2.triangulatePoints(P1,P2,pixels[:,:2].T,pixels[:,2:].T)
    if pts.shape!=(4,len(pixels)) or not np.isfinite(pts).all() or np.any(abs(pts[3])<1e-12):
        raise ValueError("independent source 3D triangulation invalid")
    xyz=(pts[:3]/pts[3][None,:]).T
    pixerr=independent_reprojection(pixels,xyz,P1,P2)
    median=float(np.median(pixerr))
    p90=float(np.quantile(pixerr,.9))
    matches=len(pixels)
    unique=len(set(source_frames))
    if matches!=EXPECTED_MATCHES or unique!=EXPECTED_FRAMES or (
        abs(median-EXPECTED_REPROJECT_MEDIAN)>1e-7
        or abs(p90-EXPECTED_REPROJECT_P90)>1e-7
    ):
        raise RuntimeError(
            f"V4_ALGORITHM_REPLAY_MISMATCH: stereo_pairs={matches}, frames={unique}, "
            f"median_px={median:.8f}, p90_px={p90:.8f}, no outcome retuning")
    return {
        "status":"INDEPENDENT_ORIGINAL_AUTHOR_BAT_STEREO_MATCHING_AGREEMENT",
        "source_public_author_tag":"v1.0.1",
        "original_author_Git_commit":"34d2f56bcee1eab9207890938aedd90a079bfcde",
        "source_left_candidate_rows":ln,
        "source_right_candidate_rows":rn,
        "source_original_image_frame_timestamps":len(frames),
        "independently_reconstructed_original_stereo_pairs":matches,
        "independent_unique_original_image_frames":unique,
        "independent_world_XYZ_finite_coordinate_points":len(xyz),
        "independent_stereo_reprojection_median_px":median,
        "independent_stereo_reprojection_p90_px":p90,
        "absolute_discrepancy_v3_median_px":abs(median-EXPECTED_REPROJECT_MEDIAN),
        "absolute_discrepancy_v3_p90_px":abs(p90-EXPECTED_REPROJECT_P90),
        "pairing_engine":"stdlib CSV + independent projective F, no V3 or author source matching import",
        "gps_stereo_camera_pose_source":"V2 original drone flight A only",
        "source_bat_3D_position_true_error_known":False,
        "source_3D_detection_q_calibrated":False,
        "bat_species_identified_from_original_thermal_video":False,
        "forest_LiDAR_co_registered":False,
        "real_3D_bat_airspace_niche_effect_estimated":False,
    }


def main():
    path=Path("results/happ_real_bat_stereo_independent_v4.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=independent_replay(Path("external/happ"))
    except Exception as exc:
        result={
            "status":"INDEPENDENT_BAT_STEREO_SOURCE_OR_ALGORITHM_MISMATCH_STOP",
            "error_type":type(exc).__name__,
            "reason":str(exc)[:450],
            "original_v3_source_result_not_overwritten":True,
            "real_3D_bat_airspace_niche_effect_estimated":False,
        }
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
