"""V34: exact V33 support; matched smoothing controls. No permutation p-values."""
import argparse,json
from collections import defaultdict,Counter
import numpy as np
from scripts.motion_conditioned_vertical_v32 import prepare,counts,normalized,panel_raw,PANELS,OUT,EDGES
L=20.; K=len(EDGES)-1; NROT=7; N=3+NROT
# O0,I0,O2,I2 in that order; all values taken from completed V33.
EXPECTED={
"tadarida":{"strict":(1,None),"broader":(5,[-2.3157598437087343,-2.4635965921022764,-2.3695408794437673,-2.64195221238932])},
"eidolon":{"strict":(0,None),"broader":(10,[-1.8671854343525083,-1.4361975196741243,-1.8467145962757368,-1.3892256710219746])},
"hypsignathus":{"strict":(19,[-1.3990409973745106,-1.2634217179888025,-1.371645646093697,-1.2391646331408268]),"broader":(23,[-1.3832321073469265,-1.2407789866831356,-1.354634611864613,-1.213431819635819])},
"phyllostomus_2022":{"strict":(28,[-1.1846089345375799,-1.1294572212447467,-1.134953107419108,-1.0815710379995924]),"broader":(33,[-1.2272266539169236,-1.1557929129300615,-1.1808798785863779,-1.1098961101610705])},
"phyllostomus_2023":{"strict":(8,[-1.356512701440828,-1.3535862864433044,-1.3249500802735503,-1.3250164534256794]),"broader":(15,[-1.4045024106322126,-1.4092807753328862,-1.3739190881311705,-1.3844341090039782])},
"phyllostomus_2016":{"strict":(4,None),"broader":(10,[-.993037707636167,-.9689940140630716,-1.0012704054218038,-1.0750273853532017])}}
def state_arrays(events):
    # Within this training session and cell, ordered sequence of states and heights.
    s,z=np.asarray(events,dtype=np.int64).T
    base=np.bincount(z,minlength=K)
    c=np.bincount(s*K+z,minlength=3*K).reshape(3,K)
    n=c.sum(axis=1);p0=normalized(base)
    assert np.array_equal(c.sum(axis=0),base)
    expected=n[:,None]*base[None,:]/base.sum()
    rows=[np.broadcast_to(p0,(3,K)),(c+L*p0)/(n[:,None]+L),(expected+L*p0)/(n[:,None]+L)]
    for k in range(1,NROT+1):
        v=np.bincount(np.roll(s,(k*len(s))//8)*K+z,minlength=3*K).reshape(3,K)
        assert np.array_equal(v.sum(axis=0),base) and np.array_equal(v.sum(axis=1),n)
        rows.append((v+L*p0)/(n[:,None]+L))
    a=np.stack(rows,axis=1)
    assert a.shape==(3,N,K) and np.allclose(a.sum(axis=-1),1.)
    return base,n,a
def test():
    b,n,a=state_arrays([(0,0),(0,0),(1,1),(1,1)]*4)
    assert np.allclose(a[2],normalized(b))
    assert a[0,1,0]>a[0,2,0]
    b,n,a=state_arrays([(0,0),(0,1),(1,0),(1,1)]*4)
    assert np.allclose(a[:,1],a[:,2])
def summary(x):
    return {"mean_nats":float(x.mean()),"positive_bats":int((x>0).sum()),
      "q05_q50_q95":np.quantile(x,[.05,.5,.95]).tolist(),
      "leave_one_bat_range":[float(y.min()),float(y.max())] if len(x)>1 else None} if (y:=(x.sum()-x)/(len(x)-1) if len(x)>1 else x).size else {}
def scheme(sessions,index,by,strict):
    per=defaultdict(list);eligible_fixes=0;before_bat=0
    for (cohort,iid,sid),events in sessions.items():
        if len(by[(cohort,iid)])<(3 if strict else 2):continue
        obs=Counter(events);cache={};values=np.zeros((2,N));num=0
        for (cell,s,z),freq in obs.items():
            key=(cell,s)
            if key not in cache:
                D=index.get((cohort,cell),{})
                def total(M,own):
                    return sum(int(n[s] if strict else b.sum()) for ss,(b,n,p) in M.items() if not own or ss!=sid)
                if total(D.get(iid,{}),True)<10:
                    cache[key]=None
                else:
                    oth=[j for j,M in D.items() if j!=iid and total(M,False)>=10]
                    if len(oth)<2:cache[key]=None
                    else:
                        def profile(j,own):
                            return np.mean([p[s] for ss,(b,n,p) in D[j].items() if not own or ss!=sid],axis=0)
                        i=profile(iid,True);o=np.mean([profile(j,False) for j in oth],axis=0)
                        cache[key]=np.log(np.stack([o,i]))
            p=cache[key]
            if p is not None:values+=freq*p[:,:,z];num+=freq
        eligible_fixes+=num
        if num>=(50 if strict else 10):
            per[cohort,iid].append((values/num,num));before_bat+=num
    kept=[v for v in per.values() if len(v)>=2 and (strict or sum(r[1] for r in v)>=50)]
    out={"eligible_bats":len(kept),"target_fixes_before_session_gate":eligible_fixes,"target_fixes_before_bat_gate":before_bat,
      "scored_sessions":sum(len(v) for v in kept),"scored_fixes":sum(r[1] for v in kept for r in v)}
    if len(kept)<5:out["status"]="STOP_LOW_SUPPORT";return out
    a=np.stack([np.mean([r[0] for r in v],axis=0) for v in kept])
    means=a.mean(axis=0)
    out["status"]="SCORED"
    out["mean_log_scores"]={name:dict(zip(["baseline","true","matched_expected"]+[f"rotation{k}" for k in range(1,8)],means[i].tolist())) for i,name in enumerate(("other","own"))}
    out["reproduction_vector"]=[float(means[0,0]),float(means[1,0]),float(means[0,1]),float(means[1,1])]
    gains={}
    for i,n in enumerate(("other","own")):
        x=a[:,i,:];r=x[:,3:]
        gains[n]={"true_minus_baseline":summary(x[:,1]-x[:,0]),"true_minus_expected":summary(x[:,1]-x[:,2]),
          "expected_minus_baseline":summary(x[:,2]-x[:,0]),"true_minus_rotation_mean":summary(x[:,1]-r.mean(axis=1)),
          "true_minus_each_rotation_mean":(means[i,1]-means[i,3:]).tolist(),
          "true_beats_all_rotations":bool(np.all(means[i,1]>means[i,3:]))}
    out["gains"]=gains
    out["identity"]={"baseline":summary(a[:,1,0]-a[:,0,0]),"true":summary(a[:,1,1]-a[:,0,1]),
      "expected":summary(a[:,1,2]-a[:,0,2])}
    out["matched_gate"]=all(gains[n]["true_minus_expected"]["mean_nats"]>0 and gains[n]["true_minus_expected"]["leave_one_bat_range"][0]>0 for n in ("own","other"))
    out["rotation_mean_gate"]=all(gains[n]["true_minus_rotation_mean"]["mean_nats"]>0 for n in ("own","other"))
    out["all_rotations_gate"]=all(gains[n]["true_beats_all_rotations"] for n in ("own","other"))
    return out
def run(panel):
    test();raw,src=panel_raw(panel);sessions=prepare(raw)
    index=defaultdict(lambda:defaultdict(dict));by=defaultdict(list)
    for (cohort,iid,sid),events in sessions.items():
        by[cohort,iid].append(sid);cells=defaultdict(list)
        for c,s,z in events:cells[c].append((s,z))
        for c,v in cells.items():index[cohort,c][iid][sid]=state_arrays(v)
    out={"panel":panel,"source":src,"lambda":L,"raw_fixes":len(raw),"motion_fixes":sum(map(len,sessions.values())),"results":{}}
    for name,strict in (("strict",True),("broader",False)):
        r=scheme(sessions,index,by,strict);n,e=EXPECTED[panel][name]
        ok=r["eligible_bats"]==n;drift=None
        if e is not None and r["status"]=="SCORED":
            drift=float(np.max(np.abs(np.array(r["reproduction_vector"])-e)));ok=ok and drift<=1e-8
        elif e is not None:ok=False
        r["v33_reproduction"]={"pass":bool(ok),"max_log_score_drift":drift}
        out["results"][name]=r
        if not ok:out["status"]="STOP_V33_REPRODUCTION";return out
    out["status"]="COMPLETE";return out
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--panel",choices=PANELS,required=True);a=p.parse_args()
    try:r=run(a.panel)
    except Exception as e:r={"panel":a.panel,"status":"STOP","error":repr(e)}
    OUT.mkdir(exist_ok=True);(OUT/f"motion_signal_matched_v34_{a.panel}.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(json.dumps(r,indent=2,allow_nan=False))
