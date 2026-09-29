#!/usr/bin/env python3
from __future__ import annotations

import json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core

CONTRACT=ROOT/"post_freeze_extensions/phyllostomus_2021_wet/preflight_contract_v1.json"
SOURCE_CONTRACT=ROOT/"contract/phyllostomus_replication_v1.json"
OUT=ROOT/"post_freeze_extensions/phyllostomus_2021_wet/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/phyllostomus_2021_wet/PREFLIGHT_RESULT_V1.md"


def main():
    c=json.loads(CONTRACT.read_text())
    sc=json.loads(SOURCE_CONTRACT.read_text())
    ua="batter-phyllostomus-2021-wet-preflight-v1/1.0"
    gps=core.get(sc["source"]["gps"],ua)
    ref=core.get(sc["source"]["reference"],ua)
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)

    pre=core.build_pre_numeric(rows,headers,refs,sc)
    admitted=list(pre["admitted_cohorts"])
    target=[x for x in admitted if str(x).endswith("::2021")]
    target_meta={k:v for k,v in pre["cohort_meta"].items() if str(k).endswith("::2021")}
    all_years=sorted({str(k).split("::")[-1] for k in pre["cohort_meta"]})

    # Existing run_contract() calls analyze(rows, pre, contract, ...) using the full admitted cohort list.
    original_pipeline_would_include_2021=bool(target)
    prospective_untouched_possible=False

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_height_values_parsed":False,
        "source_gps_rows":len(rows),
        "all_structural_years":all_years,
        "all_admitted_cohorts":admitted,
        "target_2021_cohorts":target,
        "target_2021_cohort_meta":target_meta,
        "original_pipeline_uses_full_admitted_cohort_list":True,
        "original_numeric_pipeline_would_include_admitted_2021":original_pipeline_would_include_2021,
        "prospective_untouched_2021_test_possible":prospective_untouched_possible,
        "decision":(
            "2021_admitted_but_not_untouched"
            if target else
            "no_admitted_2021_cohort"
        ),
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=[
      "# Phyllostomus 2021 wet-season structural audit v1","",
      "**X-Y-TIME / FIELD-PRESENCE ONLY. Numeric height values were not parsed in this audit.**","",
      f"Admitted 2021 cohorts: **{len(target)}**","",
      f"Decision: **{payload['decision']}**","",
      "The original replication runner passes the full admitted cohort list to the numeric analysis. Therefore an admitted 2021 cohort cannot be called an untouched prospective validation unless a separate historical year filter existed; none is present in the frozen contract/runner.",""
    ]
    for k,v in target_meta.items():
        lines.append(f"- {k}: individuals={v.get('individual_count')}, repeat={v.get('repeat_individual_count')}, sessions={v.get('eligible_session_count')}")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
      "all_admitted_cohorts":admitted,
      "target_2021_cohorts":target,
      "target_2021_meta":target_meta,
      "decision":payload["decision"],
      "prospective_untouched_possible":prospective_untouched_possible
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
