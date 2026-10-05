#!/usr/bin/env python3
"""Recover predeclared P2: policy distance versus dyad-specific excess co-use separation."""
from __future__ import annotations
import importlib.util, json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

P=loadmod("P",HERE/"policy_distance_couse_separation_receipt_v2.py")
CO=loadmod("CO",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py")

NPERM=9999
POLICY_SEEDS={"2022":202610052301,"2023":202610052302}
PANELS={"2022":"phyllostomus_2022","2023":"phyllostomus_2023"}

AUTHORITATIVE={
 "2022":{
   "panel_null_mean":7.729698412244561,
   "panel_observed":6.78230386000064,
   "panel_excess":-0.9473945522439209,
   "encounter_sha":"f5395250f476e22eab441bd9c2b52297277f282e71d66c0a4eebc531f612158a",
 },
 "2023":{
   "panel_null_mean":22.991942626060883,
   "panel_observed":26.56567049998826,
   "panel_excess":3.5737278739273783,
   "encounter_sha":"d4250eafeb7b602e47f7b9449bb76d4a71af0f0bfaa3bc3b801b260e69f2f6bb",
 },
}

def recover_dyad_null(panel,year):
    cfg=json.loads(CO.CFG.read_text(encoding="utf-8"))
    receipt=json.loads(CO.RECEIPT.read_text(encoding="utf-8"))

    # Verify frozen x-y-time encounter set before using z.
    xy=CO.shift.pre.load_xy_time(panel)
    _,encounters,_,_,esha,_=CO.reconstruct_primary(panel,xy,cfg,receipt)
    if esha!=AUTHORITATIVE[year]["encounter_sha"]:
        raise RuntimeError(f"{panel}: encounter SHA drift before z")

    records,contract=CO.load_panel_records(panel)
    CO.add_terrain_relative_z(panel,records,contract)
    rr,_,_,_,esha_z,_=CO.reconstruct_primary(panel,records,cfg,receipt)
    if esha_z!=esha:
        raise RuntimeError(f"{panel}: encounter SHA drift after z")

    lookup=CO.make_record_lookup(rr)
    gd,ga,pa,gb,pb,di,dyad_list=CO.build_phase_groups(rr,lookup,encounters)
    za=CO.observed_endpoint_values(gd,ga,pa)
    zb=CO.observed_endpoint_values(gd,gb,pb)
    obs_panel,obs_meds=CO.panel_stat(np.abs(za-zb),di,len(dyad_list))

    if not math.isclose(obs_panel,AUTHORITATIVE[year]["panel_observed"],rel_tol=0,abs_tol=1e-9):
        raise RuntimeError(f"{panel}: observed panel drift {obs_panel}")

    B=int(cfg["null"]["B"])
    seed=int(cfg["null"]["seeds"][panel])
    rng=np.random.default_rng(seed)
    dyad_sum=np.zeros(len(dyad_list),dtype=float)
    panel_sum=0.0

    for _ in range(B):
        shifts=CO.draw_group_shifts(gd,rng)
        za_p=CO.permuted_endpoint_values(gd,ga,pa,shifts)
        zb_p=CO.permuted_endpoint_values(gd,gb,pb,shifts)
        ps,meds=CO.panel_stat(np.abs(za_p-zb_p),di,len(dyad_list))
        panel_sum+=ps
        dyad_sum+=meds

    panel_null=panel_sum/B
    dyad_null=dyad_sum/B

    if not math.isclose(panel_null,AUTHORITATIVE[year]["panel_null_mean"],rel_tol=0,abs_tol=1e-10):
        raise RuntimeError(f"{panel}: panel null drift {panel_null}")
    panel_excess=obs_panel-panel_null
    if not math.isclose(panel_excess,AUTHORITATIVE[year]["panel_excess"],rel_tol=0,abs_tol=1e-10):
        raise RuntimeError(f"{panel}: panel excess drift {panel_excess}")

    rows=[]
    for k,d in enumerate(dyad_list):
        rows.append({
          "cohort":str(d[0]),"a":str(d[1]),"b":str(d[2]),
          "observed_median_m":float(obs_meds[k]),
          "null_mean_dyad_median_m":float(dyad_null[k]),
          "excess_m":float(obs_meds[k]-dyad_null[k]),
          "encounters":int(np.sum(di==k)),
        })
    return rows,esha,B,seed,panel_null

def attach_policy(rows,theta):
    out=[]
    for r in rows:
        ka=(r["cohort"],r["a"]);kb=(r["cohort"],r["b"])
        if ka not in theta or kb not in theta:continue
        dp=float(np.linalg.norm(theta[ka]-theta[kb]))
        out.append({**r,"D_policy":dp})
    return out

def run(year,panel):
    theta,audit=P.policy_centroids(panel)
    if theta is None:
        return {"status":"STOP_POLICY_SUPPORT","audit":audit}

    dyad_rows,esha,Bshift,shift_seed,panel_null=recover_dyad_null(panel,year)
    obs=attach_policy(dyad_rows,theta)
    if len(obs)<5:
        return {"status":"STOP_DYAD_POLICY_OVERLAP","n_policy_matched_dyads":len(obs)}

    rho=P.spearman([x["D_policy"] for x in obs],[x["excess_m"] for x in obs])
    if not math.isfinite(rho):
        return {"status":"STOP_PRIMARY_STATISTIC"}

    rng=np.random.default_rng(POLICY_SEEDS[year])
    null=[]
    for _ in range(NPERM):
        rr=attach_policy(dyad_rows,P.permute_theta(theta,rng))
        if len(rr)!=len(obs):
            raise RuntimeError("eligible dyad count changed under policy permutation")
        q=P.spearman([x["D_policy"] for x in rr],[x["excess_m"] for x in rr])
        if math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=rho))/(1+len(a))) if len(a) else None
    verdict=(
      "POSITIVE_POLICY_DISTANCE_EXCESS_SEPARATION"
      if rho>0 and p is not None and p<=.05 and len(a)>=9500
      else "NO_POSITIVE_POLICY_DISTANCE_EXCESS_SEPARATION"
    )
    return {
      "status":"DONE" if len(a)>=9500 else "STOP_RANDOMIZATION_SUPPORT",
      "panel":panel,
      "encounter_set_sha256":esha,
      "n_frozen_dyads":len(dyad_rows),
      "n_policy_matched_dyads":len(obs),
      "phase_shift_B":Bshift,
      "phase_shift_seed":shift_seed,
      "reconstructed_panel_null_mean_m":panel_null,
      "dyads":obs,
      "rho_policy_distance_vs_excess_separation":float(rho),
      "requested_policy_permutations":NPERM,
      "valid_policy_permutations":int(len(a)),
      "policy_seed":POLICY_SEEDS[year],
      "null_mean_rho":float(a.mean()) if len(a) else None,
      "null_q025_rho":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975_rho":float(np.quantile(a,.975)) if len(a) else None,
      "p_policy_one_sided":p,
      "diagnostic_verdict":verdict,
    }

def main():
    print(json.dumps({
      "contract":"POLICY_DISTANCE_COUSE_EXCESS_P2_FREEZE_V1.md",
      "status":"RECOVERED_PREDECLARED_P2",
      "years":{y:run(y,p) for y,p in PANELS.items()}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
