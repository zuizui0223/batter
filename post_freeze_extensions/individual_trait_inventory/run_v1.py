#!/usr/bin/env python3
from __future__ import annotations

import csv, io, json, math, re, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from post_freeze_extensions.behavior_proxy_inventory.run_v1 import SOURCES, get, canon

OUT=ROOT/"post_freeze_extensions/individual_trait_inventory/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/individual_trait_inventory/RESULT_V1.md"

PANELS=["eidolon","hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"]
KEYWORDS=["sex","age","life_stage","reproductive","lactat","mass","weight","body","forearm","wing","condition"]


def rows(data):
    rd=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    out=[]
    for r in rd:
        out.append({canon(k):("" if v is None else str(v).strip()) for k,v in r.items() if k is not None})
    return out


def summarize(vals):
    v=[x for x in vals if str(x).strip()!=""]
    uniq=sorted(set(v))
    numeric=[]
    for x in v:
        try:
            z=float(x)
            if math.isfinite(z): numeric.append(z)
        except Exception:
            pass
    out={"nonempty_n":len(v),"unique_n":len(uniq),"unique_values":uniq[:30]}
    if len(numeric)==len(v) and numeric:
        a=np.asarray(numeric,dtype=float)
        out["numeric"]={"min":float(a.min()),"median":float(np.median(a)),"max":float(a.max()),"sd":float(a.std(ddof=1)) if len(a)>1 else 0.0}
    return out


def main():
    panels={}
    common=None
    for panel in PANELS:
        data=get(SOURCES[panel]["reference"],panel,"reference")
        rr=rows(data)
        headers=sorted({k for r in rr for k in r})
        cand=[h for h in headers if any(k in h.lower() for k in KEYWORDS)]
        rec={"reference_rows":len(rr),"candidate_fields":{}}
        for h in cand:
            rec["candidate_fields"][h]=summarize([r.get(h,"") for r in rr])
        panels[panel]=rec
        common=set(cand) if common is None else common & set(cand)

    common=sorted(common or [])
    variable_common=[]
    for h in common:
        if all(panels[p]["candidate_fields"][h]["unique_n"]>=2 for p in PANELS):
            variable_common.append(h)

    payload={
        "schema_version":1,
        "study_id":"batter-individual-trait-inventory-v1",
        "vertical_outcomes_used":False,
        "panels":panels,
        "candidate_fields_common_to_all_five":common,
        "variable_candidate_fields_common_to_all_five":variable_common
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=["# Individual-trait inventory v1","",
           "**Reference-data audit only. No vertical outcome was used.**","",
           "| panel | candidate individual fields |",
           "|---|---|"]
    for p in PANELS:
        fields=[]
        for h,s in panels[p]["candidate_fields"].items():
            fields.append(f"{h} (nonempty {s['nonempty_n']}, unique {s['unique_n']})")
        lines.append(f"| {p} | "+(", ".join(fields) if fields else "none")+" |")
    lines += ["","Common candidate fields across all five: "+(", ".join(common) if common else "**none**"),
              "","Common fields with variation in every panel: "+(", ".join(variable_common) if variable_common else "**none**"),""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "common":common,
        "variable_common":variable_common,
        "panels":{p:panels[p]["candidate_fields"] for p in PANELS}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
