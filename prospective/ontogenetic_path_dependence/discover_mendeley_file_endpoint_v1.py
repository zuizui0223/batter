#!/usr/bin/env python3
"""Discover anonymous Mendeley file-list endpoint from public frontend bundles.

Metadata/network-contract discovery only. Never follows dataset file download links.
"""
from __future__ import annotations
import html, re, urllib.parse, urllib.request

UA="batter-mendeley-endpoint-discovery/1.0"
PAGE="https://data.mendeley.com/datasets/gpcg9m5758/1"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/javascript,*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return r.read().decode("utf-8",errors="replace")

page=get(PAGE)
srcs=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',page,re.I)
srcs=[urllib.parse.urljoin(PAGE,html.unescape(s)) for s in srcs]
print("SCRIPT_COUNT",len(srcs))
seen=set()
for n,url in enumerate(srcs[:40],1):
    try:
        txt=get(url)
    except Exception as e:
        print("SCRIPT_FAIL",n,url,repr(e)); continue
    candidates=[]
    pats=[
        r'https?://[^"\'\s)]+',
        r'["\']([^"\']*(?:datasets|files|folders)[^"\']*)["\']',
    ]
    for pat in pats:
        for m in re.finditer(pat,txt,re.I):
            val=m.group(1) if m.lastindex else m.group(0)
            if any(k in val.lower() for k in ["files","folders","api.data.mendeley","/datasets"]):
                val=val[:500]
                if val not in seen:
                    seen.add(val); candidates.append(val)
    if candidates:
        print("\nBUNDLE",n,url,"bytes",len(txt))
        for c in candidates[:80]:
            print("CAND",c)
print("\nTOTAL_CANDIDATES",len(seen))
