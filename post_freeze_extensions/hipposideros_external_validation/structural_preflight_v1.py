#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, re
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/hipposideros_external_validation/structural_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/hipposideros_external_validation/structural_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/hipposideros_external_validation/STRUCTURAL_RESULT_V1.md"
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def resolve_file(c,session):
    r=session.get(c["source"]["landing_url"],headers=UA,timeout=90)
    r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser")
    target=None
    for a in soup.find_all("a"):
        if a.get_text(" ",strip=True)==c["source"]["file"]:
            target=a.get("href"); break
    if not target:
        # fallback: any href whose visible/file text contains the exact frozen file name
        for a in soup.find_all("a",href=True):
            if c["source"]["file"] in (a.get_text(" ",strip=True) or "") or c["source"]["file"] in a["href"]:
                target=a["href"]; break
    if not target:
        raise RuntimeError("could not resolve frozen Dryad file link without opening file contents")
    return urljoin(c["source"]["landing_url"],target)

def main():
    c=json.loads(CONTRACT.read_text())
    session=requests.Session()
    session.headers.update({**UA,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
    url=resolve_file(c,session)
    headers={**UA,"Referer":c["source"]["landing_url"],"Accept":"text/csv,text/plain,*/*"}
    candidates=[url]
    m=re.search(r"/file_stream/(\d+)",url)
    if m:
        fid=m.group(1)
        candidates += [
            f"https://datadryad.org/stash/downloads/file_stream/{fid}",
            f"https://datadryad.org/api/v2/files/{fid}/download",
            f"https://datadryad.org/api/v2/files/{fid}/content",
        ]
    raw=None
    attempts=[]
    for u in candidates:
        rr=session.get(u,headers=headers,timeout=180,allow_redirects=True)
        ctype=rr.headers.get("content-type","")
        first_line=rr.content[:4096].decode("utf-8",errors="ignore").splitlines()[0] if rr.content else ""
        header_ok=all(x in first_line for x in ["id","timestamp","longitude","latitude","height"])
        attempts.append({"url":u,"status":rr.status_code,"content_type":ctype,"csv_header_ok":header_ok})
        if rr.status_code==200 and len(rr.content)>1000 and header_ok:
            raw=rr.content
            break
    if raw is None:
        raise RuntimeError(f"no public Dryad download route succeeded: {attempts}")
    sha=hashlib.sha256(raw).hexdigest()

    df=pd.read_csv(io.BytesIO(raw),dtype=str,low_memory=False)
    f=c["fields_expected"]
    req=[f["individual"],f["timestamp"],f["longitude"],f["latitude"],f["vertical_presence_only"]]
    missing=[x for x in req if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing expected fields: {missing}")

    mask=pd.Series(True,index=df.index)
    for col in req:
        mask &= present(df[col])
    d=df.loc[mask,req].copy()

    # Height remains an unopened string throughout this structural script.
    if pd.api.types.is_numeric_dtype(d[f["vertical_presence_only"]]):
        raise RuntimeError("height unexpectedly coerced numeric")

    d["t"]=pd.to_datetime(d[f["timestamp"]],errors="coerce")
    if d["t"].isna().any():
        raise RuntimeError(f"timestamp parse failures: {int(d['t'].isna().sum())}")

    non_midnight=bool(((d["t"].dt.hour!=0)|(d["t"].dt.minute!=0)|(d["t"].dt.second!=0)).any())
    if non_midnight:
        d["session_date"]=(d["t"]-pd.Timedelta(hours=12)).dt.date.astype(str)
        session_rule_used="timestamp_minus_12h_then_date"
    else:
        d["session_date"]=d["t"].dt.date.astype(str)
        session_rule_used="raw_calendar_date"

    iid=f["individual"]
    counts=(d.groupby([iid,"session_date"],sort=True).size().rename("n").reset_index())
    minfix=int(c["structural_gate"]["minimum_presence_qualified_fixes_per_session"])
    qual=counts[counts["n"]>=minfix].copy()

    per_ind=[]
    for bat,g in counts.groupby(iid,sort=True):
        q=qual[qual[iid]==bat]
        per_ind.append({
            "id":str(bat),
            "id_prefix":re.match(r"^[A-Za-z]+",str(bat)).group(0) if re.match(r"^[A-Za-z]+",str(bat)) else "",
            "total_presence_qualified_rows":int(g["n"].sum()),
            "candidate_nights":int(len(g)),
            "nights_ge50":int(len(q)),
            "max_rows_in_night":int(g["n"].max()),
            "repeat_eligible":bool(len(q)>=2)
        })

    repeat=[x for x in per_ind if x["repeat_eligible"]]
    prefix_counts={}
    for x in per_ind:
        prefix_counts.setdefault(x["id_prefix"],0)
        prefix_counts[x["id_prefix"]]+=1

    gate=len(repeat)>=int(c["structural_gate"]["minimum_repeat_individuals_total"])
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_height_values_read":False,
        "raw_file_sha256":sha,
        "raw_file_size_bytes":len(raw),
        "rows_total":int(len(df)),
        "rows_presence_qualified":int(len(d)),
        "columns":list(df.columns),
        "timestamp_has_time_of_day":non_midnight,
        "session_rule_used":session_rule_used,
        "individual_count":int(d[iid].nunique()),
        "id_prefix_counts":prefix_counts,
        "qualified_nights_ge50":int(len(qual)),
        "repeat_eligible_individual_count":int(len(repeat)),
        "repeat_eligible_ids":[x["id"] for x in repeat],
        "per_individual_structure":per_ind,
        "gate":{
            "required_repeat_individuals":int(c["structural_gate"]["minimum_repeat_individuals_total"]),
            "observed_repeat_individuals":int(len(repeat)),
            "pass":bool(gate)
        },
        "species_mapping_status":"UNRESOLVED_OUTCOME_BLIND",
        "next_step":"resolve ID-to-species mapping without numeric height; only then freeze full vertical-validation contract" if gate else "STOP; do not lower >=50-fix threshold in this prospective family"
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Hipposideros outcome-blind structural gate v1","",
        "**Numeric height magnitudes were not parsed or summarized.**","",
        f"- raw SHA256: `{sha}`",
        f"- rows: **{len(df)}** total; **{len(d)}** presence-qualified",
        f"- individuals: **{d[iid].nunique()}**",
        f"- session rule: **{session_rule_used}**",
        f"- >=50-fix nights: **{len(qual)}**",
        f"- repeat-eligible individuals (>=2 such nights): **{len(repeat)}**",
        f"- structural gate: **{'PASS' if gate else 'FAIL'}**","",
        "## Individual structural counts","",
        "| id | prefix | candidate nights | nights >=50 | max rows/night | repeat eligible |",
        "|---|---|---:|---:|---:|---|"
    ]
    for x in per_ind:
        lines.append(f"| {x['id']} | {x['id_prefix']} | {x['candidate_nights']} | {x['nights_ge50']} | {x['max_rows_in_night']} | {'yes' if x['repeat_eligible'] else 'no'} |")
    lines += ["","Species mapping remains unresolved and must be fixed outcome-blind before any numeric height is opened.",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({"gate":payload["gate"],"repeat_ids":payload["repeat_eligible_ids"],"prefix_counts":prefix_counts,"session_rule":session_rule_used,"sha256":sha},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
