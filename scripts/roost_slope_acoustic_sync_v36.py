"""V36: exact identity normalization and bounded time-origin diagnostics.
Do not analyze acoustic outcomes, expose IDs, coordinates or timestamps, or optimize time offsets.
"""
import io,json,math,re,tempfile,zipfile,hashlib
from bisect import bisect_left
from collections import Counter,defaultdict
from pathlib import PurePosixPath
from datetime import datetime,timezone
from importlib.metadata import version
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from roost_fd_source_audit_v2 import OUT
from roost_slope_acoustic_decoder_v35 import read
from roost_slope_acoustic_gps_archive_v31 import FILES,fetch
from roost_slope_native_nmea_v33 import MAPSHA,load_mapping,norm,decode
from roost_slope_acoustic_gps_schema_v32 import SOURCE_SHAS,clean_line

KNOWN={"leptonycteris yerbabuenae","myotis myotis","myotis vivesi","rhinopoma microphyllum"}
START=datetime(2000,1,1,tzinfo=timezone.utc).timestamp()
END=datetime(2024,1,1,tzinfo=timezone.utc).timestamp()
def sha(x):return hashlib.sha256(x).hexdigest()
def scalar(x,depth=0):
    if depth>12:return None
    if isinstance(x,(str,np.str_)):return str(x)
    if isinstance(x,(list,tuple)):
        if len(x)==1:return scalar(x[0],depth+1)
        return None
    if isinstance(x,np.ndarray):
        if x.size==1:return scalar(x.ravel()[0],depth+1)
        if x.dtype.kind=="U" and x.ndim<=2 and (x.ndim==1 or min(x.shape)==1):
            vals=x.ravel().tolist()
            if all(isinstance(v,str) and len(v)==1 for v in vals):return "".join(vals)
    return None
def label(x):
    a=scalar(x)
    return norm(a) if a is not None else None
def type_signature(x):
    s=type(x).__name__
    if isinstance(x,np.ndarray):return s+":"+str(x.dtype.kind)+":"+str(x.ndim)+"d"
    return s
def number(x):
    try:
        a=float(x)
        return a if math.isfinite(a) else None
    except (TypeError,ValueError,OverflowError):return None
def quant(a):
    x=np.asarray(a,dtype=float);x=x[np.isfinite(x)]
    return dict(zip(["min","q25","median","q75","max"],map(float,np.quantile(x,[0,.25,.5,.75,1])))) if len(x) else {}
def spec_label(x):
    if x in KNOWN:return x
    if x is None:return "unreadable"
    return "unrecognized_"+sha(x.encode())[:12]
def read_meta(b):
    w=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
    try:
        it=w.worksheets[0].values;head=list(next(it));cols={str(x or "").strip():i for i,x in enumerate(head)}
        assert {"species","batName","timeZone"}<=set(cols)
        out={}
        for row in it:
            k=(norm(row[cols["species"]]),norm(row[cols["batName"]]))
            v=row[cols["timeZone"]]
            out[k]=number(v)
        return out
    finally:w.close()
def source_audit(b):
    out=[];meta=None
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for i in z.infolist():
            if i.is_dir() or "__MACOSX" in PurePosixPath(i.filename).parts:continue
            suf=PurePosixPath(i.filename).suffix.lower()
            if suf not in (".m",".xlsx"):continue
            raw=z.read(i);h=sha(raw)
            if h==MAPSHA:meta=read_meta(raw)
            if h not in SOURCE_SHAS:continue
            lines=raw.decode("utf-8-sig",errors="replace").splitlines()
            hits=[]
            for j,l in enumerate(lines,1):
                if not re.search(r"fileStartTime|timeInFile|ExtractAudioInfo|MatchAudioInfo2Data|datenum|x2mdate|timeZone|indGPS|audioAll|batName",l,re.I):continue
                clean=clean_line(l)
                if clean:hits.append({"line":j,"code":clean})
            out.append({"sha256":h,"matching_lines":hits[:65],"count":len(hits)})
    assert meta is not None
    return meta,out
def origins(x):
    # Fixed candidate units/epochs, independent of matching score.
    return {"matlab_datenum":(x-719529.)*86400.,
            "excel_serial_days":(x-25569.)*86400.,
            "unix_seconds":x,"unix_milliseconds":x/1000.}
def valid_date(x):return np.isfinite(x)&(x>=START)&(x<END)
def identity(a,m):
    ss=[label(x) for x in a["species"]]
    nn=[label(x) for x in a["batName"]]
    bare=defaultdict(list)
    for k in m:bare[k[1]].append(k)
    matched=[];ct=Counter();cats=defaultdict(Counter);ident=defaultdict(set)
    bareids=set()
    for s,n in zip(ss,nn):
        k=(s,n)
        if k in m:
            matched.append(k);ct["exact_pair"]+=1;ident[s].add(k)
        else:
            matched.append(None)
            ct["unmatched_pair"]+=1
        if n in bare and len(bare[n])==1:
            k2=bare[n][0];bareids.add(k2);ct["unique_bare_name"]+=1
            cats[spec_label(s)][k2[0]]+=1
        elif n in bare:ct["ambiguous_bare_name"]+=1
        else:ct["unmatched_bare_name"]+=1
    return matched,{"rows":len(a),"type_signatures":{"species":dict(Counter(type_signature(x) for x in a["species"])),
       "batName":dict(Counter(type_signature(x) for x in a["batName"]))},
       "species_labels":dict(Counter(spec_label(x) for x in ss)),
       "unreadable_species_rows":sum(x is None for x in ss),"unreadable_batName_rows":sum(x is None for x in nn),
       "match_counts":dict(ct),"distinct_exact_identities":sum(len(v) for v in ident.values()),
       "exact_identities_by_species":{s:len(v) for s,v in ident.items()},
       "exact_rows_by_species":dict(Counter(k[0] for k in matched if k is not None)),
       "unique_bare_name_identities":len(bareids),
       "bare_name_species_concordance":{s:dict(v) for s,v in cats.items()}}
def coverage(t,chains):
    # Native fix times are internal only. Input t is unique file start UTC seconds.
    r=Counter()
    if not len(t):return r
    arrays=[np.array([x[0] for x in c],dtype=float)/1e6 for c in chains if len(c)]
    if not arrays:return r
    all_times=np.unique(np.concatenate(arrays))
    starts=np.array([a[0] for a in arrays]);ends=np.array([a[-1] for a in arrays])
    order=np.argsort(starts);starts=starts[order];ends=np.maximum.accumulate(ends[order])
    p=np.searchsorted(all_times,t);i=np.clip(p,0,len(all_times)-1);j=np.clip(p-1,0,len(all_times)-1)
    dt=np.minimum(np.abs(all_times[i]-t),np.abs(all_times[j]-t))
    q=np.searchsorted(starts,t,side="right")-1
    chain_ok=(q>=0)&(ends[np.maximum(q,0)]>=t)
    r["files"]+=len(t);r["within_native_range"]+=int(((t>=all_times[0])&(t<=all_times[-1])).sum())
    r["within_valid_chain_span"]+=int(chain_ok.sum())
    for sec in (5,15,30):r["nearest_fix_le"+str(sec)+"s"]+=int((dt<=sec).sum())
    return r
def gps_source():
    b=fetch(FILES["data_zip"])
    matched=defaultdict(list)
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        infos=[i for i in z.infolist() if not i.is_dir() and "__MACOSX" not in PurePosixPath(i.filename).parts and not PurePosixPath(i.filename).name.startswith("._") and PurePosixPath(i.filename).name.lower()!=".ds_store"]
        mappings=[z.read(i) for i in infos if PurePosixPath(i.filename).suffix.lower()==".xlsx"]
        m=load_mapping(next(x for x in mappings if sha(x)==MAPSHA))
        for i in infos:
            if PurePosixPath(i.filename).suffix.lower()!=".txt":continue
            raw=z.read(i)
            if raw.startswith(b"\x00\x05\x16\x07"):continue
            pp=[norm(p) for p in PurePosixPath(i.filename).parts[:-1]]
            ks=[k for k in m if any(pp[j]==k[0] and pp[j+1]==k[1] for j in range(len(pp)-1))]
            assert len(ks)==1
            matched[ks[0]].append(raw)
        assert len(matched)==22 and all(len(x)==1 for x in matched.values())
    return m,matched


def run():
    out={"status":"identity_clock_diagnostic","numeric_acoustic_outcomes_analyzed":False,"versions":{k:version(k) for k in ("mat-io","numpy","pandas","scipy","h5py")}}
    b=fetch(FILES["data_zip"])
    meta,code=source_audit(b)
    m,tracks=gps_source()
    assert len(m)==len(meta)==25 and set(m)==set(meta)
    out["source_static_audit"]=code
    out["timezone_metadata_by_species"]={s:dict(Counter("missing_or_outside_range" if v is None or abs(v)>14 else str(v) for k,v in meta.items() if k[0]==s)) for s in sorted(KNOWN)}
    with tempfile.TemporaryDirectory() as td:
        data=read(fetch(FILES["audio_mat"]),td,"audio.mat")
    a=data["audioAll"]
    assert isinstance(a,pd.DataFrame) and a.shape==(74782,29)
    assert {"species","batName","fileStartTime","timeInFile","ipi","indGPS"}<=set(a.columns)
    out["audio_shape"]=list(a.shape)
    keys,out["identity"]=identity(a,m)
    st=pd.to_numeric(a["fileStartTime"],errors="coerce").to_numpy(float)
    ts=origins(st)
    out["file_start_origin_counts"]={k:int(valid_date(v).sum()) for k,v in ts.items()}
    out["file_start_finite"]=int(np.isfinite(st).sum())
    # timeInFile is timing metadata only, not IPI or call outcome.
    ti=pd.to_numeric(a["timeInFile"],errors="coerce").to_numpy(float)
    out["time_in_file_unit_diagnostic"]={"finite":int(np.isfinite(ti).sum()),"negative":int((ti<0).sum()),
       "zero":int((ti==0).sum()),**{"within_0_"+str(u):int(((ti>=0)&(ti<=u)).sum()) for u in (.5,5,500,5000)}}
    plausible=[k for k,v in ts.items() if int(valid_date(v).sum())==int(np.isfinite(st).sum())]
    out["plausible_full_origins"]=plausible
    if len(plausible)!=1:out["timing_status"]="ambiguous_origin";return out
    if not any(k is not None for k in keys):out["timing_status"]="no_exact_identity_matches";return out
    val=ts[plausible[0]]
    file_starts=defaultdict(set)
    for k,t in zip(keys,val):
        if k is not None and np.isfinite(t) and START<=t<END:file_starts[k].add(float(t))
    r=defaultdict(lambda:defaultdict(Counter));matched_ids=Counter()
    for k,starts in file_starts.items():
        if k not in tracks or m[k]["gps"]!="1":continue
        chains,_,*_=decode(tracks[k][0])
        if not chains:continue
        s=k[0];matched_ids[s]+=1;t=np.array(sorted(starts))
        r[s]["UTC_as_stored"].update(coverage(t,chains))
        off=meta[k]
        if off is not None and abs(off)<=14:
            r[s]["subtract_numeric_timezone_hours"].update(coverage(t-off*3600,chains))
            r[s]["add_numeric_timezone_hours"].update(coverage(t+off*3600,chains))
    out["GPS_linked_exact_identities_by_species"]=dict(matched_ids)
    out["timing_diagnostic_by_species"]={s:{k:dict(v) for k,v in models.items()} for s,models in r.items()}
    out["timing_status"]="diagnostic_only_no_clock_convention_admitted"
    return out
def test():
    assert label(np.array([np.array(["Myotis myotis"])],dtype=object))=="myotis myotis"
    assert scalar(np.array(["b","a","t"]))=="bat"
    assert scalar(1) is None
    assert origins(np.array([719529.]))["matlab_datenum"][0]==0
def main():
    dest=OUT/"audit_v36_acoustic_sync.json"
    test()
    try:r=run();r["synthetic_tests"]="pass"
    except Exception as e:r={"status":"blocked","error_type":type(e).__name__,"synthetic_tests":"pass"}
    dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    print(dest.read_text())
    return 0 if r["status"]=="identity_clock_diagnostic" else 2
if __name__=="__main__":raise SystemExit(main())
