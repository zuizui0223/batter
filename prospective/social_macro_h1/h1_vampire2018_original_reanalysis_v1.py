#!/usr/bin/env python3
"""Vrtilek et al. 2018 Figshare original trial-accurate maze learning audit.

Only aggregate animal-by-phase outcomes leave the GitHub runner. Prior art!
Physical bat IDs and raw original rows never committed or archived.
Data DOI 10.6084/m9.figshare.6466022.v2 (original file 12183227).
"""
from collections import Counter,defaultdict
import csv,hashlib,io,json,os,urllib.request
from pathlib import Path
OUT=Path(os.getenv("H1_VAMPIRE2018_ORIGINAL_RESULT","/tmp/h1_vampire2018_derived_only.json"))
URL="https://ndownloader.figshare.com/files/12183227"
EXPECTED_MD5="935d61487756bd62837b9a53cc5f11f8"
EXPECTED_SHA="49e5e2a24ee7e0cb69f2c1df64ddc2c2c0964be39a1d2e5fc1cc9d06d7b5c128"
FIELDS=["experiment","trial ","bat","demonstrator","phase","attempt","latency","latency2","exit.in.15","naive"]

def read_original():
    req=urllib.request.Request(URL,headers={"User-Agent":"Vampire2018BatPublishedOriginalSourceCheck/1.0"})
    with urllib.request.urlopen(req,timeout=30) as r: buf=r.read(20000)
    if (len(buf),hashlib.md5(buf).hexdigest(),hashlib.sha256(buf).hexdigest())!=(
        6615,EXPECTED_MD5,EXPECTED_SHA):
        raise ValueError("Original 2018 Figshare file bytes mismatch")
    rd=csv.DictReader(io.StringIO(buf.decode("utf-8-sig"),newline=""))
    if rd.fieldnames!=FIELDS:raise ValueError("Unexpected original header")
    rows=list(rd)
    if len(rows)!=188:raise ValueError("Original 188-record dataset changed")
    return rows,buf

def clean_outcome(raw):
    val=str(raw).strip()
    if val in ("T","TRUE","true","1"):return True
    if val in ("F","FALSE","false","0"):return False
    if val in ("","NA","NaN","na","N/A"):return None
    raise ValueError("Unknown original exit.in.15 coding: "+val[:30])

def aggregate():
    rows,buf=read_original()
    byphase=defaultdict(list)
    bysubject=defaultdict(dict)
    trainings=[]
    for r in rows:
        if r["experiment"]=="train":
            if r["phase"]!="train" or r["demonstrator"]!="T":raise ValueError("Training role mismatch")
            trainings.append(r)
            continue
        if r["experiment"]!="test":raise ValueError("Unexpected original experiment")
        if r["phase"] not in ("1pre","2test","3post"):raise ValueError("Unexpected original test phase")
        outcome=clean_outcome(r["exit.in.15"])
        stage=r["phase"]
        if r["demonstrator"]=="F":
            subject=r["bat"]
            if stage in bysubject[subject]:raise ValueError("Duplicate naive subject × stage")
            bysubject[subject][stage]=outcome
            byphase[stage].append({"bat":subject,"outcome":outcome,"trial":r["trial "]})
        elif r["demonstrator"]!="T" or stage!="2test":
            raise ValueError("Trained demonstrator included outside 2test")
    if len(trainings)!=104 or len({x["bat"] for x in trainings})!=12:
        raise ValueError("Original demonstrator train grain changed")
    if len(bysubject)!=24:
        raise ValueError("Original 24 naive bats absent")
    if {x:len(byphase[x]) for x in ("1pre","2test","3post")} != {"1pre":24,"2test":24,"3post":24}:
        raise ValueError("Naive phase counts changed; not inferring missing subjects")
    design={}
    for stage in ("1pre","2test","3post"):
        obs=[x["outcome"] for x in byphase[stage]]
        design[stage]={"raw_naive_rows":len(obs),
                       "valid_exit_binary_n":sum(x is not None for x in obs),
                       "exit_in_15_yes":sum(x is True for x in obs),
                       "exit_in_15_no":sum(x is False for x in obs),
                       "outcome_missing_n":sum(x is None for x in obs),
                       "n_unique_physical_triads_by_trial":len({x["trial"] for x in byphase[stage]})}
    transitions=[]
    statuses={}
    for bat,vals in bysubject.items():
        if set(vals)!={"1pre","2test","3post"}:raise ValueError("Naive bat missing one of three phase rows")
        pre=vals["1pre"];during=vals["2test"];post=vals["3post"]
        if pre is not None and post is not None:
            transitions.append((pre,post))
        statuses.setdefault("all_pairs",[]).append((pre,during,post))
    valid_during=[x for x in statuses["all_pairs"] if x[1] is not None]
    during_winners=[x for x in statuses["all_pairs"] if x[1] is True]
    during_winner_with_post=[x for x in during_winners if x[2] is not None]
    conditional_post_n=sum(x[2] is True for x in during_winner_with_post)
    table=Counter(f"{'T' if a else 'F'}->{'T' if b else 'F'}" for a,b in transitions)
    table_all={f"{a}->{b}":table.get(f"{a}->{b}",0) for a in ("F","T") for b in ("F","T")}
    out={
      "status":"ORIGINAL_2018_MAZE_REANALYSIS_OF_PUBLISHED_BEHAVIOR",
      "paper_doi":"10.1098/rsos.172483",
      "public_original_figshare":"10.6084/m9.figshare.6466022.v2",
      "original_csv_url":URL,"original_sha256":EXPECTED_SHA,"original_md5":EXPECTED_MD5,
      "original_n_rows":188,"n_training_demonstrator_bats":12,"n_training_rows":104,
      "naive_bat_count":24,
      "phase_naive_records":design,
      "matched_pre_to_post_binary_n":len(transitions),
      "individual_pre_post_transition_table":table_all,
      "during_exit_positive_naive_n":len(during_winners),
      "during_exit_valid_naive_n":len(valid_during),
      "during_exit_positive_with_post_binary_n":len(during_winner_with_post),
      "after_demonstrator_retention_positive_n":conditional_post_n,
      "after_demonstrator_retention_fraction":(
            conditional_post_n/len(during_winner_with_post) if during_winner_with_post else None),
      "published_pre_0_24_consistent":design["1pre"]["exit_in_15_yes"]==0 and design["1pre"]["valid_exit_binary_n"]==24,
      "published_during_5_23_consistent":design["2test"]["exit_in_15_yes"]==5 and design["2test"]["valid_exit_binary_n"]==23,
      "published_four_of_five_retained_consistent":conditional_post_n==4 and len(during_winner_with_post)==5,
      "claim_boundary":{
         "individual_trial_rows_committed":False,
         "conditional_retention_not_causal_treatment_effect":True,
         "pre_vs_during_not_randomized_exposure_order":True,
         "triad_exposures_independent":False,
         "full_original_naive_subjects_included_before_selection":True,
         "resource_food_availability_or_cue_posterior_measured":False,
         "external_cross_species_validation_provided":False,
         "original_2018_discovery_already_published":True
      }
    }
    return out

if __name__=="__main__":
    result=aggregate()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
