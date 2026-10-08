#!/usr/bin/env python3
"""Four-route whole-path vs compositional motor-skill feedback.

Reproducible mathematical/synthetic diagnostic ONLY. No observed bat data.
See FOUR_ROUTE_SKILL_FEEDBACK_CONTRACT_V1.md for the locked tests.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import t as student_t

ETA, DELTA, K_MODULE = 0.20, 0.10, 2.0
A_COEX = 3.0 * math.log(3.0)
A_UNIFORM = 4.0
A_VALUES = (3.1, 3.25, A_COEX, 3.5, 3.9, 4.0, 4.3)
SEED_COUNTS = (0, 1, 2, 3, 6, 12)
N_ITER = 4000
N = 20
N_BLOCKS = 5
Q = 4
N_SIM = 1000
NOISE_STD = 0.08
GLOBAL_STD = 0.04
ROOT_SEED = 202610081747
MODEL_NAMES = ('WHOLE_ROUTE', 'SHARED_MANEUVERS', 'GLOBAL_FAMILIARITY')


def a_at_x(x: float) -> float:
    if not 0.25 < x < 1:
        raise ValueError('x must exceed 1/4 and be less than one')
    return 3.0 * math.log(3.0*x/(1.0-x)) / (4.0*x-1.0)


def tangency(x: float) -> float:
    return (4.0*x-1.0)/(x*(1.0-x))-4.0*math.log(3.0*x/(1.0-x))


def free_energy(p: np.ndarray, a: float) -> float:
    p = np.asarray(p, float)
    if p.shape != (4,) or not np.isclose(p.sum(), 1.0) or np.any(p <= 0):
        raise AssertionError('nonprobability vector')
    return float(a*0.5*np.sum(p*p) - np.sum(p*np.log(p)))


def whole_route_roots(a: float, xspin: float, aspin: float):
    if a <= aspin + 1e-11:
        return []
    xs = []
    if a < 4.0 - 1e-11:
        lower = brentq(lambda x:a_at_x(x)-a, 0.25+1e-9, xspin-1e-10,
                       xtol=1e-14, rtol=1e-14)
        xs.append(float(lower))
    upper = brentq(lambda x:a_at_x(x)-a, xspin+1e-10, 1-1e-10,
                   xtol=1e-14, rtol=1e-14)
    xs.append(float(upper))
    return xs


def root_summary(a: float, x: float):
    y = (1-x)/3
    p = np.asarray([x, y, y, y])
    eig_long = 1-DELTA+DELTA*a*(4*x*y)
    eig_minor = 1-DELTA+DELTA*a*y
    residual = math.log(x/y)-a*(x-y)
    return {
        'p_leader': float(x),
        'p_each_other': float(y),
        'fixed_point_logratio_residual':float(residual),
        'lambda_leader_vs_minors':float(eig_long),
        'lambda_minor_contrasts':float(eig_minor),
        'locally_attractive':bool(max(abs(eig_long), abs(eig_minor))<1),
        'free_energy_minus_uniform':float(free_energy(p,a)-free_energy(np.ones(4)/4,a))
    }


def softmax(v: np.ndarray, axis=-1) -> np.ndarray:
    w=np.asarray(v,dtype=float)
    z=np.exp(w-np.max(w,axis=axis,keepdims=True))
    return z/z.sum(axis=axis,keepdims=True)


def whole_route_fixedpoint(p: np.ndarray, a: float):
    return softmax(a*p)


def basin(a: float, n_seed: int):
    kappa = a*DELTA/ETA
    state=np.zeros(4, float)
    for _ in range(n_seed):
        state *= 1-DELTA
        state[0] += ETA
    for _ in range(N_ITER):
        state = (1-DELTA)*state + ETA*softmax(kappa*state)
    p=softmax(kappa*state)
    return {'initial_forced_choices':int(n_seed),
            'late_choice_practiced_route':float(p[0]),
            'late_skill_margin_over_other_routes':float(state[0]-state[1:].mean()),
            'classification':('SPECIALIZED' if p[0]>.60 else 'BALANCED')}


def module_factorization_test():
    h=np.asarray([.30,-.10])
    v=np.asarray([.20,-.25])
    joint=np.asarray([h[0]+v[0],h[0]+v[1],h[1]+v[0],h[1]+v[1]])
    calculated=softmax(K_MODULE*joint).reshape((2,2))
    product=np.outer(softmax(K_MODULE*h),softmax(K_MODULE*v))
    residual=float(np.max(np.abs(calculated-product)))
    if residual>1e-14:
        raise AssertionError(f'factorization failed {residual}')
    eig_module=1-DELTA+ETA*K_MODULE/2
    eig_whole_4=1-DELTA+ETA*K_MODULE/4
    return {
        'factorization_max_abs_error':residual,
        'g_module_each_axis':float(ETA*K_MODULE/(2*DELTA)),
        'g_whole_four_route':float(ETA*K_MODULE/(4*DELTA)),
        'jacobian_module_horizontal_contrast':float(eig_module),
        'jacobian_module_vertical_contrast':float(eig_module),
        'jacobian_whole_route_contrast':float(eig_whole_4),
        'fixed_skill_parameterization_warning':'Two module skills updated per flight; threshold comparison assumes per-component rates, not equal total learning resource.'
    }


def observed_transfer_effects(rng: np.random.Generator, name: str):
    trained = np.concatenate([rng.permutation(Q) for _ in range(N_BLOCKS)]).astype(int)
    shared_h = trained ^ 1
    shared_v = trained ^ 2
    neither = trained ^ 3
    if not all(set(trained[4*i:4*i+4])==set(range(Q)) for i in range(N_BLOCKS)):
        raise AssertionError('unbalanced random practice')
    if not np.all((shared_h!=shared_v)&(trained!=shared_h)&(neither!=shared_h)):
        raise AssertionError('route-sharing map drift')
    pre_true = 1 + rng.normal(0,.07,size=(N,1)) + rng.normal(0,.025,size=(N,4))
    gain=np.zeros((N,4))
    ii=np.arange(N)
    if name=='WHOLE_ROUTE':
        gain[ii,trained]=.20
    elif name=='SHARED_MANEUVERS':
        gain[ii,trained]=.20
        gain[ii,shared_h]=.10
        gain[ii,shared_v]=.10
    elif name=='GLOBAL_FAMILIARITY':
        gain[:,:]=.10
    else:
        raise ValueError(name)
    extra_global=rng.normal(0,GLOBAL_STD,size=(N,1))
    pre = pre_true[:,:,None] + rng.normal(0,NOISE_STD,size=(N,4,2))
    post=(pre_true-gain-extra_global)[:,:,None] + rng.normal(0,NOISE_STD,size=(N,4,2))
    improvement=np.mean(pre,axis=-1)-np.mean(post,axis=-1)
    c_individual=.5*(improvement[ii,shared_h]+improvement[ii,shared_v])-improvement[ii,neither]
    d_individual=improvement[ii,trained]-improvement[ii,neither]
    mean_c=float(c_individual.mean())
    sd_c=float(c_individual.std(ddof=1))
    sem=sd_c/math.sqrt(N)
    lower=mean_c-float(student_t.ppf(.975,N-1))*sem
    return {'C':mean_c, 'D':float(d_individual.mean()), 'C_positive_CI':bool(lower>0)}


def simulation_series(root: np.random.SeedSequence):
    scenarios={}
    for name, ss in zip(MODEL_NAMES,root.spawn(len(MODEL_NAMES))):
        points=[observed_transfer_effects(np.random.default_rng(seed),name)
                for seed in ss.spawn(N_SIM)]
        c=np.asarray([x['C'] for x in points]); d=np.asarray([x['D'] for x in points]);
        hit=np.asarray([x['C_positive_CI'] for x in points])
        frac=float(hit.mean())
        scenarios[name]={
            'mean_share_vs_neither_C':float(c.mean()),
            'mean_practiced_vs_neither_D':float(d.mean()),
            'std_C_across_synthetic_experiments':float(c.std(ddof=1)),
            'number_positive_95percent_t_interval_C':int(hit.sum()),
            'fraction_positive_95percent_t_interval_C':frac,
            'binomial_mc_se':float(np.sqrt(frac*(1-frac)/N_SIM)),
            'n_independent_synthetic_experiments':N_SIM,
        }
    return scenarios


def preflight():
    xspin=brentq(tangency,.251,.98,xtol=1e-15)
    aspin=a_at_x(xspin)
    if not aspin<A_COEX<A_UNIFORM:
        raise AssertionError('ordering of spinodal/coexistence/uniform lost')
    q=np.asarray([.75,1/12,1/12,1/12]); u=np.ones(4)/4
    assert np.max(np.abs(whole_route_fixedpoint(q,A_COEX)-q))<1e-13
    assert abs(free_energy(q,A_COEX)-free_energy(u,A_COEX))<1e-13
    assert len(whole_route_roots(3.5,xspin,aspin))==2
    assert not root_summary(3.5,whole_route_roots(3.5,xspin,aspin)[0])['locally_attractive']
    assert root_summary(3.5,whole_route_roots(3.5,xspin,aspin)[1])['locally_attractive']
    assert module_factorization_test()['factorization_max_abs_error']<1e-14
    expected={'WHOLE_ROUTE':(0,.2),'SHARED_MANEUVERS':(.1,.2),'GLOBAL_FAMILIARITY':(0,0)}
    for name,(c,d) in expected.items():
        rr=np.zeros(4)
        if name=='WHOLE_ROUTE':rr=[.2,0,0,0]
        elif name=='SHARED_MANEUVERS':rr=[.2,.1,.1,0]
        else:rr=[.1,.1,.1,.1]
        cc=.5*(rr[1]+rr[2])-rr[3]
        dd=rr[0]-rr[3]
        assert abs(cc-c)<1e-14 and abs(dd-d)<1e-14
    return {'mathematical_equal_free_energy':'PASS',
            'spinodal_below_coexistence_below_linear_instability':'PASS',
            'two_real_roots_one_unstable_one_attractive_A_3_5':'PASS',
            'four_route_module_factorization':'PASS',
            'three_expected_transfer_contrast_controls':'PASS'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--out',default='FOUR_ROUTE_SKILL_FEEDBACK_RESULT_V1.json')
    args=parser.parse_args()
    check=preflight()
    if args.self_test:
        print(json.dumps(check,indent=2));return
    xspin=float(brentq(tangency,.251,.98,xtol=1e-15))
    aspin=float(a_at_x(xspin))
    branches=[]
    for a in A_VALUES:
        r=[root_summary(a,x) for x in whole_route_roots(a,xspin,aspin)]
        uniform_eig=1-DELTA+DELTA*a/4
        uniform_stable=bool(uniform_eig<1-1e-12)
        for br in r:
            assert abs(br['fixed_point_logratio_residual'])<1e-10
        branches.append({'A':float(a),'uniform_contrast_eigenvalue':float(uniform_eig),
                         'uniform_locally_attractive':uniform_stable,
                         'dominant_branch_roots':r,
                         'number_locally_attractive_stationary_options':int(uniform_stable+4*sum(v['locally_attractive'] for v in r))})
    for b in branches:
        if abs(b['A']-3.5)<1e-12 and b['number_locally_attractive_stationary_options']!=5:
            raise AssertionError('expected coexisting uniform and 4 specialized routes')
    report={
       'evidence_status':'SYNTHETIC_FORMATION_MECHANISM_NOT_BAT_DATA',
       'contract':'FOUR_ROUTE_SKILL_FEEDBACK_CONTRACT_V1.md',
       'parameters':{'eta':ETA,'delta':DELTA,'kappa_module':K_MODULE,'root_seed':ROOT_SEED,
                     'n_experiments_per_transfer_model':N_SIM,'n_animals_per_experiment':N},
       'analytic':{
          'critical_first_dominant_at_x':xspin,
          'four_route_saddle_node_A':aspin,
          'four_route_potential_equal_A':A_COEX,
          'four_route_uniform_linear_instability_A':A_UNIFORM,
          'four_route_A_scan':branches,
          'module_factorization':module_factorization_test(),
          'A_3_5_forced_exposure_basin_diagnostic':[basin(3.5,m) for m in SEED_COUNTS]
       },
       'measurement_transfer_synthetic':{
         'three_fixed_models':simulation_series(np.random.SeedSequence(ROOT_SEED)),
         'hypothetical_cost_gain_W_M_G':{'WHOLE_ROUTE':[.2,0,0,0],
              'SHARED_MANEUVERS':[.2,.1,.1,0],
              'GLOBAL_FAMILIARITY':[.1,.1,.1,.1]},
         'metric':'C=mean_one_shared_component_improvement - share_neither_improvement',
         'route_mapping':'L-low,L-high,R-low,R-high',
         'measurement_noise_sd':NOISE_STD,'extra_individual_global_gain_sd':GLOBAL_STD,
         'note':'Nominal t-interval simulation diagnostic; not a real experimental p-value.'
       },
       'preflight':check,
       'ceiling':[
        'Four-state mean-field Potts-like discontinuity is established mathematical theory, not a novel dynamical law.',
        'No bat data, cost measurements, or fitness effects have been observed in this calculation.',
        'Module transfer can also be due to common visual/acoustic cues or shared task demands.',
        'Models W/M do not equate total per-flight practice resource: M updates two skills.',
        'Randomized practice and independent pre/post performance on all four routes are required to test motor modularity.'
       ]
    }
    path=Path(args.out)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('four_route_spinodal',round(aspin,10),'coexist',round(A_COEX,10),'linear',A_UNIFORM)
    print('A=3.5 fixed points',[(round(x['p_leader'],6),x['locally_attractive']) for x in branches[3]['dominant_branch_roots']])
    print('initial_forced_choices_basin',[(x['initial_forced_choices'],round(x['late_choice_practiced_route'],6),x['classification']) for x in report['analytic']['A_3_5_forced_exposure_basin_diagnostic']])
    print('transfer',[(k,round(v['mean_share_vs_neither_C'],5),v['number_positive_95percent_t_interval_C']) for k,v in report['measurement_transfer_synthetic']['three_fixed_models'].items()])
    print('json',str(path))


if __name__=='__main__':main()
