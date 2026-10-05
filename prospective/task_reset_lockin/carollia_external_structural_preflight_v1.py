#!/usr/bin/env python3
"""Metadata-only structural preflight for pinned Carollia MATLAB v7.3 trial files."""
from __future__ import annotations
import hashlib, json, re, tempfile, urllib.request
import h5py

OWNER="00keveland";REPO="Tunnel_2026";PIN="59928a71887d521fec143080b0b187736c046a0e"
API=f"https://api.github.com/repos/{OWNER}/{REPO}/contents/Trial_Data_Carolia?ref={PIN}"
UA="batter-carollia-external-structural/1.1"
PAT=re.compile(r"^C(?P<bat>\d+)_(?P<trial>\d+)_(?P<date>\d+)_traj_bat_pos_RESULTS\.mat$")

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

def get_bytes(url,maxn=5_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(maxn+1)
    if len(b)>maxn:
        raise RuntimeError("download budget exceeded")
    return b

def hdf_metadata_only(b):
    rows=[]
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(b);tmp.flush()
        with h5py.File(tmp.name,"r") as h:
            def visitor(name,obj):
                if name.startswith("#refs#"):
                    return
                rec={
                    "path":name,
                    "object_type":"group" if isinstance(obj,h5py.Group) else "dataset",
                    "attribute_names":sorted(str(k) for k in obj.attrs.keys()),
                }
                if isinstance(obj,h5py.Dataset):
                    rec["shape"]=list(obj.shape)
                    rec["dtype"]=str(obj.dtype)
                rows.append(rec)
            h.visititems(visitor)
    paths={r["path"] for r in rows}
    low={p.lower() for p in paths}
    # Standard v7.3 scalar-struct layout expected from public author code.
    has_results=any(p=="results" or p.startswith("results/") for p in low)
    has_tsec=any(p.endswith("/track/tsec") or p=="results/track/tsec" for p in low)
    has_pos=any(p.endswith("/track/pos_sm") or p=="results/track/pos_sm" for p in low)
    return rows,has_results,has_tsec,has_pos

def main():
    listing=get_json(API);rows=[]
    for f in listing:
        name=f.get("name") or "";m=PAT.match(name)
        if not m:
            continue
        raw=f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{PIN}/Trial_Data_Carolia/{name}"
        b=get_bytes(raw)
        meta,has_results,has_tsec,has_pos=hdf_metadata_only(b)
        passed=bool(has_results and has_tsec and has_pos)
        rows.append({
            "filename":name,
            "bat":int(m.group("bat")),
            "trial":int(m.group("trial")),
            "date":m.group("date"),
            "bytes":len(b),
            "sha256":hashlib.sha256(b).hexdigest(),
            "has_RESULTS":has_results,
            "has_track_tSec":has_tsec,
            "has_track_pos_sm":has_pos,
            "pass_structural_file":passed,
            "hdf_metadata":meta,
        })

    counts={}
    for r in rows:
        if r["pass_structural_file"]:
            counts.setdefault(r["date"],{}).setdefault(str(r["bat"]),0)
            counts[r["date"]][str(r["bat"])]+=1

    eligible={}
    for date,d in counts.items():
        eligible[date]=sorted([b for b,n in d.items() if n>=3],key=int)

    verdict=(
        "PASS_TO_FROZEN_EXTERNAL_OUTCOME"
        if all(len(eligible.get(d,[]))>=3 for d in ["20231216","20231222"])
        else "STOP_INSUFFICIENT_STRUCTURAL_SUPPORT"
    )
    print(json.dumps({
        "contract":"CAROLLIA_EXTERNAL_STRUCTURAL_PREFLIGHT_V1.md",
        "technical_amendment":"CAROLLIA_V73_METADATA_AMENDMENT_V1.md",
        "movement_values_loaded":False,
        "n_trial_files":len(rows),
        "files":rows,
        "counts_by_date_bat":counts,
        "eligible_bats_by_date":eligible,
        "verdict":verdict,
    },ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
