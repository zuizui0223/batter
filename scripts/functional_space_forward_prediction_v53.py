"""V53: within-track temporal transfer conditional on held-out GPS and mark totals."""
import json,pathlib
import numpy as np
import functional_space_common_minute_v52 as v52
from roeleke_minute_bundle_v50 import bundle_rotations
from hurme_functional_space_v42 import B,SEED,OFFSETS
from hurme_detected_functional_space_v41 import avg_animal,quant
OUT=pathlib.Path("results/functional_space_forward_prediction_v53.json")
ALPHA=5.
def partition(r):
    bundles=sorted([ix for group in r["bundles"] for ix in group],key=lambda ix:int(ix[0]))
    n=len(r["marks"]);assert np.array_equal(np.concatenate(bundles),np.arange(n))
    mid=len(bundles)//2
    if mid<=5 or len(bundles)-mid<=5:return None,"insufficient_minutes"
    train=np.concatenate(bundles[:mid-5]);test=np.concatenate(bundles[mid+5:])
    assert len(train) and len(test) and train[-1]<test[0]
    if min(len(train),len(test))<40:return None,"below40_fixes"
    if min(np.count_nonzero(r["marks"][train]),np.count_nonzero(r["marks"][test]))<5:return None,"below5_positive_fixes"
    # Whole minute bundles remain intact; no marks are moved across the temporal split.
    train_groups=[];test_groups=[]
    for group in r["bundles"]:
        a=[ix for ix in group if ix[-1]<=train[-1]]
        b=[ix for ix in group if ix[0]>=test[0]]
        if a:train_groups.append(a)
        if b:test_groups.append(np.concatenate(b))
    assert np.array_equal(np.sort(np.concatenate([ix for group in train_groups for ix in group])),train)
    assert np.array_equal(np.sort(np.concatenate(test_groups)),test)
    return dict(r,train=train,test=test,train_groups=train_groups,test_groups=test_groups,embargo_fixes=n-len(train)-len(test)),"PASS"
def scores(rate,cc,w,test_groups):
    """One held-out score per row of rate; probabilities normalized within test strata."""
    rate=np.asarray(rate,float);assert rate.ndim==2 and (rate>0).all()
    num=np.zeros(len(rate));total=0.
    for ix in test_groups:
        m=float(w[ix].sum())
        if m==0:continue
        z=rate[:,cc[ix]]
        num+=np.log(z)@w[ix]-m*np.log(z.mean(axis=1))
        total+=m
    assert total>0
    return num/total
def fit_and_score(r,cc,w,rot):
    train=r["train"];test=r["test"]
    k=int(cc.max())+1
    expected=np.zeros(len(w))
    for group in r["train_groups"]:
        ix=np.concatenate(group);expected[ix]=float(w[ix].sum())/len(ix)
    E=np.bincount(cc[train],weights=expected[train],minlength=k)
    # First draw is actual training marks; remaining draws permute ONLY training indices.
    raw=np.vstack([w[train],w[rot[:,train]]])
    assert np.all(raw.sum(axis=1)==w[train].sum())
    K=np.stack([np.bincount(cc[train],weights=z,minlength=k) for z in raw])
    rate=(K+ALPHA)/(E[None,:]+ALPHA)
    assert np.all(rate[:,E==0]==1.)
    return scores(rate,cc,w,r["test_groups"])
def summarize(rows,values):
    # shape: tracks x (actual + 499 controls)
    a=avg_animal(rows,np.asarray(values,float));obs=a[:,0];ref=a[:,1:]
    excess=obs-ref.mean(axis=1);n=len(obs)
    assert n>=2
    loo=(obs.sum()-obs)/(n-1);le=(excess.sum()-excess)/(n-1)
    r=ref.mean(axis=0);m=float(obs.mean())
    return {"mean_gain_nats_per_mark":m,"reference_mean":float(r.mean()),"reference_q05_median_q95":np.quantile(r,[.05,.5,.95]).tolist(),"excess_gain":float(excess.mean()),"positive_gain_animals":int((obs>0).sum()),"positive_excess_animals":int((excess>0).sum()),"leave_one_animal_gain_range":[float(loo.min()),float(loo.max())],"leave_one_animal_excess_range":[float(le.min()),float(le.max())],"gate":bool(m>0 and loo.min()>0 and m>np.quantile(r,.95) and le.min()>0)}
def test():
    cc=np.array([0,0,1,1]);w=np.array([1,0,0,0])
    z=scores(np.array([[1.,1.],[2.,1.]]),cc,w,[np.arange(4)])
    assert np.allclose(z,[0.,np.log(4/3)])
    # Training marks in cell 0, balanced availability; test marks in cell 0.
    r={"train":np.arange(4),"test":np.arange(4,8),"train_groups":[[np.arange(4)]],"test_groups":[np.arange(4,8)]}
    cc=np.array([0,0,1,1,0,0,1,1]);w=np.array([1,1,0,0,1,1,0,0])
    rot=np.array([[2,3,0,1,4,5,6,7]])
    z=fit_and_score(r,cc,w,rot);assert z[0]>0 and z[1]<0
    # Changing test marks cannot change the training rates (fit only uses train).
    z2=fit_and_score(r,cc,np.array([1,1,0,0,0,0,1,1]),rot);assert z2[0]<0 and z2[1]>0
def evaluate(rows,s,o):
    o["v52_support"]=s
    if s["movable_mark_fraction"]<.5:o["status"]="STOP_V52_SUPPORT";return o
    valid=[];excluded={}
    for r in rows:
        x,why=partition(r)
        if x is None:excluded[why]=excluded.get(why,0)+1
        else:valid.append(x)
    animals=len(set(r["animal"] for r in valid))
    support={"eligible_tracks":len(valid),"eligible_animals":animals,"excluded_tracks":excluded,
        "train_fixes":sum(len(r["train"]) for r in valid),"test_fixes":sum(len(r["test"]) for r in valid),
        "embargo_fixes":sum(r["embargo_fixes"] for r in valid),
        "train_marks":sum(int(r["marks"][r["train"]].sum()) for r in valid),"test_marks":sum(int(r["marks"][r["test"]].sum()) for r in valid),
        "train_positive_fixes":sum(int(np.count_nonzero(r["marks"][r["train"]])) for r in valid),"test_positive_fixes":sum(int(np.count_nonzero(r["marks"][r["test"]])) for r in valid)}
    o["support"]=support
    if animals<6:o["status"]="STOP_LOW_PREDICTION_SUPPORT";return o
    rng=np.random.default_rng(SEED);vals={k:[] for k in ("count","positive_fix")};overlap=[]
    for r in valid:
        w=r["marks"];rot=bundle_rotations(r["train_groups"],len(w),B,rng)
        assert np.all(rot[:,r["test"]]==r["test"])
        assert np.all(np.isin(rot[:,r["train"]],r["train"]))
        rowscores={k:[] for k in vals};ov=[]
        for off in OFFSETS:
            _,cc=np.unique(np.floor(r["xy"]/1000-np.array(off)).astype(np.int64),axis=0,return_inverse=True)
            ov.append(float(np.isin(cc[r["test"]],np.unique(cc[r["train"]])).mean()))
            for k,ww in (("count",w),("positive_fix",(w>0).astype(np.int64))):
                rowscores[k].append(fit_and_score(r,cc,ww,rot))
        overlap.append(ov)
        for k in vals:vals[k].append(np.stack(rowscores[k]))
    support["equal_animal_test_fix_overlap_by_origin"]=avg_animal(valid,np.asarray(overlap)).mean(axis=0).tolist()
    o["results"]={}
    for k,v in vals.items():
        a=np.stack(v)
        per=[summarize(valid,a[:,i,:]) for i in range(4)]
        m=summarize(valid,a.mean(axis=1));m["passing_origins"]=sum(p["gate"] for p in per)
        m["origin_robust_gate"]=bool(m["gate"] and m["passing_origins"]>=3)
        o["results"][k]={"equal_origin":m,"origins":[{"offset":list(off),"metrics":p} for off,p in zip(OFFSETS,per)]}
    o["gate"]=bool(all(v["equal_origin"]["origin_robust_gate"] for v in o["results"].values()))
    o["status"]="COMPLETE";return o
def run():
    test();v52.v50.test();v52.v41.test()
    # Replace only the terminal endpoint; exact source admission and V52 track selection unchanged.
    v52.evaluate=evaluate
    a=v52.safe(v52.vivesi);b=v52.safe(v52.noctule)
    return {"scope":"forward conditional detected-mark allocation; not prospective path or feeding prediction","synthetic_tests":"PASS","reference":{"grid_m":1000,"origins":4,"train_only_rotations":B,"seed":SEED,"pseudocount":ALPHA,"split":"first vs latter occupied-minute halves, exclude 5 minutes each side of split","actual_audio_effort":"unknown"},"vivesi":a,"noctule":b,"common_prediction_gate":bool(a.get("status")=="COMPLETE" and b.get("status")=="COMPLETE" and a.get("gate") and b.get("gate"))}
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error_type":type(e).__name__}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
