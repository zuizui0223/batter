"""Source-free known-truth tests: georeference is NEVER inferred from one lamp."""
from __future__ import annotations
import numpy as np
import pytest

from batter.air_volume_registration_v1 import fit_surveyed_rigid_registration


def proven_calibration():
    source=np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]])
    heldout=np.array([[0.,0.,1.],[2.,3.,4.]])
    R=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
    offset=np.array([400000.,5750000.,100.])
    scale=2.0
    observed_world=source*scale@R.T+offset
    validation_world=heldout*scale@R.T+offset
    return source,observed_world,heldout,validation_world,R,offset,scale


def registered(source=None,cal=None,hold=None,truth=None,**kw):
    a,b,c,d,R,t,scale=proven_calibration()
    return fit_surveyed_rigid_registration(
        a if source is None else source,
        b if cal is None else cal,
        c if hold is None else hold,
        d if truth is None else truth,
        source_m_per_unit=kw.get("source_m_per_unit",scale),
        world_horizontal_epsg=kw.get("world_horizontal_epsg","EPSG:25832"),
        world_vertical_datum=kw.get("world_vertical_datum","DHHN2016"),
        max_calibration_rms_m=.5,
        max_independent_validation_error_m=.5,
    )


def test_true_independent_3D_rigid_transform_resolves_synthetic_rotation():
    a,b,c,d,R,offset,scale=proven_calibration()
    model=registered()
    assert model.n_calibration_fiducials==3
    assert model.n_independent_validation_fiducials==2
    np.testing.assert_allclose(model.rotation,R,rtol=0,atol=1e-9)
    np.testing.assert_allclose(model.apply(c),d,rtol=0,atol=1e-7)
    assert model.heldout_max_error_m<1e-7
    assert np.linalg.det(model.rotation)==pytest.approx(1.,abs=1e-12)


def test_same_lamp_over_many_frames_does_not_make_three_tie_points():
    a,b,c,d,R,offset,scale=proven_calibration()
    with pytest.raises(ValueError,match="at least|requires finite|calibration"):
        registered(source=a[:1],cal=b[:1])
    repeated=np.vstack([a[0],a[0],a[0]])
    worldrepeated=np.vstack([b[0],b[0],b[0]])
    with pytest.raises(ValueError,match="coincident"):
        registered(source=repeated,cal=worldrepeated)


def test_collinear_3D_fiducials_are_not_full_rotation_control():
    a,b,c,d,R,offset,scale=proven_calibration()
    source=np.array([[0.,0.,0.],[1.,0.,0.],[2.,0.,0.]])
    world=source*scale@R.T+offset
    with pytest.raises(ValueError,match="collinear"):
        registered(source=source,cal=world)


def test_relabelled_validation_point_is_flagged_not_force_fitted():
    a,b,c,d,R,offset,scale=proven_calibration()
    bad=d.copy()
    bad[0,0]+=2.0
    with pytest.raises(ValueError,match="residual"):
        registered(truth=bad)


def test_unknown_source_scale_and_invalid_geographic_crs_are_hard_stops():
    a,b,c,d,R,offset,scale=proven_calibration()
    with pytest.raises(ValueError,match="source local"):
        registered(source_m_per_unit=None)
    with pytest.raises(ValueError,match="projected metric"):
        registered(world_horizontal_epsg="EPSG:4326")
    with pytest.raises(ValueError,match="vertical datum"):
        registered(world_vertical_datum="unknown")


def test_source_local_calibration_scale_cannot_be_estimated_from_bat_flight():
    a,b,c,d,R,offset,scale=proven_calibration()
    # Synthetic ground-truth world is metric but source local units 2m.
    with pytest.raises(ValueError,match="residual"):
        registered(source_m_per_unit=1.0)


def test_vertical_world_datum_not_AGL_until_independent_ground_model():
    a,b,c,d,R,offset,scale=proven_calibration()
    model=registered()
    world=model.apply(c)
    # synthetic DTM shows terrain 99m and world synthetic elevations 102,108
    ground=np.array([99.,99.])
    agl=model.to_agl(world,ground,ground_vertical_datum="DHHN2016")
    assert agl.tolist()==pytest.approx([3.,9.])
    with pytest.raises(ValueError,match="datum"):
        model.to_agl(world,ground,ground_vertical_datum="EGM96")
    with pytest.raises(ValueError,match="below surveyed ground"):
        model.to_agl(world,np.array([world[0,2]+1,99.]),
                     ground_vertical_datum="DHHN2016")


def test_reference_and_scene_xyz_points_have_safe_shape():
    model=registered()
    with pytest.raises(ValueError,match="3-vectors"):
        model.apply(np.array([1.,2.,3.]))
    with pytest.raises(ValueError,match="finite"):
        model.apply(np.array([[1.,2.,np.nan]]))
