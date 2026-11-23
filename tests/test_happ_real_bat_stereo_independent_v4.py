"""Pure synthetic tests for independently reproduced author stereo candidate matcher."""
import numpy as np
import pytest
pytest.importorskip('cv2')

from scripts.verify_happ_real_bat_stereo_v4_independent import (
    independent_fundamental,independent_original_style_pairs,
    independent_reprojection
)


def test_system():
    K=np.array([[800.,0,320],[0,800.,240],[0,0,1.]])
    p1=K@np.column_stack([np.eye(3),np.zeros(3)])
    p2=K@np.column_stack([np.eye(3),np.array([-4.,0.,0.])])
    return p1,p2


def test_source_independent_projective_F_satisfies_epipolar_geometry():
    p1,p2=test_system()
    F=independent_fundamental(p1,p2)
    assert np.linalg.matrix_rank(F)==2
    world=np.array([[0,0,20],[2,1,25]],dtype=float)
    def project(p):
        t=np.column_stack([world,np.ones(len(world))])@p.T
        return t[:,:2]/t[:,2,None]
    l=project(p1);r=project(p2)
    for pt1,pt2 in zip(l,r):
        assert abs(np.append(pt2,1)@F@np.append(pt1,1))<1e-9


def test_source_original_epipolar_distance_and_area_rules():
    p1,p2=test_system()
    F=independent_fundamental(p1,p2)
    left=[(320.,240.,20.,2.,4.),(320.,300.,20.,3.,4.)]
    right=[(160.,240.,20.,2.,4.),(160.,300.,20.,3.,4.)]
    pairs=independent_original_style_pairs(left,right,F)
    assert pairs==[(320.,240.,160.,240.),(320.,300.,160.,300.)]


def test_ambiguous_right_correspondence_rejected_without_choose_nearest():
    p1,p2=test_system()
    F=independent_fundamental(p1,p2)
    left=[(320.,240.,20.,2.,4.),(350.,240.,20.,3.,4.)]
    right=[(160.,240.,20.,2.,4.)]
    assert independent_original_style_pairs(left,right,F)==[]


def test_source_area_ratio_exact_boundary_not_admitted():
    p1,p2=test_system()
    F=independent_fundamental(p1,p2)
    left=[(320.,240.,8.,3.,4.)]
    right=[(160.,240.,2.,3.,4.)]
    assert independent_original_style_pairs(left,right,F)==[]


def test_separate_world_projection_residual_known_zero():
    p1,p2=test_system()
    xyz=np.array([[0.,0.,20.],[1.,2.,15.]])
    h=np.column_stack([xyz,np.ones(len(xyz))])
    def project(p):
        q=h@p.T
        return q[:,:2]/q[:,2,None]
    pixels=np.column_stack([project(p1),project(p2)])
    errs=independent_reprojection(pixels,xyz,p1,p2)
    np.testing.assert_allclose(errs,np.zeros(2),rtol=0,atol=1e-10)
