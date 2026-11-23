#!/usr/bin/env python3
"""Source-free synthetic 3D air-volume and 2D-projection proof receipt.

All data are purpose-built mathematical fixtures, NOT real bat occurrences.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

from batter.air_volume_sdm_v1 import (
    regular_air_volume,binned_3d_kernel,expected_counts,log_intensity,
    fit_fixed_grid_known_kernel,score_known_kernel,
    synthetic_multispecies_projection_witness,kernel_rank_diagnostic,
)


def run():
    # Two heldout *synthetic sites* represented by half of a 4x2x2 voxel
    # volume: x 0:2 train, x 2:4 test, 1m³ each and all declared known air.
    v=regular_air_volume((0,4,0,2,0,2),1,[1]*16,crs="local_projected_m")
    xyz=v.centers_m
    ix=np.floor(xyz[:,0]).astype(int)
    iy=np.floor(xyz[:,1]).astype(int)
    iz=np.floor(xyz[:,2]).astype(int)
    h=iz.astype(float)
    # Illustrative vegetation-near/far label; no real laser ray tracing.
    clutter=((ix+iy+iz)%2).astype(float)
    expected_source_lam=log_intensity(v,h,clutter,3.,0.,2.)
    k=binned_3d_kernel(v)
    observed=np.rint(expected_counts(v,expected_source_lam,k,
                                    np.ones(len(k)))).astype(int)
    train=np.flatnonzero(ix<2)
    test=np.flatnonzero(ix>=2)
    train_k=k[train]
    test_k=k[test]
    baseline=fit_fixed_grid_known_kernel(
        v,h,clutter,train_k,np.ones(len(train)),observed[train],
        use_clutter=False)
    with_clutter=fit_fixed_grid_known_kernel(
        v,h,clutter,train_k,np.ones(len(train)),observed[train],
        use_clutter=True)
    b0=score_known_kernel(v,h,clutter,test_k,np.ones(len(test)),
                          observed[test],baseline)
    b1=score_known_kernel(v,h,clutter,test_k,np.ones(len(test)),
                          observed[test],with_clutter)
    result={
        "status":"synthetic_known_truth_air_volume_model_executed",
        "original_bat_field_data_processed":False,
        "physical_voxel_edge_m":1.0,
        "explicit_source_air_voxels":16,
        "air_volume_m3":float(v.voxel_volume_m3.sum()),
        "synthetic_known_true_clutter_coefficient":2.0,
        "synthetic_train_voxels":len(train),
        "synthetic_heldout_voxels":len(test),
        "assumed_source_q":"known_ideal_exact_localisation_in_synthetic_fixture",
        "height_only_fitted_intercept_height_clutter":list(baseline),
        "volume_clutter_fitted_intercept_height_clutter":list(with_clutter),
        "heldout_synthetic_height_only_log_score":b0,
        "heldout_synthetic_3D_clutter_log_score":b1,
        "heldout_synthetic_gain_b1_minus_b0":b1-b0,
        "planar_observation_identifiability_counterexample":
           synthetic_multispecies_projection_witness(),
        "no_field_source_replicated":True,
        "no_real_animal_3d_predictive_claim":True,
    }
    if not (b1>b0 and result["planar_observation_identifiability_counterexample"]["same_observed_planar_data"]):
        raise RuntimeError("synthetic positive control or planar nonidentifiability failed")
    return result


def main():
    result=run()
    out=Path("results/prospective_air_volume_synthetic_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
