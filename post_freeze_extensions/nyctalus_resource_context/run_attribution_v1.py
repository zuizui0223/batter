#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CONTRACT=ROOT/"post_freeze_extensions/nyctalus_resource_context/attribution_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/nyctalus_resource_context/attribution_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/nyctalus_resource_context/ATTRIBUTION_RESULT_V1.md"
UA={"User-Agent":"batter-nyctalus-resource-context-attribution-v1/1.0"}
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1
ALPHA=0.5

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def fetch_file(record_id,name):
    meta=requests.get(f"https://zenodo.org/api/records/{record_id}",headers=UA,timeout=90)
    meta.raise_for_status()
    rec=meta.json()
    target=None
    for f in rec.get("files",[]):
        if (f.get("key") or f.get("filename"))==name:
            target=f;break
    if target is None:
        raise RuntimeError(f"missing source file {name}")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=UA,timeout=240)
    r.raise_for_status()
    raw=r.content
    return raw,hashlib.sha256(raw).hexdigest()

def parse_bins(vals):
    return [math.inf if x=="inf" else float(x) for x in vals]

def bin_index(x,edges):
    for i in range(len(edges)-1):
        if edges[i] <= x < edges[i+1]:
            return i
    return len(edges)-2

def load_and_link(c):
    rid=int(c["source"]["record_id"])
    obs_raw,obs_sha=fetch_file(rid,c["source"]["observed_file"])
    rsf_raw,rsf_sha=fetch_file(rid,c["source"]["rsf_file"])
    if obs_sha!=c["source"]["observed_sha256"]:
        raise RuntimeError(f"observed SHA mismatch {obs_sha}")

    obs=pd.read_csv(io.BytesIO(obs_raw),dtype=str,low_memory=False)
    rsf=pd.read_csv(io.BytesIO(rsf_raw),dtype=str,low_memory=False)
    need_obs=["bat_id","trackid","x","y","Height","Year","field_period","move_state"]
    need_rsf=["response_rvso","trackid","x_","y_",
              c["fixed_context"]["roost_distance_field"],
              c["structural_preflight"]["landcover_field"]]
    missing=[x for x in need_obs if x not in obs.columns]+[x for x in need_rsf if x not in rsf.columns]
    if missing:
        raise RuntimeError(f"missing fields {missing}")

    mask=pd.Series(True,index=obs.index)
    for col in need_obs:
        mask &= present(obs[col])
    obs=obs.loc[mask,need_obs].copy()
    if len(obs)!=int(c["linkage"]["expected_rows"]):
        raise RuntimeError(f"observed rows {len(obs)} != frozen {c['linkage']['expected_rows']}")

    obs["x_num"]=pd.to_numeric(obs["x"],errors="coerce")
    obs["y_num"]=pd.to_numeric(obs["y"],errors="coerce")
    obs["height_num"]=pd.to_numeric(obs["Height"],errors="coerce")
    if obs[["x_num","y_num","height_num"]].isna().any().any():
        raise RuntimeError("observed numeric parse failure")
    if not np.isfinite(obs["height_num"].to_numpy(dtype=float)).all():
        raise RuntimeError("nonfinite Height")
    obs["bat_id"]=obs["bat_id"].astype(str)
    obs["trackid"]=obs["trackid"].astype(str)
    obs["move_state"]=obs["move_state"].astype(str).str.strip()
    obs["cohort"]=obs["Year"].astype(str).str.strip()+"::"+obs["field_period"].astype(str).str.strip()

    # Full-track centering before state/context filtering.
    obs["track_median"]=obs.groupby(["cohort","trackid"])["height_num"].transform("median")
    obs["resid_height"]=obs["height_num"]-obs["track_median"]

    used=rsf[rsf["response_rvso"].astype(str)=="1"].copy()
    if len(used)!=len(obs):
        raise RuntimeError(f"RSF used rows {len(used)} != observed {len(obs)}")

    max_allowed=float(c["linkage"]["maximum_distance_m"])
    linked=[]
    tracks=sorted(obs["trackid"].unique())
    if len(tracks)!=int(c["linkage"]["expected_tracks"]):
        raise RuntimeError(f"track count {len(tracks)} != frozen {c['linkage']['expected_tracks']}")

    for tid in tracks:
        og=obs[obs["trackid"]==tid].reset_index(drop=True)
        ug=used[used["trackid"].astype(str)==tid].reset_index(drop=True)
        if len(og)!=len(ug):
            raise RuntimeError(f"track {tid}: row count mismatch")
        ox=og["x_num"].to_numpy(dtype=float); oy=og["y_num"].to_numpy(dtype=float)
        ux=pd.to_numeric(ug["x_"],errors="coerce").to_numpy(dtype=float)
        uy=pd.to_numeric(ug["y_"],errors="coerce").to_numpy(dtype=float)
        if not (np.isfinite(ux).all() and np.isfinite(uy).all()):
            raise RuntimeError(f"track {tid}: RSF coordinate parse failure")
        D=np.hypot(ox[:,None]-ux[None,:],oy[:,None]-uy[None,:])
        ix=np.argmin(D,axis=1)
        mins=D[np.arange(len(og)),ix]
        if len(set(int(x) for x in ix))!=len(og):
            raise RuntimeError(f"track {tid}: non-bijective linkage")
        if float(mins.max())>max_allowed:
            raise RuntimeError(f"track {tid}: max linkage distance {float(mins.max())} > {max_allowed}")
        for i,j in enumerate(ix):
            o=og.iloc[i]; u=ug.iloc[int(j)]
            linked.append({
                "bat_id":str(o["bat_id"]),
                "trackid":str(o["trackid"]),
                "cohort":str(o["cohort"]),
                "move_state":str(o["move_state"]),
                "x":float(o["x_num"]),
                "y":float(o["y_num"]),
                "resid_height":float(o["resid_height"]),
                "roost_km":u[c["fixed_context"]["roost_distance_field"]],
                "landcover":str(u[c["structural_preflight"]["landcover_field"]]).strip(),
                "link_distance_m":float(mins[i])
            })
    d=pd.DataFrame(linked)
    if len(d)!=len(obs):
        raise RuntimeError("linked row count mismatch")
    d["roost_km"]=pd.to_numeric(d["roost_km"],errors="coerce")
    if d["roost_km"].isna().any() or (d["roost_km"]<0).any():
        raise RuntimeError("invalid roost distance")
    if (d["landcover"]=="").any():
        raise RuntimeError("missing landcover")
    return d,obs_sha,rsf_sha

def prepare(c):
    d,obs_sha,rsf_sha=load_and_link(c)
    q=d[d["move_state"].isin(c["fixed_context"]["valid_source_states"])].copy()
    grid=int(c["fixed_context"]["horizontal_grid_m"])
    q["cx"]=np.floor(q["x"]/grid).astype(int)
    q["cy"]=np.floor(q["y"]/grid).astype(int)
    rbins=parse_bins(c["structural_preflight"]["roost_distance_bins_km"])
    q["rbin"]=[bin_index(float(x),rbins) for x in q["roost_km"]]
    q["zbin"]=[z_bin(float(x),edges=EDGES) for x in q["resid_height"]]

    cohorts=defaultdict(dict)
    for (cohort,sid),g in q.groupby(["cohort","trackid"],sort=True):
        if g["bat_id"].nunique()!=1:
            raise RuntimeError(f"track {sid} maps to multiple bats")
        iid=str(g["bat_id"].iloc[0])
        base_counts={}
        context_counts={}
        context_to_base={}
        for r in g.itertuples(index=False):
            base=(int(r.cx),int(r.cy),str(r.move_state))
            ctx=base+(int(r.rbin),str(r.landcover))
            if base not in base_counts:
                base_counts[base]=np.zeros(K,dtype=float)
            if ctx not in context_counts:
                context_counts[ctx]=np.zeros(K,dtype=float)
            base_counts[base][int(r.zbin)]+=1
            context_counts[ctx][int(r.zbin)]+=1
            context_to_base[ctx]=base
        cohorts[str(cohort)][str(sid)]={
            "session":str(sid),
            "original_label":iid,
            "base_counts":base_counts,
            "context_counts":context_counts,
            "context_to_base":context_to_base
        }
    return dict(cohorts),{
        "observed_sha256":obs_sha,
        "rsf_sha256":rsf_sha,
        "linked_rows":int(len(d)),
        "link_distance_median":float(d["link_distance_m"].median()),
        "link_distance_max":float(d["link_distance_m"].max()),
        "arm_com_rows":int(len(q)),
        "tracks":int(sum(len(x) for x in cohorts.values()))
    }

def smooth(cnt):
    x=np.asarray(cnt,dtype=float)+ALPHA
    return x/x.sum()

def self_profile(sessions,sids,key):
    per=defaultdict(list)
    for sid in sids:
        for s,cnt in sessions[sid][key].items():
            per[s].append(smooth(cnt))
    return {s:np.mean(np.stack(v),axis=0) for s,v in per.items()}

def other_profile(sessions,sids,labels,key):
    grouped={}
    for sid in sids:
        lab=labels[sid]
        for s,cnt in sessions[sid][key].items():
            k=(lab,s)
            if k not in grouped:
                grouped[k]=np.zeros(K,dtype=float)
            grouped[k]+=cnt
    per=defaultdict(list)
    for (lab,s),cnt in grouped.items():
        per[s].append(smooth(cnt))
    return {s:np.mean(np.stack(v),axis=0) for s,v in per.items()}

def self_weights(sessions,sids,supported,key):
    supported=list(supported)
    ws=[]
    for sid in sids:
        vals=np.array([float(sessions[sid][key].get(s,np.zeros(K)).sum()) for s in supported],dtype=float)
        tot=vals.sum()
        if tot>0:
            ws.append(vals/tot)
    if not ws:
        return None
    w=np.mean(np.stack(ws),axis=0)
    return w/w.sum()

def score(cohorts,labels_by_cohort,min_scored):
    rows=[]
    for cohort,sessions in sorted(cohorts.items()):
        labels=labels_by_cohort[cohort]
        ids=sorted(sessions)
        for sid in ids:
            lab=labels[sid]
            self_sids=[x for x in ids if x!=sid and labels[x]==lab]
            other_sids=[x for x in ids if labels[x]!=lab]
            if not self_sids or not other_sids:
                continue
            ps_ctx=self_profile(sessions,self_sids,"context_counts")
            po_ctx=other_profile(sessions,other_sids,labels,"context_counts")
            ps_base=self_profile(sessions,self_sids,"base_counts")
            po_base=other_profile(sessions,other_sids,labels,"base_counts")
            target=sessions[sid]
            supported_ctx=[
                c for c in target["context_counts"]
                if c in ps_ctx and c in po_ctx
                and target["context_to_base"][c] in ps_base
                and target["context_to_base"][c] in po_base
            ]
            scored=int(sum(target["context_counts"][c].sum() for c in supported_ctx))
            if scored<min_scored:
                continue
            supported_base=sorted({target["context_to_base"][c] for c in supported_ctx})
            w_ctx=self_weights(sessions,self_sids,supported_ctx,"context_counts")
            w_base=self_weights(sessions,self_sids,supported_base,"base_counts")
            if w_ctx is None or w_base is None:
                continue
            psc=np.stack([ps_ctx[c] for c in supported_ctx]); poc=np.stack([po_ctx[c] for c in supported_ctx])
            psb=np.stack([ps_base[b] for b in supported_base]); pob=np.stack([po_base[b] for b in supported_base])
            m_self_ctx=np.sum(psc*w_ctx[:,None],axis=0); m_other_ctx=np.sum(poc*w_ctx[:,None],axis=0)
            m_self_base=np.sum(psb*w_base[:,None],axis=0); m_other_base=np.sum(pob*w_base[:,None],axis=0)
            target_z=np.zeros(K,dtype=float)
            for c in supported_ctx:
                target_z+=target["context_counts"][c]
            g_ctx=float(np.sum(target_z*(np.log(m_self_ctx)-np.log(m_other_ctx)))/scored)
            g_base=float(np.sum(target_z*(np.log(m_self_base)-np.log(m_other_base)))/scored)
            rows.append({
                "cohort":cohort,"session":sid,"label":lab,"scored_events":scored,
                "context_gain":g_ctx,"base_gain":g_base,"context_increment":g_ctx-g_base
            })

    per={}
    for lab in sorted({r["label"] for r in rows}):
        rs=[r for r in rows if r["label"]==lab]
        per[lab]={
            "evaluable_sessions":len(rs),
            "context_gain":float(np.mean([r["context_gain"] for r in rs])),
            "base_gain":float(np.mean([r["base_gain"] for r in rs])),
            "context_increment":float(np.mean([r["context_increment"] for r in rs]))
        }
    vals=list(per.values())
    return {
        "eligible_individuals":len(vals),
        "context_gain":float(np.mean([v["context_gain"] for v in vals])) if vals else None,
        "base_gain":float(np.mean([v["base_gain"] for v in vals])) if vals else None,
        "context_increment":float(np.mean([v["context_increment"] for v in vals])) if vals else None,
        "individual_results":per,
        "session_results":rows
    }

def observed_labels(cohorts):
    return {cohort:{sid:r["original_label"] for sid,r in sessions.items()} for cohort,sessions in cohorts.items()}

def perm_labels(cohorts,rng):
    out={}
    for cohort,sessions in sorted(cohorts.items()):
        ids=sorted(sessions)
        labs=np.asarray([sessions[sid]["original_label"] for sid in ids],dtype=object)
        pp=rng.permutation(labs)
        out[cohort]={sid:str(pp[i]) for i,sid in enumerate(ids)}
    return out

def main():
    c=json.loads(CONTRACT.read_text())
    cohorts,diag=prepare(c)
    min_scored=int(c["fixed_context"]["minimum_scored_target_events"])
    obs=score(cohorts,observed_labels(cohorts),min_scored)
    expected=int(c["structural_preflight"]["expected_evaluable_individuals"])
    if obs["eligible_individuals"]!=expected:
        raise RuntimeError(f"observed n {obs['eligible_individuals']} != frozen {expected}")

    B=int(c["calibration"]["B"]);seed=int(c["calibration"]["seed"])
    rng=np.random.default_rng(seed)
    null_inc=[];null_ctx=[];null_base=[];invalid=0
    for _ in range(B):
        p=score(cohorts,perm_labels(cohorts,rng),min_scored)
        if p["eligible_individuals"]<1:
            invalid+=1;continue
        null_inc.append(float(p["context_increment"]))
        null_ctx.append(float(p["context_gain"]))
        null_base.append(float(p["base_gain"]))
    inc=cal.tail_summary(null_inc,float(obs["context_increment"]))
    ctx=cal.tail_summary(null_ctx,float(obs["context_gain"]))
    base=cal.tail_summary(null_base,float(obs["base_gain"]))
    supported=inc["observed_minus_null_mean"]<0 and inc["p_null_le_observed"]<=0.05

    payload={
        "schema_version":1,"study_id":c["study_id"],
        "diagnostics":diag,"observed":obs,
        "permutation":{
            "B":B,"seed":seed,"invalid_replicates":invalid,
            "context_increment":inc,"context_gain":ctx,"base_gain":base
        },
        "primary_supported":bool(supported),
        "interpretation_key":"attenuation_PASS" if supported else "attenuation_FAIL",
        "interpretation":c["interpretation_matrix"]["attenuation_PASS" if supported else "attenuation_FAIL"],
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Nyctalus support-matched source-RSF resource-context attribution v1","",
        "**POST-OUTCOME MECHANISM LOCALIZATION; FINAL SAME-SOURCE NYCTALUS MECHANISM FAMILY.**","",
        f"- n: **{obs['eligible_individuals']}**",
        f"- support-matched HMM-state base gain: **{obs['base_gain']:+.5f}**",
        f"- + roost-distance × land-cover context gain: **{obs['context_gain']:+.5f}**",
        f"- paired context increment: **{obs['context_increment']:+.5f}**",
        f"- null-centered paired increment: **{inc['observed_minus_null_mean']:+.5f}**",
        f"- one-sided p(null <= observed): **{inc['p_null_le_observed']:.4f}**",
        f"- attribution verdict: **{'PASS' if supported else 'FAIL'}**","",
        "Support-matched calibration:",
        f"- HMM-state base calibrated excess: **{base['observed_minus_null_mean']:+.5f}**, p_upper={base['p_null_ge_observed']:.4f}",
        f"- resource-context calibrated excess: **{ctx['observed_minus_null_mean']:+.5f}**, p_upper={ctx['p_null_ge_observed']:.4f}","",
        c["interpretation_matrix"]["attenuation_PASS" if supported else "attenuation_FAIL"],""
    ]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "n":obs["eligible_individuals"],
        "base_gain":obs["base_gain"],
        "context_gain":obs["context_gain"],
        "context_increment":obs["context_increment"],
        "calibrated_context_increment":inc["observed_minus_null_mean"],
        "p_lower":inc["p_null_le_observed"],
        "base_calibrated_excess":base["observed_minus_null_mean"],
        "base_p_upper":base["p_null_ge_observed"],
        "context_calibrated_excess":ctx["observed_minus_null_mean"],
        "context_p_upper":ctx["p_null_ge_observed"],
        "supported":supported
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
