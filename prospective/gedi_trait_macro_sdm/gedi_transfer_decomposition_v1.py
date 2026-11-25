"""Frozen paired comparison: R50 beyond leaf composition and topography."""
import hashlib,itertools,json,math,pathlib,sys
import numpy as np,pandas as pd
from scipy.special import expit
from scipy.optimize import minimize
ALT=True
OUT=pathlib.Path("gedi_transfer_decomposition");OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
PIN="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
assert sha(SRC)==PIN
K=["cell_x","cell_y"];G=["dataset_key","year","bx","by"]
roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
base=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{v}_fraction" for v in [10,20,30,40,50]],"GVSM_area_mean_RH98_m"]
terrain=["surface_elev_mean_m","surface_elev_sd_m"];leaf=["lc100_broadleaf_class_fraction","lc100_needleleaf_class_fraction","lc100_mixed_class_fraction","lc100_other_forest_class_fraction"] if ALT else ["broadleaf_fraction","conifer_fraction"]
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
# New measured-profile sensitivity, frozen before source access.
report={"status":"START","original_comparisons":len(z),"original_blocks":len(blocks),"source_doi":"10.3334/ORNLDAAC/2339","main_sdm_admitted":False}
def save():
    # JSON conversion only; retain the original numeric arrays and fit settings.
    def scalar(v):
        if isinstance(v,np.generic):return v.item()
        if isinstance(v,np.ndarray):return v.tolist()
        raise TypeError(type(v).__name__)
    raw=json.dumps(report,indent=2,allow_nan=False,default=scalar)
    (OUT/"report.json").write_text(raw+"\n")
    print("GEDI_MATCHED_FIT",report["status"],flush=True)
    print("GEDI_MATCHED_REPORT="+json.dumps(report,allow_nan=False,default=scalar),flush=True)
for mode,cols in [("terrain",terrain),("leaf",leaf)]:
    p=pathlib.Path(("baseline_lc100" if mode=="leaf" else "baseline_terrain")+"/report.json")
    a=json.loads(p.read_text());q=p.parent/"cell_covariates.csv.gz"
    assert sha(q)==a["output_sha256"]
    if mode=="terrain":assert a["output_sha256"]=="0b24b047ad6ce0209b0de93dc3e8fa3aae4c78078d69d40d9a6991530ed65d43"
    else:assert a["source_variant"]=="LC100_2019_DISCRETE_NOT_DLT"
    v=pd.read_csv(q);assert len(v)==1796 and not v.duplicated(K).any()
    ct=ct.merge(v[K+cols+[mode+"_support"]],on=K,validate="one_to_one",how="left")
    ct[mode+"_support"]=yes(ct[mode+"_support"])&np.isfinite(ct[cols]).all(1)
p=pathlib.Path("gedi_grid/cell_gedi_profiles.csv.gz");receipt=json.loads(p.with_name("receipt.json").read_text())
assert receipt["status"]=="GRID_PROFILE_SUPPORT_READY" and sha(p)==receipt["output_sha256"]
v=pd.read_csv(p);assert len(v)==1796 and not v.duplicated(K).any()
extra=["rh-98-a0","pai-a0","cover-a0"];profile="PAVD_lower_fraction"
ct=ct.merge(v[K+extra+[profile,"gedi_support"]],on=K,validate="one_to_one",how="left")
assert ct.cell_index.tolist()==list(range(1796))
raw_names=base+terrain+leaf+extra+["R50",profile]
raw=ct[raw_names].to_numpy(float)
valid=ct.terrain_support&ct.leaf_support&yes(ct.gedi_support)&np.isfinite(raw).all(1)
mask=valid.to_numpy()[ca]&valid.to_numpy()[cb];live=sorted(set(block[mask]))
def taxa(m):return set(np.r_[sa[m],sb[m]])
tax=taxa(mask);report.update(eligible_cells=int(valid.sum()),matched_pairs=int(mask.sum()),blocks=len(live),taxa=len(tax),fold_blocks=[int(sum(b%5==k for b in live)) for k in range(5)])
if len(live)<20 or min(report["fold_blocks"])<4 or len(tax)<10 or any(taxa(mask&(fold!=k))!=tax for k in range(5)):
    report["status"]="STOP_INSUFFICIENT_MATCHED_SUPPORT";save();sys.exit(0)
A=np.eye(nsp)[sa]-np.eye(nsp)[sb];D=A@P;trait=A@az
def weights(m):
    gn=np.bincount(gi[m],minlength=len(gb));bc=np.bincount(gbi[gn>0],minlength=len(blocks));return 1/(bc[block[m]]*gn[gi[m]]*len(np.unique(block[m])))
def objective(b,X,w):
    h=X@b;return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
# Fixed support and strict source-by-geography transfer. No refitting of shape axes.
R=pathlib.Path(__file__).resolve().parent
prior=json.loads((R/"GEDI_AUTHENTICATED_MEASURED_RECEIPT_V1.json").read_text())
assert sha(pathlib.Path("gedi_grid/cell_gedi_profiles.csv.gz"))==prior["grid"]["output_sha256"]
assert (int(valid.sum()),int(mask.sum()),len(live),len(tax))==(1587,28284,48,14)
legacy=json.loads((R/"ADJUSTED_SOURCE_BLOCK_HOLDOUT_RECEIPT_V1.json").read_text())
assert legacy["status"]=="ADJUSTED_STRICT_COMPLETE_DESCRIPTIVE_ONLY"
expected={v["fold"]:v for v in legacy["intersections"]};assert len(expected)==15
source_names=sorted(set(gs),key=lambda s:hashlib.sha256(s.encode()).hexdigest());si={s:i for i,s in enumerate(source_names)}
src=np.array([si[s] for s in gs])[gi];sf=src%5
names=["neutral","TLG","TLG+R50","TLG+PAVD","TLG+R50+PAVD"]
def fit(tr,te):
    assert not np.any(tr&te)
    used=np.unique(np.r_[ca[tr],cb[tr]]);mu=raw[used].mean(0);sd=raw[used].std(0);zero=sd<=1e-12;sd[zero]=1
    X=(raw-mu)/sd;X[:,zero]=0;diff=X[ca]-X[cb];b=diff[:,:-2]
    Y=np.column_stack([(D[:,:,None]*b[:,None,:]).reshape(len(z),-1),trait[:,None]*b])
    r=A*diff[:,-2,None];p=A*diff[:,-1,None]
    scored=[np.full(int(te.sum()),-math.log(2))];coef=None;opts=[]
    for j,xx in enumerate([Y,np.column_stack([Y,r]),np.column_stack([Y,p]),np.column_stack([Y,r,p])],1):
        xt=np.ascontiguousarray(xx[tr]);xe=np.ascontiguousarray(xx[te]);w=weights(tr)
        sol=minimize(objective,np.zeros(xt.shape[1]),args=(xt,w),jac=True,method="L-BFGS-B",options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
        opts.append({"model":names[j],"success":bool(sol.success),"iterations":int(sol.nit)})
        if not sol.success:raise RuntimeError("optimizer failure "+names[j])
        scored.append(-np.logaddexp(0,-xe@sol.x))
        if j==4:
            cr=sol.x[-2*nsp:-nsp]/sd[-2]*.1;cp=sol.x[-nsp:]/sd[-1]*.1
            if zero[-2]:cr[:]=0
            if zero[-1]:cp[:]=0
            coef={"r50_per_0.1":cr.tolist(),"pavd_fraction_per_0.1":cp.tolist()}
            assert abs(cr.sum())<1e-8 and abs(cp.sum())<1e-8
    sc=np.column_stack(scored)
    return sc,dict(zip(names,map(float,weights(te)@sc))),coef,opts
def summarize(sc,usable,folds):
    w=weights(usable);bw=np.bincount(block[usable],weights=w,minlength=len(blocks));bb=np.flatnonzero(bw>0)
    bs=np.column_stack([np.bincount(block[usable],weights=w*sc[usable,j],minlength=len(blocks)) for j in range(len(names))])[bb]/bw[bb,None]
    assert np.allclose(bs.mean(0),w@sc[usable])
    boot=np.random.default_rng(20261126).integers(0,len(bb),size=(10000,len(bb)))
    contrasts={}
    for a,b in [(names[3],names[1]),(names[2],names[1]),(names[4],names[2]),(names[4],names[3]),(names[4],names[1])]:
        dd=bs[:,names.index(a)]-bs[:,names.index(b)];fg=[v["scores"][a]-v["scores"][b] for v in folds];omit=(dd.sum()-dd)/(len(dd)-1)
        contrasts[a+" minus "+b]={"gain":float(dd.mean()),"positive_blocks":int((dd>0).sum()),"positive_intersections":sum(x>0 for x in fg),"intersection_gains":fg,"delete_one_block_range":[float(omit.min()),float(omit.max())],"conditional_block_bootstrap_95":np.quantile(dd[boot].mean(1),[.025,.975]).tolist(),"block_gains":dd.tolist(),"screen":bool(dd.mean()>0 and sum(x>0 for x in fg)>=math.ceil(.8*len(fg)) and omit.min()>0)}
    return {"comparisons":int(usable.sum()),"blocks":len(bb),"providers":int(np.unique(src[usable]).size),"taxa":len(taxa(usable)),"scores":dict(zip(names,map(float,bs.mean(0)))),"contrasts":contrasts,"splits":folds}
# Identical test rows for three transfer regimes, no feature/penalty tuning.
strict_prior=json.loads((R/"GEDI_STRICT_SOURCE_BLOCK_RECEIPT_V1.json").read_text())
assert strict_prior["status"]=="COMPLETE_DESCRIPTIVE_ONLY"
omitted={v["fold"] for v in strict_prior["omitted"]}
assert len(omitted)==2
modes=["geography_only","provider_only","both"]
scs={m:np.full((len(z),len(names)),np.nan) for m in modes}
folds={m:[] for m in modes}
for k in range(5):
    for h in range(5):
        label=f"block{k+1}_source{h+1}"
        if label not in expected or label in omitted:continue
        te=mask&(fold==k)&(sf==h)
        train={"geography_only":mask&(fold!=k),"provider_only":mask&(sf!=h),"both":mask&(fold!=k)&(sf!=h)}
        for m in modes:
            tr=train[m]
            assert not np.any(tr&te) and taxa(te)<=taxa(tr)
            if m!="provider_only":assert not(set(block[tr])&set(block[te]))
            if m!="geography_only":assert not(set(src[tr])&set(src[te]))
            x,ss,co,opts=fit(tr,te)
            scs[m][te]=x
            train_cells=set(np.r_[ca[tr],cb[tr]]);test_cells=set(np.r_[ca[te],cb[te]])
            folds[m].append({"fold":label,"scores":ss,"train_pairs":int(tr.sum()),"test_pairs":int(te.sum()),"train_blocks":int(np.unique(block[tr]).size),"test_blocks":int(np.unique(block[te]).size),"shared_blocks":len(set(block[tr])&set(block[te])),"shared_providers":len(set(src[tr])&set(src[te])),"shared_cells":len(train_cells&test_cells)})
        print("GEDI_TRANSFER_DECOMP_SPLIT",label,flush=True)
usable=np.isfinite(scs["both"]).all(1)
assert (int(usable.sum()),len(np.unique(block[usable])),len(np.unique(src[usable])),len(taxa(usable)))==(20327,44,28,14)
assert all(np.array_equal(np.isfinite(scs[m]).all(1),usable) for m in modes)
out={m:summarize(scs[m],usable,folds[m]) for m in modes}
for n in names:assert abs(out["both"]["scores"][n]-strict_prior["strict"]["scores"][n])<1e-7,(n,out["both"]["scores"][n])
for v in strict_prior["contrasts"]:assert abs(out["both"]["contrasts"][v["contrast"]]["gain"]-v["gain"])<1e-7
w=weights(usable);bw=np.bincount(block[usable],weights=w,minlength=len(blocks));bb=np.flatnonzero(bw>0)
def perblock(d):return np.bincount(block[usable],weights=w*d,minlength=len(blocks))[bb]/bw[bb]
boot=np.random.default_rng(20261126).integers(0,len(bb),size=(10000,len(bb)))
changes={}
for a,b in [("geography_only","both"),("provider_only","both"),("geography_only","provider_only")]:
    dd=(scs[a][usable,4]-scs[a][usable,2])-(scs[b][usable,4]-scs[b][usable,2])
    q=perblock(dd);om=(q.sum()-q)/(len(q)-1)
    changes[a+" minus "+b]={"gain_difference":float(q.mean()),"positive_blocks":int((q>0).sum()),"delete_one_block_range":[float(om.min()),float(om.max())],"conditional_block_bootstrap_95":np.quantile(q[boot].mean(1),[.025,.975]).tolist()}
report.update(status="COMPLETE_DESCRIPTIVE_ONLY",stage="post-result transfer failure decomposition",strict_scores_replayed=True,matched_comparisons=int(usable.sum()),matched_blocks=len(bb),matched_providers=int(np.unique(src[usable]).size),modes=out,paired_changes=changes,limits=["Same test rows but training sizes and support differ. Not a causal decomposition of observation bias.","Provider-only permits same region and cells in training; optimistic diagnostic, not spatial generalization.","Geography-only permits same data providers in training; both excludes source ID and block fold, but not measurement-method bias.","All results post-pilot on the same archive; no extra model choice or tuning."])
save()
for m,v in out.items():
    print("GEDI_DECOMP_MODE="+json.dumps({"mode":m,**{k:v[k] for k in ["comparisons","blocks","providers","taxa","scores"]},"contrasts":{k:{a:b for a,b in vv.items() if a!="block_gains"} for k,vv in v["contrasts"].items()},"splits":v["splits"]}),flush=True)
print("GEDI_DECOMP_CHANGES="+json.dumps(changes),flush=True)
