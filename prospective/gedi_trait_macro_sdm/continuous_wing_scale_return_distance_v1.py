"""Numerical observed-return distance diagnostic on four fixed metre-verified EPT patches.
See CONTINUOUS_WING_SCALE_RETURN_DISTANCE_CONTRACT_V1.md.
Not true empty space, flight feasibility, or a fitted ecological response.
"""
import hashlib,itertools,json,math,pathlib,sys
import numpy as np,pandas as pd
from scipy.spatial import cKDTree
import return_topology_feasibility_v1 as v
ID=v.ID
POS={"NH1":[9],"WA1":[2,6,8]}[ID]
O=pathlib.Path("continuous_wing_distance")/ID;O.mkdir(parents=True,exist_ok=True)
V2=pathlib.Path("v2")/ID/"report.json"
R={"stage":"continuous wing-scale nearest observed return diagnostic","project":ID,"status":"START","patches":[],"new_fit":False,"limits":["Numerical distance from sampled XYZ point to observed nonground return; lack of a nearby return does not mean physical free space.","Half wing span is an illustrative radius, not a flight clearance requirement.","Fixed selected patches from previously inspected geometry only, no biological detections or connectivity claims.","Hypothetical perturbation bounds are mathematical sensitivity, not measured positional uncertainty. Monte Carlo errors conditional on sampled cloud only."]}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else x.tolist() if isinstance(x,np.ndarray) else None)
    (O/"report.json").write_text(s+"\n");print("CONTINUOUS_WING_REPORT="+s,flush=True)
def truth(x):
    t=x.astype(str).str.lower();assert t.isin(["true","false"]).all()
    return t.eq("true")
def fractions(d,r):
    a=np.sort(d);return 1-np.searchsorted(a,r,side="right")/len(a)
def summary(primary,half,idw,r,names,cohorts):
    p=fractions(primary,r);h=fractions(half,r);t=fractions(idw,r)
    out={}
    for k,ix in cohorts.items():
        a,b,c=p[ix],h[ix],t[ix]
        # For pairs of species, measure whether uncertainty in contrast,
        # rather than common shift, is at least its full-data magnitude.
        i,j=np.triu_indices(len(ix),k=1)
        delta=a[i]-a[j]
        active=abs(delta)>0
        dh=(b[i]-b[j])-delta;dt=(c[i]-c[j])-delta
        out[k]={"species":len(ix),"radius_min_m":float(r[ix].min()),"radius_max_m":float(r[ix].max()),"full_fraction_min":float(a.min()),"full_fraction_median":float(np.median(a)),"full_fraction_max":float(a.max()),"species_spread":float(np.ptp(a)),"thinning_median_absolute_change":float(np.median(abs(b-a))),"thinning_max_absolute_change":float(max(abs(b-a))),"terrain_median_absolute_change":float(np.median(abs(c-a))),"terrain_max_absolute_change":float(max(abs(c-a))),"pairs":len(i),"nonzero_full_contrasts":int(active.sum()),"thinning_contrast_change_ge_full_contrast":int((active&(abs(dh)>=abs(delta))).sum()),"terrain_contrast_change_ge_full_contrast":int((active&(abs(dt)>=abs(delta))).sum())}
        out[k]["hypothetical_distance_perturbation"]={}
        for e in [.05,.1,.25]:
            lo=fractions(primary,r[ix]+e);hi=fractions(primary,np.maximum(0,r[ix]-e))
            out[k]["hypothetical_distance_perturbation"][str(e)]={"median_interval_width":float(np.median(hi-lo)),"max_interval_width":float(max(hi-lo))}
    return out,p,h,t
def main():
    # All original EPT node bytes must match the independently verified V2
    # acquisition; keep the fixed source and do not select patches by result.
    prior=json.loads(V2.read_text())
    assert prior["status"]=="COMPLETE_GEOMETRY_ONLY"
    pp={x["position_index"]:x for x in prior["patches"] if x["status"]=="COMPLETE_GEOMETRY_ONLY"}
    assert sorted(pp)==POS
    old={x["path"]:x["sha256"] for x in prior["transfers"]}
    assert all(x["source_nodes_rehashed"] and x["prior_observed_replayed"] and x["vertical_unit_audit"]["hypothesis"]=="metre" for x in pp.values())
    q=pathlib.Path("spans/physical_wing_span.csv");assert sha(q)=="5846e23da9cda8bd3f60e0e539ebc12fb622f20b1cd5ca504b6517755b7c92fb"
    d=pd.read_csv(q).set_index("scientificName.iucn").sort_index();assert len(d)==280 and d.index.is_unique
    q=pathlib.Path("domain/frozen_trait_domain.csv");assert sha(q)=="6d9ba6bbada4e103606f09f15f25fab9cde13e26c2a15d6e3366fa48808f9f06"
    dom=pd.read_csv(q).set_index("scientificName.iucn");assert set(dom.index)==set(d.index)
    dom=dom.loc[d.index];r=d.half_span_m.to_numpy(float);assert np.isfinite(r).all() and (r>0).all() and np.allclose(r,d.span_m/2)
    fws=["Eptesicus fuscus","Lasiurus borealis","Lasiurus cinereus","Myotis lucifugus","Nycticeius humeralis","Perimyotis subflavus"]
    assert set(fws)<=set(d.index)
    cohorts={"global_280":np.arange(len(d)),"Europe_14":np.flatnonzero(truth(dom.training_species)),"FWS_6":np.flatnonzero(d.index.isin(fws))}
    assert [len(x) for x in cohorts.values()]==[280,14,6]
    v.synthetic();meta=v.getjson("ept.json");bb=meta["boundsConforming"];pos=list(itertools.product([.25,.5,.75],repeat=2))
    for j in POS:
        u,w=pos[j-1];ctr=[bb[0]+u*(bb[3]-bb[0]),bb[1]+w*(bb[4]-bb[1])]
        rec={"position_index":j};R["patches"].append(rec)
        a,info=v.acquire(meta,ctr)
        assert all(x.get("sha256")==old.get(x["path"]) for x in v.R["transfers"])
        rec["source_nodes_rehashed"]=True
        norm,reason=v.support(a,dict(info));assert reason is None
        # Replay the observed 1m graph exactly. The continuous distances below
        # are measured in original metric XYZ, not AGL-warped coordinates.
        expected=np.asarray(pp[j]["scales"]["full_1m"]["pre_dilation_layer_count_null"]["observed"])
        # V2 adds conditional component fraction in column 2.
        assert np.allclose(v.curves(v.vox(norm,1),1,[0,1,2]),expected[:,[0,1,3,4,5]],rtol=0,atol=1e-12)
        rec["original_1m_replay"]=True
        g=a[a[:,3]==2,:3];q=a[a[:,3]!=2,:3]
        assert len(g)>=8 and len(q)>1 and np.isfinite(a).all()
        rng=np.random.default_rng(np.random.SeedSequence([20261126,71,list(v.PROJECTS).index(ID),j]))
        xy=rng.uniform(-32,32,(131072,2));z=rng.uniform(2,30,131072)
        dist,idx=cKDTree(g[:,:2]).query(xy,k=8)
        valid=dist[:,0]<=3;rec["query_ground_support_fraction"]=float(valid.mean())
        if valid.mean()<.99:
            rec["status"]="STOP_QUERY_GROUND_SUPPORT";save();continue
        xy,z,dist,idx=xy[valid],z[valid],dist[valid],idx[valid]
        g0=g[idx[:,0],2]
        weight=np.where(dist<=3,1/np.maximum(dist,1e-6)**2,0)
        assert (weight.sum(1)>0).all()
        g1=(weight*g[idx,2]).sum(1)/weight.sum(1)
        u=np.column_stack([xy,z+g0]);w=np.column_stack([xy,z+g1])
        tree=cKDTree(q);d0=tree.query(u,k=1)[0];d1=tree.query(w,k=1)[0]
        # Fixed 50% thinning of nonground returns only.
        thin=rng.choice(len(q),len(q)//2,replace=False)
        dh=cKDTree(q[thin]).query(u,k=1)[0]
        assert np.all(dh+1e-10>=d0)
        assert np.all(np.abs(d1-d0)<=abs(g1-g0)+1e-9) # distance function 1-Lipschitz
        stats,p,h,t=summary(d0,dh,d1,r,d.index,cohorts)
        rec.update(status="COMPLETE_GEOMETRY_ONLY",sample_count=len(d0),nonground_points=len(q),ground_points=len(g),ground_elevation_method_difference_abs_quantiles=np.quantile(abs(g1-g0),[.5,.95,1]).tolist(),distance_quantiles_m=np.quantile(d0,[0,.01,.05,.1,.25,.5,.75,.95,1]).tolist(),cohorts=stats,maximum_binomial_MC_SE=float(np.max(np.sqrt(p*(1-p)/len(d0)))))
        s=d[["span_m","half_span_m"]].copy();s["full_fraction"]=p;s["half_points_fraction"]=h;s["alternative_ground_fraction"]=t
        path=O/("patch_"+str(j)+"_species_distance_fractions.csv");s.reset_index().to_csv(path,index=False);rec["species_output_sha256"]=sha(path)
        print("CONTINUOUS_WING_PATCH="+json.dumps({"position":j,"status":rec["status"],"cohorts":stats}),flush=True)
        save()
    R.update(status="COMPLETE_GEOMETRY_ONLY",completed_patches=sum(x["status"]=="COMPLETE_GEOMETRY_ONLY" for x in R["patches"]))
    save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:200]);save();raise
