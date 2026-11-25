"""Frozen local measured-structure diagnostic; no occupancy/altitude inference.
See DK15_MEASURED_PROFILE_DIAGNOSTIC_CONTRACT_V1.md.
"""
import collections,hashlib,itertools,json,pathlib
import numpy as np,pandas as pd
from scipy.special import expit
from scipy.optimize import minimize
OUT=pathlib.Path("dk15_profile_diagnostic");OUT.mkdir(exist_ok=True)
E=pathlib.Path("fixed_environment/all_bat_species_cell_source_year_environment.csv.gz")
F=pathlib.Path("observation/source_cell_year_observation_flags.csv.gz")
M=pathlib.Path("holdout/fixed_source_cell_year_holdout_masks.csv.gz")
D=pathlib.Path("ecodes/matched_ecodes_gvsm_cells.csv.gz")
pins={E:"85ad737229aa7b10720a8d5c8bd0ea389f63f908c37871c7ce46ae87c9bed1d6",F:"de971292065a8aee3491880adb00a5623efae61bc83b2bd2ae4d663b45edf0f0",M:"6796dcc358dd1990cb3cca25b95fe068b52cce7a979ff8602ce639c5708e4b96",D:"1a133c3932fd19aed8369c75544fd612bb11a18d06dbe99a3321b8fa1b8e2377"}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
for p,h in pins.items():assert sha(p)==h,str(p)
def read(p):
    return pd.read_csv(p,dtype={k:str for k in ["species","snapshot_species_key","legacy_gbif_species_key","dataset_key","year","license"]},keep_default_na=False,low_memory=False)
def boolean(d,k):
    z=d[k].astype(str).str.lower()
    assert z.isin(["true","false"]).all(),k
    return z.eq("true")
K=["cell_x","cell_y"];J=["species","snapshot_species_key",*K,"dataset_key","year","license"]
e,f,m,d=map(read,[E,F,M,D])
for a in [e,f,m]:assert a.records.sum()==219960 and not a.duplicated(J).any()
assert len(d)==909 and not d.duplicated(K).any()
measured=["ALS_valid_area_fraction","ALS_canopy_H95_m","ALS_all_return_mean_height_m","ALS_openness","ALS_mean_to_H95","R50"]
d[measured]=d[measured].apply(pd.to_numeric,errors="coerce")
d=d[d.ALS_valid_area_fraction.ge(.7)&d.ALS_canopy_H95_m.gt(5)&np.isfinite(d[measured]).all(axis=1)].copy()
assert len(d)==375
m=m[J+["records","archive_block_seen","archive_source_seen"]].rename(columns={"records":"mask_records"})
f=f[J+["records","flag_explicit_captive","flag_roost_context"]].rename(columns={"records":"flag_records"})
q=e.merge(m,on=J,validate="one_to_one").merge(f,on=J,validate="one_to_one")
assert len(q)==len(e) and q.records.eq(q.mask_records).all() and q.records.eq(q.flag_records).all()
assert q.flag_explicit_captive.sum()==0 and q.flag_roost_context.sum()==684
q["screened_records"]=q.records-q.flag_roost_context
q["species_key"]=q.legacy_gbif_species_key
matched=boolean(q,"provisional_trait_match")&q.species_key.ne("")
forest=boolean(q,"forest_profile_support")
a=q[matched&forest][["species_key",*K]].drop_duplicates()
taxa=[]
for s,v in a.groupby("species_key"):
    c=v.groupby([v.cell_x//200,v.cell_y//200]).size()
    if len(v)>=30 and c.ge(5).sum()>=4:taxa.append(s)
taxa=sorted(taxa);assert len(taxa)==20
unseen=~boolean(q,"archive_block_seen")&~boolean(q,"archive_source_seen")
north=boolean(q,"north_extrapolation")
q=q[matched&forest&unseen&north&q.screened_records.gt(0)&q.species_key.isin(taxa)&q.dataset_key.ne("")&q.year.str.fullmatch(r"20[0-9]{2}")].copy()
q=q.merge(d[K+["R50","ALS_canopy_H95_m","ALS_mean_to_H95"]].rename(columns={"R50":"checked_R50"}),on=K,validate="many_to_one")
q["R50"]=pd.to_numeric(q.R50,errors="raise")
assert np.allclose(q.R50,q.checked_R50,atol=1e-9,rtol=1e-8)
q["bx50"]=q.cell_x//50;q["by50"]=q.cell_y//50
base=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{i}_fraction" for i in [10,20,30,40,50]],"GVSM_area_mean_RH98_m","ALS_canopy_H95_m"]
feat=base+["R50","ALS_mean_to_H95"]
q[feat]=q[feat].apply(pd.to_numeric,errors="raise")
assert np.isfinite(q[feat]).all().all()
ct=q[K+feat].drop_duplicates().sort_values(K).reset_index(drop=True)
assert not ct.duplicated(K).any()
ct["cell_index"]=np.arange(len(ct))
G=["dataset_key","year","bx50","by50"]
q=q.merge(ct[K+["cell_index"]],on=K,validate="many_to_one")
q=q.drop_duplicates(["species_key","cell_index",*G]).sort_values([*G,"species_key","cell_index"])
report={"stage":"local measured versus predicted structure diagnostic; not occupancy or continental SDM","input_sha256":{str(k):v for k,v in pins.items()},"candidate_measured_cells":len(d),"matched_strict_northern_cells":len(ct),"matched_species":int(q.species_key.nunique()),"matched_species_cells":len(q[["species_key",*K]].drop_duplicates()),"matched_records_before_label_deduplication_note":"records are screened before source-year-cell-label deduplication; no abundance weights","source_year_block_strata":len(q[G].drop_duplicates()),"sources":int(q.dataset_key.nunique()),"status":"START","limitations":["2014–15 ALS vs 2020 GVSM; all-return mean/H95 and waveform RH50/RH98 are distinct proxies.","Strictly disjoint prior archive providers and 200km blocks; new local 50km CV diagnostic only.","Same provider/year/block does not equal common effort; no absence or altitude inference.","Known-taxon predictions only; no primary SDM admission. Small local sample and source bias."]}
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
    print("DK15_PROFILE_REPORT="+json.dumps(report,allow_nan=False),flush=True)
ix={k:i for i,k in enumerate(taxa)};rng=np.random.default_rng(20261126)
pairs=[];group_block=[];group_source=[]
for key,v in q.groupby(G,sort=True):
    by={s:np.sort(w.cell_index.unique()) for s,w in v.groupby("species_key",sort=True)}
    for s,t in itertools.combinations(sorted(by),2):
        ca=np.repeat(by[s],len(by[t]));cb=np.tile(by[t],len(by[s]))
        ok=ca!=cb;ca,cb=ca[ok],cb[ok]
        if not len(ca):continue
        if len(ca)>128:
            pick=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[pick],cb[pick]
        g=len(group_block);group_block.append((int(key[2]),int(key[3])));group_source.append(str(key[0]))
        pairs.extend((ix[s],ix[t],int(x),int(y),g) for x,y in zip(ca,cb))
z=np.asarray(pairs,dtype=int).reshape(-1,5)
sa,sb,ca,cb,gi=z.T
blocks=sorted(set(group_block),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
sources=sorted(set(group_source),key=lambda x:hashlib.sha256(x.encode()).hexdigest())
bi={b:i for i,b in enumerate(blocks)};si={s:i for i,s in enumerate(sources)}
gb=np.asarray([bi[b] for b in group_block],int);gs=np.asarray([si[s] for s in group_source],int)
block=gb[gi];source=gs[gi];fold=block%5;sf=source%5;nb=len(blocks);ng=len(gb)
report["comparison_support"]={"comparisons":len(z),"blocks":nb,"sources":len(sources),"taxa":len(np.unique(np.r_[sa,sb])),"groups":ng,"cells":len(np.unique(np.r_[ca,cb]))}
if len(z)<300 or nb<10 or len(np.unique(np.r_[sa,sb]))<6 or len(np.unique(np.r_[ca,cb]))<30:
    report["status"]="INSUFFICIENT_COMPARISON_SUPPORT";save();raise SystemExit(0)
A=np.eye(len(taxa))[sa]-np.eye(len(taxa))[sb];raw=ct[feat].to_numpy(float)
def weights(mask):
    n=np.bincount(gi[mask],minlength=ng)
    perblock=np.bincount(gb[n>0],minlength=nb)
    w=1/(perblock[block[mask]]*n[gi[mask]])
    w=w/np.unique(block[mask]).size
    assert np.isclose(w.sum(),1)
    return w
def obj(p,X,w):
    h=X@p
    return float(w@np.logaddexp(0,-h)+.1*(p@p)),X.T@(-w*expit(-h))+.2*p
def compare(train,test):
    used=np.unique(np.r_[sa[train],sb[train]])
    test=test&np.isin(sa,used)&np.isin(sb,used)
    if train.sum()<300 or len(used)<6 or len(np.unique(block[train]))<8 or test.sum()<10 or len(np.unique(block[test]))<2:return test,None,"support"
    assert not np.any(train&test)
    cs=np.unique(np.r_[ca[train],cb[train]])
    sd=raw[cs].std(axis=0);zero=sd<=1e-12;sd[zero]=1
    X=(raw[ca]-raw[cb])/sd;X[:,zero]=0
    B=(A[:,:,None]*X[:,:len(base)][:,None,:]).reshape(len(z),-1)
    GP=A*X[:,-2,None];LP=A*X[:,-1,None]
    W=weights(train);out=[]
    for mat in [B,np.column_stack([B,GP]),np.column_stack([B,LP]),np.column_stack([B,GP,LP])]:
        Xtr=np.ascontiguousarray(mat[train]);Xte=np.ascontiguousarray(mat[test])
        fit=minimize(obj,np.zeros(mat.shape[1]),args=(Xtr,W),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
        if not fit.success:return test,None,"optimizer"
        out.append(-np.logaddexp(0,-Xte@fit.x))
    return test,np.stack(out,axis=1),None
def evaluate(joint):
    scores=np.full((len(z),4),np.nan);details=[];skips=collections.Counter()
    for k in range(5):
        for h in (range(5) if joint else [None]):
            tr=(fold!=k)&((sf!=h) if joint else True)
            te=(fold==k)&((sf==h) if joint else True)
            te,val,reason=compare(tr,te)
            if reason:skips[reason]+=1;continue
            assert not np.isfinite(scores[te]).any()
            scores[te]=val
            details.append({"block_fold":k+1,"source_fold":None if h is None else h+1,"test_comparisons":int(te.sum()),"test_blocks":len(np.unique(block[te])),"test_sources":len(np.unique(source[te])),"scores":(weights(te)@val).tolist()})
    ok=np.isfinite(scores).all(1)
    support={"scored_comparisons":int(ok.sum()),"coverage":float(ok.mean()),"scored_blocks":len(np.unique(block[ok])),"scored_taxa":len(np.unique(np.r_[sa[ok],sb[ok]])),"scored_sources":len(np.unique(source[ok])),"completed_folds":len(details),"completed_block_folds":len({d["block_fold"] for d in details}),"skips":dict(skips)}
    if support["completed_block_folds"]<3 or support["scored_blocks"]<8:return {"status":"INSUFFICIENT_SCORED_SUPPORT",**support}
    w=weights(ok);S=scores[ok];mean=w@S;b=block[ok]
    den=np.bincount(b,weights=w,minlength=nb);live=den>0
    gains={}
    for name,a,c in [("G_B",1,0),("L_B",2,0),("L_G",2,1),("GL_G",3,1),("GL_L",3,2)]:
        vals=np.bincount(b,weights=w*(S[:,a]-S[:,c]),minlength=nb)[live]/den[live]
        boot=np.random.default_rng(20261126).choice(vals,size=(2000,len(vals)),replace=True).mean(1)
        gains[name]={"gain":float(mean[a]-mean[c]),"positive_blocks":int((vals>0).sum()),"block_quantiles":np.quantile(vals,[.05,.5,.95]).tolist(),"conditional_block_bootstrap_95":np.quantile(boot,[.025,.975]).tolist()}
    return {"status":"COMPLETE_DESCRIPTIVE_ONLY",**support,"scores":dict(zip(["B","G","L","GL"],map(float,mean))),"gains":gains,"folds":details}
report["block_cv"]=evaluate(False);save()
report["strict_source_block_cv"]=evaluate(True)
report["status"]="DIAGNOSTIC_COMPLETE";report["original_primary_sdm_admitted"]=False;save()
