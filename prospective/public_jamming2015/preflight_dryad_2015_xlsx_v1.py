#!/usr/bin/env python3
"""Dryad DOI 10.5061/dryad.8f0v4 strict source/Excel structure gate.

Inspect only official file metadata, workbook sheet names and FIRST header row.
Never open call numeric outcomes, bat-specific acoustic metrics or coefficients.
"""
import argparse
import datetime as dt
import hashlib
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET

import requests

URL = "https://datadryad.org/downloads/file_stream/68296"
DOI = "10.5061/dryad.8f0v4"
FILE = "Dryad.xlsx"
CAP = 8 * 1024 * 1024
TIMEOUT = (12, 55)
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "p": "http://schemas.openxmlformats.org/package/2006/relationships"}

def probe():
    x = {
        "doi": DOI,
        "expected_filename": FILE,
        "exact_official_url": URL,
        "source_checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "STOP_RAW_SOURCE_INACCESSIBLE",
        "evidence_tier": "SOURCE_SCHEMA_ONLY_NO_BAT_ACOUSTIC_VALUES",
        "http_status": None,
        "size": None,
        "sha256": None,
        "workbook_sheets": [],
        "sheet_header_metadata": [],
        "outcome_values_opened": False,
        "warnings": [],
    }
    session = requests.Session()
    try:
        with session.get(URL, stream=True, allow_redirects=True,
                         headers={"User-Agent":"batter-research-structural-audit/1.0",
                                  "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
                         timeout=TIMEOUT) as resp:
            x["http_status"] = resp.status_code
            x["final_host"] = requests.utils.urlparse(resp.url).hostname
            if resp.status_code != 200:
                raise RuntimeError("HTTP_%s" % resp.status_code)
            h = hashlib.sha256()
            chunks = []
            size = 0
            for chunk in resp.iter_content(65536):
                if not chunk: continue
                size += len(chunk)
                if size > CAP:
                    raise RuntimeError("STOP_GT_8_MIB")
                h.update(chunk)
                chunks.append(chunk)
            binary = b"".join(chunks)
            x["size"],x["sha256"]=size,h.hexdigest()
            if not zipfile.is_zipfile(io.BytesIO(binary)):
                raise RuntimeError("NOT_XLSX_ZIP")
        with zipfile.ZipFile(io.BytesIO(binary)) as z:
            names=set(z.namelist())
            required={"xl/workbook.xml","xl/_rels/workbook.xml.rels"}
            if not required.issubset(names):
                raise RuntimeError("XLSX_MISSING_WORKBOOK_METADATA")
            wb=ET.fromstring(z.read("xl/workbook.xml"))
            relationships=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            relations={a.attrib["Id"]:a.attrib.get("Target") for a in relationships if a.attrib.get("Id")}
            shared=[]
            if "xl/sharedStrings.xml" in names:
                raw=ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in raw.findall("m:si",NS):
                    shared.append("".join(t.text or "" for t in si.findall(".//m:t",NS)))
            for sheet in wb.findall(".//m:sheet",NS):
                title=sheet.attrib["name"]
                target=relations.get(sheet.attrib.get("{%s}id" % NS["r"]),"")
                target=target.lstrip("/")
                path=target if target.startswith("xl/") else "xl/"+target
                path=path.replace("xl/../","")
                info={"sheet":title,"source_member":path,"dimension":None,"first_row_headers":[],"opened_numeric_values":False}
                x["workbook_sheets"].append(title)
                if path not in names:
                    info["warning"]="MISSING_SHEET_XML"
                    x["sheet_header_metadata"].append(info)
                    continue
                # Stream only until the first row has been fully parsed.
                with z.open(path) as stream:
                    for ev,el in ET.iterparse(stream,events=("start","end")):
                        local=el.tag.split("}")[-1]
                        if ev=="start" and local=="dimension" and info["dimension"] is None:
                            info["dimension"]=el.attrib.get("ref")
                        if ev=="end" and local=="row":
                            cells=[]
                            for cell in list(el):
                                if cell.tag.split("}")[-1]!="c":continue
                                v=cell.find("m:v",NS)
                                ty=cell.attrib.get("t")
                                if ty=="s" and v is not None:
                                    try: value=shared[int(v.text)]
                                    except Exception: value="<invalid shared-text index>"
                                elif ty=="inlineStr":
                                    value="".join(t.text or "" for t in cell.findall(".//m:t",NS))
                                elif ty=="str" and v is not None:
                                    value=v.text or ""
                                else:
                                    value="<unlabelled numeric/blank cell>"
                                cells.append({"cell":cell.attrib.get("r"),"header":str(value)[:130]})
                            info["first_row_headers"]=cells[:70]
                            break
                x["sheet_header_metadata"].append(info)
        x["status"]="PASS_SOURCE_SCHEMA_ONLY_IDENTIFIABILITY_PENDING"
    except Exception as exc:
        x["warnings"].append(type(exc).__name__+": "+str(exc)[:230])
    return x

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="PIPISTRELLUS_DRYAD_2015_SCHEMA_RECEIPT_V1.json")
    o=a.parse_args()
    data=probe()
    with open(o.out,"w",encoding="utf-8") as fd:
        json.dump(data,fd,indent=2,ensure_ascii=False)
        fd.write("\n")
    print(json.dumps({k:data[k] for k in ("status","http_status","final_host","size","sha256","workbook_sheets","sheet_header_metadata","warnings") if k in data},ensure_ascii=False))
    assert data["outcome_values_opened"] is False

if __name__=="__main__":main()
