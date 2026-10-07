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

    sheet_inventory=[
        {"name":ws.title,"max_row":ws.max_row,"max_column":ws.max_column}
        for ws in wb.worksheets
    ]
    fig_names=[x["name"] for x in sheet_inventory if re.search(r"fig\\s*2",x["name"],re.I)]
    if len(fig_names)!=1:
        raise RuntimeError(f"expected one Fig 2 sheet, got {fig_names}")
    ws=wb[fig_names[0]]

    # Structural labels only from Fig 2 sheet.
    labels=[]
    for row in ws.iter_rows():
        for cell in row:
            v=cell.value
            if isinstance(v,str) and v.strip():
                labels.append({"cell":cell.coordinate,"value":v.strip()})

    # Identify rows/columns that appear to encode pup/group/session/LD labels.
    relevant_labels=[x for x in labels if KEY.search(x["value"])]

    # All string labels are structural; numeric coordinate values remain unopened.
    result={
        "version":2,
        "source":"10.1371/journal.pbio.2002556.s011",
        "download_route":source_url,
        "bytes":len(data),
        "sheet_inventory":sheet_inventory,
        "fig2_sheet":ws.title,
        "fig2_max_row":ws.max_row,
        "fig2_max_column":ws.max_column,
        "fig2_all_string_labels":labels,
        "fig2_relevant_labels":relevant_labels,
    }
    wb.close()
    LOCAL.unlink(missing_ok=True)
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\\n")

    lines=[
        "# Crowd-playback S1 Data schema audit v2","",
        "**FIG.2 STRUCTURE ONLY — NO NUMERIC LD/F0/ENTROPY VALUES REPORTED.**","",
        f"- workbook bytes: **{len(data)}**",
        f"- download route: \`{source_url}\`",
        f"- sheets: **{len(sheet_inventory)}**",
        f"- Fig 2 sheet: **{ws.title}**",
        f"- Fig 2 rows × columns: **{ws.max_row} × {ws.max_column}**","",
        "## Sheet inventory","",
    ]
    for x in sheet_inventory:
        lines.append(f"- {x['name']}: {x['max_row']} × {x['max_column']}")
    lines += ["","## Fig 2 structural labels",""]
    for x in labels:
        lines.append(f"- {x['cell']}: {x['value']}")
    lines += ["","No numeric pup coordinate, F0 value, centroid, dispersion, or p-value was opened.",""]
    OUTMD.write_text("\\n".join(lines)+"\\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
