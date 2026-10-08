#!/usr/bin/env python3
"""Synthetic payoff revaluation versus acquired motor skill; NOT bat data.

All numeric choices locked in ROUTE_HISTORY_PAYOFF_IDENTIFIABILITY_CONTRACT_V1.md.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
from pathlib import Path
import numpy as np

N, K, BLOCKS, Q, R = 20, 4, 5, 8, 1000
SEED = 202610081510
H, GAMMA, A = 2.0, 0.35, 2.0 / 0.35
LOW, HIGH = 0.25, 0.60
COST_NOISE = 0.20
N_COST_PERMS = 1999
P24 = np.asarray(list(itertools.permutations(range(K))), dtype=np.int8)


def draw_assignments(rng):
    seed = np.concatenate([rng.permutation(K) for _ in range(BLOCKS)]).astype(np.int8)
    bonus = np.concatenate([rng.permutation(K) for _ in range(BLOCKS)]).astype(np.int8)
    return seed, bonus


def softmax(a):
    x = a - a.max(axis=1, keepdims=True)
    x = np.exp(x)
    return x / x.sum(axis=1, keepdims=True)


def draw_choices(rng, probabilities):
    u = rng.random((N, Q))
    return np.sum(u[:, :, None] > np.cumsum(probabilities, axis=1)[:, None, :], axis=2).astype(np.int8)


def counts_by_route(route_choices):
    if route_choices.shape != (N, Q):
        raise RuntimeError('wrong synthetic input support')
    return np.stack([(route_choices == r).sum(axis=1) for r in range(K)], axis=1)


def exact_route_hit(counts, assigned):
    if counts.shape != (N, K) or assigned.shape != (N,):
        raise ValueError('shape drift')
    observed = int(counts[np.arange(N), assigned].sum())
    hist = np.array([1], dtype=np.int64)
    for block in range(BLOCKS):
        c = counts[block * K:(block + 1) * K]
        mapping_hits = c[np.arange(K)[None, :], P24].sum(axis=1)
        h = np.bincount(mapping_hits, minlength=K * Q + 1).astype(np.int64)
        if h.sum() != 24:
            raise RuntimeError('bad block histogram')
        hist = np.convolve(hist, h)
    legal = int(24 ** BLOCKS)
    if hist.sum() != legal:
        raise RuntimeError('bad global histogram')
    return {'p': float(hist[observed:].sum() / legal),
            'hit_rate': float(observed / (N * Q)),
            'excess': float(observed / (N * Q) - 0.25),
            'hits': observed}


def measured_skill_gain(pre, post, seed):
    if pre.shape != (N, K, 2) or post.shape != (N, K, 2):
        raise RuntimeError('technical performance cell mismatch')
    d = post.mean(axis=2) - pre.mean(axis=2)
    s = d[np.arange(N), seed]
    mean_others = (d.sum(axis=1) - s) / (K - 1)
    return float(np.mean(mean_others - s)), d


def performance_perm_test(d, seed, maps):
    observed = float(np.mean(((d.sum(axis=1) - d[np.arange(N), seed]) / 3) - d[np.arange(N), seed]))
    vals = d[np.arange(N)[None, :], maps]
    null = d.sum(axis=1).mean() / 3 - (4 / 3) * vals.mean(axis=1)
    p = (1 + int(np.count_nonzero(null >= observed - 1e-12))) / (len(null) + 1)
    return {'gain': observed, 'p': p}


def regret(q, base_cost, seeds, bonus_routes, bonus, skill_saving):
    true_post_cost = base_cost - skill_saving * np.eye(K)[seeds]
    reward = bonus * np.eye(K)[bonus_routes]
    net = reward - true_post_cost
    regret_vector = net.max(axis=1) - np.sum(q * net, axis=1)
    mismatch = seeds != bonus_routes
    return float(regret_vector[mismatch].mean())


def conf_res(q, seeds, bonus_routes):
    mismatch = seeds != bonus_routes
    return {
       'n_mismatch': int(mismatch.sum()),
       'seed_choice_probability': float(q[np.arange(N), seeds][mismatch].mean()),
       'bonus_choice_probability': float(q[np.arange(N), bonus_routes][mismatch].mean()),
    }


def one_experiment(root):
    assignment_rng, route_rng, technical_rng, permutation_rng = [np.random.default_rng(s) for s in root.spawn(4)]
    seed, bonus_route = draw_assignments(assignment_rng)
    if not all(sorted(seed[k:k+4]) == list(range(4)) and sorted(bonus_route[k:k+4]) == list(range(4)) for k in range(0,N,4)):
        raise AssertionError('balance failed')
    intrinsic = route_rng.normal(0, 0.45, size=(N,K))
    seed_offset = H * np.eye(K)[seed]
    bonus_indicator = np.eye(K)[bonus_route]
    q0 = softmax(intrinsic + seed_offset)
    qlow = softmax(intrinsic + seed_offset + A * LOW * bonus_indicator)
    qhigh = softmax(intrinsic + seed_offset + A * HIGH * bonus_indicator)
    y0, ylow, yhigh = [draw_choices(route_rng, q) for q in (q0, qlow, qhigh)]
    # Both biological worlds have exactly identical choice observations by construction.
    habit_choices = (y0.copy(), ylow.copy(), yhigh.copy())
    skill_choices = (y0.copy(), ylow.copy(), yhigh.copy())
    assert all(np.array_equal(a,b) for a,b in zip(habit_choices,skill_choices))
    seed_res = exact_route_hit(counts_by_route(y0), seed)
    bonus_lo = exact_route_hit(counts_by_route(ylow), bonus_route)
    bonus_hi = exact_route_hit(counts_by_route(yhigh), bonus_route)
    # Technical route costs are measured independently, with balanced forced trials AFTER choices.
    c0 = 1 + technical_rng.normal(0, 0.07, size=(N,1)) + technical_rng.normal(0,0.025,size=(N,K))
    noise_pre = technical_rng.normal(0,COST_NOISE,size=(N,K,2))
    noise_post = technical_rng.normal(0,COST_NOISE,size=(N,K,2))
    pre = c0[:,:,None] + noise_pre
    habit_post = c0[:,:,None] + noise_post
    skill_post = habit_post - GAMMA * np.eye(K)[seed][:,:,None]
    gh, dh = measured_skill_gain(pre, habit_post, seed)
    gs, ds = measured_skill_gain(pre, skill_post, seed)
    assert np.isclose(gs - gh, GAMMA, atol=1e-13), 'performance-label coupling violation'
    maps = P24[permutation_rng.integers(0,24,size=(N_COST_PERMS,BLOCKS))].reshape(N_COST_PERMS,N)
    cost_habit = performance_perm_test(dh, seed, maps)
    cost_skill = performance_perm_test(ds, seed, maps)
    assert math.isclose(cost_habit['gain'],gh,abs_tol=1e-12)
    assert math.isclose(cost_skill['gain'],gs,abs_tol=1e-12)
    return {
      'seed':seed_res, 'bonus_low':bonus_lo, 'bonus_high':bonus_hi,
      'trait_only_seed_control':exact_route_hit(counts_by_route(draw_choices(route_rng,softmax(intrinsic))), seed),
      'no_bonus_control':exact_route_hit(counts_by_route(draw_choices(route_rng,q0)), bonus_route),
      'habit_cost':cost_habit, 'skill_cost':cost_skill,
      'conflict_low':conf_res(qlow,seed,bonus_route),
      'conflict_high':conf_res(qhigh,seed,bonus_route),
      'habit_regret_low':regret(qlow,c0,seed,bonus_route,LOW,0),
      'skill_regret_low':regret(qlow,c0,seed,bonus_route,LOW,GAMMA),
      'habit_regret_high':regret(qhigh,c0,seed,bonus_route,HIGH,0),
      'skill_regret_high':regret(qhigh,c0,seed,bonus_route,HIGH,GAMMA),
      'choice_data_exactly_equal':True,
    }


def preflight():
    assert len(P24)==24 and len({tuple(row) for row in P24})==24
    assert 24**5==7_962_624
    toy = np.array([[2,4,1,1],[0,2,5,1],[4,2,1,1],[1,0,2,5],
                    [1,2,2,3],[4,0,0,4],[0,1,3,4],[2,1,2,3]])
    groups=[]
    for p in (toy[:4],toy[4:]):
        counts = [int(p[np.arange(4),pr].sum()) for pr in P24]
        groups.append(np.bincount(counts,minlength=33))
    hist=np.convolve(groups[0],groups[1])
    brute=np.zeros(len(hist),dtype=np.int64)
    for p in P24:
      for q in P24:
        hit=int(toy[:4][np.arange(4),p].sum()+toy[4:][np.arange(4),q].sum())
        brute[hit]+=1
    assert np.array_equal(hist,brute) and hist.sum()==576
    rng=np.random.default_rng(111)
    for _ in range(20):
        s,b=draw_assignments(rng)
        assert all(sorted(s[k:k+4])==list(range(4)) for k in range(0,20,4))
        assert all(sorted(b[k:k+4])==list(range(4)) for k in range(0,20,4))
        counts=counts_by_route(rng.integers(0,4,size=(20,8)))
        p=exact_route_hit(counts,s)
        assert 0<=p['p']<=1
    return dict(exact_assignments=24**5, brute_force_576='PASS', balanced_independent_seed_and_bonus='PASS', route_choice_coupling='VERIFIED_AT_EVERY_REPLICATION', skill_gain_delta_identity='VERIFIED_AT_EVERY_REPLICATION')


def summarize(rows):
    def metric(p):return np.asarray([p(x) for x in rows],dtype=float)
    e1=metric(lambda x:x['seed']['excess'])
    for_key={}
    for id,k in [('seed','seed'),('bonus_low','bonus_low'),('bonus_high','bonus_high'),('trait_null_seed','trait_only_seed_control'),('bonus_null','no_bonus_control'),('habit_cost','habit_cost'),('skill_cost','skill_cost')]:
        eff_key='gain' if 'cost' in id else 'excess'
        effects=metric(lambda x:x[k][eff_key]); pp=metric(lambda x:x[k]['p'])
        yes=(effects>0)&(pp<=0.05)
        frequency=float(np.mean(yes))
        for_key[id]=dict(mean_effect=float(effects.mean()),support_count=int(yes.sum()),support_fraction=frequency,mc_se=float(np.sqrt(frequency*(1-frequency)/len(rows))),median_p=float(np.median(pp)))
    s={**for_key,'conflicts':{},'true_regret':{},'n_replicates':len(rows)}
    for bonus in ('low','high'):
        s['conflicts'][bonus]={name:float(metric(lambda x:x['conflict_'+bonus][name]).mean()) for name in ('n_mismatch','seed_choice_probability','bonus_choice_probability')}
        s['true_regret'][bonus]={m:float(metric(lambda x:x[m+'_regret_'+bonus]).mean()) for m in ('habit','skill')}
    s['both_seed_and_skill_cost_fraction']=float(np.mean(metric(lambda x:float(x['seed']['excess']>0 and x['seed']['p']<=.05 and x['skill_cost']['gain']>0 and x['skill_cost']['p']<=.05))))
    s['both_seed_and_habit_cost_fraction']=float(np.mean(metric(lambda x:float(x['seed']['excess']>0 and x['seed']['p']<=.05 and x['habit_cost']['gain']>0 and x['habit_cost']['p']<=.05))))
    s['observed_behavior_identical_between_worlds']=bool(all(x['choice_data_exactly_equal'] for x in rows))
    s['exactly_equal_choice_test_statistics_by_construction']=True
    return s


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--self-test',action='store_true')
    a.add_argument('--out',default='ROUTE_HISTORY_PAYOFF_SIMULATION_RESULT_V1.json')
    v=a.parse_args()
    tests=preflight()
    if v.self_test:
        print(json.dumps(tests,indent=2))
        return
    root=np.random.SeedSequence(SEED)
    observations=[]
    for s in root.spawn(R):
        observations.append(one_experiment(s))
    data={'tier':'SYNTHETIC_PROSPECTIVE_NOT_BAT_EVIDENCE','contract':'ROUTE_HISTORY_PAYOFF_IDENTIFIABILITY_CONTRACT_V1.md','seed':SEED,'n_synthetic_experiments':R,'bats':N,'num_routes':K,'route_choices_per_context':Q,'bonus_magnitudes':[LOW,HIGH],'history_utility_parameter':H,'motor_skill_cost_reduction':GAMMA,'choice_inverse_utility_scale':A,'exact_assignments':24**5,'cost_permutation_samples':N_COST_PERMS,'preflight':tests,'results':summarize(observations),'limitations':['Not a biological finding or actual future animal design.','Route-choice observations are exactly identical by construction for HABIT_PRIOR and SKILL_BENEFIT.','The cost saving is generated by assumption and measured in synthetic comparable payoff units only.','Any real experiment requires pre-randomization performance baseline, carefully controlled reward, counterfactual flight-cost assessment and ethical review.']}
    Path(v.out).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(data['results'],indent=2,sort_keys=True))

if __name__=='__main__':main()
