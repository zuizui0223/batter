"""Frozen fixed-snapshot profile validation A/B. No new source retrieval or model tuning."""
import pathlib,hashlib,json,itertools,math,collections
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize

R=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path("fixed_profile_validation");OUT.mkdir(exist_ok=True)
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def load(p):return json.loads(pathlib.Path(p).read_text())
def require(p,pin):
    p=pathlib.Path(p);assert sha(p)==pin,str(p);return p
def read(p):return pd.read_csv(p,dtype={"species_key":str,"snapshot_species_key":str,"legacy_gbif_species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
def yes(x):return x.astype(str).str.lower().eq("true")
K=["cell_x","cell_y"];G=["dataset_key","year","bx","by"];SK=["species_key",*K]
base=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{i}_fraction" for i in [10,20,30,40,50]],"GVSM_area_mean_RH98_m"];features=base+["R50"]
roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
old=read(require("pilot/species_cell_source_year_environment.csv.gz","5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"))
old=old.loc[yes(old.forest_profile_support)&old.species_key.isin(roster)&old.dataset_key.ne("")&old.year.str.fullmatch(r"20[0-9]{2}")].copy()
assert len(old[G].drop_duplicates())==491
old["AR"]=pd.to_numeric(old.AR,errors="raise")
ar=old[["species_key","AR"]].drop_duplicates().set_index("species_key").loc[roster,"AR"].to_numpy(float)
assert len(ar)==14 and np.std(ar)>0
az=(ar-ar.mean())/ar.std();nsp=len(roster)
P=np.eye(nsp)-np.ones((nsp,nsp))/nsp-np.outer(az,az)/nsp
assert np.max(np.abs(P@az))<1e-10 and np.max(np.abs(P@P-P))<1e-10
index={k:i for i,k in enumerate(roster)}
def pair_support(df):
    """Compute exact eligible comparison block set, before sampling."""
    blocks=set();sources=set();n=0;groups=0
    for key,v in df.drop_duplicates(["species_key",*K,*G]).groupby(G,sort=True):
        by={k:set(map(tuple,q[K].itertuples(index=False,name=None))) for k,q in v.groupby("species_key",sort=True)}
        for s,t in itertools.combinations(sorted(by),2):
            m=len(by[s])*len(by[t])-len(by[s]&by[t])
            if m:
                blocks.add((int(key[2]),int(key[3])));sources.add(str(key[0]));n+=min(m,128);groups+=1
    return blocks,sources,n,groups
ob,osrc,on,og=pair_support(old)
assert (len(ob),on,og)==(51,31601,1626)
oldcells=set(map(tuple,old[K].drop_duplicates().itertuples(index=False,name=None)))

# Environment manifest must be the exact committed result receipt of the successful fixed run.
er=load(R/"FIXED_SNAPSHOT_ENVIRONMENT_RECEIPT_V1.json")
assert er["status"]=="FIXED_SNAPSHOT_ENVIRONMENT_READY" and er["audit"]["run_id"]==45591426116
ep=require("environment/all_bat_species_cell_source_year_environment.csv.gz",er["output_sha256"]["all_bat_species_cell_source_year_environment.csv.gz"])
f=read(ep)
assert int(f.records.sum())==219960 and len(f[["snapshot_species_key",*K]].drop_duplicates())==23489
flags=read(require("audit/source_cell_year_observation_flags.csv.gz","de971292065a8aee3491880adb00a5623efae61bc83b2bd2ae4d663b45edf0f0"))
keys=["species","snapshot_species_key",*K,"dataset_key","year","license"]
assert not f.duplicated(keys).any() and not flags.duplicated(keys).any()
f=f.merge(flags,on=keys,how="outer",suffixes=("","_audit"),validate="one_to_one",indicator=True)
assert f._merge.eq("both").all() and f.records.eq(f.records_audit).all()
assert f.flag_explicit_captive.sum()==0 and f.flag_roost_context.sum()==684
assert f.flag_roost_context.le(f.records).all()
# 0 explicit captive flags, so roost subtraction is exact union. Missing establishment/behavior
# stays unknown; metadata flags do not classify every recording. Human and machine observations
# already screened at original fixed-snapshot extraction. Do not declare unflagged records in flight.
f["clean_records"]=f.records-f.flag_roost_context
t=read(require("traits/physical_trait_crosswalk.csv","43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"))
norm=lambda x:" ".join(str(x).split()).casefold()
t=t[t.species_key.isin(roster)].copy();t["norm"]=t.source_name.map(norm)
assert len(t)==len(roster) and not t.norm.duplicated().any() and not t.species_key.duplicated().any()
f["norm"]=f.species.map(norm)
names=f.groupby("norm").snapshot_species_key.nunique()
keys_to_names=f.groupby("snapshot_species_key").norm.nunique()
amb=set(names[names!=1].index);amb_keys=set(keys_to_names[keys_to_names!=1].index)
mapping=t[["species_key","source_name","norm","AR"]].copy();mapping["AR"]=pd.to_numeric(mapping.AR,errors="raise")
assert np.allclose(mapping.set_index("species_key").loc[roster,"AR"].to_numpy(),ar,rtol=0,atol=1e-10)
# Never join old numeric taxon IDs to snapshot alphanumeric IDs. Exact one-to-one accepted-name bridge
# with snapshot species field and recorded snapshot key; report unresolved mappings.
candidate=f[f.norm.isin(mapping.norm)&~f.norm.isin(amb)&~f.snapshot_species_key.isin(amb_keys)&yes(f.provisional_trait_match)].copy()
bridge=candidate[["norm","snapshot_species_key"]].drop_duplicates().merge(mapping,on="norm",validate="one_to_one")
assert not bridge.species_key.duplicated().any() and not bridge.snapshot_species_key.duplicated().any()
# Environment already verified exact-name trait match; validate stored AR against authoritative table.
v=candidate.merge(bridge[["norm","species_key","source_name","AR"]].rename(columns={"AR":"AR_verified","source_name":"trait_name"}),on="norm",validate="many_to_one")
assert np.allclose(pd.to_numeric(v.AR,errors="raise"),v.AR_verified,rtol=0,atol=1e-10)
assert v.species_key.isin(roster).all()
validsrc=v.dataset_key.ne("")&v.year.str.fullmatch(r"20[0-9]{2}")&v.license.isin(["CC_BY_4_0","CC0_1_0","CC_BY_NC_4_0"])
south=yes(v.training_latitude_support)&~yes(v.north_extrapolation)&~yes(v.latitude_boundary_cell)
mask=validsrc&south&yes(v.forest_profile_support)&v.clean_records.gt(0)
v=v[mask].copy()
v[features]=v[features].apply(pd.to_numeric,errors="raise");assert np.isfinite(v[features].to_numpy()).all()
assert (v.bx==v.cell_x//200).all() and (v.by==v.cell_y//200).all()
def coverage(df):
    a=[]
    for k,q in df[SK].drop_duplicates().groupby("species_key"):
        b=q.groupby([q.cell_x//200,q.cell_y//200]).size();a.append({"species_key":str(k),"cells":len(q),"blocks_ge5":int(b.ge(5).sum()),"pass":bool(len(q)>=30 and b.ge(5).sum()>=4)})
    return a
cov=coverage(v);eligible={q["species_key"] for q in cov if q["pass"]}
v=v[v.species_key.isin(eligible)].copy()
report={"stage":"fixed GBIF snapshot conditional label prediction, post-pilot check","snapshot_doi":"10.15468/dl.8yrbe7","source_hashes":{"environment":sha(ep),"pilot":sha(pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")),"flags":sha(pathlib.Path("audit/source_cell_year_observation_flags.csv.gz"))},"fixed_snapshot_raw_records":219960,"all_roost_flags_excluded":684,"explicit_captive_flags":0,"metadata_unknown":"establishment missing for all records; no assertion of wild status/actual flight, same source/year not equal effort","bridge_species":[{"species":r.source_name,"old_key":r.species_key,"snapshot_key":r.snapshot_species_key} for r in bridge.itertuples()],"coverage_before_roster_gate":cov,"eligible_shared_taxa":len(eligible),"eligible_south_records":int(v.clean_records.sum()),"eligible_south_species_cells":len(v[SK].drop_duplicates()),"main_sdm_admitted":False,"limitations":["Fixed snapshot may share observations with November pilot; A is not independent replication.","Observed label allocation, no inference of nonoccurrence or calibrated habitat preference.","No terrain/roost/effort causal controls; keyword screening only, missing fields unknown.","Within GVSM training latitude only; northern predictions not used in primary validation."]}
def overlap(df):
    blocks,sources,n,groups=pair_support(df)
    cells=set(map(tuple,df[K].drop_duplicates().itertuples(index=False,name=None)))
    return {"recorded_cells":len(cells),"cells_overlapping_pilot":len(cells&oldcells),"comparison_sources":len(sources),"sources_overlapping_pilot":len(sources&osrc),"comparison_blocks":len(blocks),"blocks_overlapping_pilot":len(blocks&ob),"novel_blocks":len(blocks-ob),"comparisons":n,"pair_stratum_groups":groups}
report["overlap"]=overlap(v)
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("FIXED_PROFILE_REPORT="+json.dumps(report,allow_nan=False),flush=True)
if len(eligible)<10:
    report.update(status="STOP_INSUFFICIENT_SHARED_TAXA",A={"status":"STOP"},B={"status":"STOP"});save();raise SystemExit(0)
def construct(df):
    ct=df[K+features].drop_duplicates().sort_values(K).reset_index(drop=True)
    assert not ct.duplicated(K).any()
    ct["cell_index"]=np.arange(len(ct))
    f=df.merge(ct[K+["cell_index"]],on=K,validate="many_to_one").drop_duplicates(["species_key","cell_index",*G]).sort_values([*G,"species_key","cell_index"])
    rng=np.random.default_rng(20261125);rows=[];gb=[];gs=[]
    for key,part in f.groupby(G,sort=True):
        by={s:np.sort(p.cell_index.unique()) for s,p in part.groupby("species_key",sort=True)}
        for s,t in itertools.combinations(sorted(by),2):
            a,b=by[s],by[t]
            # Exact original lexicographic Cartesian product and cap. No outcome-adaptive resampling.
            ca=np.repeat(a,len(b));cb=np.tile(b,len(a));keep=ca!=cb;ca,cb=ca[keep],cb[keep]
            if not len(ca):continue
            if len(ca)>128:
                sel=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[sel],cb[sel]
            group=len(gb);gb.append((int(key[2]),int(key[3])));gs.append(str(key[0]))
            rows.extend((index[s],index[t],int(x),int(y),group) for x,y in zip(ca,cb))
    if not rows:return None
    z=np.asarray(rows,dtype=int);sa,sb,ca,cb,gi=z.T
    blocks=sorted(set(gb),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
    bi={b:i for i,b in enumerate(blocks)};gbi=np.array([bi[b] for b in gb]);block=gbi[gi]
    A=np.eye(nsp)[sa]-np.eye(nsp)[sb];D=A@P;trait=A@az
    return dict(z=z,sa=sa,sb=sb,ca=ca,cb=cb,gi=gi,blocks=blocks,gbi=gbi,block=block,gb=gb,gs=gs,raw=ct[features].to_numpy(float),A=A,D=D,trait=trait)
def taxa(q,mask):return set(np.r_[q["sa"][mask],q["sb"][mask]])
def weights(q,mask):
    gi=q["gi"];block=q["block"];nb=len(q["blocks"]);gn=np.bincount(gi[mask],minlength=len(q["gb"]));counts=np.bincount(q["gbi"][gn>0],minlength=nb)
    w=1/(counts[block[mask]]*gn[gi[mask]])
    return w/len(np.unique(block[mask]))
def objective(b,X,w):
    h=X@b
    return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
def fit(q,tr,te):
    assert not np.any(tr&te) and not (set(q["block"][tr])&set(q["block"][te]))
    raw=q["raw"];ca=q["ca"];cb=q["cb"]
    cells=np.unique(np.r_[ca[tr],cb[tr]])
    mu=raw[cells].mean(axis=0);sd=raw[cells].std(axis=0);zero=sd<=1e-12;sd[zero]=1
    X=(raw-mu)/sd;X[:,zero]=0;diff=X[ca]-X[cb];B=diff[:,:len(base)];r=diff[:,-1]
    Y=np.column_stack([(q["D"][:,:,None]*B[:,None,:]).reshape(len(r),-1),q["trait"][:,None]*B])
    W=weights(q,tr);assert np.isclose(W.sum(),1)
    scores=[np.full(int(te.sum()),-math.log(2))];opts=[];gamma=None
    for m in [1,2,3]:
        X=Y if m==1 else np.column_stack([Y,q["A"]*r[:,None]]) if m==2 else np.column_stack([Y,q["D"]*r[:,None],q["trait"]*r])
        xt=np.ascontiguousarray(X[tr]);xe=np.ascontiguousarray(X[te])
        sol=minimize(objective,np.zeros(X.shape[1]),args=(xt,W),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
        opts.append({"model":f"B{m}","success":bool(sol.success),"iterations":int(sol.nit),"max_abs_gradient":float(np.max(np.abs(sol.jac)))})
        if not sol.success:return None,{"optimizers":opts}
        scores.append(-np.logaddexp(0,-(xe@sol.x)))
        if m==3:gamma=float(sol.x[-1])
        del X,xt,xe
    return np.stack(scores,axis=1),{"optimizers":opts,"gamma_AR_profile":gamma}
def summarize(q,sc,mask):
    w=weights(q,mask);ss=w@sc[mask]
    b=q["block"][mask];nb=len(q["blocks"]);bw=np.bincount(b,weights=w,minlength=nb)
    bs=np.column_stack([np.bincount(b,weights=w*sc[mask,i],minlength=nb) for i in range(4)])
    live=bw>0;bs=bs[live]/bw[live,None];d=bs[:,2]-bs[:,1]
    omit=(d.sum()-d)/(len(d)-1) if len(d)>1 else np.array([float(d[0])])
    return {"scores":{f"B{i}":float(x) for i,x in enumerate(ss)},"gains":{"B1_B0":float(ss[1]-ss[0]),"B2_B1":float(ss[2]-ss[1]),"B3_B2":float(ss[3]-ss[2]),"B3_B1":float(ss[3]-ss[1])},"scored_blocks":int(len(d)),"scored_comparisons":int(mask.sum()),"positive_blocks_profile":int((d>0).sum()),"profile_block_gain_quantiles":np.quantile(d,[.05,.5,.95]).tolist(),"profile_omission_mean_range":[float(omit.min()),float(omit.max())],"block_gains":[float(x) for x in d]}
# A: exact 5-block-fold implementation on eligible fixed-snapshot-only data.
q=construct(v);A={"status":"STOP_INSUFFICIENT_SUPPORT"}
if q is not None:
    block=q["block"];fold=block%5;nb=len(q["blocks"]);alltaxa=taxa(q,np.ones(len(block),bool))
    A["support"]={"blocks":nb,"fold_blocks":[int((np.arange(nb)%5==k).sum()) for k in range(5)],"contributing_taxa":len(alltaxa),"comparisons":len(block)}
    if nb>=20 and min(A["support"]["fold_blocks"])>=4 and len(alltaxa)>=10 and all(taxa(q,fold!=k)==alltaxa for k in range(5)):
        sc=np.full((len(block),4),np.nan);fs=[];ok=True
        for k in range(5):
            tr=fold!=k;te=~tr;x,diag=fit(q,tr,te)
            if x is None:ok=False;A["status"]="STOP_OPTIMIZER";A["optimizer_failure"]=diag;break
            sc[te]=x;fs.append({"fold":k+1,**summarize(q,sc,te),**diag})
        if ok:
            m=summarize(q,sc,np.ones(len(block),bool));pos=sum(x["gains"]["B2_B1"]>0 for x in fs)
            A.update(status="COMPLETE_DESCRIPTIVE_ONLY",**m,folds=fs,positive_folds_profile=pos,screen=bool(m["gains"]["B2_B1"]>0 and pos>=4 and m["profile_omission_mean_range"][0]>0))
report["A"]=A
# B: eligible training taxa fixed using support counts; no outcome-based selection.
v["pilot_block"]=[(int(x),int(y)) in ob for x,y in zip(v.bx,v.by)]
train_cov=coverage(v[v.pilot_block])
train_ok={x["species_key"] for x in train_cov if x["blocks_ge5"]>=4}
testtax=set(v.loc[~v.pilot_block,"species_key"]);shared=train_ok&testtax&eligible
bdata=v[v.species_key.isin(shared)].copy()
B={"status":"STOP_INSUFFICIENT_NOVEL_BLOCK_SUPPORT","shared_taxa_from_support":len(shared),"training_coverage":train_cov,"overlap":overlap(bdata)}
qb=construct(bdata) if len(shared)>=10 and len(bdata) else None
if qb is not None:
    isold=np.array([b in ob for b in qb["blocks"]]);tr=isold[qb["block"]];te=~tr
    train_tax=taxa(qb,tr);test_tax=taxa(qb,te)
    B["support"]={"train_blocks":int(len(np.unique(qb["block"][tr]))),"novel_test_blocks":int(len(np.unique(qb["block"][te]))),"train_taxa":len(train_tax),"test_taxa":len(test_tax),"train_comparisons":int(tr.sum()),"test_comparisons":int(te.sum()),"train_test_source_overlap":len({qb["gs"][i] for i in np.unique(qb["gi"][tr])}&{qb["gs"][i] for i in np.unique(qb["gi"][te])})}
    if B["support"]["novel_test_blocks"]>=10 and len(test_tax)>=10 and test_tax<=train_tax:
        x,diag=fit(qb,tr,te)
        if x is None:B.update(status="STOP_OPTIMIZER",optimizer_failure=diag)
        else:
            sc=np.full((len(te),4),np.nan);sc[te]=x;m=summarize(qb,sc,te)
            B.update(status="COMPLETE_DESCRIPTIVE_ONLY",**m,**diag,screen=bool(m["gains"]["B2_B1"]>0 and m["profile_omission_mean_range"][0]>0 and m["positive_blocks_profile"]>m["scored_blocks"]/2))
report["B"]=B
report["status"]="VALIDATION_FINISHED_WITH_SUPPORT_GATES";save()
