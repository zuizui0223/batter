"""V20: flight/sensory geometry of European range-defined assemblages."""
import collections as C,hashlib,json,re
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing
from macro_fd_v19_acoustic_sources import api,get,table,norm
OUT=Path("macro_fd_v20b_result.json")
SEED=20261128
NREP=4999
FILES={
"04_acoustic_signature.csv":(38642864,"22381fc194772a55190d463278dee95707d7d3ca5e84a60e980c8c7bd18f3604"),
"Taxon.csv":(38642894,"d2789d8e8775c7693282b45f7832d54475054d9d596cab37464b505e91d9db68"),
"Trait_description.csv":(38642897,"a990aa682fc9d417181368ed6a23eb24847d79640c573de9e71293bde9c6e2e7")}
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V20B_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def canonical(x):return re.sub("[^a-z]","",str(x).casefold())
def nonmissing(s):
    return ~s.str.strip().str.casefold().isin(["","na","n/a","none","nan","unknown","not known","not specified"])
def source(o):
    rec={};o["euro_source"]=rec
    j=api("https://api.figshare.com/v2/articles/21777161/versions/2",rec,"metadata")
    assert j["doi"]=="10.6084/m9.figshare.21777161.v2"
    tab={}
    for name,(fid,sha) in FILES.items():
        f=[x for x in j["files"] if x["name"]==name]
        assert len(f)==1 and f[0]["id"]==fid
        v=f[0];fr={};rec[name]=fr
        b=get(v.get("downloadUrl") or v.get("download_url"),2*1024**2,fr,"download",v["size"],v["computed_md5"])
        assert hashlib.sha256(b).hexdigest()==sha
        tab[name]=table(b)
    d=tab["04_acoustic_signature.csv"];tax=tab["Taxon.csv"];dic=tab["Trait_description.csv"]
    assert len(d)==1373 and len(tax)==47 and len(dic)==118
    known=tax.verbatimScientificName.map(norm)
    assert known.is_unique
    d["name"]=d.verbatimScientificName.map(norm)
    o["trait_names"]=dict(C.Counter(d.verbatimTraitName))
    out={};o["traits"]={}
    for target,unit in [("callpeakfrequency","khz"),("callduration","ms")]:
        a=dic[dic.Name.map(canonical)==target]
        if len(a)!=1:raise ValueError("trait definition not unique: "+target)
        ar=a.iloc[0];label=ar.Name
        tr={"definition":str(ar.Definition),"dictionary_unit":str(ar.Unit),"name":label}
        o["traits"][target]=tr
        defn=str(ar.Definition).casefold()
        if target=="callpeakfrequency":assert "frequency" in defn and ("peak" in defn or "energy" in defn or "amplitude" in defn)
        else:assert "duration" in defn and ("call" in defn or "pulse" in defn)
        s=d[d.verbatimTraitName.eq(label)].copy()
        tr["all_rows"]=len(s)
        tr["units"]=dict(C.Counter(s.verbatimTraitUnit))
        tr["types"]=dict(C.Counter(s.verbatimTraitValueType))
        tr["methods"]=dict(C.Counter(s.verbatimTraitMethod))
        tr["all_species"]=int(s.name.nunique())
        ref=s.FullReference.where(nonmissing(s.FullReference),s.ShortReference).str.strip()
        method=s.verbatimTraitMethod.str.casefold()
        numeric=pd.to_numeric(s.verbatimTraitValue,errors="coerce")
        units=s.verbatimTraitUnit.str.strip().str.casefold().str.replace(" ","",regex=False).eq(unit)
        types=s.verbatimTraitValueType.str.strip().str.casefold().isin(["mean","average","median"])
        explicit=method.str.strip().eq("free-flight")
        excluded=method.str.contains(r"imput|predict|modell|modeling|estimated|unspecified",regex=True)
        good=s.name.isin(set(known))&s.name.str.fullmatch(r"[a-z-]+_[a-z-]+")&units&types&nonmissing(ref)&np.isfinite(numeric)&numeric.gt(0)
        tr["reported_numeric_summary_rows"]=int(good.sum())
        tr["reported_numeric_species"]=int(s.loc[good,"name"].nunique())
        good&=explicit&~excluded
        m=pd.DataFrame({"name":s.loc[good,"name"],"ref":ref[good],"value":numeric[good]})
        by=m.groupby(["name","ref"]).value.median()
        v=by.groupby(level=0).median()
        tr["admitted_rows"]=len(m);tr["species"]=len(v);tr["distinct_references"]=int(m.ref.nunique())
        tr["reference_species_pairs"]=len(by)
        out[target]=v
    return pd.DataFrame(out).dropna()
def dist(z):
    z=np.asarray(z,float)
    assert (np.std(z,axis=0)>0).all()
    z=(z-z.mean(0))/z.std(0)
    d=((z[:,None,:]-z[None,:,:])**2).sum(2)
    n=len(d);assert np.isfinite(d).all() and d.sum()>0
    return d/(d.sum()/(n*(n-1)))
def geometry(W,A,P,blocks,groups,grain):
    n=P.shape[1]
    ub=sorted(set(blocks))
    B=np.zeros((len(ub),n,n));means=np.zeros((len(ub),3))
    ix={v:i for i,v in enumerate(ub)};counts=np.zeros(len(ub))
    for p,b in zip(P,blocks):
        q=np.outer(p,p).astype(float);np.fill_diagonal(q,0);q/=q.sum()
        meanw=float(np.sum(q*W));meana=float(np.sum(q*A))
        k=q*(W-meanw);j=ix[b];B[j]+=k
        means[j]+=[meanw,meana,float(np.sum(k*A))];counts[j]+=1
    B/=counts[:,None,None];means/=counts[:,None]
    M=B.mean(0);obs=float(np.sum(M*A));assert abs(obs-means[:,2].mean())<1e-12
    rng=np.random.default_rng(SEED+grain)
    vals={};gen_mean=None
    for label in ("unrestricted","genus"):
        vv=[];meanmat=np.zeros_like(A)
        for _ in range(NREP):
            if label=="unrestricted":perm=rng.permutation(n)
            else:
                perm=np.arange(n)
                for g in groups:perm[g]=rng.permutation(g)
            a=A[np.ix_(perm,perm)]
            vv.append(float(np.sum(M*a)));meanmat+=a
        vv=np.array(vv);meanmat/=NREP
        lo,hi=np.quantile(vv,[.025,.975])
        vals[label]={"mean":float(vv.mean()),"q025":float(lo),"q975":float(hi),"rank":float((vv<=obs).mean()),"residual":float(obs-vv.mean()),"outside":bool(obs<lo or obs>hi)}
        if label=="genus":gen_mean=meanmat
    residual=np.einsum("bij,ij->b",B,A-gen_mean);overall=float(residual.mean())
    assert abs(overall-vals["genus"]["residual"])<1e-10
    loo=(overall*len(residual)-residual)/(len(residual)-1)
    return {"grain":grain,"blocks":len(ub),"cells":len(P),"mean_W":float(means[:,0].mean()),"mean_A":float(means[:,1].mean()),"observed_K":obs,"null":vals,"genus_residual_positive_blocks":int((residual>0).sum()),"delete_one_block_range":[float(loo.min()),float(loo.max())],"primary_pass":bool(vals["genus"]["outside"] and ((overall>0 and loo.min()>0) or (overall<0 and loo.max()<0)))}
def selftest():
    z=np.array([[1.,2.],[2.,1.],[4.,3.],[2.,5.],[3.,1.]])
    W=dist(z);A=dist(z[:,::-1])
    p=np.ones(5,dtype=bool);q=np.outer(p,p).astype(float);np.fill_diagonal(q,0);q/=q.sum()
    k=float(np.sum(q*W*A)-np.sum(q*W)*np.sum(q*A))
    assert k>0 and abs(k-np.sum(q*(W-np.sum(q*W))*A))<1e-12
def main():
    o={"stage":"European free-flight reported flight/sensory geometry","status":"START","limits":["reported acoustic summaries not new waveform measurements","potential range assemblages not observed coexistence","genus shuffles not full phylogenetic control","no GEDI fit, altitude or causal partitioning claim"]}
    try:
        selftest()
        acoustic=source(o)
        o["common_acoustic_species_before_range_wing"]=len(acoustic)
        o["status"]="ACOUSTIC_CENSUS";save(o)
        if len(acoustic)<20:o["status"]="ACOUSTIC_SUPPORT_STOP";save(o);return
        names,R,shape,crs,T=read_ranges(o);w=wing(o)
        nm=sorted(set(names)&set(w.index)&set(acoustic.index));o["joint_species"]=len(nm)
        if len(nm)<20:o["status"]="JOINT_ROSTER_STOP";save(o);return
        ids=[names.index(n) for n in nm];a=acoustic.loc[nm].to_numpy(float)
        ww=w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float)
        W=dist(np.c_[ww[:,0],np.log(ww[:,1])]);A=dist(np.log(a));M=dist(np.log(ww[:,2,None]))
        gs=C.defaultdict(list)
        for i,n in enumerate(nm):gs[n.split("_")[0]].append(i)
        groups=[np.array(v,int) for v in gs.values()]
        mutable=sum(len(g) for g in groups if len(g)>1 and np.unique(a[g],axis=0).shape[0]>1)
        o["roster_support"]={"species":len(nm),"genera":len(groups),"mutable_acoustic_species":mutable,"trait_names":nm}
        if len(groups)<5 or mutable<5:o["status"]="GENUS_NULL_SUPPORT_STOP";save(o);return
        rc=np.array(np.unravel_index(np.arange(R.shape[1]),shape)).T
        p=Transformer.from_crs(crs,4326,always_xy=True)
        lon,lat=p.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        full=R.sum(0);sub=R[ids];k=sub.sum(0);cov=np.divide(k,full,out=np.zeros_like(full,float),where=full>0)
        ok=(lon>=-12)&(lon<=40)&(lat>=35)&(lat<=72)&(k>=5)&(cov>=.3)
        P=sub[:,ok].T;rr=rc[ok]
        o["cell_support"]={"cells":len(P),"blocks2":len({tuple(x//2) for x in rr}),"blocks4":len({tuple(x//4) for x in rr}),"coverage_median":float(np.median(cov[ok])) if ok.any() else None}
        if len(P)<100 or o["cell_support"]["blocks2"]<15 or o["cell_support"]["blocks4"]<2:o["status"]="SPATIAL_SUPPORT_STOP";save(o);return
        o["tests"]={str(g):geometry(W,A,P,[tuple(x//g) for x in rr],groups,g) for g in (2,4)}
        z=[v["null"]["genus"]["residual"] for v in o["tests"].values()]
        o["primary_pass"]=all(v["primary_pass"] for v in o["tests"].values()) and z[0]*z[1]>0
        o["secondary_roster_global_mass_acoustic_distance_covariance"]=float(np.mean(M[np.triu_indices(len(nm),1)]*A[np.triu_indices(len(nm),1)])-np.mean(M[np.triu_indices(len(nm),1)])*np.mean(A[np.triu_indices(len(nm),1)]))
        o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__
        if isinstance(e,ValueError):o["validation"]=str(e)[:200]
        save(o)
if __name__=="__main__":main()
