"""V31: inspect exact published archive schemas and code lineage without numerical outcomes.
No execution of third-party code, no raw observations or identifiers in output.
"""
import csv, hashlib, io, json, re, zipfile
from collections import Counter
from pathlib import PurePosixPath
import numpy as np
import requests
from scipy.io import whosmat, loadmat
import h5py
from openpyxl import load_workbook
from roost_fd_source_audit_v2 import OUT

BASE="https://data.mendeley.com/public-files/datasets/w4s2xrkv6p/files/"
FILES={
 "audio_mat":("b2aefd1c-53f0-4ef6-9250-ed80b94f1bf1",7368362,"9c28df516e175e436640f2183a87ead5707ec727827132eeb4afdc2d1d033daf"),
 "data_zip":("f8b1917e-4950-42b1-aee9-6d51a96a9fcb",22909253,"47131ece9148e0ef72a89ffe64a3c81421ab6699b08b39b0fbd66dfdfaec28ab")}
MAX_TOTAL=150_000_000; MAX_MEMBER=40_000_000; MAX_MEMBERS=500
TOKENS={
 "gps":r"gps|gnss",
 "native":r"raw|original|native|unprocess",
 "position":r"position|coord|track|trajectory|location|latitude|longitude|easting|northing",
 "latitude":r"latitude|\blat\b",
 "longitude":r"longitude|\blon\b|\blong\b",
 "vertical":r"altitude|height|ellipsoid|elevation|\bz\b",
 "time":r"timestamp|datetime|time|date",
 "individual":r"individual|animal|bat[_ ]?id|tag[_ ]?id|subject",
 "acoustic":r"audio|acoustic|echolocation|call|pulse|ipi|inter.?pulse",
 "speed":r"speed|velocity|distance",
 "interp":r"interp\w*|resampl\w*",
 "smooth":r"smooth\w*|loess|lowess|sgolay|movmean|movmedian",
 "filter":r"filter\w*|outlier\w*|clean\w*",
 "load":r"\bload\b|readtable|readmatrix|csvread|importdata|readcell|h5read|matfile",
 "device":r"device|logger|sampling|sample.?rate|cadence|tag"}
def tags(s):
    return [k for k,v in TOKENS.items() if re.search(v,str(s),flags=re.I)]
def digest(x):return hashlib.sha256(x).hexdigest()
def keyname(x):
    # Never release arbitrary labels from cell/struct keys or paths.
    x=str(x)
    if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,60}",x) and (tags(x) or x.lower() in
        {"x","y","z","lat","lon","t","id","data","name","species","sex","age","frequency","duration","fs","dt","h","n","a","b","c","r","s","v","p"}):
        # Only field-like names, not strings containing embedded individual numbers.
        if not re.search(r"\d{2,}",x):return x
    return "field_"+digest(x.encode())[:12]
def fetch(spec):
    fid,size,sha=spec
    with requests.get(BASE+fid+"/file_downloaded",stream=True,timeout=(15,90),
        headers={"User-Agent":"batter-source-schema-v31/1.0"}) as r:
        r.raise_for_status()
        b=bytearray()
        for chunk in r.iter_content(1024*1024):
            b.extend(chunk)
            if len(b)>size:raise ValueError("published size exceeded")
    b=bytes(b)
    if len(b)!=size or digest(b)!=sha:raise ValueError("published digest or size mismatch")
    return b

def code_audit(b):
    txt=b.decode("utf-8-sig",errors="replace")
    lines=txt.splitlines(); counts={}
    for k,v in TOKENS.items():
        hits=[i+1 for i,l in enumerate(lines) if re.search(v,l,flags=re.I)]
        if hits:counts[k]={"line_count":len(hits),"first_lines":hits[:12]}
    # Report only generic processing function tokens, not arguments or source data.
    funs=sorted({m.group(0).lower() for m in re.finditer(
        r"\b(?:interp1|interp2|interpft|griddedInterpolant|resample|smooth|smoothdata|loess|lowess|sgolayfilt|movmean|movmedian|readtable|readmatrix|load|matfile|readcell|csvread|importdata|fillmissing|isoutlier|rmoutliers|datetime|datenum)\b",
        txt,flags=re.I)})
    return {"lines":len(lines),"term_hits":counts,"processing_functions":funs}

def schema_v5(b):
    specs=whosmat(io.BytesIO(b))
    names=[n for n,sh,t in specs]
    output={"format":"MAT_v4_v5","variables":[{"name":keyname(n),"tags":tags(n),"shape":list(sh),"class":t} for n,sh,t in specs],
        "schema_nodes":[],"inspection_truncated":False}
    # Guard against huge explicitly advertised numeric arrays.
    sizes=sum(int(np.prod(sh,dtype=np.int64))*16 for n,sh,t in specs if t not in ("struct","cell","object","char"))
    if sizes>MAX_TOTAL*4:
        output["inspection_truncated"]=True;output["reason"]="advertised_numeric_size_gate";return output
    dat=loadmat(io.BytesIO(b),variable_names=names,struct_as_record=True,squeeze_me=False,
        verify_compressed_data_integrity=True)
    nodes={}; visits=0
    def walk(x,path,depth=0):
        nonlocal visits
        if visits>=1400 or depth>7:
            output["inspection_truncated"]=True;return
        visits+=1
        if not isinstance(x,np.ndarray):return
        shape=tuple(int(k) for k in x.shape)
        kind="struct" if x.dtype.names else ("cell" if x.dtype.kind=="O" else str(x.dtype.kind))
        key=(path,shape,kind)
        nodes[key]=nodes.get(key,0)+1
        if x.dtype.names:
            for field in x.dtype.names:
                walk(x[field],path+"."+keyname(field),depth+1)
        elif x.dtype.kind=="O":
            flat=x.ravel()
            # Deterministic structural sample only. Never emit text or numeric contents.
            if len(flat)>48:output["inspection_truncated"]=True
            indices=np.unique(np.linspace(0,len(flat)-1,min(48,len(flat)),dtype=int)) if len(flat) else []
            for i in indices:walk(flat[i],path+"[]",depth+1)
    for n in names:
        if n in dat:walk(dat[n],keyname(n))
    # Limit output; preserve distinct shape/type counts.
    output["schema_nodes"]=[{"path":p,"shape":list(sh),"kind":k,"observations":v} for (p,sh,k),v in nodes.items()][:220]
    if len(nodes)>220:output["inspection_truncated"]=True
    output["distinct_schema_nodes"]=len(nodes)
    return output

def schema_hdf(b):
    o={"format":"MAT_v7_3_HDF5","schema_nodes":[],"inspection_truncated":False}
    with h5py.File(io.BytesIO(b),"r") as f:
        visited=set()
        def walk(g,path,depth):
            if depth>8 or len(o["schema_nodes"])>=220:
                o["inspection_truncated"]=True;return
            for k in g.keys():
                if len(o["schema_nodes"])>=220:
                    o["inspection_truncated"]=True;break
                link=g.get(k,getlink=True)
                if not isinstance(link,h5py.HardLink):continue
                q=g[k];p=path+"/"+keyname(k)
                addr=h5py.h5o.get_info(q.id).addr
                if addr in visited:continue
                visited.add(addr)
                if isinstance(q,h5py.Dataset):
                    o["schema_nodes"].append({"path":p,"shape":list(q.shape),"dtype":str(q.dtype),"reference_dtype":bool(h5py.check_dtype(ref=q.dtype))})
                elif isinstance(q,h5py.Group):
                    o["schema_nodes"].append({"path":p,"kind":"group"})
                    walk(q,p,depth+1)
        walk(f,"",0)
    return o

def mat(b):
    if b.startswith(b"MATLAB 7.3 MAT-file"):return schema_hdf(b)
    try:return schema_v5(b)
    except NotImplementedError:return schema_hdf(b)

def table(b,suffix):
    if suffix in (".xlsx",".xlsm"):
        w=load_workbook(io.BytesIO(b),read_only=True,data_only=False)
        try:
            sheets=[]
            for sh in w.worksheets[:30]:
                first=next(sh.iter_rows(min_row=1,max_row=1,values_only=True),())
                sheets.append({"row_count_metadata":sh.max_row,"column_count_metadata":sh.max_column,
                    "first_row_field_tokens":[{"name":keyname(v),"tags":tags(v)} for v in first if isinstance(v,str) and tags(v)][:100]})
            return {"sheet_count":len(w.worksheets),"sheets":sheets}
        finally:w.close()
    txt=b.decode("utf-8-sig",errors="replace")
    first=next(csv.reader(io.StringIO(txt),delimiter="\t" if suffix==".tsv" else ","),[])
    return {"column_count":len(first),"first_row_field_tokens":[{"name":keyname(v),"tags":tags(v)} for v in first if tags(v)][:100]}

def inspect_zip(b):
    result={"members":[]}
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        infos=[i for i in z.infolist() if not i.is_dir()]
        result.update(member_count=len(infos),total_uncompressed_bytes=sum(i.file_size for i in infos),
          extensions=dict(Counter(PurePosixPath(i.filename).suffix.lower() for i in infos)))
        if len(infos)>MAX_MEMBERS or result["total_uncompressed_bytes"]>MAX_TOTAL:
            result["status"]="archive_cap";return result
        for index,i in enumerate(infos):
            suffix=PurePosixPath(i.filename).suffix.lower()
            r={"index":index,"path_sha256":digest(i.filename.encode()),"suffix":suffix,
                "path_tags":tags(i.filename),"size":i.file_size,"crc32":format(i.CRC,"08x")}
            if i.file_size>MAX_MEMBER:
                r["status"]="member_cap"
            elif suffix in (".mat",".m",".txt",".md",".csv",".tsv",".xlsx",".xlsm",".py",".r"):
                try:
                    content=z.read(i);r["sha256"]=digest(content)
                    if suffix==".mat":r["schema"]=mat(content)
                    elif suffix in (".csv",".tsv",".xlsx",".xlsm"):r["schema"]=table(content,suffix)
                    else:r["code_or_documentation"]=code_audit(content)
                    r["status"]="inspected"
                except Exception as e:r["status"]="parser_blocked";r["error_type"]=type(e).__name__
            else:r["status"]="metadata_only"
            result["members"].append(r)
        result["status"]="inspected"
    return result

def main():
    out={"status":"archive_schema_only","numeric_outcomes_summarized":False,"third_party_code_executed":False,
        "native_GPS_admission":"not_adjudicated","files":{}}
    dest=OUT/"audit_v31_acoustic_gps_archive.json"
    def save():dest.write_text(json.dumps(out,indent=2,allow_nan=False))
    save()
    for k,s in FILES.items():
        try:
            b=fetch(s);r={"size":len(b),"sha256":digest(b),"published_hash_match":True}
            r["audit"]=mat(b) if k=="audio_mat" else inspect_zip(b)
            r["status"]="inspected"
        except Exception as e:r={"status":"blocked","error_type":type(e).__name__}
        out["files"][k]=r;save()
    print(dest.read_text())
    return 0 if all(v["status"]=="inspected" for v in out["files"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
