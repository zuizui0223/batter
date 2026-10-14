#!/usr/bin/env python3
"""Independent Python CSV-vs-Node JSON reproduction of 1D overlap (descriptive).

This deliberately reads the *original immutable CSV*, not the JS-derived pair
CSV or the Python-compatible transformed JSON read by the JS figure script.
All comparisons are original cohort-restricted and contain NO significance test.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ARCHIVED=HERE/"figures/original_jae/centered_shape_individual_profiles_v1.csv"
DERIVED=HERE/"figures/FROZEN_PROFILE_OVERLAP_DESCRIPTIVE_V1.json"
EXPECTED_CSV_SHA256="91cae4c22588db0976dfe3e273eabebaa89dc2844e996f42d01ef617672dc3f8"

def quantile(sorted_values,q):
    if not sorted_values:return None
    x=(len(sorted_values)-1)*q
    lo,hi=math.floor(x),math.ceil(x)
    return sorted_values[lo]*(1-(x-lo))+sorted_values[hi]*(x-lo)

def compare(got,want,label):
    assert math.isclose(got,want,rel_tol=0,abs_tol=1e-12),(label,got,want)

def main():
    assert hashlib.sha256(ARCHIVED.read_bytes()).hexdigest()==EXPECTED_CSV_SHA256
    with ARCHIVED.open(newline="",encoding="utf8") as f:
        original=list(csv.DictReader(f))
    assert len(original)==103
    keys=[c for c in original[0] if c.startswith("bin_")]
    assert len(keys)==10
    meta=json.loads(DERIVED.read_text(encoding="utf8"))
    panels=meta["panel_summary"]
    assert len(panels)==5 and meta["total_within_cohort_pairs"]==684
    count=0
    for item in panels:
        panel=item["panel"]
        subset=[r for r in original if r["panel"]==panel]
        assert len(subset)==item["n_individuals"]
        cohort_map=defaultdict(list)
        for r in subset:
            probs=[float(r[key]) for key in keys]
            compare(sum(probs),1,("original profile normalization",panel))
            cohort_map[r["cohorts"]].append(probs)
        assert len(cohort_map)==item["n_source_cohorts"]
        scores=[]
        for cohort,profiles in cohort_map.items():
            per_cohort=[]
            for i in range(len(profiles)):
                for j in range(i+1,len(profiles)):
                    a,b=profiles[i],profiles[j]
                    observed=sum(min(x,y) for x,y in zip(a,b))
                    equivalent=1-0.5*sum(abs(x-y) for x,y in zip(a,b))
                    compare(observed,equivalent,("total variation identity",panel,cohort))
                    per_cohort.append(observed)
                    scores.append(observed)
            archived_row=next(x for x in meta["cohort_summary"] if x["panel"]==panel and x["cohort"]==cohort)
            assert archived_row["n_pairs"]==len(per_cohort)
            if per_cohort:
                compare(statistics.median(per_cohort),archived_row["median"],("stratum median",panel,cohort))
        assert len(scores)==item["n_pairs"]
        scores.sort()
        compare(statistics.median(scores),item["median"],("panel median",panel))
        compare(quantile(scores,.10),item["p10"],("panel q10",panel))
        compare(quantile(scores,.90),item["p90"],("panel q90",panel))
        count+=len(scores)
        print("Independent Python original-CSV match:",panel,
              "biological_n",len(subset),"dependent_dyads",len(scores),
              "median_overlap",f"{statistics.median(scores):.12f}")
    assert count==684
    print("PASS two independent code paths, original CSV vs original JSON: 103 individual profiles, 684 nonindependent same-cohort dyads")

if __name__=="__main__":
    main()
