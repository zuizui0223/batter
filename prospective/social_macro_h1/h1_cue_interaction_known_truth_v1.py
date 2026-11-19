#!/usr/bin/env python3
"""Known-truth interaction-identifiability control for H1.

Synthetic ONLY: 12 lake clusters, randomized 5-level feeding-buzz content,
pre-period activity X, playback response Y, no observed bat data.
The fitted model adjusts X directly in Y (rather than fitting Y-X against X).
"""
from __future__ import annotations
import json
import random
from pathlib import Path

BUZZ=(0,12,24,48,96)
N_LAKES=12
N_PER_LAKE=30
REPS=128
SEED=31192026

def solve(matrix,vector):
    n=len(vector)
    a=[list(map(float,matrix[i]))+[float(vector[i])] for i in range(n)]
    for p in range(n):
        pivot=max(range(p,n),key=lambda i:abs(a[i][p]))
        if abs(a[pivot][p])<1e-12:
            raise ValueError("ill-conditioned known-truth design")
        a[p],a[pivot]=a[pivot],a[p]
        scale=a[p][p]
        for k in range(p,n+1):a[p][k]/=scale
        for j in range(n):
            if j==p:continue
            c=a[j][p]
            for k in range(p,n+1):a[j][k]-=c*a[p][k]
    return [a[p][-1] for p in range(n)]

def centered(rows):
    groups={}
    for s,x,b,y in rows:
        groups.setdefault(s,[]).append((x,b,x*b,y))
    out=[]
    for g in groups.values():
        avg=[sum(r[i] for r in g)/len(g) for i in range(4)]
        out.extend(tuple(r[i]-avg[i] for i in range(4)) for r in g)
    return out

def estimated_interaction(rows):
    m=centered(rows)
    features=[r[:3] for r in m]
    lhs=[[sum(f[i]*f[j] for f in features) for j in range(3)] for i in range(3)]
    rhs=[sum(f[i]*r[3] for f,r in zip(features,m)) for i in range(3)]
    return solve(lhs,rhs)[2]

def mechanical_delta_baseline_slope(rows):
    # Slopes after lake-centering; no independently manipulated social-density effect.
    data={}
    for s,x,b,y in rows:data.setdefault(s,[]).append((x,y-x))
    xs=[];ds=[]
    for rr in data.values():
        mx=sum(x for x,_ in rr)/len(rr)
        md=sum(d for _,d in rr)/len(rr)
        xs.extend(x-mx for x,_ in rr)
        ds.extend(d-md for _,d in rr)
    return sum(x*d for x,d in zip(xs,ds))/sum(x*x for x in xs)

def one_world(rng,interaction=0.0):
    rows=[]
    for lake in range(N_LAKES):
        site_intercept=rng.gauss(3,2)
        treatments=[BUZZ[(i+lake)%len(BUZZ)] for i in range(N_PER_LAKE)]
        rng.shuffle(treatments)
        for z in treatments:
            x=rng.gauss(0,1)
            b=z/96
            y=site_intercept+0.65*x+0.25*b+interaction*x*b+rng.gauss(0,1)
            rows.append((lake,x,b,y))
    return rows

def run():
    rng=random.Random(SEED)
    out={}
    for label,beta in [("null_no_cue_density_moderation",0.0),("positive_true_cue_density_moderation",0.8)]:
        estimates=[]; naive=[]
        for _ in range(REPS):
            rows=one_world(rng,beta)
            estimates.append(estimated_interaction(rows))
            naive.append(mechanical_delta_baseline_slope(rows))
        out[label]={
            "true_buzz_x_pre_interaction":beta,
            "mean_recovered_interaction":round(sum(estimates)/len(estimates),6),
            "mean_naive_change_vs_pre_slope":round(sum(naive)/len(naive),6),
            "repetitions":REPS,"lakes":N_LAKES,"blocks_per_lake":N_PER_LAKE,
            "estimates_positive":sum(e>0 for e in estimates),
            "min_recovered_interaction":round(min(estimates),6),
            "max_recovered_interaction":round(max(estimates),6),
        }
    return {"status":"SYNTHETIC_KNOWN_TRUTH_ONLY",
            "design":"within-lake fixed-effect OLS of Y_playback ~ X_pre + buzz + buzz×X_pre",
            "estimator_identification":"no source-based empirical effect inferred",
            "results":out,
            "original2019_data":"UNAVAILABLE_AT_LAST_GATE"}
if __name__=="__main__":
    result=run()
    print(json.dumps(result,indent=2)+"\n")
