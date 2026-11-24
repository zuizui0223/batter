"""V35: pinned MCOS decoder, structural inspection only."""
import io,json,tempfile,zipfile,hashlib,re
from collections import Counter
from pathlib import Path,PurePosixPath
from importlib.metadata import version
import numpy as np
import pandas as pd
from matio import load_from_mat,save_to_mat
from roost_fd_source_audit_v2 import OUT
from roost_slope_acoustic_gps_archive_v31 import FILES,fetch,keyname,tags
from roost_slope_native_nmea_v33 import MAPSHA,load_mapping,norm
def sha(b):return hashlib.sha256(b).hexdigest()
def read(b,folder,name):
    p=Path(folder)/name;p.write_bytes(b)
    return load_from_mat(str(p),raw_data=False)
def inspect(obj,m):
    nodes=[];tables=[];seen=set();visits=0
    def walk(x,p,depth):
        nonlocal visits
        if depth>9 or visits>=1200:return
        visits+=1
        if isinstance(x,(dict,list,tuple,np.ndarray,pd.DataFrame)):
            if id(x) in seen:return
            seen.add(id(x))
        if isinstance(x,pd.DataFrame):
            cols=[]
            for i,c in enumerate(x.columns):
                s=x.iloc[:,i]
                cols.append({"name":keyname(c),"tags":tags(c),"dtype":str(s.dtype),"nonmissing":int(s.notna().sum())})
            r={"path":p,"rows":len(x),"columns":cols,"index_dtype":str(x.index.dtype)}
            cs={str(c).strip().casefold():c for c in x.columns}
            if "species" in cs and "batname" in cs:
                ct=Counter();ids=set()
                for s,a in zip(x[cs["species"]],x[cs["batname"]]):
                    k=(norm(s),norm(a))
                    if k in m:ct[k[0]]+=1;ids.add(k)
                    else:ct["unmatched"]+=1
                r["exact_identity_matches"]={"rows_by_species":dict(ct),"distinct_workbook_identities":len(ids),
                    "identities_by_species":dict(Counter(k[0] for k in ids))}
            tables.append(r);return
        if isinstance(x,dict):
            for k,v in x.items():
                if not str(k).startswith("__"):walk(v,p+"."+keyname(k),depth+1)
        elif isinstance(x,np.void) and x.dtype.names:
            for k in x.dtype.names:walk(x[k],p+"."+keyname(k),depth+1)
        elif isinstance(x,np.ndarray):
            nodes.append({"path":p,"shape":list(x.shape),"dtype":str(x.dtype),"class":type(x).__name__})
            if x.dtype.names:
                for k in x.dtype.names:walk(x[k],p+"."+keyname(k),depth+1)
            elif x.dtype.kind=="O":
                for j in np.unique(np.linspace(0,x.size-1,min(x.size,64),dtype=int)) if x.size else []:walk(x.ravel()[j],p+"[]",depth+1)
        elif isinstance(x,(list,tuple)):
            for v in x[:64]:walk(v,p+"[]",depth+1)
        elif hasattr(x,"properties"):
            nodes.append({"path":p,"class":type(x).__name__,"opaque_class":keyname(getattr(x,"classname","unknown"))})
            # Unknown object properties remain opaque; do not reinterpret data.
    walk(obj,"root",0)
    return {"tables":tables[:64],"nodes":nodes[:100],"visits":visits,"truncated":visits>=1200 or len(tables)>64 or len(nodes)>100}
def main():
    out={"status":"acoustic_schema_only","versions":{k:version(k) for k in ("mat-io","numpy","pandas","scipy","h5py","openpyxl","requests")},
        "numeric_outcomes_analyzed":False,"files":{}}
    dest=OUT/"audit_v35_acoustic_decoder.json"
    def save():dest.write_text(json.dumps(out,indent=2,allow_nan=False))
    save()
    with tempfile.TemporaryDirectory() as td:
        try:
            p=Path(td)/"synthetic.mat"
            f=pd.DataFrame({"time":pd.date_range("2020-01-01",periods=3,freq="s"),"value":[1.,2.,3.]})
            save_to_mat(str(p),{"synthetic":f},version="v7")
            x=load_from_mat(str(p),raw_data=False)
            out["synthetic_test"]="pass" if isinstance(x.get("synthetic"),pd.DataFrame) and x["synthetic"].shape==(3,2) else "shape_mismatch"
        except Exception as e:out["synthetic_test"]="blocked:"+type(e).__name__
        save()
        try:
            b=fetch(FILES["data_zip"])
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                infos=[i for i in z.infolist() if not i.is_dir() and "__MACOSX" not in PurePosixPath(i.filename).parts and not PurePosixPath(i.filename).name.startswith("._") and PurePosixPath(i.filename).name.lower()!=".ds_store"]
                m=load_mapping(next(z.read(i) for i in infos if PurePosixPath(i.filename).suffix.lower()==".xlsx" and sha(z.read(i))==MAPSHA))
                raw=[i for i in infos if i.filename.lower().endswith(".mat") and "raw" in i.filename.lower()]
                processed=[i for i in infos if i.filename.lower().endswith(".mat") and "raw" not in i.filename.lower()]
                assert len(raw)==len(processed)==22
                inputs={"native_example":z.read(raw[0]),"processed_example":z.read(processed[0]),"audio":fetch(FILES["audio_mat"])}
            for k,b in inputs.items():
                r={"sha256":sha(b),"bytes":len(b)}
                try:r["schema"]=inspect(read(b,td,k+".mat"),m);r["status"]="decoded"
                except Exception as e:r["status"]="blocked";r["error_type"]=type(e).__name__
                out["files"][k]=r;save()
        except Exception as e:out["status"]="source_blocked";out["error_type"]=type(e).__name__;save()
    print(dest.read_text())
    return 0 if out["files"].get("audio",{}).get("status")=="decoded" else 2
if __name__=="__main__":raise SystemExit(main())
