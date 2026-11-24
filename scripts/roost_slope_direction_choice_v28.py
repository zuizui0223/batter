"""V28 directional choice conditional on observed step length, geometric controls only.
No coordinates, tag IDs, individual records, or cave locations in output.
"""
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
from roost_fd_source_audit_v2 import OUT
from roost_slope_matched_panels_v21 import summary
from roost_slope_device_matched_scale_v24 import load,tadarida,anchors
from roost_slope_error_dem_v25 import Copernicus
SEED=20261124
EARTH=6371008.8
PANELS=["tadarida","phyllostomus_2016","phyllostomus_2023"]
NCONTROL=24
NAMES=["cos_turn","sin_turn","cos_2turn","sin_2turn","cos_heading","sin_heading","cos_2heading","sin_2heading","abs_net_gradient","signed_net_gradient"]

def displacement(a,b):
    la,lb=np.deg2rad([a.lat,b.lat]);dl=np.deg2rad(b.lon-a.lon)
    hav=np.sin((lb-la)/2)**2+np.cos(la)*np.cos(lb)*np.sin(dl/2)**2
    d=2*EARTH*np.arcsin(np.sqrt(np.clip(hav,0,1)))
    bearing=np.arctan2(np.sin(dl)*np.cos(lb),np.cos(la)*np.sin(lb)-np.sin(la)*np.cos(lb)*np.cos(dl))
    return float(d),float(bearing)

def destinations(lat,lon,bearing,length):
    la=np.deg2rad(lat);lo=np.deg2rad(lon);arc=length/EARTH
    ll=np.arcsin(np.clip(np.sin(la)*np.cos(arc)+np.cos(la)*np.sin(arc)*np.cos(bearing),-1,1))
    oo=lo+np.arctan2(np.sin(bearing)*np.sin(arc)*np.cos(la),np.cos(arc)-np.sin(la)*np.sin(ll))
    return np.rad2deg(ll),(np.rad2deg(oo)+180)%360-180

def candidate_features(head,history,gradient):
    t=head-history
    return np.column_stack([np.cos(t),np.sin(t),np.cos(2*t),np.sin(2*t),np.cos(head),np.sin(head),np.cos(2*head),np.sin(2*head),np.abs(gradient),gradient])

def choices(d,dem):
    a,info=anchors(d,60,5);rng=np.random.default_rng(SEED)
    feats=[];animals=[];counts={"candidate_windows":0,"horizontal_gate":0,"incomplete_DEM_sets":0,"complete_sets_before_animal_gate":0}
    if a.empty:return None,None,{**info,**counts}
    for (animal,session),g in a.groupby(["animal","session"],sort=True):
        g=g.sort_values("time").reset_index(drop=True)
        for i in range(0,len(g)-2,2):
            a0,a1,a2=[g.iloc[j] for j in (i,i+1,i+2)]
            counts["candidate_windows"]+=1
            d0,t0=displacement(a0,a1);d1,t1=displacement(a1,a2)
            dt0=(a1.time-a0.time).total_seconds();dt1=(a2.time-a1.time).total_seconds()
            if not(55<=dt0<=65 and 55<=dt1<=65 and 2<=d0/dt0<=50 and 2<=d1/dt1<=50):continue
            counts["horizontal_gate"]+=1
            # Draw controls before any DEM sampling; no replacement after missing data.
            h=np.r_[t1,rng.uniform(-np.pi,np.pi,NCONTROL)]
            lat,lon=destinations(a1.lat,a1.lon,h,d1)
            lat[0]=a2.lat;lon[0]=a2.lon
            start=dem.value(float(a1.lat),float(a1.lon))
            if start is None:
                counts["incomplete_DEM_sets"]+=1;continue
            z=[dem.value(float(la),float(lo)) for la,lo in zip(lat,lon)]
            if any(v is None or not np.isfinite(v) for v in z):
                counts["incomplete_DEM_sets"]+=1;continue
            gradient=(np.asarray(z,float)-start)/d1
            X=candidate_features(h,t0,gradient)
            if not np.isfinite(X).all():raise ValueError("nonfinite choice features")
            feats.append(X);animals.append(str(animal))
    counts["complete_sets_before_animal_gate"]=len(feats)
    if not feats:return None,None,{**info,**counts}
    X=np.array(feats);aid=np.array(animals)
    cnt=pd.Series(aid).value_counts();keep=np.isin(aid,cnt[cnt>=50].index)
    return X[keep],aid[keep],{**info,**counts,"animals_before_gate":len(cnt),"animals_after_gate":int(len(set(aid[keep])))}

def center(X):return X-X.mean(axis=1,keepdims=True)

def fit_choice(X,w):
    X=center(X)
    s=np.sqrt(np.average(np.mean(X*X,axis=1),axis=0,weights=w))
    s=np.where(s>1e-12,s,1.)
    Z=X/s
    def obj(b):
        u=Z@b
        lse=logsumexp(u,axis=1)
        p=np.exp(u-lse[:,None])
        val=float(np.dot(w,lse-u[:,0])+5*np.dot(b,b))
        grad=np.einsum("i,ijk->k",w,np.einsum("ij,ijk->ijk",p,Z))-np.einsum("i,ij->j",w,Z[:,0,:])+10*b
        return val,grad
    r=minimize(obj,np.zeros(X.shape[-1]),jac=True,method="L-BFGS-B",options={"maxiter":500,"ftol":1e-12,"gtol":1e-7})
    if not r.success or not np.isfinite(r.x).all():raise RuntimeError("optimizer failed")
    return r.x/s

def compare(X,aid):
    if X is None:return {"status":"no_complete_sets"}
    n=len(X);groups=sorted(set(aid))
    o={"n":n,"animals":len(groups),"sets_per_animal":summary(pd.Series(aid).value_counts()),
       "status":"insufficient_animals","uniform_log_probability":float(-np.log(NCONTROL+1))}
    if len(groups)<6:return o
    use={"M0":8,"M1":9,"M2":10}
    scores={k:np.full(n,np.nan) for k in use};wins={k:np.full(n,np.nan) for k in use};coefs={k:[] for k in use}
    for animal in groups:
        te=aid==animal;tr=~te
        cnt=pd.Series(aid[tr]).value_counts();w=pd.Series(aid[tr]).map(1/cnt).to_numpy();w/=w.mean()
        for k,p in use.items():
            b=fit_choice(X[tr,:,:p],w);u=center(X[te,:,:p])@b
            scores[k][te]=u[:,0]-logsumexp(u,axis=1)
            # Fractional credit if tied; avoid deterministic chosen-column advantage.
            mx=u.max(axis=1);tied=np.isclose(u,mx[:,None],rtol=0,atol=1e-10)
            wins[k][te]=tied[:,0]/tied.sum(axis=1)
            coefs[k].append(b)
    assert all(np.isfinite(v).all() for v in scores.values())
    means={k:pd.DataFrame({"animal":aid,"v":v}).groupby("animal").v.mean() for k,v in scores.items()}
    wm={k:pd.DataFrame({"animal":aid,"v":v}).groupby("animal").v.mean() for k,v in wins.items()}
    o.update(status="computed",models={k:{"equal_animal_log_probability":float(v.mean()),"equal_animal_top1":float(wm[k].mean())} for k,v in means.items()},
       M1_abs_gradient_coefficient=summary([float(b[8]) for b in coefs["M1"]]),
       M2_abs_gradient_coefficient=summary([float(b[8]) for b in coefs["M2"]]),
       M2_signed_gradient_coefficient=summary([float(b[9]) for b in coefs["M2"]]))
    o["contrasts"]={}
    for a,b in [("M1","M0"),("M2","M1")]:
        delta=means[a]-means[b]
        o["contrasts"][a+"_minus_"+b]={"delta_log_probability":float(delta.mean()),"animals_improved":int((delta>0).sum()),"animal_delta":summary(delta)}
    actual=X[:,0,8];control=X[:,1:,8].mean(axis=1)
    o["descriptive"]={"actual_abs_gradient":summary(actual),"control_mean_abs_gradient":summary(control),
      "actual_minus_control_mean":summary(actual-control),"actual_smaller_fraction":float(np.mean(actual<control))}
    return o

def test():
    rng=np.random.default_rng(42);X=rng.normal(size=(500,25,2));X[:,0,0]-=1
    b=fit_choice(X,np.ones(len(X)))
    assert b[0]<0
    b2=fit_choice(X+np.array([3.,-4.]),np.ones(len(X)))
    assert np.allclose(b,b2,atol=1e-7)
    lat,lon=destinations(0,0,np.array([0.,np.pi/2]),1000.)
    assert np.isclose(lat[0],1000/EARTH*180/np.pi) and np.isclose(lon[1],1000/EARTH*180/np.pi)

def main():
    r={"status":"conditional_direction_pilot","claim_boundary":"Same-length directions are geometric controls, not verified accessible routes. No causal, energetic or route-formation claim.","panels":{}}
    dest=OUT/"audit_v28_slope.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save();test();r["synthetic_test"]="pass";save()
    for p in PANELS:
        q={}
        try:
            d,_=tadarida() if p=="tadarida" else load(p)
            d["alternate"]=np.nan;dem=Copernicus()
            X,aid,a=choices(d,dem)
            q["choice_audit"]=a
            q["DEM_receipts"]={"tiles_attempted":len(dem.tiles),"failures":dem.failures,"verified_objects":dem.receipts}
            q["result"]=compare(X,aid);q["status"]="computed"
        except Exception as e:q["status"]="blocked";q["error_type"]=type(e).__name__
        r["panels"][p]=q;save()
    print(dest.read_text())
    return 0 if all(v["status"]=="computed" for v in r["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
