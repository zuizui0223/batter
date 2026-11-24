"""V29: pilot gravity-unit diagnostic, two literal source-threshold conventions.
No HR response opened. One-second approximation, no ground-truth flight label.
"""
import hashlib,io,json,pathlib,zipfile
import numpy as np
import pandas as pd
from bayer_acc_hr_transfer_v26 import SPECS,AX,ID,TAG,NS,STEP
from bayer_field_join_v17 import original,table,fetch
import bayer_wind_hr_v19 as v
OUT=pathlib.Path("results/bayer_flight_gate_v29.json")
G=9.80665
class PoseSeconds:
    """Retain the final partial second across read chunks; no interpolation."""
    def __init__(self):
        self.tail_t=np.empty(0,dtype=np.int64)
        self.tail_x=np.empty((0,3))
        self.last=None; self.seconds=[];self.activity=[]
        self.n=0;self.gaps=0;self.partial=0;self.bad_values=0;self.static=[]
    def consume(self,t,x,final=False):
        t=np.asarray(t,np.int64);x=np.asarray(x,float)
        assert x.shape==(len(t),3)
        if len(t):
            delta=np.diff(t,prepend=self.last if self.last is not None else t[0]-STEP)
            assert np.all(delta>0),"nonmonotone/duplicate timestamp"
            assert np.all(delta%STEP==0),"unexpected 25-Hz clock grid"
            self.gaps+=int((delta>STEP).sum())
            self.last=int(t[-1]);self.n+=len(t)
        t=np.r_[self.tail_t,t];x=np.vstack([self.tail_x,x])
        if not len(t):return
        sec=t//NS
        cut=len(t) if final else int(np.searchsorted(sec,sec[-1],side="left"))
        self.tail_t=t[cut:];self.tail_x=x[cut:]
        t=t[:cut];x=x[:cut];sec=sec[:cut]
        if not len(t):return
        ss,idx,cnt=np.unique(sec,return_index=True,return_counts=True)
        good=cnt==25
        self.partial+=int((~good).sum())
        if not good.any():return
        j=idx[good,None]+np.arange(25)[None,:]
        a=x[j];tt=t[j]
        ok=np.isfinite(a).all(axis=(1,2))&(np.diff(tt,axis=1)==STEP).all(axis=1)
        self.bad_values+=int((~ok).sum())
        a=a[ok];s=ss[good][ok]
        v=np.linalg.norm(a-a.mean(axis=1,keepdims=True),axis=2).mean(axis=1)
        self.seconds.append(s);self.activity.append(v);self.static.append(a.mean(axis=1))
    def result(self):
        self.consume(np.empty(0,np.int64),np.empty((0,3)),final=True)
        s=np.concatenate(self.seconds) if self.seconds else np.array([],np.int64)
        v=np.concatenate(self.activity) if self.activity else np.array([],float)
        assert np.all(np.diff(s)>0)
        a=np.concatenate(self.static,axis=0) if self.static else np.empty((0,3))
        return pd.DataFrame({"second":s,"activity":v,"sx":a[:,0],"sy":a[:,1],"sz":a[:,2]})


def qs(x):
    a=np.asarray(x,dtype=float)
    return np.quantile(a,[.05,.5,.95]).tolist() if len(a) else []
def synth():
    a=PoseSeconds()
    t=np.r_[np.arange(25)*STEP,np.arange(25)*STEP+2*NS]
    x=np.column_stack([np.cos(np.arange(50)*2*np.pi/25),np.sin(np.arange(50)*2*np.pi/25),np.ones(50)])
    a.consume(t[:31],x[:31]);a.consume(t[31:],x[31:])
    d=a.result()
    assert d.second.tolist()==[0,2] and np.allclose(d.activity,1)
    assert np.allclose(d[["sx","sy","sz"]].to_numpy(),[[0,0,1],[0,0,1]],atol=1e-12)
    assert a.gaps==1
def bouts(sec,valid,fly):
    # True runs split at any missing second, or at analysis mask boundary.
    k=np.flatnonzero(valid&fly)
    core=np.zeros(len(sec),bool)
    if not len(k):return core,[]
    splits=np.flatnonzero((np.diff(k)!=1)|(np.diff(sec[k])!=1))+1
    rr=np.split(k,splits);lengths=[len(a) for a in rr]
    for a in rr:
        if len(a)>180:core[a[30:-30]]=True
    return core,lengths
def summary(sec,valid,fly):
    core,L=bouts(sec,valid,fly)
    return {"known_seconds":int(valid.sum()),"candidate_flight_seconds":int((valid&fly).sum()),
        "candidate_fraction":float((valid&fly).sum()/valid.sum()) if valid.any() else None,
        "bout_count":len(L),"bout_duration_quantiles_s":qs(L),
        "bouts_over180s":sum(x>180 for x in L),"commuting_core_seconds":int(core.sum())},core
def gps_check(aid,sec,valid,fly,core):
    raw,_=original("gps");d=table(raw)
    d["id"]=v.idnorm(d[ID]);d["t"]=v.dt(d.timestamp)
    d=d.loc[d.id.eq(aid)&d.t.notna()&d.visible.str.lower().eq("true")&v.nightmask(d.t)].copy()
    for c in ("location-long","location-lat"):d[c]=pd.to_numeric(d[c],errors="coerce")
    d=d.loc[d["location-long"].between(-180,180)&d["location-lat"].between(-90,90)].copy()
    d["night"]=v.night(d.t)
    d=d.loc[~d.duplicated(["id","t"],keep=False)].sort_values("t")
    prev=d.groupby("night")[["t","location-long","location-lat"]].shift()
    dur=(d.t-prev.t).dt.total_seconds()
    speed=v.dist(prev["location-long"].to_numpy(),prev["location-lat"].to_numpy(),d["location-long"].to_numpy(),d["location-lat"].to_numpy())/dur
    midpoint=prev.t+(d.t-prev.t)/2
    k=dur.between(45,90)&speed.gt(0)&speed.le(30)&midpoint.notna()
    target=(midpoint[k].astype("int64").to_numpy()//NS)
    speed=speed[k].to_numpy();pos=np.searchsorted(sec,target)
    pp=np.clip(pos,0,len(sec)-1)
    ok=(pos<len(sec))&(sec[pp]==target)&valid[pp]
    mask={"candidate_flight":ok&fly[pp],"candidate_nonflight":ok&~fly[pp],"candidate_commuting_core":ok&core[pp]}
    return {"candidate_steps":len(target),"matched":int(ok.sum()),"states":{label:{"n":int(m.sum()),"ground_speed_quantiles_m_s":qs(speed[m]),"fraction_speed_ge3":float(np.mean(speed[m]>=3)) if m.any() else None} for label,m in mask.items()}}

def run():
    synth()
    uuid,n,md5=SPECS[7]
    raw,_=fetch("https://datarepository.movebank.org/server/api/core/bitstreams/"+uuid+"/content",n)
    assert len(raw)==n and hashlib.md5(raw).hexdigest()==md5
    assert hashlib.sha256(raw).hexdigest()=="bd6c90df8fd59a76da79aa654316c39c8dc36e553fe3268bd99f902bef68c53f"
    z=zipfile.ZipFile(io.BytesIO(raw));ms=[x for x in z.infolist() if x.filename.lower().endswith(".csv")]
    assert len(ms)==1 and ms[0].file_size<1_500_000_000
    a=PoseSeconds();ids=set()
    with z.open(ms[0]) as f:
        for d in pd.read_csv(f,usecols=["timestamp",ID]+AX,dtype={ID:str,**{c:float for c in AX}},chunksize=400000,encoding="utf-8-sig"):
            ids.update(v.idnorm(d[ID]).unique())
            t=pd.to_datetime(d.timestamp,format="mixed",utc=True,errors="raise").dt.as_unit("ns")
            a.consume(t.astype("int64").to_numpy(),d[AX].to_numpy())
    assert len(ids)==1
    aid=next(iter(ids));d=a.result()
    stat=d[["sx","sy","sz"]].to_numpy()
    norm=np.linalg.norm(stat,axis=1)
    low=d.activity.to_numpy()<=np.quantile(d.activity,.1)
    selected=norm[low];med=float(np.median(selected))
    gates={str(g):{"median_relative_error":abs(med/g-1),"fraction_within15percent":float(np.mean(abs(selected/g-1)<=.15))} for g in (1.,G)}
    admitted=[g for g in (1.,G) if gates[str(g)]["median_relative_error"]<=.1 and gates[str(g)]["fraction_within15percent"]>=.8]
    out={"scope":"source-scale and approximate 1s flight-rule sensitivity; not validated labels",
      "status":"UNIT_GATE_PASS" if len(admitted)==1 else "STOP_UNIT_GATE",
      "synthetic_test":"PASS","archive":7,"rows":a.n,"full_seconds":len(d),"gaps":a.gaps,
      "unit_audit":{"low_motion_seconds":int(low.sum()),"static_norm_raw_quantiles":qs(selected),
        "all_static_norm_raw_quantiles":qs(norm),"dynamic_proxy_raw_quantiles":qs(d.activity),"candidates":gates}}
    if len(admitted)!=1:return out
    scale=admitted[0]
    out["unit_audit"]["provisional_raw_units"]="g_like" if scale==1 else "SI_like"
    out["unit_audit"]["raw_to_g"]=1/scale
    m=stat/scale
    pitch=np.degrees(np.arctan2(m[:,0],np.hypot(m[:,1],m[:,2])))
    sec=d.second.to_numpy()
    mat=np.column_stack([m[:,1],pitch,d.activity.to_numpy()/scale,m[:,2]])
    smooth=np.empty_like(mat);smooth[:]=np.nan
    adjacent=np.r_[False,np.diff(sec)==1]
    smooth[1:]=(mat[1:]+mat[:-1])/2
    smooth[~adjacent]=np.nan
    known=np.isfinite(smooth).all(1)
    local=pd.Series(pd.to_datetime(sec,unit="s",utc=True))
    night=v.nightmask(local).to_numpy()
    masks={"all":known,"night_after_first":known&night}
    out["classification"]={}
    states={}
    for name,th in [("literal_SI",.5/G),("numeric_g",.5)]:
        fly=known&(smooth[:,0]>-th)&(smooth[:,1]>-30)&(smooth[:,2]>.3)&(smooth[:,3]>th)
        states[name]=fly
        p={}
        for label,mask in masks.items():
            p[label],core=summary(sec,mask,fly)
            if label=="night_after_first":p["gps_plausibility"]=gps_check(aid,sec,mask,fly,core)
        out["classification"][name]=p
    f=states["literal_SI"];h=states["numeric_g"]
    out["agreement"]={key:{"agreement":float(np.mean(f[k]==h[k])) if k.any() else None,
        "flight_jaccard":float((f&h&k).sum()/((f|h)&k).sum()) if ((f|h)&k).any() else None} for key,k in masks.items()}
    out["status"]="PILOT_CONVENTION_DIAGNOSTIC"
    return out
if __name__=="__main__":
    try:result=run()
    except Exception as e:result={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(result,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
