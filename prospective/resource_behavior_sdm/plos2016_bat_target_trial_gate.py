"""PLOS 2016 S1 original 3D source: response-blind Bat×Target×Test gate.

After checksum/headers, inspect ONLY columns E/F/G (target, bat, test).
Never access/read X/Y/Z numeric coordinates or Distance toT in this stage.
No raw bat labels, target labels or per-trial rows are persisted.
The sample support is frozen from the original paper: n=5, two targets,
three trials/animal/target, 30 independent trial sequences.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

from plos2016_3d_xlsx_source_gate import fetch_official, structure_audit,SHEET_NS
from plos2016_3d_header_semantics import inspect_publisher_header

SHA="3cce76e3f75c1eb49ac1a8344880a42da1de163886372a944080e074cdd1fb42"
HEADER=["X Ref Target","Y Ref Target","Z Ref Target","Distance toT","Target","Bat","Test"]
PASS="PLOS_BAT_TARGET_TEST_LABEL_SUPPORT_PASS"


def parse_labels(payload):
    head=inspect_publisher_header(payload)
    if head["source_sha256"]!=SHA:
        raise RuntimeError("PLOS_ORIGINAL_S1_BYTE_IDENTITY_DRIFT")
    if head["verified_original_first_row_column_names"]!=HEADER:
        raise RuntimeError("PLOS_ORIGINAL_HEADER_CONTRACT_DRIFT")
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        strings=[]
        if "xl/sharedStrings.xml" in z.namelist():
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings=["".join((y.text or "") for y in n.iter(SHEET_NS+"t")) for n in root.findall(SHEET_NS+"si")]
        sheet=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows=sheet.findall(".//"+SHEET_NS+"sheetData/"+SHEET_NS+"row")
        groups=Counter()
        entities=set()
        targets=set()
        pairs=defaultdict(set)
        missing=0
        records=0
        for r in rows[1:]:
            # E/F/G are original grouping metadata; columns A-D are not touched.
            keys={}
            for c in r.findall(SHEET_NS+"c"):
                cell=c.get("r","")
                m=re.fullmatch(r"([A-Z]+)[0-9]+",cell)
                if not m or m.group(1) not in ("E","F","G"):
                    continue
                value=c.find(SHEET_NS+"v")
                if value is None:
                    continue
                raw=(value.text or "").strip()
                if c.get("t")=="s":
                    if not raw.isdigit() or int(raw)>=len(strings):
                        raise RuntimeError("PLOS_SOURCE_METADATA_SHARED_STRING_INVALID")
                    raw=strings[int(raw)].strip()
                keys[m.group(1)]=raw
            records+=1
            if any(not keys.get(x) for x in ("E","F","G")):
                missing+=1
                continue
            target,individual,test=keys["E"],keys["F"],keys["G"]
            if len(target)>70 or len(individual)>70 or len(test)>70:
                raise RuntimeError("PLOS_UNSAFE_CATEGORICAL_SOURCE_LABEL")
            groups[(individual,target,test)]+=1
            entities.add(individual)
            targets.add(target)
            pairs[(individual,target)].add(test)
    sizes=list(groups.values())
    per_target_group_counts=Counter()
    per_bat_target_coverage=defaultdict(set)
    per_bat_group_counts=Counter()
    for bat, target, test in groups:
        per_target_group_counts[target]+=1
        per_bat_target_coverage[bat].add(target)
        per_bat_group_counts[bat]+=1
    coverage_hist=Counter(len(v) for v in per_bat_target_coverage.values())
    result={
      "schema":"batter.plos_2016_source_bat_target_test.v1",
      "status":PASS,
      "original_supplement_sha256":SHA,
      "full_observed_rows_with_group_labels":records-missing,
      "rows_missing_group_labels":missing,
      "n_animal_groups":len(entities),
      "n_source_target_levels":len(targets),
      "n_bat_target_pairs":len(pairs),
      "n_distinct_bat_target_trial_sequences":len(groups),
      "bat_target_coverage_histogram":{str(k):v for k,v in sorted(coverage_hist.items())},
      "target_group_counts_sorted":sorted(per_target_group_counts.values()),
      "individual_total_trial_counts_sorted":sorted(per_bat_group_counts.values()),
      "min_rows_per_sequence":min(sizes) if sizes else None,
      "max_rows_per_sequence":max(sizes) if sizes else None,
      "bat_target_sequence_count_values_sorted":sorted(Counter(len(t) for t in pairs.values()).items()),
      "expected_5_bats_2_targets_3_trials_each":(len(entities)==5 and len(targets)==2
           and len(pairs)==10 and all(len(v)==3 for v in pairs.values())
           and len(groups)==30 and missing==0 and len(sizes)>0),
      "raw_bat_labels_saved":False,
      "raw_target_labels_saved":False,
      "x_y_z_or_distance_values_read":False,
      "new_predictive_effect":None,
    }
    if not result["expected_5_bats_2_targets_3_trials_each"]:
        result["status"]="PLOS_BAT_TARGET_TRIAL_SUPPORT_STOP"
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="prospective/resource_behavior_sdm/plos2016_bat_target_trial_structure.json")
    opts=ap.parse_args()
    out=Path(opts.out);out.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=parse_labels(fetch_official())
    except Exception as exc:
        result={"schema":"batter.plos_2016_source_bat_target_test.v1",
                "status":"PLOS_BAT_TARGET_TRIAL_SOURCE_STOP",
                "reason":(type(exc).__name__+":"+str(exc))[:230],
                "x_y_z_or_distance_values_read":False,
                "new_predictive_effect":None}
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PLOS_BAT_TARGET_TEST",result["status"],flush=True)
    if "n_animal_groups" in result:
        keys=["full_observed_rows_with_group_labels","n_animal_groups",
              "n_source_target_levels","n_bat_target_pairs",
              "n_distinct_bat_target_trial_sequences",
              "bat_target_sequence_count_values_sorted"]
        print("PLOS_LABEL_STRUCTURE",json.dumps({k:result[k] for k in keys}),flush=True)
        print("PLOS_LABEL_DIAGNOSTICS",json.dumps({
            "bat_target_coverage_histogram":result["bat_target_coverage_histogram"],
            "target_group_counts_sorted":result["target_group_counts_sorted"],
            "individual_total_trial_counts_sorted":result["individual_total_trial_counts_sorted"],
            "per_bat_target_number_of_tests_histogram":result["bat_target_sequence_count_values_sorted"],
        },sort_keys=True),flush=True)
    else:
        print("PLOS_LABEL_STRUCTURE_STOP",result["reason"],flush=True)
    return 0 if result["status"]==PASS else 3

if __name__=="__main__":
    raise SystemExit(main())
