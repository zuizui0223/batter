#!/usr/bin/env python3
"""Independent fixed two-axis validation in public call-sampled 3-D sequences.

Implements INDEPENDENT_CALL_SAMPLED_TWO_AXIS_VALIDATION_CONTRACT_V1.md.
"""
from __future__ import annotations
import collections, hashlib, io, json, math, re, urllib.request, zipfile
import xml.etree.ElementTree as ET
import numpy as np

BASE="https://data.mendeley.com/public-api"
DS="hbb2t3dnbc"
UA="batter-independent-call-sampled-two-axis-validation/1.0"

FILES=[
(1,"Bat 1.xlsx","49856030-9ce0-4082-94ea-7725f89aa3b1",1108243,"eb358e554b6c25d4837c99b5b1d957dd9c0ed7daaa8a116e71f77f83713b1943","pregnant"),
(2,"Bat 2.xlsx","3648b8b4-f29b-44b7-a844-f51d4414c2a6",945590,"02edd8b5d64c1ac75bc3dbdd6cf81ac0da80a0ee41b4da90aa3ef556d0752c75","pregnant"),
(3,"Bat 3.xlsx","4fe0e3aa-397e-416f-b211-574a0af4f7d6",1232373,"4f09052e1d9c10a5f1ac51f4f3afc17c48b6aecc4677c6ea7130396ffbcce254","pregnant"),
(5,"Bat 5.xlsx","4f646af4-8430-4ee9-b207-d14259496da6",1593787,"daa53f235b1d3056ee87b9449a13e48246c5e67202561d2c84816e780544bf16","pregnant"),
(6,"Bat 6.xlsx","1952636e-f052-4e13-a4bc-c5c4c71f1845",484690,"be3abb145cc9dd9c9c1881fcadc056462b2817f9e6bb1860cbbb935c0e5f08a1","post_lactating"),
(7,"Bat 7.xlsx","5a05372d-0cff-4535-96ee-c63f57eacb24",615557,"964613f3b64a5d8593ed4c49ee783f2c6c2deb2544b27bf78c11c85c687eacd1","post_lactating"),
(8,"Bat 8.xlsx","88799a4b-eb6e-492f-8ef9-dd7e3f558d2c",636717,"7b62277666bae703c08d280c192a652f51753475fa32c5aba5561cd38083af13","post_lactating"),
(9,"Bat 9.xlsx","08cb4de9-b114-4f65-8f3a-27aa95c6fc98",1440600,"c8959a134b2282579a538176e855b0b85e119c643a9549e1b2c9be7e97c124a4","post_lactating"),
(10,"Bat 10.xlsx","9726518e-8433-441e-86c8-5009102afbcf",1846191,"8d18da29b1e5bdc3ba35b2e11683fef1d9591a38373a9147d4c4314770dac003","post_lactating"),
]

NPERM=9999
SEED=202610051121
MIN_VALID=9500
REQ_HEADERS={"A":"Call no.","B":"Time","C":"x","D":"y","E":"z"}

NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def gj(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

def gb(url,n):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=90) as r:b=r.read(n+1)
    if len(b)>n:raise RuntimeError("download budget exceeded")
    return b

def col_letters(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def shared_strings(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//m:t",NS)) for si in root.findall("m:si",NS)]

def cell_value(c,ss):
    typ=c.attrib.get("t")
    if typ=="inlineStr":
        t=c.find(".//m:t",NS);return t.text if t is not None else None
    v=c.find("m:v",NS)
    if v is None:return None
    if typ=="s":return ss[int(v.text)]
    if typ=="b":return "1" if v.text=="1" else "0"
    return v.text

def sheet_paths(z):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rm={x.attrib["Id"]:x.attrib["Target"] for x in rels}
    out=[]
    for sh in wb.findall("m:sheets/m:sheet",NS):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        p=rm[rid].lstrip("/")
        if not p.startswith("xl/"):p="xl/"+p
        out.append((sh.attrib.get("name"),p))
    return out

def parse_candidate_sheet(z,ss,name,path):
    root=ET.fromstring(z.read(path))
    rows=root.findall("m:sheetData/m:row",NS)
    if not rows:return None
    hdr={}
    for c in rows[0].findall("m:c",NS):
        cc=col_letters(c.attrib.get("r"))
        if cc in REQ_HEADERS:hdr[cc]=cell_value(c,ss)
    if any(hdr.get(c)!=v for c,v in REQ_HEADERS.items()):
        return None
    vals=[]
    for row in rows[1:]:
        d={}
        for c in row.findall("m:c",NS):
            cc=col_letters(c.attrib.get("r"))
            if cc not in {"B","C","D","E"}:continue
            v=cell_value(c,ss)
            if v is not None:d[cc]=v
        if len(d)<4:continue
        try:
            q=[float(d[k]) for k in ("B","C","D","E")]
        except Exception:
            continue
        if all(math.isfinite(x) for x in q):vals.append(q)
    if not vals:return {"sheet":name,"features":None,"n_finite":0,"reason":"NO_FINITE_ROWS"}
    a=np.asarray(vals,float)
    order=np.argsort(a[:,0],kind="mergesort");a=a[order]
    _,idx=np.unique(a[:,0],return_index=True);a=a[np.sort(idx)]
    if len(a)<20:return {"sheet":name,"features":None,"n_finite":int(len(a)),"reason":"LT20_POINTS"}
    t=a[:,0];xyz=a[:,1:4]
    dt=np.diff(t);dxyz=np.diff(xyz,axis=0)
    good=(dt>0)&np.all(np.isfinite(dxyz),axis=1)
    if int(np.sum(good))<19:return {"sheet":name,"features":None,"n_finite":int(len(a)),"reason":"LT19_SPEED_INTERVALS"}
    dtg=dt[good];dg=dxyz[good]
    speed=np.linalg.norm(dg,axis=1)/dtg
    vz=np.abs(dg[:,2])/dtg
    h=np.hypot(dg[:,0],dg[:,1]);hg=h>0
    headings=np.arctan2(dg[hg,1],dg[hg,0]);hdt=dtg[hg]
    turns=[]
    for k in range(len(headings)-1):
        dtt=.5*(hdt[k]+hdt[k+1])
        if not (math.isfinite(dtt) and dtt>0):continue
        dtheta=math.atan2(math.sin(headings[k+1]-headings[k]),math.cos(headings[k+1]-headings[k]))
        turns.append(abs(dtheta)/dtt)
    turns=np.asarray(turns,float)
    if len(turns)<10:return {"sheet":name,"features":None,"n_finite":int(len(a)),"reason":"LT10_TURNS"}
    steps=np.linalg.norm(np.diff(xyz,axis=0),axis=1)
    path=float(np.sum(steps[np.isfinite(steps)]))
    duration=float(t[-1]-t[0])
    if not (duration>0 and path>0 and math.isfinite(path)):
        return {"sheet":name,"features":None,"n_finite":int(len(a)),"reason":"NONPOSITIVE_DURATION_OR_PATH"}
    eff=float(np.linalg.norm(xyz[-1]-xyz[0])/path)
    vr=float(np.max(xyz[:,2])-np.min(xyz[:,2]))
    feat=np.asarray([
        np.median(speed),np.percentile(speed,90),
        np.median(vz),np.percentile(vz,90),
        np.median(turns),np.percentile(turns,90),
        eff,vr
    ],float)
    if not np.all(np.isfinite(feat)):
        return {"sheet":name,"features":None,"n_finite":int(len(a)),"reason":"NONFINITE_FEATURE"}
    return {"sheet":name,"features":feat,"n_finite":int(len(a)),"reason":None}

def load_sequences():
    seq=[]
    audit=[]
    for bat,name,fid,size,sha,group in FILES:
        meta=gj(f"{BASE}/datasets/{DS}/files/{fid}");cd=meta.get("content_details") or {}
        if meta.get("filename")!=name:raise RuntimeError(f"filename drift {name}")
        b=gb(cd["download_url"],size+4096)
        got=hashlib.sha256(b).hexdigest()
        if len(b)!=size or got!=sha:raise RuntimeError(f"integrity {name}")
        z=zipfile.ZipFile(io.BytesIO(b));ss=shared_strings(z)
        res=[]
        for sname,path in sheet_paths(z):
            q=parse_candidate_sheet(z,ss,sname,path)
            if q is not None:res.append(q)
        valid=[q for q in res if q["features"] is not None]
        audit.append({"bat":bat,"group":group,"workbook":name,
                      "n_candidate_schema_sheets":len(res),"n_valid_sequences":len(valid),
                      "invalid_reasons":dict(collections.Counter(q["reason"] for q in res if q["reason"] is not None))})
        for q in valid:
            seq.append({"bat":str(bat),"group":group,"sheet":q["sheet"],
                        "features":q["features"],"n_finite":q["n_finite"]})
    return seq,audit

def standardize(seq):
    rows=[]
    block_stats={}
    for group in ("pregnant","post_lactating"):
        rr=[r for r in seq if r["group"]==group]
        if not rr:raise RuntimeError(f"no rows {group}")
        M=np.vstack([r["features"] for r in rr])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad external group SD {group}")
        block_stats[group]={"n_sequences":len(rr),"means":mu.tolist(),"sds":sd.tolist()}
        for r in rr:
            z=(r["features"]-mu)/sd
            q=dict(r);q["I"]=float(np.mean(z[:4]))
            q["M"]=float(np.mean(np.asarray([-z[0],z[4],z[5],z[6],z[7]],float)))
            rows.append(q)
    return rows,block_stats

def support(rows):
    counts=collections.Counter((r["group"],r["bat"]) for r in rows)
    eligible={(g,b) for (g,b),n in counts.items() if n>=5}
    preg=sorted(b for g,b in eligible if g=="pregnant")
    post=sorted(b for g,b in eligible if g=="post_lactating")
    return counts,eligible,preg,post

def vector(r,mode):
    if mode=="2D":return np.asarray([r["I"],r["M"]],float)
    if mode=="I":return np.asarray([r["I"]],float)
    if mode=="M":return np.asarray([r["M"]],float)
    raise ValueError(mode)

def identity_stat(rows,assigned_labels,mode):
    # assigned_labels is list parallel to rows, preserving group.
    groups=("pregnant","post_lactating")
    indiv_target=collections.defaultdict(list)
    for i,r in enumerate(rows):
        lab=assigned_labels[i]
        g=r["group"]
        # own other sequences
        self_idx=[j for j,x in enumerate(rows) if j!=i and x["group"]==g and assigned_labels[j]==lab]
        if not self_idx:continue
        own=np.mean(np.vstack([vector(rows[j],mode) for j in self_idx]),axis=0)
        donor_labels=sorted(set(assigned_labels[j] for j,x in enumerate(rows) if x["group"]==g and assigned_labels[j]!=lab))
        donor_cent=[]
        for dl in donor_labels:
            js=[j for j,x in enumerate(rows) if x["group"]==g and assigned_labels[j]==dl]
            if js:donor_cent.append(np.mean(np.vstack([vector(rows[j],mode) for j in js]),axis=0))
        if not donor_cent:continue
        x=vector(r,mode)
        ds=float(np.linalg.norm(x-own))
        do=float(np.mean([np.linalg.norm(x-d) for d in donor_cent]))
        indiv_target[(g,lab)].append(do-ds)

    indiv={f"{g}:{b}":float(np.mean(v)) for (g,b),v in indiv_target.items() if v}
    block={}
    for g in groups:
        vals=[float(np.mean(v)) for (gg,b),v in indiv_target.items() if gg==g and v]
        if vals:block[g]=float(np.mean(vals))
    if len(block)!=2:return None
    overall=float(np.mean([block["pregnant"],block["post_lactating"]]))
    return overall,indiv,block

def observed_labels(rows):
    return [r["bat"] for r in rows]

def permuted_labels(rows,rng):
    labs=observed_labels(rows)
    out=list(labs)
    for g in ("pregnant","post_lactating"):
        idx=[i for i,r in enumerate(rows) if r["group"]==g]
        vals=np.asarray([labs[i] for i in idx],dtype=object)
        rng.shuffle(vals)
        for k,i in enumerate(idx):out[i]=str(vals[k])
    return out

def main():
    seq,audit=load_sequences()
    rows,block_stats=standardize(seq)
    counts,eligible,preg,post=support(rows)
    structural_pass=(len(preg)==4 and len(post)>=4)
    if not structural_pass:
        print(json.dumps({
          "contract":"INDEPENDENT_CALL_SAMPLED_TWO_AXIS_VALIDATION_CONTRACT_V1.md",
          "status":"STOP_NUMERIC_SUPPORT","audit":audit,
          "eligible_pregnant":preg,"eligible_post_lactating":post
        },ensure_ascii=False,indent=2));return

    # Restrict to individuals passing frozen >=5 sequence support.
    rows=[r for r in rows if (r["group"],r["bat"]) in eligible]
    labs=observed_labels(rows)
    E1=identity_stat(rows,labs,"2D")
    EI=identity_stat(rows,labs,"I")
    EM=identity_stat(rows,labs,"M")
    if E1 is None:raise RuntimeError("observed external identity support failed")
    K,indiv,blocks=E1

    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        pl=permuted_labels(rows,rng)
        q=identity_stat(rows,pl,"2D")
        if q is not None:null.append(q[0])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=K))/(1+len(a))) if len(a) else math.nan
    pos=sum(v>0 for v in indiv.values());frac=pos/len(indiv) if indiv else math.nan
    supported=(K>0 and p<=.05 and frac>=.70 and
               blocks.get("pregnant",0)>0 and blocks.get("post_lactating",0)>0 and len(a)>=MIN_VALID)

    out={
      "contract":"INDEPENDENT_CALL_SAMPLED_TWO_AXIS_VALIDATION_CONTRACT_V1.md",
      "status":"PROSPECTIVE_EXTERNAL_VALIDATION",
      "source_species":"Pipistrellus kuhlii",
      "audit":audit,
      "block_standardization":block_stats,
      "eligible_pregnant":preg,
      "eligible_post_lactating":post,
      "n_external_individuals":len(indiv),
      "n_external_sequences":len(rows),
      "E1_fixed_2D":{
        "K":float(K),"individual_means":indiv,"block_means":blocks,
        "positive_individuals":pos,"positive_fraction":frac,
        "requested_permutations":NPERM,"valid_permutations":int(len(a)),
        "seed":SEED,"null_mean":float(np.mean(a)),
        "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
        "p_one_sided":p
      },
      "E2_components":{
        "I_K":None if EI is None else float(EI[0]),
        "I_individual_means":None if EI is None else EI[1],
        "M_K":None if EM is None else float(EM[0]),
        "M_individual_means":None if EM is None else EM[1],
      },
      "verdict":"SUPPORTED_EXTERNAL_FIXED_TWO_AXIS_IDENTITY" if supported else "UNSUPPORTED_EXTERNAL_FIXED_TWO_AXIS_IDENTITY"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
