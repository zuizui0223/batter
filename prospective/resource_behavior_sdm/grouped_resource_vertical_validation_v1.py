"""Group-heldout conditional vertical-use prediction: source-independent engine.

NOT fitted to original bats in this repository. It accepts *prequalified*
raw-record-only source rows with externally assigned categorical bins and
compares matched denominators under leave-individual / leave-site / leave-night.
No source GPS records or per-animal predictions should be committed to Git.
Source site, individual and night are blocks, not interchangeable IID fixes.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
import math

HEIGHT_CLASSES=("low","middle","high")
ALPHA=0.5
PRIOR_STRENGTH=1.0
CORE=("individual","night","site","time_bin","kinematic_state",
      "height_bin","habitat_class","is_original_fix","is_interpolated")
BASE=("time_bin","kinematic_state")
HABITAT=BASE+("habitat_class",)
FOOD=HABITAT+("food_bin",)


def validate(rows, use_food=False):
    """Fail before opening outcomes from a new source if schema is not pinned."""
    if not isinstance(rows,(list,tuple)) or not rows:
        raise ValueError("STOP_EMPTY_OR_UNMATERIALIZED_SOURCE")
    for r in rows:
        if not isinstance(r,dict) or any(k not in r for k in CORE):
            raise ValueError("STOP_INVALID_FROZEN_SOURCE_SCHEMA")
        if r["is_original_fix"] is not True or r["is_interpolated"] is not False:
            raise ValueError("STOP_NONORIGINAL_OR_INTERPOLATED_FIX")
        if any(not isinstance(r[k],str) or not r[k].strip() for k in CORE[:7]):
            raise ValueError("STOP_MISSING_SOURCE_ID_TIME_STATE_HABITAT")
        if r["height_bin"] not in HEIGHT_CLASSES:
            raise ValueError("STOP_UNFROZEN_OR_MISSING_HEIGHT_CATEGORY")
        if use_food:
            if (not isinstance(r.get("food_bin"),str) or not r["food_bin"].strip()
                or r.get("independent_food_survey") is not True
                or r.get("food_time_matched") is not True):
                raise ValueError("STOP_NO_INDEPENDENT_TIME_MATCHED_FOOD")
    if len({r["individual"] for r in rows})<4:
        raise ValueError("STOP_FEWER_THAN_FOUR_INDEPENDENT_BATS")
    return tuple(dict(r) for r in rows)


def _animal_night_weights(rows):
    bats={r["individual"] for r in rows}
    nights=defaultdict(set)
    counts=Counter()
    for r in rows:
        nights[r["individual"]].add((r["site"],r["night"]))
        counts[(r["individual"],r["site"],r["night"])]+=1
    # Per animal total weight = 1, equal weight per original bat night,
    # equal weight per observed fix within each bat night. Never use 3226
    # video frames as 3226 independent experimental replicates.
    return { (r["individual"],r["site"],r["night"]):
             1.0/(len(nights[r["individual"]])*
                   counts[(r["individual"],r["site"],r["night"])])
             for r in rows }


def _fit(train,features):
    weights=_animal_night_weights(train)
    context=defaultdict(lambda:defaultdict(float))
    totals=defaultdict(float)
    pooled=defaultdict(float)
    for r in train:
        key=tuple(r[k] for k in features)
        z=r["height_bin"]
        w=weights[(r["individual"],r["site"],r["night"])]
        context[key][z]+=w
        totals[key]+=w
        pooled[z]+=w
    n=sum(pooled.values())
    p0={z:(pooled[z]+ALPHA)/(n+len(HEIGHT_CLASSES)*ALPHA)
        for z in HEIGHT_CLASSES}
    return context,totals,p0


def _logscore(model,features,r):
    context,totals,p0=model
    key=tuple(r[k] for k in features)
    seen=key in context
    if seen:
        den=totals[key]+PRIOR_STRENGTH
        p=(context[key].get(r["height_bin"],0.0)+
           PRIOR_STRENGTH*p0[r["height_bin"]])/den
    else:
        p=p0[r["height_bin"]]
    if not (0<p<=1):
        raise ValueError("STOP_NONFINITE_PREDICTIVE_DENSITY")
    return math.log(p),seen


def _fold_value(r,heldout):
    if heldout=="individual":
        return r["individual"]
    if heldout=="site":
        return r["site"]
    if heldout=="night":
        return (r["individual"],r["site"],r["night"])
    raise ValueError("STOP_UNKNOWN_HELDOUT_UNIT")


def score_group_heldout(rows, heldout="individual", use_food=False):
    """Group-balanced held-out height log score; no IID-fix CI or p value.

    An animal never appears in training for heldout='individual', and one
    original study site never appears in training for heldout='site'.
    No model includes animal identifiers as covariates. Any food score is
    categorically blocked if independent, time-matched survey is unverified.
    """
    data=validate(rows,use_food=use_food)
    feats={"kinematic_time":BASE,"add_habitat":HABITAT}
    if use_food:
        feats["add_true_food"]=FOOD
    folds=sorted({_fold_value(r,heldout) for r in data},key=str)
    if len(folds)<2:
        raise ValueError("STOP_TOO_FEW_HELDOUT_GROUPS")
    fold_records=[]
    for group in folds:
        train=[r for r in data if _fold_value(r,heldout)!=group]
        test=[r for r in data if _fold_value(r,heldout)==group]
        if len({r["individual"] for r in train})<3:
            raise ValueError("STOP_TOO_FEW_TRAINING_BATS")
        models={name:_fit(train,fields) for name,fields in feats.items()}
        # Same EXACT test events for baseline, habitat and true-food models.
        by_night=defaultdict(lambda:defaultdict(list))
        seen=Counter()
        attempted=Counter()
        for r in test:
            nk=(r["individual"],r["site"],r["night"])
            for name,features in feats.items():
                value,supported=_logscore(models[name],features,r)
                by_night[nk][name].append(value)
                seen[name]+=int(supported)
                attempted[name]+=1
        by_bat=defaultdict(lambda:defaultdict(list))
        for nk,d in by_night.items():
            for name,vals in d.items():
                by_bat[nk[0]][name].append(math.fsum(vals)/len(vals))
        scores={name:math.fsum(
                   math.fsum(nightly[name])/len(nightly)
                   for nightly in by_bat.values())/len(by_bat)
                for name in feats}
        deltas={"habitat_minus_base":scores["add_habitat"]-scores["kinematic_time"]}
        if use_food:
            deltas["true_food_minus_habitat"]=scores["add_true_food"]-scores["add_habitat"]
        fold_records.append({
            "heldout_block":str(group), # anonymized externally; NEVER archive real bat IDs
            "heldout_bats":len(by_bat),
            "heldout_bat_nights":len(by_night),
            "original_fix_count_for_scoring":len(test),
            "matched_scores_nats_per_observed_fix":scores,
            "heldout_gain_nats_per_fix":deltas,
            "training_context_support_fraction":{
                name:seen[name]/attempted[name] for name in feats},
        })
    overall={}
    for k in fold_records[0]["heldout_gain_nats_per_fix"]:
        overall[k]=math.fsum(x["heldout_gain_nats_per_fix"][k] for x in fold_records)/len(fold_records)
    return {
        "schema":"batter.grouped_conditional_height_source_eval.v1",
        "status":"DESCRIPTIVE_HELDOUT_SCORE_NOT_CAUSAL",
        "heldout_unit":heldout,"n_folds":len(fold_records),
        "n_unique_bats":len({r["individual"] for r in data}),
        "source_row_count":len(data),
        "fixes_are_independent_replicates":False,
        "food_channel_is_directly_measured_and_time_matched":bool(use_food),
        "source_group_scores":fold_records,
        "equal_heldout_group_mean_gain":overall,
        "scientific_boundary":"No absolute AGL, food causality or species SDM from this code; external source/height-datum/effort gates required."
    }
