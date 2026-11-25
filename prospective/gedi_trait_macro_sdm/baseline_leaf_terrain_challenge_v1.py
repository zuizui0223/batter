"""Frozen paired comparison: R50 beyond leaf composition and topography."""
import hashlib,itertools,json,math,pathlib
import numpy as np,pandas as pd
from scipy.special import expit
from scipy.optimize import minimize
OUT=pathlib.Path("baseline_challenge");OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
PIN="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
assert sha(SRC)==PIN
K=["cell_x","cell_y"];G=["dataset_key","year","bx","by"]
roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
base=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{v}_fraction" for v in [10,20,30,40,50]],"GVSM_area_mean_RH98_m"]
terrain=["surface_elev_mean_m","surface_elev_sd_m"];leaf=["broadleaf_fraction","conifer_fraction"]
features=base+["R50"]
d=pd.read_csv(SRC,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
yes=lambda x:x.astype(str).str.lower().eq("true")
f=d[yes(d.forest_profile_support)&d.species_key.isin(roster)&d.dataset_key.ne("")&d.year.str.fullmatch(r"20[0-9]{2}")].copy()
f[features+["AR"]]=f[features+["AR"]].apply(pd.to_numeric,errors="raise")
assert np.isfinite(f[features+["AR"]].to_numpy()).all()
ct=f[K+features].drop_duplicates().sort_values(K).reset_index(drop=True)
assert len(ct)==1796 and not ct.duplicated(K).any() and len(f[G].drop_duplicates())==491
ar=f[["species_key","AR"]].drop_duplicates().set_index("species_key").loc[roster,"AR"].to_numpy(float)
az=(ar-ar.mean())/ar.std();nsp=len(roster)
P=np.eye(nsp)-np.ones((nsp,nsp))/nsp-np.outer(az,az)/nsp
assert np.max(np.abs(P@az))<1e-10
ct["cell_index"]=np.arange(len(ct));idx={k:i for i,k in enumerate(roster)}
f=f.merge(ct[K+["cell_index"]],on=K,validate="many_to_one").drop_duplicates(["species_key","cell_index",*G]).sort_values([*G,"species_key","cell_index"])
rng=np.random.default_rng(20261125);rows=[];gb=[];gs=[]
for key,part in f.groupby(G,sort=True):
    by={s:np.sort(v.cell_index.unique()) for s,v in part.groupby("species_key",sort=True)}
    for s,t in itertools.combinations(sorted(by),2):
        a,b=by[s],by[t];ca=np.repeat(a,len(b));cb=np.tile(b,len(a));ok=ca!=cb;ca,cb=ca[ok],cb[ok]
        if not len(ca):continue
        if len(ca)>128:
            take=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[take],cb[take]
        group=len(gb);gb.append((int(key[2]),int(key[3])));gs.append(str(key[0]))
        rows.extend((idx[s],idx[t],int(x),int(y),group) for x,y in zip(ca,cb))
z=np.asarray(rows,dtype=int);sa,sb,ca,cb,gi=z.T
blocks=sorted(set(gb),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
bi={b:i for i,b in enumerate(blocks)};gbi=np.array([bi[b] for b in gb]);block=gbi[gi];fold=block%5
assert (len(z),len(gb),len(blocks))==(31601,1626,51)
assert [int((fold==k).sum()) for k in range(5)]==[12867,2315,6228,450,9741]
report={"stage":"post-pilot forest composition and surface-topography baseline challenge","input_sha256":PIN,"original_comparisons":len(z),"original_blocks":len(blocks),"original_groups":len(gb),"fixed_folds_verified":True,"source_reports":{},"status":"START","main_sdm_admitted":False,"limits":["Recorded label orientation, not biological occupancy, causal vertical effect or actual altitude.","DLT 2018 superseded vintage; DSM elevation includes surface objects; observation interactions remain.","Post-pilot matched sensitivity, not independent ecological replication."]}
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("BASELINE_CHALLENGE_REPORT="+json.dumps(report,allow_nan=False),flush=True)
for mode,cols in [("terrain",terrain),("leaf",leaf)]:
    p=pathlib.Path("baseline_"+mode+"/report.json")
    a=json.loads(p.read_text())
    report["source_reports"][mode]={k:v for k,v in a.items() if k!="sources"}
    q=p.parent/"cell_covariates.csv.gz"
    if not q.exists() or "output_sha256" not in a:
        ct[cols]=np.nan;ct[mode+"_support"]=False;continue
    assert sha(q)==a["output_sha256"]
    v=pd.read_csv(q)
    assert len(v)==1796 and not v.duplicated(K).any()
    ct=ct.merge(v[K+cols+[mode+"_support"]],on=K,how="left",validate="one_to_one")
    ct[mode+"_support"]=yes(ct[mode+"_support"])&np.isfinite(ct[cols]).all(axis=1)
assert ct.cell_index.to_numpy().tolist()==list(range(1796))
report["cell_support"]={"terrain":int(ct.terrain_support.sum()),"leaf":int(ct.leaf_support.sum()),"both":int((ct.terrain_support&ct.leaf_support).sum())}
save()
A=np.eye(nsp)[sa]-np.eye(nsp)[sb];D=A@P;trait=A@az
def weights(mask):
    gn=np.bincount(gi[mask],minlength=len(gb));bc=np.bincount(gbi[gn>0],minlength=len(blocks))
    w=1/(bc[block[mask]]*gn[gi[mask]])
    return w/len(np.unique(block[mask]))
def taxa(mask):return set(np.r_[sa[mask],sb[mask]])
def objective(b,X,w):
    h=X@b;return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
def run(mode,valid,additional):
    mask=valid[ca]&valid[cb];live=sorted(set(block[mask]));alltaxa=taxa(mask)
    a={"status":"STOP_INSUFFICIENT_MATCHED_SUPPORT","comparisons":int(mask.sum()),"blocks":len(live),"taxa":len(alltaxa),"cells":len(set(np.r_[ca[mask],cb[mask]])),"fold_blocks":[sum(b%5==k for b in live) for k in range(5)],"providers":len({gs[g] for g in np.unique(gi[mask])}),"retained_fraction":float(mask.mean())}
    if len(live)<20 or min(a["fold_blocks"])<4 or len(alltaxa)<10 or any(taxa(mask&(fold!=k))!=alltaxa for k in range(5)):return a
    configs={"B":base}
    configs.update(additional)
    names=["neutral"]+[name+ext for name in configs for ext in ("","+R50")]
    sc=np.full((len(z),len(names)),np.nan);sc[mask,0]=-math.log(2)
    raw_names=base+["R50"]+list(dict.fromkeys(x for v in additional.values() for x in v if x not in base))
    raw=ct[raw_names].to_numpy(float)
    assert np.isfinite(raw[valid]).all()
    fs=[]
    for k in range(5):
        tr=mask&(fold!=k);te=mask&(fold==k)
        assert not(set(block[tr])&set(block[te]))
        used=np.unique(np.r_[ca[tr],cb[tr]])
        mu=raw[used].mean(0);sd=raw[used].std(0);zero=sd<=1e-12;sd[zero]=1
        X=(raw-mu)/sd;X[:,zero]=0
        diff=X[ca]-X[cb]
        r=diff[:,raw_names.index("R50")]
        W=weights(tr);assert np.isclose(W.sum(),1)
        diag=[]
        for name,feats in configs.items():
            b=diff[:,[raw_names.index(v) for v in feats]]
            Y=np.column_stack([(D[:,:,None]*b[:,None,:]).reshape(len(z),-1),trait[:,None]*b])
            for suffix,M in [("",Y),("+R50",np.column_stack([Y,A*r[:,None]]))]:
                nt=name+suffix;j=names.index(nt);xt=np.ascontiguousarray(M[tr]);xe=np.ascontiguousarray(M[te])
                assert np.isfinite(xt).all() and np.isfinite(xe).all()
                fit=minimize(objective,np.zeros(xt.shape[1]),args=(xt,W),jac=True,method="L-BFGS-B",options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
                diag.append({"model":nt,"success":bool(fit.success),"iterations":int(fit.nit),"max_abs_gradient":float(np.abs(fit.jac).max())})
                if not fit.success:a.update(status="STOP_OPTIMIZER",optimizer=diag);return a
                sc[te,j]=-np.logaddexp(0,-(xe@fit.x))
        ss=weights(te)@sc[te]
        fs.append({"fold":k+1,"comparisons":int(te.sum()),"blocks":int(len(np.unique(block[te]))),"scores":dict(zip(names,map(float,ss))),"optimizers":diag})
        print("BASELINE_CHALLENGE_FOLD",mode,k+1,flush=True)
    w=weights(mask);mean=w@sc[mask]
    bw=np.bincount(block[mask],weights=w,minlength=len(blocks));scores=np.column_stack([np.bincount(block[mask],weights=w*sc[mask,j],minlength=len(blocks)) for j in range(len(names))])
    scores=scores[live]/bw[live,None]
    assert np.allclose(scores.mean(0),mean)
    boot=np.random.default_rng(20261126).integers(0,len(live),size=(10000,len(live)))
    def contrast(x,y):
        v=scores[:,names.index(x)]-scores[:,names.index(y)];g=float(v.mean());omit=(v.sum()-v)/(len(v)-1)
        fold_g=[v["scores"][x]-v["scores"][y] for v in fs]
        return {"gain":g,"positive_blocks":int((v>0).sum()),"fold_gains":fold_g,"positive_folds":sum(x>0 for x in fold_g),"delete_one_block_range":[float(omit.min()),float(omit.max())],"conditional_block_bootstrap_95":np.quantile(v[boot].mean(1),[.025,.975]).tolist(),"block_gains":v.tolist(),"screen":bool(g>0 and sum(x>0 for x in fold_g)>=4 and omit.min()>0)}
    gains={n+"_R50":contrast(n+"+R50",n) for n in configs}
    a.update(status="COMPLETE_DESCRIPTIVE_ONLY",scores=dict(zip(names,map(float,mean))),gains=gains,folds=fs,block_scores=[{"original_block":b+1,"original_fold":b%5+1,"scores":dict(zip(names,map(float,scores[i])))} for i,b in enumerate(live)])
    if "TL" in configs:
        old=gains["B_R50"]["gain"];new=gains["TL_R50"]["gain"]
        a["full_baseline_primary"]=gains["TL_R50"]
        a["attenuation_absolute"]=old-new
        a["attenuation_fraction"]=(old-new)/old if old>0 else None
    return a
try:
    t=ct.terrain_support.to_numpy(bool);l=ct.leaf_support.to_numpy(bool)
    report["full_challenge"]=run("full",t&l,{"T":base+terrain,"L":base+leaf,"TL":base+terrain+leaf})
    if report["full_challenge"]["status"]!="COMPLETE_DESCRIPTIVE_ONLY":
        # Separate partial diagnostic, never a replacement for full baseline.
        report["terrain_only_diagnostic"]=run("terrain_only",t,{"T":base+terrain})
        report["leaf_only_diagnostic"]=run("leaf_only",l,{"L":base+leaf})
    report["status"]="FULL_BASELINE_CHALLENGE_COMPLETE" if report["full_challenge"]["status"]=="COMPLETE_DESCRIPTIVE_ONLY" else "FULL_BASELINE_NOT_ADMITTED"
    save()
except Exception as e:
    report.update(status="STOP",error=type(e).__name__+": "+str(e)[:200]);save();raise
