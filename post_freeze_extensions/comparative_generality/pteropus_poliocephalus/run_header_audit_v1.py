#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from remotezip import RemoteZip

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/header_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/header_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/HEADER_RESULT_V1.md"

UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/141 Safari/537.36"}

def norm(x):
    return re.sub(r"[^a-z0-9]+","_",str(x).strip().lower()).strip("_")

def header_from_bytes(b):
    text=b.decode("utf-8-sig",errors="replace")
    line=text.splitlines()[0] if text.splitlines() else ""
    if not line:
        return []
    delim="\t" if "\t" in line and line.count("\t")>=line.count(",") else ","
    return [x.strip() for x in next(csv.reader([line],delimiter=delim))]

def stream_header(session,url):
    headers={**UA,"Range":"bytes=0-65535","Accept":"text/csv,text/tab-separated-values,text/plain,application/octet-stream,*/*"}
    r=session.get(url,headers=headers,timeout=120,allow_redirects=True,stream=True)
    status=r.status_code
    ctype=r.headers.get("content-type","")
    data=b""
    if status in (200,206):
        for chunk in r.iter_content(chunk_size=4096):
            data+=chunk
            if b"\n" in data or len(data)>=65536:
                break
    return {
        "url":url,"final_url":r.url,"status":status,"content_type":ctype,
        "header":header_from_bytes(data) if data else []
    }

def classify_header(cols,c):
    n={norm(x):x for x in cols}
    groups={}
    for g,opts in c["required_event_header_groups"].items():
        matches=[n[norm(x)] for x in opts if norm(x) in n]
        groups[g]=matches
    v=[n[norm(x)] for x in c["accepted_native_vertical_names"] if norm(x) in n]
    is_event=all(groups[g] for g in ["individual","timestamp","longitude","latitude"])
    return {"event_groups":groups,"vertical_matches":v,"event_header":is_event,"pass_header":bool(is_event and v)}

def main():
    c=json.loads(CONTRACT.read_text())
    session=requests.Session()
    session.headers.update(UA)

    doi_url="https://doi.org/"+c["source"]["doi"]
    rr=session.get(doi_url,timeout=120,allow_redirects=True)
    landing={
        "doi_url":doi_url,
        "status":rr.status_code,
        "final_url":rr.url,
        "content_type":rr.headers.get("content-type",""),
    }
    rr.raise_for_status()
    html=rr.text

    soup=BeautifulSoup(html,"html.parser")
    raw_links=[]
    for a in soup.find_all("a",href=True):
        href=urljoin(rr.url,a["href"])
        txt=a.get_text(" ",strip=True)
        raw_links.append({"href":href,"text":txt})

    # Also capture DSpace-style bitstream/content links embedded outside <a>.
    regex_urls=re.findall(r'https?://[^"\'<>\s]+',html)
    for u in regex_urls:
        if any(k in u.lower() for k in ["bitstream","bitstreams","download","content"]):
            raw_links.append({"href":u.replace("&amp;","&"),"text":""})

    # Unique likely file links.
    seen=set(); candidates=[]
    for x in raw_links:
        u=x["href"]
        if u in seen: continue
        seen.add(u)
        low=(u+" "+x["text"]).lower()
        if any(k in low for k in [".csv",".tsv",".zip","bitstream","bitstreams","download","content"]):
            candidates.append(x)

    direct_results=[]
    zip_results=[]
    for x in candidates[:80]:
        u=x["href"]
        low=(u+" "+x["text"]).lower()
        if ".zip" in low:
            try:
                with RemoteZip(u,headers=UA) as rz:
                    names=rz.namelist()
                    members=[n for n in names if n.lower().endswith((".csv",".tsv",".txt"))]
                    member_out=[]
                    for name in members[:50]:
                        with rz.open(name) as fh:
                            data=b""
                            while len(data)<65536:
                                chunk=fh.read(4096)
                                if not chunk: break
                                data+=chunk
                                if b"\n" in data: break
                        cols=header_from_bytes(data)
                        member_out.append({"member":name,"header":cols,"classification":classify_header(cols,c)})
                    zip_results.append({"url":u,"members":members,"member_headers":member_out})
            except Exception as e:
                zip_results.append({"url":u,"error":repr(e)})
        else:
            # Only touch file-like/bitstream links. Landing/navigation pages will produce non-event headers and are harmless.
            try:
                res=stream_header(session,u)
                res["text_hint"]=x["text"]
                res["classification"]=classify_header(res["header"],c)
                direct_results.append(res)
            except Exception as e:
                direct_results.append({"url":u,"text_hint":x["text"],"error":repr(e)})

    passing=[]
    for x in direct_results:
        if x.get("classification",{}).get("pass_header"):
            passing.append({"type":"direct","url":x.get("final_url") or x["url"],"header":x["header"],"classification":x["classification"]})
    for z in zip_results:
        for m in z.get("member_headers",[]):
            if m.get("classification",{}).get("pass_header"):
                passing.append({"type":"zip_member","url":z["url"],"member":m["member"],"header":m["header"],"classification":m["classification"]})

    event_no_vertical=[]
    for x in direct_results:
        cl=x.get("classification",{})
        if cl.get("event_header") and not cl.get("vertical_matches"):
            event_no_vertical.append({"type":"direct","url":x.get("final_url") or x["url"],"header":x.get("header",[])})
    for z in zip_results:
        for m in z.get("member_headers",[]):
            cl=m.get("classification",{})
            if cl.get("event_header") and not cl.get("vertical_matches"):
                event_no_vertical.append({"type":"zip_member","url":z["url"],"member":m["member"],"header":m.get("header",[])})

    if passing:
        decision="PASS_TO_STRUCTURAL_PREFLIGHT"
    elif event_no_vertical:
        decision="REJECT_NO_VERTICAL_RESPONSE"
    elif direct_results or zip_results:
        decision="PENDING_ACCESS_OR_UNIDENTIFIED_EVENT_FILE"
    else:
        decision="PENDING_ACCESS"

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_event_rows_read":False,
        "numeric_vertical_values_read":False,
        "landing":landing,
        "candidate_link_count":len(candidates),
        "candidate_links":candidates,
        "direct_header_results":direct_results,
        "zip_header_results":zip_results,
        "passing_event_headers":passing,
        "event_headers_without_vertical":event_no_vertical,
        "decision":decision,
        "claim_boundary":c["claim_boundary"],
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Pteropus poliocephalus outcome-blind header audit v1","",
        "**No numeric event row and no vertical value was parsed.**","",
        f"- DOI landing status: **{landing['status']}**",
        f"- resolved landing: `{landing['final_url']}`",
        f"- likely file/bitstream links inspected: **{len(candidates)}**",
        f"- event headers with accepted native vertical field: **{len(passing)}**",
        f"- event headers without accepted vertical field: **{len(event_no_vertical)}**",
        f"- decision: **{decision}**",""
    ]
    if passing:
        lines += ["## Passing headers",""]
        for p in passing:
            where=p.get("member") or p.get("url")
            lines.append(f"- `{where}`: {', '.join(p['header'])}")
    elif event_no_vertical:
        lines += ["## Event headers lacking vertical response",""]
        for p in event_no_vertical:
            where=p.get("member") or p.get("url")
            lines.append(f"- `{where}`: {', '.join(p['header'])}")
    else:
        lines += ["No qualifying event header was established from the public repository surface.",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "landing":landing,
        "candidate_link_count":len(candidates),
        "passing_headers":[{"type":x["type"],"member":x.get("member"),"url":x.get("url"),"vertical":x["classification"]["vertical_matches"]} for x in passing],
        "event_no_vertical_count":len(event_no_vertical),
        "decision":decision
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
