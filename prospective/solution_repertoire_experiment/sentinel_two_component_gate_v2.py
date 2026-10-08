#!/usr/bin/env python3
"""Synthetic v2: two independent sentinel partial-transfer arms (not bat observations)."""
from __future__ import annotations
import argparse
from itertools import permutations, product
import json
from pathlib import Path
import numpy as np

ROOT_SEED=202610082015
SAMPLE_SIZES=(18,24)
REPEATS=1000
PRE_POST=2
NOISE_SD=.10
PERMS=np.asarray(list(permutations((0,1,2))),dtype=np.int8)
SCENARIOS={
 "WHOLE_ROUTE_ONLY":(0.,0.,0.),
 "GLOBAL_FAMILIARITY":(.12,.12,.12),
 "BOTH_MOTOR_COMPONENTS":(0.,.12,.12),
 "BOTH_SENSORY_CUE_GENERALIZATION":(0.,.12,.12),
 "HORIZONTAL_ONLY":(0.,0.,.24),
 "VERTICAL_ONLY":(0.,.24,0.),
 "WEAK_BOTH":(0.,.06,.06)
}

def simulate(rng,n,gains):
    b=n//3
    labels=np.concatenate([rng.permutation(3) for _ in range(b)]).astype(np.int8)
    base=1+rng.normal(0,.20,n)
    blocks=np.repeat(rng.normal(0,.05,b),3)
    individual=rng.normal(0,.05,n)
    pre=base[:,None]+rng.normal(0,NOISE_SD,(n,PRE_POST))
    post=(base-blocks-individual-np.asarray(gains)[labels])[:,None]+rng.normal(0,NOISE_SD,(n,PRE_POST))
    y=pre.mean(axis=1)-post.mean(axis=1)
    return labels,pre,post,y

def exact_primary(y,labels):
    b=len(labels)//3
    blk_y=y.reshape(b,3)
    lk=labels.reshape(b,3)
    nindex=(lk==0).argmax(axis=1)
    # Each H/V swap identical for the symmetric primary statistic.
    vals=.5*blk_y.sum(axis=1,keepdims=True)-1.5*blk_y
    observed=float(np.mean(vals[np.arange(b),nindex]))
    null=np.zeros(1)
    for x in vals:
        null=(null[:,None]+x[None,:]).reshape(-1)
    null /= b
    assert len(null)==3**b and np.isclose(np.mean(null),0,atol=1e-12)
    return observed,float(np.mean(null>=observed-1e-12)),len(null)*2**b

def exact_pair(y,labels,one):
    # one==2 -> H vs N, holding V-assigned identities fixed.
    # one==1 -> V vs N, holding H-assigned identities fixed.
    b=len(labels)//3
    v=y.reshape(b,3)
    lab=labels.reshape(b,3)
    idx_other=(lab==one).argmax(axis=1)
    idx_none=(lab==0).argmax(axis=1)
    diff=v[np.arange(b),idx_other]-v[np.arange(b),idx_none]
    observed=float(np.mean(diff))
    signs=np.asarray(list(product((-1.,1.),repeat=b)),float)
    null=signs@diff/b
    assert len(null)==2**b and np.isclose(np.mean(null),0,atol=1e-12)
    return observed,float(np.mean(null>=observed-1e-12)),len(null)

def analyze(y,labels):
    t,p0,n_alloc=exact_primary(y,labels)
    dh,ph,n_pair=exact_pair(y,labels,2)
    dv,pv,_=exact_pair(y,labels,1)
    arm_means=np.asarray([y[labels==i].mean() for i in range(3)])
    assert np.isclose(t,.5*(dh+dv),rtol=0,atol=1e-12)
    return {
      "T":t,"p_T":p0,"D_H":dh,"p_H":ph,"D_V":dv,"p_V":pv,
      "primary_supported":bool(t>0 and p0<=.05),
      "both_component_gate":bool(t>0 and p0<=.05 and dh>0 and ph<=.05 and dv>0 and pv<=.05),
      "both_sample_means_positive":bool(dh>0 and dv>0),
      "arm_means_N_V_H":arm_means.tolist(),
      "legal_assignments":n_alloc,"legal_pair_conditional_assignments":n_pair
    }

def selftest():
    assert PERMS.shape==(6,3)
    for blocks in (6,8):
        assert 6**blocks==(3**blocks)*(2**blocks)
        assert (6**blocks,2**blocks)==({6:(46656,64),8:(1679616,256)}[blocks])
    y=np.array([i*.045+np.sin(i*.345) for i in range(18)],float)
    lab=np.tile([0,1,2],6)
    t,p,_=exact_primary(y,lab)
    dh,ph,_=exact_pair(y,lab,2)
    dv,pv,_=exact_pair(y,lab,1)
    assert abs(t-(dh+dv)/2)<1e-12
    # Direct 2-block full 36 factorial assignments equal compressed primary orbit.
    yy=y[:6]; obs=[]
    for p1,p2 in product(PERMS,repeat=2):
        perm=np.concatenate([p1,p2]); vals=[]
        for j in range(2):
            v=yy[3*j:3*j+3]; l=perm[3*j:3*j+3]
            vals.append(.5*(v[l==1][0]+v[l==2][0])-v[l==0][0])
        obs.append(np.mean(vals))
    uu=np.array([.5*y[:3].sum()-1.5*y[:3],.5*y[3:6].sum()-1.5*y[3:6]])
    reduced=(uu[0,:,None]+uu[1,None,:]).ravel()/2
    assert np.allclose(np.sort(obs),np.sort(np.repeat(reduced,4)),atol=1e-12)
    # Direct two-block H/N swap while V labels held fixed: exactly 4 possibilities.
    d=np.asarray([y[2]-y[0],y[5]-y[3]])
    vals=np.array([(s0*d[0]+s1*d[1])/2 for s0,s1 in product([-1,1],repeat=2)])
    assert np.isclose(np.mean(vals),0,atol=1e-12)
    a,pr,po,z=simulate(np.random.default_rng(271828),18,SCENARIOS['BOTH_MOTOR_COMPONENTS'])
    aa,pp,qq,zz=simulate(np.random.default_rng(271828),18,SCENARIOS['BOTH_SENSORY_CUE_GENERALIZATION'])
    assert np.array_equal(a,aa) and np.array_equal(pr,pp) and np.array_equal(po,qq) and np.array_equal(z,zz)
    return {"exact_primary_36_equals_9_orbits_with_4_repetitions":"PASS", "conditional_two_block_4_signs":"PASS", "all_18_or_24_complete_blocks":"PASS", "motor_and_sensory_twin_raw_arrays":"PASS", "p_pair_min_N18":1/64, "p_pair_min_N24":1/256}

def summary(rows):
    n=len(rows)
    def rate(k):
        x=np.asarray([v[k] for v in rows],bool)
        p=float(np.mean(x))
        return {"count":int(x.sum()),"rate":p,"mc_se":float(np.sqrt(p*(1-p)/n))}
    def stats(k):return float(np.mean([v[k] for v in rows]))
    return {
      "n_synthetic_experiments":n,
      "mean_T":stats("T"),"mean_D_H":stats("D_H"),"mean_D_V":stats("D_V"),
      "primary_T_supported":rate("primary_supported"),
      "H_one_sided_p_le_0_05":rate("H_sig"),
      "V_one_sided_p_le_0_05":rate("V_sig"),
      "both_H_and_V_joint_gate":rate("both_component_gate"),
      "both_arm_contrasts_positive_without_inference":rate("both_sample_means_positive"),
      "p_H_median":float(np.median([v["p_H"] for v in rows])),
      "p_V_median":float(np.median([v["p_V"] for v in rows]))
    }

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument('--self-test',action='store_true')
    pa.add_argument('--out',default='SENTINEL_TWO_COMPONENT_GATE_RESULT_V2.json')
    args=pa.parse_args()
    checks=selftest()
    if args.self_test:
        print(json.dumps(checks,indent=2));return
    out={"status":"SYNTHETIC_PLANNING_ONLY_NO_BAT_DATA","contract":"SENTINEL_TWO_COMPONENT_GATE_CONTRACT_V2.md","root_seed":ROOT_SEED,"simulation_count_each":REPEATS,"n_bats":[18,24],"preflight":checks,"scenarios":{},"boundary":"The intersection-union pair-specific sharp-null exact tests do not identify motor versus sonar/visual generalization; only a newly randomized cue/physics experiment could do that."}
    root=np.random.SeedSequence(ROOT_SEED)
    groups=("WHOLE_ROUTE_ONLY","GLOBAL_FAMILIARITY","BOTH_MOTOR_COMPONENTS","HORIZONTAL_ONLY","VERTICAL_ONLY","WEAK_BOTH")
    coupled=0
    for n,nstream in zip(SAMPLE_SIZES,root.spawn(len(SAMPLE_SIZES))):
        st={}
        for name,sstream in zip(groups,nstream.spawn(len(groups))):
            vals=[]
            for repseed in sstream.spawn(REPEATS):
                rng=np.random.default_rng(repseed)
                labels,pre,post,y=simulate(rng,n,SCENARIOS[name]); v=analyze(y,labels)
                v['H_sig']=bool(v['D_H']>0 and v['p_H']<=.05)
                v['V_sig']=bool(v['D_V']>0 and v['p_V']<=.05)
                vals.append(v)
                if name=='BOTH_MOTOR_COMPONENTS':
                    rng2=np.random.default_rng(repseed)
                    labs2,pre2,post2,y2=simulate(rng2,n,SCENARIOS['BOTH_SENSORY_CUE_GENERALIZATION'])
                    if not all(np.array_equal(a,b) for a,b in ((labels,labs2),(pre,pre2),(post,post2),(y,y2))):
                        raise AssertionError('rival causal models have distinguishable observed arrays')
                    coupled+=1
            st[name]=summary(vals)
            if name=='BOTH_MOTOR_COMPONENTS':
                st['BOTH_SENSORY_CUE_GENERALIZATION']=summary(vals)
            print('N',n,name,'T',st[name]['primary_T_supported']['count'],'BOTH',st[name]['both_H_and_V_joint_gate']['count'],flush=True)
        out['scenarios'][str(n)]={k:st[k] for k in SCENARIOS}
    out['n_exact_raw_motor_sensory_pairs']=coupled
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('V2_PROSPECTIVE_SYNTHETIC_CALIBRATION_COMPLETE',flush=True)
if __name__=='__main__':main()
