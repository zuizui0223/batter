"""Source-free hard tests for real thermal bat source v3 geometry bridge."""
from __future__ import annotations
import hashlib
import numpy as np
import pytest

from scripts.happ_real_bat_stereo_source_v3 import (
    fundamental_from_known_source_projections,
    reprojection_residual_px,git_blob_hash,
)


def fake_cameras():
    K=np.array([[800.,0,320],[0,800.,240],[0,0,1.]])
    P1=K@np.column_stack([np.eye(3),np.zeros(3)])
    P2=K@np.column_stack([np.eye(3),np.array([-4.,0.,0.])])
    return P1,P2,K


def project(P,XYZ):
    q=np.column_stack([XYZ,np.ones(len(XYZ))])@P.T
    return q[:,:2]/q[:,2,None]


def test_fundamental_epipolar_geometry_satisfies_true_stereo_points():
    P1,P2,K=fake_cameras()
    f=fundamental_from_known_source_projections(P1,P2,K,K)
    xyz=np.array([[0.,0.,20.],[3.,2.,15.],[-2.,1.,30.]])
    l=project(P1,xyz);r=project(P2,xyz)
    assert np.linalg.matrix_rank(f)==2
    for p,q in zip(l,r):
        a=np.append(p,1.)
        b=np.append(q,1.)
        assert abs(float(b@f@a))<1e-10


def test_stereo_reprojection_pixel_residual_known_truth_is_zero():
    P1,P2,K=fake_cameras()
    xyz=np.array([[0.,0.,20.],[3.,2.,15.],[-2.,1.,30.]])
    pixels=np.column_stack([project(P1,xyz),project(P2,xyz)])
    errs,valid=reprojection_residual_px(xyz,pixels,P1,P2)
    assert valid.tolist()==[True,True,True]
    np.testing.assert_allclose(errs,0,rtol=0,atol=1e-12)


def test_incomplete_source_reconstruction_is_not_zero_height():
    P1,P2,K=fake_cameras()
    xyz=np.array([[0.,0.,20.],[np.nan,np.nan,np.nan]])
    pixels=np.array([[320,240,160,240],[320,240,160,240]],dtype=float)
    errs,valid=reprojection_residual_px(xyz,pixels,P1,P2)
    assert valid.tolist()==[True,False]
    assert np.isnan(errs[1])


def test_wrong_coordinate_frame_and_source_array_shape_cannot_be_silenced():
    P1,P2,K=fake_cameras()
    with pytest.raises(ValueError,match="rigid"):
        fundamental_from_known_source_projections(P1*2,P2,K,K)
    with pytest.raises(ValueError,match="align"):
        reprojection_residual_px(np.ones((2,3)),np.ones((3,4)),P1,P2)


def test_original_git_blob_hash_known_truth():
    data=b"abc\n"
    expect=hashlib.sha1(b"blob 4\0abc\n").hexdigest()
    assert git_blob_hash(data)==expect
