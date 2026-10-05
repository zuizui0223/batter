#!/usr/bin/env python3
"""Exact personal-bias retention test using only source-native bat-condition mean 3-D angle cells."""
from __future__ import annotations
import io,itertools,json,math,re,time,urllib.error,urllib.request,zipfile
import xml.etree.ElementTree as ET
import numpy as np

URL="https://www.dropbox.com/sh/met5cvcq9nmvxdd/AAAF4saT9FZl01FwWyRgD1pqa?dl=1"
UA="batter-reversible-sensory-bias/1.0"
MAX_BYTES=2_500_000
BATS=["Lucy","Alvin","Betty","Stevie","Dolores","Clementine"]
FILES={b:f"{b}.xlsx" for b in BATS}
P1_SHEETS={"baseline":"No masker_xyz","mask30":"board30_xyz","mask10":"board10_xyz"}
P2_BATS=["Lucy","Betty","Stevie","Dolores","Clementine"]
P2_BASE={
 "Lucy":"No masker foam_xyz","Betty":"No masker foam_xyz","Stevie":"No masker foam_xyz",
 "Dolores":"No masker foam_xyz","Clementine":"No masker foam"
}
P2_MASK={b:"foam30_xyz" for b in P2_BATS}
NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def op(req,timeout=90):
    last=None
    for a in range(5):
        try:return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (429,500,502,503,504):raise
        except urllib.error.URLError as e:last=e
        if a<4:time.sleep(2**a)
    raise last

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Accept":"application/zip,*/*"})
    with op(req) as r:b=r.read(MAX_BYTES+1)
    if len(b)>MAX_BYTES:raise RuntimeError("archive exceeds frozen byte budget")
    return b

def shared(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//m:t",NS)) for si in root.findall("m:si",NS)]

def paths(z):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rm={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out={}
    for sh in wb.findall("m:sheets/m:sheet",NS):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        p=rm[rid].lstrip("/")
        if not p.startswith("xl/"):p="xl/"+p
        out[sh.attrib["name"]]=p
    return out

def rc(ref):
    m=re.match(r"([A-Z]+)([0-9]+)",ref or "")
    if not m:return None,None
    s=m.group(1);n=0
    for ch in s:n=n*26+ord(ch)-64
    return int(m.group(2)),n

def colname(n):
    s=""
    while n:
        n,r=divmod(n-1,26);s=chr(65+r)+s
    return s

def sval(c,ss):
    typ=c.attrib.get("t")
    if typ=="inlineStr":
        t=c.find(".//m:t",NS);return (t.text or "") if t is not None else ""
    if typ=="s":
        v=c.find("m:v",NS)
        if v is None:return ""
        ix=int(v.text);return ss[ix] if 0<=ix<len(ss) else ""
    if typ=="str":
        v=c.find("m:v",NS);return (v.text or "") if v is not None else ""
    return None

def cellmap(root):
    return {c.attrib.get("r"):c for c in root.findall(".//m:c",NS) if c.attrib.get("r")}

def extract_mean(z,path,ss):
    root=ET.fromstring(z.read(path)); cm=cellmap(root)
    med=None
    for ref,c in cm.items():
        r,k=rc(ref)
        if r!=12:continue
        sv=sval(c,ss)
        if sv is not None and sv.strip().lower()=="median":
            med=(ref,k);break
    if med is None:raise RuntimeError("median label missing")
    _,mk=med
    fs=[]
    for ref,c in cm.items():
        r,k=rc(ref)
        if r==12 and k>mk and c.find("m:f",NS) is not None:
            fs.append((k,ref))
    fs=sorted(fs)
    if len(fs)<5:raise RuntimeError(f"too few per-flight formula cells: {len(fs)}")
    # Require contiguous formula cells.
    ks=[k for k,_ in fs]
    if ks!=list(range(ks[0],ks[-1]+1)):
        raise RuntimeError("noncontiguous row12 summary formula block")
    c1=colname(ks[0]);cn=colname(ks[-1])
    meanref=f"{c1}13"
    if meanref not in cm:raise RuntimeError("mean formula cell missing")
    f=cm[meanref].find("m:f",NS)
    if f is None:raise RuntimeError("mean formula missing")
    formula=(f.text or "").replace("$","").replace(" ","").upper()
    expected=f"AVERAGE({c1}12:{cn}12)".upper()
    if formula!=expected:
        raise RuntimeError(f"unexpected mean formula {meanref}: {formula} != {expected}")
    v=cm[meanref].find("m:v",NS)
    if v is None:raise RuntimeError("cached mean value missing")
    x=float(v.text)
    if not math.isfinite(x):raise RuntimeError("nonfinite cached mean")
    return {
      "mean_angle":x,
      "median_label_ref":med[0],
      "n_flight_summaries":len(fs),
      "summary_first":fs[0][1],"summary_last":fs[-1][1],
      "mean_formula_ref":meanref,"mean_formula":formula
    }

def ranks(a):
    a=np.asarray(a,float);order=np.argsort(a,kind="mergesort")
    r=np.empty(len(a),float);i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[order[j]]==a[order[i]]:j+=1
        rank=(i+j-1)/2+1
        r[order[i:j]]=rank;i=j
    return r

def corr(a,b,rank=False):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if rank:a,b=ranks(a),ranks(b)
    if len(a)<3 or np.std(a,ddof=1)<=0 or np.std(b,ddof=1)<=0:return None
    return float(np.corrcoef(a,b)[0,1])

def pair_order(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float);ok=[] 
    for i in range(len(a)):
        for j in range(i+1,len(a)):
            da=a[i]-a[j];db=b[i]-b[j]
            if da==0 or db==0:continue
            ok.append((da>0)==(db>0))
    return float(np.mean(ok)) if ok else None

def p1_metrics(vals,perm=None):
    base=np.array([vals[b]["baseline"] for b in BATS],float)
    y30=np.array([vals[b]["mask30"] for b in BATS],float)
    y10=np.array([vals[b]["mask10"] for b in BATS],float)
    theta=base-base.mean();r30=y30-y30.mean();r10=y10-y10.mean()
    if perm is not None:theta=theta[np.asarray(perm,int)]
    K=np.zeros((len(BATS),2),float)
    for i in range(len(BATS)):
        donors=[j for j in range(len(BATS)) if j!=i]
        for c,y in enumerate([r30,r10]):
            ds=abs(y[i]-theta[i]);do=np.mean([abs(y[i]-theta[j]) for j in donors])
            K[i,c]=do-ds
    ind=K.mean(axis=1)
    obs={
      "K_mask":float(ind.mean()),
      "K_mask30":float(K[:,0].mean()),
      "K_mask10":float(K[:,1].mean()),
      "individual_K":{b:float(ind[i]) for i,b in enumerate(BATS)},
      "positive_bats":int(np.sum(ind>0)),
      "positive_fraction":float(np.mean(ind>0)),
    }
    if perm is None:
        Y=np.concatenate([r30,r10]);H=np.concatenate([theta,theta])
        den=float(np.sum(Y*Y))
        obs.update({
          "R2_no_refit":float(1-np.sum((Y-H)**2)/den) if den>0 else None,
          "baseline_mask30_pearson":corr(theta,r30),
          "baseline_mask30_spearman":corr(theta,r30,True),
          "baseline_mask10_pearson":corr(theta,r10),
          "baseline_mask10_spearman":corr(theta,r10,True),
          "pair_order_mask30":pair_order(theta,r30),
          "pair_order_mask10":pair_order(theta,r10),
          "centered_baseline":{b:float(theta[i]) for i,b in enumerate(BATS)},
          "centered_mask30":{b:float(r30[i]) for i,b in enumerate(BATS)},
          "centered_mask10":{b:float(r10[i]) for i,b in enumerate(BATS)}
        })
    return obs

def p2_metrics(vals,perm=None):
    bats=P2_BATS
    base=np.array([vals[b]["foam_base"] for b in bats],float)
    targ=np.array([vals[b]["foam_mask30"] for b in bats],float)
    theta=base-base.mean();y=targ-targ.mean()
    if perm is not None:theta=theta[np.asarray(perm,int)]
    k=[]
    for i in range(len(bats)):
        donors=[j for j in range(len(bats)) if j!=i]
        k.append(float(np.mean([abs(y[i]-theta[j]) for j in donors])-abs(y[i]-theta[i])))
    k=np.asarray(k,float)
    out={"K":float(k.mean()),"individual_K":{b:float(k[i]) for i,b in enumerate(bats)},
         "positive_bats":int(np.sum(k>0)),"positive_fraction":float(np.mean(k>0))}
    if perm is None:
        den=float(np.sum(y*y))
        out.update({"R2_no_refit":float(1-np.sum((y-theta)**2)/den) if den>0 else None,
                    "pearson":corr(theta,y),"spearman":corr(theta,y,True),
                    "pair_order":pair_order(theta,y),
                    "centered_foam_no_masker":{b:float(theta[i]) for i,b in enumerate(bats)},
                    "centered_foam_mask30":{b:float(y[i]) for i,b in enumerate(bats)}})
    return out

def main():
    outer=zipfile.ZipFile(io.BytesIO(fetch()))
    vals={};audit={}
    for b in BATS:
        z=zipfile.ZipFile(io.BytesIO(outer.read(FILES[b])));ss=shared(z);pp=paths(z)
        vals[b]={};audit[b]={}
        for key,sheet in P1_SHEETS.items():
            q=extract_mean(z,pp[sheet],ss);vals[b][key]=q["mean_angle"];audit[b][key]=q
        if b in P2_BATS:
            q=extract_mean(z,pp[P2_BASE[b]],ss);vals[b]["foam_base"]=q["mean_angle"];audit[b]["foam_base"]=q
            q=extract_mean(z,pp[P2_MASK[b]],ss);vals[b]["foam_mask30"]=q["mean_angle"];audit[b]["foam_mask30"]=q

    obs1=p1_metrics(vals)
    null1=[]
    for p in itertools.permutations(range(6)):
        null1.append(p1_metrics(vals,p)["K_mask"])
    null1=np.asarray(null1,float)
    p1=float(np.mean(null1>=obs1["K_mask"]-1e-15))
    support1=bool(obs1["K_mask"]>0 and p1<=.05 and obs1["positive_bats"]>=5
                  and obs1["K_mask30"]>0 and obs1["K_mask10"]>0)

    obs2=p2_metrics(vals)
    null2=[]
    for p in itertools.permutations(range(5)):
        null2.append(p2_metrics(vals,p)["K"])
    null2=np.asarray(null2,float)
    p2=float(np.mean(null2>=obs2["K"]-1e-15))
    support2=bool(obs2["K"]>0 and p2<=.05 and obs2["positive_bats"]>=4)

    out={
      "contract":"PERSONAL_BIAS_RETENTION_CONTRACT_V1.md",
      "status":"FROZEN_PUBLIC_DATA_REANALYSIS",
      "source_scalar":"source-native bat-condition mean of per-flight 3-D angle-of-attack summaries",
      "audit":audit,
      "P1":{**obs1,"exact_permutations":720,"p_one_sided_exact":p1,
            "null_mean":float(null1.mean()),"null_min":float(null1.min()),"null_max":float(null1.max()),
            "verdict":"SUPPORTED_BASELINE_BIAS_RETENTION" if support1 else "UNSUPPORTED_BASELINE_BIAS_RETENTION"},
      "P2":{**obs2,"exact_permutations":120,"p_one_sided_exact":p2,
            "null_mean":float(null2.mean()),"null_min":float(null2.min()),"null_max":float(null2.max()),
            "verdict":"SUPPORTED_FOAM_REPERTURBATION_BIAS_RETENTION" if support2 else "UNSUPPORTED_FOAM_REPERTURBATION_BIAS_RETENTION"}
    }
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
