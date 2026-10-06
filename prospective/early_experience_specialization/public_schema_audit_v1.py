#!/usr/bin/env python3
"""Schema-only audit of the public early-experience Mendeley files.

Uses verified anonymous Mendeley endpoints:
- file inventory JSON;
- per-file download URLs from metadata.

Authorized:
- file names/sizes/types;
- CSV/TSV header only;
- XLSX sheet names/dimensions/header row only;
- MAT variable names/shapes/classes only;
- analysis-code identifiers / quoted column-like strings only.

No research data rows or numeric outcome arrays are reported.
"""

from __future__ import annotations
from pathlib import Path
import json, re, tempfile, urllib.request, urllib.parse, csv

HERE=Path(__file__).resolve().parent
OUT=HERE/"PUBLIC_SCHEMA_AUDIT_V1.json"
OUTMD=HERE/"PUBLIC_SCHEMA_AUDIT_V1.md"

DATASET="wh7c636y3t"
VERSION=1
FILE_URL=(
    f"https://data.mendeley.com/api/datasets/{DATASET}/files?"
    + urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
)
HEADERS={"User-Agent":"Mozilla/5.0 batter-early-experience-schema/1.1","Accept":"application/json,*/*"}

RELEVANT=re.compile(
    r"(bat|id|season|trial|condition|enrich|impover|bold|risk|explor|activ|"
    r"colony|origin|sex|age|gps|distance|outdoor|area|personality)",
    re.I,
)

def get_bytes(url, accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()

def get_json(url):
    return json.loads(get_bytes(url,"application/json").decode("utf-8"))

def rows_from_envelope(data):
    if isinstance(data,list):
        return data
    if isinstance(data,dict):
        for k in ("items","files","results","data"):
            if isinstance(data.get(k),list):
                return data[k]
    raise RuntimeError(f"unrecognized file-list envelope: {type(data)} keys={list(data) if isinstance(data,dict) else None}")

def download_url(row):
    cd=row.get("content_details") or {}
    return cd.get("download_url") or row.get("download_url")

def csv_header(data,name):
    text=data.decode("utf-8-sig","replace")
    first=text.splitlines()[0] if text.splitlines() else ""
    if name.lower().endswith((".tsv",".tab")):
        delim="\t"
    else:
        # sniff only the header line
        try:
            delim=csv.Sniffer().sniff(first,delimiters=",;\t").delimiter
        except Exception:
            delim=","
    try:
        row=next(csv.reader([first],delimiter=delim))
    except Exception:
        row=[first]
    return {"type":"text_table","header":[x.strip() for x in row]}

def xlsx_schema(data):
    import openpyxl
    out={"type":"xlsx","sheets":[]}
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as tf:
        tf.write(data); tf.flush()
        wb=openpyxl.load_workbook(tf.name,read_only=True,data_only=False)
        for ws in wb.worksheets:
            first=next(ws.iter_rows(min_row=1,max_row=1,values_only=True),())
            out["sheets"].append({
                "name":ws.title,
                "max_row":ws.max_row,
                "max_column":ws.max_column,
                "header":[None if v is None else str(v) for v in first],
            })
    return out

def mat_schema(data):
    import scipy.io
    out={"type":"mat","variables":[]}
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data); tf.flush()
        try:
            rows=scipy.io.whosmat(tf.name)
            for var,shape,klass in rows:
                out["variables"].append({"name":var,"shape":list(shape),"class":klass})
        except Exception as e:
            out["error"]=repr(e)
    return out

def code_schema(data,ext):
    text=data.decode("utf-8","replace")
    if ext==".m":
        text=re.sub(r"%[^\n]*","",text)
    elif ext==".r":
        text=re.sub(r"#[^\n]*","",text)
    ids=sorted(set(re.findall(r"\b[A-Za-z][A-Za-z0-9_.]*\b",text)))
    rel_ids=[x for x in ids if RELEVANT.search(x)][:1000]
    strings=sorted(set(re.findall(r'["\']([^"\'\n]{1,160})["\']',text)))
    rel_strings=[x for x in strings if RELEVANT.search(x)][:1000]
    return {"type":"code","relevant_identifiers":rel_ids,"relevant_strings":rel_strings}

def inspect_file(row):
    name=row.get("filename") or row.get("name") or ""
    ext=Path(name).suffix.lower()
    cd=row.get("content_details") or {}
    meta={
        "id":row.get("id"),
        "name":name,
        "size":row.get("size") or cd.get("size"),
        "content_type":row.get("content_type") or cd.get("content_type"),
        "sha256":row.get("sha256_hash") or cd.get("sha256_hash"),
        "schema":None,
    }
    url=download_url(row)
    if not url:
        meta["schema"]={"type":"STOP_NO_DOWNLOAD_URL"}
        return meta
    if ext not in {".csv",".tsv",".txt",".xlsx",".xlsm",".mat",".m",".r",".py"}:
        meta["schema"]={"type":"uninspected"}
        return meta
    data=get_bytes(url)
    try:
        if ext in {".csv",".tsv",".txt"}:
            meta["schema"]=csv_header(data,name)
        elif ext in {".xlsx",".xlsm"}:
            meta["schema"]=xlsx_schema(data)
        elif ext==".mat":
            meta["schema"]=mat_schema(data)
        elif ext in {".m",".r",".py"}:
            meta["schema"]=code_schema(data,ext)
    except Exception as e:
        meta["schema"]={"type":"inspection_error","error":repr(e)}
    return meta

def main():
    envelope=get_json(FILE_URL)
    file_rows=rows_from_envelope(envelope)
    inspected=[inspect_file(x) for x in file_rows if isinstance(x,dict)]

    result={
        "source_file_endpoint":FILE_URL,
        "file_count":len(inspected),
        "files":inspected,
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Early-experience public schema audit v1","",
        "**SCHEMA ONLY — NO RESEARCH DATA ROWS / NUMERIC OUTCOMES REPORTED.**","",
        f"- files: **{len(inspected)}**","",
    ]
    for r in inspected:
        lines += [
            f"## {r['name']}","",
            f"- bytes: {r.get('size')}",
            f"- content type: {r.get('content_type')}",
        ]
        s=r.get("schema") or {}
        typ=s.get("type")
        lines.append(f"- schema type: {typ}")
        if typ=="text_table":
            lines.append(f"- header: {s.get('header')}")
        elif typ=="xlsx":
            for sh in s.get("sheets",[]):
                lines.append(
                    f"- sheet `{sh['name']}`: rows={sh['max_row']} "
                    f"cols={sh['max_column']} header={sh['header']}"
                )
        elif typ=="mat":
            for v in s.get("variables",[]):
                lines.append(f"- MAT `{v['name']}`: shape={v['shape']} class={v['class']}")
            if s.get("error"):
                lines.append(f"- MAT inspection error: {s['error']}")
        elif typ=="code":
            lines.append(f"- relevant identifiers: {s.get('relevant_identifiers')}")
            lines.append(f"- relevant strings: {s.get('relevant_strings')}")
        elif s.get("error"):
            lines.append(f"- error: {s['error']}")
        lines.append("")

    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
