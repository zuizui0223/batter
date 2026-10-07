#!/usr/bin/env python3
"""Discover Mendeley internal public file/download endpoint strings from frontend JS.

No research-data values are accessed.
"""

from __future__ import annotations
import json, re, pathlib, urllib.request
from urllib.parse import urljoin

HERE=pathlib.Path(__file__).resolve().parent
OUT=HERE/"MENDELEY_BUNDLE_DISCOVERY_V1.json"
OUTMD=HERE/"MENDELEY_BUNDLE_DISCOVERY_V1.md"

PAGE="https://data.mendeley.com/datasets/wh7c636y3t/1"
BASE="https://data.mendeley.com"

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read().decode("utf-8","replace")

def main():
    html=fetch(PAGE)
    bundles=sorted(set(re.findall(r'["\']([^"\']*bundle\.js\?[^"\']+)["\']',html)))
    if not bundles:
        raise SystemExit("STOP: no bundle.js reference found")
    urls=[urljoin(BASE,x) for x in bundles]

    result={"page":PAGE,"bundles":[]}
    tokens=[
        r"/api/[^\"'\s]{1,180}",
        r"/datasets/[^\"'\s]{1,180}",
        r"public-files[^\"'\s]{0,180}",
        r"download[^\"'\s]{0,180}",
        r"files[^\"'\s]{0,180}",
        r"dataset[^\"'\s]{0,180}",
    ]

    for url in urls:
        js=fetch(url)
        hits=[]
        for pat in tokens:
            hits.extend(re.findall(pat,js,re.I))
        # collect quoted strings mentioning likely endpoint semantics
        quoted=re.findall(r'["\']([^"\']{1,240})["\']',js)
        relevant=[
            x for x in quoted
            if re.search(r"(download|public-files|/files|files\?|datasets/public|dataset-files|bundle)",x,re.I)
        ]
        result["bundles"].append({
            "url":url,
            "chars":len(js),
            "regex_hits":sorted(set(hits))[:2000],
            "relevant_strings":sorted(set(relevant))[:2000],
        })

    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Mendeley bundle endpoint discovery v1","",
        "**FRONTEND-STRUCTURE ONLY — NO RESEARCH VALUES OPENED.**","",
    ]
    for b in result["bundles"]:
        lines += [f"## {b['url']}","",f"- JS chars: {b['chars']}","",
                  "### Relevant endpoint strings",""]
        for x in b["relevant_strings"][:500]:
            lines.append(f"- `{x}`")
        lines += ["","### Regex endpoint fragments",""]
        for x in b["regex_hits"][:500]:
            lines.append(f"- `{x}`")
        lines.append("")
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
