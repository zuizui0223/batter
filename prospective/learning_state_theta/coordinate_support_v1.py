#!/usr/bin/env python3
"""Yamada coordinate/feature support gate; no identity outcome is computed.\nScientific rules frozen in COORDINATE_SUPPORT_OPENING_V1.md.\n"""
from __future__ import annotations
import hashlib, io, json, math, urllib.request, zipfile
import xml.etree.ElementTree as ET
import numpy as np

FID=33969677
SIZE=932367
MD5="2226ea5b19fb077ddcce66cb6e97088c"
URL=f"https://ndownloader.figshare.com/files/{FID}"
UA="batter-yamada-coordinate-support/1.0"
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

MAP=[
("1","1","1","bat_A_chain_1st(20151022)"),("1","1","12","bat_A_chain_12th"),
("2","1","1","bat_B_chain_1st(20160202)"),("2","1","12","bat_B_chain_12th"),
("3","1","1","bat_C_chain_1st(20160204)"),("3","1","12","bat_C_chain_12th"),
("4","1","1","bat_D_chain_1st(20160414)"),("4","1","12","bat_D_chain_12th"),
("5","1","1","bat_E_chain_1st"),("5","1","12","bat_E_chain_12th"),
("6","1","1","bat_F_chain_1st"),("6","1","12","bat_F_chain_12th"),
("7","1","1","bat_G_chain_1st"),("7","1","12","bat_G_chain_12th"),
("8","2","1","bat_F_ac_1st(20160712_2533)"),("8","2","12","bat_F_ac_12th"),
("9","2","1","bat_I_ac_1st(20161220)"),("9","2","12","bat_I_ac_12th"),
("10","2","1","bat_J_ac_1st(20160802)"),("10","2","12","bat_J_ac_12th"),
("11","2","1","bat_K_ac_1st(20170623)"),("11","2","12","y_bat_K_ac_12th"),
("12","2","1","bat_L_ac_1st(20160712)"),("12","2","12","bat_L_ac_12th"),
("13","2","1","bat_M_acril_1st"),("13","2","12","bat_M_acril_12th"),
("14","2","1","bat_N_acril_1st"),("14","2","12","bat_N_acril_12th"),
]
FEATURES=["median_speed","p90_speed","median_abs_vertical_speed","p90_abs_vertical_speed",
          "median_abs_horizontal_turn_rate","p90_abs_horizontal_turn_rate","path_efficiency","vertical_range"]

def download():
 req=urllib.request.Request(URL,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
 with urllib.request.urlopen(req,timeout=90) as r:b=r.read(SIZE+1)
 if len(b)!=SIZE or hashlib.md5(b).hexdigest()!=MD5:raise RuntimeError("raw workbook integrity fail")
 return b

def sheet_targets(z):
 wb=ET.fromstring(z.read("xl/workbook.xml")); rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
 rm={x.attrib["Id"]:x.attrib["Target"] for x in rel}
 out={}
 for sh in wb.findall("m:sheets/m:sheet",NS):
  rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
  p=rm[rid].lstrip("/")
  if not p.startswith("xl/"):p="xl/"+p
  out[sh.attrib["name"]]=p
 return out

def cell_col(ref):
 s=""
 for ch in ref or "":
  if ch.isalpha():s+=ch
  else:break
 return s

def read_abcd(z,path):
 root=ET.fromstring(z.read(path)); vals=[]
 for row in root.findall("m:sheetData/m:row",NS)[1:]:
  d={}
  for c in row.findall("m:c",NS):
   cc=cell_col(c.attrib.get("r"))
   if cc not in {"A","B","C","D"}:continue
   v=c.find("m:v",NS)
   if v is None:continue
   try:d[cc]=float(v.text)
   except Exception:pass
  if all(k in d for k in ("A","B","C","D")):vals.append([d["A"],d["B"]/1000.0,d["C"]/1000.0,d["D"]/1000.0])
 return np.asarray(vals,float) if vals else np.empty((0,4),float)

def feat(arr):
 arr=arr[np.all(np.isfinite(arr),axis=1)]
 if len(arr)==0:return None,{}
 arr=arr[np.argsort(arr[:,0],kind="mergesort")]
 _,ix=np.unique(arr[:,0],return_index=True);arr=arr[np.sort(ix)]
 if len(arr)<2:return None,{"rows":len(arr)}
 t=arr[:,0];xyz=arr[:,1:];dt=np.diff(t);dxyz=np.diff(xyz,axis=0)
 pos=dt>0;steps=np.linalg.norm(dxyz,axis=1);path=float(np.sum(steps[np.isfinite(steps)]))
 duration=float(t[-1]-t[0])
 turn=[]
 h=np.hypot(dxyz[:,0],dxyz[:,1]);heading=np.full(len(dt),np.nan)
 hg=pos&(h>0)&np.isfinite(h);heading[hg]=np.arctan2(dxyz[hg,1],dxyz[hg,0])
 for k in range(len(heading)-1):
  if not(np.isfinite(heading[k]) and np.isfinite(heading[k+1])):continue
  dtt=.5*(dt[k]+dt[k+1])
  if not(np.isfinite(dtt) and dtt>0):continue
  dh=math.atan2(math.sin(heading[k+1]-heading[k]),math.cos(heading[k+1]-heading[k]))
  turn.append(abs(dh)/dtt)
 turn=np.asarray(turn,float)
 support={"rows":int(len(arr)),"positive_intervals":int(np.sum(pos)),"turn_values":int(len(turn)),
          "positive_duration":bool(duration>0),"positive_path":bool(path>0)}
 if not(len(arr)>=100 and np.sum(pos)>=50 and len(turn)>=20 and duration>0 and path>0):
  return None,support
 sp=np.linalg.norm(dxyz[pos],axis=1)/dt[pos];vz=np.abs(dxyz[pos,2]/dt[pos])
 eff=float(np.linalg.norm(xyz[-1]-xyz[0])/path);vr=float(np.max(xyz[:,2])-np.min(xyz[:,2]))
 f=np.array([np.median(sp),np.percentile(sp,90),np.median(vz),np.percentile(vz,90),
             np.median(turn),np.percentile(turn,90),eff,vr],float)
 support["all_features_finite"]=bool(np.all(np.isfinite(f)))
 return (f if np.all(np.isfinite(f)) else None),support

def main():
 b=download();z=zipfile.ZipFile(io.BytesIO(b));targets=sheet_targets(z)
 rows=[]
 for bat,cond,trial,sheet in MAP:
  if sheet not in targets:raise RuntimeError(f"missing mapped sheet {sheet}")
  f,sup=feat(read_abcd(z,targets[sheet]))
  rows.append({"bat_id":bat,"condition":cond,"trial":trial,"sheet":sheet,"feature":f,"support":sup})
 eligible=[]
 for bat in sorted(set(r["bat_id"] for r in rows),key=int):
  rr=[r for r in rows if r["bat_id"]==bat]
  if len(rr)==2 and all(r["feature"] is not None for r in rr):eligible.append(bat)
 # pooled within-state feature scales, support only
 retained=[];dropped=[]
 for k,name in enumerate(FEATURES):
  ok=True
  for cond in ["1","2"]:
   cr=[r for r in rows if r["condition"]==cond and r["bat_id"] in eligible]
   residual=[]
   df=0
   for trial in ["1","12"]:
    tr=[r["feature"][k] for r in cr if r["trial"]==trial]
    if len(tr)<2:ok=False;continue
    mu=float(np.mean(tr));residual.extend([x-mu for x in tr]);df+=len(tr)-1
   if not ok or df<=0:continue
   scale=math.sqrt(float(np.sum(np.square(residual)))/df)
   if not(math.isfinite(scale) and scale>0):ok=False
  (retained if ok else dropped).append(name)
 counts={c:sum(b in eligible for b in sorted(set(r["bat_id"] for r in rows if r["condition"]==c))) for c in ["1","2"]}
 verdict="PASS_OPEN_PERSONAL_POLICY_PRIMARY" if counts["1"]>=5 and counts["2"]>=5 and len(eligible)>=12 and len(retained)>=6 else "STOP_COORDINATE_OR_FEATURE_SUPPORT"
 out={"contract":"COORDINATE_SUPPORT_OPENING_V1.md","identity_outcome_calculated":False,
      "sheet_support":[{"bat_id":r["bat_id"],"condition":r["condition"],"trial":r["trial"],"sheet":r["sheet"],**r["support"]} for r in rows],
      "eligible_bats":eligible,"eligible_counts_by_condition":counts,"n_eligible_bats":len(eligible),
      "retained_features":retained,"dropped_features":dropped,"verdict":verdict}
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
