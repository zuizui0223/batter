#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json

import scripts.run_cross_panel_endpoint_exclusion as ep
import scripts.run_cross_panel_estimator_calibration as cal

TOL=1e-12

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True)
    args=ap.parse_args()

    cfg,panels=ep.load_contract()
    if args.panel not in panels:
        raise SystemExit(f"unknown panel {args.panel}")

    _spec,records,k,_source,_pre,_fail=ep.load_raw_panel(args.panel)
    expected=ep.baseline_targets()[args.panel]

    old_spec,old_events,old_k,old_source,old_pre,old_fail=cal.load_panel(args.panel)
    old_arrays={
        cohort:cal.make_cohort_arrays(events,old_k)
        for cohort,events in sorted(old_events.items())
    }
    old_observed,_,_=cal.observed_eval(old_arrays)

    zero_events,zero_qc=ep.events_after_exclusion(records,0)
    zero_arrays={
        cohort:cal.make_cohort_arrays(events,k)
        for cohort,events in sorted(zero_events.items())
        if events
    }
    zero_observed,_,_=cal.observed_eval(zero_arrays)

    a=float(old_observed["common_cell_marginal"])
    b=float(zero_observed["common_cell_marginal"])
    if abs(a-expected)>TOL:
        raise RuntimeError(f"existing loader mismatch: {a} != {expected}")
    if abs(b-expected)>TOL:
        raise RuntimeError(f"zero-radius reconstruction mismatch: {b} != {expected}")

    print(json.dumps({
        "panel":args.panel,
        "expected":expected,
        "existing_loader":a,
        "zero_radius_runner":b,
        "absolute_tolerance":TOL,
        "zero_radius_surviving_sessions":zero_qc["surviving_sessions"],
        "pass":True,
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
