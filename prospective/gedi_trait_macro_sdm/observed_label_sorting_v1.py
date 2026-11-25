"""Frozen source-conditioned recorded-label sorting pilot, not a biological SDM."""
import hashlib,itertools,json,pathlib,collections,math
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize

SRC=pathlib.Path("common_forest/species_cell_source_year_environment.csv.gz")
OUT=pathlib.Path("observed_label_sorting");OUT.mkdir(exist_ok=True)
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
comparisons=[];groups=[];gblock=[];sizes=[]
for key,part in f.groupby(G,sort=True):
    by={s:np.sort(v.cell_index.unique()) for s,v in part.groupby("species_key",sort=True)}
    for s,t in itertools.combinations(sorted(by),2):
        a,b=by[s],by[t]
        ca=np.repeat(a,len(b));cb=np.tile(b,len(a))
        keep=ca!=cb;ca,cb=ca[keep],cb[keep]
        if len(ca)==0:continue
        if len(ca)>128:
            sel=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[sel],cb[sel]
        g=len(groups);block=(int(key[2]),int(key[3]));groups.append(g);gblock.append(block);sizes.append(len(ca))
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
report={"stage":"observed label sorting pilot, not an SDM or causal inference","source_sha256":PIN,"seed":20261125,"roster_size":nsp,"recorded_cells_used":int(ct.shape[0]),"source_year_block_strata":int(f[G].drop_duplicates().shape[0]),"comparisons":npair,"pair_stratum_groups":ng,"blocks":nb,"fold_blocks":[int(np.sum(np.arange(nb)%5==i)) for i in range(5)],"contributing_taxa":int(len(np.unique(np.r_[sa,sb]))),"baseline_features":baseline,"profile_feature":"R50=area-mean RH50 / area-mean RH98","main_sdm_admitted":False,"limitations":["Composite conditional score on recorded labels and recorded cells; nonreported labels are not absences.","Same source/year/block does not establish common effort or species detection.","Same taxa in training/test, no cross-region/source/species transfer claim.","No terrain/roost/effort model, DOI-pinned download or calibrated 3D use."]}
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("LABEL_SORTING_REPORT="+json.dumps(report,allow_nan=False),flush=True)
if nb<20 or min(report["fold_blocks"])<4 or report["contributing_taxa"]<10 or any(set(np.r_[sa[fold!=k],sb[fold!=k]])!=set(np.r_[sa,sb]) for k in range(5)):
    report["status"]="STOP_INSUFFICIENT_PAIR_SUPPORT";save();raise SystemExit(0)
A=np.eye(nsp)[sa]-np.eye(nsp)[sb];D=A@P;trait=A@az
raw=ct[features].to_numpy(float)
def design(train):
    cells=np.unique(np.r_[ca[train],cb[train]])
    mu=raw[cells].mean(axis=0);sd=raw[cells].std(axis=0);zero=sd<=1e-12;sd[zero]=1
    X=(raw-mu)/sd;X[:,zero]=0
    diff=X[ca]-X[cb]
    B=diff[:,:len(baseline)]
    Y=np.column_stack([(D[:,:,None]*B[:,None,:]).reshape(len(z),-1),trait[:,None]*B])
    r=diff[:,-1]
    return [Y,np.column_stack([Y,A*r[:,None]]),np.column_stack([Y,D*r[:,None],trait*r])],int(zero.sum())
def obj(b,X,w):
    h=X@b
    return float(w@np.logaddexp(0,-h)+.1*(b@b)), X.T@(-w*expit(-h))+.2*b
# Synthetic numerical checks for swap symmetry and gradient.
X=np.array([[1.,-2.],[.3,.1],[-1.,.5]]);w=np.array([.2,.3,.5]);p=np.array([.4,-.2])
v,g=obj(p,X,w);eps=1e-6
num=np.array([(obj(p+eps*np.eye(2)[k],X,w)[0]-obj(p-eps*np.eye(2)[k],X,w)[0])/(2*eps) for k in range(2)])
assert np.max(np.abs(g-num))<1e-7
h=X@p
assert np.max(np.abs(expit(h)+expit(-h)-1))<1e-12
assert np.max(np.abs(A+(-A)))==0 and np.max(np.abs(D+(-A)@P))<1e-12
report["checks"]={"gradient_max_abs_error":float(np.max(np.abs(g-num))),"orientation_probability_sum":True,"trait_orthogonal_residual":True,"equal_block_weights":True}
scores=np.full((len(z),4),np.nan);scores[:,0]=-math.log(2)
fold_reports=[]
for k in range(5):
    tr=fold!=k;te=~tr
    W=w0[tr]/np.unique(block[tr]).size
    assert np.isclose(W.sum(),1)
    matrices,zero=design(tr);fr={"fold":k+1,"test_blocks":int(np.unique(block[te]).size),"test_comparisons":int(te.sum()),"train_zero_variance_features":zero,"optimizers":[]}
    for m,X in enumerate(matrices,1):
        xt=np.ascontiguousarray(X[tr]);xe=np.ascontiguousarray(X[te])
        fit=minimize(obj,np.zeros(X.shape[1]),args=(xt,W),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
        fr["optimizers"].append({"model":f"B{m}","success":bool(fit.success),"iterations":int(fit.nit),"max_abs_gradient":float(np.max(np.abs(fit.jac)))})
        if not fit.success:
            report["status"]="STOP_OPTIMIZER";report["folds"]=fold_reports+[fr];save();raise SystemExit(0)
        scores[te,m]=-np.logaddexp(0,-(xe@fit.x))
        if m==3:fr["gamma_AR_profile"]=float(fit.x[-1])
    ss=np.average(scores[te],axis=0,weights=w0[te])
    fr["scores"]={f"B{m}":float(x) for m,x in enumerate(ss)}
    fr["B1_B0"]=float(ss[1]-ss[0]);fr["B2_B1"]=float(ss[2]-ss[1]);fr["B3_B2"]=float(ss[3]-ss[2]);fr["B3_B1"]=float(ss[3]-ss[1])
    fold_reports.append(fr)
    print("FOLD_COMPLETE="+json.dumps(fr),flush=True)
assert np.isfinite(scores).all()
bs=np.column_stack([np.bincount(block,weights=w0*scores[:,m],minlength=nb) for m in range(4)])
diff=bs[:,3]-bs[:,1];sm=bs.mean(axis=0)
omit=(diff.sum()-diff)/(nb-1);gamma=[x["gamma_AR_profile"] for x in fold_reports]
report.update({"status":"PILOT_COMPLETE_DESCRIPTIVE_ONLY","folds":fold_reports,"mean_block_scores":{f"B{m}":float(x) for m,x in enumerate(sm)},"gains":{"B1_B0":float(sm[1]-sm[0]),"B2_B1":float(sm[2]-sm[1]),"B3_B2":float(sm[3]-sm[2]),"B3_B1":float(sm[3]-sm[1])},"positive_folds_primary":sum(x["B3_B1"]>0 for x in fold_reports),"positive_blocks_primary":int((diff>0).sum()),"omission_mean_range":[float(omit.min()),float(omit.max())],"gamma_range":[float(min(gamma)),float(max(gamma))],"gamma_median":float(np.median(gamma)),"block_scores":[{"block":i+1,"fold":i%5+1,"B0":float(v[0]),"B1":float(v[1]),"B2":float(v[2]),"B3":float(v[3]),"B3_B1":float(v[3]-v[1])} for i,v in enumerate(bs)]})
report["directional_screen"]=bool(diff.mean()>0 and report["positive_folds_primary"]>=4 and omit.min()>0 and np.median(gamma)>0)
save()
