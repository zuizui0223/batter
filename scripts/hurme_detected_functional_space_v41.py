"""V41 recorded buzz-mark geography; NOT true foraging, selection, or calibrated detection."""
import hashlib,json,pathlib,re
import numpy as np
import pandas as pd
from pyproj import Transformer
from hurme_label_semantics_v40 import get,read
OUT=pathlib.Path("results/hurme_detected_functional_space_v41.json")
B=499;SEED=41025
GRIDS=(1000,500,2000)
REF_SHA="0194cfd3225c0e56da1b43c0fda4e5f1d7c483294043ecf766067cd347fcf937"
def distribution(c,w,k):
    a=np.bincount(c,weights=w,minlength=k).astype(float)
    return a/a.sum()
def entropy(p):
    p=p[p>0];return float(-np.dot(p,np.log(p)))
def js(p,q):
    m=(p+q)/2
    return max(0.,entropy(m)-(entropy(p)+entropy(q))/2)
def measures(p,q):
    return {"js":js(p,q),"total_variation":float(.5*np.abs(p-q).sum())}
def avg_animal(rows,vals):
    a=np.asarray(vals,float)
    groups={}
    for i,r in enumerate(rows):groups.setdefault(r["animal"],[]).append(i)
    return np.stack([a[ix].mean(axis=0) for ix in groups.values()])
def quant(a):
    a=np.asarray(a,float)
    return np.quantile(a,[0,.05,.5,.95,1]).tolist() if len(a) else []
def attach(g,r):
    """Require unique exact keys and time-bounded reference deployments."""
    r=r.copy();g=g.copy()
    for c in ["animal-id","tag-id","deployment-id"]:r[c]=r[c].str.strip()
    for c in ["individual-local-identifier","tag-local-identifier"]:g[c]=g[c].str.strip()
    r["on"]=pd.to_datetime(r["deploy-on-date"],format="mixed",utc=True,errors="coerce")
    r["off"]=pd.to_datetime(r["deploy-off-date"],format="mixed",utc=True,errors="coerce")
    g["t"]=pd.to_datetime(g.timestamp,format="mixed",utc=True,errors="coerce")
    assert len(r)==15 and len(g)==14328
    assert r["deployment-id"].ne("").all() and r["deployment-id"].is_unique
    assert r[["animal-id","tag-id"]].ne("").all().all()
    fulltime=r["deploy-on-date"].str.contains(r"\d{1,2}:\d{2}") & r["deploy-off-date"].str.contains(r"\d{1,2}:\d{2}")
    ok=fulltime & r.on.notna() & r.off.notna() & (r.on<=r.off)
    audit={"reference_rows":len(r),"valid_complete_time_windows":int(ok.sum()),"reference_unique_animals":int(r["animal-id"].nunique()),"reference_unique_tags":int(r["tag-id"].nunique())}
    if not ok.all():return None,audit
    g["marks"]=pd.to_numeric(g["behavioural-classification"],errors="coerce")
    assert g.t.notna().all() and g["event-id"].is_unique
    assert not g.duplicated(["individual-local-identifier","timestamp"]).any()
    assert g.marks.isin([0,1,2,3,4]).all() and int(g.marks.sum())==698 and int(g.marks.gt(0).sum())==607
    g["matches"]=0;g["dep"]=""
    for _,d in r.iterrows():
        m=(g["individual-local-identifier"]==d["animal-id"])&(g["tag-local-identifier"]==d["tag-id"])&g.t.between(d.on,d.off)
        g.loc[m,"matches"]+=1;g.loc[m,"dep"]=d["deployment-id"]
    matched=g.matches.eq(1)
    audit.update(matched_fixes=int(matched.sum()),ambiguous_fixes=int(g.matches.gt(1).sum()),unmatched_fixes=int(g.matches.eq(0).sum()),matched_marks=int(g.loc[matched,"marks"].sum()),ambiguous_marks=int(g.loc[g.matches.gt(1),"marks"].sum()),unmatched_marks=int(g.loc[g.matches.eq(0),"marks"].sum()),matched_fix_fraction=float(matched.mean()),matched_mark_fraction=float(g.loc[matched,"marks"].sum()/698))
    if matched.mean()<.95 or audit["matched_mark_fraction"]<.95:return None,audit
    g=g[matched].copy()
    g["lon"]=pd.to_numeric(g["location-long"],errors="coerce");g["lat"]=pd.to_numeric(g["location-lat"],errors="coerce")
    valid=g.visible.str.lower().eq("true")&g.lon.between(-180,180)&g.lat.between(-86,86)
    audit["invalid_or_invisible_assigned_fixes"]=int((~valid).sum())
    audit["invalid_or_invisible_assigned_marks"]=int(g.loc[~valid,"marks"].sum())
    return g[valid].copy(),audit
def collect(g):
    tr=Transformer.from_crs("EPSG:4326","EPSG:6933",always_xy=True)
    rows=[];excluded={"below100_fixes":0,"below10_positive_fixes":0};support=[]
    for _,d in g.groupby("dep",sort=True):
        d=d.sort_values("t",kind="stable")
        marks=d.marks.to_numpy(dtype=np.int64);n=len(d);pos=int(np.count_nonzero(marks))
        if n<100:excluded["below100_fixes"]+=1;continue
        if pos<10:excluded["below10_positive_fixes"]+=1;continue
        assert d["individual-local-identifier"].nunique()==1
        x,y=tr.transform(d.lon.to_numpy(),d.lat.to_numpy())
        assert np.isfinite(x).all() and np.isfinite(y).all()
        dt=d.t.diff().dt.total_seconds()
        breaks=(dt.isna()|dt.gt(60)|d.t.dt.floor("h").ne(d.t.dt.floor("h").shift())).to_numpy()
        groups=np.split(np.arange(n),np.flatnonzero(breaks)[1:])
        assert sum(map(len,groups))==n and all(len(k)>0 for k in groups)
        cells={}
        for size in GRIDS:
            _,c=np.unique(np.column_stack([np.floor(x/size).astype(np.int64),np.floor(y/size).astype(np.int64)]),axis=0,return_inverse=True)
            cells[size]=c
        rows.append({"animal":d["individual-local-identifier"].iloc[0],"marks":marks,"groups":groups,"cells":cells})
        support.append([n,pos,int(marks.sum()),len(groups),sum(bool(marks[ix].sum()) for ix in groups)])
    info={"eligible_deployments":len(rows),"eligible_animals":len(set(r["animal"] for r in rows)),"eligible_fixes":sum(len(r["marks"]) for r in rows),"eligible_positive_fixes":sum(int(np.count_nonzero(r["marks"])) for r in rows),"eligible_detected_buzzes":sum(int(r["marks"].sum()) for r in rows),"excluded_deployments":excluded,"eligible_deployment_support_quantiles":{k:quant([a[i] for a in support]) for i,k in enumerate(["fixes","positive_fixes","buzzes","time_strata","mark_positive_strata"])}}
    return rows,info
def analyze(rows):
    rng=np.random.default_rng(SEED)
    # Each simulated index rotation is shared by both mark definitions and all spatial resolutions.
    actual={};null={};geo={}
    for r in rows:
        n=len(r["marks"]);counts=r["marks"];groups=r["groups"]
        rot=np.tile(np.arange(n),(B,1))
        for ix in groups:
            if len(ix)>1:
                shifts=rng.integers(0,len(ix),size=B)
                rot[:,ix]=ix[(np.arange(len(ix))[None,:]+shifts[:,None])%len(ix)]
        for kind,w in [("count",counts),("positive_fix",counts.gt(0).astype(int) if hasattr(counts,"gt") else (counts>0).astype(int))]:
            expected=np.zeros(n,float)
            for ix in groups:expected[ix]=float(w[ix].sum())/len(ix)
            assert np.isclose(expected.sum(),w.sum())
            rw=w[rot]
            assert np.all(rw.sum(axis=1)==w.sum())
            for size in GRIDS:
                key=f"{kind}_{size}m";c=r["cells"][size];k=int(c.max())+1
                p=distribution(c,np.ones(n),k);q=distribution(c,w,k);ref=distribution(c,expected,k)
                s=js(q,ref)
                nv=np.asarray([js(distribution(c,a,k),ref) for a in rw])
                actual.setdefault(key,[]).append(s);null.setdefault(key,[]).append(nv)
                geo.setdefault(key,[]).append({"js_Q_P":js(q,p),"tv_Q_P":measures(q,p)["total_variation"],"tv_Q_R":measures(q,ref)["total_variation"],"effective_cells_P":float(np.exp(entropy(p))),"effective_cells_Q":float(np.exp(entropy(q))),"effective_cells_R":float(np.exp(entropy(ref))),"max_mass_P":float(p.max()),"max_mass_Q":float(q.max()),"max_mass_R":float(ref.max()),"n_cells":k})
    out={}
    for key in actual:
        a=avg_animal(rows,actual[key]);sim=avg_animal(rows,null[key])
        ref=sim.mean(axis=0);excess=a-sim.mean(axis=1)
        loo=(excess.sum()-excess)/(len(excess)-1)
        v={"equal_animal_mean_JS_Q_R":float(a.mean()),"reference_JS_q05_median_q95":np.quantile(ref,[.05,.5,.95]).tolist(),"reference_JS_mean":float(ref.mean()),"mean_excess":float(excess.mean()),"positive_animals":int((excess>0).sum()),"animal_excess_quantiles":quant(excess),"leave_one_animal_excess_range":[float(loo.min()),float(loo.max())],"reference_gate":bool(a.mean()>np.quantile(ref,.95) and loo.min()>0)}
        v["equal_animal_geometry"]={name:float(avg_animal(rows,[z[name] for z in geo[key]]).mean()) for name in geo[key][0]}
        out[key]=v
    return out
def test():
    assert np.isclose(js(np.array([1.,0.]),np.array([0.,1.])),np.log(2))
    assert js(np.array([.5,.5]),np.array([.5,.5]))==0
    assert np.allclose(distribution(np.array([0,1,1]),np.array([2,1,1]),2),[.5,.5])
    rows=[{"animal":"A"},{"animal":"A"},{"animal":"B"}]
    assert np.allclose(avg_animal(rows,[1,3,5]),[2,5])
def run():
    test();o={"scope":"detected buzz mark spatial divergence, not true foraging or detection-adjusted intensity","test":"PASS","sources":{},"status":"SOURCE_REVIEW"}
    raw={}
    for k in ["gps","reference","readme"]:
        b,r=get(k);o["sources"][k]=r
        if b is None:o["status"]="STOP_SOURCE";return o
        raw[k]=b
    assert hashlib.sha256(raw["reference"]).hexdigest()==REF_SHA
    g,r=read(raw["gps"]),read(raw["reference"])
    assert r["behavior-according-to"].str.strip().str.casefold().eq("values indicate buzz count").all()
    assert r["duty-cycle"].str.strip().nunique()==1
    g,a=attach(g,r);o["deployment_join"]=a
    if g is None:o["status"]="STOP_DEPLOYMENT_JOIN";return o
    rows,s=collect(g);o["support"]=s
    if len(rows)<8 or s["eligible_animals"]<6:o["status"]="STOP_LOW_SUPPORT";return o
    o["reference"]={"rotations":B,"seed":SEED,"strata":"UTC hour crossed with contiguous fix segment (gap>60s) within deployment","interpretation":"descriptive reference only; no exchangeability or actual recording effort guarantee"}
    o["results"]=analyze(rows);o["primary_gate"]=o["results"]["count_1000m"]["reference_gate"]
    o["status"]="COMPLETE";return o
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
