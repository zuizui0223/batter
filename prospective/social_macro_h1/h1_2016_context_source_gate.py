#!/usr/bin/env python3
"""Source-only, outcome-blind original 2016 roost/foraging playback XLSX gate.

No cell values beyond the first header row or sheet dimensions are ever reported.
Related 2015 Figshare is queried for metadata/file listings only.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

OUT=Path(os.getenv("H1_CONTEXT_RECEIPT","/tmp/h1_saccopteryx_2016_source_receipt.json"))
SOURCE=Path(os.getenv("H1_CONTEXT_ORIGINAL","/tmp/h1_saccopteryx_2016_original.xlsx"))
MAX_SIZE=15_000_000
NS={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

URLS=[
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC4892459/bin/rsos160151supp1.xlsx",
 "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4892459/supplementaryFiles",
 "https://royalsocietypublishing.org/doi/suppl/10.1098/rsos.160151/suppl_file/rsos160151supp1.xlsx",
]
FIGSHARE_API="https://api.figshare.com/v2/articles/1454597"

def fetch(url,seconds=24):
    request=urllib.request.Request(url,headers={
        "User-Agent":"H1-Social-Information-Public-Source-Audit/1.0 (educational research)",
        "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/zip,application/json,*/*"})
    with urllib.request.urlopen(request,timeout=seconds) as resp:
        data=resp.read(MAX_SIZE+1)
        return data,{"status":resp.status,"bytes_received":len(data),
                     "mime":resp.headers.get("Content-Type",""),
                     "effective_url":resp.geturl()}

def original_xlsx(buffer):
    if len(buffer)>MAX_SIZE:raise ValueError("oversized_payload")
    if not buffer.startswith(b"PK\x03\x04"):raise ValueError("not_zip_or_xlsx")
    with zipfile.ZipFile(io.BytesIO(buffer)) as z:
        names=z.namelist()
        if "[Content_Types].xml" in names and "xl/workbook.xml" in names:
            return buffer,"direct_xlsx"
        found=[f for f in z.infolist() if f.filename.lower().endswith(".xlsx") and f.file_size<=MAX_SIZE]
        if len(found)!=1:raise ValueError("no_single_nested_xlsx_in_zip")
        data=z.read(found[0])
        if not data.startswith(b"PK\x03\x04"):raise ValueError("nested_file_invalid")
        return data,"nested/"+found[0].filename

def inspect_xlsx(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=set(z.namelist())
        root=ET.fromstring(z.read("xl/workbook.xml"))
        shared=[]
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("x:si",NS):
                shared.append("".join(t.text or "" for t in si.findall(".//x:t",NS)))
        rels={}
        if "xl/_rels/workbook.xml.rels" in names:
            for el in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")):
                rels[el.attrib.get("Id")]=el.attrib.get("Target")
        sheets=[]
        for idx,sh in enumerate(root.findall("x:sheets/x:sheet",NS)):
            rid=sh.attrib.get("{"+NS["r"]+"}id")
            target=rels.get(rid,"")
            if target.startswith("/"):path=target[1:]
            elif target.startswith("xl/"):path=target
            else:path="xl/"+target
            if path not in names:path=f"xl/worksheets/sheet{idx+1}.xml"
            if path not in names:raise ValueError("worksheet_xml_not_found")
            ws=ET.fromstring(z.read(path))
            rows=ws.findall(".//x:sheetData/x:row",NS)
            # Need only first header row values, not biological outcomes.
            first=rows[0] if rows else None
            hdr=[]
            if first is not None:
                for cell in first.findall("x:c",NS):
                    t=cell.attrib.get("t","")
                    v=cell.find("x:v",NS)
                    value=v.text if v is not None and v.text is not None else ""
                    if t=="s" and value:value=shared[int(value)]
                    if t=="inlineStr":
                        value="".join(x.text or "" for x in cell.findall(".//x:t",NS))
                    hdr.append({"column_cell":cell.attrib.get("r"),"value":value[:110]})
            dim=ws.find("x:dimension",NS)
            sheets.append({"name":sh.attrib.get("name",""),
                           "xml_row_count":len(rows),
                           "dimension":dim.attrib.get("ref") if dim is not None else None,
                           "header_row":hdr[:60]})
        return sheets

def main():
    receipt={"original_2016_doi":"10.1098/rsos.160151",
             "supplement_filename":"rsos160151supp1.xlsx",
             "scope":"ORIGINAL_SOURCE_SCHEMA_ONLY_NO_ANIMAL_OUTCOME_ANALYSIS",
             "status":"STOP_ORIGINAL_NOT_VALIDATED","attempts":[],
             "figshare_2015_metadata":None}
    try:
        data,http=fetch(FIGSHARE_API,seconds=15)
        obj=json.loads(data)
        receipt["figshare_2015_metadata"]={
            "article_id":obj.get("id"),"title":obj.get("title"),
            "doi":obj.get("doi"),"published_date":obj.get("published_date"),
            "files":[{"name":f.get("name"),"size":f.get("size"),
                      "download_url":f.get("download_url"),
                      "supplied_md5":f.get("supplied_md5")} for f in obj.get("files",[])]
        }
    except Exception as exc:
        receipt["figshare_2015_metadata"]={"status":"ERROR","type":type(exc).__name__,"message":str(exc)[:180]}
    for url in URLS:
        a={"url":url}
        receipt["attempts"].append(a)
        try:
            buf,http=fetch(url)
            a.update(http)
            data,package=original_xlsx(buf)
            schema=inspect_xlsx(data)
            digest=hashlib.sha256(data).hexdigest()
            SOURCE.write_bytes(data)
            receipt.update({"status":"ORIGINAL_SCHEMA_PASS",
                            "original_sha256":digest,"original_bytes":len(data),
                            "source_url":url,"package":package,
                            "sheets":schema,"animal_outcome_rows_analyzed":False})
            a["result"]="VALID_XLSX"
            break
        except Exception as exc:
            a.update({"result":"STOP","error_type":type(exc).__name__,
                      "error_message":str(exc)[:180]})
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,ensure_ascii=False))
    if receipt["status"]!="ORIGINAL_SCHEMA_PASS":raise SystemExit(2)

if __name__=="__main__":
    main()
