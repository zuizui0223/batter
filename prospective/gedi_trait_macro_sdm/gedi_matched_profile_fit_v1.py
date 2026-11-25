"""Frozen paired comparison: R50 beyond leaf composition and topography."""
import hashlib,itertools,json,math,pathlib,sys
import numpy as np,pandas as pd
from scipy.special import expit
from scipy.optimize import minimize
ALT=True
OUT=pathlib.Path("gedi_matched_fit");OUT.mkdir(exist_ok=True)
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
names=["neutral","TLG","TLG+R50","TLG+PAVD","TLG+R50+PAVD"];sc=np.full((len(z),len(names)),np.nan);sc[mask,0]=-math.log(2)
folds=[]
for k in range(5):
    tr=mask&(fold!=k);te=mask&(fold==k);used=np.unique(np.r_[ca[tr],cb[tr]])
    mu=raw[used].mean(0);sd=raw[used].std(0);zero=sd<=1e-12;sd[zero]=1
    X=(raw-mu)/sd;X[:,zero]=0;diff=X[ca]-X[cb];b=diff[:,:-2]
    Y=np.column_stack([(D[:,:,None]*b[:,None,:]).reshape(len(z),-1),trait[:,None]*b])
    r=A*diff[:,-2,None];p=A*diff[:,-1,None]
    for j,features_ in enumerate([Y,np.column_stack([Y,r]),np.column_stack([Y,p]),np.column_stack([Y,r,p])],1):
        xt=np.ascontiguousarray(features_[tr]);xe=np.ascontiguousarray(features_[te]);w=weights(tr)
        sol=minimize(objective,np.zeros(xt.shape[1]),args=(xt,w),jac=True,method="L-BFGS-B",options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
        if not sol.success:report.update(status="STOP_OPTIMIZER",fold=k+1,model=names[j]);save();sys.exit(1)
        sc[te,j]=-np.logaddexp(0,-xe@sol.x)
    folds.append(dict(zip(names,map(float,weights(te)@sc[te]))))
    print("GEDI_FIT_FOLD",k+1,flush=True)
w=weights(mask);bw=np.bincount(block[mask],weights=w,minlength=len(blocks))
bs=np.column_stack([np.bincount(block[mask],weights=w*sc[mask,j],minlength=len(blocks)) for j in range(len(names))])[live]/bw[live,None]
contrasts={}
for a,b in [("TLG+PAVD","TLG"),("TLG+R50","TLG"),("TLG+PAVD","TLG+R50"),("TLG+R50+PAVD","TLG+R50")]:
    d=bs[:,names.index(a)]-bs[:,names.index(b)];fd=[x[a]-x[b] for x in folds];omit=(d.sum()-d)/(len(d)-1)
    contrasts[a+" minus "+b]={"gain":float(d.mean()),"positive_blocks":int((d>0).sum()),"positive_folds":int(sum(x>0 for x in fd)),"fold_gains":fd,"delete_one_block_range":[float(omit.min()),float(omit.max())],"block_gains":d.tolist()}
report.update(status="COMPLETE_DESCRIPTIVE_ONLY",scores=dict(zip(names,map(float,bs.mean(0)))),fold_scores=folds,contrasts=contrasts,primary="TLG+PAVD minus TLG",limits=["Same source-year conditional label allocation, not occupancy or flight height.","Post-pilot matched sensitivity; not independent biological replication.","GEDI gridded shot means, not continuous canopy volume or random complete census."])
save()
