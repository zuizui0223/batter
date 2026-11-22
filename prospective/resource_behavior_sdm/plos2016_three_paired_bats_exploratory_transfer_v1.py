"""PLOS 2016 publisher-original S1: exploratory 3 *paired* bat heldout 3D test.

THIS IS POST-FAILED-FIVE-BAT-GATE EXPLORATION, not a restored original
pre-registered result. Never report wild resource×height or causal inference.
Original numeric XYZ read only AFTER digest, header and label-only structural
admission. No animal labels / locations / frame records leave process.
"""
from __future__ import annotations
import argparse
import bisect
from collections import Counter,defaultdict
from itertools import product
import io
import json
import math
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

from plos2016_bat_target_trial_gate import (
    parse_labels, SHA, HEADER, fetch_official, SHEET_NS
)
from plos2016_3d_header_semantics import inspect_publisher_header

ALPHA=.5
RADIAL_QUANTILES=(1/3,2/3)
HEIGHT_QUANTILES=(.2,.4,.6,.8)
SOURCE="10.1371/journal.pone.0163492.s001"
STATUS="PLOS_THREE_PAIRED_BATS_POST_GATE_EXPLORATORY_ONLY"


def source_blind_structure_gate(payload):
    result=parse_labels(payload)
    head=inspect_publisher_header(payload)
    if head["source_sha256"]!=SHA or head["verified_original_first_row_column_names"]!=HEADER:
        raise ValueError("STOP_ORIGINAL_PLOS_S1_IDENTITY_OR_HEADER")
    expected=[
       (result.get("n_animal_groups"),5),
       (result.get("n_source_target_levels"),2),
       (result.get("n_bat_target_pairs"),8),
       (result.get("n_distinct_bat_target_trial_sequences"),30),
       (result.get("individual_total_trial_counts_sorted"),[3,3,8,8,8]),
       (result.get("target_group_counts_sorted"),[15,15]),
       (result.get("bat_target_coverage_histogram"),{"1":2,"2":3})
    ]
    if any(got!=required for got,required in expected):
        raise ValueError("STOP_CHANGED_SOURCE_BAT_TARGET_SUPPORT")
    if result["status"]!="PLOS_BAT_TARGET_TRIAL_SUPPORT_STOP":
        raise ValueError("STOP_EXPECTED_FAILED_ORIGINAL_FIVE_BAT_PAIR_GATE")
    return {"sha256":SHA,"n_original_bats":5,
            "n_paired_bats":3,"original_five_bat_gate_pass":False}


def _read_shared(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root=ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join((t.text or "") for t in si.iter(SHEET_NS+"t"))
            for si in root.findall(SHEET_NS+"si")]


def _value(cell, shared):
    node=cell.find(SHEET_NS+"v")
    if node is None:
        return None
    x=(node.text or "").strip()
    if cell.get("t")=="s":
        if not x.isdigit() or int(x)>=len(shared):
            raise ValueError("STOP_UNTRUSTED_SHARED_STRING_INDEX")
        return shared[int(x)].strip()
    return x


def _source_rows_after_gate(payload):
    """NEVER parse D=Distance toT, which contains the target Z."""
    source_blind_structure_gate(payload)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        strings=_read_shared(archive)
        root=ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        raw=root.findall(".//"+SHEET_NS+"sheetData/"+SHEET_NS+"row")
        rows=[]
        for row in raw[1:]:
            item={}
            for cell in row.findall(SHEET_NS+"c"):
                m=re.fullmatch(r"([A-Z]+)[0-9]+",cell.get("r",""))
                if m is None or m.group(1) not in ("A","B","C","E","F","G"):
                    continue
                item[m.group(1)]=_value(cell,strings)
            if not all(item.get(k) is not None for k in ("E","F","G")):
                raise ValueError("STOP_MISSING_ORIGINAL_TARGET_GROUPING")
            rows.append(item)
    target_names={r["E"] for r in rows}
    bats={r["F"] for r in rows}
    target_map={v:k for k,v in enumerate(sorted(target_names))}
    groups=defaultdict(list)
    for r in rows:
        groups[r["F"],r["E"],r["G"]].append(r)
    paired=[i for i in bats if len({k[1] for k in groups if k[0]==i})==2]
    if len(paired)!=3 or len(target_names)!=2:
        raise ValueError("STOP_NO_THREE_SOURCE_PAIRED_BATS")
    # Structure-only first; only open numeric coordinates of eligible bats.
    eligible=[]
    for (bat,target,test),frames in groups.items():
        if bat not in paired:
            continue
        xyz=[]
        for frame in frames:
            try:
                x,y,z=map(float,(frame.get("A"),frame.get("B"),frame.get("C")))
            except (ValueError,TypeError):
                raise ValueError("STOP_NONNUMERIC_PAIRED_XYZ")
            if not all(map(math.isfinite,(x,y,z))):
                raise ValueError("STOP_NONFINITE_PAIRED_XYZ")
            xyz.append((math.hypot(x,y),z))
        if not xyz:
            raise ValueError("STOP_EMPTY_SOURCE_SEQUENCE")
        eligible.append({"bat":bat,"target":target_map[target],
                         "group":(bat,target,test),"frames":xyz})
    cells=Counter((r["bat"],r["target"]) for r in eligible)
    if len(cells)!=6 or min(cells.values())<3 or len(eligible)!=24:
        raise ValueError("STOP_UNBALANCED_3_PAIRED_BAT_EXPLORATORY_SUPPORT")
    return eligible


def _weighted_thresholds(training, variable, quantiles):
    combos=Counter((r["bat"],r["target"]) for r in training)
    ordered=[]
    for tr in training:
        w=1./(combos[(tr["bat"],tr["target"])]*len(tr["frames"]))
        ordered.extend((pair[variable],w) for pair in tr["frames"])
    ordered.sort()
    total=math.fsum(w for _,w in ordered)
    out=[]
    for q in quantiles:
        target=q*total
        accum=0.
        chosen=ordered[-1][0]
        for v,w in ordered:
            accum+=w
            if accum>=target:
                chosen=v
                break
        out.append(chosen)
    return out


def _bin(v,thresholds):
    return bisect.bisect_right(thresholds,v)


def _train(train,swap_bats=frozenset()):
    radii=_weighted_thresholds(train,0,RADIAL_QUANTILES)
    heights=_weighted_thresholds(train,1,HEIGHT_QUANTILES)
    combos=Counter((r["bat"],r["target"]) for r in train)
    base=defaultdict(lambda:[0.]*5)
    specific=defaultdict(lambda:[0.]*5)
    for trial in train:
        w=1./(combos[(trial["bat"],trial["target"])]*len(trial["frames"]))
        label=trial["target"] ^ int(trial["bat"] in swap_bats)
        for radius,z in trial["frames"]:
            rb=_bin(radius,radii)
            zb=_bin(z,heights)
            base[rb][zb]+=w
            specific[rb,label][zb]+=w
    return radii,heights,base,specific


def _score(test,model):
    radii,heights,base,specific=model
    results=defaultdict(lambda:defaultdict(list))
    for trial in test:
        nbase=nspec=0.
        for radius,z in trial["frames"]:
            rb=_bin(radius,radii)
            zb=_bin(z,heights)
            x=base[rb]
            y=specific[rb,trial["target"]]
            nbase+=math.log((x[zb]+ALPHA)/(math.fsum(x)+5*ALPHA))
            nspec+=math.log((y[zb]+ALPHA)/(math.fsum(y)+5*ALPHA))
        results[trial["bat"]][trial["target"]].append(
            (nspec-nbase)/len(trial["frames"]))
    # trial -> target -> bat equal weighting, and NEVER count GPS frames as bats.
    targets=sorted({t["target"] for t in test})
    if len(results)!=1 or len(targets)!=2:
        raise ValueError("STOP_HELDOUT_UNPAIRED_TARGETS")
    vals={}
    for target in targets:
        x=next(iter(results.values()))[target]
        if not x:
            raise ValueError("STOP_MISSING_HELDOUT_TARGET")
        vals["target_ordinal_"+str(target+1)]=math.fsum(x)/len(x)
    return math.fsum(vals.values())/2, vals


def exploratory_paired_bat_lobo_from_source(payload):
    eligible=_source_rows_after_gate(payload)
    bats=sorted({e["bat"] for e in eligible})
    if len(bats)!=3:
        raise ValueError("STOP_EXPLORATORY_SOURCE_PAIRING_DRIFT")
    folds=[]
    for ordinal,heldout in enumerate(bats,1):
        train=[e for e in eligible if e["bat"]!=heldout]
        test=[e for e in eligible if e["bat"]==heldout]
        model=_train(train)
        outcome,bytarget=_score(test,model)
        others=sorted({r["bat"] for r in train})
        if len(others)!=2:
            raise ValueError("STOP_TRAINING_SOURCE_BATS_NOT_TWO")
        negatives=[]
        for choices in product((0,1),repeat=2):
            swapped=frozenset(others[i] for i,flag in enumerate(choices) if flag)
            model0=_train(train,swap_bats=swapped)
            val,_=_score(test,model0)
            negatives.append({"swapped_source_train_bat_count":len(swapped),
                              "delta":val})
        folds.append({
            "fold_ordinal":ordinal,
            "heldout_animal_count":1,
            "heldout_target_levels":2,
            "heldout_trials":len(test),
            "heldout_recorded_frames":sum(len(e["frames"]) for e in test),
            "target_conditioned_minus_blind_nats_per_frame":outcome,
            "per_target_class_ordinal":bytarget,
            "four_train_bat_whole_label_swaps":negatives,
        })
    deltas=[f["target_conditioned_minus_blind_nats_per_frame"] for f in folds]
    return {
        "schema":"batter.PLOS2016_exploratory_three_paired_bat_height_transfer.v1",
        "status":STATUS,
        "source_original_s001_sha256":SHA,
        "source DOI":SOURCE,
        "original_5_bat_fully_paired_gate":"STOP_UNPAIRED_SOURCE",
        "analysis_status":"POST_FIVE_BAT_SUPPORT_FAILURE_EXPLORATORY",
        "n_source_bats_original":5,
        "n_source_bats_paired_and_eligible":3,
        "n_source_trial_groups_eligible":len(eligible),
        "n_source_frame_rows_eligible":sum(len(e["frames"]) for e in eligible),
        "independent_biological_replicates":3,
        "outer_leave_one_whole_bat_out_folds":3,
        "target_levels":2,
        "not_real_food_abundance":True,
        "not_wild_bat_SDM":True,
        "height_relative_to_experimental_target_not_AGL":True,
        "distance_toT_with_source_height_not_opened":True,
        "source_animal_keys_or_XYZ_exported":False,
        "exact_0_05_test_possible":False,
        "minimum_one_sided_bat_signflip_p":.125,
        "primary_equal_bat_target_heldout_delta_nats_per_recorded_frame":
            math.fsum(deltas)/len(deltas),
        "n_positive_bat_folds":sum(v>0 for v in deltas),
        "negative_control_descriptive_only":True,
        "results_by_anonymous_fold":folds,
        "ecological_resource_conditional_wild_3D_height_gain":None,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    try:
        payload=fetch_official()
        result=exploratory_paired_bat_lobo_from_source(payload)
    except Exception as exc:
        result={"schema":"batter.PLOS2016_exploratory_three_paired_bat_height_transfer.v1",
                "status":"SOURCE_OR_VALIDITY_STOP",
                "source DOI":SOURCE,
                "original_5_bat_fully_paired_gate":"STOP_UNPAIRED_SOURCE",
                "why":(type(exc).__name__+":"+str(exc))[:240],
                "ecological_resource_conditional_wild_3D_height_gain":None,
                "source_animal_keys_or_XYZ_exported":False}
    dest=Path(args.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("PLOS3_PAIRED_BATS",result["status"])
    if result["status"]==STATUS:
        print("REAL_SOURCE_EXPLORATORY_NATS",
              result["primary_equal_bat_target_heldout_delta_nats_per_recorded_frame"])
        print("POSITIVE_SOURCE_BATS",result["n_positive_bat_folds"])
    else:
        print("SOURCE_OR_VALIDITY_STOP",result["why"])
    return 0 if result["status"]==STATUS else 3


if __name__=="__main__":
    sys.exit(main())
