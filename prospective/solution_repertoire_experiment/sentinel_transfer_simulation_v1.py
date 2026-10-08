#!/usr/bin/env python3
"""Synthetic ONLY: no actual bat data; exact target-route transfer randomization.

Follows SENTINEL_UNTRAINED_ROUTE_CONTRACT_V1.md. Python 3.13/NumPy 2.3.5.
"""
from __future__ import annotations
import argparse
from itertools import permutations, product
import json
from pathlib import Path
import numpy as np

ROOT_SEED = 202610081858
R = 1000
NBLOCKS = 6
N = 18
Q_PRE = 2
Q_POST = 2
N_LATE_ROUTES = 4
R4 = 3
K_LOCAL = 3
PERMS = np.asarray(list(permutations((0, 1, 2))), dtype=np.int8)
# Assigned training routes map N(0)->R1, V(1)->R2, H(2)->R3.
TRAIN_ROUTES = np.array((0, 1, 2))
SCENARIO_GAINS = {
    "WHOLE_ROUTE_ONLY": (0.0, 0.0, 0.0),
    "GLOBAL_FAMILIARITY": (0.12, 0.12, 0.12),
    "SHARED_MOTOR_MODULE": (0.0, 0.12, 0.12),
    "SHARED_SENSORY_CUE": (0.0, 0.12, 0.12),
    "HORIZONTAL_ONLY_TRANSFER": (0.0, 0.0, 0.24),
    "WEAK_SHARED_MODULE": (0.0, 0.06, 0.06),
}


def random_labels(rng):
    labels = np.concatenate([rng.permutation(K_LOCAL) for _ in range(NBLOCKS)]).astype(np.int8)
    if len(labels) != N or not all(sorted(labels[3*j:3*j+3]) == [0,1,2] for j in range(NBLOCKS)):
        raise AssertionError("incorrect exactly-one-of-each complete block")
    if np.any(TRAIN_ROUTES[labels] == R4):
        raise AssertionError("sentinel cannot be trained")
    return labels


def block_contributions_from_labels(y, labels):
    """Mean shared (H,V) minus unrelated (N), one contribution per block."""
    out = []
    for b in range(NBLOCKS):
        v = y[3*b:3*b+3]
        l = labels[3*b:3*b+3]
        out.append(float(0.5 * (v[l==1][0] + v[l==2][0]) - v[l==0][0]))
    return np.asarray(out)


def exact_block_test(y, labels):
    """6! not needed: H,V swap has the same contrast; use 3^6 exact values x64."""
    y = np.asarray(y, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int8)
    if y.shape != (N,) or labels.shape != (N,) or not np.all(np.isfinite(y)):
        raise ValueError("bad sentinel support")
    obs = float(np.mean(block_contributions_from_labels(y, labels)))
    local = np.asarray([0.5 * np.sum(y[3*b:3*b+3]) - 1.5*y[3*b:3*b+3]
                        for b in range(NBLOCKS)])
    # Each N choice has TWO equally likely H/V assignments.
    # The full 6^6 allocations therefore consist of 2^6 copies of these 3^6 statistics.
    null = np.zeros(1, dtype=np.float64)
    for arr in local:
        null = (null[:,None]+arr[None,:]).reshape(-1)
    null /= NBLOCKS
    if len(null) != 3**NBLOCKS:
        raise AssertionError("wrong number of distinct label-orbits")
    extreme_unique = int(np.count_nonzero(null >= obs - 1e-12))
    num = extreme_unique * 2**NBLOCKS
    den = 6**NBLOCKS
    if not np.isclose(np.mean(null),0,atol=1e-12) or num > den:
        raise AssertionError("wrong exact mean / multiplicity")
    armmeans = {code:float(np.mean(y[labels == code])) for code in range(3)}
    return {
        "T":obs,
        "p_exact":float(num/den),
        "n_allocations":int(den),
        "n_effective_unique_allocations":int(3**NBLOCKS),
        "tail_allocations":num,
        "arm_means_N_V_H":armmeans,
        "H_minus_V":float(armmeans[2]-armmeans[1]),
        "both_shared_means_exceed_unrelated":bool(armmeans[1]>armmeans[0] and armmeans[2]>armmeans[0]),
    }


def generate_once(rng, scenario):
    labels = random_labels(rng)
    perbat_baseline = 1.0 + rng.normal(0.0, 0.20, size=N)
    global_block_shift = np.repeat(rng.normal(0,0.05,size=NBLOCKS),3)
    non_specific_bat_gain = rng.normal(0,0.05,size=N)
    baseline = perbat_baseline[:,None] + rng.normal(0,0.10,size=(N,Q_PRE))
    gains = np.asarray(SCENARIO_GAINS[scenario],float)[labels]
    after = (perbat_baseline-global_block_shift-non_specific_bat_gain-gains)[:,None] + rng.normal(0,0.10,size=(N,Q_POST))
    y = np.mean(baseline,axis=1)-np.mean(after,axis=1)
    result=exact_block_test(y,labels)
    result["positive"] = bool(result["T"] > 0 and result["p_exact"] <= 0.05)
    return result,labels,baseline,after


def selftest():
    if PERMS.shape != (6,3) or len({tuple(p) for p in PERMS}) !=6:
        raise AssertionError("3! local permutations wrong")
    if 6**6 != 46656 or 3**6 *2**6 != 46656:
        raise AssertionError("allocation enumeration wrong")
    rng=np.random.default_rng(10077)
    labels=random_labels(rng)
    y=np.asarray([1.1*np.sin(i*0.37)+0.01*i for i in range(N)],float)
    a=exact_block_test(y,labels)
    if a["n_allocations"] != 46656 or a["n_effective_unique_allocations"] != 729:
        raise AssertionError("full label space incorrect")
    # Full enumeration for exactly two blocks: 6^2=36 allocations.
    block0,block1=y[:3],y[3:6]
    brute=[]
    for p1,p2 in product(PERMS, repeat=2):
        l=np.concatenate((p1,p2))
        s=[]
        for k in range(2):
            v=[block0,block1][k]
            lab=l[k*3:k*3+3]
            s.append(0.5*(v[lab==1][0]+v[lab==2][0])-v[lab==0][0])
        brute.append(np.mean(s))
    small_local=np.asarray([0.5*np.sum(t)-1.5*t for t in (block0,block1)])
    orbit=((small_local[0,:,None]+small_local[1,None,:])/2).reshape(-1)
    if not np.allclose(np.sort(brute),np.sort(np.repeat(orbit,4)),rtol=0,atol=1e-13):
        raise AssertionError("2-block 36 enumeration does not match orbit counts")
    if not np.isclose(np.mean(brute),0,atol=1e-12):
        raise AssertionError("null mean nonzero")
    sim,labels2,baseline,after=generate_once(np.random.default_rng(999),"SHARED_MOTOR_MODULE")
    if baseline.shape != (N,2) or after.shape != (N,2):
        raise AssertionError("forced sentinel support drift")
    paired,la,ba,aa=generate_once(np.random.default_rng(999),"SHARED_SENSORY_CUE")
    if sim != paired or not np.array_equal(labels2,la) or not np.array_equal(baseline,ba) or not np.array_equal(after,aa):
        raise AssertionError("paired motor vs sensory generator not observationally equivalent")
    return {
      "three_animal_blocks":6,
      "legal_randomizations":6**6,
      "distinct_primary_statistics_with_multiplicity":3**6,
      "local_paired_label_multiplicity":2**6,
      "two_block_all_36_allocations_match_reduced_orbit":"PASS",
      "sharp_null_mean_zero":"PASS",
      "no_target_route_is_ever_trained":"PASS",
      "motors_vs_cues_paired_identical_raw_observations":"PASS",
    }


def summarize(rows):
    r=np.asarray([d["positive"] for d in rows],int)
    h=np.asarray([d["T"] for d in rows],float)
    n=len(rows)
    p=r.mean()
    arms=np.asarray([list(d["arm_means_N_V_H"].values()) for d in rows],float)
    return {
      "n_synthetic_experiments":n,
      "mean_primary_T":float(h.mean()),
      "sd_primary_T":float(h.std(ddof=1)),
      "detected_count":int(r.sum()),
      "detected_fraction":float(p),
      "monte_carlo_standard_error":float(np.sqrt(p*(1-p)/n)),
      "both_H_and_V_means_exceed_N_fraction":float(np.mean([d["both_shared_means_exceed_unrelated"] for d in rows])),
      "arm_means_N_V_H":arms.mean(axis=0).tolist(),
      "mean_H_minus_V":float(np.mean([d["H_minus_V"] for d in rows])),
      "median_exact_p":float(np.median([d["p_exact"] for d in rows]))
    }


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--self-test", action="store_true")
    pa.add_argument("--out",default="SENTINEL_UNTRAINED_ROUTE_RESULT_V1.json")
    args=pa.parse_args()
    check=selftest()
    if args.self_test:
        print(json.dumps(check,indent=2))
        return
    root=np.random.SeedSequence(ROOT_SEED)
    results={}
    # share a 1000-replicate stream only between motor and perceptual rival models
    groups=("WHOLE_ROUTE_ONLY","GLOBAL_FAMILIARITY","SHARED_MOTOR_MODULE","HORIZONTAL_ONLY_TRANSFER","WEAK_SHARED_MODULE")
    twins_identical=0
    for group,stream in zip(groups,root.spawn(len(groups))):
        rows=[]
        for repseed in stream.spawn(R):
            seed=int(repseed.generate_state(1,dtype=np.uint64)[0])
            obj,l,b,a=generate_once(np.random.default_rng(seed),group)
            rows.append(obj)
            if group=="SHARED_MOTOR_MODULE":
                other,l2,b2,a2=generate_once(np.random.default_rng(seed),"SHARED_SENSORY_CUE")
                if obj!=other or not all(np.array_equal(x,y) for x,y in [(l,l2),(b,b2),(a,a2)]):
                    raise AssertionError("motor / sensory choice outcomes are not identical")
                twins_identical+=1
        results[group]=summarize(rows)
        if group=="SHARED_MOTOR_MODULE":
            results["SHARED_SENSORY_CUE"]=summarize(rows)
        print(group,results[group]["detected_count"],"/",R,"mean_T",round(results[group]["mean_primary_T"],6),flush=True)
    out={
      "status":"SYNTHETIC_DESIGN_STRESS_NOT_BAT_DATA",
      "contract":"SENTINEL_UNTRAINED_ROUTE_CONTRACT_V1.md",
      "seed":ROOT_SEED,"n_new_artificial_animals":N,"number_blocks":NBLOCKS,
      "before_and_after_technical_observations_per_bat":2,
      "training_assignment":"A-R1/R2/R3 (balanced within 3-animal blocks)",
      "sentinel_target":"B-R4, never additionally trained",
      "n_exact_legal_assignments":6**6,
      "n_unique_primary_statistics":3**6,
      "n_repetitions_per_scenario":R,
      "n_perfectly_paired_motor_versus_sensory_datasets":twins_identical,
      "preflight":check,
      "scenarios":{k:results[k] for k in SCENARIO_GAINS},
      "limits":[
        "A rejection is exact against the sharp null that sentinel potential outcomes are invariant to training-route allocation; not automatically against a weak zero-average-transfer null.",
        "The primary transfer contrast cannot separately establish horizontal AND vertical transfer, nor motor rather than sensory reuse.",
        "All effect sizes, measurement errors, practice doses, bat counts and reported detection frequencies are hypothetical. No animal trial is authorized.",
      ]
    }
    Path(args.out).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("SYNTHETIC_SENTINEL_SIMULATION_COMPLETE",flush=True)

if __name__=="__main__":main()
