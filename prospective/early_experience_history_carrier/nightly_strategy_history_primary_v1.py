#!/usr/bin/env python3
"""Frozen primary: randomized early-experience effect on personal nightly-strategy history.

Contract: NIGHTLY_STRATEGY_HISTORY_ESTIMATOR_CONTRACT_V1.md
This is the first opening of Outdoor nightly behavioural outcome values for this programme.
"""
from __future__ import annotations
import collections, datetime as dt, hashlib, io, json, math, random, re, statistics, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"; DS="wh7c636y3t"; UA="batter-nightly-strategy-history-primary/1.0"
SEED=202610041733; NPERM=9999
FILES={
 "cross":("74189289-f4ba-4db4-8b33-24be7589dc8f","Exploraion in squares.xlsx",13056,
          "0e276042876b537df07807fbc6784dfe0ec93fdd034df9f4b095bb6b25a558d0",
          "Exploration",{"Name","Season","Origin","Enrichment"}),
 "out":("48df4e40-8f31-4bbd-a854-4078274e8fb1","Outdoor data.xlsx",52518,
        "03a89b2c7de5db56b9776c34a1827f6063da1074909c081e1dbb942f88c9bd0f",
        "exit_time_temp_new",{"Bat_ID","Environmental condition","Date","Time Out (Minute)","Max distance (meters)","Explored area"}),
}
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
"r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
OUTCOMES=("Time Out (Minute)","Max distance (meters)","Explored area")

def gj(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def gb(url,n):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read(n+1)
 if len(b)>n:raise RuntimeError("download budget")
 return b
def norm(v):
 if v is None:return None
 s=str(v).strip();return None if not s or s.lower() in {"na","nan","none","null","n/a"} else s
def col(ref):
 m=re.match(r"([A-Z]+)",ref or "");return m.group(1) if m else None
def shstr(z,need):
 out={};i=-1
 if not need:return out
 with z.open("xl/sharedStrings.xml") as fh:
  for _,e in ET.iterparse(fh,events=("end",)):
   if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
    i+=1
    if i in need:out[i]="".join(t.text or "" for t in e.findall(".//m:t",NS))
    e.clear()
 return out
def rows(b,sheet,allowed):
 z=zipfile.ZipFile(io.BytesIO(b));wb=ET.fromstring(z.read("xl/workbook.xml"));rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
 rm={x.attrib["Id"]:x.attrib["Target"] for x in rels};target=None
 for sh in wb.findall("m:sheets/m:sheet",NS):
  if sh.attrib.get("name")==sheet:
   target=rm[sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]].lstrip("/");break
 if not target:raise RuntimeError("sheet")
 if not target.startswith("xl/"):target="xl/"+target
 root=ET.fromstring(z.read(target));rr=root.findall("m:sheetData/m:row",NS)
 h={};need=set()
 for c in rr[0].findall("m:c",NS):
  cc=col(c.attrib.get("r"));t=c.attrib.get("t");v=c.find("m:v",NS)
  if t=="inlineStr":
   q=c.find(".//m:t",NS);h[cc]=q.text if q is not None else None
  elif v is not None:
   if t=="s":ix=int(v.text);need.add(ix);h[cc]=("S",ix)
   else:h[cc]=v.text
 ss=shstr(z,need);h={c:(ss[v[1]] if isinstance(v,tuple) else v) for c,v in h.items()}
 amap={c:v for c,v in h.items() if v in allowed}
 if set(amap.values())!=allowed:raise RuntimeError(f"header drift {sheet}: {sorted(amap.values())}")
 tmp=[];need=set()
 for r in rr[1:]:
  d={}
  for c in r.findall("m:c",NS):
   cc=col(c.attrib.get("r"))
   if cc not in amap:continue
   t=c.attrib.get("t");v=c.find("m:v",NS)
   if t=="inlineStr":
    q=c.find(".//m:t",NS);d[amap[cc]]=q.text if q is not None else None
   elif v is not None:
    if t=="s":ix=int(v.text);need.add(ix);d[amap[cc]]=("S",ix)
    else:d[amap[cc]]=v.text
  if d:tmp.append(d)
 ss=shstr(z,need)
 return [{k:(ss[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()} for d in tmp]
def fetch(s):
 fid,name,size,sha,sheet,allowed=s;m=gj(f"{BASE}/datasets/{DS}/files/{fid}");cd=m.get("content_details") or {};b=gb(cd["download_url"],size+4096)
 if len(b)!=size or hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError(f"integrity {name}")
 return rows(b,sheet,allowed)
def pdate(v):
 s=norm(v)
 if s is None:return None
 try:
  x=float(s)
  if 20000<x<70000:return (dt.datetime(1899,12,30)+dt.timedelta(days=x)).date()
 except:pass
 for f in ("%Y-%m-%d","%d/%m/%Y","%m/%d/%Y","%Y/%m/%d"):
  try:return dt.datetime.strptime(s[:10],f).date()
  except:pass
 return None
def arm(v):
 s=(norm(v) or "").lower()
 if "enrich" in s or s=="1":return "Enriched"
 if "impover" in s or s=="0":return "Impoverished"
 return None
def fnum(v):
 s=norm(v)
 if s is None:return None
 try:
  x=float(s)
  return x if math.isfinite(x) else None
 except:return None
def meanvec(vs):
 return tuple(sum(v[k] for v in vs)/len(vs) for k in range(3))
def dist(a,b):
 return math.sqrt(sum((a[k]-b[k])**2 for k in range(3)))
def mean(xs):
 return sum(xs)/len(xs) if xs else None

def main():
 cross=fetch(FILES["cross"]);out=fetch(FILES["out"])
 design={}
 for r in cross:
  n=norm(r.get("Name"))
  if not n:continue
  if n in design:raise RuntimeError(f"duplicate crosswalk {n}")
  design[n]={"season":norm(r.get("Season")),"origin":norm(r.get("Origin")),"condition":arm(r.get("Enrichment"))}
 raw=collections.defaultdict(list)
 for r in out:
  bat=norm(r.get("Bat_ID"));d=pdate(r.get("Date"))
  if bat is None or d is None:continue
  if bat not in design:raise RuntimeError(f"unlinked outdoor bat {bat}")
  cond=arm(r.get("Environmental condition"))
  if cond!=design[bat]["condition"]:raise RuntimeError(f"condition mismatch {bat}")
  vals=tuple(fnum(r.get(k)) for k in OUTCOMES)
  raw[bat].append({"date":d,"vals":vals})
 for bat in raw:
  raw[bat].sort(key=lambda x:x["date"])
  if len({x["date"] for x in raw[bat]})!=len(raw[bat]):raise RuntimeError(f"duplicate dates {bat}")

 # Structural candidates are fixed by >=10 unique Outdoor dates.
 candidates=sorted([b for b,rr in raw.items() if len(rr)>=10])
 structural_counts=collections.Counter(design[b]["condition"] for b in candidates)
 if structural_counts["Enriched"]<5 or structural_counts["Impoverished"]<5:
  print(json.dumps({"verdict":"STOP_STRUCTURAL_SUPPORT","counts":dict(structural_counts)},indent=2));return

 # Validate and transform first 10 rows only. Invalid/missing values remain None.
 transformed=collections.defaultdict(list)
 bad_by_bat=collections.Counter()
 pooled=[[],[],[]]
 for bat in candidates:
  for r in raw[bat][:10]:
   vals=r["vals"]
   if any(x is None or x<0 for x in vals):
    transformed[bat].append(None);bad_by_bat[bat]+=1;continue
   u=tuple(math.log1p(x) for x in vals)
   transformed[bat].append(u)
   for k in range(3):pooled[k].append(u[k])
 scales=[]
 for k in range(3):
  if len(pooled[k])<2:raise RuntimeError("insufficient pooled scale")
  mu=statistics.mean(pooled[k]);sd=statistics.stdev(pooled[k])
  if not math.isfinite(sd) or sd<=0:raise RuntimeError("invalid global scale")
  scales.append((mu,sd))
 z={}
 for bat,rows_ in transformed.items():
  z[bat]=[None if v is None else tuple((v[k]-scales[k][0])/scales[k][1] for k in range(3)) for v in rows_]

 blocks=collections.defaultdict(list)
 for b in candidates:blocks[(design[b]["season"],design[b]["origin"])].append(b)
 for key in blocks:blocks[key]=sorted(blocks[key])

 observed_labels={b:design[b]["condition"] for b in candidates}

 def calc_H(labels):
  H={};r_by_t=collections.defaultdict(list);targets_by_bat={}
  for b in candidates:
   rs=[]
   for ti in range(2,10): # target ordinals 3..10
    target=z[b][ti]
    if target is None:continue
    own=[v for v in z[b][:ti] if v is not None][-5:]
    if len(own)<2:continue
    selfd=dist(target,meanvec(own))
    donor_d=[]
    for j in candidates:
     if j==b or design[j]["season"]!=design[b]["season"] or labels[j]!=labels[b]:continue
     hist=[v for v in z[j][:ti] if v is not None][-5:]
     if len(hist)<2:continue
     donor_d.append(dist(target,meanvec(hist)))
    if len(donor_d)<2:continue
    R=mean(donor_d)-selfd
    rs.append(R);r_by_t[ti+1].append(R)
   if len(rs)>=5:
    H[b]=mean(rs);targets_by_bat[b]=len(rs)
  e=[v for b,v in H.items() if labels[b]=="Enriched"]
  im=[v for b,v in H.items() if labels[b]=="Impoverished"]
  T=mean(e)-mean(im) if len(e)>=5 and len(im)>=5 else None
  return H,T,r_by_t,targets_by_bat

 Hobs,Tobs,Robs,ntobs=calc_H(observed_labels)
 eobs=[Hobs[b] for b in Hobs if observed_labels[b]=="Enriched"]
 iobs=[Hobs[b] for b in Hobs if observed_labels[b]=="Impoverished"]
 if Tobs is None:
  print(json.dumps({"contract":"NIGHTLY_STRATEGY_HISTORY_ESTIMATOR_CONTRACT_V1.md",
   "nightly_outcomes_opened":True,"verdict":"STOP_OUTCOME_SUPPORT",
   "H_counts":{"Enriched":len(eobs),"Impoverished":len(iobs)},
   "bad_first10_rows_by_bat":dict(bad_by_bat)},indent=2));return

 rng=random.Random(SEED)
 permT=[];invalid=0
 block_ne={}
 for key,members in blocks.items():
  block_ne[key]=sum(observed_labels[b]=="Enriched" for b in members)
 for _ in range(NPERM):
  lab={}
  for key,members in blocks.items():
   ne=block_ne[key]
   echosen=set(rng.sample(members,ne))
   for b in members:lab[b]="Enriched" if b in echosen else "Impoverished"
  _,tp,_,_=calc_H(lab)
  if tp is None:invalid+=1
  else:permT.append(tp)

 if len(permT)<9500:
  verdict="STOP_RANDOMIZATION_SUPPORT";p=None
 else:
  p=(1+sum(abs(x)>=abs(Tobs) for x in permT))/(1+len(permT))
  verdict="PASS_TREATMENT_EFFECT" if p<=0.05 else "FAIL_TREATMENT_EFFECT"

 def stats(xs):
  return {"n":len(xs),"mean":mean(xs),"median":statistics.median(xs) if xs else None,
          "n_positive":sum(x>0 for x in xs),"prop_positive":sum(x>0 for x in xs)/len(xs) if xs else None}
 outj={
  "contract":"NIGHTLY_STRATEGY_HISTORY_ESTIMATOR_CONTRACT_V1.md",
  "nightly_outcomes_opened":True,
  "source_file_sha256":FILES["out"][3],
  "structural_candidates":len(candidates),
  "structural_condition_counts":dict(structural_counts),
  "first10_incomplete_outcome_rows_by_bat":dict(bad_by_bat),
  "global_log1p_scales":[{"outcome":OUTCOMES[k],"mean":scales[k][0],"sd":scales[k][1]} for k in range(3)],
  "H_by_bat":[{"Bat_ID":b,"condition":observed_labels[b],"season":design[b]["season"],"origin":design[b]["origin"],
               "H":Hobs.get(b),"n_valid_targets":ntobs.get(b,0)} for b in candidates],
  "H_summary":{"Enriched":stats(eobs),"Impoverished":stats(iobs)},
  "R_by_target_ordinal":{str(t):{"n":len(v),"mean":mean(v),"median":statistics.median(v) if v else None} for t,v in sorted(Robs.items())},
  "T_observed_E_minus_I":Tobs,
  "permutation":{"seed":SEED,"requested":NPERM,"valid":len(permT),"invalid":invalid,
                 "null_mean":mean(permT) if permT else None,
                 "null_q025":sorted(permT)[int(.025*(len(permT)-1))] if permT else None,
                 "null_q975":sorted(permT)[int(.975*(len(permT)-1))] if permT else None,
                 "p_two_sided":p},
  "verdict":verdict
 }
 print(json.dumps(outj,ensure_ascii=False,indent=2))

if __name__=="__main__":
 main()
