#!/usr/bin/env python3
"""Orthogonal randomized route seed vs forced practice; synthetic planning only.

Contract: ORTHOGONAL_ROUTE_PRACTICE_CONTRACT_V1.md. No actual bat outcomes.
"""
from __future__ import annotations
import argparse, itertools, json, math
from pathlib import Path
import numpy as np

N=20
BLOCK=4
B=N//BLOCK
K=4
Q=8
MC=1000
ROOT=202610081616
HS=1.2
ETA=1.8
GAMMA=0.3
COST_SENS=ETA/GAMMA
P24=np.asarray(list(itertools.permutations(range(4))), dtype=np.int8)
SCENARIOS={
  "BASELINE_NO_PRACTICE":(False,False),
  "SKILL_CAUSES_CHOICE":(True,True),
  "FAMILIARITY_CAUSES_CHOICE":(True,True),
  "PRACTICE_SKILL_ONLY":(False,True),
  "PRACTICE_FAMILIARITY_ONLY":(True,False),
}

def eligible_derangements(seed):
    out=P24[np.all(P24 != np.asarray(seed,dtype=np.int8)[None,:],axis=1)]
    if out.shape!=(9,4): raise AssertionError(f"Expected 9 derangements, {out.shape}")
    return out

def assignments(rng):
    seed=np.concatenate([rng.permutation(K) for _ in range(B)]).astype(np.int8)
    practice=np.empty(N,np.int8)
    for j in range(B):
        options=eligible_derangements(seed[j*4:j*4+4])
        practice[j*4:j*4+4]=options[int(rng.integers(len(options)))]
    if not all(set(seed[j*4:j*4+4])=={0,1,2,3} and set(practice[j*4:j*4+4])=={0,1,2,3} for j in range(B)):
        raise AssertionError("route-balance drift")
    if np.any(seed==practice):raise AssertionError("practice must differ from seed")
    return seed,practice

def count_routes(routes):
    if routes.shape!=(N,Q):raise ValueError("wrong target shape")
    return np.stack([(routes==r).sum(axis=1) for r in range(K)],axis=1)

def practice_null(counts,seed,practice):
    if counts.shape!=(N,K) or seed.shape!=(N,) or practice.shape!=(N,):
        raise ValueError("incompatible support")
    obs=int(counts[np.arange(N),practice].sum())
    hist=np.array([1],dtype=np.int64)
    for b in range(B):
        c=counts[4*b:4*b+4]
        opts=eligible_derangements(seed[4*b:4*b+4])
        scores=c[np.arange(4)[None,:],opts].sum(axis=1)
        local=np.bincount(scores,minlength=4*Q+1).astype(np.int64)
        assert int(local.sum())==9
        hist=np.convolve(hist,local)
    assert int(hist.sum())==9**B
    other_hits=int((counts.sum(axis=1)-counts[np.arange(N),seed]).sum())
    expected=float(other_hits/3)
    exact_expected=float(np.dot(np.arange(len(hist)),hist)/float(9**B))
    if not math.isclose(exact_expected,expected,abs_tol=1e-10):
        raise AssertionError((exact_expected,expected))
    return {
      "H":obs,"p":float(hist[obs:].sum()/float(9**B)),
      "expected_H":expected,"excess_fraction":float((obs-expected)/(N*Q)),
      "practice_hit_fraction":float(obs/(N*Q))
    }

def softmax(x):
    exp=np.exp(x-x.max(axis=1,keepdims=True))
    return exp/exp.sum(axis=1,keepdims=True)

def generated_base(rng):
    seed,practice=assignments(rng)
    u=rng.normal(0,0.45,size=(N,K))
    d=rng.uniform(-0.10,0.10,size=(N,K))
    offset=rng.normal(0,0.07,size=(N,1))
    route_offset=rng.normal(0,0.025,size=(N,K))
    c0=1+offset+route_offset
    uniforms=rng.random((N,Q))
    return seed,practice,u,d,c0,uniforms

def evaluate(base,choice_effect,skill_effect):
    seed,practice,u,d,c0,uniforms=base
    a=np.eye(K)[seed]
    p=np.eye(K)[practice]
    utility=u+HS*a+(ETA*p if choice_effect else 0)-COST_SENS*d
    probs=softmax(utility)
    choice=np.sum(uniforms[:,:,None]>np.cumsum(probs,axis=1)[:,None,:],axis=2).astype(np.int8)
    counts=count_routes(choice)
    result=practice_null(counts,seed,practice)
    c1=c0-(GAMMA*p if skill_effect else 0)
    dc=c1-c0
    gain=np.mean((dc.sum(axis=1)-dc[np.arange(N),practice])/3-dc[np.arange(N),practice])
    result["G_cost"]=float(gain)
    result["seed_hit_fraction"]=float(counts[np.arange(N),seed].sum()/(N*Q))
    result["supported"]=bool(result["excess_fraction"]>0 and result["p"]<=.05)
    return result,choice,c1

def self_test():
    assert len(P24)==24
    s=np.array([0,1,2,3],np.int8)
    assert len(eligible_derangements(s))==9
    rng=np.random.default_rng(1234)
    for _ in range(25):
        seed,practice=assignments(rng)
        assert np.all(seed!=practice)
        counts=count_routes(rng.integers(0,K,size=(N,Q)))
        pr=practice_null(counts,seed,practice)
        assert 0<=pr["p"]<=1
    rng=np.random.default_rng(456)
    seed,practice=assignments(rng)
    counts=count_routes(rng.integers(0,K,size=(N,Q)))
    blocks=[]
    for j in (0,1):
        opts=eligible_derangements(seed[j*4:j*4+4])
        v=counts[np.arange(4)[None,:]+j*4,opts].sum(axis=1)
        blocks.append(v)
    from_dist=np.convolve(np.bincount(blocks[0],minlength=33),np.bincount(blocks[1],minlength=33))
    brute=np.bincount([int(i+j) for i in blocks[0] for j in blocks[1]],minlength=65)
    assert np.array_equal(from_dist,brute) and int(brute.sum())==81
    assert 9**5==59049
    return {"seed_assignments_per_block":24,"practice_derangements_per_block":9,"practice_null_assignments":59049,"two_block_81_cases":"PASS","exact_null_expected_practice_nonseed_fraction_over_3":"PASS"}

def summarize(values):
    x=np.asarray([v["supported"] for v in values],float)
    return {
      "supported_count":int(x.sum()),"supported_fraction":float(x.mean()),
      "mc_se":float(np.sqrt(x.mean()*(1-x.mean())/len(x))),
      "mean_H":float(np.mean([v["H"] for v in values])),
      "mean_excess_fraction":float(np.mean([v["excess_fraction"] for v in values])),
      "mean_practice_hit_fraction":float(np.mean([v["practice_hit_fraction"] for v in values])),
      "mean_seed_hit_fraction":float(np.mean([v["seed_hit_fraction"] for v in values])),
      "mean_cost_gain":float(np.mean([v["G_cost"] for v in values])),
      "median_p":float(np.median([v["p"] for v in values]))
    }

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--self-test",action="store_true")
    pa.add_argument("--out",default="ORTHOGONAL_ROUTE_PRACTICE_RESULT_V1.json")
    args=pa.parse_args()
    checks=self_test()
    if args.self_test:
        print(json.dumps(checks,indent=2));return
    root=np.random.SeedSequence(ROOT)
    unique=[("BASELINE_NO_PRACTICE",0),("PAIRED",1),("PRACTICE_SKILL_ONLY",2),("PRACTICE_FAMILIARITY_ONLY",3)]
    data={key:[] for key in SCENARIOS}
    integrity=0
    for (name,_),sceneseed in zip(unique,root.spawn(4)):
        for seed in sceneseed.spawn(MC):
            rng=np.random.default_rng(seed)
            base=generated_base(rng)
            if name=="PAIRED":
                a,aa,ac=evaluate(base,True,True)
                b,bb,bc=evaluate(base,True,True)
                assert np.array_equal(aa,bb) and np.array_equal(ac,bc) and a==b
                data["SKILL_CAUSES_CHOICE"].append(a)
                data["FAMILIARITY_CAUSES_CHOICE"].append(b)
                integrity+=1
            else:
                data[name].append(evaluate(base,*SCENARIOS[name])[0])
    out={
      "status":"SYNTHETIC_ONLY_NOT_ANIMAL_EVIDENCE",
      "contract":"ORTHOGONAL_ROUTE_PRACTICE_CONTRACT_V1.md",
      "n_animals":N,"routes":K,"target_trials":Q,"n_blocks":B,
      "legal_practice_assignments_conditional_on_seed":9**B,
      "root_seed":ROOT,"simulations_per_scenario":MC,
      "preflight":checks,"paired_identical_choice_and_cost_replicates":integrity,
      "scenarios":{k:summarize(v) for k,v in data.items()},
      "interpretation":"Independent practice assignment identifies a total choice effect and a performance effect, not skill mediation. SKILL_CAUSES_CHOICE and FAMILIARITY_CAUSES_CHOICE are exactly observationally equivalent for any external cost D under the fixed paired generators."
    }
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out["scenarios"][k] for k in SCENARIOS},indent=2))

if __name__=="__main__":
    main()
