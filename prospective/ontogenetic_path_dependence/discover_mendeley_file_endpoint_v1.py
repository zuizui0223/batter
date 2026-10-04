#!/usr/bin/env python3
"""Discover anonymous Mendeley file-list endpoint from public frontend bundles.

Metadata/network-contract discovery only. Never follows dataset file download links.
"""
from __future__ import annotations
import html, re, urllib.parse, urllib.request

UA="batter-mendeley-endpoint-discovery/1.1"
PAGE="https://data.mendeley.com/datasets/gpcg9m5758/1"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,application/javascript,*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return r.read().decode("utf-8",errors="replace")

page=get(PAGE)
for m in re.finditer(r'publicApiBaseUrl',page):
    print("PAGE_CONFIG",re.sub(r"\s+"," ",page[max(0,m.start()-300):m.start()+500])[:900])

srcs=re.findall(r'<script[^>]+src=["\']([^"\']+)["\']',page,re.I)
srcs=[urllib.parse.urljoin(PAGE,html.unescape(s)) for s in srcs]
print("SCRIPT_COUNT",len(srcs))
hits=0
for n,url in enumerate(srcs[:60],1):
    try:
        txt=get(url)
    except Exception as e:
        print("SCRIPT_FAIL",n,url,repr(e)); continue

    contexts=[]
    # Exact network-contract patterns likely used by file/folder loaders.
    patterns=[
        r'publicApiBaseUrl.{0,900}files',
        r'files.{0,900}publicApiBaseUrl',
        r'apiBaseUrl.{0,900}files',
        r'files.{0,900}apiBaseUrl',
        r'datasets.{0,300}/files',
        r'/files.{0,300}version',
        r'fetchFiles.{0,1200}',
        r'folders.{0,600}allowAnonymous',
    ]
    for pat in patterns:
        for m in re.finditer(pat,txt,re.I|re.S):
            c=txt[max(0,m.start()-500):min(len(txt),m.end()+500)]
            c=re.sub(r"\s+"," ",c)
            if c not in contexts:
                contexts.append(c[:2200])
    if contexts:
        hits+=1
        print("\nBUNDLE",n,url,"bytes",len(txt))
        for c in contexts[:30]:
            print("CTX",c)
print("\nBUNDLES_WITH_FILE_ENDPOINT_CONTEXT",hits)
