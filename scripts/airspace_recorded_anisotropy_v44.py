"""V44: recorded-coordinate persistence, heldout road sites, not physical availability."""
import json,math,re
from collections import Counter,defaultdict
import numpy as np
from airspace_temporal_geometry_v42 import get,rows,stats
from roost_fd_source_audit_v2 import OUT

def source():
    h,rr=rows(get("omalley_csv"),",")
    assert len(rr)==23554
    assert {"Site","Date","Survey","BatID","TrackID","Frame","X","Y","Height"}<=set(h)
    code=get("omalley_R").decode("utf-8-sig",errors="replace")
    # Confirm author ordering, not an arbitrary grouping inferred from outcomes.
    calls=re.findall(r"\barrange\s*\(([^)]*)\)",code,re.I|re.S)
    assert any(all(re.search(r"\b"+k+r"\b",s) for k in ("BatID","TrackID","Frame")) for s in calls)
    groups=defaultdict(list);contexts=defaultdict(set)
    for r in rr:
        s=tuple(r[k] for k in ("Site","Date","Survey"))
        contexts[r["BatID"]].add(s)
        key=s+(r["BatID"],r["TrackID"])
        f=float(r["Frame"]);assert math.isfinite(f) and f.is_integer()
        xyz=np.array([float(r[k]) for k in ("X","Y","Height")],float)
        assert np.isfinite(xyz).all()
        groups[key].append((int(f),xyz))
    assert len(contexts)==400 and all(len(c)==1 for c in contexts.values())
    assert len(groups)==447 and len({k[:4] for k in groups})==400 and len({k[0] for k in groups})==9
    out=[]
    for k,v in groups.items():
        v.sort(key=lambda r:r[0]);f=np.array([x[0] for x in v],dtype=int)
        assert len(set(f))==len(f) and (np.diff(f)==1).all()
        out.append((k,np.array([x[1] for x in v],float)))
    return out

def windows(segments,lag):
    data=[]
    for k,x in segments:
        for a in range(0,len(x)-2*lag,2*lag):
            b=a+lag;c=b+lag
            u=x[b]-x[a];v=x[c]-x[b]
            data.append((k[0],k[:4],u,v))
    return data

def weights(sites,paths):
    per_site=defaultdict(set);per_path=Counter(paths)
    for s,p in zip(sites,paths):per_site[s].add(p)
    w=np.array([1/(len(per_site)*len(per_site[s])*per_path[p]) for s,p in zip(sites,paths)],float)
    assert np.isclose(w.sum(),1,rtol=0,atol=1e-10)
    return w
def fit(u,v,w):
    w=np.asarray(w,float);assert np.isclose(w.sum(),1)
    scale=np.sqrt(np.sum(w[:,None]*u*u,axis=0))
    assert np.isfinite(scale).all() and (scale>0).all()
    x=u/scale;y=v/scale
    dot=np.sum(w[:,None]*x*y,axis=0)
    denom=np.sum(w[:,None]*x*x,axis=0)
    common=float(dot.sum()/denom.sum())
    rh=float(dot[:2].sum()/denom[:2].sum());rv=float(dot[2]/denom[2])
    assert np.isfinite([common,rh,rv]).all()
    return scale,{"M0":np.ones(3),"M1":np.full(3,common),"M2":np.array([rh,rh,rv])}
def error(u,v,w,scale,b):
    e=v-u*b
    raw=np.sum(w[:,None]*e*e,axis=0)
    std=raw/(scale*scale)
    return {"std_mse":float(std.mean()),"std_axis_mse":std,"raw_axis_mse":raw}
def report(segments,lag):
    dd=windows(segments,lag)
    counts=defaultdict(set);per_site_windows=Counter()
    for s,p,u,v in dd:counts[s].add(p);per_site_windows[s]+=1
    all_sites=sorted({k[0] for k,_ in segments})
    keep={s for s in all_sites if len(counts[s])>=10}
    data=[d for d in dd if d[0] in keep]
    result={"status":"STOP_LOW_SUPPORT","lag_seconds":lag/50,
        "all_sites":len(all_sites),"candidate_windows":len(dd),
        "candidate_parent_paths":len({p for _,p,_,_ in dd}),
        "paths_per_site_before_gate":stats([len(counts[s]) for s in all_sites]),
        "sites_eligible":len(keep),"windows_after_gate":len(data),
        "parent_paths_after_gate":len({p for _,p,_,_ in data})}
    if len(keep)<6:return result
    sites=[d[0] for d in data];paths=[d[1] for d in data]
    u=np.array([d[2] for d in data]);v=np.array([d[3] for d in data])
    a=np.asarray(sites);folds=[]
    for s in sorted(keep):
        te=a==s;tr=~te
        train=[i for i in range(len(data)) if tr[i]]
        test=[i for i in range(len(data)) if te[i]]
        wt=weights([sites[i] for i in train],[paths[i] for i in train])
        we=weights([sites[i] for i in test],[paths[i] for i in test])
        scale,coef=fit(u[tr],v[tr],wt)
        err={k:error(u[te],v[te],we,scale,b) for k,b in coef.items()}
        folds.append((coef,err))
    models={}
    for k in ("M0","M1","M2"):
        models[k]={"equal_site_std_MSE":float(np.mean([e[k]["std_mse"] for b,e in folds])),
            "equal_site_std_axis_MSE":np.mean([e[k]["std_axis_mse"] for b,e in folds],axis=0).tolist(),
            "equal_site_raw_axis_RMSE_stored_units":np.sqrt(np.mean([e[k]["raw_axis_mse"] for b,e in folds],axis=0)).tolist()}
    def contrast(base,new):
        z=np.array([e[base]["std_mse"]-e[new]["std_mse"] for b,e in folds])
        a=np.mean([e[base]["std_axis_mse"]-e[new]["std_axis_mse"] for b,e in folds],axis=0)
        omit=(z.sum()-z)/(len(z)-1)
        return {"equal_site_mean_gain":float(z.mean()),"sites_improved":int((z>0).sum()),
            "site_gain_summary":stats(z.tolist()),"leave_one_site_omission_mean_range":[float(omit.min()),float(omit.max())],
            "std_axis_gain":a.tolist()}
    common=[float(b["M1"][0]) for b,e in folds]
    rh=[float(b["M2"][0]) for b,e in folds];rv=[float(b["M2"][2]) for b,e in folds]
    primary=contrast("M1","M2")
    result.update(status="SCORED",models=models,shared_persistence=contrast("M0","M1"),anisotropic_persistence=primary,
        rho_common=stats(common),rho_horizontal=stats(rh),rho_vertical=stats(rv),
        rho_horizontal_minus_vertical=stats([h-v for h,v in zip(rh,rv)]),
        all_folds_horizontal_gt_vertical=all(h>v for h,v in zip(rh,rv)),
        directional_concordance=bool(primary["equal_site_mean_gain"]>0 and primary["sites_improved"]>len(keep)/2 and all(h>v for h,v in zip(rh,rv))))
    return result

def test():
    u=np.array([[1,2,3],[-2,1,-1],[3,-1,2]],float);v=u*np.array([.8,.8,.2])
    w=np.ones(3)/3
    sc,b=fit(u,v,w)
    assert np.allclose(b["M2"],[.8,.8,.2])
    assert error(u,v,w,sc,b["M2"])["std_mse"]<1e-20
    fac=np.array([2,100,.001]);sc2,b2=fit(u*fac,v*fac,w)
    assert np.allclose(sc2,sc*fac) and np.allclose(b["M1"],b2["M1"])
    assert np.isclose(error(u,v,w,sc,b["M1"])["std_mse"],error(u*fac,v*fac,w,sc2,b2["M1"])["std_mse"])
    paths=[("a","p"),("a","p"),("a","q"),("b","r")]
    assert np.allclose(weights(["a","a","a","b"],paths),[.125,.125,.25,.5])
    # Two short segments are not concatenated into a spurious longer trajectory.
    xx=np.arange(18).reshape(6,3)
    assert not windows([(("s","d","v","p","1"),xx),(("s","d","v","p","2"),xx)],5)
    yy=np.arange(33).reshape(11,3)
    assert len(windows([(("s","d","v","p","1"),yy)],5))==1
def main():
    dest=OUT/"audit_v44_recorded_anisotropy.json"
    r={"status":"recorded_kinematics_only","claim_boundary":"Observed local coordinate increments conditional on complete recorded segments; no independently calibrated measurement error, actual obstacle availability, behavior labels or biological mechanism.",
        "scales":{}}
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save()
    try:
        test();r["synthetic_tests"]="pass"
        seg=source();r["source_structure_replayed"]=True
        for lag in (5,10):
            r["scales"][str(lag)]=report(seg,lag);save()
    except Exception as e:
        r["status"]="blocked";r["error_type"]=type(e).__name__
        import traceback
        r["failure_functions"]=[x.name for x in traceback.extract_tb(e.__traceback__)[-5:]]
    save();print(dest.read_text())
    return 0 if r["status"]=="recorded_kinematics_only" else 2
if __name__=="__main__":raise SystemExit(main())
