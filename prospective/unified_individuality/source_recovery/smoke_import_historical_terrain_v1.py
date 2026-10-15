#!/usr/bin/env python3
"""Smoke-import exact original bat-3D terrain runner from recovered source.

No raw GPS, DEM tile, network call, permutation, full model fit or scientific
test is executed. A synthetic probability distribution checks original
historical formula implementation using one artificial horizontal cell.
Installed Python dependency versions are for CURRENT compatibility only:
not a recreation of the original 2026 GitHub Actions environment.
"""
from __future__ import annotations
import argparse
import importlib.util
import os
from pathlib import Path
import sys

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root",type=Path,required=True)
    args=parser.parse_args()
    source=args.source_root.resolve()
    assert (source/"post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py").is_file()
    assert (source/"src/batter/analysis.py").is_file()
    sys.path.insert(0,str(source))
    sys.path.insert(0,str(source/"src"))
    path=source/"post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py"
    spec=importlib.util.spec_from_file_location("historical_original_terrain_source_smoke",path)
    assert spec is not None and spec.loader is not None
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.load_panel_df)
    assert callable(module.load_tiles)
    assert callable(module.geom.pair_metrics)
    assert hasattr(module.ext,"pair_metrics") or hasattr(module.ext,"eval_cohort") or hasattr(module.ext,"load_cfg")
    # Exactly one SYNTHETIC overlapping 500-m cell; two 2-bin personal profiles.
    import numpy as np
    a={
      "cell_n":{(0,0):100},"pxy":{(0,0):1.0},
      "pz":{(0,0):np.array([.7,.3])},"joint":{(0,0):np.array([.7,.3])}
    }
    b={
      "cell_n":{(0,0):100},"pxy":{(0,0):1.0},
      "pz":{(0,0):np.array([.4,.6])},"joint":{(0,0):np.array([.4,.6])}
    }
    result=module.geom.pair_metrics(a,b,min_common=1)
    assert result is not None
    for field,value in [("oxy",1.0),("oxyz",.7),("ozxy",.7),("l3d",.3),("r3d",.3)]:
        assert abs(result[field]-value)<1e-12,(field,result[field],value)
    assert result["shared_cells"]==1
    print("PASS historical terrain import closure from exact Git commit")
    print("PASS historical original joint O_XY/O_XYZ/R3D formula on SYNTHETIC probability input only")
    print("No original bat observations, DEM tiles or hypothesis tests were executed.")

if __name__=="__main__":
    main()
