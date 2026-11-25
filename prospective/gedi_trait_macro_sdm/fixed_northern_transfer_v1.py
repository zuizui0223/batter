"""Pre-specified transfer stress test; recorded label sorting, not actual occupancy.
See FIXED_NORTHERN_TRANSFER_CONTRACT_V1.md.
"""
import collections,csv,hashlib,io,itertools,json,math,pathlib
import numpy as np,pandas as pd
from scipy.special import expit
from scipy.optimize import minimize
OUT=pathlib.Path("northern_transfer");OUT.mkdir(exist_ok=True)
P=pathlib.Path("common_forest/species_cell_source_year_environment.csv.gz")
E=pathlib.Path("fixed_environment/all_bat_species_cell_source_year_environment.csv.gz")
M=pathlib.Path("holdout/fixed_source_cell_year_holdout_masks.csv.gz")
F=pathlib.Path("observation/source_cell_year_observation_flags.csv.gz")
C=pathlib.Path("traits/physical_trait_crosswalk.csv")
T=pathlib.Path("physical/physical_wing_traits_original.csv")
pins={P:"5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b",E:"85ad737229aa7b10720a8d5c8bd0ea389f63f908c37871c7ce46ae87c9bed1d6",M:"6796dcc358dd1990cb3cca25b95fe068b52cce7a979ff8602ce639c5708e4b96",F:"de971292065a8aee3491880adb00a5623efae61bc83b2bd2ae4d663b45edf0f0",C:"43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f",T:"d3ebe7656a60b44933f4da1a8302ca800bed07e0864d557698bf322eb7b85f49"}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
for p,v in pins.items():assert sha(p)==v,str(p)
K=["cell_x","cell_y"];G=["dataset_key","year","bx","by"]
SK=["species_key",*K]
JOIN=["species","snapshot_species_key",*K,"dataset_key","year","license"]
base=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{i}_fraction" for i in [10,20,30,40,50]],"GVSM_area_mean_RH98_m"]
features=base+["R50"]
roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
def read(p):
    return pd.read_csv(p,dtype={k:str for k in ["species","species_key","snapshot_species_key","legacy_gbif_species_key","dataset_key","year","license"]},keep_default_na=False,low_memory=False)
def boolcol(df,k):
    z=df[k].astype(str).str.lower()
    assert z.isin(["true","false"]).all(),k
    return z.eq("true")
old=read(P);env=read(E);mask=read(M);flags=read(F)
assert old.records.sum()==20784 and env.records.sum()==mask.records.sum()==flags.records.sum()==219960
for v in [env,mask,flags]:assert not v.duplicated(JOIN).any()
mm=["trait_match","archive_block_seen","archive_source_seen","pilot_block_seen","pilot_source_seen","training_latitude","north_extrapolation"]
ff=["flag_explicit_captive","flag_roost_context","flag_acoustic_context","flag_capture_context","event_present","protocol_present"]
mask=mask[JOIN+["records",*mm]].rename(columns={"records":"mask_records","training_latitude":"mask_training_latitude","north_extrapolation":"mask_north_extrapolation","trait_match":"mask_trait_match"})
flags=flags[JOIN+["records",*ff]].rename(columns={"records":"flag_records"})
q=env.merge(mask,on=JOIN,how="left",validate="one_to_one").merge(flags,on=JOIN,how="left",validate="one_to_one")
assert len(q)==len(env) and q.records.eq(q.mask_records).all() and q.records.eq(q.flag_records).all()
assert q.flag_explicit_captive.sum()==0 and q.flag_roost_context.sum()==684
assert q.flag_roost_context.between(0,q.records).all()
q["screened_records"]=q.records-q.flag_roost_context
q["species_key"]=q.legacy_gbif_species_key
assert boolcol(q,"mask_trait_match").equals(boolcol(q,"provisional_trait_match"))
assert boolcol(q,"mask_training_latitude").equals(boolcol(q,"training_latitude_support"))
assert boolcol(q,"mask_north_extrapolation").equals(boolcol(q,"north_extrapolation"))
forest=boolcol(q,"forest_profile_support")
matched=boolcol(q,"provisional_trait_match")&q.species_key.ne("")
south=boolcol(q,"training_latitude_support");north=boolcol(q,"north_extrapolation")
unseen=~boolcol(q,"archive_block_seen")&~boolcol(q,"archive_source_seen")&q.dataset_key.ne("")
assert not (unseen&south).any()
assert (q.bx==q.cell_x//200).all() and (q.by==q.cell_y//200).all()
def coverage(d):
    u=d[["species_key",*K,"bx","by"]].drop_duplicates()
    sp=[]
    for k,v in u.groupby("species_key",sort=True):
        n=len(v);nb=int(v.groupby(["bx","by"]).size().ge(5).sum())
        sp.append({"species_key":k,"cells":n,"blocks_ge5":nb,"pass":n>=30 and nb>=4})
    return {"rows":len(d),"raw_records":int(d.records.sum()),"screened_records":int(d.screened_records.sum()),"species_cells":len(u),"species":int(u.species_key.nunique()),"blocks":len(u[["bx","by"]].drop_duplicates()),"species_passing":sum(v["pass"] for v in sp),"species_support":sp}
report={"stage":"disjoint north stress test; no primary SDM or causal mechanism","source_sha256":{str(p):v for p,v in pins.items()},"coverage":{},"status":"START"}
for name,domain in [("all",np.ones(len(q),bool)),("training_latitude",south),("north",north),("disjoint_north",north&unseen)]:
    report["coverage"][name]={"before":coverage(q[matched&forest&domain]),"after":coverage(q[matched&forest&domain&q.screened_records.gt(0)])}
target=sorted(v["species_key"] for v in report["coverage"]["all"]["before"]["species_support"] if v["pass"])
assert len(target)==20
train=old[boolcol(old,"forest_profile_support")&old.species_key.isin(roster)&old.dataset_key.ne("")&old.year.str.fullmatch(r"20[0-9]{2}")].copy()
test=q[matched&forest&north&unseen&q.screened_records.gt(0)&q.species_key.isin(target)&q.dataset_key.ne("")&q.year.str.fullmatch(r"20[0-9]{2}")].copy()
assert not set(old.dataset_key)&set(test.dataset_key)
assert not set(map(tuple,old[["bx","by"]].itertuples(index=False,name=None)))&set(map(tuple,test[["bx","by"]].itertuples(index=False,name=None)))
taxa=sorted(set(roster)|set(target));ix={s:i for i,s in enumerate(taxa)}
# Match the original deterministic construction exactly on training data.
def pairs(d):
    d=d.copy();d[features]=d[features].apply(pd.to_numeric,errors="raise")
    assert np.isfinite(d[features].to_numpy()).all()
    cells=d[K+features].drop_duplicates().sort_values(K).reset_index(drop=True)
    assert not cells.duplicated(K).any()
    cells["cell_index"]=np.arange(len(cells))
    d=d.merge(cells[K+["cell_index"]],on=K,validate="many_to_one")
    d=d.drop_duplicates(["species_key","cell_index",*G]).sort_values([*G,"species_key","cell_index"])
    rng=np.random.default_rng(20261125);z=[];gb=[];sources=[]
    for key,v in d.groupby(G,sort=True):
        by={s:np.sort(w.cell_index.unique()) for s,w in v.groupby("species_key",sort=True)}
        for s,t in itertools.combinations(sorted(by),2):
            a,b=by[s],by[t];ca=np.repeat(a,len(b));cb=np.tile(b,len(a))
            keep=ca!=cb;ca,cb=ca[keep],cb[keep]
            if not len(ca):continue
            if len(ca)>128:
                sel=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[sel],cb[sel]
            g=len(gb);gb.append((int(key[2]),int(key[3])));sources.append(str(key[0]))
            z.extend((ix[s],ix[t],int(x),int(y),g) for x,y in zip(ca,cb))
    z=np.asarray(z,dtype=int).reshape(-1,5)
    sa,sb,ca,cb,gi=z.T
    blocks=sorted(set(gb));bi={b:i for i,b in enumerate(blocks)}
    group_block=np.asarray([bi[b] for b in gb],dtype=int)
    return {"z":z,"sa":sa,"sb":sb,"ca":ca,"cb":cb,"gi":gi,"block":group_block[gi],"gb":group_block,"nb":len(blocks),"ng":len(gb),"raw":cells[features].to_numpy(float),"sources":sources,"cells":len(cells)}
A=pairs(train);B=pairs(test)
assert len(A["z"])==31601 and A["nb"]==51
report["pair_data"]={"train_comparisons":len(A["z"]),"train_blocks":A["nb"],"train_taxa":len(roster),"test_comparisons":len(B["z"]),"test_blocks":B["nb"],"test_taxa":len(np.unique(np.r_[B["sa"],B["sb"]])),"test_sources":len(set(B["sources"])),"test_cells":B["cells"]}
def weights(d,sel):
    gn=np.bincount(d["gi"][sel],minlength=d["ng"])
    perblock=np.bincount(d["gb"][gn>0],minlength=d["nb"])
    v=1/(perblock[d["block"][sel]]*gn[d["gi"][sel]])
    w=v/np.unique(d["block"][sel]).size
    assert np.isclose(w.sum(),1)
    return w
def transforms(train_mask):
    use=np.unique(np.r_[A["ca"][train_mask],A["cb"][train_mask]])
    sd=A["raw"][use].std(axis=0);zero=sd<=1e-12;sd[zero]=1
    def dif(d,m):
        r=(d["raw"][d["ca"][m]]-d["raw"][d["cb"][m]])/sd;r[:,zero]=0
        return r[:,:len(base)],r[:,-1]
    return dif
def obj(p,X,w):
    h=X@p;return float(w@np.logaddexp(0,-h)+.1*(p@p)), X.T@(-w*expit(-h))+.2*p
def fit(X,Y,w):
    z=minimize(obj,np.zeros(X.shape[1]),args=(np.ascontiguousarray(X),w),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
    if not z.success:raise RuntimeError("optimizer failed: "+str(z.message))
    return -np.logaddexp(0,-Y@z.x)
def summarize(sc,names):
    valid=np.isfinite(sc).all(axis=1)
    if not valid.any():return {"status":"INSUFFICIENT_SUPPORT"}
    w=weights(B,valid);s=w@sc[valid];bs=B["block"][valid]
    den=np.bincount(bs,weights=w,minlength=B["nb"]);live=den>0
    result={"status":"COMPLETE","scored_comparisons":int(valid.sum()),"coverage_of_test_pairs":float(valid.mean()),"scored_taxa":len(np.unique(np.r_[B["sa"][valid],B["sb"][valid]])),"scored_blocks":int(live.sum()),"scored_sources":len({B["sources"][i] for i in B["gi"][valid]}),"scores":dict(zip(names,map(float,s))),"gains":{}}
    for k in range(0,len(names),2):
        delta=sc[valid,k+1]-sc[valid,k]
        vals=np.bincount(bs,weights=w*delta,minlength=B["nb"])[live]/den[live]
        rng=np.random.default_rng(20261125)
        boot=rng.choice(vals,size=(2000,len(vals)),replace=True).mean(axis=1)
        result["gains"][names[k+1]]={"gain":float(s[k+1]-s[k]),"positive_blocks":int((vals>0).sum()),"block_quantiles":np.quantile(vals,[.05,.5,.95]).tolist(),"conditional_block_bootstrap_95":np.quantile(boot,[.025,.975]).tolist()}
    return result
# Trait tables use exact physical source and immutable crosswalk, no response-derived traits.
def norm(x):return " ".join(str(x).replace("_"," ").split()).casefold()
def positive(x):
    try:
        v=float(x);return v if math.isfinite(v) and v>0 else np.nan
    except (TypeError,ValueError):return np.nan
raw=T.read_text(encoding="utf-8-sig");phys=list(csv.DictReader(io.StringIO(raw),dialect=csv.Sniffer().sniff(raw[:8192],delimiters=",;\t")))
cw=pd.read_csv(C,dtype=str,keep_default_na=False).set_index("species_key")
phy=collections.defaultdict(list)
for t in phys:phy[norm(t["Latin names"])].append(t)
tv=[];audit=[]
for k in taxa:
    t=cw.loc[k];a=phy[norm(t.source_name)];assert len(a)==1
    a=a[0];ar=positive(t.AR);wl=positive(t.WL_N_m2);mass=positive(t.body_mass_g)
    assert np.isclose(ar,positive(a["Aspect ratio"])) and np.isclose(wl,positive(a["Wingloading"]))
    lo=positive(a["Echolocation frequency minimum"]);hi=positive(a["Echolocation frequency maximum"])
    fr=np.sqrt(lo*hi) if lo<=hi else np.nan;dur=positive(a["Duration call average"])
    row=[ar,np.log(wl),np.log(mass),np.log(fr),np.log(dur)]
    tv.append(row);audit.append({"species_key":k,"species":t.source_name,"AR":ar,"WL":wl,"mass":mass,"frequency_midpoint":fr,"duration":dur,"WA_complete":bool(np.isfinite(row).all())})
tv=np.asarray(tv);complete=np.isfinite(tv).all(axis=1)
pd.DataFrame(audit).to_csv(OUT/"trait_audit.csv",index=False)
report["complete_WA_taxa"]=int(complete.sum())
# Known taxa: prior flexible models, same parameterization as old pilot.
train_ids=np.array([ix[k] for k in roster]);known=set(train_ids.tolist())
tr=np.ones(len(A["z"]),bool);te=np.isin(B["sa"],train_ids)&np.isin(B["sb"],train_ids)
if te.sum()>=10 and len(np.unique(B["block"][te]))>=3:
    ar=tv[train_ids,0];az=(ar-ar.mean())/ar.std();ns=len(roster)
    PP=np.eye(ns)-np.ones((ns,ns))/ns-np.outer(az,az)/ns
    map0={n:i for i,n in enumerate(train_ids)}
    diff=transforms(tr)
    def flexible(d,m):
        x,r=diff(d,m);sa=np.array([map0[i] for i in d["sa"][m]]);sb=np.array([map0[i] for i in d["sb"][m]])
        U=np.eye(ns)[sa]-np.eye(ns)[sb];D=U@PP;tt=U@az
        X=np.column_stack([(D[:,:,None]*x[:,None,:]).reshape(len(x),-1),tt[:,None]*x])
        return [X,np.column_stack([X,U*r[:,None]])]
    X=flexible(A,tr);Y=flexible(B,te);scores=np.full((len(B["z"]),2),np.nan)
    scores[te]=np.stack([fit(x,y,weights(A,tr)) for x,y in zip(X,Y)],axis=1)
    report["known_species_transfer"]=summarize(scores,["flex_base","flex_profile"])
else:report["known_species_transfer"]={"status":"INSUFFICIENT_SUPPORT"}
# Trait-only, each test pair excluded from every training comparison.
scores=np.full((len(B["z"]),6),np.nan);skips=collections.Counter();pairs_done=[]
names=["AR_base","AR_profile","W_base","W_profile","WA_base","WA_profile"]
for s,t in sorted(set(zip(B["sa"],B["sb"]))):
    if not complete[s] or not complete[t]:skips["trait_missing"]+=1;continue
    te=(B["sa"]==s)&(B["sb"]==t)
    tr=(A["sa"]!=s)&(A["sb"]!=s)&(A["sa"]!=t)&(A["sb"]!=t)&complete[A["sa"]]&complete[A["sb"]]
    used=np.unique(np.r_[A["sa"][tr],A["sb"][tr]])
    if te.sum()<10 or len(np.unique(B["block"][te]))<3 or tr.sum()<300 or len(np.unique(A["block"][tr]))<10 or len(used)<8:
        skips["support"]+=1;continue
    assert not set([s,t])&set(used)
    diff=transforms(tr);sd=tv[used].std(axis=0)
    if np.any(sd<=1e-12):skips["constant_traits"]+=1;continue
    V=tv/sd
    def trait_design(d,m,n):
        x,r=diff(d,m);D=V[d["sa"][m],:n]-V[d["sb"][m],:n]
        Z=(D[:,:,None]*x[:,None,:]).reshape(len(x),-1)
        return [Z,np.column_stack([Z,D*r[:,None]])]
    w=weights(A,tr)
    vals=[]
    try:
        for n in (1,3,5):
            X=trait_design(A,tr,n);Y=trait_design(B,te,n)
            vals.extend(fit(x,y,w) for x,y in zip(X,Y))
    except RuntimeError:skips["optimizer"]+=1;continue
    assert not np.isfinite(scores[te]).any()
    scores[te]=np.stack(vals,axis=1)
    sc=weights(B,te)@scores[te]
    pairs_done.append({"taxa":[taxa[s],taxa[t]],"test_comparisons":int(te.sum()),"test_blocks":len(np.unique(B["block"][te])),"training_taxa":len(used),"scores":dict(zip(names,map(float,sc)))})
cold=summarize(scores,names);cold["skips"]=dict(skips);cold["pairs"]=pairs_done
if cold["status"]=="COMPLETE":
    sc=cold["scores"]
    cold["WA_minus_AR_profile"]=sc["WA_profile"]-sc["AR_profile"]
    cold["WA_minus_AR_base"]=sc["WA_profile"]-sc["AR_base"]
    cold["WA_minus_W_profile"]=sc["WA_profile"]-sc["W_profile"]
    cold["WA_minus_AR_gain"]=(sc["WA_profile"]-sc["WA_base"])-(sc["AR_profile"]-sc["AR_base"])
report["trait_cold_start_transfer"]=cold
report["status"]="TRANSFER_STRESS_TEST_COMPLETE"
report["original_primary_sdm_admitted"]=False
report["limits"]=["Northern test observations are disjoint by provider and 200-km block, but GVSM northern structural predictions are outside GEDI training latitude.","Same recorded-label estimand, not detection-adjusted ecological occurrence or actual altitude. Unknown observation context remains.","Block bootstrap conditional on trained models is descriptive, not a population-level confidence interval.","Test taxa selected by pre-outcome geographic coverage; no new model selection or tuning. No independent airborne structure calibration."]
(OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
summary={**report,"coverage":{n:{k:{x:y for x,y in v.items() if x!="species_support"} for k,v in d.items()} for n,d in report["coverage"].items()},"trait_cold_start_transfer":{k:v for k,v in cold.items() if k!="pairs"}}
print("NORTHERN_TRANSFER="+json.dumps(summary,allow_nan=False),flush=True)
