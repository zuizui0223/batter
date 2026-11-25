"""Frozen source-conditioned recorded-label sorting pilot, not a biological SDM."""
import hashlib,itertools,json,pathlib,collections,math
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize

SRC=pathlib.Path("common_forest/species_cell_source_year_environment.csv.gz")
OUT=pathlib.Path("sorting_transfer_diagnostic");OUT.mkdir(exist_ok=True)
PIN="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==PIN
d=pd.read_csv(SRC,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
K=["cell_x","cell_y"];SK=["species_key",*K];G=["dataset_key","year","bx","by"]
roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
baseline=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{i}_fraction" for i in [10,20,30,40,50]],"GVSM_area_mean_RH98_m"]
features=baseline+["R50"]
assert int(d.records.sum())==20784 and len(d[SK].drop_duplicates())==4854
f=d.loc[d.forest_profile_support.astype(str).str.lower().eq("true")].copy()
assert int(f.records.sum())==8811 and len(f[SK].drop_duplicates())==2977
geo=[]
for k,v in f[SK].drop_duplicates().groupby("species_key"):
    b=v.groupby([v.cell_x//200,v.cell_y//200]).size()
    if len(v)>=30 and b.ge(5).sum()>=4:geo.append(k)
assert sorted(geo)==roster
f=f[f.species_key.isin(roster)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")].copy()
assert (f.bx==f.cell_x//200).all() and (f.by==f.cell_y//200).all()
f[features+["AR"]]=f[features+["AR"]].apply(pd.to_numeric,errors="raise")
assert np.isfinite(f[features+["AR"]].to_numpy()).all()
ct=f[K+features].drop_duplicates().sort_values(K).reset_index(drop=True)
assert not ct.duplicated(K).any()
ar=f[["species_key","AR"]].drop_duplicates().set_index("species_key").loc[roster,"AR"].to_numpy(float)
assert len(ar)==14 and np.std(ar)>0
az=(ar-ar.mean())/ar.std()
# Residual parameterization: species deviations orthogonal to constant and trait.
nsp=len(roster);P=np.eye(nsp)-np.ones((nsp,nsp))/nsp-np.outer(az,az)/nsp
assert np.max(np.abs(P@az))<1e-10 and np.max(np.abs(P@P-P))<1e-10
idx={k:i for i,k in enumerate(roster)}
ct["cell_index"]=np.arange(len(ct))
f=f.merge(ct[K+["cell_index"]],on=K,validate="many_to_one")
f=f.drop_duplicates(["species_key","cell_index",*G]).sort_values([*G,"species_key","cell_index"])
rng=np.random.default_rng(20261125)
comparisons=[];groups=[];gblock=[];gsource=[];sizes=[]
for key,part in f.groupby(G,sort=True):
    by={s:np.sort(v.cell_index.unique()) for s,v in part.groupby("species_key",sort=True)}
    for s,t in itertools.combinations(sorted(by),2):
        a,b=by[s],by[t]
        ca=np.repeat(a,len(b));cb=np.tile(b,len(a))
        keep=ca!=cb;ca,cb=ca[keep],cb[keep]
        if len(ca)==0:continue
        if len(ca)>128:
            sel=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[sel],cb[sel]
        g=len(groups);block=(int(key[2]),int(key[3]));groups.append(g);gblock.append(block);gsource.append(str(key[0]));sizes.append(len(ca))
        comparisons.extend((idx[s],idx[t],int(x),int(y),g) for x,y in zip(ca,cb))
assert comparisons
z=np.asarray(comparisons,dtype=int);sa,sb,ca,cb,gi=z.T
# Anonymize output block order with fixed hash; no geographic labels saved.
blocks=sorted(set(gblock),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
bi={b:i for i,b in enumerate(blocks)};gb=np.array([bi[b] for b in gblock]);block=gb[gi]
fold=block%5;ng=len(groups);nb=len(blocks);npair=len(z)
size=np.asarray(sizes);groups_per_block=np.bincount(gb,minlength=nb)
w0=1.0/(groups_per_block[block]*size[gi])
assert np.allclose(np.bincount(block,weights=w0,minlength=nb),1)

# Diagnostic, after original pilot: no new hypothesis or primary S1 admission.
# B2 versus B3 in the original is a full-space reparameterization with different ridge penalty.
# Direct trait-only model is needed for prediction to entirely untrained taxa.
source_names=sorted(set(gsource),key=lambda s:hashlib.sha256(s.encode()).hexdigest())
si={s:i for i,s in enumerate(source_names)}
src_group=np.array([si[s] for s in gsource]);src=src_group[gi];sf=src%5
A=np.eye(nsp)[sa]-np.eye(nsp)[sb];D=A@P;trait=A@az
raw=ct[features].to_numpy(float)
report={"stage":"post-pilot robustness and cold-start diagnostic only","original_source_sha256":PIN,"comparisons":len(z),"blocks":nb,"sources":len(source_names),"species":nsp,"primary_sdm_admitted":False,"warning":"Not independent replication of the original pilot; record label prediction conditional on observed source-year-block cells. B2/B3 same slope span, different shrinkage."}
def weights(mask):
    blockn=np.bincount(block[mask],minlength=nb)
    gn=np.bincount(gi[mask],minlength=ng)
    group_live=gn>0
    perblock=np.bincount(gb[group_live],minlength=nb)
    v=1/(perblock[block[mask]]*gn[gi[mask]])
    return v/np.unique(block[mask]).size
def matrices(train,kind):
    cs=np.unique(np.r_[ca[train],cb[train]]);mu=raw[cs].mean(axis=0);sd=raw[cs].std(axis=0);zero=sd<=1e-12;sd[zero]=1
    X=(raw-mu)/sd;X[:,zero]=0
    diff=X[ca]-X[cb];B=diff[:,:len(baseline)];R=diff[:,-1]
    if kind=="trait":
        # No estimated species intercepts/slopes. Use only numeric AR, scaled from training taxa.
        used=np.unique(np.r_[sa[train],sb[train]])
        scale=np.std(ar[used])
        if not scale>0:raise ValueError("constant training AR")
        tt=(ar[sa]-ar[sb])/scale
        base=tt[:,None]*B
        return [base,np.column_stack([base,tt*R])]
    base=np.column_stack([(D[:,:,None]*B[:,None,:]).reshape(len(z),-1),trait[:,None]*B])
    return [base,np.column_stack([base,A*R[:,None]])]
def objective(b,X,w):
    h=X@b
    return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
def evaluate(train,test,kind):
    assert not np.any(train&test)
    if train.sum()<300 or test.sum()<10 or len(np.unique(block[train]))<10 or len(np.unique(block[test]))<3:return None
    Xs=matrices(train,kind);w=weights(train)
    assert np.isclose(w.sum(),1)
    score=[]
    for X in Xs:
        Xtr=np.ascontiguousarray(X[train]);Xe=np.ascontiguousarray(X[test])
        fit=minimize(objective,np.zeros(X.shape[1]),args=(Xtr,w),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
        if not fit.success:return None
        score.append(-np.logaddexp(0,-(Xe@fit.x)))
    return np.stack(score,axis=1)
def summarize(name,results):
    sc=np.full((len(z),2),np.nan)
    fold_summaries=[]
    for label,te,x in results:
        if x is None:continue
        assert not np.isfinite(sc[te]).any()
        sc[te]=x
        ww=weights(te);v=ww@x
        fold_summaries.append({"fold":label,"comparisons":int(te.sum()),"blocks":int(len(np.unique(block[te]))),"sources":int(len(np.unique(src[te]))),"score_baseline":float(v[0]),"score_profile":float(v[1]),"gain":float(v[1]-v[0])})
    valid=np.isfinite(sc).all(axis=1)
    if not valid.any():return {"name":name,"status":"INSUFFICIENT_SUPPORT"}
    ww=weights(valid);s=ww@sc[valid]
    b=block[valid];d=sc[valid,1]-sc[valid,0];ws=ww
    bs=np.bincount(b,weights=d*ws,minlength=nb);wblock=np.bincount(b,weights=ws,minlength=nb);support=wblock>0
    block_gain=bs[support]/wblock[support]
    # Descriptive spread, no naive independent comparison-level p-values.
    return {"name":name,"status":"DIAGNOSTIC_COMPLETE","coverage":float(valid.mean()),"n_scored":int(valid.sum()),"scored_blocks":int(support.sum()),"scored_sources":int(len(np.unique(src[valid]))),"baseline":float(s[0]),"with_profile":float(s[1]),"gain":float(s[1]-s[0]),"positive_blocks":int((block_gain>0).sum()),"folds":fold_summaries,"block_gain_quantiles":np.quantile(block_gain,[.05,.5,.95]).tolist()}
# Each comparison evaluated at exactly one intersection of source and block folds;
# train excludes ALL data from held-out sources AND held-out geographic blocks.
strict=[]
for k in range(5):
    for h in range(5):
        te=(fold==k)&(sf==h);tr=(fold!=k)&(sf!=h)
        if set(np.r_[sa[te],sb[te]])-set(np.r_[sa[tr],sb[tr]]):continue
        strict.append((f"block{k+1}_source{h+1}",te,evaluate(tr,te,"flex")))
report["source_and_block_transfer"]=summarize("known species; both unseen source and geography",strict)
# For each pair of taxa, train only on comparisons containing neither test species.
# For every block fold, exclude all its rows as well. Each pair evaluated once per block fold.
# Entirely new taxa; AR-based coefficients only. No learned per-species slopes.
cold=[]
pairs=sorted(set(zip(sa,sb)))
for s,t in pairs:
    pair=(sa==s)&(sb==t)
    other=(sa!=s)&(sb!=s)&(sa!=t)&(sb!=t)
    for k in range(5):
        te=pair&(fold==k)
        if te.sum()<10 or len(np.unique(block[te]))<3:continue
        tr=other&(fold!=k)
        assert not set([s,t])&set(np.r_[sa[tr],sb[tr]])
        cold.append((f"{roster[s]}_{roster[t]}_block{k+1}",te,evaluate(tr,te,"trait")))
report["unseen_species_and_block_transfer"]=summarize("two unseen taxa and unseen block; AR-only coefficients",cold)
report["limitations"]=["All tests use the previously inspected 14-taxon archive; not independent replication.","Same-source/year/block records are not standardized common effort. No absences or occurrence probability.","Cold-start support subset is determined before model outcomes by minimum test comparisons and blocks; do not generalize to all pairs.","North/south, terrain, roost, dated snapshot and final S1 still separate. No validated 3D niche."]
(OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
print("TRANSFER_DIAGNOSTIC="+json.dumps(report,allow_nan=False),flush=True)
