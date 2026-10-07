#!/usr/bin/env python3
"""Schema-only inspection of the adult vocal PAF source.

No acoustic feature values are summarized or printed.
"""

from __future__ import annotations
from pathlib import Path
import io, json, re, tempfile, urllib.parse, urllib.request, zipfile
from collections import Counter
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/"PAF_SCHEMA_AUDIT_V1.json"
OUTMD=HERE/"PAF_SCHEMA_AUDIT_V1.md"

DATASET="h5ff9vv5pc"
VERSION=1
TARGET="PAF_AllBatsData.mat"
CODE_FILES=(
    "DeafBats11_PCARegularizedPermutationDFA.m",
    "DeafBats8_ParsingVocalSpace.m",
    "DeafBats3_AcousticMeasurements.m",
)
FILE_URL=(
    f"https://data.mendeley.com/api/datasets/{DATASET}/files?"
    + urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
)
HEADERS={"User-Agent":"Mozilla/5.0 batter-paf-schema/1.0","Accept":"application/json,*/*"}

def get_bytes(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=240) as r:
        return r.read()

def get_json(url):
    return json.loads(get_bytes(url,"application/json").decode("utf-8"))

def rows(x):
    if isinstance(x,list): return x
    if isinstance(x,dict):
        for k in ("items","files","results","data"):
            if isinstance(x.get(k),list): return x[k]
    raise RuntimeError("unknown file-list envelope")

def dlurl(row):
    return (row.get("content_details") or {}).get("download_url") or row.get("download_url")

def find_files():
    rr=rows(get_json(FILE_URL))
    by={(x.get("filename") or x.get("name")):x for x in rr if isinstance(x,dict)}
    need=[TARGET,*CODE_FILES]
    missing=[x for x in need if x not in by]
    if missing: raise RuntimeError(f"missing public files: {missing}")
    return by

def safe_scalar(v):
    # Structural labels only; no numeric acoustic features.
    if isinstance(v,bytes):
        return v.decode("utf-8","replace")
    if isinstance(v,(str,np.str_)):
        return str(v)
    if isinstance(v,(int,np.integer)):
        return int(v)
    if isinstance(v,(float,np.floating)) and np.isfinite(v):
        return int(v) if float(v).is_integer() else float(v)
    return str(v)

def mat_schema(data):
    import scipy.io
    out={"loaded_type":None,"fields":[],"field_shapes":{},"label_summaries":{},"container":None}
    # MATLAB v7.3 files are HDF5; inspect structure only in that case.
    if data[:8] == b"\\x89HDF\\r\\n\\x1a\\n":
        import h5py
        out["container"]="hdf5"
        with h5py.File(io.BytesIO(data),"r") as h:
            out["hdf5_top_keys"]=sorted(h.keys())
            for k in h.keys():
                obj=h[k]
                out["field_shapes"][k]=list(getattr(obj,"shape",()))
        return out

    out["container"]="mat_v5"
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data); tf.flush()
        # Do not call whosmat: some MATLAB table/object headers trigger a SciPy
        # shape-reader bug even though loadmat can still decode the object.
        m=scipy.io.loadmat(
            tf.name,
            squeeze_me=True,
            struct_as_record=False,
            simplify_cells=True,
        )

    keys=[k for k in m if not k.startswith("__")]
    if not keys: return out
    # Prefer documented PAF_Tbl-like object; otherwise largest nonmeta variable by schema.
    key=next((k for k in keys if "PAF" in k.upper() or "TBL" in k.upper()),keys[0])
    obj=m[key]
    out["selected_variable"]=key
    out["loaded_type"]=type(obj).__name__

    if isinstance(obj,dict):
        out["fields"]=sorted(obj.keys())
        for k,v in obj.items():
            out["field_shapes"][k]=list(np.shape(v))
            if re.search(r"(bat|id|hearing|deaf|sex|group|class|type|call)",k,re.I):
                a=np.asarray(v,dtype=object).reshape(-1)
                vals=[]
                for x in a:
                    try:
                        vals.append(safe_scalar(x))
                    except Exception:
                        pass
                # structural categorical summary only
                c=Counter(map(str,vals))
                if len(c)<=100:
                    out["label_summaries"][k]={"n":len(vals),"levels":dict(sorted(c.items()))}
    else:
        fields=getattr(obj,"_fieldnames",None)
        if fields:
            out["fields"]=sorted(fields)
            for k in fields:
                v=getattr(obj,k)
                out["field_shapes"][k]=list(np.shape(v))
                if re.search(r"(bat|id|hearing|deaf|sex|group|class|type|call)",k,re.I):
                    a=np.asarray(v,dtype=object).reshape(-1)
                    c=Counter(map(str,[safe_scalar(x) for x in a]))
                    if len(c)<=100:
                        out["label_summaries"][k]={"n":len(a),"levels":dict(sorted(c.items()))}
    return out

def code_schema(data,name):
    text=data.decode("utf-8","replace")
    text=re.sub(r"%[^\n]*","",text)
    # structural identifiers and strings only
    ids=sorted(set(re.findall(r"\b[A-Za-z]\w*\b",text)))
    relevant=[x for x in ids if re.search(r"(PAF|Bat|Hearing|Deaf|Sex|Group|Acoustic|Feature|Variable|Call|Tbl|Table)",x,re.I)]
    strings=sorted(set(re.findall(r"""['"]([^'"\n]{1,200})['"]""",text)))
    relstrings=[x for x in strings if re.search(r"(PAF|Bat|Hearing|Deaf|Sex|Group|Acoustic|Feature|Call)",x,re.I)]
    # literal source feature-name blocks if present
    featureish=[x for x in strings if re.search(r"(Duration|RMS|Saliency|Fund|kHz|kurt|skew|ent|SQ|Amp)",x,re.I)]
    return {
        "filename":name,
        "relevant_identifiers":relevant[:1000],
        "relevant_strings":relstrings[:1000],
        "featureish_strings":featureish[:200],
    }

def render(r):
    lines=[
        "# Auditory-feedback PAF schema audit v1","",
        "**STRUCTURE ONLY — NO ACOUSTIC FEATURE VALUES REPORTED.**","",
        f"- selected MAT variable: \`{r['mat'].get('selected_variable')}\`",
        f"- loaded type: \`{r['mat'].get('loaded_type')}\`",
        f"- fields: {r['mat'].get('fields')}","",
        "## Categorical structural fields","",
    ]
    for k,v in r["mat"].get("label_summaries",{}).items():
        lines.append(f"- {k}: n={v['n']} levels={v['levels']}")
    lines += ["","## Field shapes",""]
    for k,v in r["mat"].get("field_shapes",{}).items():
        lines.append(f"- {k}: {v}")
    lines += ["","## Code-derived fixed feature strings",""]
    allf=[]
    for x in r["code"]:
        allf.extend(x["featureish_strings"])
    for x in sorted(set(allf)):
        lines.append(f"- {x}")
    lines += ["","No acoustic numeric value, treatment effect, identity score, or dispersion was calculated.",""]
    return "\n".join(lines)

def main():
    by=find_files()
    matdata=get_bytes(dlurl(by[TARGET]))
    m=mat_schema(matdata)
    codes=[]
    for name in CODE_FILES:
        codes.append(code_schema(get_bytes(dlurl(by[name])),name))
    result={
        "version":1,
        "source":"10.17632/h5ff9vv5pc.1",
        "mat":m,
        "code":codes,
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    OUTMD.write_text(render(result)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
