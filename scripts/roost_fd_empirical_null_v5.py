"""V5: conservative common-site FD and leave-focal-cave-out richness null.
All outputs aggregate. No cave labels, coordinates, keys, or row-level data exported.
"""
import json,sys,re
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import get,clean,OUT
from roost_fd_source_audit_v3 import label,series_label,quant
from roost_fd_source_audit_v4 import name,cavekeys,wing

SEED=20261124
NREP=999
DIET={"insectivore","omnivore","frugivore","carnivore","sanguivore","nectarivore"}
def fix_candidate(s):
    v=label(s)
    if v is None:return None
    # Two observed encoding artefacts; not a general accent stripping or fuzzy matcher.
    if not (v.endswith("ê") or "ï" in v):return None
    return name(v.removesuffix("ê").replace("ï"," "))
def numeric(s):
    x=pd.to_numeric(s,errors="coerce")
    return x.where(np.isfinite(x)&(x>0))
def realm(s):
    return label(s)
def choose_names(o,t,w,repair):
    a=o["Species.name"].map(name); b=t["Species.name"].map(name)
    c=w["scientificName.iucn"].map(name)
    oa=o["Species.name"].map(fix_candidate);tb=t["Species.name"].map(fix_candidate)
    strict_o=set(a.dropna());strict_t=set(b.dropna());strict_w=set(c.dropna())
    # For checklist recovery, require independent occurrence or wing exact name,
    # or a matching explicit genus/epithet after the same narrowly scoped cleanup.
    struct=pd.Series([name(str(g).strip()+" "+str(e).strip()) or
                     fix_candidate(str(g).strip()+" "+str(e).strip())
                     for g,e in zip(t["Genus"],t["Species"])],index=t.index)
    if repair:
        ok=tb.notna()&(tb.isin(strict_o|strict_w)|(tb==struct))
        b=b.fillna(tb.where(ok))
        ok=oa.notna()&oa.isin(set(b.dropna())|strict_w)
        a=a.fillna(oa.where(ok))
    return a,b,c,{"occ_resolved_rows":int(a.notna().sum()),"checklist_resolved_rows":int(b.notna().sum()),
        "occ_recovered":int((o["Species.name"].map(name).isna()&a.notna()).sum()),
        "checklist_recovered":int((t["Species.name"].map(name).isna()&b.notna()).sum())}
def prepare(o,l,t,w,repair):
    a,b,c,na=choose_names(o,t,w,repair)
    key=cavekeys(o,True); lk=cavekeys(l,False)
    counts=lk.dropna().value_counts(); unique=set(counts[counts==1].index)
    land=l.loc[lk.isin(unique)].copy()
    land.index=pd.Index(lk[lk.isin(unique)].tolist(),tupleize_cols=False)
    # Compare source realm only when independently exact agreement; exclude all occurrences
    # at sites whose occurrence realm is internally inconsistent or missing.
    x=pd.DataFrame({"site":key,"species":a,"tax":a.fillna(series_label(o["Species.name"]).map(lambda s:"unresolved:"+s if s else None)),
       "realm":o["Biogeographical.realm"].map(realm),"country":series_label(o["Country.record"])})
    x=x[x.site.isin(unique)].dropna(subset=["site","tax"])
    rc=x.groupby("site",sort=False).realm.agg(lambda s:len(set(s.dropna())) if s.notna().all() else -1)
    good=set(rc[rc==1].index)
    x=x[x.site.isin(good)].copy()
    rmap=dict(zip(land.index,land["Biogeographical.realm"].map(realm)))
    agree=x.realm==x.site.map(rmap)
    good=set(x.loc[agree,"site"])-set(x.loc[~agree,"site"])
    x=x[x.site.isin(good)].drop_duplicates(["site","tax"]).copy()
    # Data.entry is a separate, untrusted possible key; diagnose only.
    ae=series_label(o["Data.entry"]); le=series_label(l["Data_Entry"])
    lecnt=le.dropna().value_counts()
    lookup={e:k for e,k in zip(le,lk) if e is not None and lecnt.get(e,0)==1 and k is not None}
    comparable=ae.isin(lookup)&key.notna()
    same=pd.Series([bool(k==lookup.get(e)) if k is not None and e in lookup else False for e,k in zip(ae,key)])
    qa={"occ_keys":int(key.nunique()),"unique_land_keys":len(unique),"verified_realm_consistent_sites":int(x.site.nunique()),
        "cave_taxon_pairs":len(x),"unresolved_pairs":int(x.species.isna().sum()),"countries":int(x.country.nunique()),
        "data_entry_diagnostic":{"occ_unique":int(ae.nunique()),"land_unique":int(le.nunique()),
         "occ_rows_unique_land_entry_match":int(comparable.sum()),"also_exact_composite":int((same&comparable).sum())}}
    tr=pd.DataFrame({"species":b,"mass":numeric(t["Body.mass"]),"diet":series_label(t["Feeding groups"])})
    tr=tr[tr.species.notna()&~tr.species.duplicated(keep=False)].copy()
    tr.loc[~tr.diet.isin(DIET),"diet"]=None
    tr["logmass"]=np.log(tr.mass)
    wr=pd.DataFrame({"species":c,"ar":numeric(w["aspectRatio"]),"wl":numeric(w["wingLoading_Nm2"]),
        "n_ar":pd.to_numeric(w["n.AR"],errors="coerce"),"n_wl":pd.to_numeric(w["n.WL"],errors="coerce")})
    wr=wr[wr.species.notna()&~wr.species.duplicated(keep=False)].copy()
    wr["logar"]=np.log(wr.ar);wr["logwl"]=np.log(wr.wl)
    tr=tr.merge(wr,on="species",how="outer",validate="one_to_one")
    return x,tr,{"names":na,"sites":qa}
def build_dist(tr,fields,categorical):
    T=[]
    for c in fields:
        v=tr[c].to_numpy()
        if c in categorical:d=(v[:,None]!=v[None,:]).astype(float)
        else:
            span=v.max()-v.min()
            if not np.isfinite(span) or span<=0:raise ValueError("invalid span")
            d=np.abs(v[:,None]-v[None,:])/span
        T.append(d)
    return np.mean(T,axis=0)
def null_groups(pairs,trait,axes,region_field,coverage_threshold,weighted=False,positive_counts=False,seed=SEED):
    fields=list(dict.fromkeys(c for _,f,_ in axes for c in f))
    tr=trait.dropna(subset=fields).copy()
    if positive_counts:tr=tr[(tr.n_ar>0)&(tr.n_wl>0)]
    tr=tr.sort_values("species").reset_index(drop=True)
    index=dict(zip(tr.species,np.arange(len(tr))))
    dists=np.asarray([build_dist(tr,f,cat) for _,f,cat in axes])
    x=pairs.copy()
    x["idx"]=x.species.map(index)
    groups={}
    freq=defaultdict(Counter);nr=Counter()
    for k,g in x.groupby("site",sort=False):
        if g[region_field].nunique()!=1:continue
        ids=np.sort(g.idx.dropna().astype(int).unique())
        region=g[region_field].iloc[0];country=g.country.iloc[0]
        groups[k]=(len(g),ids,region,country)
        freq[region].update(ids.tolist());nr[region]+=1
    rng=np.random.default_rng(seed)
    result=[];coverage=[];eligible=0;zero_var=Counter()
    for k,(N,ids,region,country) in groups.items():
        n=len(ids);coverage.append(n/N)
        if n<3 or n/N<coverage_threshold:continue
        eligible+=1
        other=freq[region].copy();other.subtract(ids.tolist())
        pool=np.array(sorted([i for i,v in other.items() if v>0]),dtype=int)
        if len(pool)<max(15,2*n) or nr[region]-1<10:continue
        # Weighted sampling without replacement via exponential random keys.
        if weighted:
            w=np.array([other[i] for i in pool],float)
            u=rng.exponential(size=(NREP,len(pool)))/w[None,:]
        else:u=rng.random((NREP,len(pool)))
        draw=pool[np.argpartition(u,n-1,axis=1)[:,:n]]
        i,j=np.triu_indices(n,1)
        observed=dists[:,ids[i],ids[j]].mean(axis=1)
        expected=dists[:,draw[:,i],draw[:,j]].mean(axis=2)
        mu=expected.mean(axis=1);sd=expected.std(axis=1,ddof=1)
        delta=observed-mu;ses=np.divide(delta,sd,out=np.full_like(delta,np.nan),where=sd>1e-12)
        for z,(ax,_,_) in enumerate(axes):
            if not np.isfinite(ses[z]):zero_var[ax]+=1
            result.append((ax,country,region,n,observed[z],mu[z],delta[z],ses[z]))
    out={"trait_reference_species":len(tr),"matched_species":int(x.loc[x.idx.notna(),"species"].nunique()),
        "matched_pairs":int(x.idx.notna().sum()),"eligible_sites_pre_null":eligible,"coverage":quant(coverage),
        "pool":region_field,"coverage_threshold":coverage_threshold,"frequency_weighted":weighted,
        "positive_source_counts_only":positive_counts,"axes":{}}
    for ax,_,_ in axes:
        rr=pd.DataFrame([r[1:] for r in result if r[0]==ax],columns=["country","region","richness","mpd","expected","delta","ses"])
        if rr.empty:out["axes"][ax]={"sites":0};continue
        cm=rr.groupby("country").delta.agg(["size","median"])
        cm=cm[cm["size"]>=5]
        # Country summaries are descriptive, not independent p-values.
        out["axes"][ax]={"sites":len(rr),"countries":int(rr.country.nunique()),"regions":int(rr.region.nunique()),
            "richness":quant(rr.richness),"mpd":quant(rr.mpd),"expected":quant(rr.expected),"delta":quant(rr.delta),
            "ses":quant(rr.ses),"negative_fraction":float((rr.delta<0).mean()),"zero_null_variance":zero_var[ax],
            "countries_ge5":len(cm),"countries_ge5_negative_median":int((cm["median"]<0).sum()),
            "country_equal_median_delta":float(cm["median"].median()) if len(cm) else None,
            "regional_summary":{str(k):{"n":len(g),"median_delta":float(g.delta.median()),"median_ses":float(g.ses.dropna().median()) if g.ses.notna().any() else None} for k,g in rr.groupby("region") if len(g)>=5}}
    return out
def main():
    o,om=get("occ");l,lm=get("land");t,tm=get("traits")
    assert all(v is not None for v in (o,l,t))
    data,wm=wing();w=data["wingReview_wm_data_speciesLevel.csv"]
    meta=data["wingReview_metadata.csv"]
    desc=meta[meta.fieldTitle.astype(str).str.fullmatch(r"(?i)(aspectRatio|wingLoading_Nm2|n\.AR|n\.WL|AR_calc|WL_calc|relWingLoading)")]
    r={"sources":{"occ":om["sha256"],"land":lm["sha256"],"traits":tm["sha256"],"wing":wm},
       "wing_metadata":desc[["fieldTitle","dataDesc","dataFile"]].fillna("").to_dict("records"),
       "status":"descriptive_null_baseline_only","runs":{}}
    resource=[("resource",["logmass","diet"],["diet"])]
    flight=[("flight",["logar","logwl"],[])]
    both=flight+resource
    for repair in (False,True):
        x,tr,audit=prepare(o,l,t,w,repair)
        run={"audit":audit,"wing_trait_ranges":{"AR":quant(tr.ar),"WL_Nm2":quant(tr.wl)},
          "source_positive_counts_complete":int(((tr.n_ar>0)&(tr.n_wl>0)&tr.ar.notna()&tr.wl.notna()).sum())}
        # All axes separately first, then paired on identical caves and complete species.
        for nm,ax in [("resource_all",resource),("flight_all",flight),("paired_realm",both)]:
            run[nm]=null_groups(x,tr,ax,"realm",.8,seed=SEED)
        if repair:
            for nm,region,cov,weighted,pos in [("paired_country","country",.8,False,False),
               ("paired_weighted","realm",.8,True,False),("paired_complete","realm",1.,False,False),
               ("paired_positive_counts","realm",.8,False,True)]:
                run[nm]=null_groups(x,tr,both,region,cov,weighted,pos,seed=SEED)
        r["runs"]["encoding_repair_sensitivity" if repair else "strict_primary"]=run
    dest=OUT/"audit_v5.json";dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    # Compact logs: full details in JSON artifact, no raw records.
    print(json.dumps(r,indent=2,allow_nan=False))
    return 0
if __name__=="__main__":sys.exit(main())
