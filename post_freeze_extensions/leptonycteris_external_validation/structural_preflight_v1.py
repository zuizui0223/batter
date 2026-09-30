#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, re
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/leptonycteris_external_validation/structural_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/leptonycteris_external_validation/structural_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/leptonycteris_external_validation/STRUCTURAL_RESULT_V1.md"
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def resolve_file(c,session):
    r=session.get(c["source"]["landing_url"],headers=UA,timeout=90)
    r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    target=None
    for a in soup.find_all("a",href=True):
        txt=a.get_text(" ",strip=True)
        if txt==c["source"]["file"] or c["source"]["file"] in a["href"]:
            target=a["href"]; break
    if not target:
        raise RuntimeError("could not resolve frozen Dryad file link")
    return urljoin(c["source"]["landing_url"],target)

def download_public(c):
    session=requests.Session()
    session.headers.update({**UA,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
    url=resolve_file(c,session)
    headers={**UA,"Referer":c["source"]["landing_url"],"Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"}
    candidates=[url]
    m=re.search(r"/file_stream/(\d+)",url)
    if m:
        fid=m.group(1)
        candidates += [
            f"https://datadryad.org/stash/downloads/file_stream/{fid}",
            f"https://datadryad.org/api/v2/files/{fid}/download",
            f"https://datadryad.org/api/v2/files/{fid}/content",
        ]
    attempts=[]
    for u in candidates:
        rr=session.get(u,headers=headers,timeout=180,allow_redirects=True)
        ctype=rr.headers.get("content-type","")
        xlsx_magic=rr.content.startswith(b"PK\\x03\\x04")
        attempts.append({"url":u,"status":rr.status_code,"content_type":ctype,"xlsx_magic":xlsx_magic})
        if rr.status_code==200 and len(rr.content)>1000 and xlsx_magic:
            return rr.content,attempts
    raise RuntimeError(f"no public Dryad download route succeeded: {attempts}")

def main():
    c=json.loads(CONTRACT.read_text())
    raw,attempts=download_public(c)
    sha=hashlib.sha256(raw).hexdigest()

    f=c["fields_expected"]
    nonvertical=[f["individual"],f["timestamp"],f["longitude"],f["latitude"]]

    # Header-only read may verify that the vertical field exists, but its values are excluded.
    header=pd.read_excel(io.BytesIO(raw),nrows=0,engine="openpyxl")
    missing=[x for x in nonvertical+[f["vertical_field"]] if x not in header.columns]
    if missing:
        raise RuntimeError(f"missing expected columns: {missing}")

    df=pd.read_excel(
        io.BytesIO(raw),
        usecols=nonvertical,
        dtype=str,
        engine="openpyxl"
    )
    if f["vertical_field"] in df.columns:
        raise RuntimeError("vertical column unexpectedly loaded")

    mask=pd.Series(True,index=df.index)
    for col in nonvertical:
        mask &= present(df[col])
    d=df.loc[mask,nonvertical].copy()

    d["t"]=pd.to_datetime(d[f["timestamp"]],errors="coerce")
    d=d[d["t"].notna()].copy()
    d["session_date"]=d["t"].dt.date.astype(str)

    iid=f["individual"]
    counts=(d.groupby([iid,"session_date"],sort=True).size().rename("n").reset_index())
    minfix=int(c["structural_gate"]["minimum_nonvertical_valid_fixes_per_session"])
    qual=counts[counts["n"]>=minfix].copy()

    per_ind=[]
    for bat,g in counts.groupby(iid,sort=True):
        q=qual[qual[iid]==bat]
        per_ind.append({
            "id":str(bat),
            "candidate_nights":int(len(g)),
            "nights_ge50":int(len(q)),
            "max_rows_in_night":int(g["n"].max()),
            "total_nonvertical_valid_rows":int(g["n"].sum()),
            "repeat_eligible":bool(len(q)>=2)
        })
    repeat=[x for x in per_ind if x["repeat_eligible"]]
    required=int(c["structural_gate"]["minimum_repeat_individuals_total"])
    passed=len(repeat)>=required

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_vertical_values_read":False,
        "vertical_field_verified_by_header_only":True,
        "raw_file_sha256":sha,
        "raw_file_size_bytes":len(raw),
        "download_attempts":attempts,
        "rows_nonvertical_valid":int(len(d)),
        "individual_count":int(d[iid].nunique()),
        "qualified_nights_ge50":int(len(qual)),
        "repeat_eligible_individual_count":int(len(repeat)),
        "repeat_eligible_ids":[x["id"] for x in repeat],
        "per_individual_structure":per_ind,
        "gate":{
            "required_repeat_individuals":required,
            "observed_repeat_individuals":int(len(repeat)),
            "pass":bool(passed)
        },
        "next_step":"freeze complete vertical-validation contract before reading any Altitude values" if passed else "STOP; do not lower structural threshold"
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Leptonycteris outcome-blind structural gate v1","",
        "**Numeric Altitude values were not read. The vertical field was checked by header only.**","",
        f"- raw SHA256: `{sha}`",
        f"- nonvertical-valid rows: **{len(d)}**",
        f"- Tag IDs: **{d[iid].nunique()}**",
        f"- >=50-fix nights: **{len(qual)}**",
        f"- repeat-eligible Tag IDs (>=2 such nights): **{len(repeat)}**",
        f"- structural gate: **{'PASS' if passed else 'FAIL'}**","",
        "| Tag ID | candidate nights | nights >=50 | max rows/night | repeat eligible |",
        "|---|---:|---:|---:|---|"
    ]
    for x in per_ind:
        lines.append(f"| {x['id']} | {x['candidate_nights']} | {x['nights_ge50']} | {x['max_rows_in_night']} | {'yes' if x['repeat_eligible'] else 'no'} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({"gate":payload["gate"],"repeat_ids":payload["repeat_eligible_ids"],"sha256":sha},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
