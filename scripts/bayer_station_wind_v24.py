"""V24: all pre-specified station conventions, same GPS-HR rows.
No outcome-driven convention choice; no source observations exported."""
import concurrent.futures as cf,hashlib,io,json,pathlib,zipfile
import numpy as np
import pandas as pd
import bayer_wind_shape_v23 as v23
import bayer_wind_prediction_v22 as v22
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/bayer_station_wind_v24.json")

def get_series(item):
    role,(fid,md5,sha,member,col)=item
    raw,_=fetch("https://ndownloader.figshare.com/files/"+str(fid),40_000_000)
    assert hashlib.md5(raw).hexdigest()==md5 and hashlib.sha256(raw).hexdigest()==sha
    z=zipfile.ZipFile(io.BytesIO(raw))
    assert z.getinfo(member).file_size<120_000_000
    d=pd.read_csv(z.open(member),low_memory=False)
    d["t"]=pd.to_datetime(d.datetime.astype(str).str.strip(),format="%d/%m/%Y %H:%M:%S",errors="raise")
    d=d.loc[d.t.between("2023-08-10","2023-08-19 23:59:59")].copy().sort_values("t")
    assert len(d)==960 and not d.t.duplicated().any() and d.t.diff().dropna().eq(pd.Timedelta(minutes=15)).all()
    assert d.chk_note.astype(str).str.lower().eq("good").all()
    val=pd.to_numeric(d[col],errors="raise")
    assert val.notna().all() and val.ge(0).all()
    if role=="direction":assert val.le(360).all()
    else:assert val.le(360).all()
    return role,pd.DataFrame({"t":d.t,role:val})

def vector(w,zone,sense,angle,mid):
    t=w.t.dt.tz_localize("UTC").dt.as_unit("ns")
    if zone=="EST":t=t+pd.Timedelta(hours=5)
    if mid:t=t-pd.Timedelta(minutes=7.5)
    direction=np.deg2rad(w.direction.to_numpy()+angle)
    speed=w.speed.to_numpy()/3.6
    sign=-1 if sense=="FROM" else 1
    return t.astype("int64").to_numpy()/1e9,sign*speed*np.sin(direction),sign*speed*np.cos(direction)

def interp(t,u,v,target):
    x=target.astype("int64").to_numpy()/1e9
    j=np.searchsorted(t,x,side="right")
    good=(j>0)&(j<len(t))
    k=np.clip(j,1,len(t)-1)
    good &= np.isclose(t[k]-t[k-1],900)
    a=np.full(len(x),np.nan);b=a.copy()
    a[good]=np.interp(x[good],t,u);b[good]=np.interp(x[good],t,v)
    return a,b

def comp(a,b):
    if np.std(a)<1e-12 or np.std(b)<1e-12:return None
    return float(np.corrcoef(a,b)[0,1])

def panel(d,models):
    out={}
    for label,z in [("all",d),("fast",d[d.speed>=3])]:
        r=v23.panel(z,models)
        out[label]={"records":r["records"],"bats":r["bats"],"nights":r["nights"]}
        for f in ("leave_bat_out","leave_night_out"):
            out[label][f]=r[f]
    return out

def main():
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        fs=[ex.submit(get_series,x) for x in v23.STATION.items()]
        steps=ex.submit(v22.make_steps);era=ex.submit(v22.era5)
        station=dict(f.result() for f in fs);d,selection=steps.result();e,receipt=era.result()
    w=station["speed"].merge(station["direction"],on="t",validate="one_to_one")
    assert len(w)==960 and len(d)==349 and len(d[d.speed>=3])==177
    theta=np.deg2rad(e.wind_direction_10m.to_numpy())
    eu=-e.wind_speed_10m.to_numpy()*np.sin(theta)
    ev=-e.wind_speed_10m.to_numpy()*np.cos(theta)
    # Evaluate independent weather agreement before using HR models.
    scenarios=[(z,s,a,mid) for z in ("EST","UTC") for s in ("FROM","TO") for a,mid in [(0,True),(-10,True),(10,True),(0,False)]]
    weather={};vectors={}
    for z,s,a,mid in scenarios:
        key=f"{z}_{s}_{a}_{'mid' if mid else 'end'}"
        t,u,v=vector(w,z,s,a,mid)
        su,sv=interp(t,u,v,e.t)
        k=np.isfinite(su)&np.isfinite(sv)
        assert k.sum()>=200
        weather[key]={"hours":int(k.sum()),"vector_rmse_m_s":float(np.sqrt(np.mean((su[k]-eu[k])**2+(sv[k]-ev[k])**2))),
          "east_r":comp(su[k],eu[k]),"north_r":comp(sv[k],ev[k]),
          "station_speed_quantiles_m_s":np.quantile(np.hypot(su[k],sv[k]),[.05,.5,.95]).tolist(),
          "era5_speed_quantiles_m_s":np.quantile(e.wind_speed_10m.to_numpy()[k],[.05,.5,.95]).tolist()}
        x,y=interp(t,u,v,d.midpoint)
        assert np.isfinite(x).all() and np.isfinite(y).all()
        vectors[key]=(x,y)
    models=["B0","G","W","GW","weather_only","R90","R180","R270"]
    results={}
    for key,(u,v) in vectors.items():
        x=d.copy();east=x.speed*np.sin(x.bearing);north=x.speed*np.cos(x.bearing)
        x["windspeed"]=np.hypot(u,v)
        for rot in (0,90,180,270):
            th=np.deg2rad(rot)
            # clockwise rotation of a vector (east,north)
            ur=u*np.cos(th)+v*np.sin(th);vr=-u*np.sin(th)+v*np.cos(th)
            x["airspeed" if rot==0 else "R"+str(rot)]=np.hypot(east-ur,north-vr)
        results[key]=panel(x,models)
    nominal=[f"{z}_{s}_0_mid" for z in ("EST","UTC") for s in ("FROM","TO")]
    gate={}
    for key in nominal:
        p=results[key]["fast"]
        gate[key]=all(p[f]["mean"]["W"]["mae"]<min(p[f]["mean"]["G"]["mae"],p[f]["mean"]["B0"]["mae"]) for f in ("leave_bat_out","leave_night_out"))
    report={"scope":"station convention sensitivity; no selected convention or empirical causal claim","status":"COMPLETE",
        "station_keys":len(w),"source_sha256":{r:x[2] for r,x in v23.STATION.items()},"selection":selection,
        "era5_receipt":receipt,"weather_agreement":weather,"results":results,"nominal_gate":gate,"all_nominal_pass":all(gate.values())}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    # compact log, full metrics stored in artifact
    print(json.dumps({"status":report["status"],"station_keys":len(w),"weather_agreement":weather,
      "nominal_gate":gate,"nominal_fast_mae":{key:{f:{m:r["mae"] for m,r in results[key]["fast"][f]["mean"].items()} for f in ("leave_bat_out","leave_night_out")} for key in nominal}},indent=2,allow_nan=False))
if __name__=="__main__":main()
