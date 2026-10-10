#!/usr/bin/env python3
"""POST-OUTCOME EXPLORATORY two-night *binary* co-receiver dyad repeat count.

The original minute co-detection margins 17,14 were viewed before this
supplementary test. No p, causal evidence, GPS, individual identities or new
event selection. Reuse the source/quality parsing and cutoff of V1a unchanged.
"""
from __future__ import annotations
import argparse,json
from itertools import combinations
from pathlib import Path
from preflight_myotis_eight_tag_two_day_v5 import FILE_PAIRS
from myotis_2026_one_minute_same_receiver_descriptive_v1a import (
   DAYS, parse_events, joint_minutes
)
MARGINS={"20240515":17,"20240516":14}
DAY_ORDER=DAYS

def source_test():
    assert len(FILE_PAIRS)==8
    assert set(DAY_ORDER)==set(MARGINS)
    assert 3<=min(MARGINS.values())<=14
    positives_a={1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17}
    positives_b={1,2,3,4,5,6,7,8,9,10,11,12,13,14}
    assert len(positives_a & positives_b)==14
    return "PASS_FIXED_2X2_SUM_AND_SOURCE_ALLOWLIST"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--out",default="MYOTIS_2026_CROSS_NIGHT_DYAD_BINARY_V1B.json")
    args=parser.parse_args()
    guard=source_test()
    if args.self_test:
        print(json.dumps({"self_test":guard,"original_data_opened":False}));return

    series=[p[0] for p in FILE_PAIRS]
    maps={day:{} for day in DAYS}
    reports=[]
    for label,rid15,rid16 in FILE_PAIRS:
        for day,rid in zip(DAYS,(rid15,rid16)):
            report,mapping=parse_events(f"{label}_{day}.csv",rid,day)
            reports.append(report)
            maps[day][label]=mapping
    if any(r.get("status")!="SOURCE_STRUCTURAL_QA_ONLY" for r in reports):
        status="STOP_SOURCE_OR_MARGIN_DRIFT"
        table=None
    else:
        binary={}
        for day in DAYS:
            binary[day]={tuple((a,b)):joint_minutes(maps[day][a],maps[day][b])>0
                for a,b in combinations(series,2)}
        counts={day:sum(binary[day].values()) for day in DAYS}
        if counts!=MARGINS or len(binary[DAYS[0]])!=28:
            status="STOP_SOURCE_OR_MARGIN_DRIFT"
            table=None
        else:
            a,b=DAYS
            both=sum(binary[a][k] and binary[b][k] for k in binary[a])
            onlya=counts[a]-both
            onlyb=counts[b]-both
            neither=28-(both+onlya+onlyb)
            assert 3<=both<=14
            assert min(onlya,onlyb,neither)>=0
            assert both+onlya+onlyb+neither==28
            table={"positive_both_nights":both,
                  "positive_only_20240515":onlya,
                  "positive_only_20240516":onlyb,
                  "positive_neither_night":neither,
                  "total_possible_dyads":28,
                  "source_margins":{"20240515":17,"20240516":14},
                  "jaccard_of_positive_dyad_sets":both/(counts[a]+counts[b]-both)}
            status="EXPLORATORY_BINARY_PAIR_COUSE_REPETITION_DESCRIPTIVE_ONLY"
    result={"status":status,
        "analysis_tier":"POST_OUTCOME_EXPLORATORY_NOT_CONFIRMATORY",
        "contract":"MYOTIS_2026_CROSS_NIGHT_DYAD_PERSISTENCE_EXPLORATORY_LOCK_V1B.md",
        "source":"Original OSF sg6dz, same 16 files as V1a",
        "categorical_dyad_repetition":table,
        "raw_individual_or_receiver_ids_emitted":False,
        "exact_source_times_or_RSSI_or_coordinates_emitted":False,
        "p_values_or_social_null_simulated":False,
        "original_V1a_processing_reused":True,
        "self_test":guard}
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"aggregate_repeat_table":table,
           "no_causal_or_inferential_claim":True},sort_keys=True))
if __name__=="__main__":main()
