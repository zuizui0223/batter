#!/usr/bin/env python3
"""Prospective Yamada personal speed-state persistence primary."""
from __future__ import annotations
import collections, hashlib, io, json, math, urllib.request, zipfile
import xml.etree.ElementTree as ET
import numpy as np

FID=33969680
SIZE=18023
MD5="cb7e2f738d85ee80becb5949317ff625"
URL=f"https://ndownloader.figshare.com/files/{FID}"
UA="batter-yamada-speed-state-primary/1.0"
NPERM=9999
SEED=202610052111
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
SHEET="1st_table"

def download():
 req=urllib.request.Request(URL,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read(SIZE+1)
 if len(b)!=SIZE or hashlib.md5(b).hexdigest()!=MD5:raise RuntimeError("integrity failure")
 return b

def col(ref):
 s=""
 for ch in ref or "":
  if ch.isalpha():s+=ch
  else:break
 return s

def shared(z,needed):
 if not needed:return {}
 out={};i=-1
 with z.open("xl/sharedStrings.xml") as fh:
  for _,e in ET.iterparse(fh,events=("end",)):
   if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
    i+=1
    if i in needed:out[i]="".join(t.text or "" for t in e.findall(".//m:t",NS))
    e.clear()
 return out

def read_rows():
 z=zipfile.ZipFile(io.BytesIO(download()))
 wb=ET.fromstring(z.read("xl/workbook.xml"));rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
 rm={x.attrib["Id"]:x.attrib["Target"] for x in rel};target=None
 for sh in wb.findall("m:sheets/m:sheet",NS):
  if sh.attrib.get("name")==SHEET:
   rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
   target=rm[rid].lstrip("/");break
 if not target:raise RuntimeError("sheet missing")
 if not target.startswith("xl/"):target="xl/"+target
 root=ET.fromstring(z.read(target));tmp=[];need=set()
 for row in root.findall("m:sheetData/m:row",NS)[1:]:
  d={}
  for c in row.findall("m:c",NS):
   cc=col(c.attrib.get("r"))
   if cc not in {"C","D","E","K"}:continue
   typ=c.attrib.get("t");v=c.find("m:v",NS)
   if v is None:continue
   key={"C":"condition","D":"bat","E":"trial","K":"speed"}[cc]
   if typ=="s":
    ix=int(v.text);need.add(ix);d[key]=("S",ix)
   else:d[key]=v.text
  if d:tmp.append(d)
 ss=shared(z,need);rows=[]
 for d in tmp:
  q={k:(ss[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()}
  try:
   rows.append({"condition":str(int(float(q["condition"]))),"bat":str(int(float(q["bat"]))),
                "trial":str(int(float(q["trial"]))),"speed":float(q["speed"])})
  except Exception as e:raise RuntimeError(f"bad row {q}: {e}")
 return rows

def standardize(rows):
 out={}
 rawmeans={}; changes={}
 for cond in ["1","2"]:
  rr=[r for r in rows if r["condition"]==cond]
  res={}
  df=0;ss=0.0
  for trial in ["1","12"]:
   tr=[r for r in rr if r["trial"]==trial]
   vals=np.asarray([r["speed"] for r in tr],float)
   mu=float(vals.mean());rawmeans[(cond,trial)]=mu
   for r in tr:res[(trial,r["bat"])]=r["speed"]-mu
   ss+=float(np.sum((vals-mu)**2));df+=len(vals)-1
  scale=math.sqrt(ss/df)
  if not(math.isfinite(scale) and scale>0):raise RuntimeError(f"bad pooled scale condition {cond}")
  for (trial,bat),v in res.items():out[(cond,trial,bat)]=v/scale
  bats=sorted(set(r["bat"] for r in rr),key=int)
  changes[cond]={b:next(r["speed"] for r in rr if r["bat"]==b and r["trial"]=="12")-
                    next(r["speed"] for r in rr if r["bat"]==b and r["trial"]=="1") for b in bats}
 return out,rawmeans,changes

def stat(z,early_assignment):
 indiv={};condstats={}
 for cond in ["1","2"]:
  bats=sorted([b for (c,t,b) in z if c==cond and t=="12"],key=int)
  vals={}
  for b in bats:
   late=z[(cond,"12",b)]
   selfv=early_assignment[(cond,b)]
   ds=abs(late-selfv)
   others=[abs(late-early_assignment[(cond,j)]) for j in bats if j!=b]
   k=float(np.mean(others)-ds)
   vals[b]=k
  indiv.update({f"{cond}:{b}":v for b,v in vals.items()})
  condstats[cond]=float(np.mean(list(vals.values())))
 return float(np.mean(list(condstats.values()))),indiv,condstats

def corr_beta_acc(z,early_assignment):
 xs=[];ys=[];pairacc=[];condcorr={};condacc={}
 for cond in ["1","2"]:
  bats=sorted([b for (c,t,b) in z if c==cond and t=="12"],key=int)
  x=np.asarray([early_assignment[(cond,b)] for b in bats],float)
  y=np.asarray([z[(cond,"12",b)] for b in bats],float)
  condcorr[cond]=float(np.corrcoef(x,y)[0,1])
  a=[]
  for i in range(len(bats)):
   for j in range(i+1,len(bats)):
    dx=x[i]-x[j];dy=y[i]-y[j]
    a.append(.5 if dx==0 or dy==0 else (1.0 if np.sign(dx)==np.sign(dy) else 0.0))
  condacc[cond]=float(np.mean(a));pairacc.extend(a);xs.extend(x.tolist());ys.extend(y.tolist())
 X=np.asarray(xs,float);Y=np.asarray(ys,float)
 r=float(np.corrcoef(X,Y)[0,1])
 beta=float(np.sum(X*Y)/np.sum(X*X))
 return r,beta,float(np.mean(pairacc)),condcorr,condacc

def main():
 rows=read_rows()
 if len(rows)!=28:raise RuntimeError(f"expected 28 rows got {len(rows)}")
 # strict structural recheck
 bats=sorted(set(r["bat"] for r in rows),key=int)
 if len(bats)!=14:raise RuntimeError("bat count drift")
 for b in bats:
  rr=[r for r in rows if r["bat"]==b]
  if len(rr)!=2 or sorted(r["trial"] for r in rr)!=["1","12"]:raise RuntimeError(f"trial support {b}")
 z,rawmeans,changes=standardize(rows)
 observed={(cond,b):z[(cond,"1",b)] for cond in ["1","2"] for b in sorted([x for (c,t,x) in z if c==cond and t=="1"],key=int)}
 K,indiv,condstats=stat(z,observed)
 r,beta,acc,condcorr,condacc=corr_beta_acc(z,observed)

 rng=np.random.default_rng(SEED)
 nk=np.empty(NPERM);nr=np.empty(NPERM);nb=np.empty(NPERM);na=np.empty(NPERM)
 bats_by_cond={c:sorted([b for (cc,t,b) in z if cc==c and t=="1"],key=int) for c in ["1","2"]}
 earlyvals={c:np.asarray([z[(c,"1",b)] for b in bats_by_cond[c]],float) for c in ["1","2"]}
 for q in range(NPERM):
  mp={}
  for c in ["1","2"]:
   vals=rng.permutation(earlyvals[c])
   for b,v in zip(bats_by_cond[c],vals):mp[(c,b)]=float(v)
  nk[q],_,_=stat(z,mp)
  nr[q],nb[q],na[q],_,_=corr_beta_acc(z,mp)
 pK=float((1+np.sum(nk>=K))/(NPERM+1));pr=float((1+np.sum(nr>=r))/(NPERM+1))
 pb=float((1+np.sum(nb>=beta))/(NPERM+1));pa=float((1+np.sum(na>=acc))/(NPERM+1))
 positive={c:sum(indiv[f"{c}:{b}"]>0 for b in bats_by_cond[c]) for c in ["1","2"]}
 ntotal=sum(positive.values())
 supported=bool(K>0 and pK<=.05 and ntotal>=10 and positive["1"]>=5 and positive["2"]>=5)
 out={
  "contract":"PERSONAL_SPEED_STATE_CONTRACT_V1.md","status":"PRIMARY_OPENED",
  "n_bats":14,"condition_sizes":{"1":7,"2":7},
  "published_shift_reproduction":{
    "condition1_trial1_mean":rawmeans[("1","1")],"condition1_trial12_mean":rawmeans[("1","12")],
    "condition2_trial1_mean":rawmeans[("2","1")],"condition2_trial12_mean":rawmeans[("2","12")],
    "condition1_mean_within_bat_change":float(np.mean(list(changes["1"].values()))),
    "condition2_mean_within_bat_change":float(np.mean(list(changes["2"].values())))
  },
  "primary":{
    "K":K,"condition_K":condstats,"individual_K":indiv,
    "positive_bats_by_condition":positive,"positive_bats_total":ntotal,
    "permutations":NPERM,"seed":SEED,"null_mean":float(nk.mean()),
    "null_q025":float(np.quantile(nk,.025)),"null_q975":float(np.quantile(nk,.975)),
    "p_one_sided":pK,"verdict":"SUPPORTED_PERSONAL_SPEED_STATE_PERSISTENCE" if supported else "UNSUPPORTED_PERSONAL_SPEED_STATE_PERSISTENCE"
  },
  "secondary":{
    "pooled_pearson_r":r,"condition_pearson_r":condcorr,"p_r_one_sided":pr,
    "through_origin_beta":beta,"p_beta_one_sided":pb,
    "equal_pair_order_accuracy":acc,"condition_pair_accuracy":condacc,"p_pair_accuracy_one_sided":pa,
    "null_r_mean":float(nr.mean()),"null_beta_mean":float(nb.mean()),"null_accuracy_mean":float(na.mean())
  }
 }
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
