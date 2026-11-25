"""V48 radial calibration likelihood comparison on withheld nominal configurations.
No axis relabeling, ecological outcomes, source code execution or raw rows exported.
"""
import csv,io,json,math
from collections import Counter,defaultdict
import numpy as np
from airspace_calibration_schema_v47 import fetch,extract,sha
from roost_fd_source_audit_v2 import OUT
PINS={"calibration_csv":"f56d9a7c89fc09e29c6f50a9edde86a02f790255a7a6a6f2ff33c107532bf29f",
 "calibration_readme":"a3946d785cc8564945f84b2583a1484e124684cbc8ee5c2b9c413832f65063cb",
 "calibration_rmd":"2aa0ac113e477bc3bfc33aba9b42613d08b2d11b1f659bd21018a986100e53aa"}
def quant(x):
    x=np.asarray(x,float)
    if not len(x):return {}
    return {k:float(v) for k,v in zip(("min","q10","q25","median","q75","q90","q95","max"),
      np.quantile(x,[0,.1,.25,.5,.75,.9,.95,1]))}
def group_weights(g):
    g=np.asarray(g);c=Counter(g.tolist());w=np.asarray([1/(len(c)*c[k]) for k in g],float)
    assert np.isclose(w.sum(),1,rtol=0,atol=1e-12)
    return w
def weighted_q(x,w,p):
    order=np.argsort(x,kind="stable");a=np.asarray(x)[order];v=np.cumsum(w[order]);v/=v[-1]
    return float(a[min(np.searchsorted(v,p,side="left"),len(a)-1)])
def describe(x,w):
    x=np.asarray(x,float);a=np.abs(x)
    return {"mean_bias":float(np.sum(w*x)),"RMSE":float(np.sqrt(np.sum(w*x*x))),
       "mean_absolute_error":float(np.sum(w*a)),"median_absolute_error":weighted_q(a,w,.5),
       "q90_absolute_error":weighted_q(a,w,.9),"signed_min":float(x.min()),"signed_max":float(x.max())}
def discrepancies(a,b,tol):
    x=a-b;return {"mean_difference":float(x.mean()),"absolute_discrepancy":quant(np.abs(x)),
      "fraction_within_fixed_diagnostic_tolerance":float(np.mean(np.abs(x)<=tol)),"tolerance":tol}
def load():
    d=extract(fetch())
    assert all(sha(d[k])==h for k,h in PINS.items())
    r=csv.reader(io.StringIO(d["calibration_csv"].decode("utf-8-sig"),newline=""))
    h=next(r);rows=list(r)
    assert len(rows)==1373 and len(h)==39 and len(set(h))==38
    assert h[0:14]==["Call_ID","Call_type","Shape","LsPos","LsPos2","Az","Elev","RM0","RM1","RM2","RM3","Tp_C","RH_percent","Speed_sound_msec"]
    assert h[20:26]==["TOAD_X","TOAD_Y","TOAD_Y","TOAD_dist_to_mic","Error_TOAD_dist","Error_TOAD_dist_prcent"]
    assert all(len(z)==39 for z in rows) and len({tuple(z) for z in rows})==1373
    def num(i):
        a=np.array([float(row[i]) for row in rows],float)
        assert np.isfinite(a).all()
        return a
    setting=np.column_stack([num(i) for i in (3,4,5,6)])
    distances=np.column_stack([num(i) for i in range(7,11)])
    xyz=np.column_stack([num(i) for i in range(20,23)])
    rhat=num(23);err=num(24);pct=num(25)
    assert (distances>0).all() and (rhat>0).all()
    nominal=[tuple(x[[0,2,3]]) for x in setting]
    return {"setting":setting,"nominal":nominal,"distances":distances,"estimate":rhat,
        "coord_triplet":xyz,"stored_error":err,"stored_percent":pct,
        "call_types":[z[1] for z in rows]}
def geometry(a):
    # Group configurations connected by a repeated exact reference-distance vector.
    nominal=a["nominal"];ng=sorted(set(nominal));idx={k:i for i,k in enumerate(ng)}
    par=list(range(len(ng)));owners=defaultdict(set);vectors=defaultdict(set);categories=defaultdict(set)
    def root(i):
        while par[i]!=i:
            par[i]=par[par[i]];i=par[i]
        return i
    for k,vec,st in zip(nominal,a["distances"],a["setting"]):
        v=tuple(vec);i=idx[k];owners[v].add(i);vectors[i].add(v);categories[st[0]].add(st[1])
    for ids in owners.values():
        ii=sorted(ids)
        for j in ii[1:]:par[root(j)]=root(ii[0])
    g=np.array([root(idx[k]) for k in nominal],int)
    counts=Counter(g.tolist());dist_cls=a["setting"][:,0]
    eff_cls=defaultdict(set)
    for k,x in zip(g,dist_cls):eff_cls[int(k)].add(float(x))
    nominal_sizes=Counter(nominal)
    o={"nominal_groups":len(ng),"effective_connected_groups":len(counts),
       "nominal_signal_count":quant(list(nominal_sizes.values())),
       "effective_signal_count":quant(list(counts.values())),
       "reference_vector_count":len(owners),
       "reference_vectors_shared_across_nominal_groups":sum(len(x)>1 for x in owners.values()),
       "nominal_groups_with_multiple_reference_vectors":sum(len(x)>1 for x in vectors.values()),
       "nominal_distance_classes":len(categories),
       "distance_class_to_multiple_LsPos2_count":sum(len(x)>1 for x in categories.values()),
       "effective_groups_spanning_distance_classes":sum(len(x)>1 for x in eff_cls.values()),
       "call_type_categories":len(set(a["call_types"]))}
    o["gate_pass"]=bool(len(ng)>=30 and len(counts)>=30 and min(nominal_sizes.values())>=2)
    return g,dist_cls,o
def score(e,r,s):
    assert np.isfinite(s).all() and (np.asarray(s)>0).all()
    return -.5*math.log(2*math.pi)-np.log(s)-.5*(e/s)**2
def cv(e,r,g,block):
    # Whole geometry holdout, or whole distance class holdout. All folds use equal-geometry weights.
    folds=[];sc0=np.zeros(len(e));sc1=np.zeros(len(e));s0=np.zeros(len(e));s1=np.zeros(len(e))
    for k in sorted(set(block.tolist())):
        te=block==k;tr=~te;assert te.any() and tr.any()
        w=group_weights(g[tr])
        a=float(np.sqrt(np.sum(w*e[tr]**2)));b=float(np.sqrt(np.sum(w*(e[tr]/r[tr])**2)))
        assert a>0 and b>0 and math.isfinite(a+b)
        s0[te]=a;s1[te]=b*r[te]
        sc0[te]=score(e[te],r[te],s0[te]);sc1[te]=score(e[te],r[te],s1[te])
        wt=group_weights(g[te]);folds.append(float(np.sum(wt*(sc1[te]-sc0[te]))))
    w=group_weights(g);z=1.6448536269514722
    def model(sc,s):
        return {"equal_geometry_mean_log_density_nats_per_measurement":float(np.sum(w*sc)),
          "equal_geometry_90pct_interval_coverage":float(np.sum(w*(np.abs(e)<=z*s))),
          "equal_geometry_mean_90pct_interval_width_m":float(np.sum(w*2*z*s)),
          "equal_geometry_standardized_residual_second_moment":float(np.sum(w*(e/s)**2))}
    wins=[]
    for k in sorted(set(g.tolist())):
        te=g==k;wins.append(float(np.mean(sc1[te]-sc0[te])))
    x=np.array(wins);om=(x.sum()-x)/(len(x)-1)
    return {"folds":len(folds),"K0_constant":model(sc0,s0),"K1_range_proportional":model(sc1,s1),
      "mean_gain_nats":float(np.sum(w*(sc1-sc0))),"geometry_groups_improved":int((x>0).sum()),
      "geometry_groups":len(x),"geometry_gain_distribution":quant(x),
      "leave_one_geometry_omission_mean_range":[float(om.min()),float(om.max())],
      "heldout_block_mean_gain_distribution":quant(folds),
      "descriptive_concordance":bool(x.mean()>0 and (x>0).sum()>len(x)/2)}
def test():
    g=np.array([0,0,1]);assert np.allclose(group_weights(g),[.25,.25,.5])
    e=np.array([.1,-.2]);r=np.array([2.,4.]);s=.05
    # Density transformation must include the Jacobian.
    assert np.allclose(score(e,r,s*r),score(e/r,r,np.full(len(e),s))-np.log(r))
    u=np.array([.1,-.2,.3,-.4]);gg=np.array([0,0,1,1])
    assert np.isclose(weighted_q(np.abs(u),group_weights(gg),.5),.2)
def main():
    dest=OUT/"audit_v48_radial_calibration.json"
    o={"status":"radial_calibration_only","claim_boundary":"Static known-range acoustic calibration conditional on detection and reference configuration. No registered axis errors, time covariance, camera transfer or ecology."}
    def save():dest.write_text(json.dumps(o,indent=2,allow_nan=False))
    save()
    try:
        test();o["synthetic_checks"]="pass"
        a=load();o["source_hashes_verified"]=True
        g,cls,geo=geometry(a);o["geometry_audit"]=geo;save()
        if not geo["gate_pass"]:
            o["status"]="STOP_LOW_SUPPORT";save();print(dest.read_text());return 0
        r=a["distances"][:,0];rhat=a["estimate"];e=rhat-r;pct=100*e/r
        o["rows"]=len(e);o["range_summary_m"]=quant(r)
        o["source_QA"]={"stored_error_vs_computed":discrepancies(a["stored_error"],e,.011),
          "stored_error_vs_negative_computed":discrepancies(a["stored_error"],-e,.011),
          "stored_percent_vs_computed":discrepancies(a["stored_percent"],pct,.11),
          "stored_percent_vs_negative_computed":discrepancies(a["stored_percent"],-pct,.11),
          "coordinate_triplet_norm_vs_estimated_range":discrepancies(np.linalg.norm(a["coord_triplet"],axis=1),rhat,.011)}
        o["radial_error_summary"]={"row_equal_m":describe(e,np.full(len(e),1/len(e))),
          "geometry_equal_m":describe(e,group_weights(g)),"row_equal_percent":describe(pct,np.full(len(e),1/len(e))),
          "geometry_equal_percent":describe(pct,group_weights(g))}
        o["primary"]=cv(e,r,g,g)
        eligible=len(set(cls.tolist()))==5 and geo["effective_groups_spanning_distance_classes"]==0 and all(len(set(g[cls==c].tolist()))>=2 for c in set(cls.tolist()))
        o["leave_distance_class_out_sensitivity"]=cv(e,r,g,cls) if eligible else {"status":"STOP_DISTANCE_CLASS_SUPPORT"}
    except Exception as ex:
        import traceback
        o["status"]="blocked";o["error_type"]=type(ex).__name__;o["failure_functions"]=[x.name for x in traceback.extract_tb(ex.__traceback__)[-5:]]
    save();print(dest.read_text())
    return 2 if o["status"]=="blocked" else 0
if __name__=="__main__":raise SystemExit(main())
