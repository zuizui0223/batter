"""V42 paired grid-origin robustness and sparse-mark concentration diagnostic."""
import concurrent.futures as cf,hashlib,json,pathlib,time
import numpy as np
import pandas as pd
from pyproj import Transformer
from hurme_label_semantics_v40 import get,read
from hurme_detected_functional_space_v41 import B,SEED,GRIDS,REF_SHA,attach,avg_animal,quant,distribution,entropy,js,test as v41_test
OUT=pathlib.Path("results/hurme_functional_space_v42.json")
OFFSETS=((0.,0.),(.5,0.),(0.,.5),(.5,.5))
EXPECTED={
"count_1000m":(.17244395669635498,.1584257657171135),
"count_500m":(.2186543906632406,.22714290452839878),
"count_2000m":(.10823325884594472,.09984457385563417),
"positive_fix_1000m":(.16803952123299953,.1546756596428349),
"positive_fix_500m":(.21431411843014245,.22250466650688034),
"positive_fix_2000m":(.10537388409834314,.0976258835298349)}
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
        rows.append({"xy":np.column_stack([x,y]),"animal":d["individual-local-identifier"].iloc[0],"marks":marks,"groups":groups,"cells":cells})
        support.append([n,pos,int(marks.sum()),len(groups),sum(bool(marks[ix].sum()) for ix in groups)])
    info={"eligible_deployments":len(rows),"eligible_animals":len(set(r["animal"] for r in rows)),"eligible_fixes":sum(len(r["marks"]) for r in rows),"eligible_positive_fixes":sum(int(np.count_nonzero(r["marks"])) for r in rows),"eligible_detected_buzzes":sum(int(r["marks"].sum()) for r in rows),"excluded_deployments":excluded,"eligible_deployment_support_quantiles":{k:quant([a[i] for a in support]) for i,k in enumerate(["fixes","positive_fixes","buzzes","time_strata","mark_positive_strata"])}}
    return rows,info

def metric(q,r):
    return np.array([js(q,r),entropy(r)-entropy(q)])
def summarize(rows,a,s):
    obs=avg_animal(rows,a);sim=avg_animal(rows,s)
    excess=obs-sim.mean(axis=1)
    rr=sim.mean(axis=0)
    loo=(excess.sum(axis=0)-excess)/(len(excess)-1)
    result={}
    for j,k in enumerate(("displacement_JS","concentration_log_effective_cell_ratio")):
        m=float(obs[:,j].mean());n=rr[:,j]
        result[k]={"observed":m,"reference_mean":float(n.mean()),"reference_q05_median_q95":np.quantile(n,[.05,.5,.95]).tolist(),
        "excess":float(excess[:,j].mean()),"positive_animals":int((excess[:,j]>0).sum()),"leave_one_animal_excess_range":[float(loo[:,j].min()),float(loo[:,j].max())],
        "gate":bool(m>np.quantile(n,.95) and loo[:,j].min()>0)}
    return result
def analyze(rows):
    rng=np.random.default_rng(SEED);observed={};simulated={}
    for r in rows:
        n=len(r["marks"]);rot=np.tile(np.arange(n),(B,1))
        for ix in r["groups"]:
            if len(ix)>1:
                sh=rng.integers(0,len(ix),size=B)
                rot[:,ix]=ix[(np.arange(len(ix))[None,:]+sh[:,None])%len(ix)]
        for kind,w in (("count",r["marks"]),("positive_fix",(r["marks"]>0).astype(int))):
            expected=np.zeros(n)
            for ix in r["groups"]:expected[ix]=float(w[ix].sum())/len(ix)
            rw=w[rot];assert np.all(rw.sum(1)==w.sum())
            for size in GRIDS:
                aa=[];ss=[]
                for off in OFFSETS:
                    _,cc=np.unique(np.floor(r["xy"]/size-np.array(off)).astype(np.int64),axis=0,return_inverse=True)
                    if off==(0.,0.):assert np.array_equal(cc,r["cells"][size])
                    k=int(cc.max())+1
                    ref=distribution(cc,expected,k);q=distribution(cc,w,k)
                    aa.append(metric(q,ref))
                    ss.append(np.asarray([metric(distribution(cc,z,k),ref) for z in rw]))
                key=f"{kind}_{size}m";observed.setdefault(key,[]).append(np.stack(aa));simulated.setdefault(key,[]).append(np.stack(ss))
    out={}
    for key,a in observed.items():
        a=np.stack(a);s=np.stack(simulated[key])
        per=[summarize(rows,a[:,i,:],s[:,i,:,:]) for i in range(4)]
        avg=summarize(rows,a.mean(1),s.mean(1))
        for k in avg:
            avg[k]["passing_origins"]=sum(p[k]["gate"] for p in per)
            avg[k]["origin_robust_gate"]=bool(avg[k]["gate"] and avg[k]["passing_origins"]>=3)
        first=per[0]["displacement_JS"];expect=EXPECTED[key]
        drift=max(abs(first["observed"]-expect[0]),abs(first["reference_mean"]-expect[1]))
        out[key]={"zero_origin_reproduction_drift":drift,"reproduction_pass":bool(drift<=1e-10),"origins":[{"offset":list(o),"metrics":p} for o,p in zip(OFFSETS,per)],"equal_origin":avg}
    return out
def get_retry(k):
    b,r=get(k);first=dict(r)
    if b is None and "TimeoutError" in r.get("error",""):
        time.sleep(2);b,r=get(k)
        return k,b,{"attempts":[first,dict(r)],**r}
    return k,b,{"attempts":[first],**r}
def run():
    v41_test()
    assert np.allclose(metric(np.array([1.,0.]),np.array([.5,.5])),[js(np.array([1.,0.]),np.array([.5,.5])),np.log(2)])
    o={"scope":"observed detected-mark displacement vs concentration; paired grid origin sensitivity","status":"SOURCE_REVIEW","sources":{}}
    raw={}
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for k,b,r in ex.map(get_retry,["gps","reference","readme"]):
            o["sources"][k]=r
            if b is not None:raw[k]=b
    if len(raw)!=3:o["status"]="STOP_SOURCE";return o
    assert hashlib.sha256(raw["reference"]).hexdigest()==REF_SHA
    g,r=read(raw["gps"]),read(raw["reference"])
    assert r["behavior-according-to"].str.strip().str.casefold().eq("values indicate buzz count").all()
    g,a=attach(g,r);o["deployment_join"]=a
    if g is None:o["status"]="STOP_DEPLOYMENT_JOIN";return o
    rows,s=collect(g);o["support"]=s
    if (s["eligible_deployments"],s["eligible_animals"],s["eligible_fixes"],s["eligible_positive_fixes"],s["eligible_detected_buzzes"])!=(14,11,13855,602,693):
        o["status"]="STOP_SUPPORT_DRIFT";return o
    o["results"]=analyze(rows)
    o["status"]="COMPLETE" if all(v["reproduction_pass"] for v in o["results"].values()) else "STOP_V41_REPRODUCTION"
    if o["status"]=="COMPLETE":o["primary"]=o["results"]["count_1000m"]["equal_origin"]
    return o
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
