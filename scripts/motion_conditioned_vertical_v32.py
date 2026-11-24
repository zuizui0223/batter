"""V32 retrospective conditional shape, not observed behavior or forecast of absolute height."""
import argparse,json,math,pathlib
from collections import defaultdict,Counter
import numpy as np
from scripts.run_tag_altitude_bias_shape import panel_raw,EDGES,CELL
OUT=pathlib.Path("results")
PANELS=["tadarida","eidolon","hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"]
def normalized(c): 
    a=np.asarray(c,dtype=float)+.5
    return a/a.sum()
def prepare(raw):
    groups=defaultdict(list)
    for r in raw:groups[r["cohort"],r["iid"],r["session"]].append(r)
    result={}
    for key,rr in groups.items():
        rr=sorted(rr,key=lambda r:r["t"]);h=np.array([r["h"] for r in rr]);med=float(np.median(h))
        dt=np.array([(b["t"]-a["t"]).total_seconds() for a,b in zip(rr,rr[1:])])
        p=dt[dt>0]
        if not len(p):continue
        maxgap=min(900.,2*float(np.median(p)));events=[]
        for i,(a,b) in enumerate(zip(rr,rr[1:])):
            if not 0<dt[i]<=maxgap:continue
            speed=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/dt[i]
            if not math.isfinite(speed) or speed>30:continue
            state=0 if speed<1 else (1 if speed<3 else 2)
            cell=(math.floor(b["x"]/CELL),math.floor(b["y"]/CELL))
            z=int(np.searchsorted(EDGES[1:-1],b["h"]-med,side="right"))
            events.append((cell,state,z))
        if events:result[key]=events
    return result
def counts(rows):
    out=defaultdict(lambda:np.zeros(len(EDGES)-1,dtype=int))
    for c,s,z in rows:out[(c,None)][z]+=1;out[(c,s)][z]+=1
    return out
def test():
    assert np.allclose(normalized([0,0]),[.5,.5])
    c=counts([((0,0),1,2)]*10)
    assert c[((0,0),1)].sum()==10 and c[((0,0),None)].sum()==10
def run(panel):
    test();raw,source=panel_raw(panel)
    sessions=prepare(raw);maps={k:counts(v) for k,v in sessions.items()}
    by=defaultdict(list);bys=defaultdict(list)
    for k in sessions:by[k[:2]].append(k);bys[k[0]].append(k)
    # Per cohort and cell-state, maintain sparse index of training counts by animal/session.
    index=defaultdict(lambda:defaultdict(dict))
    for (cohort,iid,sid),m in maps.items():
        for ck,a in m.items():index[(cohort,ck)][iid][sid]=a
    def eligible(cohort,iid,sid,cell,state):
        D=index[(cohort,(cell,state))]
        own=[v for k,v in D.get(iid,{}).items() if k!=sid]
        other=[j for j,M in D.items() if j!=iid and sum(int(v.sum()) for v in M.values())>=10]
        return sum(int(v.sum()) for v in own)>=10 and len(other)>=2,other
    def profile(cohort,iid,sid,cell,state,other):
        D=index[(cohort,(cell,state))]
        own=[normalized(v) for k,v in D.get(iid,{}).items() if k!=sid]
        oth=[np.mean([normalized(v) for v in D[j].values()],axis=0) for j in other if j in D]
        return np.mean(own,axis=0),np.mean(oth,axis=0)
    summaries=defaultdict(list);scored=0;eligible_target=0
    state_counts=Counter()
    for (cohort,iid,sid),events in sessions.items():
        if len(by[(cohort,iid)])<3:continue
        # Cache candidate profiles for each target cell/state; identical other IDs in both profiles.
        cache={};vals=[]
        for c,s,z in events:
            key=(c,s)
            if key not in cache:
                ok,other=eligible(cohort,iid,sid,c,s)
                if ok:
                    i0,o0=profile(cohort,iid,sid,c,None,other)
                    i1,o1=profile(cohort,iid,sid,c,s,other)
                    cache[key]=np.log(np.stack([o0,o1,i0,i1]))
                else:cache[key]=None
            if cache[key] is not None:
                vals.append(cache[key][:,z]);state_counts[s]+=1
        eligible_target+=len(vals)
        if len(vals)>=50:summaries[(cohort,iid)].append(np.mean(vals,axis=0));scored+=len(vals)
    kept=[np.mean(x,axis=0) for x in summaries.values() if len(x)>=2]
    report={"panel":panel,"source":source,"raw_fixes":len(raw),"motion_fixes":sum(map(len,sessions.values())),"sessions":len(sessions),
      "common_target_fixes_before_session_gate":eligible_target,"scored_fixes_before_bat_gate":scored,"eligible_bats":len(kept),"state_counts_before_gates":dict(state_counts)}
    if len(kept)<5:report["status"]="STOP_LOW_SUPPORT";return report
    a=np.stack(kept);g={"other_motion":a[:,1]-a[:,0],"own_motion":a[:,3]-a[:,2],"identity_unconditioned":a[:,2]-a[:,0],"identity_conditioned":a[:,3]-a[:,1],"identity_attenuation":(a[:,2]-a[:,0])-(a[:,3]-a[:,1])}
    report.update(status="SCORED",mean_log_scores=dict(zip(["O0","O1","I0","I1"],a.mean(0).tolist())),gains={k:{"mean_nats":float(v.mean()),"positive_bats":int((v>0).sum()),"q05_q50_q95":np.quantile(v,[.05,.5,.95]).tolist()} for k,v in g.items()})
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--panel",choices=PANELS,required=True);a=p.parse_args()
    try:r=run(a.panel)
    except Exception as e:r={"panel":a.panel,"status":"STOP","error":repr(e)}
    OUT.mkdir(exist_ok=True);(OUT/f"motion_conditioned_vertical_v32_{a.panel}.json").write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(json.dumps(r,indent=2,allow_nan=False))
