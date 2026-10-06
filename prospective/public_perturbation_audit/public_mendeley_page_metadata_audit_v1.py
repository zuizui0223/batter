#!/usr/bin/env python3
"""Outcome-blind scraper for public Mendeley landing-page file metadata.

Reads only public HTML/embedded JSON/link metadata. Does not download research files.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import urllib.request
from html.parser import HTMLParser

HERE=pathlib.Path(__file__).resolve().parent
OUT_JSON=HERE/"PUBLIC_PAGE_METADATA_AUDIT_V1.json"
OUT_MD=HERE/"PUBLIC_PAGE_METADATA_AUDIT_V1.md"

SOURCES=[
    {"key":"aharon2017","url":"https://data.mendeley.com/datasets/f6mvhj5gj9/3"},
    {"key":"ma2025","url":"https://data.mendeley.com/datasets/964fv73w94/1"},
]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.scripts=[]
        self._in_script=False
        self._script_attrs={}
        self._buf=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="a" and d.get("href"):
            self.links.append({"href":d.get("href"),"download":d.get("download")})
        if tag=="script":
            self._in_script=True; self._script_attrs=d; self._buf=[]
    def handle_data(self,data):
        if self._in_script:self._buf.append(data)
    def handle_endtag(self,tag):
        if tag=="script" and self._in_script:
            self.scripts.append({"attrs":self._script_attrs,"text":"".join(self._buf)})
            self._in_script=False; self._script_attrs={}; self._buf=[]

def fetch(url):
    req=urllib.request.Request(url,headers={
        "User-Agent":"Mozilla/5.0 batter-public-page-audit/1.0",
        "Accept":"text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req,timeout=60) as r:
        return r.read().decode("utf-8","replace"),r.geturl(),r.status

def walk_json(obj,path="",out=None):
    if out is None: out=[]
    if isinstance(obj,dict):
        keys=set(obj)
        fileish=keys & {"filename","fileName","name","download_url","downloadUrl","view_url","content_type","contentType","size","sha256_hash","sha256","id"}
        vals=" ".join(str(obj.get(k,"")) for k in ("filename","fileName","name","download_url","downloadUrl"))
        if fileish and re.search(r"(\.mat|\.m\b|\.xlsx|\.xlsm|\.csv|\.zip|\.txt|file|download)",vals,re.I):
            safe={}
            for k in ("id","filename","fileName","name","size","content_type","contentType","sha256_hash","sha256","download_url","downloadUrl","view_url"):
                if k in obj and isinstance(obj[k],(str,int,float,type(None))):
                    safe[k]=obj[k]
            out.append({"path":path,"record":safe})
        for k,v in obj.items():
            walk_json(v,f"{path}/{k}",out)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            walk_json(v,f"{path}/{i}",out)
    return out

def audit(src):
    text,final,status=fetch(src["url"])
    p=Parser(); p.feed(text)
    links=[]
    for x in p.links:
        href=html.unescape(x["href"])
        if re.search(r"(download|public-files|\.mat(?:\?|$)|\.m(?:\?|$)|\.xlsx|\.csv|\.zip)",href,re.I):
            links.append(href)
    embedded=[]
    json_blocks=[]
    for s in p.scripts:
        t=s["text"].strip()
        typ=(s["attrs"].get("type") or "").lower()
        sid=s["attrs"].get("id")
        if not t: continue
        if typ=="application/json" or sid=="__NEXT_DATA__" or (t.startswith("{") and t.endswith("}")):
            try:
                obj=json.loads(t)
                recs=walk_json(obj)
                if recs:
                    embedded.extend(recs)
                json_blocks.append({"id":sid,"type":typ,"top_type":type(obj).__name__,"file_records":len(recs)})
            except Exception:
                pass
    # As a last structural fallback, collect filename-like literals from HTML.
    filename_literals=sorted(set(re.findall(
        r"[^\"'<>/\\]{1,140}\.(?:mat|m|xlsx|xlsm|csv|zip|txt)",
        text,re.I
    )))
    return {
        "key":src["key"],"requested_url":src["url"],"final_url":final,"http_status":status,
        "html_bytes":len(text.encode("utf-8")),
        "fileish_links":sorted(set(links)),
        "embedded_file_records":embedded,
        "json_blocks":json_blocks,
        "filename_literals":filename_literals[:500],
    }

def render(res):
    lines=["# Public Mendeley landing-page metadata audit v1","","## Status","",
           "**OUTCOME-BLIND PUBLIC PAGE STRUCTURE ONLY.**",""]
    for s in res["sources"]:
        lines += [
            f"## {s['key']}","",
            f"- HTTP: {s['http_status']}",
            f"- final URL: {s['final_url']}",
            f"- HTML bytes: {s['html_bytes']}",
            f"- file-like links: {len(s['fileish_links'])}",
            f"- embedded file records: {len(s['embedded_file_records'])}",
            f"- filename literals: {len(s['filename_literals'])}",""
        ]
        if s["filename_literals"]:
            lines += ["### Filename literals",""]
            lines += [f"- `{x}`" for x in s["filename_literals"]]
            lines.append("")
        if s["fileish_links"]:
            lines += ["### File/download links",""]
            lines += [f"- {x}" for x in s["fileish_links"][:200]]
            lines.append("")
        if s["embedded_file_records"]:
            lines += ["### Embedded file records",""]
            for x in s["embedded_file_records"][:200]:
                lines.append(f"- {x}")
            lines.append("")
    lines += ["## Boundary","","No research file content or numeric biological outcome was opened.",""]
    return "\n".join(lines)

def main():
    res={"audit_version":1,"sources":[]}
    for s in SOURCES:
        try: res["sources"].append(audit(s))
        except Exception as e: res["sources"].append({"key":s["key"],"error":repr(e),"fileish_links":[],"embedded_file_records":[],"filename_literals":[]})
    OUT_JSON.write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\n")
    OUT_MD.write_text(render(res)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
