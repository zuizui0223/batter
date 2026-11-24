"""V26. Gap-aware raw-scale activity proxy and blocked HR transfer.
No flight labels, physical calibration, or raw individual records exported.
Public noncommercial research: Bayer et al. DOI 10.1242/jeb.251521;
Movebank DOI 10.5441/001/1.754 (CC BY-NC).
"""
import argparse, concurrent.futures as cf, hashlib, io, json, pathlib, re, zipfile
import numpy as np
import pandas as pd
from bayer_field_join_v17 import original,table,fetch
import bayer_wind_prediction_v22 as v22

BASE="https://datarepository.movebank.org/server/api/core/bitstreams/"
SPECS={
1:("dc743782-a173-475a-a28d-9a104650736b",142739341,"3ccea2e9a1f877f6ce360a834a7c874c"),
2:("fd9a0ce0-00e3-46e9-b565-1075323d13a7",126703275,"e6db0fa42ad8b4a80a604290ca45a8b2"),
3:("653cf35b-3d7c-48f9-9966-a6bb83b1b174",134180586,"53b5b7ce4969edbd10ab709fef58d078"),
4:("92d6cb8b-4a05-4754-9c28-8af39cf7f6b6",143843133,"1ec76d873117bf3f1e48087598e75de3"),
5:("1b2ec7c0-7473-40b4-ad1a-8ca2f29263f8",119740510,"1d0230c31d88285ce8a15fd574822163"),
6:("ea498bee-d31c-4eb0-adbd-9f2ec32e8084",135232477,"c7f84477e36a3f412565f85d439dc5d6"),
7:("d35bb3ba-59fd-4d09-ac56-ac59c2ea6eff",55465865,"1549392b1c51da65acce2d960efcfd6c"),
8:("0cc6ed52-ecee-4528-9a1d-a0eff847a6c0",155535322,"ec5cd5e64fffa2e4db89558fc340e010"),
9:("255ab296-cb5c-4fee-8022-bd3c5bf4665d",127179991,"4f066979727e940387602a2dcf68cf1e"),
10:("5e7add3d-77ce-4103-9a8b-f762dc79eeb9",89600907,"1bc060314fb83c2570214b09f233c69a"),
11:("a82fc3c7-bae8-4091-adbf-239681ca49f7",76388807,"7666bef64904cf1204d86de954fc42bc"),
12:("b204beb8-dc57-4679-9999-975b06cd0a45",139149294,"e8b938c00074c1d21dc54b18ad523734")}
AX=["acceleration-raw-x","acceleration-raw-y","acceleration-raw-z"]
ID="individual-local-identifier";TAG="tag-local-identifier"
NS=1_000_000_000; STEP=40_000_000

class Seconds:
    """Retain the final partial second across read chunks; no interpolation."""
    def __init__(self):
        self.tail_t=np.empty(0,dtype=np.int64)
        self.tail_x=np.empty((0,3))
        self.last=None; self.seconds=[];self.activity=[]
        self.n=0;self.gaps=0;self.partial=0;self.bad_values=0
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
        self.seconds.append(s);self.activity.append(v)
    def result(self):
        self.consume(np.empty(0,np.int64),np.empty((0,3)),final=True)
        s=np.concatenate(self.seconds) if self.seconds else np.array([],np.int64)
        v=np.concatenate(self.activity) if self.activity else np.array([],float)
        assert np.all(np.diff(s)>0)
        return pd.DataFrame({"second":s,"activity":v})

def test():
    s=np.r_[np.arange(25)*STEP,np.arange(25)*STEP+2*NS]
    # Exact alternating +/-1 not zero mean with 25: use sinusoid and analytical calculation.
    x=np.column_stack([np.cos(np.arange(50)*2*np.pi/25),np.sin(np.arange(50)*2*np.pi/25),np.ones(50)*7])
    a=Seconds();a.consume(s[:13],x[:13]);a.consume(s[13:37],x[13:37]);a.consume(s[37:],x[37:])
    z=a.result()
    assert z.second.tolist()==[0,2] and np.allclose(z.activity,1)
    assert a.gaps==1 and a.n==50
    # full and incomplete minute; require no gap bridging for 2s smooth
    d=pd.DataFrame({"second":np.r_[np.arange(60),np.arange(60,114)],"activity":1.})
    m=minutes(d)
    assert m.coverage.tolist()==[60,54] and np.allclose(m.activity,1)
    assert m.coverage2.tolist()==[59,54]
    return "PASS"

def minutes(d):
    d=d.copy()
    # Trailing 2s mean valid only on two adjacent complete seconds.
    d["smooth2"]=((d.activity+d.activity.shift())/2).where(d.second.diff().eq(1))
    d["minute"]=(d.second//60+1)*60
    return d.groupby("minute",as_index=False).agg(activity=("activity","mean"),coverage=("activity","size"),
        activity2=("smooth2","mean"),coverage2=("smooth2","count"))

def one(num,valid_ids,ref_keys):
    uuid,size,md5=SPECS[num];receipt={"archive":num,"bytes_expected":size,"expected_md5":md5}
    try:
        raw,_=fetch(BASE+uuid+"/content",size)
        assert len(raw)==size and hashlib.md5(raw).hexdigest()==md5
        receipt["sha256"]=hashlib.sha256(raw).hexdigest()
        if num==7:assert receipt["sha256"]=="bd6c90df8fd59a76da79aa654316c39c8dc36e553fe3268bd99f902bef68c53f"
        z=zipfile.ZipFile(io.BytesIO(raw));members=z.infolist()
        assert all(not q.filename.startswith(("/","\\")) and ".." not in pathlib.PurePosixPath(q.filename).parts for q in members)
        assert sum(q.file_size for q in members)<3_500_000_000
        ms=[q for q in members if q.filename.lower().endswith(".csv")];assert len(ms)==1
        a=Seconds();ids=set();tags=set()
        with z.open(ms[0]) as f:
            for d in pd.read_csv(f,usecols=["timestamp",ID,TAG]+AX,dtype={ID:str,TAG:str,**{c:float for c in AX}},chunksize=400_000,encoding="utf-8-sig"):
                ids.update(d[ID].astype(str).str.strip().str.casefold().unique())
                tags.update(d[TAG].astype(str).str.strip().str.casefold().unique())
                t=pd.to_datetime(d.timestamp,format="mixed",utc=True,errors="raise").dt.as_unit("ns")
                assert t.notna().all()
                a.consume(t.astype("int64").to_numpy(),d[AX].to_numpy())
        assert len(ids)==len(tags)==1
        aid,tag=next(iter(ids)),next(iter(tags))
        assert aid in valid_ids and (aid,tag) in ref_keys
        sec=a.result();m=minutes(sec);m["id"]=aid
        m["hrt"]=pd.to_datetime(m.minute,unit="s",utc=True).dt.as_unit("ns")
        receipt.update(status="PASS",rows=a.n,gaps=a.gaps,complete_seconds=len(sec),partial_seconds=a.partial,
            invalid_complete_windows=a.bad_values,minutes60=int(m.coverage.eq(60).sum()),
            minutes54=int(m.coverage.ge(54).sum()),minutes2_full=int(m.coverage2.eq(60).sum()))
        return receipt,m
    except Exception as e:
        receipt.update(status="STOP",error=repr(e));return receipt,None

def time_features(d):
    h=d.hour.to_numpy()*2*np.pi/24
    return np.column_stack([np.sin(h),np.cos(h)])
def features(d,name,stage):
    x=time_features(d)
    if stage=="B":x=np.column_stack([x,np.log(d.duration.to_numpy())])
    a=np.log1p(d.activity.to_numpy());lag=np.log(d.laghr.to_numpy()) if "laghr" in d else None
    if stage=="B":
        g=np.log1p(d.speed.to_numpy());w=np.log1p(d.airspeed.to_numpy())
        more={"B0":[],"G":[g,g*g],"A2":[a,a*a],"G+A2":[g,g*g,a,a*a],"W":[w,w*w],"W+A2":[w,w*w,a,a*a]}[name]
    else:more={"B0":[],"A1":[a],"A2":[a,a*a],"L":[lag],"L+A2":[lag,a,a*a]}[name]
    return np.column_stack([x]+more)

def compare(d,field,names,stage):
    rows=[]
    for k in sorted(d[field].unique()):
        tr=d[d[field]!=k];te=d[d[field]==k]
        if len(tr)<20 or not len(te):continue
        out={}
        for name in names:
            x,z=features(tr,name,stage),features(te,name,stage)
            mu=x.mean(0);sd=x.std(0);sd[sd<1e-12]=1
            x=(x-mu)/sd;z=(z-mu)/sd
            y=np.log(tr.bpm.to_numpy())
            b=np.linalg.solve(x.T@x+np.eye(x.shape[1]),x.T@(y-y.mean()))
            pred=y.mean()+z@b;obs=te.bpm.to_numpy()
            out[name]={"mae":float(np.mean(abs(np.exp(pred)-obs))),"log_rmse":float(np.sqrt(np.mean((pred-np.log(obs))**2)))}
        rows.append(out)
    if len(rows)<2:return {"status":"STOP_FEWER_THAN_TWO_FOLDS","folds":len(rows)}
    base=names[0]
    return {"folds":len(rows),"mean":{m:{q:float(np.mean([r[m][q] for r in rows])) for q in ("mae","log_rmse")} for m in names},
      "wins_vs_baseline":{m:sum(r[m]["mae"]<r[base]["mae"] for r in rows) for m in names[1:]}}

def panel(d,stage,names,pilot=False):
    counts=d.id.value_counts()
    o={"records":len(d),"bats":int(d.id.nunique()),"nights":int(d.night.nunique()),
       "bat_nights":len(d[["id","night"]].drop_duplicates()),"records_per_bat":sorted(int(v) for v in counts)}
    eligible=(len(d)>=500 and o["bats"]>=5 and o["nights"]>=3 and (counts>=30).sum()>=3) if stage=="A" else (len(d)>=50 and o["bats"]>=5 and o["nights"]>=3 and (counts>=5).sum()>=3)
    if eligible:
        o["status"]="BLOCKED_COMPARISON";o["leave_bat_out"]=compare(d,"id",names,stage);o["leave_night_out"]=compare(d,"night",names,stage)
    else:o["status"]="PILOT_NO_COHORT_INFERENCE" if pilot else "STOP_LOW_SUPPORT"
    return o

def hr_rows(h):
    h=h.copy();h["id"]=v22.v.idnorm(h[ID]);h["hrt"]=v22.v.dt(h.timestamp)
    h["bpm"]=pd.to_numeric(h["heartrate:heart-rate"],errors="coerce")
    h["qi"]=pd.to_numeric(h["tag-tech-spec"],errors="coerce")
    h=h.loc[h.hrt.notna()&~h.duplicated(["id","hrt"],keep=False)&h.qi.isin([0,1])&h.bpm.between(100,900)].copy()
    h=h.loc[v22.v.nightmask(h.hrt)&h.hrt.dt.second.eq(0)&h.hrt.dt.microsecond.eq(0)].copy()
    local=h.hrt-pd.Timedelta(hours=5);h["hour"]=local.dt.hour+local.dt.minute/60
    h["night"]=v22.v.night(h.hrt)
    lag=h[["id","hrt","night","bpm"]].rename(columns={"bpm":"laghr"})
    lag.hrt=lag.hrt+pd.Timedelta(seconds=60)
    return h.merge(lag,on=["id","hrt","night"],how="left",validate="one_to_one")[["id","hrt","bpm","qi","hour","night","laghr"]]

def run(pilot):
    report={"scope":"gap-aware raw-unit dynamic activity proxy; conditional HR prediction, not flight or energy labels","test":test(),"pilot":pilot,"files":[]}
    h=table(original("hr")[0]);g=table(original("gps")[0]);r=table(original("ref")[0])
    norm=lambda s:s.astype(str).str.strip().str.casefold()
    ids=set(norm(h[ID]))&set(norm(g[ID]));ref_keys=set(zip(norm(r["animal-id"]),norm(r["tag-id"])))
    assert len(ids)==12
    report["reference_audit"]={"tag_models":sorted(r["tag-model"].unique().tolist()),"raw_unit_status":"UNDEFINED_IN_GENERIC_README",
       "note":"No cross-tag calibration or physical unit inferred from raw numeric distribution."}
    # Report whether actual source metadata mentions acceleration scale; no identifiers/comments dumped.
    unit_pattern=r"(?i)(?:acceleration|\bACC\b).{0,60}(?:units?|\bmg\b|m/s|\bg\b|bit|scale)"
    report["reference_audit"]["rows_with_possible_scale_documentation"]=int(r["tag-settings"].str.contains(unit_pattern,regex=True).sum())
    nums=[7] if pilot else list(SPECS)
    frames=[]
    with cf.ThreadPoolExecutor(max_workers=1 if pilot else 3) as ex:
        fs={ex.submit(one,i,ids,ref_keys):i for i in nums}
        for f in cf.as_completed(fs):
            o,m=f.result();report["files"].append(o)
            print(json.dumps({"archive":o["archive"],"status":o["status"],"rows":o.get("rows"),"minutes60":o.get("minutes60"),"error":o.get("error")}),flush=True)
            if m is not None:frames.append(m)
    report["files"].sort(key=lambda q:q["archive"])
    if not frames:report["status"]="STOP_NO_ADMITTED_FILES";return report
    a=pd.concat(frames,ignore_index=True)
    assert not a.duplicated(["id","hrt"]).any()
    h=hr_rows(h);d=h.merge(a,on=["id","hrt"],how="inner",validate="one_to_one")
    report["status"]="PILOT_COMPLETE" if pilot else ("FULL_COHORT" if len(frames)==12 and a.id.nunique()==12 else "PARTIAL_COHORT")
    report["unit_boundary"]="Raw-scale proxy only, not calibrated VeDBA or classified flight."
    report["stage_A"]={}
    for name,z in [("complete60",d[d.coverage.eq(60)]),("atleast54",d[d.coverage.ge(54)])]:
        report["stage_A"][name]=panel(z,"A",["B0","A1","A2"],pilot)
    z=d.loc[d.coverage.eq(60)&d.coverage2.eq(60)].copy()
    z["activity"]=z.activity2
    report["stage_A"]["complete60_trailing2s"]=panel(z,"A",["B0","A1","A2"],pilot)
    z=d.loc[d.coverage.eq(60)&d.laghr.notna()].copy()
    report["stage_A"]["prior_hr"]=panel(z,"A",["L","L+A2"],pilot)
    steps,sel=v22.make_steps();w,wr=v22.era5()
    steps=pd.merge_asof(steps.sort_values("midpoint"),w.sort_values("t").rename(columns={"t":"weather_time"}),left_on="midpoint",right_on="weather_time",direction="nearest",tolerance=pd.Timedelta(minutes=30))
    assert steps.weather_time.notna().all()
    th=np.deg2rad(steps.wind_direction_10m.to_numpy());wind=steps.wind_speed_10m.to_numpy()
    steps["airspeed"]=np.hypot(steps.speed*np.sin(steps.bearing)+wind*np.sin(th),steps.speed*np.cos(steps.bearing)+wind*np.cos(th))
    z=steps.merge(a[["id","hrt","activity","coverage"]],on=["id","hrt"],how="inner",validate="one_to_one")
    z=z[z.coverage.eq(60)].copy()
    report["stage_B"]={"all":panel(z,"B",["B0","G","A2","G+A2","W","W+A2"],pilot),
                       "speed_ge3_sensitivity":panel(z[z.speed>=3],"B",["B0","G","A2","G+A2","W","W+A2"],pilot)}
    report["weather_receipt"]=wr
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--pilot",action="store_true");args=parser.parse_args()
    try:report=run(args.pilot)
    except Exception as e:report={"status":"STOP","error":repr(e)}
    p=pathlib.Path("results/bayer_acc_hr_v26"+("_pilot" if args.pilot else "")+".json");p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n");print(p.read_text())
    if report["status"].startswith("STOP"):raise SystemExit(2)
