"""Frozen source-conditioned recorded-label sorting pilot, not a biological SDM."""
import hashlib,itertools,json,pathlib,collections,math
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.optimize import minimize

SRC=pathlib.Path("common_forest/species_cell_source_year_environment.csv.gz")
OUT=pathlib.Path("multitrait_cold_start");OUT.mkdir(exist_ok=True)
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

# Fixed traits and documented units; all sources are independently hashed.
import csv,io
def check(p,pin):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==pin,str(p)
def read_table(p):
    s=p.read_text(encoding="utf-8-sig")
    return list(csv.DictReader(io.StringIO(s),dialect=csv.Sniffer().sniff(s[:8192],delimiters=",;\t")))
phys=pathlib.Path("physical/physical_wing_traits_original.csv")
cross=pathlib.Path("traits/physical_trait_crosswalk.csv")
roostpath=pathlib.Path("euro/07_roost_type.csv")
foragepath=pathlib.Path("euro/06_foraging_habitat.csv")
dictpath=pathlib.Path("euro/Trait_description.csv")
for p,pin in [(phys,"d3ebe7656a60b44933f4da1a8302ca800bed07e0864d557698bf322eb7b85f49"),(cross,"43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"),(roostpath,"c0431e2353867bad4d92a0ec6bd35e5951e407bec2b165d275c04572e1d0bc17"),(foragepath,"ab7b4c67d7e4328e5ae4bf9ce2421b153fdd2894d5508dff9041aff4b32c3a61"),(dictpath,"a990aa682fc9d417181368ed6a23eb24847d79640c573de9e71293bde9c6e2e7")]:check(p,pin)
def norm(x):return " ".join(str(x).replace("_"," ").split()).casefold()
def positive(x):
    try:
        v=float(x);return v if math.isfinite(v) and v>0 else np.nan
    except (TypeError,ValueError):return np.nan
physical=read_table(phys);assert len(physical)==30
pmap=collections.defaultdict(list)
for p in physical:pmap[norm(p["Latin names"])].append(p)
cw=pd.read_csv(cross,dtype=str,keep_default_na=False)
cw=cw[cw.species_key.isin(roster)].copy();assert len(cw)==nsp and not cw.species_key.duplicated().any()
cw=cw.set_index("species_key")
roosts=collections.defaultdict(set)
for rr in read_table(roostpath):
    if rr["verbatimTraitName"]=="FirstMainMaternityRoost":
        v=norm(rr["verbatimTraitValue"])
        if v not in {"","na","n/a","unknown","none","nan","not known"}:roosts[norm(rr["verbatimScientificName"])].add(v)
T=[];cats=[];source_rows=[]
for i,key in enumerate(roster):
    t=cw.loc[key];name=norm(t.source_name)
    assert len(pmap[name])==1
    a=pmap[name][0];AR=positive(t.AR);WL=positive(t.WL_N_m2);mass=positive(t.body_mass_g)
    assert np.isclose(AR,ar[i])
    assert np.isclose(AR,positive(a["Aspect ratio"])) and np.isclose(WL,positive(a["Wingloading"]))
    lo=positive(a["Echolocation frequency minimum"]);hi=positive(a["Echolocation frequency maximum"])
    freq=np.sqrt(lo*hi) if lo<=hi else np.nan
    dur=positive(a["Duration call average"])
    c=roosts[name];cat=next(iter(c)) if len(c)==1 else ""
    T.append([AR,np.log(WL),np.log(mass),np.log(freq),np.log(dur)])
    cats.append(cat)
    source_rows.append({"species_key":key,"species":t.source_name,"AR":AR,"WL":WL,"body_mass":mass,"frequency_min":lo,"frequency_max":hi,"frequency_geometric_midpoint":freq,"mean_call_duration":dur,"maternity_roost":cat,"roost_categories":sorted(c)})
T=np.asarray(T);cats=np.asarray(cats)
fdef=[x for x in read_table(dictpath) if x["Category"]=="foraging_habitat"]
forage=read_table(foragepath)
fcounts=collections.Counter(x["verbatimTraitName"] for x in forage)
mode_names={"ForagingMode","ForagingGuild","ForagingStrategy","HuntingStrategy","HuntingMode","ForagingType"}
explicit_modes=[x for x in fdef if x["Name"] in mode_names]
raw=ct[features].to_numpy(float)
report={"stage":"post-pilot multitrait cold-start diagnostic, not an SDM","source_sha256":PIN,"comparisons":int(len(z)),"blocks":int(nb),"species":nsp,"trait_sources":{"physical":"10.5281/zenodo.7226367","roost":"10.6084/m9.figshare.21777161.v2"},"trait_columns":["AR","log_WL","log_body_mass","log_frequency_geometric_midpoint","log_mean_call_duration"],"roost_category_counts":dict(collections.Counter(cats.tolist())),"foraging_trait_dictionary":fdef,"foraging_trait_counts":dict(fcounts),"explicit_foraging_mode_candidates":explicit_modes,"foraging_used":False,"note":"Foraging habitat affinity not used; explicit functional modes require separate source review. Acoustic midpoint is not peak frequency. Fixed ridge penalty, no feature selection.","primary_sdm_admitted":False,"tiers":{}}
pd.DataFrame(source_rows).to_csv(OUT/"trait_source_audit.csv",index=False)
def weights(mask):
    gn=np.bincount(gi[mask],minlength=ng);perblock=np.bincount(gb[gn>0],minlength=nb)
    v=1/(perblock[block[mask]]*gn[gi[mask]])
    return v/np.unique(block[mask]).size
def objective(b,X,w):
    h=X@b
    return float(w@np.logaddexp(0,-h)+.1*(b@b)),X.T@(-w*expit(-h))+.2*b
def feature_matrices(train,te,num,categorical):
    used=np.unique(np.r_[sa[train],sb[train]])
    cs=np.unique(np.r_[ca[train],cb[train]])
    mu=raw[cs].mean(axis=0);sd=raw[cs].std(axis=0);zero=sd<=1e-12;sd[zero]=1
    X=(raw-mu)/sd;X[:,zero]=0
    diff=X[ca]-X[cb]
    B=diff[:,:len(baseline)];R=diff[:,-1]
    # Only differences between traits enter. Centering not needed for numeric pair differences.
    A=ar/np.std(ar[used]);delta=(A[sa]-A[sb])[:,None]
    b0=delta*B; p0=np.column_stack([b0,delta*R[:,None]])
    V=T[:,:num].copy()
    if categorical:
        train_categories=sorted(set(cats[used]))
        if not set(cats[np.unique(np.r_[sa[te],sb[te]])])<=set(train_categories):return None
        V=np.column_stack([V,*[(cats==v).astype(float) for v in train_categories]])
    spread=V[used].std(axis=0)
    keep=spread>1e-12
    if not keep.any():return None
    V=V[:,keep]/spread[keep]
    D=V[sa]-V[sb]
    base=(D[:,:,None]*B[:,None,:]).reshape(len(z),-1)
    prof=np.column_stack([base,D*R[:,None]])
    return [b0,p0,base,prof]
def run_tier(name,num,categorical):
    complete=np.isfinite(T[:,:num]).all(axis=1)
    if categorical:complete&=cats!=""
    eligible=complete[sa]&complete[sb]
    out={"complete_taxa":int(complete.sum()),"complete_species":[roster[i] for i in np.flatnonzero(complete)],"eligible_comparisons":int(eligible.sum()),"score_names":["AR_base","AR_profile","tier_base","tier_profile"],"skips":{}}
    if complete.sum()<10:return {**out,"status":"INSUFFICIENT_TRAIT_COVERAGE"}
    scores=np.full((len(z),4),np.nan)
    fold_summaries=[];skips=collections.Counter()
    for s,t in sorted(set(zip(sa,sb))):
        if not (complete[s] and complete[t]):continue
        pair=(sa==s)&(sb==t)
        other=(sa!=s)&(sb!=s)&(sa!=t)&(sb!=t)
        for k in range(5):
            te=eligible&pair&(fold==k);train=eligible&other&(fold!=k)
            used=np.unique(np.r_[sa[train],sb[train]])
            if train.sum()<300 or te.sum()<10 or len(np.unique(block[train]))<10 or len(np.unique(block[te]))<3 or len(used)<8:
                skips["support"]+=1;continue
            assert not (set([s,t])&set(used)) and not np.any(train&te)
            mats=feature_matrices(train,te,num,categorical)
            if mats is None:skips["unknown_category_or_constant"]+=1;continue
            w=weights(train);assert np.isclose(w.sum(),1)
            fitted=[]
            for X in mats:
                xt=np.ascontiguousarray(X[train]);xe=np.ascontiguousarray(X[te])
                assert np.isfinite(xt).all() and np.isfinite(xe).all()
                fit=minimize(objective,np.zeros(X.shape[1]),args=(xt,w),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
                if not fit.success:break
                fitted.append(-np.logaddexp(0,-(xe@fit.x)))
            if len(fitted)!=4:skips["optimizer"]+=1;continue
            x=np.stack(fitted,axis=1)
            assert not np.isfinite(scores[te]).any();scores[te]=x
            mean=weights(te)@x
            fold_summaries.append({"taxa":[roster[s],roster[t]],"block_fold":k+1,"comparisons":int(te.sum()),"blocks":int(len(np.unique(block[te]))),"training_taxa":int(len(used)),"scores":mean.tolist(),"tier_profile_gain":float(mean[3]-mean[2]),"AR_profile_gain":float(mean[1]-mean[0]),"tier_vs_AR_profile":float(mean[3]-mean[1])})
    valid=np.isfinite(scores).all(axis=1)
    out["skips"]=dict(skips)
    if not valid.any():return {**out,"status":"INSUFFICIENT_COLD_START_SUPPORT"}
    ww=weights(valid);sc=ww@scores[valid];delta=scores[valid,3]-scores[valid,2]
    b=block[valid];den=np.bincount(b,weights=ww,minlength=nb);num1=np.bincount(b,weights=ww*delta,minlength=nb)
    blocks_supported=den>0;bg=num1[blocks_supported]/den[blocks_supported]
    return {**out,"status":"DIAGNOSTIC_COMPLETE","scored_comparisons":int(valid.sum()),"coverage_all":float(valid.mean()),"scored_taxa":int(len(np.unique(np.r_[sa[valid],sb[valid]]))),"scored_blocks":int(blocks_supported.sum()),"scored_pair_folds":len(fold_summaries),"mean_scores":dict(zip(out["score_names"],map(float,sc))),"AR_profile_gain":float(sc[1]-sc[0]),"tier_profile_gain":float(sc[3]-sc[2]),"tier_vs_AR_profile":float(sc[3]-sc[1]),"difference_of_gains":float((sc[3]-sc[2])-(sc[1]-sc[0])),"positive_blocks_tier_profile":int((bg>0).sum()),"block_gain_quantiles":np.quantile(bg,[.05,.5,.95]).tolist(),"folds":fold_summaries}
for name,num,cat in [("W",3,False),("WA",5,False),("WAR",5,True)]:
    report["tiers"][name]=run_tier(name,num,cat)
    print("MULTITRAIT_TIER="+json.dumps({"tier":name,**{k:v for k,v in report["tiers"][name].items() if k!="folds"}},allow_nan=False),flush=True)
report["status"]="MULTITRAIT_DIAGNOSTIC_COMPLETE"
report["limitations"]=["Same already inspected archive; not independent replication or actual distribution probability.","Same observation source/year/block does not establish shared effort or non-detection.","Small taxon count, complete-case and known-category coverage; tier gains not comparable across unmatched subsets.","No causal attribution to physical flight or acoustic mechanisms. No further outcome-driven tuning on this archive."]
(OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
print("MULTITRAIT_REPORT="+json.dumps({**report,"tiers":{k:{x:y for x,y in v.items() if x!="folds"} for k,v in report["tiers"].items()}},allow_nan=False),flush=True)
