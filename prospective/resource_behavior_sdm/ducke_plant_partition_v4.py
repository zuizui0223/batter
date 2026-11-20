"""Ducke source-open v4: equal-model-complexity plant-label negative control.

SOURCE-FREE tests are safe. To run original data, pass the authorized
publisher-Dryad ZIP through ducke_original_adapter_v1 (artifact_tool).
Never commit source plot rows, coordinates, bat identifiers or per-genus
plot vectors. Results are exploratory single-study diagnostic ranks,
NOT causal plant-guild selection, species SDM or observed 5-D bat flight.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date
import argparse, json, math, random
from pathlib import Path

from ducke_original_adapter_v1 import (
    FOOD12,START,END,canon_site,parse_source_date,
    parse_original_zip,build_matched_source,
)
from ducke_joint_guild_composition_v3 import (
    BASE,fit_predict,score,
)

ALL_LABELS_N=22
NAMED_GENERA_N=21
UNKNOWN="Not_identified"
N_DRAW=199
SEEDS={"unrestricted":202611201,"abundance_stratified":202611202}
OBSERVED_PREVIOUS_SPLIT_MINUS_TOTAL=0.026106662918648254
PASS="POST_OUTCOME_SOURCE_LOCAL_PARTITION_LABEL_DIAGNOSTIC"


def original_matched_genus_plots(tables,qualified_plots):
    """Original sample dates and *independent* source plant survey counts.

    Only plot×date with original bat capture and original fruit-survey record
    in source paper sampling months. A missing fruit survey is NEVER a zero.
    Values retained privately only.
    """
    plotted={r["plot"] for r in qualified_plots}
    valid_captures=set()
    for r in tables["Bats_Ducke"]:
        if r["Species"]=="Night_without_capture":
            continue
        d=parse_source_date(r["Date_MM_DD_YYYY"])
        if START<=d<=END:
            valid_captures.add((canon_site(r["Plots"]),d))
    source_fruits=defaultdict(lambda:defaultdict(float))
    category_totals=Counter()
    original_fruit_days=set()
    source_categories=set()
    for r in tables["Fruits"]:
        site=canon_site(r["Plots"])
        d=parse_source_date(r["Date_MM_DD_YYYY"])
        label=r["Genus"]
        source_categories.add(label)
        amount=r["Amount"]
        if type(amount) not in (int,float) or not math.isfinite(amount) or amount<0:
            raise ValueError("STOP_BAD_ORIGINAL_FRUIT_AMOUNT")
        if (site,d) not in valid_captures:
            continue
        original_fruit_days.add((site,d))
        source_fruits[(site,d)][label]+=float(amount)
        category_totals[label]+=amount
    dates_by_site=defaultdict(list)
    for site,day in original_fruit_days:
        if site in plotted:
            dates_by_site[site].append(day)
    if len(original_fruit_days)!=103 or len(dates_by_site)!=46 or sum(len(x) for x in dates_by_site.values())!=103:
        raise ValueError("STOP_ORIGINAL_PLOT_NIGHT_RESOURCE_GRAIN")
    names=sorted(source_categories)
    if len(names)!=ALL_LABELS_N or len([x for x in names if x!=UNKNOWN])!=NAMED_GENERA_N:
        raise ValueError("STOP_SOURCE_PLANT_LABEL_SET_CHANGED")
    if len(FOOD12)!=12 or not FOOD12.issubset(names):
        raise ValueError("STOP_PUBLISHED_FOOD_LABEL_SET_CHANGED")
    if sum(category_totals.values())!=661 or category_totals[UNKNOWN]!=52:
        raise ValueError("STOP_ORIGINAL_GENUS_ABUNDANCE_DRIFT")
    local=[]
    for row in qualified_plots:
        site=row["plot"]
        times=dates_by_site[site]
        avg={name:sum(source_fruits[(site,d)].get(name,0) for d in times)/len(times)
             for name in names}
        if not (math.isclose(sum(avg.values()),row["fruit_all"],abs_tol=1e-10) and
                math.isclose(sum(avg[g] for g in FOOD12),row["fruit_batfood_12"],abs_tol=1e-10) and
                math.isclose(sum(avg[g] for g in names if g not in FOOD12),row["fruit_other"],abs_tol=1e-10)):
            raise ValueError("STOP_SOURCE_MEASURED_RESOURCE_REPLAY_DISAGREEMENT")
        local.append(dict(row, source_fruit_by_category=avg))
    return local,dict(category_totals)


def materialize_partition(private_plots,partition,names,named_only=False):
    """Source-level two axes use exactly same model and response support."""
    selected=frozenset(partition)
    if len(selected)!=12 or not selected.issubset(names):
        raise ValueError("STOP_WRONG_12_OF_22_PARTITION")
    remaining=set(names)-selected
    if named_only:
        if UNKNOWN in selected:
            raise ValueError("STOP_UNIDENTIFIED_ASSIGNED_TO_PUBLISHED_FOOD")
        remaining.remove(UNKNOWN)
    rows=[]
    for r in private_plots:
        source=r.get("source_fruit_by_category")
        if not isinstance(source,dict) or set(source)!=set(names):
            raise ValueError("STOP_MISSING_22_SOURCE_CATEGORIES_PER_PLOT")
        if any(type(z) not in (int,float) or z<0 or not math.isfinite(z)
               for z in source.values()):
            raise ValueError("STOP_NEGATIVE_OR_NONFINITE_SOURCE_FRUIT")
        # These particular keys are the exact publication v3 model variables.
        new=dict(r,
                 fruit_batfood_12=float(sum(source[x] for x in selected)),
                 fruit_other=float(sum(source[x] for x in remaining)))
        new["fruit_all"]=new["fruit_batfood_12"]+new["fruit_other"]
        # Per-site 22-category vectors may ONLY live in original private RAM.
        new.pop("source_fruit_by_category")
        rows.append(new)
    return rows


def split_logscore(rows,excluded_PO=False, features=BASE+("fruit_batfood_12","fruit_other")):
    original=[r for r in rows if r["block"]!="PO"] if excluded_PO else rows
    groups=sorted(set(r["block"] for r in original))
    if len(groups)!=(6 if excluded_PO else 7):
        raise ValueError("STOP_SOURCE_BLOCK_GRANULARITY_CHANGED")
    scores=[]
    for g in groups:
        training=[r for r in original if r["block"]!=g]
        test=[r for r in original if r["block"]==g]
        if len(training)<20 or len(test)==0:
            raise ValueError("STOP_MISSING_HELDOUT_SUPPORT")
        scores.append(score(test,fit_predict(training,test,features)))
    return math.fsum(scores)/len(scores)


def abundance_quartiles(names,source_count):
    if len(names)!=22 or set(source_count)!=set(names):
        raise ValueError("STOP_INVALID_SOURCE_ABUNDANCE_FAMILY")
    ordered=sorted(names,key=lambda x:(source_count[x],x))
    sizes=(6,6,5,5)
    offset=0
    quartiles=[]
    for n in sizes:
        quartiles.append(tuple(ordered[offset:offset+n]))
        offset+=n
    return tuple(quartiles)


def draw_partitions(names,food12,source_counts,mode,n=N_DRAW,seed=None):
    if len(names)!=22 or len(set(names))!=22 or len(food12)!=12:
        raise ValueError("STOP_BAD_FROZEN_LABEL_UNIVERSE")
    if not set(food12).issubset(names):
        raise ValueError("STOP_BAD_FOOD_LABELS")
    if mode not in SEEDS or n!=N_DRAW:
        raise ValueError("STOP_UNKNOWN_NULL_OR_REPETITION_COUNT")
    r=random.Random(SEEDS[mode] if seed is None else seed)
    blocks=abundance_quartiles(names,source_counts)
    observed=[len(set(q)&set(food12)) for q in blocks]
    for i in range(n):
        if mode=="unrestricted":
            pick=frozenset(r.sample(sorted(names),12))
        else:
            pick=frozenset(label for q,k in zip(blocks,observed) for label in r.sample(list(q),k))
        assert len(pick)==12
        yield pick


def null_stats(scores,observed,reference):
    if len(scores)!=N_DRAW:
        raise ValueError("STOP_MISSING_FROZEN_RANDOM_DRAWS")
    x=sorted(scores)
    atleast=sum(v>=observed-1e-11 for v in x)
    def percentile(q):
        # Match frozen v4 NumPy default linear sample-quantile convention
        # with only the Python standard library.
        pos=(len(x)-1)*q
        lower=int(pos)
        upper=min(lower+1,len(x)-1)
        fraction=pos-lower
        return (1-fraction)*x[lower]+fraction*x[upper]
    return {
       "n_draws":len(x),
       "n_at_least_observed":atleast,
       "exploratory_plus_one_tail_fraction":(1+atleast)/(N_DRAW+1),
       "null_mean_minus_total":math.fsum(x)/len(x)-reference,
       "null_quantile_05_minus_total":percentile(.05)-reference,
       "null_median_minus_total":x[len(x)//2]-reference,
       "null_quantile_95_minus_total":percentile(.95)-reference,
       "observed_minus_null_mean":observed-math.fsum(x)/len(x),
       "not_confirmatory_p_value":True,
    }


def run(original_tables,source_plots):
    if len(source_plots)!=46 or sum(r["captures"] for r in source_plots)!=810:
        raise ValueError("STOP_DUCKE_SOURCE_INPUT_DRIFT")
    private, counts=original_matched_genus_plots(original_tables,source_plots)
    labels=sorted(counts)
    observed_rows=materialize_partition(private,FOOD12,labels)
    actual=split_logscore(observed_rows)
    baseline=split_logscore(observed_rows,features=BASE)
    pooled=split_logscore(observed_rows,features=BASE+("fruit_all",))
    observed_gain=actual-pooled
    if not math.isclose(observed_gain,OBSERVED_PREVIOUS_SPLIT_MINUS_TOTAL,rel_tol=0,abs_tol=1e-7):
        raise ValueError("STOP_V3_SOURCE_OUTCOME_REPLAY_MISMATCH")
    output={}
    for mode in SEEDS:
        scores=[]
        seen=set()
        for labels12 in draw_partitions(labels,FOOD12,counts,mode):
            scores.append(split_logscore(materialize_partition(private,labels12,labels)))
            seen.add(tuple(sorted(labels12)))
        output[mode]=dict(null_stats(scores,actual,pooled),n_unique_partitions=len(seen))
    named=materialize_partition(private,FOOD12,labels,named_only=True)
    named_pooled=split_logscore(named,features=BASE+("fruit_all",))
    named_split=split_logscore(named)
    l_only_split=split_logscore(observed_rows,excluded_PO=True)
    l_only_total=split_logscore(observed_rows,excluded_PO=True,features=BASE+("fruit_all",))
    l_only_base=split_logscore(observed_rows,excluded_PO=True,features=BASE)
    return {
      "schema":"batter.ducke.equal_complexity_plant_partition_v4",
      "status":"SOURCE_OPEN_EXPLORATORY_PARTITION_FALSIFICATION",
      "source_doi":"10.5061/dryad.9rb48c5",
      "freeze_design":"DUCKE_EQUAL_COMPLEXITY_PLANT_PARTITION_V4_FROZEN.md",
      "n_matched_plots":46,"n_matched_plot_nights":103,"n_original_plant_source_categories":22,
      "n_named_genera":21,"n_original_source_fruit_units":661,
      "n_unidentified_fruit_units":52,
      "n_candidate_food_genera":12,"n_remaining_source_categories":10,
      "original_split_minus_baseline":actual-baseline,
      "original_split_minus_total":observed_gain,
      "unrestricted":output["unrestricted"],
      "abundance_stratified":output["abundance_stratified"],
      "abundance_quartile_food_group_counts":[len(set(q)&FOOD12) for q in abundance_quartiles(labels,counts)],
      "exclude_unknown_named_only_12_vs_9":{
        "n_named_genera":21,
        "split_minus_named_total":named_split-named_pooled,
      },
      "six_L3_L8_no_PO":{
        "n_source_plots":29,
        "split_minus_baseline":l_only_split-l_only_base,
        "split_minus_total":l_only_split-l_only_total,
      },
      "source_original_site_or_bat_rows_stored":False,
      "independent_external_validation":False,
      "diet_genera_are_causal_resource_choice":False,
      "source_specific_GPS_3D_height_effect":None,
      "frozen_original_published_results_modified":False
    }


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source-zip",required=True)
    a.add_argument("--aggregate-out",required=True)
    args=a.parse_args()
    tables=parse_original_zip(args.source_zip)
    plots,qc=build_matched_source(tables)
    result=run(tables,plots)
    Path(args.aggregate_out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("DUCKE_V4",result["status"],
          "UNRESTRICTED_RANDOM_TAIL",result["unrestricted"]["exploratory_plus_one_tail_fraction"],
          "ABUNDANCE_MATCHED_RANDOM_TAIL",result["abundance_stratified"]["exploratory_plus_one_tail_fraction"])


if __name__=="__main__":
    main()
