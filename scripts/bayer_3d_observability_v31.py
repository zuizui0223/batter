"""V31 GPS-only vertical observability; no altitude calibration or occupancy inference."""
import json,pathlib,re
import numpy as np
import pandas as pd
from bayer_field_join_v17 import original,table
import bayer_wind_hr_v19 as v
OUT=pathlib.Path("results/bayer_3d_observability_v31.json")
ID="individual-local-identifier"; H="height-above-msl"; D="gps:hdop"; S="gps:satellite-count"
def quant(x):
    a=np.asarray(x,dtype=float);a=a[np.isfinite(a)]
    return np.quantile(a,[0,.05,.25,.5,.75,.95,1]).tolist() if len(a) else []
def stat(d):
    n=len(d);q=d[d.pair_height]
    return {"steps":n,"bats":int(d.id.nunique()),"nights":int(d.night.nunique()),
      "paired_altitude_steps":len(q),"paired_altitude_bats":int(q.id.nunique()),"paired_altitude_nights":int(q.night.nunique()),
      "steps_per_bat":sorted(int(x) for x in d.id.value_counts()),
      "paired_steps_per_bat":sorted(int((q.id==k).sum()) for k in d.id.unique()),
      "endpoint_altitude_msl_quantiles":quant(np.r_[q[H].to_numpy(),q.prev_h.to_numpy()]),
      "delta_altitude_m_quantiles":quant(q.dz),"absolute_delta_altitude_m_quantiles":quant(q.dz.abs()),
      "vertical_net_rate_m_s_quantiles":quant(q.dz/q.duration),
      "same_altitude_count":int(q.dz.eq(0).sum()),"negative_endpoint_count":int(((q[H]<0)|(q.prev_h<0)).sum())}
def run():
    raw,receipt=original("gps");g=table(raw);r=table(original("ref")[0])
    assert len(g)==2879 and receipt["sha256"]=="936d9f444bdcf882a984dfa5375bee69a50d2f4db11c15266965bb3bfcdb3ced"
    assert all(c in g for c in [H,D,S,ID])
    g["id"]=v.idnorm(g[ID]);g["t"]=v.dt(g.timestamp)
    for c in [H,D,S,"location-long","location-lat"]:
        g[c]=pd.to_numeric(g[c],errors="coerce")
        g[c]=g[c].where(np.isfinite(g[c]))
    source={"rows":len(g),"bats":int(g.id.nunique()),"height_nonmissing":int(g[H].notna().sum()),
      "hdop_nonmissing":int(g[D].notna().sum()),"satellites_nonmissing":int(g[S].notna().sum()),
      "height_msl_quantiles":quant(g[H]),"hdop_quantiles":quant(g[D]),"satellite_count_quantiles":quant(g[S]),
      "source_fields":[c for c in g.columns if re.search("height|altitude|accuracy|hdop|satellite|signal.quality",c,re.I)]}
    # Count possible source documentation without reporting metadata text or identities.
    pattern=r"(?i)vertical accuracy|altitude accuracy|altitude datum|height datum|geoid|ellipsoid|above mean sea level|VDOP|vertical dilution"
    source["reference_rows_with_possible_altitude_documentation"]=int(r["tag-settings"].astype(str).str.contains(pattern,regex=True).sum())
    source["reference_columns"]=[c for c in r.columns if re.search("height|altitude|accuracy|quality",c,re.I)]
    g=g.loc[g.visible.str.lower().eq("true")&g.t.notna()&v.nightmask(g.t)&g["location-long"].between(-180,180)&g["location-lat"].between(-90,90)].copy()
    g["night"]=v.night(g.t);g=g.loc[~g.duplicated(["id","t"],keep=False)].sort_values(["id","night","t"])
    p=g.groupby(["id","night"])[["t","location-long","location-lat",H,D,S]].shift()
    g["duration"]=(g.t-p.t).dt.total_seconds()
    g["distance"]=v.dist(p["location-long"].to_numpy(),p["location-lat"].to_numpy(),g["location-long"].to_numpy(),g["location-lat"].to_numpy())
    g["speed"]=g.distance/g.duration
    g["prev_h"]=p[H];g["prev_d"]=p[D];g["prev_s"]=p[S];g["prev_t"]=p.t
    g["pair_height"]=g[H].notna()&g.prev_h.notna();g["dz"]=g[H]-g.prev_h
    g=g.loc[g.duration.between(45,90)&g.speed.gt(0)&g.speed.le(30)].copy()
    assert len(g)==1725
    quality={"all":np.ones(len(g),bool),
      "hdop3_sat5":g[D].between(0,3)&g.prev_d.between(0,3)&g[S].ge(5)&g.prev_s.ge(5),
      "hdop2_sat6":g[D].between(0,2)&g.prev_d.between(0,2)&g[S].ge(6)&g.prev_s.ge(6)}
    result={}
    for name,m in quality.items():
        a=g.loc[m];result[name]={"all":stat(a),"fast":stat(a[a.speed>=3]),"low_displacement_le10m":stat(a[a.distance<=10])}
        q=a[a.pair_height].copy()
        q["previous_end"]=q.groupby(["id","night"]).t.shift()
        q["previous_dz"]=q.groupby(["id","night"]).dz.shift()
        q=q[q.prev_t.eq(q.previous_end)&q.dz.ne(0)&q.previous_dz.ne(0)]
        result[name]["contiguous_nonzero_triples"]={"count":len(q),"opposite_sign_count":int((q.dz*q.previous_dz<0).sum())}
    return {"scope":"GPS-only 3D observability; reported MSL and net endpoint differences, not AGL or validated vertical motion",
       "status":"COMPLETE","source":source,"source_sha256":receipt["sha256"],"night_fixes_before_step_filter":int(p.shape[0]),"screens":result,
       "limits":"HDOP and satellite screens are horizontal quality proxies, not vertical accuracy. No DEM, no state labels, no independent altitude calibration."}
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
    if r["status"]=="STOP":raise SystemExit(2)
