#!/usr/bin/env python3
"""Open only files authorized by SCHEMA_FILE_OPENING_ALLOWLIST_V1.md.

Outputs schema summaries only. No route coordinate arrays are loaded.
"""
from __future__ import annotations
import hashlib, io, json, re, tempfile, urllib.parse, urllib.request, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
UA="batter-ontogenetic-schema-open/1.0"
OUT=Path("prospective/ontogenetic_path_dependence/SCHEMA_OPEN_RESULT_V1.json")

A_FILES={
 "Code.zip":{
   "dataset":"gpcg9m5758","id":"85077631-f5b9-469a-a628-1ce652944cf8",
   "size":32244,"sha256":"bfe2fe7a691c33a24b00a8cf56511c3668cce0ce3ebc33c8cc911df61579d773","mode":"code_zip"},
 "data_age_fa_all.xlsx":{
   "dataset":"gpcg9m5758","id":"4bd0e11b-8329-422a-aed6-2bc3e7299f81",
   "size":47700,"sha256":"c7bfa0489d04c028d1d8dee565865da74dfb3499245eecf9234b14509aa54e81","mode":"xlsx_headers"},
 "FA-FlightIndex-Lab.xlsx":{
   "dataset":"gpcg9m5758","id":"1d8da58c-162b-4558-9117-b96d9229f5c2",
   "size":10471,"sha256":"88cf76825a3fbf49dc613fe61afc7c5f02f474f38a3510255736440a0f177f08","mode":"xlsx_headers"},
}
B_ROOT={
 "batSex.mat":{"id":"03002db4-e81c-4f91-81e2-dd825b571f5f","size":1142,"sha256":"4f5d10f50fcd2838700cbd1decc5d785c2253835f4494c9e8c7f88ae40d2bdf1"},
 "buildingTableWithBatNo.mat":{"id":"eb46274b-2fc9-4165-9bf9-fd399a7b7075","size":4788,"sha256":"efd2c500d6dea7db83c118dc4daba6633aa852f8677b583d2a81aa42a475e6e5"},
 "trees.mat":{"id":"65c7574e-a3c5-4105-bcc0-a1551d6e2f0c","size":17247,"sha256":"26acb2199bacd5244d505cbeb91c9c46bd9a1ac0a01f6bf5926a17250461c6cf"},
}
B_PROBES=[
 {"cohort":"GPS_2016_2017","individual":"Ali","folder_id":"f148a7d1-8ca7-4b99-b64d-5bf0adb6dc08"},
 {"cohort":"GPS_2017_2018","individual":"Anka","folder_id":"ea9161e3-b368-4cce-8aa4-753fc6b9ffe2"},
]

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r)

def get_bytes(url,max_bytes=8_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:
        n=r.headers.get("Content-Length")
        if n and int(n)>max_bytes:
            raise RuntimeError(f"refuse content length {n} > {max_bytes}")
        data=r.read(max_bytes+1)
    if len(data)>max_bytes:
        raise RuntimeError(f"refuse downloaded bytes {len(data)} > {max_bytes}")
    return data

def file_meta(dataset,file_id):
    return get_json(f"{BASE}/datasets/{dataset}/files/{file_id}")

def download_authorized(dataset,name,spec):
    meta=file_meta(dataset,spec["id"])
    if meta.get("filename")!=name:
        raise RuntimeError(f"name mismatch {name} vs {meta.get('filename')}")
    cd=meta.get("content_details") or {}
    size=cd.get("size") or meta.get("size")
    if int(size)!=int(spec["size"]):
        raise RuntimeError(f"size mismatch {name}: {size} != {spec['size']}")
    url=cd.get("download_url")
    if not url:
        raise RuntimeError(f"no download_url for {name}")
    b=get_bytes(url,max_bytes=max(1_000_000,int(spec["size"])+4096))
    if len(b)!=int(spec["size"]):
        raise RuntimeError(f"download size mismatch {name}: {len(b)}")
    h=hashlib.sha256(b).hexdigest()
    if h!=spec["sha256"]:
        raise RuntimeError(f"sha256 mismatch {name}: {h}")
    return b,meta

def xlsx_headers(b):
    # Parse XLSX package without loading cell values beyond row 1.
    z=zipfile.ZipFile(io.BytesIO(b))
    ns={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pr":"http://schemas.openxmlformats.org/package/2006/relationships"}
    shared=[]
    if "xl/sharedStrings.xml" in z.namelist():
        root=ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si",ns):
            shared.append("".join(t.text or "" for t in si.findall(".//m:t",ns)))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out=[]
    for sh in wb.findall("m:sheets/m:sheet",ns):
        name=sh.attrib.get("name")
        rid=sh.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        target=relmap[rid]
        p=("xl/"+target.lstrip("/")) if not target.startswith("xl/") else target
        root=ET.fromstring(z.read(p))
        dim=root.find("m:dimension",ns)
        ref=dim.attrib.get("ref") if dim is not None else None
        row=root.find("m:sheetData/m:row",ns)
        headers=[]
        if row is not None:
            for c in row.findall("m:c",ns):
                typ=c.attrib.get("t")
                v=c.find("m:v",ns)
                val=None if v is None else v.text
                if typ=="s" and val is not None:
                    try: val=shared[int(val)]
                    except Exception: pass
                elif typ=="inlineStr":
                    t=c.find(".//m:t",ns); val=t.text if t is not None else None
                headers.append({"cell":c.attrib.get("r"),"value":val,"type":typ})
        out.append({"sheet":name,"dimension":ref,"first_row":headers})
    return out

def code_zip_summary(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    members=[{"name":x.filename,"size":x.file_size} for x in z.infolist()]
    excerpts=[]
    keywords=re.compile(r"(mother|pup|juven|flight|gps|tree|independ|imprint|route|date|time|lat|lon|coordinate|flightindex)",re.I)
    for x in z.infolist():
        if x.is_dir() or x.file_size>1_000_000: continue
        if not re.search(r"\.(m|r|py|txt|md|csv)$",x.filename,re.I): continue
        raw=z.read(x)
        try: txt=raw.decode("utf-8")
        except UnicodeDecodeError:
            try: txt=raw.decode("latin-1")
            except Exception: continue
        hits=[]
        for n,line in enumerate(txt.splitlines(),1):
            if keywords.search(line):
                # Keep source definition context, not bulk numeric literals.
                clean=line.strip()
                if len(clean)>500: clean=clean[:500]
                hits.append({"line":n,"text":clean})
            if len(hits)>=120: break
        excerpts.append({"file":x.filename,"matching_lines":hits})
    return {"members":members,"source_excerpts":excerpts}

def whosmat_summary(b):
    import scipy.io
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(b); tmp.flush()
        # HDF5/v7.3 first when signature is present.
        if b.startswith(b"\\x89HDF"):
            import h5py
            out=[]
            with h5py.File(tmp.name,"r") as h:
                def visitor(name,obj):
                    if isinstance(obj,h5py.Dataset):
                        out.append({"name":name,"shape":list(obj.shape),"dtype":str(obj.dtype)})
                h.visititems(visitor)
            return {"format":"mat-v7.3-hdf5","variables":out}
        try:
            rows=scipy.io.whosmat(tmp.name)
            return {"format":"mat-v5-or-earlier","reader":"scipy.whosmat",
                    "variables":[{"name":n,"shape":list(shape),"class":cls} for n,shape,cls in rows]}
        except Exception as standard_error:
            # Conservative SciPy-header fallback: list each matrix header and seek
            # past its payload WITHOUT reading the array values.
            from scipy.io.matlab._mio5 import MatFile5Reader
            variables=[]
            with open(tmp.name,"rb") as fh:
                rdr=MatFile5Reader(fh)
                rdr.initialize_read()
                rdr.read_file_header()
                while not rdr.end_of_stream():
                    hdr,next_position=rdr.read_var_header()
                    raw_name=getattr(hdr,"name",None)
                    if raw_name is None:
                        name="None"
                    elif isinstance(raw_name,bytes):
                        name=raw_name.decode("latin1",errors="replace") or "__function_workspace__"
                    else:
                        name=str(raw_name) or "__function_workspace__"
                    shape=None
                    shape_error=None
                    try:
                        shape=list(rdr._matrix_reader.shape_from_header(hdr))
                    except Exception as e:
                        shape_error=type(e).__name__
                    variables.append({
                        "name":name,
                        "shape":shape,
                        "shape_error":shape_error,
                        "mclass":getattr(hdr,"mclass",None),
                        "is_global":bool(getattr(hdr,"is_global",False)),
                        "is_logical":bool(getattr(hdr,"is_logical",False)),
                    })
                    fh.seek(next_position)
            return {"format":"mat-v5-or-earlier","reader":"header-only-fallback",
                    "standard_whosmat_error":repr(standard_error),"variables":variables}

def list_folder_files(dataset,version,folder_id):
    url=f"{BASE}/datasets/{dataset}/files?folder_id={urllib.parse.quote(folder_id)}&version={version}&$start=0&$limit=1000"
    rows=get_json(url)
    return rows if isinstance(rows,list) else rows.get("files") or rows.get("items") or rows.get("results") or []

def main():
    result={"contract":"SCHEMA_FILE_OPENING_ALLOWLIST_V1.md","route_geometry_opened":False,"source_A":{},"source_B":{}}

    for name,spec in A_FILES.items():
        b,meta=download_authorized(spec["dataset"],name,spec)
        if spec["mode"]=="code_zip":
            summary=code_zip_summary(b)
        else:
            summary=xlsx_headers(b)
        result["source_A"][name]={"id":spec["id"],"size":len(b),"sha256":hashlib.sha256(b).hexdigest(),"schema":summary}

    for name,spec0 in B_ROOT.items():
        spec={"dataset":"n9d8gbz3xr",**spec0}
        b,meta=download_authorized("n9d8gbz3xr",name,spec)
        result["source_B"][name]={"id":spec["id"],"size":len(b),"sha256":hashlib.sha256(b).hexdigest(),"schema":whosmat_summary(b)}

    probes=[]
    for p in B_PROBES:
        rows=list_folder_files("n9d8gbz3xr",1,p["folder_id"])
        selected=[]
        for row in rows:
            name=row.get("filename") or ""
            if name.lower() not in {p["individual"].lower()+".mat","data.mat"}:
                continue
            cd=row.get("content_details") or {}
            size=int(cd.get("size") or row.get("size") or 0)
            if size<=0 or size>8_000_000:
                raise RuntimeError(f"probe size refused {p['individual']} {name} {size}")
            spec={"dataset":"n9d8gbz3xr","id":row["id"],"size":size,"sha256":cd.get("sha256_hash")}
            if not spec["sha256"]:
                raise RuntimeError(f"probe no sha256 {p['individual']} {name}")
            b,_=download_authorized("n9d8gbz3xr",name,spec)
            selected.append({"filename":name,"id":row["id"],"size":size,"sha256":spec["sha256"],"schema":whosmat_summary(b)})
        probes.append({**p,"opened_files":selected,"all_folder_filenames":[r.get("filename") for r in rows]})
    result["source_B"]["deterministic_individual_schema_probes"]=probes

    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
