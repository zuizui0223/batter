"""Post-external-failure training coefficient stability only, no model selection.
Exact frozen EU pairs, covariates, standardized physical traits, ridge and group weights.
Do not overwrite the externally tested model or use diagnostic coefficients in FWS.
"""
import hashlib,itertools,json,math,pathlib
import numpy as np,pandas as pd
from wing_pavd_continental_transfer_v1 import sha,traits,weighted,inputs,fit,K,CL,LC,ENV,TRAITS
O=pathlib.Path("wing_deletion_stability");O.mkdir(exist_ok=True)
MODEL="3e282cdcf4d21bf41234f1cae0e2ef71a3359269c68d592742c10101ac1feb97"
R={"stage":"post-failure wing-PAVD coefficient deletion diagnostic","model_sha256":MODEL,"status":"START","external_model_modified":False,"limits":["Uses inspected training data after external failure, not an independent test or preplanned biological inference.","Fixed scaling and penalties, delete subsets only, not prediction model selection.","Signs are conditional regularized coefficients; not causal or phylogenetically independent; deletion ranges are not confidence intervals.","No new FWS fit, no rescue or improvement claim."]}
def save():
    text=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else None)
    (O/"report.json").write_text(text+"\n")
    print("WING_DELETION_REPORT="+text,flush=True)
def diagnose():
    t=traits();p=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
    assert sha(p)=="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
    d=pd.read_csv(p,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
    roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
    d=d[d.forest_profile_support.astype(str).str.lower().eq("true")&d.species_key.isin(roster)&d.dataset_key.ne("")&d.year.str.fullmatch(r"20[0-9]{2}")].copy()
    names=d[["species_key","source_name"]].drop_duplicates().set_index("species_key").loc[roster,"source_name"].tolist();assert len(set(names))==14
    ct=d[K+CL].drop_duplicates().sort_values(K).reset_index(drop=True);assert len(ct)==1796 and not ct.duplicated(K).any()
    ct["ci"]=np.arange(len(ct));ix={s:i for i,s in enumerate(roster)}
    G=["dataset_key","year","bx","by"]
    d=d.merge(ct[K+["ci"]],on=K,validate="many_to_one").drop_duplicates(["species_key","ci",*G]).sort_values([*G,"species_key","ci"])
    rng=np.random.default_rng(20261125);pairs=[];gb=[];gp=[]
    for key,v in d.groupby(G,sort=True):
        by={s:np.sort(w.ci.unique()) for s,w in v.groupby("species_key",sort=True)}
        for a,b in itertools.combinations(sorted(by),2):
            ca=np.repeat(by[a],len(by[b]));cb=np.tile(by[b],len(by[a]));q=ca!=cb;ca,cb=ca[q],cb[q]
            if not len(ca):continue
            if len(ca)>128:
                q=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[q],cb[q]
            g=len(gb);gb.append((int(key[2]),int(key[3])));gp.append(str(key[0]));pairs.extend((ix[a],ix[b],int(x),int(y),g) for x,y in zip(ca,cb))
    z=np.asarray(pairs,dtype=int);assert (len(z),len(gb),len(set(gb)))==(31601,1626,51)
    p=pathlib.Path("baseline_lc100/cell_covariates.csv.gz");assert sha(p)=="0712db21f70bb087d21c806fa28bf5dc65eb6463c041b386c125626c0082048b"
    lc=pd.read_csv(p);cols=["lc100_"+k+"_class_fraction" for k in LC]
    ct=ct.merge(lc[K+cols+["leaf_support"]].rename(columns=dict(zip(cols,["LC_"+k for k in LC]))),on=K,validate="one_to_one")
    p=pathlib.Path("gedi_grid/cell_gedi_profiles.csv.gz");rc=json.loads(p.with_name("receipt.json").read_text());assert rc["status"]=="GRID_PROFILE_SUPPORT_READY" and sha(p)==rc["output_sha256"]
    g=pd.read_csv(p);ct=ct.merge(g[K+["rh-98-a0","pai-a0","cover-a0","PAVD_lower_fraction","gedi_support"]].rename(columns={"rh-98-a0":"RH98","pai-a0":"PAI","cover-a0":"cover"}),on=K,validate="one_to_one")
    assert ct.ci.tolist()==list(range(1796))
    raw=ct[ENV].to_numpy(float);T=t.reindex(names)[TRAITS].to_numpy(float)
    valid=np.isfinite(raw).all(1)&ct.leaf_support.astype(str).str.lower().eq("true")&ct.gedi_support.astype(str).str.lower().eq("true")&ct[["LC_"+k for k in LC]].sum(1).ge(.3)
    sa,sb,ca,cb,gi=z.T;ok=valid.to_numpy()[ca]&valid.to_numpy()[cb]&np.isfinite(T[sa]).all(1)&np.isfinite(T[sb]).all(1)
    z=z[ok];sa,sb,ca,cb,gi=z.T
    used=np.unique(np.r_[ca,cb]);sp=np.unique(np.r_[sa,sb])
    # Keep the exact trained data, feature transforms and coefficients fixed.
    p=pathlib.Path("frozen/frozen_model.json");assert sha(p)==MODEL
    model=json.loads(p.read_text());stats=model["stats"]
    assert model["train_names"]==[names[i] for i in sp] and model["traits"]==TRAITS and model["environment"]==ENV
    assert (len(z),len(used),len(set(gb[j] for j in gi)),len(sp))==(20336,1132,46,14)
    # Reproduce the two frozen fits before any deletion diagnostics.
    w,_=weighted(z,gb);Xm=inputs(z,raw,T,stats,"W_M");Xa=inputs(z,raw,T,stats,"AR_M")
    bm,_=fit(Xm,w);ba,_=fit(Xa,w)
    assert np.max(np.abs(bm-np.array(model["coefficients"]["W_M"])))<1e-9
    assert np.max(np.abs(ba-np.array(model["coefficients"]["AR_M"])))<1e-9
    R.update(status="FROZEN_FIT_REPLAY_PASS",training_support=model["training_support"],full_profile_coefficients=dict(zip(TRAITS,bm.reshape(3,len(ENV))[:,-1].tolist())),full_AR_only=ba[-1])
    # Fixed group hashes; no redefinition, stratified balancing, or outcome-dependent exclusions.
    bl=sorted(set(gb[j] for j in gi),key=lambda x:hashlib.sha256(f"{x[0]},{x[1]}".encode()).hexdigest())
    pr=sorted(set(gp[j] for j in gi),key=lambda x:hashlib.sha256(x.encode()).hexdigest())
    bmap={v:k%5 for k,v in enumerate(bl)};pmap={v:k%5 for k,v in enumerate(pr)}
    bf=np.array([bmap[gb[j]] for j in gi]);pf=np.array([pmap[gp[j]] for j in gi])
    genera=np.array([n.split()[0] for n in names])
    arms=[("space_fold",str(k+1),bf!=k) for k in range(5)]+[("provider_fold",str(k+1),pf!=k) for k in range(5)]
    arms += [("genus",str(g),(genera[sa]!=g)&(genera[sb]!=g)) for g in sorted(set(genera))]
    res=[]
    for mode,label,keep in arms:
        u=z[keep];a,b,x,y,g=u.T
        q={"mode":mode,"excluded":label,"pairs":len(u),"taxa":len(np.unique(np.r_[a,b])),"blocks":len(set(gb[j] for j in g)),"providers":len(set(gp[j] for j in g))}
        if q["taxa"]<8 or q["blocks"]<20 or q["pairs"]<300:
            q["status"]="INSUFFICIENT_DIAGNOSTIC_SUPPORT";res.append(q);continue
        wt,_=weighted(u,gb);coef,grad=fit(Xm[keep],wt);ar,grad_a=fit(Xa[keep],wt)
        q.update(status="COMPLETE",W_profile=dict(zip(TRAITS,coef.reshape(3,len(ENV))[:,-1].tolist())),AR_only_profile=float(ar[-1]),max_gradient=max(grad,grad_a))
        res.append(q)
    R["deletions"]=res;R["summaries"]={}
    for mode in ("space_fold","provider_fold","genus"):
        v=[q for q in res if q["mode"]==mode and q["status"]=="COMPLETE"]
        if not v:continue
        row={"completed":len(v),"attempted":sum(q["mode"]==mode for q in res)}
        for k in TRAITS+["AR_only"]:
            x=np.array([q["W_profile"][k] if k!="AR_only" else q["AR_only_profile"] for q in v])
            row[k]={"negative":int((x<0).sum()),"positive":int((x>0).sum()),"range":[float(x.min()),float(x.max())],"median":float(np.median(x))}
        R["summaries"][mode]=row
    R["status"]="DELETION_STABILITY_DIAGNOSTIC_COMPLETE"
    save()
if __name__=="__main__":
    try:diagnose()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:150]);save();raise
