"""Synthetic camera reprojection and source integrity before original drone GPS."""
from __future__ import annotations

import csv, io, json
import cv2
import numpy as np
import pytest

from scripts.happ_GPS_stereo_wholeflight_transfer_v2 import (
    fit_stereo_cameras,reconstruct_flight_pixels,evaluate_direction,
    original_drone_stereo,source_camera,
)


def synthetic_flight(seed,n=50):
    rng=np.random.default_rng(seed)
    xyz=np.column_stack([
        rng.uniform(-3.,3.,n),rng.uniform(-3.,3.,n),rng.uniform(12.,30.,n)
    ])
    K=np.array([[800.,0,320],[0,800.,240],[0,0,1.]])
    projections=[
        K@np.column_stack([np.eye(3),np.array([[0.],[0.],[0.]])]),
        K@np.column_stack([np.eye(3),np.array([[-4.],[0.],[0.]])]),
    ]
    xyz4=np.column_stack([xyz,np.ones(n)])
    pixels=[]
    for P in projections:
        p=xyz4@P.T
        pixels.append(p[:,:2]/p[:,2,None])
    return {
        "gps_xyz_ref_m":xyz,"pixels1":pixels[0],"pixels2":pixels[1]
    },(K,K),(np.zeros(4),np.zeros(4))


def test_exact_known_true_stereo_camera_transform_to_heldout_3d_gps():
    train,K,D=synthetic_flight(101,100)
    test,_,_=synthetic_flight(202,48)
    models=fit_stereo_cameras(train,K,D)
    got=reconstruct_flight_pixels(test,models)
    assert np.max(np.linalg.norm(got-test["gps_xyz_ref_m"],axis=1))<1e-5
    result=evaluate_direction(train,test,K,D)
    assert result["source_heldout_matched_GPS_stereo_frames"]==48
    assert result["heldout_source_reported_GPS_3D_median_error_m"]<1e-5


def test_heldout_source_gps_is_never_used_for_fit():
    train,K,D=synthetic_flight(103,100)
    test,_,_=synthetic_flight(204,48)
    models=fit_stereo_cameras(train,K,D)
    predicted1=reconstruct_flight_pixels(test,models)
    changed=dict(test)
    changed["gps_xyz_ref_m"]=test["gps_xyz_ref_m"]+np.array([100.,0.,0.])
    predicted2=reconstruct_flight_pixels(changed,models)
    np.testing.assert_array_equal(predicted1,predicted2)
    first=evaluate_direction(train,test,K,D)
    shifted=evaluate_direction(train,changed,K,D)
    assert shifted["heldout_source_reported_GPS_3D_median_error_m"]>50
    assert first["heldout_source_reported_GPS_3D_median_error_m"]<1e-5


def test_source_drone_rows_need_finite_both_camera_pairs_and_gps():
    out=io.StringIO()
    w=csv.DictWriter(out,fieldnames=[
        "nr","datetime","x1","y1","x2","y2","lat","lon","height"])
    w.writeheader()
    for i in range(25):
        w.writerow({"nr":str(i),"datetime":"same day","x1":300,"y1":200,
                    "x2":"nan" if i==5 else 290,"y2":201,
                    "lat":49.42,"lon":11.44,"height":20.})
    r=original_drone_stereo(out.getvalue().encode(),np.array([49.42,11.44]),role="synthetic")
    assert r["source_total_rows"]==25
    assert r["source_fully_matched_rows"]==24
    assert r["source_nonnumeric_or_nonfinite_rows_not_imputed"]=={"nonfinite":1}
    assert abs(r["gps_xyz_ref_m"][:,0]).max()<1e-7
    assert abs(r["gps_xyz_ref_m"][:,1]).max()<1e-7


def test_duplicate_sensor_frame_does_not_inflate_training_sample():
    out=io.StringIO()
    w=csv.DictWriter(out,fieldnames=[
        "nr","datetime","x1","y1","x2","y2","lat","lon","height"])
    w.writeheader()
    for i in range(24):
        w.writerow({"nr":str(1 if i==23 else i),"datetime":"d",
                    "x1":1,"y1":1,"x2":2,"y2":2,
                    "lat":49.42,"lon":11.44,"height":10})
    with pytest.raises(ValueError,match="duplicate"):
        original_drone_stereo(out.getvalue().encode(),
                              np.array([49.42,11.44]),role="synthetic")


def test_train_source_line_geometry_must_not_be_collinear():
    train,K,D=synthetic_flight(9,40)
    degenerate=dict(train)
    degenerate["gps_xyz_ref_m"]=np.tile(
        np.array([[1.,2.,3.]]),(len(train["gps_xyz_ref_m"]),1))
    with pytest.raises(ValueError,match="collinear"):
        fit_stereo_cameras(degenerate,K,D)


def test_original_intrinsic_source_missing_metadata_fails_closed():
    obj={
        "ref":[49.,11.],
        "camintrinsicMatrix1":[[800,0,320],[0,800,240],[0,0,1]],
        "camintrinsicMatrix2":[[800,0,320],[0,800,240],[0,0,1]],
        "distortion1":[0,0,0,0],
        "distortion2":[0,0,0,0],
    }
    k,d,r=source_camera(json.dumps(obj).encode())
    assert r.tolist()==[49.,11.]
    assert np.array_equal(k[0],k[1])
    del obj["distortion2"]
    with pytest.raises(KeyError):
        source_camera(json.dumps(obj).encode())
