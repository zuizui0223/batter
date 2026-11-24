"""Post-V5 diagnostic, not prospective confirmation: wing-value QC and taxonomic null.
Only aggregate community results; no cave identifiers or locations.
"""
import json,sys
from collections import Counter,defaultdict
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import get,OUT
from roost_fd_source_audit_v3 import quant
from roost_fd_source_audit_v4 import wing,name
from roost_fd_empirical_null_v5 import prepare, null_groups, build_dist, SEED, NREP, numeric

AXES=[("flight",["logar","logwl"],[]),("resource",["logmass","diet"],["diet"]),
      ("AR_only",["logar"],[]),("WL_only",["logwl"],[])]
FIELDS=["logar","logwl","logmass","diet"]

def qc(w,raw):
    x=w.copy()
    x["WL"]=numeric(x["wingLoading_Nm2"])
    x["WL_from_pooled_M_and_A"]=98.0665*numeric(x["mass_g"])/numeric(x["wingArea_cm2"])
    x["ratio"]=x.WL/x.WL_from_pooled_M_and_A
    rows=[]
    for _,a in x[x.WL<1].iterrows():
        s=a["scientificName.iucn"]
        q=raw[raw["scientificName.iucn"]==s]
        rows.append({"species":str(s),"pooled_WL":float(a.WL),
            "pooled_formula_WL":float(a.WL_from_pooled_M_and_A) if np.isfinite(a.WL_from_pooled_M_and_A) else None,
            "n_WL":float(a["n.WL"]) if pd.notna(a["n.WL"]) else None,
            "study_rows":len(q),"study_WL":quant(numeric(q["wingLoading_Nm2"])),
            "study_M":quant(numeric(q["mass_g"])),"study_A":quant(numeric(q["wingArea_cm2"]))})
    return {"WL_lt_0_5":int((x.WL<.5).sum()),"WL_lt_1":int((x.WL<1).sum()),
        "pooled_WL_formula_ratio":quant(x.ratio),"low_WL_diagnostic":rows,
        "note":"Pooled mass and wing area need not refer to identical observations; formula is a diagnostic, not a correction."}

def conditioned(pairs,trait,field):
    tr=trait.dropna(subset=FIELDS+[field]).sort_values("species").reset_index(drop=True)
    index=dict(zip(tr.species,np.arange(len(tr))))
    dists=np.asarray([build_dist(tr,f,cat) for _,f,cat in AXES])
    cats=tr[field].to_numpy()
    x=pairs.copy();x["idx"]=x.species.map(index)
    groups={};freq=defaultdict(Counter);nr=Counter()
    for k,g in x.groupby("site",sort=False):
        if g.realm.nunique()!=1:continue
        ids=np.sort(g.idx.dropna().astype(int).unique())
        realm=g.realm.iloc[0];country=g.country.iloc[0]
        groups[k]=(len(g),ids,realm,country)
        freq[realm].update(ids.tolist());nr[realm]+=1
    rng=np.random.default_rng(SEED); rows=[];eligible=0;blocked=0
    for k,(N,ids,realm,country) in groups.items():
        n=len(ids)
        if n<3 or n/N<.8:continue
        eligible+=1
        other=freq[realm].copy();other.subtract(ids.tolist())
        pool=np.array(sorted(i for i,v in other.items() if v>0),dtype=int)
        if len(pool)<max(15,2*n) or nr[realm]-1<10:blocked+=1;continue
        # Preserve each focal site's number of species per family or diet category.
        draws=[];alternatives=0
        for cat,kcat in sorted(Counter(cats[ids]).items()):
            pp=pool[cats[pool]==cat]
            if len(pp)<kcat:break
            alternatives+=len(pp)-kcat
            u=rng.random((NREP,len(pp)))
            draws.append(pp[np.argpartition(u,kcat-1,axis=1)[:,:kcat]])
        else:
            if alternatives<1:blocked+=1;continue
            draw=np.concatenate(draws,axis=1)
            i,j=np.triu_indices(n,1)
            obs=dists[:,ids[i],ids[j]].mean(axis=1)
            exp=dists[:,draw[:,i],draw[:,j]].mean(axis=2)
            delta=obs-exp.mean(axis=1);sd=exp.std(axis=1,ddof=1)
            ses=np.divide(delta,sd,out=np.full_like(delta,np.nan),where=sd>1e-12)
            for z,(ax,_,_) in enumerate(AXES):
                rows.append((ax,country,realm,delta[z],ses[z]))
            continue
        blocked+=1
    out={"reference_species":len(tr),"eligible_pre_null":eligible,"blocked":blocked,"axes":{}}
    for ax,_,_ in AXES:
        g=pd.DataFrame([r[1:] for r in rows if r[0]==ax],columns=["country","realm","delta","ses"])
        if g.empty:out["axes"][ax]={"sites":0};continue
        cm=g.groupby("country").delta.agg(["size","median"]);cm=cm[cm["size"]>=5]
        out["axes"][ax]={"sites":len(g),"countries":int(g.country.nunique()),"delta":quant(g.delta),"ses":quant(g.ses),
           "negative_fraction":float((g.delta<0).mean()),"zero_null_variance":int(g.ses.isna().sum()),
           "country_units_ge5":len(cm),"negative_country_medians":int((cm["median"]<0).sum())}
    return out

def compact(r):
    return {"trait_reference_species":r["trait_reference_species"],"eligible_sites_pre_null":r["eligible_sites_pre_null"],
        "axes":{a:{k:v for k,v in d.items() if k in {"sites","countries","regions","delta","ses","negative_fraction","countries_ge5","countries_ge5_negative_median","zero_null_variance"}} for a,d in r["axes"].items()}}

def main():
    o,_=get("occ");l,_=get("land");t,_=get("traits");data,wm=wing()
    w=data["wingReview_wm_data_speciesLevel.csv"];raw=data["wingReview_wm_data_final.csv"]
    result={"status":"posthoc_diagnostic_only","wing_qc":qc(w,raw),"runs":{}}
    for repair in (False,True):
        x,tr,audit=prepare(o,l,t,w,repair)
        family=pd.DataFrame({"species":w["scientificName.iucn"].map(name),"family":w["familyName"].astype(str).str.strip().str.lower()}).dropna(subset=["species"])
        family=family[~family.species.duplicated(keep=False)]
        tr=tr.merge(family,on="species",how="left",validate="one_to_one")
        runs={}
        # Same cave/species composition across axes within each scenario.
        for floor in (0.,.5,1.):
            q=tr.copy()
            q.loc[q.wl<floor,"logwl"]=np.nan
            runs["WL_floor_"+str(floor)]=compact(null_groups(x,q,AXES,"realm",.8))
        q=tr.copy()
        complete=q.dropna(subset=FIELDS)
        # Winsorize only quantitative traits at 5th and 95th percentiles, preserving species availability.
        for v in ("logar","logwl","logmass"):
            a,b=complete[v].quantile([.05,.95]);q[v]=q[v].clip(a,b)
        runs["winsor_5_95"]=compact(null_groups(x,q,AXES,"realm",.8))
        if repair:
            q=tr.copy();q.loc[q.wl<1,"logwl"]=np.nan
            runs["WL_floor_1_frequency_weighted"]=compact(null_groups(x,q,AXES,"realm",.8,weighted=True))
            runs["WL_floor_1_family_conditioned"]=conditioned(x,q,"family")
            runs["WL_floor_1_diet_conditioned"]=conditioned(x,q,"diet")
        result["runs"]["repair" if repair else "strict"]=runs
    (OUT/"audit_v6.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps(result,indent=2,allow_nan=False))
    return 0
if __name__=="__main__":sys.exit(main())
