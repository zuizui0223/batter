"""Adjusted strict provider/block sensitivity, original pair construction from blob 1ca160c5a1fe179e2f721ec3f4753a28a05d7e59."""
import hashlib,itertools,json,pathlib,collections,math
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize

SRC=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
OUT=pathlib.Path("adjusted_source_block");OUT.mkdir(exist_ok=True)
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

ROOT=pathlib.Path(__file__).resolve().parent
old=json.loads((ROOT/"OBSERVED_LABEL_TRANSFER_RECEIPT_V1.json").read_text())["source_and_block_transfer"]
receipt=json.loads((ROOT/"BASELINE_LC100_ALTERNATIVE_RECEIPT_V1.json").read_text())
assert receipt["status"]=="LC100_ALTERNATIVE_CHALLENGE_COMPLETE" and all(receipt["audit"]["checks"].values())
assert len(z)==31601 and nb==51 and len(ct)==1796 and nsp==14
terrain=["surface_elev_mean_m","surface_elev_sd_m"]
leaf=["lc100_broadleaf_class_fraction","lc100_needleleaf_class_fraction","lc100_mixed_class_fraction","lc100_other_forest_class_fraction"]
for mode,cols,p in [("terrain",terrain,pathlib.Path("prior_terrain/cell_covariates.csv.gz")),("leaf",leaf,pathlib.Path("prior_alternative/baseline_lc100/cell_covariates.csv.gz"))]:
    assert hashlib.sha256(p.read_bytes()).hexdigest()==receipt["source_reports"][mode]["output_sha256"]
    v=pd.read_csv(p)
    assert len(v)==1796 and not v.duplicated(K).any()
    assert v[mode+"_support"].astype(str).str.lower().eq("true").all()
    ct=ct.merge(v[K+cols],on=K,how="left",validate="one_to_one")
assert ct.cell_index.tolist()==list(range(1796))
raw_names=baseline+["R50"]+terrain+leaf
raw=ct[raw_names].to_numpy(float)
assert np.isfinite(raw).all()
configs={"B":baseline,"T":baseline+terrain,"L":baseline+leaf,"TL":baseline+terrain+leaf}
names=["neutral"]+[k+s for k in configs for s in ("","+R50")]
expected={v["fold"]:v for v in old["folds"]}
assert len(expected)==15
report.update(stage="adjusted original strict source/block holdout",status="START",original_DLT_challenge_admitted=False,original_SDM_admitted=False,full_covariate_cells=len(ct),source_reports={k:receipt["source_reports"][k]["output_sha256"] for k in ("terrain","leaf")},limits=["Same pilot source archive; not independent replication.","LC100 class-area fractions and DSM proxies, not DLT or bare-earth elevation.","No occupancy, altitude, causal vertical effect, or original primary SDM admission."])
def save():
    def scalar(v):
        if isinstance(v,np.generic):return v.item()
        raise TypeError("unsupported scalar "+type(v).__name__)
    s=json.dumps(report,indent=2,allow_nan=False,default=scalar)
    (OUT/"report.json").write_text(s+"\n")
    print("ADJUSTED_SOURCE_BLOCK_REPORT="+json.dumps(report,allow_nan=False,default=scalar),flush=True)
def objective(b,X,w):
    h=X@b
    return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
scores=np.full((len(z),len(names)),np.nan);splits=[]
try:
    for k in range(5):
        for h in range(5):
            label=f"block{k+1}_source{h+1}"
            if label not in expected:continue
            te=(fold==k)&(sf==h);tr=(fold!=k)&(sf!=h)
            assert not np.any(tr&te) and not set(block[tr])&set(block[te]) and not set(src[tr])&set(src[te])
            assert not(set(np.r_[sa[te],sb[te]])-set(np.r_[sa[tr],sb[tr]]))
            v=expected[label]
            assert (int(te.sum()),len(np.unique(block[te])),len(np.unique(src[te])))==(v["comparisons"],v["blocks"],v["sources"])
            assert tr.sum()>=300 and te.sum()>=10 and len(np.unique(block[tr]))>=10 and len(np.unique(block[te]))>=3
            assert not np.isfinite(scores[te]).any()
            used=np.unique(np.r_[ca[tr],cb[tr]])
            mu=raw[used].mean(0);sd=raw[used].std(0);zero=sd<=1e-12;sd[zero]=1
            X=(raw-mu)/sd;X[:,zero]=0;diff=X[ca]-X[cb];R=diff[:,raw_names.index("R50")]
            W=weights(tr);assert np.isclose(W.sum(),1)
            scores[te,0]=-math.log(2);diags=[]
            for n,cols in configs.items():
                B=diff[:,[raw_names.index(v) for v in cols]]
                Y=np.column_stack([(D[:,:,None]*B[:,None,:]).reshape(len(z),-1),trait[:,None]*B])
                for suffix,M in [("",Y),("+R50",np.column_stack([Y,A*R[:,None]]))]:
                    name=n+suffix
                    xt=np.ascontiguousarray(M[tr]);xe=np.ascontiguousarray(M[te])
                    sol=minimize(objective,np.zeros(xt.shape[1]),args=(xt,W),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
                    diags.append({"model":name,"success":bool(sol.success),"iterations":int(sol.nit),"max_abs_gradient":float(np.abs(sol.jac).max())})
                    if not sol.success:
                        report["optimizer_stop"]={"intersection":label,"optimizers":diags};raise ValueError("optimizer did not converge")
                    scores[te,names.index(name)]=-np.logaddexp(0,-xe@sol.x)
            m=dict(zip(names,map(float,weights(te)@scores[te])))
            assert abs(m["B"]-v["score_baseline"])<1e-7 and abs(m["B+R50"]-v["score_profile"])<1e-7, label
            splits.append({"fold":label,"comparisons":int(te.sum()),"blocks":len(np.unique(block[te])),"sources":len(np.unique(src[te])),"scores":m,"optimizers":diags})
            print("ADJUSTED_STRICT_INTERSECTION",label,flush=True)
    valid=np.isfinite(scores).all(1);assert len(splits)==15 and int(valid.sum())==29247 and len(np.unique(block[valid]))==48 and len(np.unique(src[valid]))==30
    w=weights(valid);m=dict(zip(names,map(float,w@scores[valid])))
    assert abs(m["B"]-old["baseline"])<1e-7 and abs(m["B+R50"]-old["with_profile"])<1e-7
    bw=np.bincount(block[valid],weights=w,minlength=nb)
    live=bw>0
    bs=np.column_stack([np.bincount(block[valid],weights=w*scores[valid,j],minlength=nb) for j in range(len(names))])[live]/bw[live,None]
    assert np.allclose(bs.mean(0),list(m.values()))
    boot=np.random.default_rng(20261126).integers(0,len(bs),size=(10000,len(bs)))
    gains={}
    for k in configs:
        x=k+"+R50";y=k
        v=bs[:,names.index(x)]-bs[:,names.index(y)]
        gain=float(v.mean());om=(v.sum()-v)/(len(v)-1)
        fg=[s["scores"][x]-s["scores"][y] for s in splits]
        gains[k+"_R50"]={"gain":gain,"positive_blocks":int((v>0).sum()),"positive_intersections":sum(q>0 for q in fg),"intersection_gains":fg,"block_gains":v.tolist(),"delete_one_block_range":[float(om.min()),float(om.max())],"conditional_block_bootstrap_95":np.quantile(v[boot].mean(1),[.025,.975]).tolist(),"screen":bool(gain>0 and sum(q>0 for q in fg)>=12 and om.min()>0)}
    report.update(status="ADJUSTED_STRICT_COMPLETE_DESCRIPTIVE_ONLY",scored_comparisons=int(valid.sum()),scored_blocks=int(live.sum()),scored_providers=len(np.unique(src[valid])),coverage=float(valid.mean()),original_replayed=True,scores=m,gains=gains,intersections=splits,block_scores=[{"original_block":int(i)+1,"scores":dict(zip(names,map(float,v)))} for i,v in zip(np.where(live)[0],bs)],remaining_fraction=gains["TL_R50"]["gain"]/gains["B_R50"]["gain"] if gains["B_R50"]["gain"]>0 else None)
    save()
except Exception as e:
    report.update(status="STOP",error=type(e).__name__+": "+str(e)[:200],completed_intersections=splits);save();raise
