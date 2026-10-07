#!/usr/bin/env python3
"""Probe candidate Mendeley public API bases without opening research values.

Records status, redirects, content type and byte length only.
"""

from pathlib import Path
import json, urllib.request, urllib.error

HERE=Path(__file__).resolve().parent
OUT=HERE/"MENDELEY_API_BASE_PROBE_V1.json"
OUTMD=HERE/"MENDELEY_API_BASE_PROBE_V1.md"

DATASET="wh7c636y3t"
VERSION=1

BASES=[
    "https://data.mendeley.com/api/datasets-v2",
    "https://data.mendeley.com/api/datasets",
    "https://data.mendeley.com/api",
    "https://api.data.mendeley.com",
    "https://api.data.mendeley.com/datasets-v2",
]

PATHS=[
    f"/datasets/{DATASET}/snapshot/{VERSION}",
    f"/datasets/{DATASET}/files?version={VERSION}&%24start=0&%24limit=1000",
    f"/datasets/{DATASET}/zip?version={VERSION}",
    f"/{DATASET}/snapshot/{VERSION}",
    f"/{DATASET}/files?version={VERSION}&%24start=0&%24limit=1000",
    f"/{DATASET}/zip?version={VERSION}",
]

def probe(url):
    req=urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent":"Mozilla/5.0 batter-public-api-probe/1.0",
            "Accept":"application/json, application/zip, */*",
        },
    )
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            # Read at most 1 byte: only verifies body presence, does not inspect values.
            b=r.read(1)
            return {
                "requested_url":url,
                "final_url":r.geturl(),
                "status":r.status,
                "content_type":r.headers.get("content-type"),
                "content_length":r.headers.get("content-length"),
                "body_present":bool(b),
            }
    except urllib.error.HTTPError as e:
        return {
            "requested_url":url,
            "final_url":e.geturl(),
            "status":e.code,
            "content_type":e.headers.get("content-type") if e.headers else None,
            "content_length":e.headers.get("content-length") if e.headers else None,
        }
    except Exception as e:
        return {"requested_url":url,"error":repr(e)}

def main():
    rows=[]
    for base in BASES:
        for path in PATHS:
            rows.append(probe(base+path))
    OUT.write_text(json.dumps({"rows":rows},indent=2)+"\n")
    lines=[
        "# Mendeley API base probe v1","",
        "**TRANSPORT METADATA ONLY — NO RESEARCH VALUES OPENED.**","",
        "| status | content type | requested | final |",
        "|---:|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.get('status','ERR')} | {r.get('content_type')} | "
            f"{r['requested_url']} | {r.get('final_url') or r.get('error')} |"
        )
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
