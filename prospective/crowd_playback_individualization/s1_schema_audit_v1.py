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
        labels=[]
        max_scan=min(20,ws.max_row)
        for row in ws.iter_rows(min_row=1,max_row=max_scan):
            for cell in row:
                v=cell.value
                if isinstance(v,str) and v.strip():
                    labels.append({"cell":cell.coordinate,"value":v.strip()})
        sheets.append({
            "name":ws.title,
            "max_row":ws.max_row,
            "max_column":ws.max_column,
            "first20_string_labels":labels,
        })

    result={
        "version":3,
        "source":"10.1371/journal.pbio.2002556.s011",
        "download_route":source_url,
        "bytes":len(data),
        "sheets":sheets,
    }
    wb.close()
    LOCAL.unlink(missing_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Crowd-playback S1 Data workbook structure v3","",
        "**SHEET NAMES / FIRST-20-ROW STRING LABELS ONLY — NO NUMERIC OUTCOMES.**","",
        f"- workbook bytes: **{len(data)}**",
        f"- sheets: **{len(sheets)}**","",
    ]
    for s in sheets:
        lines += [
            f"## {s['name']}","",
            f"- rows × columns: {s['max_row']} × {s['max_column']}",
            "- first-20-row strings:",
        ]
        for x in s["first20_string_labels"]:
            lines.append(f"  - {x['cell']}: {x['value']}")
        lines.append("")
    lines += ["No numeric pup coordinate, F0 value, centroid, dispersion, or p-value was opened.",""]
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
