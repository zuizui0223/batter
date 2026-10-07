#!/usr/bin/env python3
"""Schema-only inspection of PLOS S1 Data for crowd vocal learning.

No numeric acoustic outcome values are emitted.
"""

from __future__ import annotations
from io import BytesIO
from pathlib import Path
import json, re
import openpyxl

HERE=Path(__file__).resolve().parent
OUT=HERE/"S1_SCHEMA_AUDIT_V1.json"
OUTMD=HERE/"S1_SCHEMA_AUDIT_V1.md"

LOCAL=Path(__file__).resolve().parent/"S1_Data.xlsx"

KEY=re.compile(r"(pup|bat|individual|id|group|playback|sex|session|age|week|LD1|LD2|Fig.?2)",re.I)

def fetch():
    if not LOCAL.exists():
        raise RuntimeError(f"local S1_Data.xlsx missing: {LOCAL}")
    data=LOCAL.read_bytes()
    if data[:2] != b"PK":
        raise RuntimeError(f"not XLSX magic: {data[:16]!r}")
    return data,"workflow-curl-local"

def is_id_like_header(x):
    return isinstance(x,str) and bool(re.search(r"(pup|bat|individual|id|group|playback|sex|session|age|week)",x,re.I))

def main():
    data,source_url=fetch()
    wb=openpyxl.load_workbook(BytesIO(data),read_only=True,data_only=False)

    sheets=[]
    for ws in wb.worksheets:
        # Collect all string labels with coordinates. These are structural.
        labels=[]
        for row in ws.iter_rows():
            for cell in row:
                v=cell.value
                if isinstance(v,str) and v.strip():
                    labels.append({"cell":cell.coordinate,"value":v.strip()})

        # Search first 25 rows for likely header cells.
        header_candidates=[]
        for row in ws.iter_rows(min_row=1,max_row=min(25,ws.max_row)):
            vals=[c.value for c in row]
            if any(is_id_like_header(v) or (isinstance(v,str) and re.search(r"LD1|LD2|Fig.?2",v,re.I)) for v in vals):
                header_candidates.append({
                    "row":row[0].row,
                    "strings":[None if not isinstance(v,str) else v for v in vals],
                })

        # Structural ID/group/session values are allowed only in columns with explicit structural headers.
        structural_columns=[]
        for cand in header_candidates:
            r=cand["row"]
            for col,v in enumerate(cand["strings"],start=1):
                if is_id_like_header(v):
                    structural_columns.append({"header_row":r,"col":col,"header":v})

        structural_values={}
        for spec in structural_columns:
            key=f"{spec['header']}@R{spec['header_row']}C{spec['col']}"
            vals=[]
            for rr in range(spec["header_row"]+1,ws.max_row+1):
                v=ws.cell(rr,spec["col"]).value
                if v is None: continue
                # IDs/treatment/session labels only, no coordinate columns.
                if isinstance(v,(str,int)):
                    vals.append(str(v))
                elif isinstance(v,float) and v.is_integer():
                    vals.append(str(int(v)))
            structural_values[key]=sorted(set(vals))[:200]

        sheets.append({
            "name":ws.title,
            "max_row":ws.max_row,
            "max_column":ws.max_column,
            "labels":labels,
            "header_candidates":header_candidates,
            "structural_columns":structural_columns,
            "structural_values":structural_values,
        })

    wb.close()
    LOCAL.unlink(missing_ok=True)
    result={
        "version":1,
        "source":"10.1371/journal.pbio.2002556.s011",
        "download_route":source_url,
        "bytes":len(data),
        "sheets":sheets,
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Crowd-playback S1 Data schema audit v1","",
        "**STRUCTURE ONLY — NO NUMERIC ACOUSTIC OUTCOME VALUES REPORTED.**","",
        f"- workbook bytes: **{len(data)}**",
        f"- download route: `{source_url}`",
        f"- sheets: **{len(sheets)}**","",
    ]
    for s in sheets:
        lines += [
            f"## {s['name']}","",
            f"- rows: {s['max_row']}",
            f"- columns: {s['max_column']}",
            f"- structural headers: {[x['header'] for x in s['structural_columns']]}",
        ]
        # Print only strings relevant to structure/fig2.
        rel=[x for x in s["labels"] if KEY.search(x["value"])]
        if rel:
            lines.append("- relevant labels:")
            for x in rel[:120]:
                lines.append(f"  - {x['cell']}: {x['value']}")
        if s["structural_values"]:
            lines.append("- structural levels:")
            for k,v in s["structural_values"].items():
                lines.append(f"  - {k}: {v}")
        lines.append("")
    lines += ["No LD-coordinate, F0, entropy, centroid, dispersion, or p-value was calculated.",""]
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
