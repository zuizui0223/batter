"""V19: two separate gates, historical wind schema and GPS-only HR prediction.
No raw coordinates, records, or animal identifiers output. Noncommercial research.
"""
import concurrent.futures as cf, csv, hashlib, io, json, pathlib, re, urllib.parse, urllib.request
import numpy as np
import pandas as pd
from bayer_field_join_v17 import original, table, fetch

OUT=pathlib.Path("results/bayer_wind_hr_v19.json")
ARTICLES={"speed":10042541,"direction":10042553}
API="https://api.figshare.com/v2/articles/"
def getjson(url):
    raw,_=fetch(url,4_000_000)
    return json.loads(raw)
def weather(kv):
    key,aid=kv
    out={"article_id":aid,"role":key}
    try:
        versions=getjson(f"{API}{aid}/versions")
        candidates=[]
        for row in versions:
            # Figshare returns a date field for each published version.
            dt=row.get("published_date") or row.get("publishedDate")
            if dt is None:
                meta=getjson(f"{API}{aid}/versions/{row['version']}")
                dt=meta.get("published_date")
            if dt and dt[:10]>"2023-08-18":
                candidates.append((dt,int(row["version"])))
        if not candidates:raise ValueError("No post-tracking version found")
        date,v=min(candidates)
        meta=getjson(f"{API}{aid}/versions/{v}")
        assert meta["id"]==aid and meta["version"]==v
        assert "Bocas del Toro" in meta["title"] and ("Wind "+key).lower() in meta["title"].lower()
        license=meta.get("license") or {}
        assert "creativecommons.org/licenses/by/4.0" in str(license.get("url","")).lower() or str(license.get("name","")).lower()=="cc by 4.0"
        out.update(version=v,published=date,title=meta["title"],doi=meta.get("doi"),license=license,files=[])
        for f in meta["files"]:
            info={k:f.get(k) for k in ("id","name","size","computed_md5","supplied_md5","download_url")}
            out["files"].append(info)
            if not f["name"].lower().endswith((".csv",".txt")) or f["size"]>35_000_000:continue
            try:
                b,_=fetch(f["download_url"],35_000_000)
                md5=hashlib.md5(b).hexdigest()
                assert len(b)==f["size"] and md5==(f.get("computed_md5") or f["supplied_md5"])
                info.update(sha256=hashlib.sha256(b).hexdigest(),status="HASH_VERIFIED")
                s=b.decode("utf-8-sig",errors="strict")
                lines=[x for x in s.splitlines() if x.strip()]
                sample=lines[:10]
                # Print header, date tokens only. Never report wind values.
                dialect=csv.Sniffer().sniff("\n".join(sample),delimiters=",;\t")
                reader=csv.reader(io.StringIO(s),dialect)
                header=next(reader)
                date_re=re.compile(r"(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})")
                first,last=None,None
                n=0;aug2023=0
                for row in reader:
                    if not row:continue
                    n+=1
                    tokens=[x[:40] for x in row if date_re.search(x) and len(x)<50]
                    if tokens:
                        if first is None:first=tokens
                        last=tokens
                        if any(re.search(r"2023[-/]0?8[-/]|0?8[-/]\d{1,2}[-/]2023|\d{1,2}[-/]0?8[-/]2023",t) for t in tokens):aug2023+=1
                info.update(header=header,rows=n,first_date_tokens=first,last_date_tokens=last,aug2023_candidate_rows=aug2023)
            except Exception as e:info.update(status="STOP",error=repr(e))
        out["status"]="HASH_VERIFIED_CSV" if any(f.get("status")=="HASH_VERIFIED" and "header" in f for f in out["files"]) else "NO_ADMITTED_CSV"
    except Exception as e:out.update(status="SOURCE_STOP",error=repr(e))
    return key,out
def dt(s):return pd.to_datetime(s,format="mixed",utc=True,errors="coerce").dt.as_unit("ns")
def idnorm(s):return s.astype(str).str.strip().str.casefold()
def night(t):return (t-pd.Timedelta(hours=17)).dt.strftime("%Y-%m-%d")
def nightmask(t):
    hr=(t-pd.Timedelta(hours=5)).dt.hour
    return ((hr>=18)|(hr<5))&(night(t)!="2023-08-11")
def dist(lon1,lat1,lon2,lat2):
    lon1,lat1,lon2,lat2=map(np.deg2rad,(lon1,lat1,lon2,lat2))
    a=np.sin((lat2-lat1)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 6371008.8*2*np.arcsin(np.sqrt(np.clip(a,0,1)))
def features(d,model):
    hour=d.hour.to_numpy()*2*np.pi/24
    x=np.column_stack([np.sin(hour),np.cos(hour),np.log(d.duration.to_numpy())])
    if model>=1:
        g=np.log1p(d.speed.to_numpy())
        x=np.column_stack([x,g])
        if model==2:x=np.column_stack([x,g*g])
    return x
def cv(d,group):
    rows=[]
    for k in sorted(d[group].unique()):
        train=d[d[group]!=k];test=d[d[group]==k]
        if len(train)<20 or not len(test):continue
        result={}
        for model in (0,1,2):
            x=features(train,model);z=features(test,model)
            mu=x.mean(0);sd=x.std(0);sd[sd<1e-12]=1
            x=(x-mu)/sd;z=(z-mu)/sd
            y=np.log(train.bpm.to_numpy())
            beta=np.linalg.solve(x.T@x+np.eye(x.shape[1]),x.T@(y-y.mean()))
            predlog=y.mean()+z@beta;obs=test.bpm.to_numpy()
            pred=np.exp(predlog)
            result[str(model)]={"MAE_bpm":float(np.mean(abs(pred-obs))),"RMSE_bpm":float(np.sqrt(np.mean((pred-obs)**2))),"RMSE_log":float(np.sqrt(np.mean((predlog-np.log(obs))**2)))}
        rows.append(result)
    if len(rows)<2:return {"status":"STOP_FEWER_THAN_TWO_FOLDS","folds":len(rows)}
    return {"folds":len(rows),"mean_fold_metrics":{str(m):{k:float(np.mean([r[str(m)][k] for r in rows])) for k in rows[0][str(m)]} for m in (0,1,2)},
     "MAE_improved_folds_vs_B0":{str(m):sum(r[str(m)]["MAE_bpm"]<r["0"]["MAE_bpm"] for r in rows) for m in (1,2)}}
def baseline():
    rawg,rg=original("gps");rawh,rh=original("hr")
    g=table(rawg);h=table(rawh)
    g["id"]=idnorm(g["individual-local-identifier"]);g["t"]=dt(g.timestamp)
    h["id"]=idnorm(h["individual-local-identifier"]);h["t"]=dt(h.timestamp)
    assert len(g)==2879 and len(h)==101036 and g.id.nunique()==12 and h.id.nunique()==12
    # Only remove the paper's named inactive GPS animal after matching actual ID.
    inactive=g.id.str.replace(r"\s+","",regex=True).eq("phyl30")
    if not inactive.any():raise ValueError("Published inactive GPS ID not found")
    for c in ("location-long","location-lat"):g[c]=pd.to_numeric(g[c],errors="coerce")
    g=g.loc[~inactive & g.visible.str.lower().eq("true") & g.t.notna() & nightmask(g.t) & g["location-long"].between(-180,180)&g["location-lat"].between(-90,90)].copy()
    g["night"]=night(g.t)
    g=g.loc[~g.duplicated(["id","t"],keep=False)].sort_values(["id","t"])
    prev=g.groupby(["id","night"])[["t","location-long","location-lat"]].shift()
    g["duration"]=(g.t-prev.t).dt.total_seconds()
    g["speed"]=dist(prev["location-long"].to_numpy(),prev["location-lat"].to_numpy(),g["location-long"].to_numpy(),g["location-lat"].to_numpy())/g.duration
    g=g.loc[g.duration.between(45,90)&g.speed.gt(0)&g.speed.le(30)].copy()
    before=len(g)
    h["qi"]=pd.to_numeric(h["tag-tech-spec"],errors="coerce")
    h["bpm"]=pd.to_numeric(h["heartrate:heart-rate"],errors="coerce")
    quality=h.qi.isin([0,1])&h.bpm.between(100,900)
    # Find nearest original HR timestamp first; quality mask only after matching.
    h=h.loc[h.t.notna()&~h.duplicated(["id","t"],keep=False)].sort_values("t")
    h=h[["id","t","qi","bpm"]].rename(columns={"t":"hrt"})
    d=pd.merge_asof(g.sort_values("t"),h,left_on="t",right_on="hrt",by="id",direction="forward",tolerance=pd.Timedelta(seconds=30))
    matched=int(d.hrt.notna().sum());d=d.loc[d.hrt.notna()].copy()
    d["lag"]=(d.hrt-d.t).dt.total_seconds()
    d=d.sort_values("lag",kind="stable").drop_duplicates(["id","hrt"])
    d=d.loc[d.qi.isin([0,1])&d.bpm.between(100,900)].copy()
    t=d.t-pd.Timedelta(hours=5)
    d["hour"]=t.dt.hour+t.dt.minute/60
    result={"status":"GPS_ONLY_PREDICTIVE_BASELINE","gps_sha256":rg["sha256"],"hr_sha256":rh["sha256"],"source_hr_qi_bpm_pass":int(quality.sum()),"gps_candidate_steps":before,"matched_before_qc":matched,"sets":{}}
    for label,x in [("all",d),("speed_ge_3_sensitivity",d.loc[d.speed>=3])]:
        result["sets"][label]={"records":len(x),"bats":x.id.nunique(),"nights":x.night.nunique(),"bat_nights":len(x[["id","night"]].drop_duplicates()),"leave_bat_out":cv(x,"id"),"leave_night_out":cv(x,"night")}
    return result
def main():
    report={"scope":"weather schema only; separate GPS-only HR predictive comparison; not wind or flight-state validation"}
    with cf.ThreadPoolExecutor(max_workers=3) as pool:
        fut=[pool.submit(weather,x) for x in ARTICLES.items()];b=pool.submit(baseline)
        report["weather"]=dict(f.result() for f in fut)
        try:report["baseline"]=b.result()
        except Exception as e:report["baseline"]={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
