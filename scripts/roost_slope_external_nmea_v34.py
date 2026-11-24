"""V34 independent source/species panels: frozen V29 prediction architecture.
Native NMEA height only; no interpolation, no calibrated AGL, no raw records exported.
"""
import io,json,math,zipfile
from collections import Counter,defaultdict
from pathlib import PurePosixPath
from bisect import bisect_left,bisect_right
from types import SimpleNamespace
import numpy as np
import pandas as pd
from scipy.special import logsumexp
from scipy.stats import t,norm
from roost_fd_source_audit_v2 import OUT
from roost_slope_native_nmea_v33 import (
 FILES,fetch,MAPSHA,sha,norm as norm_label,load_mapping,sentence,rmc,clock,coords,
 finite,dist,decode,anchors_and_windows,test as test_v33)
from roost_slope_joint_endpoint_v29 import (
 DF,t_scale,animal_means,contrast,fit,summary,fit_choice,center,SEED,NCONTROL,
 displacement,destinations,candidate_features,Copernicus,test as test_v29)

EXPECTED={"myotis myotis":(8,67880,1486),"rhinopoma microphyllum":(6,7975,758)}

def decode_height(b):
    seq=[];c=Counter();sat=[];hdop=[]
    for l in b.decode("utf-8-sig",errors="replace").splitlines():
        t=sentence(l.strip())
        if t is None:continue
        k,f=t;seq.append((k,f));c[k]+=1
        if f is None:c[k+"_bad_checksum_or_format"]+=1
    # use adjacent acquisition sentence indices, not same clock from another day
    R={i:rmc(f) for i,(k,f) in enumerate(seq) if k=="RMC"}
    c["RMC_valid_status_date_time_xy"]=sum(v is not None for v in R.values())
    rows=[]
    for i,(k,f) in enumerate(seq):
        if k!="GGA":continue
        row=None;reason=None
        if f is None or len(f)<13:reason="checksum_or_format"
        else:
            try:
                t=clock(f[1])
                if f[6] not in ("1","2"):reason="fix_quality_not_1_2"
                else:
                    lat,lon=coords(f[2],f[3],f[4],f[5])
                    if not finite(f[9]) or f[10]!="M":reason="height_missing_or_unit"
                    else:
                        c["GGA_valid_xyz_time_quality"]+=1
                        if finite(f[11]) and f[12]=="M":c["geoid_present_m"]+=1
                        matches=set()
                        for j in range(max(0,i-8),min(len(seq),i+9)):
                            v=R.get(j)
                            if v is not None and v[0]==t and dist(lat,lon,v[2],v[3])<=20:
                                matches.add(v[1])
                        if len(matches)!=1:reason="no_unique_same_time_RMC_date"
                        else:
                            row=(next(iter(matches))+t,lat,lon,float(f[9]))
                            if finite(f[7]):sat.append(float(f[7]))
                            if finite(f[8]):hdop.append(float(f[8]))
            except (ValueError,OverflowError,IndexError):reason="invalid_time_or_xy"
        if row is None:c["GGA_rejected_"+str(reason)]+=1
        else:c["GGA_RMC_valid_pair"]+=1
        rows.append(row)
    counts=Counter(r[0] for r in rows if r is not None)
    out=[];chain=[];gaps=[]
    for row in rows:
        if row is None or counts[row[0]]!=1:
            if row is not None:c["duplicate_utc_rows"]+=1
            if chain:out.append(chain);chain=[]
            continue
        if chain:
            dt=(row[0]-chain[-1][0])/1e6
            if dt>0:gaps.append(dt)
            if dt<=0 or dt>65:
                c["chain_break_gap_or_nonincrease"]+=1
                out.append(chain);chain=[]
        chain.append(row)
    if chain:out.append(chain)
    c["unique_timestamp_valid_rows"]=sum(map(len,out))
    return out,c,gaps,sat,hdop

def run(panel,X,aid,y,V):
    assert len(set(aid))>=6
    groups=sorted(set(aid));n=len(aid)
    H={k:np.full(n,np.nan) for k in ["H0","H1"]}
    T={k:np.full(n,np.nan) for k in ["V0","V1"]}
    G={k:np.full(n,np.nan) for k in T}
    P={k:np.full(n,np.nan) for k in T}
    scale={k:[] for k in T};coef=[];hcoef=[]
    for animal in groups:
        te=aid==animal;tr=~te
        cnt=pd.Series(aid[tr]).value_counts();w=pd.Series(aid[tr]).map(1/cnt).to_numpy();w/=w.mean()
        for k,p in [("H0",8),("H1",9)]:
            b=fit_choice(X[tr,:,:p],w);u=center(X[te,:,:p])@b
            H[k][te]=u[:,0]-logsumexp(u,axis=1)
            if k=="H1":hcoef.append(float(b[8]))
        for k,p in [("V0",12),("V1",13)]:
            mu,sd,cy,b=fit(V[tr,:p],y[tr],w)
            train=cy+((V[tr,:p]-mu)/sd)@b
            pred=cy+((V[te,:p]-mu)/sd)@b
            res=y[tr]-train;s=t_scale(res,w)
            g=max(float(np.sqrt(np.average(res*res,weights=w))),np.exp(-12))
            P[k][te]=pred
            T[k][te]=t.logpdf((y[te]-pred)/s,df=DF)-np.log(s)
            G[k][te]=norm.logpdf(y[te],loc=pred,scale=g)
            scale[k].append(s)
            if k=="V1":coef.append(float(b[-1]/sd[-1]))
    for a in [H,T,G,P]:assert all(np.isfinite(v).all() for v in a.values())
    hm={k:animal_means(aid,v) for k,v in H.items()}
    tm={k:animal_means(aid,v) for k,v in T.items()}
    gm={k:animal_means(aid,v) for k,v in G.items()}
    out={"n":n,"animals":len(groups),"architecture_replayed":True,"H1_abs_gradient_coefficient":summary(hcoef),
        "direction":{"H0":float(hm["H0"].mean()),"H1":float(hm["H1"].mean()),"increment":contrast(hm["H1"],hm["H0"])},
        "vertical_rate":summary(y),"fraction_abs_rate_gt15":float(np.mean(np.abs(y)>15)),
        "q_coefficient_V1":summary(coef),"vertical":{}}
    for k in T:
        mse=animal_means(aid,(y-P[k])**2)
        out["vertical"][k]={"equal_animal_RMSE":float(np.sqrt(mse.mean())),
            "equal_animal_t_log_density":float(tm[k].mean()),"equal_animal_gaussian_log_density":float(gm[k].mean()),
            "training_t_scale_across_folds":summary(scale[k])}
    def joint(vm):
        m={h+v:hm[h]+vm[v] for h in hm for v in vm}
        dh=hm["H1"]-hm["H0"];dv=vm["V1"]-vm["V0"]
        assert np.allclose((m["H1V1"]-m["H0V0"]).to_numpy(),(dh+dv).to_numpy(),rtol=0,atol=1e-12)
        return {"joint_log_scores":{k:float(v.mean()) for k,v in m.items()},
            "direction_only":contrast(m["H1V0"],m["H0V0"]),
            "vertical_only":contrast(m["H0V1"],m["H0V0"]),
            "both":contrast(m["H1V1"],m["H0V0"]),
            "both_minus_direction_only":contrast(m["H1V1"],m["H1V0"]),
            "both_minus_vertical_only":contrast(m["H1V1"],m["H0V1"])}
    out["student_t_joint"]=joint(tm);out["gaussian_joint_sensitivity"]=joint(gm)
    return out

def source():
    b=fetch(FILES["data_zip"])
    matched=defaultdict(list)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        infos=[i for i in z.infolist() if not i.is_dir() and "__MACOSX" not in PurePosixPath(i.filename).parts and not PurePosixPath(i.filename).name.startswith("._") and PurePosixPath(i.filename).name.lower()!=".ds_store"]
        mappings=[z.read(i) for i in infos if PurePosixPath(i.filename).suffix.lower()==".xlsx"]
        m=load_mapping(next(x for x in mappings if sha(x)==MAPSHA))
        for i in infos:
            if PurePosixPath(i.filename).suffix.lower()!=".txt":continue
            raw=z.read(i)
            if raw.startswith(b"\x00\x05\x16\x07"):continue
            pp=[norm_label(p) for p in PurePosixPath(i.filename).parts[:-1]]
            ks=[k for k in m if any(pp[j]==k[0] and pp[j+1]==k[1] for j in range(len(pp)-1))]
            assert len(ks)==1
            matched[ks[0]].append(raw)
        assert len(matched)==22 and all(len(x)==1 for x in matched.values())
    return m,matched

def windows(chains):
    # Identical V33 anchor construction and horizontal gate, retain all three fixes.
    for chain in chains:
        times=[r[0] for r in chain];n=len(chain);i=0
        while i<n:
            ids=[i];current=i
            while True:
                target=times[current]+60_000_000
                a=bisect_left(times,target-5_000_000,current+1)
                b=bisect_right(times,target+5_000_000,a)
                if a==b:break
                current=min(range(a,b),key=lambda k:(abs(times[k]-target),times[k]))
                ids.append(current)
            i=current+1
            for j in range(0,len(ids)-2,2):
                r0,r1,r2=[chain[k] for k in ids[j:j+3]]
                dt1=(r1[0]-r0[0])/1e6;dt2=(r2[0]-r1[0])/1e6
                assert 55<=dt1<=65 and 55<=dt2<=65
                v1=dist(r0[1],r0[2],r1[1],r1[2])/dt1
                v2=dist(r1[1],r1[2],r2[1],r2[2])/dt2
                if 2<=v1<=50 and 2<=v2<=50:yield r0,r1,r2

def replay(panel,m,matched):
    # Complete source-admission reconciliation before fitting any altitude outcome.
    tracks=[];counts=Counter();audit=Counter();eligible_counts=[]
    for j,(key,v) in enumerate(m.items()):
        if key[0]!=panel or v["gps"]!="1":continue
        assert len(matched.get(key,[]))==1
        raw=matched[key][0]
        orig,oc,*_=decode(raw)
        native,nc,*_=decode_height(raw)
        assert oc==nc and len(orig)==len(native)
        assert all(len(o)==len(n) and all(tuple(x)==tuple(y[:3]) for x,y in zip(o,n)) for o,n in zip(orig,native))
        ww=list(windows(native));wa=anchors_and_windows(orig)
        assert len(ww)==wa["horizontal_eligible_windows"]
        eligible_counts.append(len(ww));counts.update(oc);audit.update(wa)
        tracks.append((str(j),ww))
    en,ef,ew=EXPECTED[panel]
    assert len(tracks)==en and counts["unique_timestamp_valid_rows"]==ef and sum(eligible_counts)==ew
    assert all(v>=50 for v in eligible_counts)
    return tracks,{"raw_structure_reproduced":True,"individuals":len(tracks),"native_counts":dict(counts),
        "window_counts":dict(audit),"horizontal_windows_per_individual":summary(eligible_counts)}

def choices(panel,tracks):
    dem=Copernicus();rng=np.random.default_rng(SEED)
    feats=[];animals=[];resp=[];vert=[];audit=Counter()
    for animal,ww in tracks:
        for a0,a1,a2 in ww:
            r0,r1,r2=[SimpleNamespace(lat=r[1],lon=r[2],height=r[3]) for r in (a0,a1,a2)]
            d0,t0=displacement(r0,r1);d1,t1=displacement(r1,r2)
            dt0=(a1[0]-a0[0])/1e6;dt1=(a2[0]-a1[0])/1e6
            assert 55<=dt0<=65 and 55<=dt1<=65 and d1>0
            audit["horizontal_gate"]+=1
            h=np.r_[t1,rng.uniform(-np.pi,np.pi,NCONTROL)]
            lat,lon=destinations(r1.lat,r1.lon,h,d1)
            lat[0]=r2.lat;lon[0]=r2.lon
            start=dem.value(float(r1.lat),float(r1.lon))
            if start is None:
                audit["incomplete_DEM_sets"]+=1;continue
            z=[dem.value(float(la),float(lo)) for la,lo in zip(lat,lon)]
            if any(v is None or not np.isfinite(v) for v in z):
                audit["incomplete_DEM_sets"]+=1;continue
            gradient=(np.asarray(z,float)-start)/d1
            X=candidate_features(h,t0,gradient)
            y=(r2.height-r1.height)/dt1
            v=np.r_[np.log(dt1),d1/dt1,d0/dt0,start,X[0,:8],gradient[0]*d1/dt1]
            assert np.isfinite(X).all() and np.isfinite(v).all() and np.isfinite(y)
            feats.append(X);animals.append(animal);resp.append(y);vert.append(v)
    assert audit["horizontal_gate"]==EXPECTED[panel][2]
    audit["complete_sets_before_animal_gate"]=len(feats)
    aid=np.asarray(animals);cnt=pd.Series(aid,dtype=str).value_counts();keep=np.isin(aid,cnt[cnt>=50].index)
    audit["animals_before_gate"]=len(cnt);audit["animals_after_gate"]=len(set(aid[keep]))
    audit["sets_after_gate"]=int(keep.sum())
    receipt={"tiles_attempted":len(dem.tiles),"failures":dem.failures,"verified_objects":dem.receipts}
    if audit["animals_after_gate"]<6:return None,dict(audit),receipt
    return (np.asarray(feats)[keep],aid[keep],np.asarray(resp)[keep],np.asarray(vert)[keep]),dict(audit),receipt

def main():
    r={"status":"independent_panel_prediction_replication",
       "claim_boundary":"Source new relative to V19–29; model refit within each species. Conditional known chord/time, native GGA vertical rates, geometric direction controls; not AGL, sensory causation, free-air volume or SDM.",
       "panels":{}}
    dest=OUT/"audit_v34_external_nmea.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save()
    test_v33();test_v29();r["prior_synthetic_tests"]="pass"
    try:m,matched=source()
    except Exception as e:r["status"]="source_blocked";r["error_type"]=type(e).__name__;save();print(dest.read_text());return 2
    for panel in EXPECTED:
        q={}
        try:
            tracks,q["source_replay"]=replay(panel,m,matched)
            values,q["choice_audit"],q["DEM_receipts"]=choices(panel,tracks)
            if values is None:q["status"]="insufficient_animals_after_DEM_gate"
            else:
                q["result"]=run(panel,*values);q["status"]="computed"
        except Exception as e:q["status"]="blocked";q["error_type"]=type(e).__name__
        r["panels"][panel]=q;save()
    print(dest.read_text())
    return 0 if all(q["status"] in ("computed","insufficient_animals_after_DEM_gate") for q in r["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
