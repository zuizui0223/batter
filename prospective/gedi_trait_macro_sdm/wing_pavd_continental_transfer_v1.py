"""Physical wing x measured PAVD continental transfer, frozen contract V1.
Train-only coefficients; external scoring never fits FWS labels. No raw coordinates exported.
"""
import hashlib,itertools,json,math,pathlib,sys
import numpy as np,pandas as pd
from scipy.optimize import minimize
from scipy.special import expit
O=pathlib.Path("wing_pavd_transfer");O.mkdir(exist_ok=True)
K=["cell_x","cell_y"];CL=["bio1","bio4","bio5","bio6","bio12","bio15"]
LC=["broadleaf","needleleaf","mixed","other_forest"]
ENV=CL+["LC_"+k for k in LC]+["RH98","PAI","cover","PAVD_lower_fraction"]
TRAITS=["AR","log_WL","log_mass"]
PIN="99a19c169e18a0bafa4a518b7f844b56d2fe846cac13d5c035f4eae562a74c7b"
MOD=["AR_B","AR_M","W_B","W_M"]
def sha(p):
    with pathlib.Path(p).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def dump(name,r):
    s=json.dumps(r,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else None)
    (O/name).write_text(s+"\n")
    print("WING_PAVD_REPORT="+s,flush=True)
def traits():
    p=pathlib.Path("wing/primary_LSA_physical.csv");assert sha(p)==PIN
    t=pd.read_csv(p).set_index("scientificName.iucn")
    assert len(t)==280 and t.index.is_unique
    t["log_WL"]=np.log(t.WL_N_m2);t["log_mass"]=np.log(t.mass_g_physical)
    assert np.isfinite(t[TRAITS]).all().all()
    return t
def weighted(z,gb):
    g=z[:,4];groups=np.bincount(g,minlength=len(gb))
    blocks={b:i for i,b in enumerate(sorted(set(gb[j] for j in np.flatnonzero(groups))))}
    bidx=np.array([blocks[gb[j]] for j in g])
    ngrp=np.bincount([blocks[gb[j]] for j in np.flatnonzero(groups)],minlength=len(blocks))
    w=1/(groups[g]*ngrp[bidx]*len(blocks));assert np.isclose(w.sum(),1)
    return w,bidx
def inputs(z,raw,T,stats,model):
    sa,sb,ca,cb,_=z.T
    D=(raw[ca]-raw[cb])/np.asarray(stats["env_sd"])
    V=(T[sa]-T[sb])/np.asarray(stats["trait_sd"])
    n=1 if model.startswith("AR") else 3
    e=len(ENV) if model.endswith("_M") else len(ENV)-1
    return (V[:,:n,None]*D[:,None,:e]).reshape(len(z),n*e)
def fit(X,w):
    def obj(b):
        h=X@b
        return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
    f=minimize(obj,np.zeros(X.shape[1]),jac=True,method="L-BFGS-B",options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
    assert f.success or np.max(np.abs(f.jac))<1e-6
    return f.x,float(np.max(np.abs(f.jac)))
def train():
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
    rng=np.random.default_rng(20261125);pairs=[];gb=[]
    for key,v in d.groupby(G,sort=True):
        by={s:np.sort(w.ci.unique()) for s,w in v.groupby("species_key",sort=True)}
        for a,b in itertools.combinations(sorted(by),2):
            ca=np.repeat(by[a],len(by[b]));cb=np.tile(by[b],len(by[a]));q=ca!=cb;ca,cb=ca[q],cb[q]
            if not len(ca):continue
            if len(ca)>128:
                q=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[q],cb[q]
            g=len(gb);gb.append((int(key[2]),int(key[3])));pairs.extend((ix[a],ix[b],int(x),int(y),g) for x,y in zip(ca,cb))
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
    R={"stage":"European training only; external test not inspected","status":"START","source_trait_sha256":PIN,"measured_grid_sha256":rc["output_sha256"],"train_comparisons":len(z),"train_blocks":len(set(gb[j] for j in gi)),"train_cells":len(used),"train_taxa":len(sp),"train_names":[names[i] for i in sp],"unmatched_trait_names":[n for n in names if n not in t.index],"original_SDM_admitted":False}
    dump("report.json",R)
    if R["train_taxa"]<10 or R["train_blocks"]<20 or len(z)<300 or len(used)<30:
        R["status"]="STOP_INSUFFICIENT_TRAINING_SUPPORT";dump("report.json",R);return
    es=raw[used].std(0);ts=T[sp].std(0);assert (ts>0).all();es[es<=1e-12]=1
    stats={"env_sd":es.tolist(),"trait_sd":ts.tolist(),"env_min":raw[used].min(0).tolist(),"env_max":raw[used].max(0).tolist(),"trait_min":T[sp].min(0).tolist(),"trait_max":T[sp].max(0).tolist()}
    w,_=weighted(z,gb);co={}
    for model in MOD:
        X=inputs(z,raw,T,stats,model);b,grad=fit(X,w);co[model]=b.tolist()
        R.setdefault("optimizer",{})[model]={"max_gradient":grad}
    model={"contract":"WING_PAVD_CONTINENTAL_TRANSFER_CONTRACT_V1.md","train_names":R["train_names"],"stats":stats,"environment":ENV,"traits":TRAITS,"coefficients":co,"trait_source_sha256":PIN,"training_support":{k:R[k] for k in ["train_comparisons","train_blocks","train_cells","train_taxa"]}}
    dump("frozen_model.json",model)
    R.update(status="TRAINED_FROZEN_COEFFICIENTS_NO_EXTERNAL_SCORE",model_sha256=sha(O/"frozen_model.json"),profile_coefficients=dict(zip(TRAITS,np.asarray(co["W_M"]).reshape(3,len(ENV))[:,-1].tolist())),ar_only_profile_coefficient=co["AR_M"][-1],note="Training slopes only, no confidence interval or validation; no FWS outcomes used.")
    dump("report.json",R)
def external(ct,z,gb,gr,names,u):
    # Callback replaces local fit entirely; no FWS response fitting.
    import fws_measured_pavd_independent_v1 as m
    p=pathlib.Path("frozen/frozen_model.json");q=json.loads(p.with_name("report.json").read_text())
    assert q["status"]=="TRAINED_FROZEN_COEFFICIENTS_NO_EXTERNAL_SCORE" and sha(p)==q["model_sha256"]
    model=json.loads(p.read_text());assert model["environment"]==ENV and model["traits"]==TRAITS and model["trait_source_sha256"]==PIN
    t=traits();T=t.reindex(names)[TRAITS].to_numpy(float)
    assert not set(names)&set(model["train_names"])
    sa,sb,ca,cb,gi=z.T
    keep=np.isfinite(T[sa]).all(1)&np.isfinite(T[sb]).all(1)
    z=z[keep];sa,sb,ca,cb,gi=z.T
    sp=np.unique(np.r_[sa,sb]);used=np.unique(np.r_[ca,cb])
    s={"comparisons":len(z),"taxa":len(sp),"blocks":len(set(gb[j] for j in gi)),"routes":len(set(gr[j] for j in gi)),"cells":len(used),"names":[names[i] for i in sp],"fraction_of_measured_pairs_retained":float(keep.mean())}
    R=m.R;R.update(stage="external FWS wing trait transfer, no local training",frozen_model_sha256=sha(p),test_support=s,training_support=model["training_support"],original_SDM_admitted=False)
    if s["taxa"]<6 or s["routes"]<10 or s["blocks"]<8 or s["comparisons"]<300 or s["cells"]<30:
        R["status"]="STOP_INSUFFICIENT_EXTERNAL_TRAIT_SUPPORT";dump("external_report.json",R);return
    raw=ct.merge(u,on=K,validate="one_to_one").sort_values("ci")[ENV].to_numpy(float)
    assert np.isfinite(raw[used]).all()
    stats=model["stats"];w,bidx=weighted(z,gb)
    scores=np.stack([-np.logaddexp(0,-inputs(z,raw,T,stats,k)@np.array(model["coefficients"][k])) for k in MOD],axis=1)
    mean=w@scores
    den=np.bincount(bidx,weights=w);block_scores=np.column_stack([np.bincount(bidx,weights=w*scores[:,i])/den for i in range(len(MOD))])
    contrasts={}
    for a,b in [("W_M","W_B"),("W_M","AR_M"),("AR_M","AR_B"),("W_M","neutral")]:
        d=block_scores[:,MOD.index(a)]-(block_scores[:,MOD.index(b)] if b!="neutral" else -math.log(2))
        boots=np.random.default_rng(20261126).choice(d,size=(2000,len(d)),replace=True).mean(1)
        contrasts[a+" minus "+b]={"gain":float(d.mean()),"positive_blocks":int((d>0).sum()),"conditional_block_bootstrap_95":np.quantile(boots,[.025,.975]).tolist()}
    def outside(x,keys,lo,hi):
        return {k:int(v) for k,v in zip(keys,((x<np.asarray(lo))|(x>np.asarray(hi))).sum(0))}
    R.update(status="EXTERNAL_TRANSFER_COMPLETE_DESCRIPTIVE_ONLY",scores={**dict(zip(MOD,map(float,mean))),"neutral":-math.log(2)},contrasts=contrasts,environment_marginal_exceedance=outside(raw[used],ENV,stats["env_min"],stats["env_max"]),trait_marginal_exceedance=outside(T[sp],TRAITS,stats["trait_min"],stats["trait_max"]),limits=["1-km European training vs 6-km North American observation support; not scale-equivalent.","Different observational protocols and source-open FWS GVSM diagnostic. No FWS fitting, selection or calibration.","Actual flight altitude, occupancy, detection kernel and causal mechanism unidentifiable."])
    dump("external_report.json",R)
def test():
    import fws_measured_pavd_independent_v1 as m
    m.fit=external
    # Preserve pre-fit source and support receipts if measured or forest gate fails.
    m.main()
    if not (O/"external_report.json").exists():dump("external_report.json",m.R)
if __name__=="__main__":
    try:
        if sys.argv[1]=="train":train()
        elif sys.argv[1]=="test":test()
        else:raise ValueError("mode")
    except Exception as e:
        dump("failure.json",{"status":"INCOMPLETE","error_type":type(e).__name__});raise
