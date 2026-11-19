#!/usr/bin/env python3
"""H1 aggregate-only contrast audit and a known-truth change-score negative control.

All reported coefficients/RRs belong to original publications; no new independent
animal data are used. The synthetic data have NO social cue or competition effect.
"""
import argparse
import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def readcsv(filename):
    with (ROOT/filename).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def slope(x,y):
    mx=sum(x)/len(x);my=sum(y)/len(y)
    denom=sum((v-mx)**2 for v in x)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/denom

def group_centered_slope(groups):
    x=[];delta=[]
    for pre,during in groups:
        mx=sum(pre)/len(pre);md=sum(during)/len(during)
        x.extend(v-mx for v in pre)
        delta.extend((b-a)-(md-mx) for a,b in zip(pre,during))
    return sum(a*b for a,b in zip(x,delta))/sum(a*a for a in x)

def simulate_stationary_null(rho, seed, n_sites=12, n_blocks=30):
    rng=random.Random(seed)
    groups=[]
    for site in range(n_sites):
        mean=20.0+site*0.2
        pre=[rng.gauss(mean,3.0) for _ in range(n_blocks)]
        during=[mean+rho*(v-mean)+math.sqrt(1.0-rho*rho)*rng.gauss(0,3.0) for v in pre]
        groups.append((pre,during))
    return group_centered_slope(groups)

def main_audit():
    year2019=readcsv("PUBLISHED_LEWANZIK_2019_DENSITY_V1.csv")
    year2026=readcsv("PUBLISHED_GLOSSOPHAGA_CONTRASTS_V1.csv")
    assert len(year2019)==4, "Expected four original receiver taxon/group coefficients"
    assert len(year2026)==8, "Expected published four signal conditions x two sexes"
    assert len({r["study_id"] for r in year2019})==1
    assert len({r["study_id"] for r in year2026})==1
    assert len({r["response_taxon_or_group"] for r in year2019})==4
    assert sum(r["taxon_resolution"]=="species" for r in year2019)==3
    assert all(float(r["cri95_upper"])<0 for r in year2019)

    by_signal=defaultdict(dict)
    for r in year2026:
        assert float(r["playback_vs_silent_ratio"])>0
        k=r["signal"];sex=r["sex"]
        assert sex not in by_signal[k]
        by_signal[k][sex]=r
    assert set(by_signal)=={"alert","benign","noise_for_alert","noise_for_benign"}
    estimates=[]
    for signal in ["alert","benign","noise_for_alert","noise_for_benign"]:
        rows=by_signal[signal]
        assert set(rows)=={"male","female"}
        male=float(rows["male"]["playback_vs_silent_ratio"])
        female=float(rows["female"]["playback_vs_silent_ratio"])
        beta_m=math.log(male);beta_f=math.log(female)
        z_m=float(rows["male"]["reported_z"]);z_f=float(rows["female"]["reported_z"])
        se_m=abs(beta_m/z_m); se_f=abs(beta_f/z_f)
        ratio=female/male
        beta=math.log(ratio)
        # This is approximate, reconstructed from rounded summary statistics and
        # independence across male/female (not across treatments). Descriptive only.
        approx_se=math.hypot(se_f,se_m)
        estimates.append({
            "signal":signal,"male_playback_silent_rr":male,
            "female_playback_silent_rr":female,
            "female_vs_male_ratio_of_rate_ratios":round(ratio,5),
            "approx_wald_95_ci_if_sex_contrasts_independent":[round(math.exp(beta-1.96*approx_se),5),round(math.exp(beta+1.96*approx_se),5)],
            "caveat":"summary-based descriptive; no sex-by-signal factorial p, no raw-animal re-fit"
        })

    simulations=[]
    for rho in [0.0,0.5,0.9]:
        values=[simulate_stationary_null(rho,seed=27011+i) for i in range(128)]
        expected=rho-1.0
        avg=sum(values)/len(values)
        simulations.append({
            "stationary_pre_during_correlation":rho,
            "true_social_effect":0,
            "theoretical_delta_on_pre_slope":round(expected,5),
            "mean_within_site_slope_from_128_simulations":round(avg,5),
            "number_of_negative_slopes":sum(x<0 for x in values),
            "n_simulated_sites":12,"n_blocks_per_site":30,
            "note":"known-truth illustration of mathematical coupling; NOT empirical bat inference",
        })
    result={
      "status":"published_aggregate_audit_and_synthetic_null_only",
      "meta_analytic_eligibility":"STOP: distinct outcomes and no independent matched study-level cue effects",
      "published_2019":{
        "independent_studies":1,"recipient_units":4,
        "recipient_species":3,"pooled_recipient_groups":1,
        "all_four_baseline_coefficients_have_negative_reported_95cri":True,
        "causal_competition_interpretation":"NOT_IDENTIFIED_FROM_CHANGE_SCORE_BASELINE_REGRESSION",
        "reference":"https://doi.org/10.1111/1365-2656.12989"
      },
      "published_2026":{
        "independent_studies":1,"original_n_bats":16,"n_male":8,"n_female":8,
        "rate_ratio_contrasts":estimates,
        "reference":"https://doi.org/10.1111/nyas.70427"
      },
      "known_truth_null":{
        "model":"Y_pre=mu+epsilon0; Y_during=mu+rho*epsilon0+sqrt(1-rho^2)*epsilon1; no effect of cues or conspecific competition",
        "analytic_identity":"slope((Y_during-Y_pre)~Y_pre)=Corr(Y_during,Y_pre)*SD(Y_during)/SD(Y_pre)-1; stationary equal-variance case=rho-1",
        "simulations":simulations
      },
      "interpretation":"mechanically negative change-score baseline association does not prove no social effect or invalidate buzz-rate effects; identify cue-by-density moderation with randomized matched controls",
    }
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output", type=Path,default=None)
    args=ap.parse_args()
    result=main_audit()
    serialized=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(serialized,encoding="utf-8")
    print(serialized,end="")
