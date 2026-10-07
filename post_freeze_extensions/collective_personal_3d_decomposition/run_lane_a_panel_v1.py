#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.collective_personal_3d_decomposition.run_v1 import cfg, build_sessions, run_laneA

OUTDIR=ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/lane_a_panel_results"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True)
    args=ap.parse_args()
    c=cfg()
    if args.panel not in c["lane_A_natural_turnover"]["included_panels"]:
        raise SystemExit("panel not frozen for Lane A")
    sessions,_=build_sessions(args.panel,c)
    result=run_laneA(args.panel,sessions,c)
    OUTDIR.mkdir(parents=True,exist_ok=True)
    (OUTDIR/f"{args.panel}_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({args.panel:result},sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
