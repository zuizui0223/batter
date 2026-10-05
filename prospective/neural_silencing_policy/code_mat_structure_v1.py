#!/usr/bin/env python3
"""Source-code and MAT-directory structural opening for neural-silencing programme."""
from __future__ import annotations
import hashlib,json,re,urllib.parse,urllib.request
from pathlib import Path
import tempfile
import scipy.io
import h5py

REC="https://zenodo.org/records/13857870/files"
FILES={
 "DREADDs_allbatstrajectory_updated.m":("1690084f3a80774d1fbfcf6fdc03877d",18934),
 "DREADD_OverallBehavior_updatedJL.m":("6709265a6a054aea5521708a290353a8",31878),
 "jane_trajectorydata.mat":("23e901165feff18b667d734760f67637",439086),
 "jason_trajectorydata.mat":("d70e3b01284b56a95d91b361991dd7e7",347712),
 "bea_trajectorydata.mat":("c23a4591118ce99ef706cf5022aae254",458612),
 "Dreadds_behav_structure.mat":("0db9b5e06097e7d1a840c7c53c4ac601",10415),
}
UA="batter-neural-silencing-structure/1.0"

def get(name,size):
    url=f"{REC}/{urllib.parse.quote(name)}?download=1"
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=90) as r:b=r.read(size+1)
    if len(b)!=size:raise RuntimeError(f"size mismatch {name}: {len(b)} != {size}")
    md5=hashlib.md5(b).hexdigest()
    if md5!=FILES[name][0]:raise RuntimeError(f"md5 mismatch {name}")
    return b

def code_summary(name,b):
    s=b.decode("utf-8",errors="replace")
    lines=s.splitlines()
    # Source-architecture lines only; retain code text but omit pure plotting cosmetics.
    pats=[
      r"load\s*\(",r"load\s+",r"jane",r"jason",r"bea",r"stella",
      r"saline",r"ligand",r"baseline",r"dread",r"sham",
      r"traj",r"trajectory",r"session",r"trial",r"bat",
      r"condition",r"treatment",r"pos",r"xyz",r"coordinate",
      r"success",r"clip",r"behavior",r"behav"
    ]
    rx=re.compile("|".join(pats),re.I)
    hits=[]
    for i,line in enumerate(lines,1):
        if rx.search(line):
            hits.append({"line":i,"text":line[:500]})
    return {
      "filename":name,"n_lines":len(lines),
      "source_text_opened_in_full":True,
      "matched_architecture_lines":hits,
    }

def mat_summary(name,b):
    with tempfile.NamedTemporaryFile(suffix=".mat") as f:
        f.write(b);f.flush()
        try:
            rows=scipy.io.whosmat(f.name)
            return {"filename":name,"mat_version":"pre_v7_3_or_scipy_readable",
                    "values_loaded":False,
                    "variables":[{"name":n,"shape":list(sh),"matlab_class":cl} for n,sh,cl in rows]}
        except Exception as e:
            try:
                out=[]
                with h5py.File(f.name,"r") as h:
                    def visit(n,obj):
                        if isinstance(obj,h5py.Dataset):
                            out.append({"path":n,"kind":"dataset","shape":list(obj.shape),"dtype":str(obj.dtype)})
                        else:
                            out.append({"path":n,"kind":"group"})
                    h.visititems(visit)
                return {"filename":name,"mat_version":"hdf5_v7_3",
                        "values_loaded":False,"objects":out}
            except Exception as e2:
                return {"filename":name,"mat_version":"unreadable_metadata",
                        "values_loaded":False,"error":type(e).__name__+":"+str(e),
                        "hdf5_error":type(e2).__name__+":"+str(e2)}

def main():
    codes=[];mats=[]
    for name,(md5,size) in FILES.items():
        b=get(name,size)
        if name.endswith(".m"):codes.append(code_summary(name,b))
        else:mats.append(mat_summary(name,b))
    print(json.dumps({
      "contract":"CODE_MAT_STRUCTURE_CONTRACT_V1.md",
      "numeric_mat_values_opened":False,
      "files_verified":list(FILES),
      "code":codes,
      "mat_metadata":mats,
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
