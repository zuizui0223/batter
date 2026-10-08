#!/usr/bin/env python3
"""Synthetic two-route skill reinforcement: bifurcation and environmental reversal."""
import json
import numpy as np
from scipy.optimize import brentq

ETA,DECAY,ALPHA,BETA=0.20,0.10,1.0,2.0
KAPPA=ALPHA*BETA
ROOT_SEED=202610081818

def drift(d,delta_reward=0):
    return -DECAY*d+ETA*np.tanh((KAPPA*d+ALPHA*delta_reward)/2)

def equilibria(delta_reward):
    xs=np.linspace(-ETA/DECAY-.01,ETA/DECAY+.01,10002)
    vals=drift(xs,delta_reward)
    roots=[]
    for i in range(len(xs)-1):
        if vals[i]*vals[i+1]<0:
            root=brentq(lambda x:drift(x,delta_reward),xs[i],xs[i+1])
            if not roots or abs(roots[-1]-root)>1e-6:
                roots.append(root)
    return [{'d':float(x),
             'local_derivative':float(1-DECAY+ETA*KAPPA/2/np.cosh((KAPPA*x+ALPHA*delta_reward)/2)**2),
             'stable':bool(abs(1-DECAY+ETA*KAPPA/2/np.cosh((KAPPA*x+ALPHA*delta_reward)/2)**2)<1)}
            for x in roots]

def run():
    g=ETA*KAPPA/(2*DECAY)
    if not g>1:raise RuntimeError('The registered scenario requires bifurcation gain > 1.')
    critical=(KAPPA*(ETA/DECAY)*np.sqrt(1-1/g)-2*np.arccosh(np.sqrt(g)))/ALPHA
    by_reward={str(x):equilibria(x) for x in [-1.2,-1.0,-.5,0,.5,1.0,1.2]}
    if [len(by_reward[str(x)]) for x in [-1.2,-1.0,-.5,0,.5,1.0,1.2]]!=[1,3,3,3,3,3,1]:
        raise AssertionError('Equilibrium branch count drift')
    rng=np.random.default_rng(ROOT_SEED)
    n=2000
    state=np.zeros(n)
    first=np.zeros(n)
    for t in range(1500):
        p=1/(1+np.exp(-KAPPA*state))
        choose=rng.random(n)<p
        state=(1-DECAY)*state+ETA*np.where(choose,1,-1)
        if t==799:first=state.copy()
    same=float(np.mean(np.sign(first)==np.sign(state)))
    q=np.quantile(state,[.01,.05,.25,.5,.75,.95,.99])
    low=np.zeros(n)
    for t in range(1500):
        p=1/(1+np.exp(-.6*low))
        low=(1-DECAY)*low+ETA*np.where(rng.random(n)<p,1,-1)
    result={'status':'SYNTHETIC_FINITE_STATE_MEAN_FIELD_MODEL',
        'parameters':{'eta':ETA,'decay':DECAY,'alpha':ALPHA,'beta':BETA,'gain':float(g),'critical_reward_gap':float(critical)},
        'equilibria_by_bonus':by_reward,
        'synthetic_2000_individuals':{
          'P_end_positive':float(np.mean(state>0)),
          'fraction_same_branch_between_t800_and_t1500':same,
          'end_quantiles':q.tolist(),
          'end_sd':float(np.std(state)),
          'low_feedback_gain_0_6_sd':float(np.std(low))
        }}
    print(json.dumps(result,indent=2))
    with open('SKILL_FEEDBACK_PHASE_RESULT_V1.json','w') as f:
        json.dump(result,f,indent=2);f.write('\n')
if __name__=='__main__':run()
