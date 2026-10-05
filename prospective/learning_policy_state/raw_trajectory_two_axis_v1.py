#!/usr/bin/env python3
"""Prospective raw-trajectory external replication of transparent Rhino policy axes.

Uses only time/X/Y/Z from the 28 linked Yamada first/12th trajectory sheets.
Feature extraction reuses the exact Teshima task-reset implementation.
"""
from __future__ import annotations

import collections
import hashlib
import importlib.util
import io
import json
import math
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent

FEATURES = [
    "median_speed",
    "p90_speed",
    "median_abs_vertical_speed",
    "p90_abs_vertical_speed",
    "median_abs_horizontal_turn_rate",
    "p90_abs_horizontal_turn_rate",
    "path_efficiency",
    "vertical_range",
]

def trajectory_features(a):
    """Exact eight-feature implementation frozen in RAW_TRAJECTORY_TWO_AXIS_CONTRACT_V1.md."""
    if a.shape[0] < 100:
        return None
    t=a[:,0]
    xyz=a[:,1:4]
    dt=np.diff(t)
    dxyz=np.diff(xyz,axis=0)
    good=np.isfinite(dt) & (dt>0) & np.all(np.isfinite(dxyz),axis=1)
    if int(np.sum(good)) < 50:
        return None
    dtg=dt[good]
    dg=dxyz[good]
    v3=np.linalg.norm(dg,axis=1)/dtg
    vz=np.abs(dg[:,2])/dtg

    horiz=np.linalg.norm(dg[:,:2],axis=1)
    head_good=horiz>0
    headings=np.arctan2(dg[head_good,1],dg[head_good,0])
    turn_rates=[]
    if len(headings)>=2:
        base_dt=dtg[head_good]
        dtheta=np.arctan2(np.sin(np.diff(headings)),np.cos(np.diff(headings)))
        dtturn=(base_dt[1:]+base_dt[:-1])/2.0
        valid=np.isfinite(dtheta)&np.isfinite(dtturn)&(dtturn>0)
        turn_rates=np.abs(dtheta[valid])/dtturn[valid]
    turn_rates=np.asarray(turn_rates,dtype=np.float64)
    if len(turn_rates)<20:
        return None

    steps=np.linalg.norm(np.diff(xyz,axis=0),axis=1)
    total=float(np.sum(steps[np.isfinite(steps)]))
    if not math.isfinite(total) or total<=0:
        return None
    net=float(np.linalg.norm(xyz[-1]-xyz[0]))
    eff=net/total
    vrange=float(np.max(xyz[:,2])-np.min(xyz[:,2]))

    feats=np.asarray([
        np.median(v3),np.percentile(v3,90),
        np.median(vz),np.percentile(vz,90),
        np.median(turn_rates),np.percentile(turn_rates,90),
        eff,vrange,
    ],dtype=np.float64)
    return feats if np.all(np.isfinite(feats)) else None

# Frozen outcome-blind linkage implementation.
specL=importlib.util.spec_from_file_location(
    "L",HERE/"raw_trajectory_linkage_v1.py"
)
L=importlib.util.module_from_spec(specL);specL.loader.exec_module(L)

API="https://api.figshare.com/v2/articles/19102712"
UA="batter-yamada-raw-two-axis/1.0"
NPERM=9999
SEEDS={"IM":202610050951,"I":202610050952,"M":202610050953,"FULL8":202610050954}

NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def build_links(bsmall,bbig):
    subjects=L.read_structural_summary(bsmall)
    parsed=[x for x in (L.parse_sheet(n) for n in L.read_sheet_names_only(bbig)) if x is not None]
    links=[]
    used=collections.Counter()
    for sh in parsed:
        candidates=[s for s in subjects.values() if s["condition"]==sh["condition"]]
        ds=[s for s in candidates if s["dataset_norm"]==sh["sheet_norm"]]
        if len(ds)==1:
            match=ds[0];method="dataset_name"
        elif len(ds)==0:
            os=[s for s in candidates if s["origin_norm"]==sh["sheet_norm"]]
            if len(os)!=1:
                raise RuntimeError(f"linkage origin ambiguity {sh['sheet']}: {[x['bats_id'] for x in os]}")
            match=os[0];method="origin_name_fallback"
        else:
            raise RuntimeError(f"linkage dataset ambiguity {sh['sheet']}")
        used[(match["bats_id"],sh["trial"])]+=1
        links.append({**sh,"bats_id":match["bats_id"],"link_method":method})
    expected={(bid,t) for bid in subjects for t in (1,12)}
    if len(links)!=28 or set(used)!=expected or any(n!=1 for n in used.values()):
        raise RuntimeError("frozen linkage no longer closes 28/28")
    return links,subjects

def worksheet_paths(z):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out={}
    for sh in wb.findall("m:sheets/m:sheet",NS):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target=relmap[rid].lstrip("/")
        if not target.startswith("xl/"):target="xl/"+target
        out[sh.attrib.get("name")]=target
    return out

def col_letter(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def read_time_xyz(z,path):
    root=ET.fromstring(z.read(path))
    vals=[]
    # Row 1 is header, already audited.
    for row in root.findall("m:sheetData/m:row",NS):
        rn=int(row.attrib.get("r","0"))
        if rn<2:continue
        d={}
        for c in row.findall("m:c",NS):
            col=col_letter(c.attrib.get("r"))
            if col not in {"A","B","C","D"}:continue
            v=c.find("m:v",NS)
            if v is None:continue
            try:x=float(v.text)
            except Exception:continue
            if math.isfinite(x):d[col]=x
        if all(k in d for k in ("A","B","C","D")):
            # Time remains seconds; XYZ mm -> metres.
            vals.append([d["A"],d["B"]/1000.0,d["C"]/1000.0,d["D"]/1000.0])
    if not vals:return np.empty((0,4),float)
    a=np.asarray(vals,dtype=np.float64)
    order=np.argsort(a[:,0],kind="mergesort")
    a=a[order]
    _,idx=np.unique(a[:,0],return_index=True)
    a=a[np.sort(idx)]
    return a

def fetch_files():
    art=L.get_json(API)
    files={int(f["id"]):f for f in art.get("files") or []}
    bsmall=L.fetch(L.SMALL,files)
    bbig=L.fetch(L.BIG,files)
    return bsmall,bbig

def extract_features():
    bsmall,bbig=fetch_files()
    links,subjects=build_links(bsmall,bbig)
    z=zipfile.ZipFile(io.BytesIO(bbig))
    paths=worksheet_paths(z)
    rows=[]
    support=[]
    for lk in sorted(links,key=lambda x:(int(x["bats_id"]),x["trial"])):
        path=paths.get(lk["sheet"])
        if path is None:raise RuntimeError(f"sheet path missing {lk['sheet']}")
        a=read_time_xyz(z,path)
        feat=trajectory_features(a)
        valid=feat is not None and np.all(np.isfinite(feat))
        support.append({
          "bats_id":lk["bats_id"],"condition":lk["condition"],"trial":lk["trial"],
          "sheet":lk["sheet"],"n_finite_unique_time_rows":int(a.shape[0]),
          "feature_valid":bool(valid)
        })
        if valid:
            rows.append({
              "bat":lk["bats_id"],"condition":lk["condition"],"trial":lk["trial"],
              "sheet":lk["sheet"],"feature":np.asarray(feat,dtype=np.float64)
            })
    # Subject complete cases.
    by=collections.defaultdict(dict);cond={}
    for r in rows:
        by[r["bat"]][r["trial"]]=r
        cond[r["bat"]]=r["condition"]
    bats=sorted(
        [b for b,d in by.items() if set(d)=={1,12}],
        key=int
    )
    cc=collections.Counter(cond[b] for b in bats)
    if len(bats)<12 or cc[1]<5 or cc[2]<5:
        raise RuntimeError(f"STOP raw trajectory support bats={len(bats)} cond={dict(cc)}")
    rows=[r for r in rows if r["bat"] in set(bats)]
    return rows,bats,cond,support

def standardize_relative(rows,bats,cond):
    by={(r["bat"],r["trial"]):r["feature"] for r in rows}
    z={}
    cell_stats={}
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        for t in (1,12):
            M=np.vstack([by[(b,t)] for b in cb])
            mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
            if np.any(~np.isfinite(sd)) or np.any(sd<=0):
                raise RuntimeError(f"zero/nonfinite feature SD condition={c} trial={t}")
            cell_stats[(c,t)]={"mean":mu,"sd":sd}
            for b in cb:z[(b,t)]=(by[(b,t)]-mu)/sd
    return z,by,cell_stats

def axes(zvec):
    I=float(np.mean(zvec[:4]))
    M=float(np.mean(np.array([-zvec[0],zvec[4],zvec[5],zvec[6],zvec[7]],float)))
    return I,M

def vectors_from_z(z,bats,mode):
    out={}
    for b in bats:
        for t in (1,12):
            v=z[(b,t)]
            I,M=axes(v)
            if mode=="IM":q=np.array([I,M],float)
            elif mode=="I":q=np.array([I],float)
            elif mode=="M":q=np.array([M],float)
            elif mode=="FULL8":q=np.asarray(v,float)
            else:raise ValueError(mode)
            out[(b,t)]=q
    return out

def identity_stat(vec,bats,cond,label12=None):
    per={}
    cms=[]
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        vals=[]
        for b in cb:
            assigned=label12[b] if label12 is not None else b
            dself=float(np.linalg.norm(vec[(b,1)]-vec[(assigned,12)]))
            others=[j for j in cb if j!=assigned]
            dother=float(np.mean([np.linalg.norm(vec[(b,1)]-vec[(j,12)]) for j in others]))
            k=dother-dself
            per[b]=k;vals.append(k)
        cms.append(float(np.mean(vals)))
    return float(np.mean(cms)),per

def perm_map(bats,cond,rng):
    mp={}
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        p=list(rng.permutation(np.asarray(cb,dtype=object)))
        for b,j in zip(cb,p):mp[b]=str(j)
    return mp

def calibrate(mode,z,bats,cond,seed):
    vec=vectors_from_z(z,bats,mode)
    obs,ki=identity_stat(vec,bats,cond,None)
    rng=np.random.default_rng(seed)
    null=np.empty(NPERM,float)
    for q in range(NPERM):
        mp=perm_map(bats,cond,rng)
        null[q]=identity_stat(vec,bats,cond,mp)[0]
    p=float((1+np.sum(null>=obs))/(NPERM+1))
    pos=sum(v>0 for v in ki.values())
    need=math.ceil(.70*len(bats))
    return {
      "K":obs,"K_i":ki,"positive_subjects":pos,"n_subjects":len(bats),
      "required_positive_subjects":need,"positive_fraction":pos/len(bats),
      "permutations":NPERM,"seed":seed,
      "null_mean":float(null.mean()),"null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),"p_one_sided":p,
      "supported":bool(obs>0 and p<=.05 and pos>=need)
    }

def learning_displacement(by,bats,cond):
    out={}
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        M1=np.vstack([by[(b,1)] for b in cb])
        mu=M1.mean(axis=0);sd=M1.std(axis=0,ddof=1)
        if np.any(sd<=0):raise RuntimeError(f"bad baseline SD condition={c}")
        vals={}
        for t in (1,12):
            Z=np.vstack([(by[(b,t)]-mu)/sd for b in cb])
            A=np.asarray([axes(z) for z in Z],float)
            vals[t]=A.mean(axis=0)
        out[str(c)]={
          "trial1_mean_IM":vals[1].tolist(),
          "trial12_mean_IM":vals[12].tolist(),
          "learning_displacement_IM":(vals[12]-vals[1]).tolist(),
        }
    return out

def main():
    rows,bats,cond,support=extract_features()
    z,by,stats=standardize_relative(rows,bats,cond)

    R1=calibrate("IM",z,bats,cond,SEEDS["IM"])
    R2I=calibrate("I",z,bats,cond,SEEDS["I"])
    R2M=calibrate("M",z,bats,cond,SEEDS["M"])
    R3=calibrate("FULL8",z,bats,cond,SEEDS["FULL8"])

    out={
      "contract":"RAW_TRAJECTORY_TWO_AXIS_CONTRACT_V1.md",
      "status":"PROSPECTIVE_EXTERNAL_POLICY_AXIS_REPLICATION",
      "species":"Rhinolophus ferrumequinum nippon",
      "n_evaluable_subjects":len(bats),
      "subjects_by_condition":{str(c):sum(cond[b]==c for b in bats) for c in (1,2)},
      "feature_names":list(FEATURES),
      "trajectory_support":support,
      "R1_transparent_IM":{
        **R1,
        "verdict":"PASS_EXTERNAL_TWO_AXIS_MAINTENANCE" if R1["supported"] else "FAIL_EXTERNAL_TWO_AXIS_MAINTENANCE"
      },
      "R2_axis_specific":{
        "FlightIntensity":R2I,
        "ManeuveringExtent":R2M,
      },
      "R3_full8":R3,
      "descriptive_baseline_scaled_learning_vector":learning_displacement(by,bats,cond)
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
