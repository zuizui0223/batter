#!/usr/bin/env python3
from __future__ import annotations

import json, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"prospective/decentralized_route_theory/simulation_v1.json"
OUT_MD=ROOT/"prospective/decentralized_route_theory/SIMULATION_RESULT_V1.md"

SEED=20261003073
RNG=np.random.default_rng(SEED)

def entropy_from_counts(counts):
    x=np.asarray(counts,dtype=float)
    s=x.sum(axis=-1,keepdims=True)
    p=np.divide(x,s,out=np.zeros_like(x),where=s>0)
    with np.errstate(divide="ignore",invalid="ignore"):
        logp=np.where(p>0,np.log(p),0.0)
    return -np.sum(p*logp,axis=-1)

def exact_grid():
    rows=[]
    for K in (3,5,10):
        for a in (0.1,0.5,1.0,5.0,20.0):
            n=50000
            theta=RNG.dirichlet(np.full(K,a),size=n)
            self_emp=float(np.mean(np.sum(theta*theta,axis=1)))
            theta2=RNG.dirichlet(np.full(K,a),size=n)
            other_emp=float(np.mean(np.sum(theta*theta2,axis=1)))

            self_theory=(a+1.0)/(K*a+1.0)
            other_theory=1.0/K
            delta_theory=(K-1.0)/(K*(K*a+1.0))
            rows.append({
                "K":K,"a":a,
                "self_theory":self_theory,
                "self_sim":self_emp,
                "other_theory":other_theory,
                "other_sim":other_emp,
                "delta_theory":delta_theory,
                "delta_sim":self_emp-other_emp,
                "abs_error_self":abs(self_emp-self_theory),
                "abs_error_other":abs(other_emp-other_theory),
                "abs_error_delta":abs((self_emp-other_emp)-delta_theory),
            })
    return rows

def choose(probs,rng):
    return int(rng.choice(len(probs),p=probs))

def explore_refine(K=5,n_ind=4000,T=60,a=1.0,rho=1.8):
    choices=np.empty((n_ind,T),dtype=np.int16)
    counts=np.zeros((n_ind,K),dtype=np.int32)

    eps=[]
    for t in range(T):
        e=0.05+0.85*math.exp(-t/12.0)
        eps.append(e)
        for i in range(n_ind):
            w=(a+counts[i].astype(float))**rho
            exploit=w/w.sum()
            p=e*np.full(K,1.0/K)+(1.0-e)*exploit
            k=choose(p,RNG)
            choices[i,t]=k
            counts[i,k]+=1

    early=np.zeros((n_ind,K),dtype=int)
    late=np.zeros((n_ind,K),dtype=int)
    for i in range(n_ind):
        early[i]=np.bincount(choices[i,:10],minlength=K)
        late[i]=np.bincount(choices[i,-10:],minlength=K)

    H_early=entropy_from_counts(early)
    H_late=entropy_from_counts(late)

    # Same-individual route match probability in late window.
    late_p=late/late.sum(axis=1,keepdims=True)
    self_match=float(np.mean(np.sum(late_p*late_p,axis=1)))

    # Between-individual match using a deterministic pairing.
    other_p=np.roll(late_p,1,axis=0)
    other_match=float(np.mean(np.sum(late_p*other_p,axis=1)))

    # Whether first-20 dominant route remains dominant in last-20.
    first20=np.array([np.bincount(x[:20],minlength=K) for x in choices])
    last20=np.array([np.bincount(x[-20:],minlength=K) for x in choices])
    first_dom=np.argmax(first20,axis=1)
    last_dom=np.argmax(last20,axis=1)
    dominant_persistence=float(np.mean(first_dom==last_dom))

    # Population marginal should remain near symmetric.
    pop=np.bincount(choices.ravel(),minlength=K)/choices.size

    return {
        "K":K,"n_individuals":n_ind,"trips":T,"a":a,"rho":rho,
        "exploration_schedule":{"first":eps[0],"trip_10":eps[9],"trip_30":eps[29],"last":eps[-1]},
        "mean_early_10_trip_entropy":float(np.mean(H_early)),
        "mean_late_10_trip_entropy":float(np.mean(H_late)),
        "entropy_change_late_minus_early":float(np.mean(H_late)-np.mean(H_early)),
        "late_self_match":self_match,
        "late_between_match":other_match,
        "late_self_advantage":self_match-other_match,
        "first20_to_last20_dominant_route_persistence":dominant_persistence,
        "population_route_fractions":pop.tolist(),
    }

def overlap_geometry(K=5,a=0.5,n_ind=5000):
    # Strongly overlapping latent vertical profiles.
    z=np.linspace(-100,100,81)
    means=np.linspace(-20,20,K)
    sigma=45.0
    G=np.stack([np.exp(-0.5*((z-m)/sigma)**2) for m in means],axis=1)
    G=G/G.sum(axis=0,keepdims=True)

    theta=RNG.dirichlet(np.full(K,a),size=n_ind)
    F=theta@G.T

    # Pair each individual with the next individual.
    F2=np.roll(F,1,axis=0)
    tv=0.5*np.sum(np.abs(F-F2),axis=1)

    # Latent route-mixture distance is much larger than realized vertical TV
    # when route profiles overlap strongly.
    th2=np.roll(theta,1,axis=0)
    latent_tv=0.5*np.sum(np.abs(theta-th2),axis=1)

    return {
      "K":K,"a":a,"sigma_vertical_profile":sigma,
      "mean_pairwise_latent_route_TV":float(np.mean(latent_tv)),
      "mean_pairwise_realized_vertical_TV":float(np.mean(tv)),
      "attenuation_ratio_vertical_over_latent":float(np.mean(tv)/np.mean(latent_tv)),
      "interpretation":"Strong route-mixture individuality can map to weak spatial/vertical segregation when latent route geometries overlap."
    }

def main():
    exact=exact_grid()
    maxerr=max(max(r["abs_error_self"],r["abs_error_other"],r["abs_error_delta"]) for r in exact)
    er=explore_refine()
    geom=overlap_geometry()

    payload={
      "schema_version":1,
      "study_id":"decentralized-airway-theory-simulation-v1",
      "classification":"theoretical simulation; no empirical bat outcome",
      "seed":SEED,
      "exact_polya_validation":{"rows":exact,"max_absolute_error":maxerr,"pass":maxerr<0.01},
      "exploration_refinement":er,
      "overlapping_geometry":geom,
      "claim_boundary":"demonstrates sufficiency of a mechanism class, not empirical identification"
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
      "# Decentralized airway simulation result v1","",
      "**THEORETICAL ONLY — no empirical bat outcome.**","",
      f"Exact Pólya formula validation max absolute simulation error: **{maxerr:.4f}**.",
      "",
      "## Exploration → refinement extension","",
      f"- early 10-trip entropy: **{er['mean_early_10_trip_entropy']:.3f} nats**",
      f"- late 10-trip entropy: **{er['mean_late_10_trip_entropy']:.3f} nats**",
      f"- late − early entropy: **{er['entropy_change_late_minus_early']:.3f} nats**",
      f"- late same-individual route match: **{er['late_self_match']:.3f}**",
      f"- late between-individual route match: **{er['late_between_match']:.3f}**",
      f"- late self advantage: **{er['late_self_advantage']:.3f}**",
      f"- first-20 dominant route still dominant in last-20: **{er['first20_to_last20_dominant_route_persistence']:.3f}**",
      "",
      "Population route fractions:",
      ", ".join(f"{x:.3f}" for x in er["population_route_fractions"]),
      "",
      "## Overlapping geometry","",
      f"- latent route-mixture TV: **{geom['mean_pairwise_latent_route_TV']:.3f}**",
      f"- realized vertical-distribution TV: **{geom['mean_pairwise_realized_vertical_TV']:.3f}**",
      f"- vertical/latent attenuation ratio: **{geom['attenuation_ratio_vertical_over_latent']:.3f}**",
      "",
      "Interpretation: individual route mixtures can diverge strongly while their realized vertical distributions remain highly overlapping.",
      ""
    ]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
      "polya_formula_pass":payload["exact_polya_validation"]["pass"],
      "max_abs_error":maxerr,
      "early_entropy":er["mean_early_10_trip_entropy"],
      "late_entropy":er["mean_late_10_trip_entropy"],
      "late_self_advantage":er["late_self_advantage"],
      "dominant_persistence":er["first20_to_last20_dominant_route_persistence"],
      "vertical_over_latent_TV":geom["attenuation_ratio_vertical_over_latent"],
    },sort_keys=True))

if __name__=="__main__":
    main()
