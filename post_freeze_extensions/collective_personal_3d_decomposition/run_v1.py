#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_tag_altitude_bias_shape as shape

CFG=ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/RESULT_V1.md"

EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1

def cfg():
    return json.loads(CFG.read_text(encoding="utf-8"))

def median_time(vals):
    xs=sorted(vals); n=len(xs)
    if n%2: return xs[n//2]
    return xs[n//2-1]+(xs[n//2]-xs[n//2-1])/2

def build_sessions(panel,c):
    rec,source=shape.panel_raw(panel)
    grid=float(c["common_geometry"]["horizontal_grid_m"])
    alpha=float(c["common_geometry"]["jeffreys_alpha"])
    minfix=int(c["common_geometry"]["minimum_session_fixes"])
    by=defaultdict(list)
    for r in rec:
        by[(r["cohort"],r["session"],r["iid"])].append(r)
    out=[]
    for (cohort,sid,iid),vals in sorted(by.items()):
        if len(vals)<minfix: continue
        med=float(np.median([r["h"] for r in vals]))
        counts=defaultdict(lambda:np.zeros(K,dtype=np.int64))
        for r in vals:
            cell=(math.floor(r["x"]/grid),math.floor(r["y"]/grid))
            z=shape.z_bin(float(r["h"]-med),edges=EDGES)
            counts[cell][z]+=1
        total=int(sum(int(v.sum()) for v in counts.values()))
        if total<minfix: continue
        pxy={cell:float(v.sum())/total for cell,v in counts.items()}
        pz={cell:(v.astype(float)+alpha)/(float(v.sum())+alpha*K) for cell,v in counts.items()}
        marg_counts=np.sum(np.stack(list(counts.values())),axis=0)
        marg=(marg_counts.astype(float)+alpha)/(float(marg_counts.sum())+alpha*K)
        mt=median_time([r["t"] for r in vals])
        out.append({
            "cohort":cohort,"session":sid,"individual":iid,"mid_time":mt,
            "night":(mt-timedelta(hours=12)).date().isoformat(),
            "counts":dict(counts),"pxy":pxy,"pz":pz,"marginal":marg,"n":total
        })
    return out,source

def avg_profiles_sessions(sessions):
    cells=sorted(set().union(*(set(s["pz"]) for s in sessions))) if sessions else []
    out={}
    for cell in cells:
        xs=[s["pz"][cell] for s in sessions if cell in s["pz"]]
        if xs: out[cell]=np.mean(np.stack(xs),axis=0)
    return out

def avg_profiles_other(sessions):
    by=defaultdict(list)
    for s in sessions: by[s["individual"]].append(s)
    per={iid:avg_profiles_sessions(ss) for iid,ss in by.items()}
    cells=sorted(set().union(*(set(x) for x in per.values()))) if per else []
    out={}
    for cell in cells:
        xs=[m[cell] for m in per.values() if cell in m]
        if xs: out[cell]=np.mean(np.stack(xs),axis=0)
    return out,per

def avg_other_marginal(sessions):
    by=defaultdict(list)
    for s in sessions: by[s["individual"]].append(s)
    xs=[]
    for ss in by.values():
        xs.append(np.mean(np.stack([s["marginal"] for s in ss]),axis=0))
    return np.mean(np.stack(xs),axis=0) if xs else None

def group_night_distribution(sessions,pz_override=None):
    by_iid=defaultdict(list)
    for s in sessions: by_iid[s["individual"]].append(s)
    ids=sorted(by_iid)
    ind_pxy={}
    ind_pz={}
    for iid,ss in by_iid.items():
        cells=sorted(set().union(*(set(s["pxy"]) for s in ss)))
        px={}
        for cell in cells:
            px[cell]=float(np.mean([s["pxy"].get(cell,0.0) for s in ss]))
        ps={}
        for cell in cells:
            vals=[]
            for s in ss:
                if cell in s["pz"]:
                    if pz_override is None:
                        vals.append(s["pz"][cell])
                    else:
                        vals.append(pz_override[s["session"]][cell])
            if vals: ps[cell]=np.mean(np.stack(vals),axis=0)
        ind_pxy[iid]=px; ind_pz[iid]=ps
    allcells=sorted(set().union(*(set(x) for x in ind_pxy.values())))
    gpx={cell:float(np.mean([ind_pxy[i].get(cell,0.0) for i in ids])) for cell in allcells}
    gpz={}
    for cell in allcells:
        xs=[ind_pz[i][cell] for i in ids if cell in ind_pz[i]]
        if xs: gpz[cell]=np.mean(np.stack(xs),axis=0)
    return {"pxy":gpx,"pz":gpz}

def ozxy(a,b):
    common=sorted(set(a["pz"])&set(b["pz"])&set(a["pxy"])&set(b["pxy"]))
    if not common: return None
    w=np.asarray([min(a["pxy"][c],b["pxy"][c]) for c in common],dtype=float)
    if float(w.sum())<=0: return None
    w=w/w.sum()
    vals=[float(np.minimum(a["pz"][c],b["pz"][c]).sum()) for c in common]
    return float(np.dot(w,np.asarray(vals)))

def reconstruct_laneA(panel,sessions,c):
    spec=c["lane_A_natural_turnover"]
    lag=timedelta(days=float(c["common_geometry"]["minimum_history_lag_days"]))
    minind=int(spec["night_min_individuals"])
    mincommon=int(spec["pair_common_horizontal_support_min_fixes_each"])
    by=defaultdict(list)
    for s in sessions: by[(s["cohort"],s["night"])].append(s)
    nights=[]
    for (cohort,night),ss in sorted(by.items()):
        ids=sorted({s["individual"] for s in ss})
        if len(ids)<minind: continue
        mt=median_time([s["mid_time"] for s in ss])
        cellcounts=Counter()
        for s in ss:
            for cell,v in s["counts"].items(): cellcounts[cell]+=int(v.sum())
        nights.append({"cohort":cohort,"night":night,"sessions":ss,"ids":ids,"mid_time":mt,"cellcounts":cellcounts})
    pairs=[]
    for cohort in sorted({n["cohort"] for n in nights}):
        ns=sorted([n for n in nights if n["cohort"]==cohort],key=lambda x:x["mid_time"])
        for i,a in enumerate(ns):
            for b in ns[i+1:]:
                if b["mid_time"]-a["mid_time"]<lag: continue
                if set(a["ids"])&set(b["ids"]): continue
                common=set(a["cellcounts"])&set(b["cellcounts"])
                fa=sum(a["cellcounts"][x] for x in common); fb=sum(b["cellcounts"][x] for x in common)
                if fa<mincommon or fb<mincommon: continue
                pairs.append((a,b))
    exp=spec["expected_structural_counts"][panel]
    unique={(n["cohort"],n["night"]) for ab in pairs for n in ab}
    if len(pairs)!=int(exp["eligible_pairs"]) or len(unique)!=int(exp["unique_nights"]):
        raise RuntimeError(f"{panel}: lane A structural drift pairs={len(pairs)} nights={len(unique)}")
    return nights,pairs

def permuted_profile_maps(sessions,rng):
    out={}
    for s in sessions:
        cells=sorted(s["pz"])
        vals=[s["pz"][c] for c in cells]
        order=rng.permutation(len(vals))
        out[s["session"]]={cell:vals[int(order[j])] for j,cell in enumerate(cells)}
    return out

def run_laneA(panel,sessions,c):
    nights,pairs=reconstruct_laneA(panel,sessions,c)
    nd={(n["cohort"],n["night"]):n for n in nights}
    gobs={k:group_night_distribution(n["sessions"]) for k,n in nd.items()}
    obsvals=[]
    for a,b in pairs:
        v=ozxy(gobs[(a["cohort"],a["night"])],gobs[(b["cohort"],b["night"])])
        if v is None: raise RuntimeError("lane A observed overlap missing")
        obsvals.append(v)
    observed=float(np.mean(obsvals))
    rng=np.random.default_rng(int(c["lane_A_natural_turnover"]["seeds"][panel]))
    B=int(c["lane_A_natural_turnover"]["B"])
    null=[]
    relevant_sessions={s["session"]:s for n in nights for s in n["sessions"]}
    rel=list(relevant_sessions.values())
    for _ in range(B):
        po=permuted_profile_maps(rel,rng)
        gp={k:group_night_distribution(n["sessions"],po) for k,n in nd.items()}
        vals=[ozxy(gp[(a["cohort"],a["night"])],gp[(b["cohort"],b["night"])]) for a,b in pairs]
        null.append(float(np.mean(vals)))
    arr=np.asarray(null)
    p=float((1+np.sum(arr>=observed-1e-15))/(B+1))
    excess=float(observed-arr.mean())
    return {
        "eligible_pairs":len(pairs),"unique_nights":len({(n["cohort"],n["night"]) for ab in pairs for n in ab}),
        "observed_mean_ozxy":observed,
        "pair_ozxy_mean":observed,
        "pair_ozxy_q025":float(np.quantile(obsvals,0.025)),
        "pair_ozxy_q975":float(np.quantile(obsvals,0.975)),
        "null_mean":float(arr.mean()),"null_q05":float(np.quantile(arr,0.05)),
        "null_q95":float(np.quantile(arr,0.95)),"observed_minus_null_mean":excess,
        "p_null_ge_observed":p,
        "supported":bool(excess>0 and p<=0.05)
    }

def target_rows_laneB(sessions,c,panel):
    spec=c["lane_B_cross_individual_prediction"]
    lag=timedelta(days=float(c["common_geometry"]["minimum_history_lag_days"]))
    min_other=int(spec["minimum_other_history_individuals"])
    minscore=int(spec["minimum_scored_target_fixes"])
    rows=[]
    for t in sessions:
        cutoff=t["mid_time"]-lag
        prior=[s for s in sessions if s["cohort"]==t["cohort"] and s["mid_time"]<=cutoff]
        sh=[s for s in prior if s["individual"]==t["individual"]]
        oh=[s for s in prior if s["individual"]!=t["individual"]]
        oids=sorted({s["individual"] for s in oh})
        if not sh or len(oids)<min_other: continue
        selfm=avg_profiles_sessions(sh)
        groupm,_=avg_profiles_other(oh)
        marg=avg_other_marginal(oh)
        common=set(selfm)&set(groupm)&set(t["counts"])
        scored=int(sum(int(t["counts"][cell].sum()) for cell in common))
        if scored<minscore: continue
        gnum=pnum=tnum=0.0
        for cell in common:
            cnt=t["counts"][cell].astype(float)
            g=groupm[cell]; s=selfm[cell]
            gnum+=float(np.sum(cnt*(np.log(g)-np.log(marg))))
            pnum+=float(np.sum(cnt*(np.log(s)-np.log(g))))
            tnum+=float(np.sum(cnt*(np.log(s)-np.log(marg))))
        gg=gnum/scored; pp=pnum/scored; tt=tnum/scored
        if abs((gg+pp)-tt)>1e-10: raise RuntimeError("additive score identity failed")
        rows.append({
            "cohort":t["cohort"],"session":t["session"],"individual":t["individual"],
            "scored_fixes":scored,"prior_self_sessions":len(sh),"prior_other_individuals":len(oids),
            "shared_group_gain":gg,"personal_increment":pp,"total_personal_history_gain":tt
        })
    exp=spec["expected_structural_counts"][panel]
    nids=len({r["individual"] for r in rows})
    if len(rows)!=int(exp["target_sessions"]) or nids!=int(exp["target_individuals"]):
        raise RuntimeError(f"{panel}: lane B structural drift sessions={len(rows)} individuals={nids}")
    return rows

def aggregate_by_individual(rows):
    out={}
    for iid in sorted({r["individual"] for r in rows}):
        rs=[r for r in rows if r["individual"]==iid]
        out[iid]={
            "target_sessions":len(rs),
            "shared_group_gain":float(np.mean([r["shared_group_gain"] for r in rs])),
            "personal_increment":float(np.mean([r["personal_increment"] for r in rs])),
            "total_personal_history_gain":float(np.mean([r["total_personal_history_gain"] for r in rs]))
        }
    return out

def bootstrap_summary(per,seed,B):
    ids=sorted(per); n=len(ids); rng=np.random.default_rng(seed)
    keys=["shared_group_gain","personal_increment","total_personal_history_gain"]
    obs={k:float(np.mean([per[i][k] for i in ids])) for k in keys}
    boots={k:[] for k in keys}
    for _ in range(B):
        samp=rng.choice(ids,size=n,replace=True)
        for k in keys: boots[k].append(float(np.mean([per[i][k] for i in samp])))
    out={}
    for k in keys:
        a=np.asarray(boots[k])
        out[k]={
            "mean":obs[k],"ci95_low":float(np.quantile(a,0.025)),"ci95_high":float(np.quantile(a,0.975)),
            "positive_individuals":int(sum(per[i][k]>0 for i in ids)),"individuals":n,
            "supported":bool(obs[k]>0 and np.quantile(a,0.025)>0)
        }
    return out

def run_laneB(panel,sessions,c):
    rows=target_rows_laneB(sessions,c,panel)
    per=aggregate_by_individual(rows)
    spec=c["lane_B_cross_individual_prediction"]
    boot=bootstrap_summary(per,int(spec["bootstrap_seeds"][panel]),int(spec["bootstrap_B"]))
    shared=boot["shared_group_gain"]["supported"]; personal=boot["personal_increment"]["supported"]
    if shared and personal: cat="shared_plus_personal"
    elif shared: cat="shared_only"
    elif personal: cat="personal_only"
    else: cat="neither"
    return {
        "target_sessions":len(rows),"target_individuals":len(per),
        "bootstrap":boot,"classification":cat,
        "individual_results":per,"target_results":rows
    }

def make_md(payload):
    lines=["# Collective-versus-personal 3D decomposition result v1","",
           "## Lane A — natural tracked-member turnover","",
           "| panel | pairs | observed O_Z|XY | null mean | excess | p | support |",
           "|---|---:|---:|---:|---:|---:|---|"]
    for p,v in payload["lane_A"].items():
        lines.append(f"| {p} | {v['eligible_pairs']} | {v['observed_mean_ozxy']:.3f} | {v['null_mean']:.3f} | {v['observed_minus_null_mean']:+.3f} | {v['p_null_ge_observed']:.4f} | {'PASS' if v['supported'] else 'FAIL'} |")
    lines += ["","## Lane B — strictly past cross-individual prediction","",
              "| panel | n individuals | shared group gain | 95% CI | personal increment | 95% CI | class |",
              "|---|---:|---:|---|---:|---|---|"]
    for p,v in payload["lane_B"].items():
        g=v["bootstrap"]["shared_group_gain"]; q=v["bootstrap"]["personal_increment"]
        lines.append(f"| {p} | {v['target_individuals']} | {g['mean']:+.4f} | [{g['ci95_low']:+.4f}, {g['ci95_high']:+.4f}] | {q['mean']:+.4f} | [{q['ci95_low']:+.4f}, {q['ci95_high']:+.4f}] | {v['classification']} |")
    lines += ["","## Interpretation boundary","",
              "Lane A tests collective spatial persistence after complete tracked-member turnover. Lane B separates cross-individual shared predictive information from focal-individual history. Neither result alone identifies social or cognitive memory.",""]
    return "\n".join(lines)

def main():
    c=cfg()
    needed=sorted(set(c["lane_A_natural_turnover"]["included_panels"])|set(c["lane_B_cross_individual_prediction"]["included_panels"]))
    data={}
    sources={}
    for p in needed:
        data[p],sources[p]=build_sessions(p,c)
    A={p:run_laneA(p,data[p],c) for p in c["lane_A_natural_turnover"]["included_panels"]}
    B={p:run_laneB(p,data[p],c) for p in c["lane_B_cross_individual_prediction"]["included_panels"]}
    payload={
        "schema_version":1,"study_id":c["study_id"],"sources":sources,
        "lane_A":A,"lane_B":B,"claim_boundary":c["claim_boundary"],
        "headline":{
            "lane_A_supported_panels":[p for p,v in A.items() if v["supported"]],
            "lane_B_classification":{p:v["classification"] for p,v in B.items()}
        }
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    OUT_MD.write_text(make_md(payload),encoding="utf-8")
    print(json.dumps({
        "lane_A":{p:{"excess":v["observed_minus_null_mean"],"p":v["p_null_ge_observed"],"supported":v["supported"]} for p,v in A.items()},
        "lane_B":{p:{"classification":v["classification"],"shared":v["bootstrap"]["shared_group_gain"],"personal":v["bootstrap"]["personal_increment"],"total":v["bootstrap"]["total_personal_history_gain"]} for p,v in B.items()}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
