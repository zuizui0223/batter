#!/usr/bin/env python3
"""Outcome-blind acquisition/schema check for published Lewanzik et al. 2019 XLSX.

Uses Python standard-library ZIP/XML primitives (not an Excel editing library).
Outputs only source provenance and schema metadata; never row-level animal data.
"""
import hashlib
import io
import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SOURCES = [
  "https://datadryad.org/downloads/file_stream/83444",
  "https://datadryad.org/api/v2/files/83444/download",
  "https://datadryad.org/api/v2/datasets/doi%3A10.5061%2Fdryad.gp65g2t/download",
]
ROOT = Path(__file__).resolve().parent
OUT = Path(os.getenv("H1_SOURCE_RECEIPT", ROOT / "source_access_receipt_2019.json"))
MAX_BYTES = 12_000_000
NS = {"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def request_once(url):
    req=urllib.request.Request(url,headers={
       "User-Agent":"BatSocialInfoReanalysis/1.0 (+https://doi.org/10.5061/dryad.gp65g2t)",
       "Accept":"application/octet-stream, application/zip, */*",
    })
    with urllib.request.urlopen(req, timeout=28) as resp:
        return resp.geturl(),resp.status,resp.headers.get("Content-Type",""),resp.read(MAX_BYTES+1)

def open_original_xlsx(payload):
    if len(payload)>MAX_BYTES or not payload.startswith(b"PK\x03\x04"):
        raise ValueError("not_zip_or_oversized")
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        entries=z.namelist()
        if "xl/workbook.xml" in entries and "[Content_Types].xml" in entries:
            return payload,"direct_xlsx"
        source_files=[i for i in z.infolist() if i.filename.lower().endswith(".xlsx") and i.file_size<MAX_BYTES]
        if len(source_files)!=1:
            raise ValueError("not_a_single_published_xlsx_in_archive")
        content=z.read(source_files[0])
        if not content.startswith(b"PK\x03\x04"):
            raise ValueError("nested_file_not_xlsx")
        return content,"dataset_zip/"+source_files[0].filename

def inspect_schema(payload):
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names=z.namelist()
        if "xl/workbook.xml" not in names:
            raise ValueError("missing_workbook_xml")
        shared=[]
        if "xl/sharedStrings.xml" in names:
            xml=ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in xml.findall("x:si",NS):
                shared.append("".join(t.text or "" for t in si.findall(".//x:t",NS)))
        workbook=ET.fromstring(z.read("xl/workbook.xml"))
        rels={}
        relspath="xl/_rels/workbook.xml.rels"
        if relspath in names:
            relroot=ET.fromstring(z.read(relspath))
            for rel in relroot:
                rels[rel.attrib.get("Id","")]=rel.attrib.get("Target","")
        sheets=[]
        for sh in workbook.findall("x:sheets/x:sheet",NS):
            name=sh.attrib.get("name","unknown")
            target=rels.get(sh.attrib.get("{"+NS["r"]+"}id",""),"")
            if target.startswith("/"): path=target.lstrip("/")
            elif target.startswith("xl/"): path=target
            else: path="xl/"+target
            if path not in names:
                # Backwards-compatible, sequential XLSX location fallback.
                cand="xl/worksheets/sheet"+str(len(sheets)+1)+".xml"
                if cand not in names:raise ValueError("worksheet_xml_missing: "+name)
                path=cand
            root=ET.fromstring(z.read(path))
            rows=root.findall(".//x:sheetData/x:row",NS)
            headers=[]
            for row in rows[:1]:
                for cell in row.findall("x:c",NS):
                    typ=cell.attrib.get("t","")
                    val=cell.find("x:v",NS)
                    inline=cell.find("x:is",NS)
                    sval=val.text if val is not None else ""
                    if typ=="s" and sval:
                        try: sval=shared[int(sval)]
                        except (ValueError,IndexError):sval="<invalid_shared_string>"
                    elif typ=="inlineStr" and inline is not None:
                        sval="".join(t.text or "" for t in inline.findall(".//x:t",NS))
                    headers.append({"address":cell.attrib.get("r",""),"header":sval[:100]})
            sheets.append({"sheet_name":name,"sheet_xml":path,"xml_row_count":len(rows),
                           "first_row_headers":headers[:70],
                           "dimension":root.find("x:dimension",NS).attrib.get("ref") if root.find("x:dimension",NS) is not None else None})
        return sheets

def main():
    attempts=[]
    receipt={"status":"STOP_NOT_DOWNLOADED","dataset_doi":"10.5061/dryad.gp65g2t",
             "published_filename":"Lewanzik_etal_2019_JAE_DATA.xlsx",
             "report_scope":"original_file_retrieval_and_column_schema_only",
             "animal_outcomes_opened":False,"attempts":attempts}
    for u in SOURCES:
        try:
            final,status,mime,data=request_once(u)
            attempt={"url":u,"effective_url":final,"status":status,
                     "content_type":mime,"received_bytes":len(data)}
            attempts.append(attempt)
            xlsx,container=open_original_xlsx(data)
            sheet_schema=inspect_schema(xlsx)
            receipt.update({"status":"SCHEMA_ONLY_PASS","selected_url":u,
                "container":container,"original_xlsx_sha256":hashlib.sha256(xlsx).hexdigest(),
                "original_xlsx_bytes":len(xlsx),"sheet_schema":sheet_schema})
            attempt["file_status"]="valid_xlsx"
            # File remains in GitHub runner temp and is NOT uploaded as an artifact.
            break
        except Exception as exc:
            attempts.append({"url":u,"status":"unavailable_or_invalid",
                             "error_type":type(exc).__name__,
                             "error_detail":str(exc)[:180]})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,ensure_ascii=False))
    if receipt["status"]!="SCHEMA_ONLY_PASS":
        raise SystemExit(2)

if __name__=="__main__":
    main()
