#!/usr/bin/env python3
"""Check future 2x2 bat-level opportunity×masking data and compute a DESCRIPTIVE interaction.

NO bat records are bundled. No synthetic biological power is calculated.
Important: This script is not an authorized confirmatory statistical test.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

FIELDS = ("bat_id","block_id","route_open","masker_on","n_assigned_attempts","n_successes")
ARMS = frozenset(((0,0),(0,1),(1,0),(1,1)))

class StructuralStop(ValueError):
    pass

def parse_int(value, field, line, allowed=None):
    if value is None or not str(value).strip():
        raise StructuralStop(f"row {line}: missing {field}")
    try:
        number=int(value)
        if str(number)!=str(value).strip():
            raise ValueError("noncanonical integer")
    except Exception:
        raise StructuralStop(f"row {line}: {field} must be a canonical integer")
    if allowed is not None and number not in allowed:
        raise StructuralStop(f"row {line}: {field} invalid value {number}")
    return number

def analyse(rows, expected_trials=None):
    if not rows:
        raise StructuralStop("STOP_NO_RANDOMIZED_BATS")
    by_block=defaultdict(dict)
    seen_bats=set()
    allowed_fields=set(FIELDS)
    for line,row in enumerate(rows,start=2):
        if not allowed_fields.issubset(row):
            raise StructuralStop(f"row {line}: required fields missing")
        bat=(row["bat_id"] or "").strip()
        block=(row["block_id"] or "").strip()
        if not bat or not block:
            raise StructuralStop(f"row {line}: empty animal or block")
        if bat in seen_bats:
            raise StructuralStop(f"row {line}: repeated bat_id {bat!r} is NOT a new biological replicate")
        seen_bats.add(bat)
        r=parse_int(row["route_open"],"route_open",line,allowed={0,1})
        m=parse_int(row["masker_on"],"masker_on",line,allowed={0,1})
        attempts=parse_int(row["n_assigned_attempts"],"n_assigned_attempts",line)
        successes=parse_int(row["n_successes"],"n_successes",line)
        if attempts<1 or successes<0 or successes>attempts:
            raise StructuralStop(f"row {line}: invalid success counts")
        if expected_trials is not None and attempts!=expected_trials:
            raise StructuralStop(f"row {line}: expected {expected_trials} attempts, got {attempts}; attrition must be adjudicated separately")
        arm=(r,m)
        if arm in by_block[block]:
            raise StructuralStop(f"row {line}: duplicated cell {arm} in randomization block {block}")
        by_block[block][arm]=(bat,successes/attempts,attempts,successes)
    for block,cells in by_block.items():
        if frozenset(cells)!=ARMS:
            raise StructuralStop(f"block {block}: four randomization cells not complete; no automatic dropping/imputation")
    if len(by_block)<2:
        raise StructuralStop("At least 2 independent 4-bat blocks needed for descriptive between-block variation")
    ds=[]
    summaries={}
    for block,cells in sorted(by_block.items()):
        y=lambda r,m: cells[r,m][1]
        d=(y(1,1)-y(0,1))-(y(1,0)-y(0,0))
        ds.append(d)
        summaries[block]={"bat_count":4,"difference_in_differences":d}
    est=sum(ds)/len(ds)
    sd=math.sqrt(sum((x-est)**2 for x in ds)/(len(ds)-1))
    return {
        "tier":"BAT_LEVEL_DESCRIPTIVE_NO_INFERENTIAL_TEST",
        "n_biological_bats":len(seen_bats),
        "n_complete_independent_randomization_blocks":len(by_block),
        "route_opportunity_x_masker_success_interaction":est,
        "between_block_sd":sd,
        "estimated_p_value":None,
        "confidence_interval":None,
        "reason_no_inference":"New experiment not authorized; nominal exact permutation of 4!^B tests global sharp no-effect, not interaction-only null with main effects",
        "warning":"Block labels and observed arm allocation cannot prove real randomization; must audit source-sealed schedule and complete attrition externally",
        "block_descriptive":summaries
    }

def self_test():
    patterns=[
       (("A",1,0),[0.5,0.3,0.6,0.55]),
       (("B",1,1),[0.4,0.2,0.5,0.45])
    ]
    rows=[]
    for block_meta, vals in patterns:
        block=block_meta[0]
        for j,(arm,y) in enumerate(zip(sorted(ARMS),vals)):
            rows.append(dict(bat_id=f"{block}{j}",block_id=block,
                             route_open=str(arm[0]),masker_on=str(arm[1]),
                             n_assigned_attempts="20",n_successes=str(round(20*y))))
    res=analyse(rows,expected_trials=20)
    # At 20 attempts per bat, 0.55 -> 11/20, 0.45 -> 9/20.
    assert math.isclose(res["route_opportunity_x_masker_success_interaction"],0.15,abs_tol=1e-12),res
    assert res["estimated_p_value"] is None and res["n_biological_bats"]==8
    bad=[r.copy() for r in rows]
    bad[4]["bat_id"]=bad[0]["bat_id"]
    try:analyse(bad,expected_trials=20)
    except StructuralStop:pass
    else:raise AssertionError("duplicate bat not caught")
    bad=[r.copy() for r in rows]
    bad.pop()
    try:analyse(bad,expected_trials=20)
    except StructuralStop:pass
    else:raise AssertionError("missing randomized bat not caught")
    bad=[r.copy() for r in rows]
    bad[0]["n_assigned_attempts"]="19"
    try:analyse(bad,expected_trials=20)
    except StructuralStop:pass
    else:raise AssertionError("post-randomization missingness not caught")
    return {"toy_cell_level_interaction":0.15,
            "eight_physical_bat_units":"PASS",
            "duplicate_bat_guard":"PASS",
            "missing_randomized_bat_guard":"PASS",
            "incomplete_attempt_guard":"PASS",
            "no_fake_interaction_p_value":"PASS"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",help="Future externally frozen and independently verified bat-level design table")
    p.add_argument("--expected-trials",type=int,default=None)
    p.add_argument("--out",default=None)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),indent=2));return
    if not args.csv or args.expected_trials is None or args.expected_trials<1:
        raise SystemExit("Need a source-verified bat-level --csv and positive frozen --expected-trials; see study protocol")
    with open(args.csv,newline="",encoding="utf-8-sig") as fh:
        result=analyse(list(csv.DictReader(fh)),expected_trials=args.expected_trials)
    if args.out:
        Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
