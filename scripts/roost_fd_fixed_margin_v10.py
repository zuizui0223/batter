"""V10 exploratory fixed-margin assemblage null after the negative V9 terrain result.
No cave-level data, coordinates, keys, or source labels exported.
"""
import json,sys
from collections import Counter,defaultdict
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import get,OUT
from roost_fd_source_audit_v3 import quant,series_label
from roost_fd_source_audit_v4 import wing,name,cavekeys
from roost_fd_empirical_null_v5 import prepare,build_dist,SEED
from roost_fd_study_wing_v7 import study_wing

FIELDS=["logar","logwl","logmass","diet"]
AXES=[("flight",["logar","logwl"],[]),("resource",["logmass","diet"],["diet"]),
      ("AR",["logar"],[]),("WL",["logwl"],[]),("mass",["logmass"],[]),("diet",["diet"],["diet"])]
CHAINS=4
DRAWS=250
BURN=30
THIN=2

def mpd(D,row):
    ix=np.array(sorted(row),dtype=int)
    i,j=np.triu_indices(len(ix),1)
    return D[:,ix[i],ix[j]].mean(axis=1)

def margins(rows):
    return tuple(map(len,rows)),Counter(v for row in rows for v in row)

def family_margins(rows,families):
    return [Counter(families[v] for v in row) for row in rows]

def trade(rows,i,j,rng,families=None):
    a,b=rows[i],rows[j]
    common=a&b; aa=a-b;bb=b-a
    if not aa or not bb:return False
    # Each exchange is a symmetric random reallocation of exclusive species,
    # conditional on shared members and row sizes; family mode conditions
    # independently on each row's family count, preserving its family mix.
    if families is None:
        p=sorted(aa|bb);rng.shuffle(p);n=len(aa)
        u=set(p[:n]);v=set(p[n:])
    else:
        ca=Counter(families[k] for k in aa)
        blocks=defaultdict(list)
        for k in sorted(aa|bb):blocks[families[k]].append(k)
        u=set();v=set()
        for f,p in sorted(blocks.items()):
            rng.shuffle(p);n=ca[f];u.update(p[:n]);v.update(p[n:])
    if u==aa:return False
    rows[i]=common|u;rows[j]=common|v
    return True

def test():
    rows=[{0,1,2},{1,3},{0,4,5},{2,3,4}]
    initial=margins(rows); fam=["a","a","b","b","a","b"]
    fm=family_margins(rows,fam);rng=np.random.default_rng(SEED)
    for _ in range(200):
        i,j=rng.choice(len(rows),2,replace=False)
        trade(rows,i,j,rng,fam)
        assert margins(rows)==initial and family_margins(rows,fam)==fm
    for _ in range(200):
        i,j=rng.choice(len(rows),2,replace=False)
        trade(rows,i,j,rng)
        assert margins(rows)==initial

def one_block(rows,target,D,seed,families):
    base=[set(s) for s in rows];m=margins(base);n=len(base)
    fm=family_margins(base,families) if families is not None else None
    obs=np.array([mpd(D,base[i]) for i in target])
    vals=np.empty((CHAINS,DRAWS,len(target),len(AXES)))
    unique=[set() for _ in target];changed=np.zeros(len(target),int)
    accepts=attempts=0
    for c in range(CHAINS):
        rng=np.random.default_rng(seed+c)
        work=[set(s) for s in base]
        def sweep():
            nonlocal accepts,attempts
            # Row pair chosen independently of matrix contents. n attempts / sweep.
            for _ in range(n):
                i=int(rng.integers(n));j=int(rng.integers(n-1));j+=j>=i
                accepts+=int(trade(work,i,j,rng,families));attempts+=1
        for _ in range(BURN):sweep()
        for d in range(DRAWS):
            for _ in range(THIN):sweep()
            for k,i in enumerate(target):
                key=tuple(sorted(work[i]));unique[k].add(key)
                changed[k]+=int(work[i]!=base[i])
                vals[c,d,k]=mpd(D,work[i])
        assert margins(work)==m
        if fm is not None:assert family_margins(work,families)==fm
    pooled=vals.reshape(CHAINS*DRAWS,len(target),len(AXES))
    mu=pooled.mean(axis=0);sd=pooled.std(axis=0,ddof=1)
    delta=obs-mu
    ses=np.divide(delta,sd,out=np.full_like(delta,np.nan),where=sd>1e-12)
    # Split-chain mean disagreement relative to total null SD, descriptive mixing diagnostic.
    gap=np.ptp(vals.mean(axis=1),axis=0)
    gap=np.divide(gap,sd,out=np.full_like(gap,np.nan),where=sd>1e-12)
    return obs,delta,ses,gap,[len(x) for x in unique],changed/(CHAINS*DRAWS),accepts,attempts

def make_sites(x,tr,o):
    tr=tr.dropna(subset=FIELDS).sort_values("species").reset_index(drop=True)
    idx=dict(zip(tr.species,np.arange(len(tr))))
    assert tr.species.is_unique
    D=np.asarray([build_dist(tr,f,cat) for _,f,cat in AXES])
    # Single-source site sensitivity, not assuming citations are sampling effort.
    k=cavekeys(o,True)
    q=pd.DataFrame({"site":k,"source":series_label(o["Record.source"])}).dropna(subset=["site"])
    sources={}
    for key,g in q.groupby("site",sort=False):
        s=set(g.source.dropna())
        if len(s)==1 and g.source.notna().all():sources[key]=next(iter(s))
    y=x.copy();y["idx"]=y.species.map(idx);sites=[]
    for key,g in y.groupby("site",sort=False):
        ids=set(g.idx.dropna().astype(int))
        assert len(ids)==int(g.idx.notna().sum())
        if not ids:continue
        sites.append({"site":key,"country":g.country.iloc[0],"realm":g.realm.iloc[0],
            "source":sources.get(key),"ids":ids,"n":len(ids),"coverage":len(ids)/len(g)})
    return sites,tr,D

def scenario(sites,tr,D,mode,seed):
    groups=defaultdict(list)
    for a in sites:
        if mode=="source" and a["source"] is None:continue
        g=(a["country"],a["realm"])
        if mode=="source":g+=(a["source"],)
        groups[g].append(a)
    family=tr.family.to_numpy() if mode=="family" else None
    results=[];target_total=blocked=0;accepted=attempted=0;blocks=0
    for b,(_,g) in enumerate(sorted(groups.items())):
        pool=set().union(*(a["ids"] for a in g))
        targets=[i for i,a in enumerate(g) if a["n"]>=3 and a["coverage"]>=.8]
        target_total+=len(targets)
        ok=[i for i in targets if len(g)>=10 and len(pool)>=max(15,2*g[i]["n"])]
        blocked+=len(targets)-len(ok)
        if not ok:continue
        blocks+=1
        obs,de,se,ga,un,ch,ac,at=one_block([a["ids"] for a in g],ok,D,seed+10007*b,family)
        accepted+=ac;attempted+=at
        for j,i in enumerate(ok):
            a=g[i]
            d={"site":a["site"],"country":a["country"],"n":a["n"],"coverage":a["coverage"],
                "null_unique":un[j],"changed_fraction":ch[j]}
            for h,(ax,_,_) in enumerate(AXES):
                d[ax+"_observed"]=obs[j,h];d[ax+"_delta"]=de[j,h];d[ax+"_ses"]=se[j,h];d[ax+"_chain_gap"]=ga[j,h]
            results.append(d)
    r=pd.DataFrame(results)
    audit={"blocks_with_targets":blocks,"available_targets":target_total,"targets_blocked_by_pool_gate":blocked,
            "tested_targets":len(r),"trade_acceptance":accepted/attempted if attempted else None}
    return r,audit

def summarize(r):
    if r.empty:return {"sites":0}
    d={"sites":len(r),"countries":int(r.country.nunique()),"unique_null_assemblages":quant(r.null_unique),
        "null_changed_fraction":quant(r.changed_fraction),"fixed_sites":int((r.null_unique==1).sum()),"axes":{}}
    for ax,_,_ in AXES:
        z=r[ax+"_delta"];s=r[ax+"_ses"];ok=s.notna()
        cm=r.loc[ok].groupby("country")[ax+"_delta"].agg(["size","median"])
        cm=cm[cm["size"]>=3]
        d["axes"][ax]={"n_nonzero_variance":int(ok.sum()),"delta":quant(z),"ses":quant(s),
           "negative_fraction_nonzero_variance":float((z[ok]<0).mean()) if ok.any() else None,
           "chain_mean_gap_SD":quant(r[ax+"_chain_gap"]),
           "countries_ge3":len(cm),"countries_ge3_negative_median":int((cm["median"]<0).sum()),
           "country_equal_median_delta":float(cm["median"].median()) if len(cm) else None}
    ok=r.flight_ses.notna()&r.resource_ses.notna()
    d["paired"]={"n_nonzero_both":int(ok.sum()),
       "resource_minus_flight_SES":quant(r.loc[ok,"resource_ses"]-r.loc[ok,"flight_ses"]),
       "flight_negative_resource_positive":float(((r.loc[ok,"flight_delta"]<0)&(r.loc[ok,"resource_delta"]>0)).mean()) if ok.any() else None}
    return d

def main():
    test()
    o,om=get("occ");l,lm=get("land");t,tm=get("traits");data,wm=wing()
    raw=data["wingReview_wm_data_final.csv"];w,qc=study_wing(raw,"direct_or_formula")
    family=pd.DataFrame({"species":raw["scientificName.iucn"].map(name),
       "family":raw["familyName"].astype(str).str.strip().str.lower()}).dropna(subset=["species"])
    f=family.groupby("species").family.agg(lambda s:sorted(set(s)))
    f={k:v[0] for k,v in f.items() if len(v)==1 and v[0] not in ("nan","")}
    report={"status":"posthoc_fixed_margin_diagnostic","seed":SEED,"chains":CHAINS,"draws_each":DRAWS,
      "burn_sweeps":BURN,"thin_sweeps":THIN,"runs":{},"sources":{"occ":om["sha256"],"land":lm["sha256"],"traits":tm["sha256"],"wing":wm}}
    for repair in (True,False):
        x,tr,audit=prepare(o,l,t,w,repair);tr["family"]=tr.species.map(f)
        # Family labels must be known for every complete reference species, or stop
        # rather than change trait pool between conditioned and unconditioned tests.
        if tr.dropna(subset=FIELDS).family.isna().any():raise ValueError("family mapping incomplete")
        sites,tr,D=make_sites(x,tr,o);r={};frames={}
        for mode in (("geography","source","family") if repair else ("geography",)):
            v,a=scenario(sites,tr,D,mode,SEED);frames[mode]=v;r[mode]={"audit":a,"summary":summarize(v)}
        for mode in ("family","source"):
            if mode in frames and not frames[mode].empty and not frames["geography"].empty:
                shared=set(frames[mode].site)&set(frames["geography"].site)
                r[mode]["same_targets_comparison"]={k:summarize(frames[k][frames[k].site.isin(shared)]) for k in ("geography",mode)}
        report["runs"]["repair" if repair else "strict"]={"site_audit":audit,"trait_complete_species":len(tr),"scenarios":r}
    (OUT/"audit_v10.json").write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps(report,indent=2,allow_nan=False))
if __name__=="__main__":main()
