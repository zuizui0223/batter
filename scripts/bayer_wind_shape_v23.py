"""V23: station date diagnosis and regional wind negative controls plus AFPT shape.
Aggregates only, no raw records/coordinates or inferred inactive ID."""
import concurrent.futures as cf,hashlib,io,json,pathlib,zipfile
import numpy as np
import pandas as pd
import bayer_wind_prediction_v22 as v22
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/bayer_wind_shape_v23.json")
STATION={
"speed":(49086346,"0ba69bbf18449dce0eefe06a69138563","901ee367a2c90a6557be5b286174da0a32325a0d381598f5647bfe34612d7f1b","bocas_tower_ws_elect.csv","ws"),
"direction":(49086331,"3e5d2ac915aa46f41c961317d0e8c193","615441c691469d2f094f86f627aaf630884d38492f5066e53ab83e9e633f2f66","bocas_tower_wdvm_elect.csv","wdvm")}
def station(item):
    role,(fid,md5,sha,member,col)=item
    out={"file_id":fid,"sha256":sha}
    try:
        raw,_=fetch("https://ndownloader.figshare.com/files/"+str(fid),40_000_000)
        assert hashlib.md5(raw).hexdigest()==md5 and hashlib.sha256(raw).hexdigest()==sha
        z=zipfile.ZipFile(io.BytesIO(raw))
        assert z.getinfo(member).file_size<120_000_000
        d=pd.read_csv(z.open(member),low_memory=False)
        s=d.datetime.astype(str).str.strip()
        out["total_rows"]=len(d)
        pair=s.str.extract(r"^(\d{1,2})/(\d{1,2})/")
        a,b=pd.to_numeric(pair[0],errors="coerce"),pd.to_numeric(pair[1],errors="coerce")
        out["unambiguous"]={"first_gt12":int((a>12).sum()),"second_gt12":int((b>12).sum())}
        out["first_timestamp_token"]=s.iloc[0]
        out["last_timestamp_token"]=s.iloc[-1]
        out["orders"]={}; keys={}
        val=pd.to_numeric(d[col],errors="coerce")
        for name,fmt,dayfmt in [("MDY","%m/%d/%Y %H:%M:%S","%m/%d/%Y"),("DMY","%d/%m/%Y %H:%M:%S","%d/%m/%Y"),("ISO","%Y-%m-%d %H:%M:%S","%Y-%m-%d")]:
            t=pd.to_datetime(s,format=fmt,errors="coerce")
            day=pd.to_datetime(d.date.astype(str).str.strip(),format=dayfmt,errors="coerce")
            delta=t.dropna().diff().dropna().dt.total_seconds()
            window=t.between("2023-08-10","2023-08-19 23:59:59")
            good=window&d.chk_note.astype(str).str.lower().eq("good")&val.ge(0)&val.notna()&~t.duplicated(keep=False)
            if role=="direction":good &= val.le(360)
            keys[name]=set(t[good].astype(str))
            out["orders"][name]={"parse_fraction":float(t.notna().mean()),"date_agreement":float((t.dt.normalize()==day).mean()),
            "backward_intervals":int((delta<0).sum()),"positive_intervals_le_1h":int(((delta>0)&(delta<=3600)).sum()),
            "window_rows":int(window.sum()),"window_good":int(good.sum()),
            "window_qc":{str(k):int(v) for k,v in d.loc[window,"chk_note"].value_counts(dropna=False).items()},
            "window_unique_timestamps":int(t[window].nunique())}
        admitted=[k for k,v in out["orders"].items() if v["parse_fraction"]>=.99 and v["date_agreement"]>=.99 and v["backward_intervals"]==0]
        out["admitted_order"]=admitted[0] if len(admitted)==1 else None
        out["status"]="DATE_ORDER_VERIFIED" if len(admitted)==1 else "DATE_ORDER_UNRESOLVED"
        return role,out,keys.get(out["admitted_order"],set())
    except Exception as e:
        out.update(status="STOP",error=repr(e))
        return role,out,set()

def features(d,name):
    if name in ("B0","G","W","GW","AW","weather_only"):
        return v22.features(d,name)
    x=v22.v.features(d,0)
    if name=="P":return np.column_stack([x,np.log(d.power.to_numpy())])
    z=np.log1p(d[name].to_numpy())
    return np.column_stack([x,z,z*z])

def compare(d,field,models):
    rows=[]
    for k in sorted(d[field].unique()):
        tr=d[d[field]!=k];te=d[d[field]==k]
        if len(tr)<20 or not len(te):continue
        out={}
        for name in models:
            a,b=features(tr,name),features(te,name)
            mu=a.mean(0);sd=a.std(0);sd[sd<1e-12]=1
            a=(a-mu)/sd;b=(b-mu)/sd
            y=np.log(tr.bpm.to_numpy())
            beta=np.linalg.solve(a.T@a+np.eye(a.shape[1]),a.T@(y-y.mean()))
            predlog=y.mean()+b@beta;obs=te.bpm.to_numpy()
            out[name]={"mae":float(np.mean(abs(np.exp(predlog)-obs))),"log_rmse":float(np.sqrt(np.mean((predlog-np.log(obs))**2)))}
        rows.append(out)
    if len(rows)<2:return {"folds":len(rows),"status":"STOP"}
    return {"folds":len(rows),"mean":{m:{q:float(np.mean([r[m][q] for r in rows])) for q in ("mae","log_rmse")} for m in models},
      "wins_vs_G":{m:sum(r[m]["mae"]<r["G"]["mae"] for r in rows) for m in models if m!="G"},
      "W_wins_vs":{m:sum(r["W"]["mae"]<r[m]["mae"] for r in rows) for m in models if m!="W"}}

def panel(d,models):
    return {"records":len(d),"bats":int(d.id.nunique()),"nights":int(d.night.nunique()),
      "counts_per_bat":sorted(int(n) for n in d.id.value_counts()),"leave_bat_out":compare(d,"id",models),"leave_night_out":compare(d,"night",models)}

def envelope(d):
    models=["B0","G","W"]
    out={}
    for fld in ("id","night"):
        gains={"vs_G":[],"vs_B0":[]}
        for a in sorted(d.id.unique()):
            x=compare(d[d.id!=a],fld,models)
            if "mean" not in x:continue
            q=x["mean"]
            gains["vs_G"].append(q["G"]["mae"]-q["W"]["mae"])
            gains["vs_B0"].append(q["B0"]["mae"]-q["W"]["mae"])
        out[fld]={k:{"n":len(a),"range":[min(a),max(a)] if a else [],"positive":sum(x>0 for x in a)} for k,a in gains.items()}
    return out

def power_interp(u,grid,p,valid):
    # exact or adjacent valid grid interpolation; never bridge invalid interval
    pos=np.searchsorted(grid,u,side="right")-1
    clip=np.clip(pos,0,len(grid)-2)
    admiss=(u>=grid[0])&(u<=grid[-1])&valid[clip]&valid[clip+1]
    ans=np.full(len(u),np.nan)
    ans[admiss]=np.interp(u[admiss],grid,p)
    return ans

def run():
    d,counts=v22.make_steps();w,receipt=v22.era5()
    assert len(d)==349 and len(d[d.speed>=3])==177
    receipt["hourly_data_sha256"]=hashlib.sha256(w.to_csv(index=False).encode()).hexdigest()
    d=pd.merge_asof(d.sort_values("midpoint"),w.sort_values("t").rename(columns={"t":"weather_time"}),left_on="midpoint",right_on="weather_time",direction="nearest",tolerance=pd.Timedelta(minutes=30))
    assert d.weather_time.notna().all()
    g=pd.read_csv("external/bayer_afpt_curve_v23.csv")
    speed,p=g.speed.to_numpy(),g.power.to_numpy();valid=g.valid.astype(str).str.lower().eq("true").to_numpy()
    assert len(speed)==241 and valid.any()
    report={"status":"REGIONAL_DIAGNOSTIC","weather_receipt":receipt,"selection":counts,
       "afpt_grid":{"n_valid":int(valid.sum()),"n_total":len(valid),"endpoints":speed[valid][[0,-1]].tolist()},"sets":{}}
    expected={10:(53.117209,53.923525,61.793041,62.416460,84.601697,71.084643,82.001836,72.975299),
              100:(53.117209,53.559544,61.793041,62.072353,84.601697,69.210980,82.001836,71.401057)}
    for h in (10,100):
        x=d.copy();wind=x[f"wind_speed_{h}m"].to_numpy();theta=np.deg2rad(x[f"wind_direction_{h}m"].to_numpy())
        east=x.speed*np.sin(x.bearing);north=x.speed*np.cos(x.bearing)
        for rot in (0,90,180,270):
            t=theta+np.deg2rad(rot)
            x["airspeed" if rot==0 else "R"+str(rot)]=np.hypot(east+wind*np.sin(t),north+wind*np.cos(t))
        x["windspeed"]=wind;x["power"]=power_interp(x.airspeed.to_numpy(),speed,p,valid)
        out={}; seen=[]
        for label,z in [("all",x),("fast",x[x.speed>=3])]:
            q=panel(z,["B0","G","W","GW","weather_only","R90","R180","R270"])
            for fold in ("leave_bat_out","leave_night_out"):
                seen.extend([q[fold]["mean"][k]["mae"] for k in ("G","W")])
            q["omission"]=envelope(z)
            m=z[z.power.notna()].copy()
            eligible=len(m)>=50 and m.id.nunique()>=5 and m.night.nunique()>=3 and (m.id.value_counts()>=5).sum()>=3
            q["AFPT"]={"status":"COMMON_SUPPORT" if eligible else "STOP_LOW_SUPPORT","records":len(m),"bats":int(m.id.nunique()),"nights":int(m.night.nunique()),"excluded":len(z)-len(m)}
            if eligible:q["AFPT"]["panel"]=panel(m,["B0","G","W","weather_only","P"])
            out[label]=q
        err=float(np.max(abs(np.array(seen)-expected[h])))
        if err>.05:return {"status":"STOP_V22_DRIFT","height":h,"max_mae_drift":err,"weather_receipt":receipt}
        out["max_v22_mae_drift"]=err
        report["sets"][str(h)]=out
    return report
def main():
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        fs=[ex.submit(station,x) for x in STATION.items()];rr=ex.submit(run)
        a,b=[f.result() for f in fs]
        result={"scope":"station date audit plus regional negative controls; conditional HR prediction","station":{a[0]:a[1],b[0]:b[1]},
                "paired_admitted_station_keys":len(a[2]&b[2])}
        try:result["regional"]=rr.result()
        except Exception as e:result["regional"]={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    print(OUT.read_text())
if __name__=="__main__":main()
