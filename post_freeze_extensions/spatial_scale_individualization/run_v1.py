#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader is not None
    spec.loader.exec_module(mod); return mod

base=load_module("collective_personal_v1",ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/run_v1.py")
CFG=ROOT/"post_freeze_extensions/spatial_scale_individualization/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/spatial_scale_individualization/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/spatial_scale_individualization/RESULT_V1.md"

def hdist(session,scale):
    ratio=int(scale//500)
    if ratio<1 or ratio*500!=scale:
        raise RuntimeError("scale must be integer multiple of 500 m")
    d=defaultdict(float)
    for (ix,iy),v in session["counts"].items():
        d[(int(ix)//ratio,int(iy)//ratio)]+=float(v.sum())
    tot=sum(d.values())
    return {k:v/tot for k,v in d.items()}

def equal_session_model(sessions,scale):
    ds=[hdist(s,scale) for s in sessions]
    cells=set().union(*(set(d) for d in ds))
    return {c:float(np.mean([d.get(c,0.0) for d in ds])) for c in cells}

def equal_individual_model(sessions,scale):
    by=defaultdict(list)
    for s in sessions: by[s["individual"]].append(s)
    ims=[equal_session_model(ss,scale) for ss in by.values()]
    cells=set().union(*(set(d) for d in ims))
    return {c:float(np.mean([d.get(c,0.0) for d in ims])) for c in cells}

def map500(cell,scale):
    ratio=int(scale//500)
    return (int(cell[0])//ratio,int(cell[1])//ratio)

def target_rows(sessions,c,panel):
    spec=c["history"]; lag=base.timedelta(days=float(spec["minimum_lag_days"]))
    rows=[]
    scales=[int(x) for x in c["horizontal_scales_m"]]
    for t in sessions:
        cutoff=t["mid_time"]-lag
        prior=[s for s in sessions if s["cohort"]==t["cohort"] and s["mid_time"]<=cutoff]
        sh=[s for s in prior if s["individual"]==t["individual"]]
        oh=[s for s in prior if s["individual"]!=t["individual"]]
        if not sh or len({s["individual"] for s in oh})<int(spec["minimum_other_individuals"]):
            continue

        selfz=base.avg_profiles_sessions(sh)
        groupz,_=base.avg_profiles_other(oh)
        fixed=set(selfz)&set(groupz)&set(t["counts"])
        scored=int(sum(int(t["counts"][cell].sum()) for cell in fixed))
        if scored<int(spec["minimum_scored_target_fixes"]): continue

        gains={}
        for scale in scales:
            sm=equal_session_model(sh,scale)
            gm=equal_individual_model(oh,scale)
            num=0.0
            for c500 in fixed:
                cc=map500(c500,scale)
                ps=float(sm.get(cc,0.0)); pg=float(gm.get(cc,0.0))
                if ps<=0 or pg<=0:
                    raise RuntimeError(f"{panel}: common 500m support did not imply positive coarse support")
                n=float(t["counts"][c500].sum())
                num+=n*(math.log(ps)-math.log(pg))
            gains[str(scale)]=num/scored

        rows.append({
            "cohort":t["cohort"],"session":t["session"],"individual":t["individual"],
            "scored_fixes":scored,"gains":gains,
            "scale_amplification_500_minus_10000":gains["500"]-gains["10000"]
        })

    exp=c["expected_structural_counts"][panel]
    nids=len({r["individual"] for r in rows})
    if len(rows)!=int(exp["target_sessions"]) or nids!=int(exp["target_individuals"]):
        raise RuntimeError(f"{panel}: structural drift sessions={len(rows)} individuals={nids}")
    return rows

def per_individual(rows,scales):
    out={}
    for iid in sorted({r["individual"] for r in rows}):
        rs=[r for r in rows if r["individual"]==iid]
        d={"target_sessions":len(rs)}
        for s in scales:
            d[str(s)]=float(np.mean([r["gains"][str(s)] for r in rs]))
        d["amplification"]=float(np.mean([r["scale_amplification_500_minus_10000"] for r in rs]))
        out[iid]=d
    return out

def boot(per,scales,seed,B):
    ids=sorted(per); n=len(ids); rng=np.random.default_rng(seed)
    keys=[str(s) for s in scales]+["amplification"]
    obs={k:float(np.mean([per[i][k] for i in ids])) for k in keys}
    vals={k:[] for k in keys}
    for _ in range(B):
        ss=rng.choice(ids,size=n,replace=True)
        for k in keys: vals[k].append(float(np.mean([per[i][k] for i in ss])))
    out={}
    for k in keys:
        a=np.asarray(vals[k])
        out[k]={"mean":obs[k],"ci95_low":float(np.quantile(a,.025)),"ci95_high":float(np.quantile(a,.975))}
    return out

def classify(b):
    coarse=b["10000"]; fine=b["500"]; amp=b["amplification"]
    if coarse["ci95_low"]>0: return "personal_already_coarse"
    if (coarse["mean"]<=0 or coarse["ci95_low"]<=0<=coarse["ci95_high"]) and fine["ci95_low"]>0 and amp["ci95_low"]>0:
        return "coarse_portable_fine_personal"
    if fine["ci95_high"]<=0: return "no_horizontal_personalization"
    return "mixed"

def main():
    c=json.loads(CFG.read_text())
    scales=[int(x) for x in c["horizontal_scales_m"]]
    res={}
    for p in c["panels"]:
        sessions,_=base.build_sessions(p,c={
            **json.loads((ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/contract_v1.json").read_text())
        })
        rows=target_rows(sessions,c,p)
        per=per_individual(rows,scales)
        b=boot(per,scales,int(c["uncertainty"]["seeds"][p]),int(c["uncertainty"]["bootstrap_B"]))
        res[p]={"target_sessions":len(rows),"target_individuals":len(per),"bootstrap":b,
                "classification":classify(b),"individual_results":per}

    payload={"schema_version":1,"study_id":c["study_id"],"panels":res,"claim_boundary":c["claim_boundary"]}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Spatial scale of individualization result v1","",
           "| panel | 10 km self gain [95% CI] | 500 m self gain [95% CI] | 500m-10km [95% CI] | class |",
           "|---|---:|---:|---:|---|"]
    for p,v in res.items():
        b=v["bootstrap"]; a=b["10000"]; f=b["500"]; q=b["amplification"]
        lines.append(f"| {p} | {a['mean']:+.4f} [{a['ci95_low']:+.4f},{a['ci95_high']:+.4f}] | {f['mean']:+.4f} [{f['ci95_low']:+.4f},{f['ci95_high']:+.4f}] | {q['mean']:+.4f} [{q['ci95_low']:+.4f},{q['ci95_high']:+.4f}] | {v['classification']} |")
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(json.dumps({p:{"classification":v["classification"],
                         "10km":v["bootstrap"]["10000"],
                         "5km":v["bootstrap"]["5000"],
                         "2.5km":v["bootstrap"]["2500"],
                         "1km":v["bootstrap"]["1000"],
                         "500m":v["bootstrap"]["500"],
                         "amplification":v["bootstrap"]["amplification"]} for p,v in res.items()},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
