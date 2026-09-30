#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, re
from pathlib import Path
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/nyctalus_rsf_context_audit/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/nyctalus_rsf_context_audit/result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/nyctalus_rsf_context_audit/RESULT_V1.md"
UA={"User-Agent":"batter-nyctalus-rsf-context-audit-v1/1.0"}

def norm(x):
    return re.sub(r"[^a-z0-9]+","_",str(x).strip().lower()).strip("_")

def fetch_file(record_id,name):
    meta=requests.get(f"https://zenodo.org/api/records/{record_id}",headers=UA,timeout=90)
    meta.raise_for_status()
    rec=meta.json()
    target=None
    for f in rec.get("files",[]):
        if (f.get("key") or f.get("filename"))==name:
            target=f;break
    if target is None:
        raise RuntimeError(f"missing file {name}")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=UA,timeout=240)
    r.raise_for_status()
    raw=r.content
    return raw,hashlib.sha256(raw).hexdigest()

def find_xy(cols):
    bynorm={norm(c):c for c in cols}
    if "x" in bynorm and "y" in bynorm:
        return bynorm["x"],bynorm["y"]
    xs=[c for c in cols if norm(c) in {"utm_x","easting","xcoord","x_coord"}]
    ys=[c for c in cols if norm(c) in {"utm_y","northing","ycoord","y_coord"}]
    if xs and ys:
        return xs[0],ys[0]
    raise RuntimeError(f"could not determine x/y columns from {cols}")

def main():
    c=json.loads(CONTRACT.read_text())
    rid=int(c["source"]["record_id"])
    obs_raw,obs_sha=fetch_file(rid,c["source"]["observed_file"])
    rsf_raw,rsf_sha=fetch_file(rid,c["source"]["rsf_file"])

    obs=pd.read_csv(io.BytesIO(obs_raw),dtype=str,low_memory=False)
    rsf=pd.read_csv(io.BytesIO(rsf_raw),dtype=str,low_memory=False)

    # Fail closed: strip any vertical-like columns before all summaries.
    obs_safe=[x for x in obs.columns if "height" not in norm(x) and "alt" not in norm(x)]
    rsf_safe=[x for x in rsf.columns if "height" not in norm(x) and "alt" not in norm(x)]
    obs=obs.loc[:,obs_safe].copy()
    rsf=rsf.loc[:,rsf_safe].copy()

    ox,oy=find_xy(obs.columns)
    rx,ry=find_xy(rsf.columns)
    obs_x=pd.to_numeric(obs[ox],errors="coerce")
    obs_y=pd.to_numeric(obs[oy],errors="coerce")
    rsf_x=pd.to_numeric(rsf[rx],errors="coerce")
    rsf_y=pd.to_numeric(rsf[ry],errors="coerce")
    omask=obs_x.notna()&obs_y.notna()
    rmask=rsf_x.notna()&rsf_y.notna()

    obs_pairs=list(zip(obs_x[omask].astype(float),obs_y[omask].astype(float)))
    rsf_pairs=list(zip(rsf_x[rmask].astype(float),rsf_y[rmask].astype(float)))
    rsf_set=set(rsf_pairs)
    exact_matches=sum(p in rsf_set for p in obs_pairs)

    obs_round=[(round(a,3),round(b,3)) for a,b in obs_pairs]
    rsf_round=set((round(a,3),round(b,3)) for a,b in rsf_pairs)
    rounded_matches=sum(p in rsf_round for p in obs_round)

    pair_counts=pd.Series(rsf_pairs).value_counts()
    matched_counts=[int(pair_counts.get(p,0)) for p in obs_pairs if p in rsf_set]

    keywords=("roost","wka","turb","clc","forest","land","habitat","dist","water","mead","agri","city","wet","shrub","rotor")
    candidate_cols=[
        col for col in rsf.columns
        if col not in {rx,ry}
        and any(k in norm(col) for k in keywords)
    ]

    low_card={}
    for col in rsf.columns:
        if col in {rx,ry}:
            continue
        vals=rsf[col].dropna().astype(str).str.strip()
        vals=vals[vals!=""]
        nunq=int(vals.nunique())
        if 1<=nunq<=20:
            low_card[col]={
                "nonempty_n":int(len(vals)),
                "unique_n":nunq,
                "values":sorted(vals.unique().tolist())[:20]
            }

    common_cols=sorted(set(obs.columns)&set(rsf.columns))
    key_audit={}
    for keys in [["bat_id","trackid","utc"],["id","trackid","utc"],["bat_id","utc"],["id","utc"],["trackid","utc"]]:
        if all(k in obs.columns and k in rsf.columns for k in keys):
            o=set(map(tuple,obs[keys].astype(str).itertuples(index=False,name=None)))
            rr=set(map(tuple,rsf[keys].astype(str).itertuples(index=False,name=None)))
            key_audit["+".join(keys)]={
                "observed_unique_keys":len(o),
                "rsf_unique_keys":len(rr),
                "observed_keys_found_in_rsf":sum(x in rr for x in o),
                "fraction":sum(x in rr for x in o)/len(o) if o else None
            }

    response_counts={}
    response_used_match=None
    if "response_rvso" in rsf.columns:
        response_counts={str(k):int(v) for k,v in rsf["response_rvso"].astype(str).value_counts(dropna=False).items()}
        used=rsf[rsf["response_rvso"].astype(str)=="1"].copy()
        ux=pd.to_numeric(used[rx],errors="coerce")
        uy=pd.to_numeric(used[ry],errors="coerce")
        um=ux.notna()&uy.notna()
        uset=set(zip(ux[um].astype(float),uy[um].astype(float)))
        response_used_match={
            "used_rows":int(len(used)),
            "used_numeric_xy_rows":int(um.sum()),
            "observed_exact_xy_match_rows":int(sum(p in uset for p in obs_pairs)),
            "observed_exact_xy_match_fraction":float(sum(p in uset for p in obs_pairs)/len(obs_pairs)) if obs_pairs else None
        }

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "data_values_read_vertical":False,
        "observed_sha256":obs_sha,
        "rsf_sha256":rsf_sha,
        "observed_rows":int(len(obs)),
        "rsf_rows":int(len(rsf)),
        "observed_columns_nonvertical":list(obs.columns),
        "rsf_columns_nonvertical":list(rsf.columns),
        "observed_xy":[ox,oy],
        "rsf_xy":[rx,ry],
        "coordinate_linkage":{
            "observed_numeric_xy_rows":len(obs_pairs),
            "exact_match_rows":int(exact_matches),
            "exact_match_fraction":float(exact_matches/len(obs_pairs)) if obs_pairs else None,
            "rounded_3dp_match_rows":int(rounded_matches),
            "rounded_3dp_match_fraction":float(rounded_matches/len(obs_pairs)) if obs_pairs else None,
            "matched_rsf_rows_per_observed_coordinate_median":float(pd.Series(matched_counts).median()) if matched_counts else None,
            "matched_rsf_rows_per_observed_coordinate_max":max(matched_counts) if matched_counts else None
        },
        "candidate_context_columns":candidate_cols,
        "low_cardinality_fields":low_card,
        "common_nonvertical_columns":common_cols,
        "key_linkage_audit":key_audit,
        "response_rvso_counts":response_counts,
        "response_used_xy_linkage":response_used_match,
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Nyctalus RSF context/linkage audit v1","",
        "**No vertical-like column was retained or summarized.**","",
        f"- observed rows: **{len(obs)}**",
        f"- RSF rows: **{len(rsf)}**",
        f"- exact observed→RSF x-y matches: **{exact_matches}/{len(obs_pairs)} ({exact_matches/len(obs_pairs):.3f})**",
        f"- rounded 3-decimal matches: **{rounded_matches}/{len(obs_pairs)} ({rounded_matches/len(obs_pairs):.3f})**","",
        "## Candidate nonvertical context columns",""
    ]
    for col in candidate_cols:
        lines.append(f"- `{col}`")
    lines += ["","## All nonvertical RSF columns","",", ".join(f"`{x}`" for x in rsf.columns),""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "observed_rows":len(obs),
        "rsf_rows":len(rsf),
        "exact_match_fraction":payload["coordinate_linkage"]["exact_match_fraction"],
        "rounded_match_fraction":payload["coordinate_linkage"]["rounded_3dp_match_fraction"],
        "candidate_context_columns":candidate_cols,
        "rsf_columns":list(rsf.columns),
        "common_columns":common_cols,
        "key_linkage_audit":key_audit,
        "response_counts":response_counts,
        "response_used_xy_linkage":response_used_match,
        "low_cardinality_fields":low_card
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
