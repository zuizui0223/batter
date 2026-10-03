#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUMMARY=ROOT/"prospective/route_emergence/source_preflight_summary_v1.json"
CONTRACT=ROOT/"prospective/route_emergence/preflight_contract_v1.json"

FORBIDDEN=[
    "prospective/route_emergence/route_emergence_result_v1.json",
    "prospective/route_emergence/ROUTE_EMERGENCE_RESULT_V1.md",
    "prospective/route_emergence/run_route_emergence_outcome_v1.py",
    "prospective/route_emergence/early_late_route_stereotypy_v1.json",
]

def main():
    failures=[]
    if not SUMMARY.is_file(): failures.append("missing source-preflight summary")
    if not CONTRACT.is_file(): failures.append("missing frozen preflight contract")
    if not failures:
        s=json.loads(SUMMARY.read_text())
        c=json.loads(CONTRACT.read_text())
        if s.get("tier_A_or_B_exists") is not False:
            failures.append("source adjudication no longer records tier_A_or_B_exists=false")
        if s.get("decision")!="STOP_EXISTING_DATA_ROUTE_FORMATION_OUTCOME":
            failures.append("source adjudication decision is not STOP")
        if s.get("route_shape_outcome_opened") is not False:
            failures.append("route-shape outcome was opened")
        if s.get("vertical_outcome_opened") is not False:
            failures.append("vertical outcome was opened")
        if c.get("outcome_opened") is not False:
            failures.append("contract no longer records outcome_opened=false")
        if "No result from this branch may alter JAE v0.4.0." not in c.get("jae_firewall",""):
            failures.append("JAE firewall wording drifted")

    for p in FORBIDDEN:
        if (ROOT/p).exists():
            failures.append(f"forbidden existing-data formation outcome exists: {p}")

    if failures:
        print("Route-emergence stop guard: BLOCKED")
        for x in failures: print(" -",x)
        return 1

    print("Route-emergence stop guard: PASS")
    print("No Tier A/B formation boundary exists in the current archive.")
    print("No existing-data route-formation or vertical outcome is present.")
    print("Prospective data/reset required before route-emergence inference.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
