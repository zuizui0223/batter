"""V21: independent GPS-only baseline, and separate original station source audit."""
import concurrent.futures as cf, hashlib, io, json, pathlib, re, zipfile
import numpy as np
import pandas as pd
import bayer_wind_hr_v19 as v
from bayer_archive_id_v20 import FILES
from bayer_field_join_v17 import original,table,fetch
from pypdf import PdfReader
OUT=pathlib.Path("results/bayer_all_animal_baseline_v21.json")

def weather(item):
    role,(fid,size,md5)=item
    out={"file_id":fid}
    try:
        raw,_=fetch(f"https://ndownloader.figshare.com/files/{fid}",size)
        assert len(raw)==size and hashlib.md5(raw).hexdigest()==md5
        out.update(md5=md5,sha256=hashlib.sha256(raw).hexdigest())
        z=zipfile.ZipFile(io.BytesIO(raw))
        member="bocas_tower_ws_elect.csv" if role=="speed" else "bocas_tower_wdvm_elect.csv"
        readme="readme-Bocas_WS.txt" if role=="speed" else "readme-Bocas_WDVM.txt"
        out["readme"]=z.read(readme).decode("utf-8-sig",errors="replace")
        pdf=PdfReader(io.BytesIO(z.read("Methods_Electronic_Wind_Speed_Dir.pdf")))
        out["methods_text"]="\n".join(p.extract_text() or "" for p in pdf.pages)[:18000]
        d=pd.read_csv(z.open(member),low_memory=False)
        d["t"]=pd.to_datetime(d.datetime,format="%m/%d/%Y %H:%M:%S",errors="coerce")
        d=d.loc[d.t.between("2023-08-10","2023-08-19 23:59:59")].copy()
        col="ws" if role=="speed" else "wdvm"
        d["value"]=pd.to_numeric(d[col],errors="coerce")
        good=d.chk_note.astype(str).str.lower().eq("good")&d.value.ge(0)&d.value.notna()&~d.t.duplicated(keep=False)
        if role=="direction":good &= d.value.le(360)
        out.update(status="HASH_VERIFIED_WINDOW",rows=len(d),duplicate_rows=int(d.t.duplicated(keep=False).sum()),quality_counts=d.chk_note.value_counts(dropna=False).to_dict(),
                   first=str(d.t.min()),last=str(d.t.max()),good_records=int(good.sum()),
                   good_time_keys=[str(x) for x in d.loc[good,"t"]])
    except Exception as e:out.update(status="STOP",error=repr(e))
    return role,out

def baseline():
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
    result={"status":"ALL_ANIMAL_GPS_ONLY_BASELINE","gps_sha256":rg["sha256"],"hr_sha256":rh["sha256"],
            "source_hr_qi_bpm_pass":int(quality.sum()),"gps_candidate_steps":before,"matched_before_qc":matched,"sets":{}}
    for label,x in [("all",d),("speed_ge_3_sensitivity",d.loc[d.speed>=3])]:
        o={"records":len(x),"bats":int(x.id.nunique()),"nights":int(x.night.nunique()),"bat_nights":len(x[["id","night"]].drop_duplicates()),
           "counts_per_bat_including_zero":sorted(int((x.id==i).sum()) for i in ids)}
        for field in ("id","night"):
            o["leave_"+field+"_out"]=v.cv(x,field)
            deltas={"1":[],"2":[]}
            for omitted in ids:
                z=v.cv(x.loc[x.id!=omitted],field)
                if "mean_fold_metrics" not in z:continue
                q=z["mean_fold_metrics"]
                for m in deltas:deltas[m].append(q["0"]["MAE_bpm"]-q[m]["MAE_bpm"])
            o["exclude_one_"+field+"_out"]={m:{"evaluated":len(a),"min_gain_bpm":min(a) if a else None,"max_gain_bpm":max(a) if a else None,
                "positive_gain":sum(s>0 for s in a)} for m,a in deltas.items()}
        result["sets"][label]=o
    return result

def main():
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        fs=[ex.submit(weather,x) for x in FILES.items()];b=ex.submit(baseline)
        weather_results=dict(f.result() for f in fs)
        if all(x.get("status")=="HASH_VERIFIED_WINDOW" for x in weather_results.values()):
            a=set(weather_results["speed"].pop("good_time_keys"));c=set(weather_results["direction"].pop("good_time_keys"))
            paired={"good_speed":len(a),"good_direction":len(c),"paired":len(a&c)}
        else:
            paired={"status":"STOP"}
            for x in weather_results.values():x.pop("good_time_keys",None)
        result={"scope":"independent GPS-HR baseline; separate weather source audit; not article exact reproduction","weather":weather_results,"paired_station_keys":paired}
        try:result["baseline"]=b.result()
        except Exception as e:result["baseline"]={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n");print(OUT.read_text())
if __name__=="__main__":main()
