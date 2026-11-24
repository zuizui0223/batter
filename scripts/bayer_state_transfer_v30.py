"""V30 fixed candidate state rules, gap-aware prior-minute HR and commuting-core checks.
Aggregate outputs only; not direct-observation labels or calibrated energy."""
import concurrent.futures as cf,hashlib,io,json,pathlib,zipfile
import numpy as np
import pandas as pd
import bayer_acc_hr_transfer_v26 as v26
import bayer_flight_gate_v29 as v29
import bayer_wind_prediction_v22 as v22
from bayer_field_join_v17 import original,table,fetch
OUT=pathlib.Path("results/bayer_state_transfer_v30.json")
SHA={
1:"43256d7cf7ef7639b308c4643403c77ba48f5e95cf295658e393dd5b62405c48",
2:"e90a5f68d54c8073ea891d8559258157a3ea90c56dcb66af98d15b06a6621998",
3:"ef1f234a83d9fdc4a8c4632b044618683a0486f8e5666c415a5e84bdc1bba09e",
4:"d8262aa0e6da5f188aa8e00ab629bab854e128153b014552db3b71ddb736a7be",
5:"4cc0121e34d5e477102c251d960b26ac2f222840cf549d1fae7ff82b90da8753",
6:"02ab069442b24f8eeb7a2ca8d4e928aba8195cc050f01db8090a445a3f45606c",
7:"bd6c90df8fd59a76da79aa654316c39c8dc36e553fe3268bd99f902bef68c53f",
8:"8bfeae3e22f8d4fb65d05d22668aba49b74b8c172beb96c779652d906d1551b0",
9:"6d0e9e7eaa9078caedfebcf4ab09496b3fcfed0db081a036c78e92dcccaff1bb",
10:"7e46fdac2efaab1aed87b4d028cdb6b82c1019bcd8f88c5328d7187ce044a98f",
11:"f9e02fa6c78786d3ecd6ab1ab12355364a3f21b13c94699824d610d3efb06ec6",
12:"40dabf77402b9963766089faa398b4f34b471f6ed26017dbdfdbc52f7156261b"}
ID,TAG,AX=v26.ID,v26.TAG,v26.AX
NS=v26.NS;G=v29.G
CONVS=("literal_SI","numeric_g")
def same_run(sec,core,lo,hi):
    """All seconds overlapping [lo, hi) must be in one contiguous core."""
    i=np.searchsorted(sec,lo,side="left");j=np.searchsorted(sec,hi,side="left")
    if hi<=lo or i>=len(sec) or j<=i:return False
    return j-i==hi-lo and sec[i]==lo and sec[j-1]==hi-1 and bool(core[i:j].all())
def midpoint_labels(sec,known,fly,core,gps):
    t=gps.midpoint.astype("int64").to_numpy()//NS
    i=np.searchsorted(sec,t);k=np.minimum(i,len(sec)-1)
    ok=(i<len(sec))&(sec[k]==t)&known[k]
    ans={}
    for n,mask in [("flight",ok&fly[k]),("nonflight",ok&~fly[k]),("core",ok&core[k])]:
        z=gps.speed.to_numpy()[mask]
        ans[n]={"records":len(z),"speed_quantiles":v29.qs(z),"fraction_ge3":float((z>=3).mean()) if len(z) else None}
    return ans
def gps_steps_only(raw):
    v=v22.v
    g=raw.copy();g["id"]=v.idnorm(g[ID]);g["t"]=v.dt(g.timestamp)
    for c in ("location-long","location-lat"):g[c]=pd.to_numeric(g[c],errors="coerce")
    g=g.loc[g.visible.str.lower().eq("true")&g.t.notna()&v.nightmask(g.t)&g["location-long"].between(-180,180)&g["location-lat"].between(-90,90)].copy()
    g["night"]=v.night(g.t)
    g=g.loc[~g.duplicated(["id","t"],keep=False)].sort_values(["id","t"])
    p=g.groupby(["id","night"])[["t","location-long","location-lat"]].shift()
    g["duration"]=(g.t-p.t).dt.total_seconds()
    g["speed"]=v.dist(p["location-long"].to_numpy(),p["location-lat"].to_numpy(),g["location-long"].to_numpy(),g["location-lat"].to_numpy())/g.duration
    g["midpoint"]=p.t+(g.t-p.t)/2
    return g.loc[g.duration.between(45,90)&g.speed.gt(0)&g.speed.le(30),["id","t","midpoint","duration","speed"]]
def source_one(num,valid_ids,ref_keys,gps,steps):
    uuid,size,md5=v26.SPECS[num];o={"archive":num}
    try:
        raw,_=fetch(v26.BASE+uuid+"/content",size)
        assert len(raw)==size and hashlib.md5(raw).hexdigest()==md5 and hashlib.sha256(raw).hexdigest()==SHA[num]
        o["sha256"]=SHA[num]
        z=zipfile.ZipFile(io.BytesIO(raw));ms=[m for m in z.infolist() if m.filename.lower().endswith(".csv")]
        assert len(ms)==1 and sum(m.file_size for m in z.infolist())<3_500_000_000
        assert all(not m.filename.startswith(("/","\\")) and ".." not in pathlib.PurePosixPath(m.filename).parts for m in z.infolist())
        a=v29.PoseSeconds();ids=set();tags=set()
        with z.open(ms[0]) as f:
            for d in pd.read_csv(f,usecols=["timestamp",ID,TAG]+AX,dtype={ID:str,TAG:str,**{c:float for c in AX}},chunksize=400000,encoding="utf-8-sig"):
                ids.update(v22.v.idnorm(d[ID]).unique());tags.update(v22.v.idnorm(d[TAG]).unique())
                t=pd.to_datetime(d.timestamp,format="mixed",utc=True,errors="raise").dt.as_unit("ns")
                assert t.notna().all()
                a.consume(t.astype("int64").to_numpy(),d[AX].to_numpy())
        assert len(ids)==len(tags)==1
        aid,tag=next(iter(ids)),next(iter(tags))
        assert aid in valid_ids and (aid,tag) in ref_keys
        d=a.result();sec=d.second.to_numpy();stat=d[["sx","sy","sz"]].to_numpy();activity=d.activity.to_numpy()
        norm=np.linalg.norm(stat,axis=1);low=activity<=np.quantile(activity,.1);m=float(np.median(norm[low]))
        gates={str(g):{"median_relative_error":abs(m/g-1),"fraction_within15percent":float(np.mean(abs(norm[low]/g-1)<=.15))} for g in (1.,G)}
        passed=[g for g in (1.,G) if gates[str(g)]["median_relative_error"]<=.1 and gates[str(g)]["fraction_within15percent"]>=.8]
        o.update(rows=a.n,complete_seconds=len(d),gaps=a.gaps,low_motion_norm_quantiles=v29.qs(norm[low]),unit_gates=gates)
        if len(passed)!=1:o["status"]="STOP_UNIT_GATE";return o,None,None
        scale=passed[0];stat=stat/scale;activity=activity/scale
        pitch=np.degrees(np.arctan2(stat[:,0],np.hypot(stat[:,1],stat[:,2])))
        mat=np.column_stack([stat[:,1],pitch,activity,stat[:,2]])
        sm=np.full_like(mat,np.nan);sm[1:]=(mat[1:]+mat[:-1])/2
        adj=np.r_[False,np.diff(sec)==1];sm[~adj]=np.nan
        known=np.isfinite(sm).all(axis=1);night=v22.v.nightmask(pd.Series(pd.to_datetime(sec,unit="s",utc=True))).to_numpy()
        mask=known&night
        gg=gps[gps.id==aid];ss=steps[steps.id==aid].copy()
        frames=[];cores=[];states={};o["conventions"]={}
        for name,th in [("literal_SI",.5/G),("numeric_g",.5)]:
            fly=known&(sm[:,0]>-th)&(sm[:,1]>-30)&(sm[:,2]>.3)&(sm[:,3]>th)
            states[name]=fly
            q,core=v29.summary(sec,mask,fly)
            q["gps_midpoint_plausibility"]=midpoint_labels(sec,mask,fly,core,gg)
            # Full prior 60s of known state. Activity is unsmoothed and normalized.
            dd=pd.DataFrame({"minute":(sec[mask]//60+1)*60,"activity":activity[mask],"flight":fly[mask].astype(float)})
            mn=dd.groupby("minute",as_index=False).agg(activity=("activity","mean"),F=("flight","mean"),coverage=("flight","size"))
            mn=mn[mn.coverage==60].copy();mn["id"]=aid;mn["convention"]=name
            mn["hrt"]=pd.to_datetime(mn.minute,unit="s",utc=True).dt.as_unit("ns")
            frames.append(mn)
            # Whole GPS step AND prior HR minute in a single contiguous trimmed core.
            t=ss.t.astype("int64").to_numpy();hr=ss.hrt.astype("int64").to_numpy()
            start=t-np.rint(ss.duration.to_numpy()*NS).astype(np.int64)
            lo=np.minimum(start,hr-60*NS)//NS
            hi=(np.maximum(t,hr)+NS-1)//NS
            keep=np.array([same_run(sec,core,l,h) for l,h in zip(lo,hi)],dtype=bool)
            zz=ss.loc[keep,["id","hrt"]].copy();zz["convention"]=name
            cores.append(zz);q["whole_step_and_hr_minute_core_count"]=len(zz)
            o["conventions"][name]=q
        f,h=(states[c] for c in CONVS)
        o["night_state_agreement"]=float(np.mean(f[mask]==h[mask])) if mask.any() else None
        o["night_flight_jaccard"]=float((f&h&mask).sum()/((f|h)&mask).sum()) if ((f|h)&mask).any() else None
        o.update(status="PASS",provisional_raw_to_g=1/scale)
        return o,pd.concat(frames,ignore_index=True),pd.concat(cores,ignore_index=True)
    except Exception as e:
        o.update(status="STOP",error=repr(e));return o,None,None
def features(d,name,stage):
    if stage=="B":return v26.features(d,name,stage)
    x=v26.time_features(d);a=np.log1p(d.activity.to_numpy());f=d.F.to_numpy()
    lag=np.log(d.laghr.to_numpy()) if "laghr" in d else None
    extra={"B0":[],"A2":[a,a*a],"F":[f],"FA":[f,a,a*a],"FAI":[f,a,a*a,f*a],"L":[lag],"L+F":[lag,f],"L+FA":[lag,f,a,a*a]}[name]
    return np.column_stack([x]+extra)
def compare(d,field,models,stage):
    rows=[]
    for k in sorted(d[field].unique()):
        tr=d[d[field]!=k];te=d[d[field]==k]
        if len(tr)<20 or not len(te):continue
        o={}
        for name in models:
            x,z=features(tr,name,stage),features(te,name,stage)
            mu=x.mean(0);sd=x.std(0);sd[sd<1e-12]=1
            x=(x-mu)/sd;z=(z-mu)/sd
            y=np.log(tr.bpm.to_numpy());beta=np.linalg.solve(x.T@x+np.eye(x.shape[1]),x.T@(y-y.mean()))
            pred=y.mean()+z@beta;obs=te.bpm.to_numpy()
            o[name]={"mae":float(np.mean(abs(np.exp(pred)-obs))),"log_rmse":float(np.sqrt(np.mean((pred-np.log(obs))**2)))}
        rows.append(o)
    if len(rows)<2:return {"status":"STOP_FEWER_THAN_TWO_FOLDS","folds":len(rows)}
    return {"folds":len(rows),"mean":{m:{q:float(np.mean([r[m][q] for r in rows])) for q in ("mae","log_rmse")} for m in models},
      "fold_wins":{m:{b:sum(r[m]["mae"]<r[b]["mae"] for r in rows) for b in models if b!=m} for m in models}}
def panel(d,models,stage,small=False):
    counts=d.id.value_counts();o={"records":len(d),"bats":int(d.id.nunique()),"nights":int(d.night.nunique()),"bat_nights":len(d[["id","night"]].drop_duplicates()),"records_per_bat":sorted(int(x) for x in counts)}
    eligible=len(d)>=(50 if small else 500) and o["bats"]>=5 and o["nights"]>=3 and (counts>=(5 if small else 30)).sum()>=3
    if eligible:o.update(status="BLOCKED_COMPARISON",leave_bat_out=compare(d,"id",models,stage),leave_night_out=compare(d,"night",models,stage))
    else:o["status"]="STOP_LOW_SUPPORT"
    return o
def test():
    v29.synth()
    sec=np.r_[np.arange(10),np.arange(11,20)];core=np.ones(len(sec),bool)
    assert same_run(sec,core,2,9) and not same_run(sec,core,2,12)
    core[5]=False;assert not same_run(sec,core,2,9)
def main():
    test()
    h=table(original("hr")[0]);g=table(original("gps")[0]);r=table(original("ref")[0])
    norm=v22.v.idnorm;ids=set(norm(h[ID]))&set(norm(g[ID]));ref=set(zip(norm(r["animal-id"]),norm(r["tag-id"])))
    assert len(ids)==12
    gps=gps_steps_only(g);steps,selection=v22.make_steps()
    assert len(steps)==349
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        fs=[ex.submit(source_one,i,ids,ref,gps,steps) for i in SHA];receipts=[];minutes=[];cores=[]
        for f in cf.as_completed(fs):
            o,m,c=f.result();receipts.append(o)
            print(json.dumps({"archive":o["archive"],"status":o["status"],"rows":o.get("rows"),"error":o.get("error")}),flush=True)
            if m is not None:minutes.append(m);cores.append(c)
    report={"scope":"candidate-state conditional transfer; approximate 1s Fig S2 rule; no direct observation labels","files":sorted(receipts,key=lambda x:x["archive"]),"selection":selection,"test":"PASS"}
    if not minutes:report["status"]="STOP_NO_ADMITTED_FILES";return report
    a=pd.concat(minutes,ignore_index=True);c=pd.concat(cores,ignore_index=True)
    assert not a.duplicated(["id","hrt","convention"]).any() and not c.duplicated(["id","hrt","convention"]).any()
    report["status"]="FULL_COHORT" if len(minutes)==12 and a.id.nunique()==12 else "PARTIAL_COHORT"
    hr=v26.hr_rows(h);d=hr.merge(a,on=["id","hrt"],validate="one_to_many")
    w,wr=v22.era5()
    steps=pd.merge_asof(steps.sort_values("midpoint"),w.sort_values("t").rename(columns={"t":"weather_time"}),left_on="midpoint",right_on="weather_time",direction="nearest",tolerance=pd.Timedelta(minutes=30))
    assert steps.weather_time.notna().all()
    th=np.deg2rad(steps.wind_direction_10m.to_numpy());wind=steps.wind_speed_10m.to_numpy()
    steps["airspeed"]=np.hypot(steps.speed*np.sin(steps.bearing)+wind*np.sin(th),steps.speed*np.cos(steps.bearing)+wind*np.cos(th))
    report["weather_receipt"]=wr;report["results"]={};gates={}
    for conv in CONVS:
        x=d[d.convention==conv];o={}
        o["all_minutes"]=panel(x,["B0","A2","F","FA","FAI"],"A")
        for n,z in [("pure_flight",x[x.F==1]),("pure_nonflight",x[x.F==0])]:
            o[n]=panel(z,["B0","A2"],"A",True)
        o["mixed_minutes"]=int(x.F.between(0,1,inclusive="neither").sum())
        mm=x[x.F.isin([0.,1.])].groupby(["id","F"]).bpm.median().unstack()
        dif=(mm[1.]-mm[0.]).dropna() if 1. in mm and 0. in mm else pd.Series(dtype=float)
        o["paired_bat_median_HR_difference_flight_minus_nonflight"]={"bats":len(dif),"quantiles_bpm":v29.qs(dif),"positive":int((dif>0).sum())}
        o["lag_support"]=panel(x[x.laghr.notna()],["L","L+F","L+FA"],"A")
        core=c[c.convention==conv][["id","hrt"]]
        z=steps.merge(core,on=["id","hrt"],validate="one_to_one").merge(a[a.convention==conv][["id","hrt","activity","F"]],on=["id","hrt"],validate="one_to_one")
        o["commuting_core"]=panel(z,["B0","G","A2","G+A2","W","W+A2"],"B",True)
        q=o["all_minutes"];gates[conv]=q["status"]=="BLOCKED_COMPARISON" and all(q[t].get("mean",{}).get("FA",{}).get("mae",float("inf"))<q[t].get("mean",{}).get("A2",{}).get("mae",-float("inf")) and q[t].get("mean",{}).get("F",{}).get("mae",float("inf"))<q[t].get("mean",{}).get("B0",{}).get("mae",-float("inf")) for t in ("leave_bat_out","leave_night_out"))
        report["results"][conv]=o
    report["state_gate"]=gates;report["full_state_gate"]=all(gates.values()) and report["status"]=="FULL_COHORT"
    return report
if __name__=="__main__":
    try:r=main()
    except Exception as e:r={"status":"STOP","error":repr(e)}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
    if r["status"].startswith("STOP"):raise SystemExit(2)
