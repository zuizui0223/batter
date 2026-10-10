#!/usr/bin/env python3
"""Exploratory V2: same 8 bats, same 2 nights, ONE central 23:00–02:00 bin restriction.

All-night margins V1a=17/14 and both-night recurrence V1b=13 are known already:
this is deliberately POST-OUTCOME and never yields social inference or p-values.
No names of bat RFID, receivers, coordinates or exact clock values leave memory.
"""
from __future__ import annotations
import argparse
from itertools import combinations
import json
from pathlib import Path
from preflight_myotis_eight_tag_two_day_v5 import FILE_PAIRS
from myotis_2026_one_minute_same_receiver_descriptive_v1a import (
    DAYS,parse_events,joint_minutes,q
)

FROZEN_NIGHT_MARGINS={"20240515":17,"20240516":14}
FROZEN_BOTH_NIGHTS=13
CORE_HOURS=frozenset((23,0,1))

def restrict_core(source):
    if source is None:return None
    return {minute:stations for minute,stations in source.items()
            if minute[3] in CORE_HOURS}

def source_test():
    a={(2024,5,15,22,59):{"R1"},
       (2024,5,15,23,0):{"R2"},
       (2024,5,16,1,59):{"R3"},
       (2024,5,16,2,0):{"R4"}}
    assert list(restrict_core(a))==[(2024,5,15,23,0),(2024,5,16,1,59)]
    assert len(FILE_PAIRS)==8 and len(DAYS)==2
    assert set(FROZEN_NIGHT_MARGINS)==set(DAYS)
    return "PASS_SOURCE_CORE_HOURS_AND_NESTED_PAIR_GATES"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--out",default="MYOTIS_2026_CORE_LOGGER_WINDOW_V2.json")
    a=parser.parse_args()
    guard=source_test()
    if a.self_test:
        print(json.dumps({"synthetic_test":guard,"real_data_opened":False}))
        return

    bats=[p[0] for p in FILE_PAIRS]
    full={d:{} for d in DAYS}
    reports=[]
    for label,r15,r16 in FILE_PAIRS:
        for day,rid in zip(DAYS,(r15,r16)):
            rep,mapping=parse_events(f"{label}_{day}.csv",rid,day)
            reports.append(rep)
            full[day][label]=mapping

    result=None
    status="STOP_SOURCE_QA_OR_MARGINS"
    diagnostic_flags={"all_16_source_QA_pass":False,"old_margins_match":None,
        "old_both_night_pair_total_match":None,"core_nested_in_allnight":None,
        "core_incidence_not_larger_than_allnight":None,"core_both_subset":None}
    diagnostic_flags["all_16_source_QA_pass"]=all(r.get("status")=="SOURCE_STRUCTURAL_QA_ONLY" for r in reports)
    if diagnostic_flags["all_16_source_QA_pass"]:
        fullbinary={}
        corebinary={}
        nightstats=[]
        for night in DAYS:
            selection={b:restrict_core(full[night][b]) for b in bats}
            all_minutes=sum(len(full[night][b]) for b in bats)
            core_minutes=sum(len(selection[b]) for b in bats)
            pairall={}
            paircore={}
            central_totals=[]
            for b1,b2 in combinations(bats,2):
                k=(b1,b2)
                pairall[k]=joint_minutes(full[night][b1],full[night][b2])>0
                newJ=joint_minutes(selection[b1],selection[b2])
                paircore[k]=newJ>0
                central_totals.append(newJ)
            fullbinary[night]=pairall
            corebinary[night]=paircore
            nightstats.append({
                "original_source_night":night,
                "original_tagged_bats":8,
                "fixed_possible_pairs":len(central_totals),
                "bats_with_any_core_qualified_minute":sum(bool(selection[b]) for b in bats),
                "qualified_bat_minute_keys_full_night":all_minutes,
                "qualified_bat_minute_keys_core":core_minutes,
                "fraction_of_qualified_bat_minute_keys_core":core_minutes/all_minutes if all_minutes else 0,
                "pairs_with_core_shared_receiver_minute":sum(paircore.values()),
                "sum_pair_by_minute_core_incidences":sum(central_totals),
                "core_pair_minutes_median":q(central_totals,.5),
                "core_pair_minutes_p05":q(central_totals,.05),
                "core_pair_minutes_p95":q(central_totals,.95)
            })

        n_full={d:sum(fullbinary[d].values()) for d in DAYS}
        full_both=sum(fullbinary[DAYS[0]][k] and fullbinary[DAYS[1]][k]
                      for k in fullbinary[DAYS[0]])
        core_both=sum(corebinary[DAYS[0]][k] and corebinary[DAYS[1]][k]
                      for k in corebinary[DAYS[0]])
        subset=all(not corebinary[d][k] or fullbinary[d][k]
                   for d in DAYS for k in corebinary[d])
        diagnostic_flags.update({
          "old_margins_match":n_full==FROZEN_NIGHT_MARGINS,
          "old_both_night_pair_total_match":full_both==FROZEN_BOTH_NIGHTS,
          "core_nested_in_allnight":subset,
          "core_incidence_not_larger_than_allnight":all(
              s["sum_pair_by_minute_core_incidences"]<=x
              for s,x in zip(nightstats,(347,516))),
          "core_both_subset":core_both<=13,
          "has_exactly_28_fixed_pairs":len(fullbinary[DAYS[0]])==28
        })
        valid=all(diagnostic_flags[k] for k in (
            "old_margins_match","old_both_night_pair_total_match",
            "core_nested_in_allnight","core_incidence_not_larger_than_allnight",
            "core_both_subset","has_exactly_28_fixed_pairs"))
        if valid:
            status="EXPLORATORY_CORE_LOGGER_WINDOW_DESCRIPTIVE_ONLY"
            first=nightstats[0]["pairs_with_core_shared_receiver_minute"]
            second=nightstats[1]["pairs_with_core_shared_receiver_minute"]
            result={
                "source_nights":nightstats,
                "core_binary_pairs_positive_both_nights":core_both,
                "core_binary_pairs_only_first":first-core_both,
                "core_binary_pairs_only_second":second-core_both,
                "core_binary_pairs_neither":28-first-second+core_both,
                "known_full_night_positives":n_full,
                "known_full_night_binary_both":full_both
            }
            assert sum(result[k] for k in (
                "core_binary_pairs_positive_both_nights",
                "core_binary_pairs_only_first",
                "core_binary_pairs_only_second",
                "core_binary_pairs_neither"))==28

    receipt={
      "status":status,
      "analysis_tier":"POST_OUTCOME_EXPLORATORY_SENSITIVITY_ONLY",
      "contract":"MYOTIS_2026_LOGGER_CORE_23_TO_02_EXPLORATORY_CONTRACT_V2.md",
      "time_bin":"source clock 23:00-02:00, NOT validated astronomical foraging window",
      "core_hours_preselected":[0,1,23],
      "n_original_source_files":len(reports),
      "descriptive_aggregates":result,
      "QA_boolean_diagnostic_flags":diagnostic_flags,
      "raw_bat_or_receiver_ID_or_datetime_or_RSSI_output":False,
      "source_station_coordinates_or_prey_results_accessed":False,
      "no_p_values_or_social_causal_conclusion":True,
      "old_full_night_V1a_V1b_unmodified":True,
      "independent_uptime_and_true_clock_zone_unverified":True,
      "synthetic_source_guard":guard
    }
    Path(a.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":status,
      "core_aggregates":result,
      "QA_boolean_diagnostic_flags":diagnostic_flags,
      "no_social_p_values_or_raw_identifiers":True,
      "not_equivalent_to_original_sunset_sunrise_exclusion":True
    },sort_keys=True))

if __name__=="__main__":
    main()
