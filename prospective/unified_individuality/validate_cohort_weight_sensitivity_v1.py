#!/usr/bin/env python3
"""Independent original-CSV check of dependent-dyad cohort weighting diagnostics.

Reads the immutable JAE CSV and reproduces all committed descriptive medians
and cohort pair dominance; this runs NO hypothesis tests/bootstraps or fitting.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict, Counter
import csv, hashlib, json, math, statistics

ROOT=Path(__file__).resolve().parent
ORIGINAL=ROOT/"figures/original_jae/centered_shape_individual_profiles_v1.csv"
SUMMARY=ROOT/"figures/COHORT_WEIGHT_SENSITIVITY_V1.json"
SOURCE_SHA="91cae4c22588db0976dfe3e273eabebaa89dc2844e996f42d01ef617672dc3f8"
JSON_SHA="9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2"
PANELS=["eidolon","hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"]
EXPECTED_INDIV=[20,24,33,16,10]
EXPECTED_PAIRS=[41,276,262,60,45]

def same(x,y,what):
    assert math.isclose(x,y,abs_tol=1e-11,rel_tol=0),(what,x,y)

def main():
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==SOURCE_SHA
    s=json.loads(SUMMARY.read_text(encoding="utf8"))
    assert s["source_csv_sha256"]==SOURCE_SHA
    assert s["source_json_sha256"]==JSON_SHA
    assert s["schema_version"]==1
    assert "post-outcome descriptive" in s["analysis_tier"]
    assert s["source_profile_records"]==103
    assert s["total_within_cohort_nonindependent_pairs"]==684
    with ORIGINAL.open(newline="",encoding="utf8") as f:
        records=list(csv.DictReader(f))
    assert len(records)==103
    names=[k for k in records[0] if k.startswith("bin_")]
    assert len(names)==10
    raw_ids=Counter(r["individual"] for r in records)
    assert len(raw_ids)==101 and sorted(v for v in raw_ids.values() if v>1)==[2,2]
    assert s["distinct_literal_identifier_strings"]==101
    assert s["source_ids_repeated_across_panels"]==2
    groups=defaultdict(list)
    for row in records:
        prob=tuple(float(row[k]) for k in names)
        same(sum(prob),1,"source original probability row")
        groups[(row["panel"],row["cohorts"])].append(prob)
    assert len(groups)==12
    byco={(r["panel"],r["cohort"]):r for r in s["by_cohort"]}
    assert len(byco)==12
    assert set(byco)==set(groups)
    groups_per_panel=defaultdict(list)
    for key,records in groups.items():
        panel,cohort=key
        values=[]
        for i in range(len(records)):
            for j in range(i+1,len(records)):
                v=sum(min(x,y) for x,y in zip(records[i],records[j]))
                w=1-.5*sum(abs(x-y) for x,y in zip(records[i],records[j]))
                same(v,w,"total variation identity")
                values.append(v)
        expected=byco[key]
        assert len(records)==expected["n_source_panel_records"]
        assert len(values)==expected["n_unordered_pairs"]
        if values:
            same(statistics.median(values),expected["dyad_median"],"cohort median "+cohort)
        else:
            assert expected["dyad_median"] is None
        groups_per_panel[panel].append((cohort,records,values))
    bypanel={r["panel"]:r for r in s["by_panel"]}
    assert set(bypanel)==set(PANELS)
    for panel,n,pairs in zip(PANELS,EXPECTED_INDIV,EXPECTED_PAIRS):
        g=groups_per_panel[panel]
        total_n=sum(len(records) for _,records,_ in g)
        observed=[v for _,_,values in g for v in values]
        eligible=[item for item in g if len(item[2])>0]
        all_cohort_medians=[statistics.median(values) for _,_,values in eligible]
        ranked=sorted(eligible,key=lambda x:(-len(x[2]),x[0]))
        biggest=ranked[0]
        without=[v for _,_,values in eligible if values is not biggest[2] for v in values]
        # Lists are references in this computation; identity check just removes the
        # unique largest cohort rather than deleting a median-matched value.
        expected=bypanel[panel]
        assert total_n==n==expected["n_panel_profile_records"]
        assert len(observed)==pairs==expected["n_unordered_pairs"]
        assert expected["n_cohorts"]==len(g)
        assert expected["n_pair_eligible_cohorts"]==len(eligible)
        assert expected["n_two_record_cohorts"]==sum(len(a)==2 for _,a,_ in eligible)
        same(statistics.median(observed),expected["pair_pooled_median"],panel+" pooled")
        same(statistics.median(all_cohort_medians),expected["equal_cohort_median_of_medians"],panel+" cohort")
        same(min(all_cohort_medians),expected["min_cohort_median"],panel+" min cohort")
        same(max(all_cohort_medians),expected["max_cohort_median"],panel+" max cohort")
        assert biggest[0]==expected["dominant_cohort"]
        assert len(biggest[1])==expected["dominant_cohort_n_profiles"]
        assert len(biggest[2])==expected["dominant_cohort_pairs"]
        same(len(biggest[2])/len(observed),expected["dominant_cohort_pair_share"],panel+" dominant share")
        assert len(without)==expected["leave_dominant_out_pairs"]
        if without:
            same(statistics.median(without),expected["leave_dominant_out_median"],panel+" without largest")
        else:
            assert expected["leave_dominant_out_median"] is None
        print("PASS",panel,"original bats/panel",n,"nonindependent pairs",pairs,
              "pooled median",f"{statistics.median(observed):.6f}",
              "equal cohort median",f"{statistics.median(all_cohort_medians):.6f}")
    assert sum(len(g) for g in groups.values())==103
    assert sum(1 for _,r,_ in groups_per_panel["eidolon"] if len(r)==2)==3
    for f,table,methods in [
        ("SUPPORTING_INFORMATION_DRAFT_V1.md","Supplementary Table U9.","Supplementary Methods U14."),
        ("SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md","Supplementary Table S9.","Supplementary Methods S14.")
    ]:
        t=(ROOT/f).read_text(encoding="utf8")
        for term in [table,methods,"68.3%","75.0%","0.865","not confidence",
                     "single pair"]:
            assert term.lower() in t.lower(),(f,term)
    main=(ROOT/"INTEGRATED_MANUSCRIPT_V1.md").read_text(encoding="utf8")
    anon=(ROOT/"COMPLETE_ANONYMOUS_TEXT_DRAFT_V1.md").read_text(encoding="utf8")
    for t in [main,anon]:
        for term in ["cohort","68.3%","75.0%","not species"]:
            assert term.lower() in t.lower(),("cohort warning absent",term)
    print("PASS independent original CSV source-to-cohort-weight audit: NO new inferential family")

if __name__=="__main__":
    main()
