#!/usr/bin/env python3
"""Dedicated 19-bat Outdoor crosswalk; identity/design fields only."""
from __future__ import annotations
import collections, datetime as dt, hashlib, io, json, re, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"; DS="wh7c636y3t"; UA="batter-outdoor-crosswalk-v2/1.0"
FILES={
 "cross":("74189289-f4ba-4db4-8b33-24be7589dc8f","Exploraion in squares.xlsx",13056,
          "0e276042876b537df07807fbc6784dfe0ec93fdd034df9f4b095bb6b25a558d0",
          "Exploration",{"Bat no.","Name","Season","Sex","Origin","Colony","Enrichment"}),
 "out":("48df4e40-8f31-4bbd-a854-4078274e8fb1","Outdoor data.xlsx",52518,
        "03a89b2c7de5db56b9776c34a1827f6063da1074909c081e1dbb942f88c9bd0f",
        "exit_time_temp_new",{"Bat_ID","Sex","Environmental condition","Origin","Date","NumberDaysOut"}),
}
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
"r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def gj(url):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def gb(url,n):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
 with urllib.request.urlopen(req,timeout=60) as r:b=r.read(n+1)
 if len(b)>n:raise RuntimeError("budget");return b
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
 if set(amap.values())!=allowed:raise RuntimeError(f"header drift {sheet}")
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
 if len(b)!=size or hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError("integrity")
 return rows(b,sheet,allowed)
def pdate(v):
 s=norm(v)
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
def main():
 cr=fetch(FILES["cross"]);out=fetch(FILES["out"])
 cm={}
 dup=[]
 for r in cr:
  n=norm(r.get("Name"))
  if not n:continue
  if n in cm:dup.append(n)
  cm[n]=r
 om=collections.defaultdict(list)
 for r in out:
  n=norm(r.get("Bat_ID"))
  if n:om[n].append(r)
 report=[];errors=[];ys=collections.defaultdict(set);eligible=collections.Counter();blocks=collections.Counter()
 for bat,rr in sorted(om.items()):
  c=cm.get(bat)
  if c is None:
   errors.append({"bat":bat,"type":"missing_crosswalk"});continue
  oc=sorted(set(norm(x.get("Environmental condition")) for x in rr if norm(x.get("Environmental condition"))))
  oo=sorted(set(norm(x.get("Origin")) for x in rr if norm(x.get("Origin"))))
  os=sorted(set(norm(x.get("Sex")) for x in rr if norm(x.get("Sex"))))
  ds=sorted(set(pdate(x.get("Date")) for x in rr if pdate(x.get("Date"))));years=sorted(set(d.year for d in ds))
  cc=arm(c.get("Enrichment")); co=norm(c.get("Origin")); cs=norm(c.get("Season")); csex=norm(c.get("Sex"))
  if len(oc)!=1 or arm(oc[0])!=cc:errors.append({"bat":bat,"type":"treatment_mismatch","outdoor":oc,"crosswalk":norm(c.get("Enrichment"))})
  if len(oo)==1 and co and oo[0]!=co:errors.append({"bat":bat,"type":"origin_mismatch","outdoor":oo,"crosswalk":co})
  if len(os)==1 and csex and os[0]!=csex:errors.append({"bat":bat,"type":"sex_mismatch","outdoor":os,"crosswalk":csex})
  if not co or not cs or not cc or len(years)!=1:errors.append({"bat":bat,"type":"unresolved_design_field"})
  else:
   ys[years[0]].add(cs);blocks[(cs,co,cc)]+=1
   if len(ds)>=10:eligible[cc]+=1
  report.append({"Bat_ID":bat,"Bat_no":norm(c.get("Bat no.")),"condition":cc,"season":cs,"origin":co,"colony":norm(c.get("Colony")),"year":years[0] if len(years)==1 else None,"n_unique_dates":len(ds),"outdoor_origin":oo})
 extra=sorted(set(cm)-set(om));missing=sorted(set(om)-set(cm))
 ymap={str(k):sorted(v) for k,v in sorted(ys.items())}
 bij=len(ymap)==2 and all(len(v)==1 for v in ymap.values()) and len(set(v[0] for v in ymap.values()))==2
 verdict="PASS_FREEZE_NIGHTLY_STRATEGY_ESTIMATOR" if not dup and not errors and not extra and not missing and bij and eligible["Enriched"]>=5 and eligible["Impoverished"]>=5 else "STOP_CROSSWALK"
 print(json.dumps({"contract":"OUTDOOR_CROSSWALK_AMENDMENT_V2.md","behavioural_outcomes_opened":False,
 "crosswalk_rows":len(cr),"outdoor_bats":len(om),"duplicate_names":dup,"extra_crosswalk_names":extra,"missing_crosswalk_names":missing,
 "errors":errors,"year_to_season":ymap,"year_season_bijection":bij,"eligible_ge10":dict(eligible),
 "block_counts":[{"season":k[0],"origin":k[1],"condition":k[2],"n_bats":v} for k,v in sorted(blocks.items())],
 "crosswalk":report,"verdict":verdict},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
