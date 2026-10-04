#!/usr/bin/env python3
"""Outcome-blind Mendeley schema/file inventory for ontogenetic path-dependence v1.

This script is intentionally restricted to public dataset/file METADATA.
It does not download file contents and does not calculate route geometry.
"""
from __future__ import annotations
import json, sys, urllib.parse, urllib.request
from pathlib import Path

BASE = "https://api.data.mendeley.com"
DATASETS = [
    {"label":"source_A_maternal", "id":"gpcg9m5758", "version":1, "doi":"10.17632/gpcg9m5758.1"},
    {"label":"source_B_first_flight", "id":"n9d8gbz3xr", "version":1, "doi":"10.17632/n9d8gbz3xr.1"},
]
OUT = Path("prospective/ontogenetic_path_dependence/schema_inventory_v1.json")

def get_json(url: str):
    req = urllib.request.Request(url, headers={
        "Accept":"application/json, application/vnd.mendeley-public-dataset.1+json",
        "User-Agent":"batter-ontogenetic-path-dependence-schema-preflight/1.0",
    })
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    report = {"contract":"SCHEMA_PREFLIGHT_CONTRACT_V1.md", "outcome_opened":False, "sources":[]}
    for d in DATASETS:
        meta_url = f"{BASE}/datasets/{d['id']}?version={d['version']}"
        files_url = f"{BASE}/datasets/{d['id']}/files?version={d['version']}&$start=0&$limit=100"
        try:
            meta = get_json(meta_url)
            files = get_json(files_url)
            if isinstance(files, dict):
                file_rows = files.get("results") or files.get("items") or files.get("files") or []
            else:
                file_rows = files or []
            slim=[]
            for f in file_rows:
                cd=f.get("content_details") or {}
                slim.append({
                    "id":f.get("id"),
                    "filename":f.get("filename") or f.get("name"),
                    "folder_id":f.get("folder_id"),
                    "size":f.get("size") or cd.get("size"),
                    "content_type":cd.get("content_type") or f.get("content_type"),
                    "sha256_hash":cd.get("sha256_hash"),
                    "description":f.get("description"),
                    # Deliberately omit download_url/view_url.
                })
            report["sources"].append({
                "label":d["label"], "requested_id":d["id"], "doi":d["doi"],
                "resolved_id":meta.get("id") if isinstance(meta,dict) else None,
                "name":meta.get("name") if isinstance(meta,dict) else None,
                "version":meta.get("version") if isinstance(meta,dict) else d["version"],
                "file_count":len(slim), "files":slim, "status":"METADATA_PASS",
            })
        except Exception as e:
            report["sources"].append({
                "label":d["label"], "requested_id":d["id"], "doi":d["doi"],
                "status":"STOP_METADATA_RETRIEVAL", "error":repr(e),
            })
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if any(s["status"].startswith("STOP") for s in report["sources"]):
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
