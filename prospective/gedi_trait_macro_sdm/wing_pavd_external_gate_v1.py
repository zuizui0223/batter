"""No new fit. Verify frozen model, then score the preregistered external sample.
No raw locations, new trait choices, or replacement of frozen coefficients.
"""
import json,math,pathlib,hashlib,sys
import numpy as np
import wing_pavd_continental_transfer_v1 as w
O=pathlib.Path("wing_external_gate");O.mkdir(exist_ok=True)
MODEL="3e282cdcf4d21bf41234f1cae0e2ef71a3359269c68d592742c10101ac1feb97"
GRID="35fd3897562e9b8a6ee909d86b3d36c429098d939ace120016d76f1815a6fa7c"
R={"stage":"frozen wing-PAVD external scoring integrity gate","status":"START","training_run":45718786057,"predecessor_FWS_run":45717643905,"model_sha256":MODEL,"new_fit":False}
def save():
    (O/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False)+"\n")
    print("WING_EXTERNAL_GATE_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def preflight():
    p=pathlib.Path("frozen/frozen_model.json")
    q=json.loads(p.with_name("report.json").read_text())
    assert w.sha(p)==MODEL==q["model_sha256"]
    assert q["status"]=="TRAINED_FROZEN_COEFFICIENTS_NO_EXTERNAL_SCORE"
    assert q["measured_grid_sha256"]==GRID and q["source_trait_sha256"]==w.PIN
    m=json.loads(p.read_text())
    assert m["environment"]==w.ENV and m["traits"]==w.TRAITS
    assert m["trait_source_sha256"]==w.PIN and len(set(m["train_names"]))==14
    assert m["training_support"]=={"train_comparisons":20336,"train_blocks":46,"train_cells":1132,"train_taxa":14}
    t=w.traits();assert set(m["train_names"])<=set(t.index)
    s=m["stats"];assert len(s["env_sd"])==len(w.ENV) and len(s["trait_sd"])==3
    assert np.isfinite(s["env_sd"]).all() and np.isfinite(s["trait_sd"]).all()
    assert np.all(np.array(s["env_sd"])>0) and np.all(np.array(s["trait_sd"])>0)
    for prefix in ("env","trait"):
        lo=np.asarray(s[prefix+"_min"]);hi=np.asarray(s[prefix+"_max"])
        assert lo.shape==hi.shape and np.isfinite(lo).all() and np.isfinite(hi).all() and (lo<=hi).all()
    # Independently verify analytic orientation symmetry and the neutral case.
    # Artificial vectors: one SD difference in AR or the full three-trait vector,
    # with one SD difference in the PAVD lower fraction. No real test observations.
    D=np.array(s["env_sd"]);T=np.array(s["trait_sd"])
    raw=np.stack([D,np.zeros_like(D)])
    traits=np.stack([T,np.zeros_like(T)])
    z=np.array([[0,1,0,1,0],[1,0,0,1,0],[0,1,1,0,0],[1,0,1,0,0]])
    checks={}
    for k in w.MOD:
        co=np.array(m["coefficients"][k]);n=1 if k.startswith("AR") else 3;e=len(w.ENV) if k.endswith("_M") else len(w.ENV)-1
        assert co.shape==(n*e,) and np.isfinite(co).all()
        x=w.inputs(z,raw,traits,s,k)
        assert np.array_equal(x[0],np.ones(n*e))
        h=x@co
        assert np.allclose(h,[co.sum(),-co.sum(),-co.sum(),co.sum()],rtol=1e-12,atol=1e-12)
        assert np.allclose(w.inputs(z,raw,np.zeros_like(traits),s,k),0)
        assert np.allclose(w.inputs(z,np.zeros_like(raw),traits,s,k),0)
        for idx in range(n):
            # Isolate a single trait and the final environment coordinate.
            tr=np.zeros_like(traits);tr[0,idx]=T[idx]
            en=np.zeros_like(raw);en[0,-1]=D[-1]
            got=float(w.inputs(z[:1],en,tr,s,k)[0]@co)
            exp=float(co.reshape(n,e)[idx,-1]) if k.endswith("_M") else 0.
            assert math.isclose(got,exp,rel_tol=1e-12,abs_tol=1e-12)
        checks[k]={"parameter_count":len(co),"orientation_symmetry":True,"neutral_identical_traits_or_environment":True,"profile_column_isolation":True}
    R.update(status="FROZEN_MODEL_PREFLIGHT_PASS",checks=checks,training_support=m["training_support"],synthetic_test_only=True)
    save()
def predecessor():
    p=pathlib.Path("predecessor/report.json")
    d=json.loads(p.read_text())
    R["predecessor_report_sha256"]=w.sha(p)
    R["predecessor_status"]=d.get("status")
    s=d.get("forest_comparison_support") or {}
    R["predecessor_support"]={k:s.get(k) for k in ("eligible_taxa","comparison_taxa","comparison_routes","comparison_blocks","comparisons","comparison_cells")}
    R["predecessor_gedi_coverage"]=d.get("gedi_coverage")
    assert d.get("source_sha256")=="adc036ca0e0b8f822925db22151562b01321ab61fc7d9c611aca21257da9b490"
    assert d.get("source_measured_doi")=="10.3334/ORNLDAAC/2339"
    # A completed local fit is not required, but common environmental support is.
    admitted=d.get("status") in {"COMPLETE_DESCRIPTIVE_INDEPENDENT_MEASURED_PAVD_DIAGNOSTIC","STOP_INSUFFICIENT_DISJOINT_SCORED_SUPPORT"}
    import fws_coarse_profile_diagnostic_v1 as f
    if not admitted or not s or not f.passes(s):
        R["status"]="STOP_PREDECESSOR_COMMON_SUPPORT_NOT_ADMITTED";save()
        return None
    assert d["gedi_cell_table_sha256"] and d["gedi_coverage"]["candidate_cells"]==241
    R["status"]="PREDECESSOR_COMMON_SUPPORT_ADMITTED";save()
    return d
def external():
    preflight();d=predecessor()
    if d is None:return
    import fws_measured_pavd_independent_v1 as m
    original=w.external
    def checked(ct,z,gb,gr,names,u):
        # Check actual acquired measurements, covariate windows and frozen
        # comparison support against the completed predecessor, not its scores.
        # No change to selection or fitting if reproducibility fails.
        for k in ("gedi_cell_table_sha256","gedi_coverage","common_environment_cells","forest_comparison_support"):
            assert m.R.get(k)==d.get(k),"predecessor mismatch: "+k
        assert m.R.get("LC100",{}).get("sha256")==d.get("LC100",{}).get("sha256")
        assert m.R.get("raster_source_windows")==d.get("raster_source_windows"),"climate source windows differ"
        R["status"]="EXACT_SUPPORT_REPLAY_PASS";save()
        original(ct,z,gb,gr,names,u)
        R["status"]="EXTERNAL_SCORING_CALLBACK_COMPLETE";save()
    m.fit=checked
    m.main()
    if not (w.O/"external_report.json").exists():
        # Do not substitute a local fit, loosen admission, or report test scores.
        w.dump("external_report.json",m.R)
    R["external_status"]=json.loads((w.O/"external_report.json").read_text()).get("status")
    R["status"]="EXTERNAL_RUN_FINISHED";save()
if __name__=="__main__":
    try:
        if sys.argv[1]=="preflight":preflight()
        elif sys.argv[1]=="external":external()
        else:raise ValueError("mode")
    except Exception as e:
        R.update(status="INCOMPLETE",error_type=type(e).__name__);save()
        raise SystemExit(1)
