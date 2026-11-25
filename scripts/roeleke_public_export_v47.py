"""V47: previously retrieved public export only; frozen V46 estimator."""
import hashlib,io,json,pathlib,csv,re
import numpy as np
import pandas as pd
import roeleke_functional_space_v46 as v46
from bayer_field_join_v17 import fetch
from functional_space_external_v45 import url_same
OUT=pathlib.Path("results/roeleke_public_export_v47.json")
URL="https://repository.zalf.de/datasets/geonode:foraging_strategies_study/dataset_download"
SHA="a2a3a9cc02b718e729aba4342a81d0e025c4809234b8dd6b7f88fc1ecc815186"
SIZE=2398326
def parse_diagnostic(b):
    o={"format":"unknown"}
    if b.startswith(b"PK\x03\x04"):o["format"]="ZIP";return o
    try:s=b.decode("utf-8-sig")
    except UnicodeDecodeError:o["format"]="non-UTF8";return o
    if s.lstrip().startswith("<"):o["format"]="markup";return o
    if s.lstrip().startswith(("{","[")):o["format"]="JSON";return o
    o["format"]="text"
    for sep in (",",";","\t"):
        try:
            r=csv.reader(io.StringIO(s),delimiter=sep);h=next(r)
            # Header only; do not emit candidate raw record values.
            if len(h)>2 and len(h)<=100 and all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_. ():-]{0,90}",v.strip()) for v in h):
                o.setdefault("header_candidates",[]).append({"delimiter":sep,"headers":[v46.canonical(v) for v in h]})
        except Exception:pass
    return o
def exact_export(routes,meta):
    # No other routes, in particular no denied original asset.
    r={"route":"previously_retrieved_public_export"}
    try:
        assert meta["download_url"]==URL and ("dataset_download",URL) in routes
        assert "download_resourcebase" in meta["perms"] and meta["is_published"]
        b,final=fetch(url_same(URL,v46.BASE),SIZE)
        r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        assert len(b)==SIZE and r["sha256"]==SHA,"V45 export identity drift"
        r["matches_V45_export"]=True
        d,sep=v46.parse_csv(b)
        r.update(status="CSV_PARSED",rows=len(d),headers=list(d.columns),delimiter=sep)
        return d,"dataset_download",[r]
    except Exception as e:
        r.update(status="STOP_ROUTE",error=type(e).__name__+":"+str(e)[:180])
        if r.get("matches_V45_export"):r["structural_diagnostic"]=parse_diagnostic(b)
        return None,None,[r]
def run():
    v46.fetch_table=exact_export
    r=v46.run()
    r["version"]="V47"
    r["source_boundary"]="Only exact previously retrieved public export; restricted original asset not requested; V46 estimator unchanged."
    return r
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)[:500]}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
