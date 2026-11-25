"""Fixed A adjusted baseline: unchanged cohort/pair construction from blob 23cfa845156dd8db8abf8051e666d1f4f449a4e4; fixed fit routine from d87e7981daadf36e21604c058ce3dde8f0f75e56."""
import pathlib,hashlib,json,itertools,math,collections,sys
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize

R=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path("fixed_adjusted_support");OUT.mkdir(exist_ok=True)
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

assert sys.argv[1:] in (["--prepare"],["--fit"])
q=construct(v)
assert q is not None
z=q["z"];sa=q["sa"];sb=q["sb"];ca=q["ca"];cb=q["cb"];gi=q["gi"]
blocks=q["blocks"];gbi=q["gbi"];block=q["block"];gb=q["gb"];gs=q["gs"];fold=block%5
ct=v[K+features].drop_duplicates().sort_values(K).reset_index(drop=True)
assert not ct.duplicated(K).any()
assert np.array_equal(ct[features].to_numpy(float),q["raw"])
ct["cell_index"]=np.arange(len(ct))
prior=load(R/"FIXED_SNAPSHOT_PROFILE_VALIDATION_RECEIPT_V1.json")
assert prior["audit"]["run_id"]==45599009912 and prior["A"]["status"]=="COMPLETE_DESCRIPTIVE_ONLY"
assert report["overlap"]==prior["overlap"]
assert report["eligible_south_records"]==9705 and report["eligible_south_species_cells"]==2826
assert len(eligible)==14 and len(ct)==1763 and len(z)==34350 and len(blocks)==50 and len(gb)==1685
assert [int((fold==k).sum()) for k in range(5)]==[2407,8831,463,13384,9265]
assert [int((np.arange(len(blocks))%5==k).sum()) for k in range(5)]==[10]*5
report.update(stage="fixed-snapshot A adjusted baseline, overlapping consistency sensitivity",status="PAIR_SUPPORT_READY",original_DLT_challenge_admitted=False,original_comparisons=len(z),original_groups=len(gb),original_blocks=len(blocks),fixed_folds_verified=True,source_reports={},limits=["Not independent regional replication: 47/50 blocks overlap the pilot.","LC100 forest-class areas not DLT leaf cover; DSM includes surface objects.","No causal vertical effect, occupancy, flight height or new 20-taxon SDM admission."])
def save():
    def scalar(v):
        if isinstance(v,np.generic):return v.item()
        raise TypeError("unsupported result value "+type(v).__name__)
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False,default=scalar)+"\n")
    print("FIXED_ADJUSTED_REPORT="+json.dumps(report,allow_nan=False,default=scalar),flush=True)
p=OUT/"candidate_cells.csv.gz"
if sys.argv[1:]==["--prepare"]:
    ct[K].to_csv(p,index=False,compression={"method":"gzip","mtime":0})
    report["candidate_cells_sha256"]=sha(p)
    save()
    raise SystemExit(0)
pr=load(OUT/"report.json")
assert pr["status"]=="PAIR_SUPPORT_READY" and sha(p)==pr["candidate_cells_sha256"]
assert ct[K].equals(pd.read_csv(p))
report["candidate_cells_sha256"]=sha(p)
env=load("fixed_adjusted_covariates/report.json")
assert env["status"] in ("COVARIATES_COMPLETE","COVARIATES_PARTIAL")
assert env["candidate_cells_sha256"]==sha(p)
cp=require("fixed_adjusted_covariates/cell_covariates.csv.gz",env["output_sha256"])
covs=pd.read_csv(cp);assert len(covs)==1763 and not covs.duplicated(K).any()
terrain=["surface_elev_mean_m","surface_elev_sd_m"]
leaf=["lc100_broadleaf_class_fraction","lc100_needleleaf_class_fraction","lc100_mixed_class_fraction","lc100_other_forest_class_fraction"]
ct=ct.merge(covs[K+terrain+leaf+["terrain_support","leaf_support"]],on=K,validate="one_to_one",how="left")
assert ct.cell_index.tolist()==list(range(1763))
for mode,cols in [("terrain",terrain),("leaf",leaf)]:
    ct[mode+"_support"]=yes(ct[mode+"_support"])&np.isfinite(ct[cols]).all(1)
report["cell_support"]={"terrain":int(ct.terrain_support.sum()),"leaf":int(ct.leaf_support.sum()),"both":int((ct.terrain_support&ct.leaf_support).sum())}
report["source_reports"]={k:env[k] for k in ("reused_cells","new_cells","output_sha256","candidate_cells_sha256","old_table_sha256")}
OUT=pathlib.Path("fixed_adjusted_baseline");OUT.mkdir(exist_ok=True)
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
    valid=ct.terrain_support.to_numpy(bool)&ct.leaf_support.to_numpy(bool)
    report["full_challenge"]=run("fixed_A",valid,{"T":base+terrain,"L":base+leaf,"TL":base+terrain+leaf})
    a=report["full_challenge"]
    report["status"]="FIXED_ADJUSTED_COMPLETE_DESCRIPTIVE_ONLY" if a["status"]=="COMPLETE_DESCRIPTIVE_ONLY" else "FIXED_ADJUSTED_NOT_ADMITTED"
    if a["status"]=="COMPLETE_DESCRIPTIVE_ONLY":
        report["full_support_original_replay"]=None
        if a["comparisons"]==34350:
            check={"B":abs(a["scores"]["B"]-prior["A"]["scores"]["B1"])<1e-7,"B+R50":abs(a["scores"]["B+R50"]-prior["A"]["scores"]["B2"])<1e-7}
            report["full_support_original_replay"]=check
            if not all(check.values()):
                report["status"]="STOP_ORIGINAL_SCORE_REPLAY_MISMATCH"
                save();raise ValueError("original score replay mismatch")
        else:
            report["original_full_support_scores"]={k:prior["A"]["scores"][v] for k,v in [("B","B1"),("B+R50","B2")]}
    save()
except Exception as e:
    report.update(status="STOP",error=type(e).__name__+": "+str(e)[:200]);save();raise
