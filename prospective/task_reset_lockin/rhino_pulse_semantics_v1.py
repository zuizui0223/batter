#!/usr/bin/env python3
"""Pulse-field semantics probe for authoritative Rhino CSVs.

No bat-level or environment-level pulse comparison is calculated.
"""
from __future__ import annotations
import collections,csv,hashlib,io,json,math,urllib.request
import importlib.util
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

def parse_pulse(b):
    reader=csv.DictReader(io.StringIO(b.decode("utf-8-sig",errors="strict")))
    if reader.fieldnames!=["Time (Seconds)","X","Y","Z","pulse"]:
        raise RuntimeError("header drift")
    rows=[]; tokens=[]
    for row in reader:
        ts=(row.get("Time (Seconds)") or "").strip()
        ps=(row.get("pulse") or "").strip()
        try:t=float(ts)
        except Exception:t=math.nan
        rows.append((t,ps))
        if ps!="":tokens.append(ps)
    return rows,tokens

def main():
    article=P.get_article()
    all_tokens=[]
    files=[]
    for f in article.get("files") or []:
        fid=int(f["id"]); name=f.get("name") or ""
        if not P.PAT.match(name) or not (P.RHINO_MIN<=fid<=P.RHINO_MAX):
            continue
        size=int(f["size"])
        b=P.get_bytes(f["download_url"],size+4096)
        if len(b)!=size:raise RuntimeError(f"size mismatch {name}")
        expected=f.get("computed_md5") or f.get("supplied_md5")
        if expected and hashlib.md5(b).hexdigest()!=expected:
            raise RuntimeError(f"md5 mismatch {name}")
        rows,tokens=parse_pulse(b)
        missing=len(rows)-len(tokens)
        nonzero=0; numeric=[]; changes=0; prev=None
        for tok in tokens:
            try:
                x=float(tok)
                if math.isfinite(x):
                    numeric.append(x)
                    if x!=0:nonzero+=1
            except Exception:
                pass
            if prev is not None and tok!=prev:changes+=1
            prev=tok
        files.append({
          "name":name,
          "n_rows":len(rows),
          "missing_pulse":missing,
          "nonmissing_pulse":len(tokens),
          "numeric_pulse":len(numeric),
          "nonzero_pulse":nonzero if len(numeric)==len(tokens) else None,
          "nonzero_proportion":(nonzero/len(numeric)) if numeric and len(numeric)==len(tokens) else None,
          "successive_token_changes":changes,
        })
        all_tokens.extend(tokens)

    uniq=sorted(set(all_tokens))
    numeric=[]
    for tok in all_tokens:
        try:
            x=float(tok)
            if math.isfinite(x):numeric.append(x)
        except Exception:pass

    summary={
      "contract":"RHINO_PULSE_SEMANTICS_OPENING_V1.md",
      "status":"STRUCTURAL_SEMANTICS_ONLY",
      "bat_level_contrasts_calculated":False,
      "n_files":len(files),
      "n_rows":sum(x["n_rows"] for x in files),
      "missing_pulse":sum(x["missing_pulse"] for x in files),
      "nonmissing_pulse_tokens":len(all_tokens),
      "unique_nonmissing_token_count":len(uniq),
      "all_nonmissing_numeric":len(numeric)==len(all_tokens),
      "zero_count":sum(x==0 for x in numeric) if len(numeric)==len(all_tokens) else None,
      "nonzero_count":sum(x!=0 for x in numeric) if len(numeric)==len(all_tokens) else None,
      "files":files,
    }
    if len(uniq)<=20:
        summary["unique_tokens"]=uniq
    elif len(numeric)==len(all_tokens) and numeric:
        arr=np.asarray(numeric,float)
        summary["numeric_min"]=float(np.min(arr))
        summary["numeric_max"]=float(np.max(arr))
        summary["numeric_q01"]=float(np.quantile(arr,.01))
        summary["numeric_median"]=float(np.quantile(arr,.5))
        summary["numeric_q99"]=float(np.quantile(arr,.99))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
