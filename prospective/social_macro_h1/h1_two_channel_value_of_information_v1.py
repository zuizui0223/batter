#!/usr/bin/env python3
"""H1 prospective two-channel value-of-information model (pure Python).

This is a decision-theory *counterexample* to the universal negative
social-information versus private-memory tradeoff, not a bat fit or a claim
of first invention. Spatially located patch, unpredictable temporal state,
social availability cue, and irreversible travel cost.

Rousettus 2024: DOI 10.1098/rstb.2024.0060 (source motivation, not model fit)
Kohles et al. 2022: DOI 10.1111/brv.12881 (social strategy prior art).
"""
import argparse
import json
from pathlib import Path

PARAMS={
 "prior_resource_available":0.40,
 "cue_true_positive_sensitivity":0.85,
 "cue_false_positive_rate":0.15,
 "reward_when_food_and_location_correct":10.0,
 "travel_cost_per_visit":3.0,
 "cue_acquisition_cost":0.10,
}
def check(x):
    p=x["prior_resource_available"];a=x["cue_true_positive_sensitivity"]
    b=x["cue_false_positive_rate"];r=x["reward_when_food_and_location_correct"]
    c=x["travel_cost_per_visit"];k=x["cue_acquisition_cost"]
    if not (0<p<1 and 0<b<a<1 and r>0 and c>0 and k>=0):
        raise ValueError("Invalid informative cue/utility parameter range")
    return p,a,b,r,c,k

def posterior(x):
    p,a,b,r,c,k=check(x)
    q=p*a+(1-p)*b
    plus=p*a/q
    minus=p*(1-a)/(1-q)
    assert 0<=minus<p<plus<=1
    return {"P(cue_positive)":q,"P(available_given_positive)":plus,
            "P(available_given_negative)":minus,
            "prior_available":p}

def value(x,m):
    if not (0<=m<=1):raise ValueError("Memory m outside [0,1]")
    p,a,b,reward,travel,cue_cost=check(x)
    z=posterior(x);q=z["P(cue_positive)"]
    pos=z["P(available_given_positive)"];neg=z["P(available_given_negative)"]
    # If bat visits, a failed location memory gives reward 0 but travel cost is paid.
    u0=m*p*reward-travel
    up=m*pos*reward-travel
    un=m*neg*reward-travel
    base=max(0.0,u0)
    with_cue=q*max(0.0,up)+(1-q)*max(0.0,un)
    voi=with_cue-base
    net=voi-cue_cost
    return {"m":m,"baseline_optimal_visit":u0>0,
            "visit_after_positive_cue":up>0,"visit_after_negative_cue":un>0,
            "without_cue_optimal_value":base,
            "gross_value_of_information":voi,
            "net_value_if_cue_purchased":net,
            "would_purchase_cue":net>0}

def piecewise_thresholds(x):
    p,a,b,reward,travel,k=check(x)
    z=posterior(x)
    return {
        "positive_cue_visit":travel/(reward*z["P(available_given_positive)"]),
        "baseline_visit":travel/(reward*p),
        "negative_cue_visit":travel/(reward*z["P(available_given_negative)"]),
        "none_to_positive_cue_slope":a*p*reward,
        "baseline_visits_but_negative_cue_skips_slope":(a-1)*p*reward,
    }
def run(x=None):
    if x is None:x=PARAMS.copy()
    th=piecewise_thresholds(x)
    q=posterior(x)
    path=[value(x,i/1000) for i in range(1001)]
    peak=max(path,key=lambda z:z["net_value_if_cue_purchased"])
    sampled=[value(x,v) for v in (0,0.25,0.38,0.4,0.5,0.6,0.75,0.85,1)]
    assert th["positive_cue_visit"] < th["baseline_visit"] < 1 < th["negative_cue_visit"],(
        "Numerical demonstration thresholds require designated example params"
    )
    assert th["none_to_positive_cue_slope"]>0
    assert th["baseline_visits_but_negative_cue_skips_slope"]<0
    assert abs(peak["m"]-th["baseline_visit"])<.002
    return {
      "evidence_status":"THEORETICAL_ILLUSTRATION_NOT_EMPIRICAL_BAT_FIT",
      "study_question":"Can spatial private memory and a social timing cue be complements and substitutes in different regimes?",
      "source_motivations":[
        "Rousettus fruit timing social odors + personal spatial memory, DOI 10.1098/rstb.2024.0060",
        "Bats social foraging cue strategies prior art, DOI 10.1111/brv.12881"
      ],
      "parameters":x,"cue_posteriors":q,"switch_points":th,
      "maximum_net_information_value_in_0_to_1":peak,
      "selected_memory_values":sampled,
      "scientific_conclusion":{
        "universal_negative_private_social_relationship":"MATHEMATICALLY_UNJUSTIFIED",
        "social_timing_cue":"MEMORY_COMPLEMENT_WHEN_POSITIVE_CUE_ALONE_TRIGGERS_VISIT",
        "social_timing_after_baseline_visit":"MARGINAL_INFORMATION_VALUE_DECREASES_WITH_MEMORY",
        "global_species_effect_estimated":False,
        "real_bat_memory_m_measured":False,
        "novelty_claim":"NONE: standard value-of-information reasoning, applied as H1 falsifiable model"
      },
      "next_measurements_required":[
        "independent spatial location memory or patch revisit accuracy",
        "resource availability prior and temporal predictability",
        "cue sensitivity and false-positive rate measured separately from response",
        "travel reward/cost and randomized cue with suitable control",
        "independent species/population holdout without inferring cognition from diet"
      ]
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=None)
    args=parser.parse_args()
    out=run()
    result=json.dumps(out,indent=2,ensure_ascii=False)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(result,encoding="utf-8")
    print(result,end="")

if __name__=="__main__":
    main()
