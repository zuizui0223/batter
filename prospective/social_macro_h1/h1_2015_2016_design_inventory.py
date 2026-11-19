#!/usr/bin/env python3
"""Follow-on source design inventory, before checking any response magnitudes.

The previous 2016 original XLSX schema gate has passed; this script examines
study IDs and treatment labels (A:C) only and obtains the 2015 original CSV
with independent Figshare-advertised MD5.
"""
import csv
from collections import Counter,defaultdict
import hashlib
import io
import json
import os
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile
import h1_2016_context_source_gate as gate

EXPECTED_2016="28402ac6c969f7a6c13acf5f90192afbfa4b6c5158e1bbc8f657b55f255b05ef"
EXPECTED_2015_MD5="991be124c47f48a955fa5a0a40dd864c"
URL_2016="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4892459/supplementaryFiles"
URL_2015="https://ndownloader.figshare.com/files/2126435"
OUT=Path(os.environ.get("H1_CONTEXT_DESIGN_RECEIPT","/tmp/h1_original_context_design_receipt.json"))

NS=gate.NS

def raw_rows(buf):
    with zipfile.ZipFile(io.BytesIO(buf)) as z:
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("x:si",NS):
                shared.append("".join(t.text or "" for t in si.findall(".//x:t",NS)))
        sheet=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        out=[]
        for row in sheet.findall(".//x:sheetData/x:row",NS):
            d={}
            for c in row.findall("x:c",NS):
                addr=c.attrib.get("r","")
                col=re.match(r"^[A-Z]+",addr)
                if not col or col.group() not in ("A","B","C"):continue
                val=c.find("x:v",NS)
                x=val.text if val is not None else ""
                if c.attrib.get("t")=="s":x=shared[int(x)]
                if c.attrib.get("t")=="inlineStr":x="".join(t.text or "" for t in c.findall(".//x:t",NS))
                d[col.group()]=x
            if d:out.append(d)
        return out

def main():
    receipt={"status":"STOP","stage":"ORIGINAL_STRATIFICATION_METADATA_NOT_OUTCOME",
             "response_columns_opened":False}
    raw,http=gate.fetch(URL_2016)
    xlsx,package=gate.original_xlsx(raw)
    digest=hashlib.sha256(xlsx).hexdigest()
    if digest!=EXPECTED_2016:raise ValueError("2016 source SHA drift")
    cells=raw_rows(xlsx)
    assert len(cells)==115
    row_list=cells[1:]
    for r in row_list:assert all(k in r for k in ["A","B","C"])
    codes={c:dict(sorted(Counter(r[c] for r in row_list).items())) for c in ["A","B","C"]}
    groups=defaultdict(list)
    for r in row_list:groups[r["A"]].append(r)
    original_2016={
        "file_sha256":digest,"n_data_rows":len(row_list),
        "header_ABC":cells[0],"factor_levels":codes,
        "n_colony_labels":len(groups),
        "per_colony_nrows":dict(sorted((k,len(v)) for k,v in groups.items())),
        "within_colony_location_stimulus_counts":{
           k:{f"{z[0]}|{z[1]}":n for z,n in sorted(Counter((x["B"],x["C"]) for x in v).items())}
           for k,v in sorted(groups.items())
        },
    }
    receipt["original_2016"]=original_2016
    file2015,http15=gate.fetch(URL_2015)
    md5=hashlib.md5(file2015).hexdigest()
    if md5!=EXPECTED_2015_MD5:raise ValueError("2015 Figshare source MD5 drift")
    decoded=file2015.decode("utf-8-sig")
    # Figshare CSV uses literal commas; Sniffer mis-infers the quote convention
    # from natural-language header/metadata, corrupting newlines in source cells.
    rows=list(csv.DictReader(io.StringIO(decoded,newline=""),delimiter=","))
    fields=list(rows[0]) if rows else []
    important={c:dict(Counter(str(r[c]) for r in rows).most_common(20))
               for c in fields if any(p in c.lower() for p in ["treatment","roost","session","sequence","day"])}
    receipt["original_2015"]={
       "source_md5":md5,"byte_size":len(file2015),
       "n_rows":len(rows),"header_fields":fields,
       "design_factor_summaries":important,
       "caller_activity_opened":False
    }
    receipt["status"]="DESIGN_CODES_PASS"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
