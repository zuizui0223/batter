#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.screen_bat_panel_structure as core

CONFIG=Path("config/recovered_child_sources_v1.json")


def main():
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    results=[]
    for spec in cfg["sources"]:
        try:
            result=core.screen({
              "doi":spec["doi"],
              "title":spec["taxon_hint"],
              "bitstream_id":spec["bitstream_id"],
              "filename":spec["filename"],
              "size_bytes":spec["size_bytes"],
              "checksum":spec["md5"],
              "content_url":spec["content_url"],
            })
            result["id"]=spec["id"]
            result["taxon_hint"]=spec["taxon_hint"]
            results.append(result)
        except Exception as exc:
            results.append({
              "id":spec["id"],
              "taxon_hint":spec["taxon_hint"],
              "doi":spec["doi"],
              "status":"transport_or_schema_failure",
              "reason":f"{type(exc).__name__}: {exc}",
              "passes_gate":False,
              "numeric_height_values_parsed":False,
            })

    passing=[r for r in results if r.get("passes_gate")]
    payload={
      "screen_id":"batter-recovered-child-structural-screen-v1",
      "results":results,
      "passing_source_count":len(passing),
      "numeric_height_values_parsed":False,
    }
    out=Path("results/recovered_child_structural_screen_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "passing_source_count":len(passing),
      "results":[{
        k:r.get(k) for k in [
          "id","taxon_hint","doi","status","native_height_field","row_count",
          "individual_count","repeat_individual_count","passes_gate","reason",
          "taxon_presence_counts"
        ]
      } for r in results],
      "numeric_height_values_parsed":False,
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
