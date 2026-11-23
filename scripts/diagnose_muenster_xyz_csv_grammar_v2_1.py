#!/usr/bin/env python3
"""Diagnose original Münster 3D CSV lexical structure without numeric outcomes.

The already authenticated original 3D archive failed strict v2 numeric parser;
this scanner prints file/member names and categorical first-five-row *types*,
no XYZ values, flight heights or biological statistics. The prior v2 STOP
remains unchanged regardless of this engineering diagnostic result.
"""
from __future__ import annotations
from hashlib import sha256
from io import BytesIO,StringIO
from pathlib import Path
from zipfile import ZipFile
from urllib.request import Request,urlopen
from collections import Counter
import csv,json,math,re
from scripts.audit_muenster_thermal_3d_geometry_v2 import (
    ZIP_URL,ZIP_MD5,ZIP_SHA256,verified_get,BASENAME,
)


def describe_cell(raw):
    s=raw.strip()
    if s=="":
        return "blank"
    try:
        f=float(s)
        return "finite_number" if math.isfinite(f) else "missing_NaN_or_infinity"
    except ValueError:
        return "text_or_metadata"


def lexical_preview(data:bytes):
    lines=data.decode("utf-8-sig",errors="replace").splitlines()
    first=lines[0] if lines else ""
    delimiter=max((",","\t",";"),key=lambda ch:first.count(ch))
    patterns=[]
    text_headers=[]
    for row_idx,line in enumerate(lines[:5]):
        row=next(csv.reader(StringIO(line),delimiter=delimiter))
        labels=[describe_cell(v) for v in row]
        patterns.append({"row":row_idx+1,"columns":len(row),"lexical_cell_types":labels})
        if row_idx==0:
            for s in row:
                if describe_cell(s)=="text_or_metadata":
                    t=s.strip()
                    # Do not print an unknown source number/symbol as a bat xyz.
                    if re.fullmatch(r"[A-Za-z_./ \-]{1,40}",t):
                        text_headers.append(t)
    return {
        "delimiter_type":"comma" if delimiter=="," else ("tab" if delimiter=="\t" else "semicolon"),
        "source_physical_rows":len(lines),
        "first_five_row_structure_only":patterns,
        "possible_literal_textual_first_row_header_tokens":text_headers,
        "numeric_XYZ_values_opened_or_printed":False,
    }


def run():
    data=verified_get(ZIP_URL,ZIP_MD5,ZIP_SHA256)
    reports=[]
    with ZipFile(BytesIO(data)) as z:
        for file in z.namelist():
            if not file.endswith(".csv"):
                continue
            if "coordinates_tracks/" not in file:
                raise RuntimeError("unexpected source member directory")
            name=Path(file).name
            if BASENAME.fullmatch(name) is None:
                raise RuntimeError("source member outside frozen bat/lamp grammar")
            reports.append({"source_name":name,**lexical_preview(z.read(file))})
    return {
        "status":"source_grammar_diagnostic_only_prior_v2_STOP_preserved",
        "source_zip_sha256":sha256(data).hexdigest(),
        "original_xyz_csv_file_count":len(reports),
        "per_file_lexical_schema":reports,
        "real_bat_xyz_numbers_or_height_distributions_reported":False,
        "does_not_authorize_any_bat_LiDAR_colocation":True,
        "prior_v2_SOURCE_FORMAT_STOP_not_reclassified":True,
    }


def main():
    dst=Path("results/muenster_original_xyz_lexical_diag_v2_1.json")
    dst.parent.mkdir(parents=True,exist_ok=True)
    try:
        r=run()
    except Exception as exc:
        r={"status":"source_grammar_diagnostic_failed",
           "reason":str(exc)[:300],"exception":type(exc).__name__,
           "real_bat_xyz_numbers_or_height_distributions_reported":False}
    dst.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    main()
