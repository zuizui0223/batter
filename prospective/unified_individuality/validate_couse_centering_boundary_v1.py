#!/usr/bin/env python3
"""Verify historical co-use estimator is a session-centered deviation distance.

Synthetic-only mathematical proof. No original GPS/DEM download or co-use
event/outcome opening, phase-shift permutation, new mechanism test or refit.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HIST=ROOT/"source_recovery"/"co_use_centered_history"
PY_SHA="1f528f0343ac9e6e26851e4adad5c106e8e5dffc"
CONTRACT_SHA="9e5f65772605baaba400e57ea21a9bb91baa819f"


def git_sha(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\x00"+data).hexdigest()


def audit():
    runner=HIST/"run_couse_vertical_separation_v1.py"
    contract=HIST/"couse_vertical_separation_contract_v1.json"
    assert git_sha(runner)==PY_SHA
    assert git_sha(contract)==CONTRACT_SHA
    source=runner.read_text(encoding="utf-8")
    ast.parse(source,filename=str(runner))
    c=json.loads(contract.read_text(encoding="utf-8"))
    assert c["candidate_tolerances_s"]==[60,120,300,600]
    assert c["vertical"]["endpoint"]=="absolute pair difference in DEM-terrain-relative, session-median-centered height"
    assert c["null"]["type"].startswith("fixed observed encounter set")
    for part in (
        'rel=np.array([r["native_h"] for r in records],dtype=float)-terrain',
        'med[key]=float(np.median(rel[ix]))',
        'r["z_rel"]=float(rel[i]-med[(r["cohort"],r["session"])])',
        'sep=np.abs(za-zb)',
        'null[b]=panel_stat(np.abs(za_p-zb_p),di,len(dyad_list))[0]',
    ):
        assert part in source,("Original corrected source formula changed",part)
    assert "za=observed_endpoint_values(group_data,ga,pa)" in source
    assert "zb=observed_endpoint_values(group_data,gb,pb)" in source
    # Two toy encounter examples demonstrate that the original source gap
    # and the actual height gap are independent, even for perfect instruments.
    def gaps(ha,hb,median_a,median_b):
        physical=abs(ha-hb)
        relative=abs((ha-median_a)-(hb-median_b))
        return physical,relative
    assert gaps(100,200,100,200)==(100,0)
    assert gaps(150,150,100,200)==(0,100)
    for ha,hb,ma,mb in [
        (100,200,100,200),
        (150,150,100,200),
        (107,113,99,104),
    ]:
        residual_difference=(ha-ma)-(hb-mb)
        physical_difference=ha-hb
        assert math.isclose(residual_difference,physical_difference-(ma-mb),abs_tol=1e-12)
    print("PASS original corrected co-use source Git hashes and fixed centered-relative-height endpoint")
    print("PASS synthetic counterexamples: physical gap 100 m => source gap 0 m; physical gap 0 m => source gap 100 m")
    print("NOT a real GPS/DEM-based physical altitude gap, independent 2023 rerun or behavioral avoidance finding")


if __name__=="__main__":
    audit()
