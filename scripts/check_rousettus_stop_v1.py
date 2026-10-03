#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SQL=ROOT/"prospective/rousettus_social_seeding/sqlite_schema_preflight_summary_v1.json"
DONOR=ROOT/"prospective/rousettus_social_seeding/donor_identity_preflight_summary_v1.json"
ROUTE=ROOT/"prospective/rousettus_social_seeding/route_reuse_contract_v1.json"
WAY=ROOT/"prospective/rousettus_social_seeding/waypoint_sequence_reuse_contract_v1.json"

FORBIDDEN=[
  "prospective/rousettus_social_seeding/ROUTE_REUSE_RESULT_V1.md",
  "prospective/rousettus_social_seeding/route_reuse_result_v1.json",
  "prospective/rousettus_social_seeding/WAYPOINT_SEQUENCE_REUSE_RESULT_V1.md",
  "prospective/rousettus_social_seeding/waypoint_sequence_reuse_result_v1.json",
  "prospective/rousettus_social_seeding/run_route_reuse_outcome_v1.py",
  "prospective/rousettus_social_seeding/run_waypoint_sequence_outcome_v1.py",
]

def main():
    failures=[]
    for p in (SQL,DONOR,ROUTE,WAY):
        if not p.is_file(): failures.append(f"missing required stop/contract file: {p.relative_to(ROOT)}")
    if not failures:
        s=json.loads(SQL.read_text())
        d=json.loads(DONOR.read_text())
        r=json.loads(ROUTE.read_text())
        w=json.loads(WAY.read_text())
        if s.get("decision")!="STOP_BEFORE_COORDINATE_OPENING":
            failures.append("SQLite gate is not STOP_BEFORE_COORDINATE_OPENING")
        if s.get("route_geometry_opened") is not False:
            failures.append("SQLite gate indicates route geometry opened")
        if s.get("coordinate_numeric_values_opened") is not False:
            failures.append("SQLite gate indicates coordinate numeric values opened")
        if d.get("decision")!="STOP_PUBLIC_SOURCE_DONOR_IDENTITY":
            failures.append("donor gate is not STOP_PUBLIC_SOURCE_DONOR_IDENTITY")
        if int(d.get("known_status_max_evaluable_targets",-1))>=int(d.get("frozen_evaluable_target_min",5)):
            failures.append("donor stop no longer structurally binding")
        if r.get("outcome_opened") is not False:
            failures.append("continuous route contract indicates outcome opened")
        if w.get("outcome_opened") is not False:
            failures.append("waypoint contract indicates outcome opened")

    for p in FORBIDDEN:
        if (ROOT/p).exists():
            failures.append(f"forbidden outcome exists after stop: {p}")

    if failures:
        print("Rousettus prospective stop guard: BLOCKED")
        for x in failures: print(" -",x)
        return 1

    print("Rousettus prospective stop guard: PASS")
    print("Continuous route outcome unopened: raw coordinates inaccessible.")
    print("Waypoint-sequence outcome unopened: known-status donor ceiling 4 < 5.")
    print("No rescue outcome files present.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
