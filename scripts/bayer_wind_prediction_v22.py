"""V22: later weather-QC source check and independent ERA5 regional sensitivity.
Only aggregate outputs. Fixed comparison; no HR-guided wind adjustment.
"""
import concurrent.futures as cf, hashlib, io, json, pathlib, urllib.parse, zipfile
import numpy as np
import pandas as pd
import bayer_wind_hr_v19 as v
from bayer_field_join_v17 import original, table, fetch
OUT=pathlib.Path("results/bayer_wind_prediction_v22.json")
API="https://api.figshare.com/v2/articles/"
def getjson(url):
    raw,_=fetch(url,5_000_000)
    return json.loads(raw)
def latest_station(item):
    role,aid=item
    out={"role":role,"article_id":aid}
    try:
        versions=getjson(f"{API}{aid}/versions")
        cand=[]
        for row in versions:
            dt=row.get("published_date") or row.get("publishedDate")
            if dt is None:dt=getjson(f"{API}{aid}/versions/{row['version']}").get("published_date")
            if dt and dt[:10]<="2026-11-24":cand.append((dt,int(row["version"])))
        date,num=max(cand)
        meta=getjson(f"{API}{aid}/versions/{num}")
        assert meta["id"]==aid and meta["version"]==num and "Bocas del Toro" in meta["title"] and ("Wind "+role).lower() in meta["title"].lower()
        lic=meta.get("license") or {}
        assert lic.get("name","").lower()=="cc by 4.0" or "creativecommons.org/licenses/by/4.0" in lic.get("url","")
        files=[f for f in meta["files"] if f["name"].lower().endswith(".zip")]
        assert len(files)==1
        f=files[0]
        assert f["size"]<40_000_000
        raw,_=fetch(f["download_url"],f["size"])
        assert len(raw)==f["size"] and hashlib.md5(raw).hexdigest()==(f.get("computed_md5") or f.get("supplied_md5"))
        out.update(version=num,published=date,doi=meta.get("doi"),file_id=f["id"],md5=hashlib.md5(raw).hexdigest(),sha256=hashlib.sha256(raw).hexdigest())
        z=zipfile.ZipFile(io.BytesIO(raw))
        member="bocas_tower_ws_elect.csv" if role=="speed" else "bocas_tower_wdvm_elect.csv"
        assert z.getinfo(member).file_size<120_000_000
        d=pd.read_csv(z.open(member),low_memory=False)
        d["t"]=pd.to_datetime(d.datetime,format="%m/%d/%Y %H:%M:%S",errors="coerce")
        d=d.loc[d.t.between("2023-08-10","2023-08-19 23:59:59")].copy()
        col="ws" if role=="speed" else "wdvm"
        val=pd.to_numeric(d[col],errors="coerce")
        good=d.chk_note.astype(str).str.lower().eq("good")&val.ge(0)&val.notna()&~d.t.duplicated(keep=False)
        if role=="direction":good &= val.le(360)
        out.update(status="HASH_VERIFIED_WINDOW",rows=len(d),quality_counts=d.chk_note.value_counts(dropna=False).to_dict(),good_records=int(good.sum()),good_keys=[str(x) for x in d.loc[good,"t"]])
    except Exception as e:out.update(status="STOP",error=repr(e))
    return role,out

def make_steps():
    rawg,rg=original("gps");rawh,rh=original("hr")
    g=table(rawg);h=table(rawh)
    g["id"]=v.idnorm(g["individual-local-identifier"]);g["t"]=v.dt(g.timestamp)
    h["id"]=v.idnorm(h["individual-local-identifier"]);h["t"]=v.dt(h.timestamp)
    ids=sorted(g.id.unique())
    assert len(g)==2879 and len(h)==101036 and len(ids)==12 and h.id.nunique()==12
    for c in ("location-long","location-lat"):g[c]=pd.to_numeric(g[c],errors="coerce")
    g=g.loc[g.visible.str.lower().eq("true")&g.t.notna()&v.nightmask(g.t)&g["location-long"].between(-180,180)&g["location-lat"].between(-90,90)].copy()
    g["night"]=v.night(g.t)
    g=g.loc[~g.duplicated(["id","t"],keep=False)].sort_values(["id","t"])
    prev=g.groupby(["id","night"])[["t","location-long","location-lat"]].shift()
    g["duration"]=(g.t-prev.t).dt.total_seconds()
    lon1,lat1,lon2,lat2=map(np.deg2rad,(prev["location-long"],prev["location-lat"],g["location-long"],g["location-lat"]))
    dl=lon2-lon1
    g["bearing"]=np.arctan2(np.sin(dl)*np.cos(lat2),np.cos(lat1)*np.sin(lat2)-np.sin(lat1)*np.cos(lat2)*np.cos(dl))
    g["midpoint"]=prev.t+(g.t-prev.t)/2
    g["speed"]=v.dist(prev["location-long"].to_numpy(),prev["location-lat"].to_numpy(),g["location-long"].to_numpy(),g["location-lat"].to_numpy())/g.duration
    g=g.loc[g.duration.between(45,90)&g.speed.gt(0)&g.speed.le(30)].copy()
    before=len(g)
    h["qi"]=pd.to_numeric(h["tag-tech-spec"],errors="coerce")
    h["bpm"]=pd.to_numeric(h["heartrate:heart-rate"],errors="coerce")
    quality=h.qi.isin([0,1])&h.bpm.between(100,900)
    h=h.loc[h.t.notna()&~h.duplicated(["id","t"],keep=False)].sort_values("t")
    h=h[["id","t","qi","bpm"]].rename(columns={"t":"hrt"})
    d=pd.merge_asof(g.sort_values("t"),h,left_on="t",right_on="hrt",by="id",direction="forward",tolerance=pd.Timedelta(seconds=30))
    matched=int(d.hrt.notna().sum());d=d.loc[d.hrt.notna()].copy()
    d["lag"]=(d.hrt-d.t).dt.total_seconds()
    d=d.sort_values("lag",kind="stable").drop_duplicates(["id","hrt"])
    d=d.loc[d.qi.isin([0,1])&d.bpm.between(100,900)].copy()
    t=d.t-pd.Timedelta(hours=5)
    d["hour"]=t.dt.hour+t.dt.minute/60

    return d,{"gps_candidate_steps":before,"matched_before_qc":matched,"source_hr_qi_bpm_pass":int(quality.sum())}

def era5():
    params={"latitude":"9.351553","longitude":"-82.256565","start_date":"2023-08-10","end_date":"2023-08-19",
        "hourly":"wind_speed_10m,wind_direction_10m,wind_speed_100m,wind_direction_100m","models":"era5",
        "wind_speed_unit":"ms","timezone":"GMT","cell_selection":"nearest"}
    url="https://archive-api.open-meteo.com/v1/archive?"+urllib.parse.urlencode(params)
    raw,_=fetch(url,1_000_000)
    x=json.loads(raw); assert x["utc_offset_seconds"]==0
    for h in (10,100):
        assert x["hourly_units"][f"wind_speed_{h}m"]=="m/s"
        assert x["hourly_units"][f"wind_direction_{h}m"]=="°"
    w=pd.DataFrame(x["hourly"]);w["t"]=pd.to_datetime(w.pop("time"),utc=True).dt.as_unit("ns")
    assert len(w)==240 and not w.t.duplicated().any() and w.t.diff().dropna().eq(pd.Timedelta(hours=1)).all()
    assert w.t.min()==pd.Timestamp("2023-08-10",tz="UTC") and w.t.max()==pd.Timestamp("2023-08-19 23:00",tz="UTC")
    assert not w.isna().any().any()
    for h in (10,100):
        assert w[f"wind_speed_{h}m"].between(0,100).all() and w[f"wind_direction_{h}m"].between(0,360).all()
    receipt={"url":url,"sha256":hashlib.sha256(raw).hexdigest(),"hours":len(w),"units":x["hourly_units"],"grid_latitude":x["latitude"],"grid_longitude":x["longitude"],"source":"ERA5 via Open-Meteo; regional reanalysis, not measured local wind"}
    return w,receipt
def features(d,model):
    x=v.features(d,0)
    gg=np.log1p(d.speed.to_numpy());aa=np.log1p(d.airspeed.to_numpy());ww=np.log1p(d.windspeed.to_numpy())
    extra={"B0":[],"G":[gg,gg*gg],"W":[aa,aa*aa],"GW":[gg,gg*gg,ww],"AW":[aa,aa*aa,ww],"weather_only":[ww]}[model]
    return np.column_stack([x]+extra)
def compare(d,field):
    rows=[]
    models=["B0","G","W","GW","AW","weather_only"]
    for k in sorted(d[field].unique()):
        tr=d.loc[d[field]!=k];te=d.loc[d[field]==k]
        if len(tr)<20 or not len(te):continue
        out={}
        for name in models:
            a=features(tr,name);b=features(te,name);mu=a.mean(0);sd=a.std(0);sd[sd<1e-12]=1
            a=(a-mu)/sd;b=(b-mu)/sd
            y=np.log(tr.bpm.to_numpy());beta=np.linalg.solve(a.T@a+np.eye(a.shape[1]),a.T@(y-y.mean()))
            predlog=y.mean()+b@beta;obs=te.bpm.to_numpy()
            out[name]={"MAE_bpm":float(np.mean(abs(np.exp(predlog)-obs))),"RMSE_log":float(np.sqrt(np.mean((predlog-np.log(obs))**2)))}
        rows.append(out)
    if len(rows)<2:return {"status":"STOP_INSUFFICIENT_FOLDS","folds":len(rows)}
    return {"folds":len(rows),"mean_metrics":{m:{q:float(np.mean([r[m][q] for r in rows])) for q in rows[0][m]} for m in models},
        "better_than_G":{m:sum(r[m]["MAE_bpm"]<r["G"]["MAE_bpm"] for r in rows) for m in models if m!="G"}}
def run():
    d,counts=make_steps();w,receipt=era5()
    d=pd.merge_asof(d.sort_values("midpoint"),w.sort_values("t").rename(columns={"t":"weather_time"}),left_on="midpoint",right_on="weather_time",direction="nearest",tolerance=pd.Timedelta(minutes=30))
    d=d.dropna(subset=["weather_time"]).copy()
    result={"status":"ERA5_REGIONAL_SENSITIVITY","source":receipt,"selection":counts,"matched":len(d),"sets":{}}
    for h in (10,100):
        x=d.copy();wind=x[f"wind_speed_{h}m"].to_numpy();theta=np.deg2rad(x[f"wind_direction_{h}m"].to_numpy())
        east=x.speed*np.sin(x.bearing);north=x.speed*np.cos(x.bearing)
        x["airspeed"]=np.hypot(east+wind*np.sin(theta),north+wind*np.cos(theta));x["windspeed"]=wind
        result["sets"][str(h)]={}
        for name,z in [("all",x),("fast",x.loc[x.speed>=3])]:
            result["sets"][str(h)][name]={"records":len(z),"bats":int(z.id.nunique()),"nights":int(z.night.nunique()),"leave_bat_out":compare(z,"id"),"leave_night_out":compare(z,"night"),
               "airspeed_quantiles":np.quantile(z.airspeed,[.05,.5,.95]).tolist() if len(z) else [],
               "windspeed_quantiles":np.quantile(z.windspeed,[.05,.5,.95]).tolist() if len(z) else []}
    return result
def main():
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        f=[ex.submit(latest_station,x) for x in [("speed",10042541),("direction",10042553)]];p=ex.submit(run)
        station=dict(x.result() for x in f)
        a=set(station["speed"].pop("good_keys",[]));b=set(station["direction"].pop("good_keys",[]))
        report={"scope":"separate station QC audit and ERA5-only physiological prediction; not station replication","station":station,"paired_good_station_keys":len(a&b)}
        try:report["era5"]=p.result()
        except Exception as e:report["era5"]={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
