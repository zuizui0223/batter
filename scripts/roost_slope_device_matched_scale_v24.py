"""V24 exact device-lineage audit and same-window 60/120 s terrain diagnostic.
No raw positions, tag IDs, animal IDs, or inferred roost locations emitted.
"""
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_slope_matched_panels_v21 import PANELS,core,summary,compare,tadarida
from roost_slope_measurement_lineage_v23 import load,pairs,stats
from roost_slope_cadence_datum_v22 import anchors

BASE=["log_dt","hspeed","start_ground"]

def single(vals):
    vals={str(v).strip() for v in vals if str(v).strip() and str(v).strip().lower() not in ("na","nan","none")}
    return (next(iter(vals)),"matched") if len(vals)==1 else ("","missing" if not vals else "conflict")

def device_lineage(panel,d):
    c=json.loads((Path("contract")/PANELS[panel]).read_text())
    refs,_=core.read_csv(core.get(c["source"]["reference"],"batter-slope-v24/1.0"))
    grouped=defaultdict(list)
    for r in refs:
        a=str(r.get("animal_id","")).strip()
        t=str(r.get("tag_id","")).strip()
        if a and t:grouped[(a,t)].append(r)
    lookup={}
    for key,rs in grouped.items():
        model,ms=single([r.get("tag_model","") for r in rs])
        maker,ks=single([r.get("tag_manufacturer_name","") for r in rs])
        cycle,cs=single([r.get("duty_cycle","") for r in rs])
        lookup[key]=(model,maker,ms,ks,cs)
    x=d.copy()
    # No moving interval spanning a device change, even within an admitted session.
    ok=x.session.notna()&x.tag.ne("")
    x.loc[ok,"session"]=x.loc[ok,"session"].astype(str)+"::device::"+x.loc[ok,"tag"]
    x.loc[~ok,"session"]=None
    q=pairs(x);q=q[q.speed.between(2,50)].copy()
    keys=list(zip(q.animal,q.tag))
    joined=[lookup.get(k,("","","unmatched","unmatched","unmatched")) for k in keys]
    q[["model","maker","model_status","maker_status","cycle_status"]]=pd.DataFrame(joined,index=q.index)
    r={"reference_pairs":len(lookup),"moving_pairs_with_tag":len(q),
       "distinct_tag_animal_pairs":len(set(keys)),
       "tag_model_status":{str(k):int(v) for k,v in q.model_status.value_counts().items()},
       "tag_maker_status":{str(k):int(v) for k,v in q.maker_status.value_counts().items()},
       "duty_cycle_status":{str(k):int(v) for k,v in q.cycle_status.value_counts().items()},
       "model_groups":[],"cohort_device_crosswalk":[]}
    def report(g):
        return {"pairs":len(g),"tags":int(g.tag.nunique()),"animals":int(g.animal.nunique()),
            "median_abs_dh":float(g.dh.abs().median()) if len(g) else None,
            "median_abs_dg":float(g.dg.abs().median()) if len(g) else None,
            "median_speed":float(g.speed.median()) if len(g) else None,
            "integer_increment_fraction":float(np.mean(np.isclose(g.dh,np.round(g.dh),atol=1e-8,rtol=0))) if len(g) else None}
    def label(k,g):
        m,manufacturer,status=k
        if status!="matched":return status
        if g.tag.nunique()<2:return "suppressed_single_tag"
        # Suppress arbitrary long comments or unusual identifiers; publish only model categories.
        if len(m)>80 or len(manufacturer)>80:return "suppressed_label"
        return manufacturer+" / "+m if manufacturer else m
    for i,(k,g) in enumerate(q.groupby(["model","maker","model_status"],sort=True)):
        row={"category_index":i,"model":label(k,g),"all":report(g),
             "exact120":report(g[g.dt==120]),"150_200":report(g[g.dt.between(150,200)])}
        r["model_groups"].append(row)
        for ci,(_,gc) in enumerate(g.groupby("cohort",sort=True)):
            # Global cohort index from existing anonymized source field, not a site label.
            r["cohort_device_crosswalk"].append({"category_index":i,"cohort_index":str(gc.cohort.iloc[0]),
              "all":report(gc),"exact120":report(gc[gc.dt==120]),"150_200":report(gc[gc.dt.between(150,200)])})
    return r

def interval(a,b):
    dt=(b.time-a.time).total_seconds()
    if dt<=0:return None
    vals=np.array([a.lat,a.lon,b.lat,b.lon,a.height,b.height,a.ground,b.ground],float)
    if not np.isfinite(vals).all():return None
    la,lb=np.deg2rad([a.lat,b.lat]);dl=np.deg2rad(b.lon-a.lon)
    hav=np.sin((lb-la)/2)**2+np.cos(la)*np.cos(lb)*np.sin(dl/2)**2
    speed=float(2*6371008.8*np.arcsin(np.sqrt(np.clip(hav,0,1)))/dt)
    dh=float(b.height-a.height);dg=float(b.ground-a.ground)
    if not 2<=speed<=50 or abs(dh/dt)>15:return None
    return {"dt":dt,"log_dt":float(np.log(dt)),"hspeed":speed,"start_ground":float(a.ground),
            "y":dh/dt,"q":dg/dt,"dh":dh,"dg":dg}

def matched_windows(d):
    a,info=anchors(d,60,5)
    w=[];short=[];long=[]
    candidates=0
    if a.empty:return pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),info
    for (animal,session),g in a.groupby(["animal","session"],sort=True):
        g=g.sort_values("time").reset_index(drop=True)
        for i in range(0,len(g)-2,2):
            r0,r1,r2=[g.iloc[j] for j in (i,i+1,i+2)]
            candidates+=1
            s1=interval(r0,r1);s2=interval(r1,r2);l=interval(r0,r2)
            if s1 is None or s2 is None or l is None:continue
            if not (55<=s1["dt"]<=65 and 55<=s2["dt"]<=65 and 110<=l["dt"]<=130):continue
            assert np.isclose(l["dh"],s1["dh"]+s2["dh"],rtol=0,atol=1e-8)
            assert np.isclose(l["dg"],s1["dg"]+s2["dg"],rtol=0,atol=1e-8)
            k=len(w)
            w.append({"animal":str(animal),"window":k,"x1":s1["dg"],"x2":s2["dg"],"y1":s1["dh"],"y2":s2["dh"]})
            for z in [s1,s2]:short.append({**z,"animal":str(animal),"session":session,"window":k})
            long.append({**l,"animal":str(animal),"session":session,"window":k})
    info={**info,"candidate_windows":candidates,"valid_windows_before_animal_gate":len(w)}
    if not w:return pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),info
    W=pd.DataFrame(w);S=pd.DataFrame(short);L=pd.DataFrame(long)
    n=W.animal.value_counts();keep=set(n[n>=50].index)
    W=W[W.animal.isin(keep)].copy();S=S[S.animal.isin(keep)].copy();L=L[L.animal.isin(keep)].copy()
    assert len(S)==2*len(W)==2*len(L)
    assert set(S.window)==set(L.window)==set(W.window)
    return W,S,L,info

def association(d):
    if d.empty:return {"n":0}
    n=d[(d.dh!=0)&(d.dg!=0)]
    cs=[]
    for _,g in d.groupby("animal"):
        a=g.dh.rank();b=g.dg.rank()
        if len(a)>=3 and a.std()>0 and b.std()>0:
            z=a.corr(b)
            if np.isfinite(z):cs.append(float(z))
    return {"n":len(d),"animals":int(d.animal.nunique()),
            "median_animal_spearman":summary(cs),
            "nonzero_both":len(n),"same_sign_fraction":float(np.mean(np.sign(n.dh)==np.sign(n.dg))) if len(n) else None}

def decompose(W):
    # Center each substep position separately within animal. Average covariances
    # across animals equally; the aggregate covariance expands exactly.
    if W.empty:return {}
    terms=[]
    for _,g in W.groupby("animal"):
        x1,x2,y1,y2=[g[k].to_numpy(float)-g[k].mean() for k in ("x1","x2","y1","y2")]
        v=float(np.mean(x1*x1+x2*x2));vc=float(2*np.mean(x1*x2))
        c=float(np.mean(x1*y1+x2*y2));cc=float(np.mean(x1*y2+x2*y1))
        vl=float(np.mean((x1+x2)**2));cl=float(np.mean((x1+x2)*(y1+y2)))
        assert np.isclose(v+vc,vl) and np.isclose(c+cc,cl)
        terms.append([v,vc,c,cc,vl,cl])
    v,vc,c,cc,vl,cl=np.mean(terms,axis=0)
    return {"within_substep_variance":float(v),"cross_substep_variance":float(vc),
            "within_substep_covariance":float(c),"cross_substep_covariance":float(cc),
            "aggregate_variance":float(vl),"aggregate_covariance":float(cl),
            "raw_within_slope":float(c/v) if v>0 else None,
            "raw_aggregate_slope":float(cl/vl) if vl>0 else None,
            "note":"Position-specific within-animal centering; unadjusted slopes, not regression coefficients."}

def scale(d):
    W,S,L,a=matched_windows(d)
    r={"anchors":a,"windows":len(W),"animals":int(W.animal.nunique()) if len(W) else 0}
    if len(W)==0 or r["animals"]<6:return {**r,"status":"insufficient_matched_windows"}
    r["status"]="computed"
    r["windows_per_animal"]=summary(W.animal.value_counts())
    r["60"]={"association":association(S),"LOIO":compare(S,BASE)}
    r["120"]={"association":association(L),"LOIO":compare(L,BASE)}
    r["covariance_decomposition"]=decompose(W)
    b=r["60"]["LOIO"];c=r["120"]["LOIO"]
    if b.get("status")=="exploratory" and c.get("status")=="exploratory":
        v=b["q_coefficient"]["median"]
        r["coefficient_ratio_120_over_60"]=c["q_coefficient"]["median"]/v if v>0 else None
    return r

def main():
    r={"status":"measurement_and_matched_scale_diagnostic","panels":{},
       "claim_boundary":"Known panels only. Device/cadence/cohort confounding and GPS error not identified by aggregation; no species/year causal conclusion."}
    dest=OUT/"audit_v24_slope.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    for p in ["tadarida"]+list(PANELS):
        q={}
        try:
            if p=="tadarida":
                d,_=tadarida()
            else:
                d,_=load(p)
                try:q["device_lineage"]=device_lineage(p,d)
                except Exception as e:q["device_lineage"]={"status":"blocked","error_type":type(e).__name__}
            if p=="phyllostomus_2022":q["scale"]={"status":"excluded_preoutput_no_60s_anchor_chains"}
            else:
                d["alternate"]=np.nan
                q["scale"]=scale(d)
            q["status"]="computed"
        except Exception as e:q["status"]="blocked";q["error_type"]=type(e).__name__
        r["panels"][p]=q;save()
    print(dest.read_text())
    return 0 if any(v.get("status")=="computed" for v in r["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
