"""Synthetic known-truth controls for true air-volume observation-aware bat SDM.

No bat empirical response is loaded. These are **mathematical engineering tests**.
"""
from __future__ import annotations

import numpy as np
import pytest

from batter.air_volume_sdm_v1 import (
    AirVolume, regular_air_volume,
    nearest_vegetation_distance_m, clutter_proximity_proxy,
    planar_column_kernel, binned_3d_kernel, acoustic_footprint_kernel,
    validate_measurements, expected_counts, poisson_loglik,
    kernel_rank_diagnostic, log_intensity, fit_fixed_grid_known_kernel,
    score_known_kernel, synthetic_multispecies_projection_witness,
)


def tiny_world():
    return AirVolume(
        np.array([[0.5,0.5,0.5],[0.5,0.5,1.5],
                  [1.5,0.5,0.5],[1.5,0.5,1.5]]),
        np.ones(4), np.ones(4,dtype=int),
        ("xy0","xy0","xy1","xy1"),
        crs="local_projected_m",
    )


def test_real_air_volume_is_cubic_and_not_surfaces():
    v=regular_air_volume((0,2,0,1,0,2),1,[1,1,1,1])
    assert len(v.centers_m)==4
    assert np.all(v.voxel_volume_m3==1)
    assert v.centers_m[0].tolist()==[.5,.5,.5]
    assert v.horizontal_cell[0]==v.horizontal_cell[1]
    with pytest.raises(ValueError,match="AGL"):
        AirVolume(v.centers_m,v.voxel_volume_m3,v.classification,
                  v.horizontal_cell,"local_projected_m","MSL")
    with pytest.raises(ValueError,match="projected"):
        AirVolume(v.centers_m,v.voxel_volume_m3,v.classification,
                  v.horizontal_cell,"EPSG:4326")


def test_planar_projection_cannot_identify_height_separation():
    w=synthetic_multispecies_projection_witness()
    assert w["same_observed_planar_data"]
    assert w["planar_counts_world_A"]==[100,100]
    assert w["planar_counts_world_B"]==[100,100]
    assert w["latent_species_by_height_info_A_nats"]==pytest.approx(
        0.3680642071684971,rel=1e-12)
    assert w["latent_species_by_height_info_B_nats"]==pytest.approx(0)
    assert w["known_planar_kernel_rank"]["unidentified_arbitrary_voxel_directions"]==1
    assert not w["known_planar_kernel_rank"]["arbitrary_voxel_intensities_fully_linearly_identifiable"]


def test_3d_kernel_has_full_rank_in_exact_synthetic_case_and_planar_does_not():
    v=tiny_world()
    planar,_=planar_column_kernel(v)
    assert kernel_rank_diagnostic(v,planar)["independent_linear_measurement_rank"]==2
    assert kernel_rank_diagnostic(v,planar)["unidentified_arbitrary_voxel_directions"]==2
    point=binned_3d_kernel(v)
    assert kernel_rank_diagnostic(v,point)["independent_linear_measurement_rank"]==4


def test_voxel_cubic_volume_and_detector_exposure_not_pixel_area():
    v=tiny_world()
    k,_=planar_column_kernel(v)
    lam=np.array([1,3,2,4],dtype=float)
    y=expected_counts(v,lam,k,np.array([1,1]))
    assert y.tolist()==[4,6]
    volume2=AirVolume(v.centers_m,v.voxel_volume_m3*2,v.classification,
                      v.horizontal_cell,v.crs)
    assert expected_counts(volume2,lam,k,np.ones(2)).tolist()==[8,12]
    assert expected_counts(v,lam,k,np.array([2,2])).tolist()==[8,12]


def test_lidar_return_absence_does_not_certify_free_air():
    v=AirVolume(
        centers_m=np.array([[.5,.5,.5],[.5,.5,1.5],[1.5,.5,.5],[1.5,.5,1.5]]),
        voxel_volume_m3=np.ones(4),
        classification=np.array([1,-1,0,1]),
        horizontal_cell=("xy0","xy0","xy1","xy1"),
        crs="local_projected_m",
    )
    with pytest.raises(ValueError,match="empty"):
        nearest_vegetation_distance_m(v,np.empty((0,3)))
    d=nearest_vegetation_distance_m(v,np.array([[.5,0,.5]]))
    assert d[0]==pytest.approx(.5)
    assert np.isnan(d[1]) and np.isnan(d[2])
    assert d[3]>0
    c=clutter_proximity_proxy(d,1.)
    assert c[0]==pytest.approx(np.exp(-.5))
    assert np.isnan(c[1])
    k,_=planar_column_kernel(v)
    assert k[:,1].sum()==0 and k[:,2].sum()==0
    assert expected_counts(v,np.array([1.,0.,0.,2.]),k,np.ones(2)).sum()==pytest.approx(3)
    with pytest.raises(ValueError,match="unresolved"):
        expected_counts(v,np.array([1.,1.,0.,2.]),k,np.ones(2))


def test_source_specific_detection_kernel_probability_must_be_calibrated():
    v=tiny_world()
    m=np.array([[.5,.5,.5],[1.5,.5,.5]])
    q=np.array([.8,.8,.5,.5])
    k=acoustic_footprint_kernel(v,m,q,2.)
    assert k.shape==(2,4)
    assert np.all(k>=0) and np.all(k<=1)
    assert k[0,0]==pytest.approx(.8)
    assert k[1,2]==pytest.approx(.5)
    with pytest.raises(ValueError,match="calibrated detector"):
        acoustic_footprint_kernel(v,m,np.array([1,1,1,2]),2.)
    with pytest.raises(ValueError,match="K cannot"):
        validate_measurements(v,k*4,np.ones(2))


def test_positive_counts_with_zero_detection_footprint_are_impossible():
    v=tiny_world()
    k=np.zeros((1,4))
    y=np.array([1])
    with pytest.raises(ValueError,match="no source-known q"):
        fit_fixed_grid_known_kernel(v,v.centers_m[:,2],np.zeros(4),k,np.ones(1),y,
                                    use_clutter=True)
    assert poisson_loglik(y,np.zeros(1))==float("-inf")
    with pytest.raises(ValueError,match="source counts"):
        validate_measurements(v,k,np.ones(1),np.array([-1]))


def _source_synthetic_known_q_plot_split(with_clutter):
    v=regular_air_volume((0,4,0,2,0,2),1,[1]*16)
    coords=v.centers_m
    ix=np.floor(coords[:,0]).astype(int)
    iy=np.floor(coords[:,1]).astype(int)
    iz=np.floor(coords[:,2]).astype(int)
    h=iz.astype(float)
    c=((ix+iy+iz)%2).astype(float)
    beta_c=2.0 if with_clutter else 0.0
    original=log_intensity(v,h,c,3.,0.,beta_c)
    k=binned_3d_kernel(v)
    count=np.rint(expected_counts(v,original,k,np.ones(16))).astype(int)
    train=np.nonzero(ix<2)[0]
    test=np.nonzero(ix>=2)[0]
    return v,h,c,k[train],k[test],count[train],count[test]


def test_3d_clutter_can_predict_heldout_synthetic_plot_beyond_height_only():
    v,h,c,ktr,kte,ytr,yte=_source_synthetic_known_q_plot_split(True)
    b0=fit_fixed_grid_known_kernel(v,h,c,ktr,np.ones(len(ytr)),ytr,
                                   use_clutter=False)
    b1=fit_fixed_grid_known_kernel(v,h,c,ktr,np.ones(len(ytr)),ytr,
                                   use_clutter=True)
    a=score_known_kernel(v,h,c,kte,np.ones(len(yte)),yte,b0)
    b=score_known_kernel(v,h,c,kte,np.ones(len(yte)),yte,b1)
    assert b>a+20
    assert b1[2]==pytest.approx(2.)
    assert b0[2]==pytest.approx(0)


def test_no_clutter_signal_in_synthetic_world_needs_no_clutter():
    v,h,c,ktr,kte,ytr,yte=_source_synthetic_known_q_plot_split(False)
    b0=fit_fixed_grid_known_kernel(v,h,c,ktr,np.ones(len(ytr)),ytr,
                                   use_clutter=False)
    b1=fit_fixed_grid_known_kernel(v,h,c,ktr,np.ones(len(ytr)),ytr,
                                   use_clutter=True)
    assert b1[2]==pytest.approx(0)
    a=score_known_kernel(v,h,c,kte,np.ones(len(yte)),yte,b0)
    b=score_known_kernel(v,h,c,kte,np.ones(len(yte)),yte,b1)
    assert b==pytest.approx(a)


def test_unknown_voxels_cannot_be_an_observed_negative_control():
    v=AirVolume(
        np.array([[0.5,0.5,.5],[.5,.5,1.5]]),
        np.array([1,1]),
        np.array([1,-1]),
        ("xy0","xy0"),
        "local_projected_m",
    )
    k=np.array([[1,0]])
    mu=expected_counts(v,np.array([2.,0.]),k,np.ones(1))
    assert mu[0]==pytest.approx(2)
    bad_k=np.array([[1,1]])
    with pytest.raises(ValueError,match="unknown and vegetation"):
        validate_measurements(v,bad_k,np.ones(1))
