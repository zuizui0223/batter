"""V17: publisher-checksum provenance, time/ID linkage, weather-source discovery.
Noncommercial scholarly use. Do not print coordinates, heart rate or identifiers.
"""
import concurrent.futures as cf
import csv, hashlib, io, json, pathlib, re, urllib.parse, urllib.request
from html.parser import HTMLParser
from collections import Counter
import numpy as np
import pandas as pd

BASE="https://datarepository.movebank.org/server/api/core/bitstreams/"
SPECS={
"gps":("622a8566-62a0-4d51-9228-625c08f6c533",564649,"7ffe83e9956b53da076bc5a9b8ba73ba"),
"hr":("75bfe6e0-f4d5-41ab-8b83-c75980991fdc",18367167,"1f8610b3c22b234a970cd6b112800f8e"),
"ref":("13743730-f2fe-4ed9-8303-2c3618d19cfa",20743,"f8ca2a1169e8c781b6b7c7cd75ab0687"),
"readme":("647c2c63-9550-44cc-a47e-45dff075e6c6",24019,"57256253efa7de1b473a41091690ba4c"),
"old2016":("35cd7452-fe48-4423-81fb-4ff8e0717da8",7299,"17bf1ab59daeb37b5ee1f8f1c127d0b4"),
"old2021_22":("baae11b3-e466-4f51-b7ee-3119fc51810a",15626,"008c0513007d291884d128b7c7af9629"),
"old2023":("31403d15-5784-4b01-80bd-9ef9c0a7f4cd",8384,"9880d2b155237d61ce6e6391296df1da")}
STATION="https://striresearch.si.edu/physical-monitoring/bocas-del-toro/"
OUT=pathlib.Path("results/bayer_field_join_v17.json")
def fetch(url,limit):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-noncommercial-research-source-audit/1.0","Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=45) as r:
        b=r.read(limit+1)
        if len(b)>limit:raise ValueError("size limit")
        return b,r.geturl()
def original(k):
    uuid,size,md5=SPECS[k]
    b,url=fetch(BASE+uuid+"/content",size)
    assert len(b)==size and hashlib.md5(b).hexdigest()==md5
    return b,{"size":len(b),"md5":md5,"sha256":hashlib.sha256(b).hexdigest()}
def table(b):
    return pd.read_csv(io.BytesIO(b),dtype=str,keep_default_na=False,encoding="utf-8-sig")
def ts(a):
    return pd.to_datetime(a,format="mixed",utc=True,errors="coerce")
def canon(s):
    return s.astype(str).str.strip().str.casefold()
def counts(a):
    return {str(k):int(v) for k,v in a.value_counts(dropna=False).items()}
def frame_audit(d):
    time=ts(d["timestamp"]); ids=canon(d["individual-local-identifier"])
    t=d.assign(_t=time,_id=ids).dropna(subset=["_t"]).sort_values(["_id","_t"])
    delta=t.groupby("_id")["_t"].diff().dt.total_seconds()
    return {"rows":len(d),"ids":int(ids[ids!=""].nunique()),"tags":int(d["tag-local-identifier"].nunique()),
            "missing_time":int(time.isna().sum()),"missing_id":int((ids=="").sum()),
            "duplicate_id_time_rows":int(t.duplicated(["_id","_t"],keep=False).sum()),
            "timestamp_min":str(time.min()),"timestamp_max":str(time.max()),"visible":counts(d["visible"]),
            "positive_interval_quantiles_seconds":[float(x) for x in delta[delta>0].quantile([.05,.5,.95])],
            "per_id_count_quantiles":[float(x) for x in ids.value_counts().quantile([0,.5,1])]}
def readme_context(raw):
    s=raw.decode("utf-8-sig",errors="replace")
    # Read documentation on field semantics only; redact identifiers/coordinates.
    lines=s.splitlines(); out=[]
    for l in lines:
        if re.search(r"quality index|quality score|tag.tech.spec|time.?zone|UTC|EST|local time|heart.rate.*(unit|bpm)|body mass.*(unit|gram|kg)|wind (speed|direction)|measurement.*quality",l,re.I):
            if re.search(r"latitude|longitude|location.*[0-9]{2}\.[0-9]|(?:Phyl|PIT)\s*\d+",l,re.I):continue
            out.append(l[:500])
    return {"matched_documentation_lines":out[:60],"readme_line_count":len(lines)}
def time_link(g,h,ref):
    gps=g.assign(t=ts(g.timestamp),id=canon(g["individual-local-identifier"])).dropna(subset=["t"])
    hr=h.assign(t=ts(h.timestamp),id=canon(h["individual-local-identifier"])).dropna(subset=["t"])
    # Duplicates cannot be unique linkage; exclude all duplicate keys, preserve counts.
    gps=gps.loc[(gps.id!="")&~gps.duplicated(["id","t"],keep=False)]
    hr=hr.loc[(hr.id!="")&~hr.duplicated(["id","t"],keep=False)]
    if "visible" in gps and not set(gps.visible.str.lower().unique())-{"true","false",""}:
        gps=gps.loc[gps.visible.str.lower().eq("true")]
    # Timings only, no response values.
    n={"gps_unique_visible":len(gps),"hr_unique":len(hr),"gps_bats_with_hr":0,
       "nearest30":0,"nearest15":0,"candidate_gps_steps45_90":0,"steps_with_hr_within30_of_midpoint":0,
       "bats_with_matched_steps":0,"bat_nights_with_matched_steps":0}
    stepn=[]
    for aid,x in gps.groupby("id"):
        z=hr.loc[hr.id==aid]
        if not len(z):continue
        n["gps_bats_with_hr"]+=1
        t=np.sort(x.t.astype("int64").to_numpy()/1e9)
        u=np.sort(z.t.astype("int64").to_numpy()/1e9)
        # pandas may use microsecond timestamps; convert via .as_unit('ns') when required
        def nearest(a):
            j=np.searchsorted(u,a)
            return np.minimum(abs(a-u[np.clip(j-1,0,len(u)-1)]),abs(a-u[np.clip(j,0,len(u)-1)]))
        q=nearest(t)
        n["nearest30"]+=int((q<=30).sum());n["nearest15"]+=int((q<=15).sum())
        step=np.diff(t); mids=(t[1:]+t[:-1])/2
        ok=(step>=45)&(step<=90)
        matched=ok&(nearest(mids)<=30)
        n["candidate_gps_steps45_90"]+=int(ok.sum());n["steps_with_hr_within30_of_midpoint"]+=int(matched.sum())
        if matched.any():
            n["bats_with_matched_steps"]+=1
            nights=(pd.to_datetime(mids[matched],unit="s",utc=True)-pd.Timedelta(hours=17)).date
            n["bat_nights_with_matched_steps"]+=len(set(nights));stepn.append(int(matched.sum()))
    n["steps_per_matched_bat_quantiles"]=np.quantile(stepn,[0,.5,1]).tolist() if stepn else []
    n["night_definition"]="UTC-5, shifted by 12 hours for calendar evening grouping; assumes archived UTC timestamps, verify README before using for inference"
    return n
class Rows(HTMLParser):
    def __init__(self):super().__init__();self.row=False;self.rows=[];self.parts=[];self.links=[];self.all=[]
    def handle_starttag(self,tag,attrs):
        if tag=="tr":self.row=True;self.parts=[];self.links=[]
        if tag=="a":
            link=dict(attrs).get("href")
            if link:self.all.append(link)
            if self.row and link:self.links.append(link)
    def handle_data(self,data):
        if self.row:self.parts.append(data)
    def handle_endtag(self,tag):
        if tag=="tr" and self.row:self.rows.append((" ".join(" ".join(self.parts).split()),self.links));self.row=False
def station():
    try:
        raw,url=fetch(STATION,4_000_000)
        p=Rows();p.feed(raw.decode(errors="replace"))
        rows=[{"label":t[:300],"links":[urllib.parse.urljoin(url,x) for x in links]} for t,links in p.rows if re.search(r"wind (speed|direction)",t,re.I)]
        return {"url":url,"sha256":hashlib.sha256(raw).hexdigest(),"wind_rows":rows,"metadata_candidates":[urllib.parse.urljoin(url,x) for x in p.all if re.search(r"metadata|bocas.*meta|tower.*pdf",x,re.I)][:20],"status":"LINK_AUDIT" if rows else "NO_MATCHING_ROWS"}
    except Exception as e:return {"status":"STOP","error":repr(e)}
def main():
    report={"scope":"structural audit only; no flight or heart-rate responses fit","sources":{}}
    raws={}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        fut={ex.submit(original,k):k for k in SPECS}
        for f in cf.as_completed(fut):
            k=fut[f]
            try:raws[k],report["sources"][k]=f.result()
            except Exception as e:report["sources"][k]={"status":"STOP","error":repr(e)}
    if not {"gps","hr","ref","readme"}<=raws.keys():
        report["status"]="STOP_ORIGINAL_BYTES"
    else:
        g,h,r=[table(raws[k]) for k in ("gps","hr","ref")]
        # Force nanosecond timestamp resolution across pandas versions.
        global ts
        ts=lambda a:pd.to_datetime(a,format="mixed",utc=True,errors="coerce").dt.as_unit("ns")
        report["gps"]=frame_audit(g);report["hr"]=frame_audit(h)
        report["readme"]=readme_context(raws["readme"])
        report["hr_field_availability"]={"numeric_heart_rate_nonblank":int(h["heartrate:heart-rate"].ne("").sum()),
          "tag_tech_spec_nonblank":int(h["tag-tech-spec"].ne("").sum()),
          "tag_tech_spec_distinct_count":int(h["tag-tech-spec"].nunique()),
          "quality_named_columns":[c for c in h.columns if re.search("quality|qi",c,re.I)]}
        ids_g=set(canon(g["individual-local-identifier"]));ids_h=set(canon(h["individual-local-identifier"]));ids_r=set(canon(r["animal-id"]))
        report["ref"]={"rows":len(r),"animals":len(ids_r-{""}),"tags":int(r["tag-id"].nunique()),"sex":counts(r["animal-sex"]),
         "mass_nonblank":int(r["animal-mass"].ne("").sum()),"gps_id_in_ref":len(ids_g&ids_r),"hr_id_in_ref":len(ids_h&ids_r),
         "gps_hr_shared_ids":len(ids_g&ids_h),"deployment_date_min":str(ts(r["deploy-on-date"]).min()),"deployment_date_max":str(ts(r["deploy-off-date"]).max())}
        report["linkage"]=time_link(g,h,r)
        report["prior_overlap"]={}
        for k in ("old2016","old2021_22","old2023"):
            if k not in raws:continue
            d=table(raws[k]); old=set(canon(d["animal-id"])); tag=set(canon(d["tag-id"]))
            report["prior_overlap"][k]={"animal_id_matches":len((old&ids_r)-{""}),"tag_id_matches":len((tag&set(canon(r["tag-id"])))-{""}),
              "old_start":str(ts(d["deploy-on-date"]).min()),"old_end":str(ts(d["deploy-off-date"]).max())}
        report["status"]="STRUCTURAL_AUDIT_COMPLETE"
    report["station"]=station()
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
