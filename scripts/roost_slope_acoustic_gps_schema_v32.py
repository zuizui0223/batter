"""V32 source-format repair. Inspect metadata/structure only; no author code execution."""
import collections, hashlib, io, json, re, traceback, zipfile
from pathlib import PurePosixPath
import numpy as np
from scipy.io import whosmat,loadmat
from openpyxl import load_workbook
from roost_fd_source_audit_v2 import OUT
from roost_slope_acoustic_gps_archive_v31 import FILES,fetch,keyname,tags,schema_hdf

KNOWN={"leptonycteris yerbabuenae","myotis myotis","myotis vivesi","rhinopoma microphyllum"}
SOURCE_SHAS={"84dbf900e2f8322ebb0f93fad4a5d1110ab3b6d2fbd4b62fc321218d8a6a6734","dc725826f1c149ecdc65d2970952a19ae923ae19a4c932b51dacbb642ca56626"}
MAPPING_SHA="a9d64f04e8abe29cb728e1d2810bc4a572cbb9624c8410c1b5f7bdbfc3f91d17"
def sha(b):return hashlib.sha256(b).hexdigest()
def err(e,stage):
    # No arbitrary exception text: only generic function/stage identifiers.
    frames=traceback.extract_tb(e.__traceback__)
    return {"stage":stage,"error_type":type(e).__name__,"functions":[f.name for f in frames[-5:]]}
def dims(sh):
    if sh is None:return None
    return [int(x) if x is not None else None for x in sh]
def mat_schema(b):
    if b.startswith(b"MATLAB 7.3 MAT-file"):
        return schema_hdf(b)
    r={"format":"MAT_v4_v5","header_variables":[],"errors":[]}
    try:
        spec=whosmat(io.BytesIO(b))
        r["header_variables"]=[{"name":keyname(n),"shape":dims(sh),"class":str(t)} for n,sh,t in spec]
    except Exception as e:r["errors"].append(err(e,"whosmat"))
    try:
        data=loadmat(io.BytesIO(b),struct_as_record=True,squeeze_me=False,verify_compressed_data_integrity=True)
    except Exception as e:
        r["errors"].append(err(e,"loadmat"));r["status"]="load_blocked";return r
    nodes=collections.Counter();visits=0;trunc=False
    def walk(x,p,depth=0):
        nonlocal visits,trunc
        if depth>9 or visits>=2500:trunc=True;return
        visits+=1
        if not isinstance(x,(np.ndarray,np.void)):return
        sh=tuple(x.shape) if hasattr(x,"shape") else ()
        dtype=x.dtype;cls=type(x).__name__
        kind=("structured" if dtype.names else dtype.kind)
        nodes[(p,sh,kind,cls)]+=1
        if dtype.names:
            for k in dtype.names:walk(x[k],p+"."+keyname(k),depth+1)
        elif dtype.kind=="O" and isinstance(x,np.ndarray):
            f=x.ravel()
            # Structural traversal only. Empty character/numeric values never accessed for output.
            if len(f)>64:trunc=True
            inds=np.unique(np.linspace(0,len(f)-1,min(64,len(f)),dtype=int)) if len(f) else []
            for i in inds:walk(f[i],p+"[]",depth+1)
    for k,x in data.items():
        if not k.startswith("__"):walk(x,keyname(k))
    r["schema_nodes"]=[{"path":p,"shape":list(s),"kind":k,"array_class":c,"count":n} for (p,s,k,c),n in nodes.items()][:160]
    r["distinct_schema_nodes"]=len(nodes);r["inspection_truncated"]=trunc or len(nodes)>160
    r["status"]="schema_read";return r
def clean_line(line):
    # Source provenance only: no literal paths, coordinates, dates, identifiers or comments.
    s=line.split("%",1)[0]
    s=re.sub(r"""'(?:[^']|'')*'|"(?:[^"]|"")*" """.strip(),"<string>",s)
    s=re.sub(r"(?<![A-Za-z_])[-+]?\d+\.\d+(?:[eE][-+]?\d+)?","<number>",s)
    s=re.sub(r"(?<![A-Za-z_])\d{2,}","<number>",s)
    if re.search(r"roost|cave|https?://|@|[A-Za-z]:\\",s,re.I):return ""
    return s.strip()[:250]
def source_audit(b):
    lines=b.decode("utf-8-sig",errors="replace").splitlines()
    out=[]
    for i,line in enumerate(lines,1):
        if line.lstrip().startswith("%"):continue
        if not re.search(r"gps|latitude|longitude|altitude|ellipsoid|height|interp|smooth|loess|readtable|load\(|dataAudio|sampleRate|timeZone|startTime|datenum|datetime",line,re.I):continue
        s=clean_line(line)
        if s:out.append({"line":i,"code":s})
    return {"lines":len(lines),"sanitized_relevant_code":out[:70],"relevant_count":len(out)}
def logger(b):
    txt=b.decode("utf-8-sig",errors="replace")
    lines=txt.splitlines();counts=collections.Counter();header=collections.Counter()
    for line in lines:
        s=line.strip()
        if not s:counts["empty"]+=1;continue
        # Only delimiter/type signatures, no source values.
        if re.search(r"(?i)\b(?:time|date|gps|latitude|longitude|altitude|height|sampling|sensor)\b",s):
            for t in tags(s):header[t]+=1
            counts["metadata_like"]+=1;continue
        if s.startswith("$GP") or s.startswith("$GN"):
            tag=s.split(",",1)[0]
            counts["nmea_"+(tag[3:6] if re.fullmatch(r"\$G[PN][A-Z]{3}",tag) else "other")]+=1;continue
        sep="comma" if "," in s else "tab" if "\t" in s else "space"
        v=s.split(",") if sep=="comma" else s.split("\t") if sep=="tab" else s.split()
        if len(v)>50:counts["wide_other"]+=1;continue
        mask=[bool(re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",p.strip())) for p in v]
        counts[f"{sep}:{len(v)}columns:{sum(mask)}numeric"]+=1
    return {"lines":len(lines),"line_format_counts":dict(counts.most_common(20)),"header_term_counts":dict(header)}
def mapping(b,members):
    w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    try:
        sh=w.worksheets[0];it=sh.values;head=next(it)
        labels=[str(x or "").strip() for x in head]
        fields=[{"index":i,"field":keyname(v),"tags":tags(v)} for i,v in enumerate(labels)]
        def norm(s):return str(s or "").strip().replace("\\","/").lstrip("./").casefold()
        byfull=collections.defaultdict(list);bybase=collections.defaultdict(list);bystem=collections.defaultdict(list)
        for i in members:
            p=norm(i.filename);base=PurePosixPath(p).name
            byfull[p].append(i);bybase[base].append(i);bystem[PurePosixPath(base).stem].append(i)
        def match(v):
            p=norm(v)
            if not p:return "missing",None
            for key,table in [(p,byfull),(PurePosixPath(p).name,bybase),(PurePosixPath(p).stem,bystem)]:
                if key in table:
                    if len(table[key])==1:return "unique_exact",table[key][0]
                    return "ambiguous",None
            return "unmatched",None
        rows=list(it);out={"rows":len(rows),"fields":fields,"matches":{}}
        for j,label in enumerate(labels):
            if not re.search(r"gps|audio",label,re.I):continue
            ctr=collections.Counter();matched=set()
            for row in rows:
                state,i=match(row[j] if j<len(row) else None)
                if i is not None:
                    matched.add(i.filename);t="native_name" if "raw" in i.filename.lower() else "other_name"
                    ctr[state+":"+PurePosixPath(i.filename).suffix.lower()+":"+t]+=1
                else:ctr[state]+=1
            out["matches"][keyname(label)]={"counts":dict(ctr),"distinct_matched_members":len(matched)}
        for j,label in enumerate(labels):
            if "species" not in label.lower():continue
            c=collections.Counter(str(row[j] or "").strip().casefold() for row in rows)
            out["species_exact_full_name_counts"]={k:int(c[k]) for k in sorted(KNOWN)}
            out["other_or_missing_species_rows"]=len(rows)-sum(c[k] for k in KNOWN)
        return out
    finally:w.close()
def archive(b):
    r={"mat":{},"logger":{},"source":[],"mapping":[],"apple_metadata_excluded":0}
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        infos=[i for i in z.infolist() if not i.is_dir()]
        assert len(infos)==178 and sum(i.file_size for i in infos)==95993482
        valid=[]
        for i in infos:
            name=PurePosixPath(i.filename)
            if "__MACOSX" in name.parts or name.name.startswith("._") or name.name.lower()==".ds_store":
                r["apple_metadata_excluded"]+=1;continue
            valid.append(i)
        r["substantive_members"]=len(valid)
        for i in valid:
            s=PurePosixPath(i.filename).suffix.lower()
            if s not in (".mat",".txt",".m",".xlsx"):continue
            raw=z.read(i)
            if raw.startswith(b"\x00\x05\x16\x07"):
                r["apple_metadata_excluded"]+=1;continue
            h=sha(raw)
            if s==".mat":
                kind="native_name" if "raw" in i.filename.lower() else "other_name"
                entry={"sha256":h,"kind":kind,"size":len(raw)}
                try:entry["schema"]=mat_schema(raw)
                except Exception as e:entry["schema"]={"status":"blocked",**err(e,"schema")}
                r["mat"][sha(i.filename.encode())[:16]]=entry
            elif s==".txt":
                r["logger"][sha(i.filename.encode())[:16]]={"sha256":h,"size":len(raw),**logger(raw)}
            elif s==".m" and h in SOURCE_SHAS:r["source"].append({"sha256":h,**source_audit(raw)})
            elif s==".xlsx" and h==MAPPING_SHA:r["mapping"].append({"sha256":h,**mapping(raw,valid)})
    return r
def main():
    r={"status":"schema_repair_only","numeric_outcomes_read":False,"files":{}}
    dest=OUT/"audit_v32_acoustic_gps_schema.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save()
    for k in FILES:
        try:
            b=fetch(FILES[k])
            r["files"][k]={"sha256":sha(b),"bytes":len(b),"published_hash_match":True,"audit":mat_schema(b) if k=="audio_mat" else archive(b)}
        except Exception as e:r["files"][k]={"status":"blocked",**err(e,"file")}
        save()
    # Compact console output; complete aggregate schema artifact separately.
    z=r["files"].get("data_zip",{}).get("audit",{})
    mats=z.get("mat",{})
    # Aggregate identical schema headers and status, with one representative per group.
    groups={}
    for e in mats.values():
        a=e["schema"];key=json.dumps([e["kind"],a.get("status"),[(x["name"],x["class"]) for x in a.get("header_variables",[])],a.get("errors")],sort_keys=True)
        if key not in groups:groups[key]={"count":0,"kind":e["kind"],"example":a}
        groups[key]["count"]+=1
    loggroups=collections.Counter()
    for l in z.get("logger",{}).values():
        loggroups.update(l["line_format_counts"])
    print(json.dumps({"status":r["status"],"audio_mat":r["files"].get("audio_mat"),
      "archive":{"apple_metadata_excluded":z.get("apple_metadata_excluded"),"substantive_members":z.get("substantive_members"),
       "mat_count":len(mats),"mat_schema_groups":list(groups.values()),
       "logger_count":len(z.get("logger",{})),"logger_format_counts":dict(loggroups.most_common(20)),
       "source":z.get("source"),"mapping":z.get("mapping")}},indent=2,allow_nan=False))
    return 0 if len(mats)>0 else 2
if __name__=="__main__":raise SystemExit(main())
