"""PLOS 2016 source-structure-compatible counterexample: target confounding.

PURE KNOWN TRUTH: no real PLOS XYZ value used.
Shows a population-level target-height statistical association from bat
composition alone despite zero within-bat and zero intervention effect.
Do not report as an observed ecological target response.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import json
import math

# One deliberately constructed source-compatible allocation.
# Five bats, 2 targets, 15 sequences/target, 30 sequences total, 8
# bat×target pairs, bat totals [3,3,8,8,8], 5 cells of size 3 + 3 of 5.
# Each bat always chooses the same Z state whatever target; no target effect.
CONSTRUCTED_DESIGN=(
    ("bat_a","flower",3,"low"),
    ("bat_b","flower",3,"low"),
    ("bat_c","flower",3,"high"),
    ("bat_c","hemisphere",5,"high"),
    ("bat_d","flower",3,"high"),
    ("bat_d","hemisphere",5,"high"),
    ("bat_e","flower",3,"high"),
    ("bat_e","hemisphere",5,"high"),
)


def observational_mutual_information(rows):
    totals=Counter()
    by_target=Counter()
    by_height=Counter()
    n=0
    for bat,target,k,height in rows:
        if not isinstance(k,int) or k<=0:
            raise ValueError("invalid trial count")
        totals[(target,height)]+=k
        by_target[target]+=k
        by_height[height]+=k
        n+=k
    if n==0:
        raise ValueError("empty synthetic design")
    info=0.
    for (t,h),count in totals.items():
        info+=count/n*math.log(count*n/(by_target[t]*by_height[h]))
    return info


def info_given_animal(rows):
    bats=defaultdict(list)
    n=sum(k for _,_,k,_ in rows)
    for bat,t,k,h in rows:
        bats[bat].append((bat,t,k,h))
    # Conditional MI is the probability-weighted per-bat MI.
    return math.fsum(
        sum(k for _,_,k,_ in cohort)/n*observational_mutual_information(cohort)
        for cohort in bats.values()
    )


def calculate_counterexample():
    rows=CONSTRUCTED_DESIGN
    bat_totals=Counter()
    per_target=Counter()
    pairs=Counter()
    for b,t,n,z in rows:
        bat_totals[b]+=n
        per_target[t]+=n
        pairs[(b,t)]+=n
    if sorted(bat_totals.values()) != [3,3,8,8,8]:
        raise AssertionError("wrong published-source-compatible bat totals")
    if sorted(per_target.values()) != [15,15] or len(pairs)!=8:
        raise AssertionError("wrong source structural target margins")
    if Counter(pairs.values())!=Counter({3:5,5:3}):
        raise AssertionError("wrong bat×target trial-count shape")
    info=observational_mutual_information(rows)
    conditional=info_given_animal(rows)
    if abs(info-0.1638965900335596)>1e-12 or abs(conditional)>1e-12:
        raise AssertionError("known-truth counterexample drift")
    matched={bat for bat,tar,n,h in rows if tar=="hemisphere"}
    return {
        "schema":"batter.plos_source_compatible_target_confounding.v1",
        "status":"SYNTHETIC_COUNTEREXAMPLE_VERIFIED",
        "source_structural_input":"PLOS2016 structural-only source gate: five bats, 15/15 target, 30 trials; eight bat×target pairs with counts 3 or 5",
        "constructed_no_real_biology_rows":True,
        "constructed_target_trial_counts_sorted":sorted(per_target.values()),
        "constructed_bat_trial_counts_sorted":sorted(bat_totals.values()),
        "constructed_bat_target_pair_count":len(pairs),
        "constructed_pairs_by_trial_count":dict(sorted(Counter(pairs.values()).items())),
        "target_height_marginal_information_nats":info,
        "target_height_information_conditioned_on_bat_nats":conditional,
        "true_target_effect_on_height_by_construction":0.,
        "number_of_source_structurally_both_target_bats":len(matched),
        "best_possible_one_sided_signflip_p_for_three_bats":1/2**len(matched),
        "real_PLOS_target_height_coefficient":None,
        "real_resource_availability_SDМ_coefficient":None,
        "source_original_raw_data_opened":False,
    }


if __name__=="__main__":
    print(json.dumps(calculate_counterexample(),ensure_ascii=False,indent=2))
