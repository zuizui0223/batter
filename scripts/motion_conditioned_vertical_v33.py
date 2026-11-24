"""V33 fixed partial pooling. Strict reproduction and separately defined wider support."""
import argparse,json
from collections import defaultdict,Counter
import numpy as np
from scripts.motion_conditioned_vertical_v32 import prepare,counts,normalized,panel_raw,PANELS,OUT
LAMBDA=20.
EXPECTED={
"tadarida":(1,None),"eidolon":(0,None),"phyllostomus_2016":(4,None),
"hypsignathus":(19,[-1.399040997374511,-1.4176308415494028,-1.2634217179888025,-1.2817580169472627]),
"phyllostomus_2022":(28,[-1.1846089345375799,-1.2552343746621275,-1.1294572212447467,-1.1930415494467599]),
"phyllostomus_2023":(8,[-1.356512701440829,-1.3834422568959877,-1.353586286443305,-1.360282877380472])}
def shrink(base,state):
    p=normalized(base)
    return (state+LAMBDA*p)/(state.sum()+LAMBDA)
def test():
    b=np.array([2,8]);z=np.zeros(2)
    assert np.allclose(shrink(b,z),normalized(b))
    assert np.isclose(shrink(b,b).sum(),1.)
def scheme(sessions,index,by,strict):
    summary=defaultdict(list);state_counts=Counter();n_own0=0;n_others0=0;before=0;retained=0
    K=len(next(iter(next(iter(index.values())).values())).values().__iter__().__next__())
    zero=np.zeros(K,dtype=int)
    for (cohort,iid,sid),events in sessions.items():
        if len(by[(cohort,iid)])<(3 if strict else 2):continue
        # Aggregate test events by cell/state/z, exact equivalent to fix-wise mean.
        obs=Counter(events);cache={};values=np.zeros(6);n=0;own0=0;other0=0;states=Counter()
        for (c,s,z),freq in obs.items():
            key=(c,s)
            if key not in cache:
                B=index.get((cohort,(c,None)),{})
                S=index.get((cohort,(c,s)),{})
                D=S if strict else B
                own_n=sum(int(a.sum()) for ss,a in D.get(iid,{}).items() if ss!=sid)
                others=[j for j,M in D.items() if j!=iid and sum(int(a.sum()) for a in M.values())>=10]
                if own_n<10 or len(others)<2:
                    cache[key]=None
                else:
                    def source(j,own):
                        bs=[(ss,a) for ss,a in B[j].items() if not own or ss!=sid]
                        ssmap=S.get(j,{})
                        ps=[normalized(a) for _,a in bs]
                        qs=[shrink(a,ssmap.get(ss,zero)) for ss,a in bs]
                        raw=[normalized(ssmap[ss]) for ss,_ in bs if ss in ssmap]
                        ns=sum(int(ssmap.get(ss,zero).sum()) for ss,_ in bs)
                        return np.mean(ps,axis=0),np.mean(qs,axis=0),np.mean(raw,axis=0) if raw else np.mean(ps,axis=0),ns
                    i0,i2,i1,ni=source(iid,True)
                    oo=[source(j,False) for j in others]
                    o0,o2,o1=[np.mean([a[t] for a in oo],axis=0) for t in range(3)]
                    cache[key]=(np.log(np.stack([o0,o1,i0,i1,o2,i2])),ni==0,all(a[3]==0 for a in oo))
            entry=cache[key]
            if entry is None:continue
            p,ownz,otherz=entry
            values+=freq*p[:,z];n+=freq;own0+=freq*ownz;other0+=freq*otherz;states[s]+=freq
        before+=n
        if n>=(50 if strict else 10):
            summary[(cohort,iid)].append((values/n,n,own0,other0,states))
            retained+=n
    kept=[v for v in summary.values() if len(v)>=2 and (strict or sum(r[1] for r in v)>=50)]
    report={"eligible_bats":len(kept),"target_fixes_before_session_gate":before,"target_fixes_before_bat_gate":retained,
       "scored_sessions":sum(len(v) for v in kept),"scored_fixes":sum(r[1] for v in kept for r in v)}
    if not kept:report["status"]="STOP_LOW_SUPPORT";return report
    n=report["scored_fixes"];report["own_state_absent_fraction"]=sum(r[2] for v in kept for r in v)/n
    report["all_other_state_absent_fraction"]=sum(r[3] for v in kept for r in v)/n
    for v in kept:
        for r in v:state_counts.update(r[4])
    report["state_counts"]=dict(state_counts)
    if len(kept)<5:report["status"]="STOP_LOW_SUPPORT";return report
    a=np.stack([np.mean([r[0] for r in v],axis=0) for v in kept])
    means=a.mean(0)
    report["status"]="SCORED";report["mean_log_scores"]={k:float(v) for k,v in zip(["O0","O1_raw","I0","I1_raw","O2_pooled","I2_pooled"],means) if strict or k not in ("O1_raw","I1_raw")}
    g={"other_motion":a[:,4]-a[:,0],"own_motion":a[:,5]-a[:,2],"identity_unconditioned":a[:,2]-a[:,0],"identity_conditioned":a[:,5]-a[:,4],"identity_attenuation":(a[:,2]-a[:,0])-(a[:,5]-a[:,4])}
    if strict:g.update(raw_other_motion=a[:,1]-a[:,0],raw_own_motion=a[:,3]-a[:,2],raw_identity_conditioned=a[:,3]-a[:,1])
    report["gains"]={k:{"mean_nats":float(x.mean()),"positive_bats":int((x>0).sum()),
      "q05_q50_q95":np.quantile(x,[.05,.5,.95]).tolist(),
      "leave_one_bat_mean_range":[float(y.min()),float(y.max())]} for k,x in g.items() for y in [(x.sum()-x)/(len(x)-1)]}
    return report
def run(panel):
    test();raw,src=panel_raw(panel);sessions=prepare(raw)
    index=defaultdict(lambda:defaultdict(dict));by=defaultdict(list)
    for (cohort,iid,sid),events in sessions.items():
        by[cohort,iid].append(sid)
        for ck,a in counts(events).items():index[cohort,ck][iid][sid]=a
    if not index:return {"panel":panel,"status":"STOP_EMPTY"}
    strict=scheme(sessions,index,by,True);n,expected=EXPECTED[panel]
    ok=strict["eligible_bats"]==n
    drift=None
    if expected is not None and strict["status"]=="SCORED":
        m=strict["mean_log_scores"]
        drift=float(np.max(np.abs(np.array([m[k] for k in ("O0","O1_raw","I0","I1_raw")])-expected)))
        ok=ok and drift<=1e-8
    elif expected is not None:ok=False
    report={"panel":panel,"source":src,"raw_fixes":len(raw),"motion_fixes":sum(map(len,sessions.values())),"sessions":len(sessions),"lambda":LAMBDA,
      "strict_reproduction":{"pass":bool(ok),"max_log_score_drift":drift},"strict":strict}
    if not ok:report["status"]="STOP_V32_REPRODUCTION";return report
    report["broader_support"]=scheme(sessions,index,by,False);report["status"]="COMPLETE"
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--panel",choices=PANELS,required=True);a=p.parse_args()
    try:r=run(a.panel)
    except Exception as e:r={"panel":a.panel,"status":"STOP","error":repr(e)}
    OUT.mkdir(exist_ok=True);(OUT/f"motion_conditioned_vertical_v33_{a.panel}.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(json.dumps(r,indent=2,allow_nan=False))
