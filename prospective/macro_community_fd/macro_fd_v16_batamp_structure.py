"""V16: coarse-grid observed wing FD relative to monitored species pool."""
import collections as C, hashlib, json, math
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer
from macro_fd_v15_batamp_admission import ROOT,PIN,FILES,verify,numbers,dictionary
from macro_fd_v4_global_ranges import read_ranges,wing,metric
from macro_fd_v5_structure import edges,check_overlap,climate,gedi

OUT=Path("macro_fd_v16_result.json")
ENV_HASH={"rh-98-a0":"72ade8803e3b80aad3316633a3a61ea1bb2c745e8166932776e5e89da0b6b413","cover-a0":"48d852d46634b917fbc0a2544ed604b70ff7fa2a5d8585597c6c58cdb196d13b","pai-a0":"39a3ddf5dd8fca5324c68a6b916a3020eb39a9d7da15962e554479a938c4acab","pavd-bot-frac":"644b9b2c62d3b59c5d6929ce7a71fee537b3c94e6f89b883eff13b847000a2b6"}
CLIM_HASH="00513224583665ec0f2f955a4ec252730c4deb2004cce9e793492a3f26df4dcf"
YNAME=["wing_MPD_excess_monitored_pool","wing_MPD_detected","size_MPD_excess_monitored_pool"]
FEATURES=["log_monitored_matched","log_detected_matched","trait_coverage","mean_reported_nights","sd_reported_nights","log1p_mic_height","nabat","activity","month_sin","month_cos","year","abs_lat","bio1","bio4","bio5","bio6","bio12","bio15","log1p_RH98","cover","log1p_PAI","climate_area_support","GEDI_area_support","monitored_wing_MPD","log1p_range_richness","log1p_range_wing_richness","bottom_half_PAVD_fraction"]
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V16_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def mpd(D,indices):
    n=len(indices);assert n>=2
    return D[np.ix_(indices,indices)].sum((0,1))/(n*(n-1))
def keyfold(keys):
    u=sorted(set(keys),key=lambda x:hashlib.sha256(repr(x).encode()).hexdigest())
    m={k:i%5 for i,k in enumerate(u)}
    return np.array([m[k] for k in keys])
def blocks(t,g):
    return [(int(r)//g,int(c)//g) for r,c in zip(t.row,t.col)]
def support(t):
    return {"units":len(t),"sites":int(t.siteId.nunique()),"native_cells":int(t.cell.nunique()),"blocks2":len(set(blocks(t,2))),"dataset_strings":int(t.dataset.nunique()),"distinct_source_dataset_strings":len(set(zip(t.source,t.dataset)))}
def admitted(c):
    return c["units"]>=100 and c["sites"]>=60 and c["native_cells"]>=20 and c["blocks2"]>=15 and c["dataset_strings"]>=10
def getweights(t,b,mask):
    w=np.zeros(len(t));group=C.defaultdict(lambda:C.defaultdict(lambda:C.defaultdict(list)))
    for i in np.flatnonzero(mask):
        group[b[i]][int(t.cell.iloc[i])][int(t.siteId.iloc[i])].append(i)
    for cells in group.values():
        for sites in cells.values():
            for v in sites.values():w[v]=1/(len(group)*len(cells)*len(sites)*len(v))
    assert abs(w.sum()-1)<1e-10
    return w
def fit(t,b,X,Y,tr,te):
    w=getweights(t,b,tr)[tr];a=X[tr];y=Y[tr]
    mu=w@a;sd=np.sqrt(w@((a-mu)**2));active=sd>1e-12;sd[~active]=1.
    z=(a-mu)/sd;zt=(X[te]-mu)/sd;z[:,~active]=0;zt[:,~active]=0
    ym=w@y;pred=[np.repeat(ym[None,:],te.sum(),axis=0)]
    for n in (X.shape[1]-1,X.shape[1]):
        u=z[:,:n];v=zt[:,:n];coef=np.linalg.solve(u.T@(w[:,None]*u)+.1*np.eye(n),u.T@(w[:,None]*(y-ym)))
        assert np.max(abs(u.T@(w[:,None]*(u@coef-(y-ym)))+.1*coef))<1e-8
        pred.append(ym+v@coef)
    return np.stack([(a-Y[te])**2 for a in pred],axis=1)
def score(t,X,Y,g,strict=False):
    b=blocks(t,g);src=list(zip(t.source,t.dataset))
    bf=keyfold(b);sf=keyfold(src)
    keys=list(itertools.product(range(5),repeat=2)) if strict else [(i,None) for i in range(5)]
    sc=np.full((len(t),3,Y.shape[1]),np.nan);folds=[]
    for i,j in keys:
        te=(bf==i)&(sf==j) if strict else bf==i
        tr=(bf!=i)&(sf!=j) if strict else bf!=i
        tb=len({b[k] for k in np.flatnonzero(te)});ts=int(t.loc[te,"siteId"].nunique());rs=int(t.loc[tr,"siteId"].nunique())
        if tb<2 or ts<2 or rs<30:continue
        assert not {b[k] for k in np.flatnonzero(tr)}&{b[k] for k in np.flatnonzero(te)}
        if strict:assert not {src[k] for k in np.flatnonzero(tr)}&{src[k] for k in np.flatnonzero(te)}
        sc[te]=fit(t,b,X,Y,tr,te)
        w=getweights(t,b,te)[te];a=np.einsum("i,imk->mk",w,sc[te])
        folds.append({"fold":[i,j],"units":int(te.sum()),"test_blocks":tb,"test_sites":ts,"training_sites":rs,"V_B":(a[1]-a[2]).tolist(),"V_N":(a[0]-a[2]).tolist()})
    ok=np.isfinite(sc).all((1,2));status=len(folds)>=(10 if strict else 5) and ok.mean()>=(.7 if strict else 1.) and len({b[i] for i in np.flatnonzero(ok)})>=10
    o={"status":"scored" if status else "insufficient_fold_support","grain":g,"strict":strict,"scored_units":int(ok.sum()),"scored_fraction":float(ok.mean()),"folds":folds}
    if not status:return o
    w=getweights(t,b,ok);mean=np.einsum("i,imk->mk",w[ok],sc[ok]);by=C.defaultdict(list)
    for i in np.flatnonzero(ok):by[b[i]].append(i)
    bw=np.array([w[v].sum() for v in by.values()])
    bd=np.array([np.einsum("i,ik->k",w[v]/w[v].sum(),sc[v,1]-sc[v,2]) for v in by.values()])
    gain=bw@bd;assert np.allclose(gain,mean[1]-mean[2])
    om=(gain-bw[:,None]*bd)/(1-bw[:,None])
    o.update(MSE=dict(zip(["N","B","V"],mean.tolist())),V_B=gain.tolist(),V_N=(mean[0]-mean[2]).tolist(),blocks=len(by),positive_blocks=(bd>0).sum(0).tolist(),positive_folds=sum(f["V_B"][0]>0 for f in folds),delete_one_block_range=[om.min(0).tolist(),om.max(0).tolist()])
    o["primary_pass"]=bool(gain[0]>0 and (mean[0]-mean[2])[0]>0 and o["positive_blocks"][0]/o["blocks"]>=.6 and o["positive_folds"]/len(folds)>=.8 and om[:,0].min()>0)
    return o
import itertools
def main():
    o={"stage":"coarse-grid BatAMP monitored-pool wing FD and measured vegetation","status":"START","source_commit":PIN,"response_order":YNAME,"feature_order":FEATURES,"limits":["no true occupancy, altitude-specific use or actual competitive partitioning","published monthly aggregates and source-imputed zeros","coarse vegetation association, 15km guard not coordinate calibration","no raw locations or identifiers exported","not independent of all prior US sources"]}
    try:
        o["batamp_files"]={k:verify(ROOT,PIN,k,v) for k,v in FILES.items()}
        for k in ("ui/src/config.js","analysis/README.md","analysis/merge.py"):o["batamp_files"][k]=verify(ROOT,PIN,k)
        spec=dictionary((ROOT/"ui/src/config.js").read_text())
        d=pd.read_feather(ROOT/"ui/static/data/detectors.feather")
        s=pd.read_feather(ROOT/"ui/static/data/spp_detections.feather")
        numbers(d,["id","siteId","micHt","lat","lon"])
        numbers(s,["detId","year","month","species","detections","detectionNights","detectorNights"])
        assert len(d)==9485 and len(s)==262107 and d.id.is_unique and s.detId.isin(d.id).all() and not s.duplicated(["detId","year","month","species"]).any() and s.detections.sum()==6982180
        assert (s.detectionNights<=s.detectorNights).all() and ((s.detections>0)==(s.detectionNights>0)).all()
        s["name"]=s.species.map(spec);assert s.name.notna().all()
        names,R,shape,crs,T=read_ranges(o);w=wing(o)
        ids=[i for i,k in enumerate(names) if k in w.index];nm=[names[i] for i in ids];assert len(nm)==264
        _,D=metric(w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float))
        pos={k:i for i,k in enumerate(nm)};total=R.sum(0);wr=R[ids].sum(0)
        for k in ("source","countType","dataset"):d[k]=d[k].astype(object).fillna("").astype(str).str.strip()
        good=d.lon.between(-170,-50)&d.lat.between(15,51.6)&np.isfinite(d.micHt)&d.micHt.gt(0)&d.siteId.notna()&d.source.isin(["batamp","nabat"])&d.countType.isin(["a","p"])&d.dataset.ne("")
        d=d.loc[good,["id","siteId","micHt","lat","lon","source","countType","dataset"]].copy()
        tr=Transformer.from_crs(4326,crs,always_xy=True);rev=Transformer.from_crs(crs,4326,always_xy=True)
        x,y=tr.transform(d.lon.to_numpy(),d.lat.to_numpy());col,row=(~T)*(x,y)
        d["col"]=np.floor(col).astype(int);d["row"]=np.floor(row).astype(int)
        interior=(np.minimum(col%1,1-col%1)*T.a>=15000)&(np.minimum(row%1,1-row%1)*abs(T.e)>=15000)
        _,a=rev.transform(np.zeros(len(d)),T.f+d.row.to_numpy()*T.e);_,b=rev.transform(np.zeros(len(d)),T.f+(d.row.to_numpy()+1)*T.e)
        grid=d.row.between(0,shape[0]-1)&d.col.between(0,shape[1]-1)&(np.maximum(a,b)<=51.6)&(np.minimum(a,b)>=-51.6)
        o["detector_support"]={"regional_positive_height_nonempty_source":len(d),"grid_interior_and_GEDI_latitude":int((interior&grid).sum())}
        d=d.loc[interior&grid].copy();d["cell"]=d.row*shape[1]+d.col
        keep=s.name.str.fullmatch(r"[a-z]+_[a-z-]+")&s.year.between(2019,2022)&s.month.between(5,9)&s.detectorNights.ge(5)
        s=s.loc[keep,["detId","year","month","name","detectorNights","detectionNights"]].merge(d,left_on="detId",right_on="id",validate="many_to_one")
        counts=C.Counter();records=[]
        for _,g in s.groupby(["detId","year","month"],observed=True,sort=False):
            counts["all_detector_months"]+=1;assert g.name.is_unique
            m=g[g.name.isin(pos)];n=len(m);cov=n/len(g)
            if n<5 or cov<.5:continue
            counts["monitored_trait_gate"]+=1
            det=m[m.detectionNights>0]
            if len(det)<3:continue
            counts["detected_gate"]+=1
            m0=[pos[k] for k in m.name];d0=[pos[k] for k in det.name]
            expect=mpd(D,m0);raw=mpd(D,d0)
            r=g.iloc[0][["detId","siteId","row","col","cell","lat","micHt","year","month","source","countType","dataset"]].to_dict()
            r.update(n=n,k=len(det),cov=cov,nights=float(m.detectorNights.mean()),night_sd=float(m.detectorNights.std(ddof=0)),sum_nights=int(m.detectorNights.sum()),expected=float(expect[1]),Y0=float(raw[1]-expect[1]),Y1=float(raw[1]),Y2=float(raw[2]-expect[2]))
            records.append(r)
        o["unit_attrition"]=dict(counts)
        if not records:o["status"]="OBSERVATION_SUPPORT_STOP";save(o);return
        t=pd.DataFrame(records).sort_values(["n","sum_nights","detId"],ascending=[False,False,True]).drop_duplicates(["siteId","source","countType","year","month"]).reset_index(drop=True)
        o["pre_environment"]=support(t);o["status"]="OBSERVATION_SUPPORT_COMPLETE";save(o)
        if not admitted(o["pre_environment"]):o["status"]="OBSERVATION_SUPPORT_STOP";save(o);return
        check_overlap();tx,ty=edges(T,shape)
        o["status"]="CLIMATE_ACQUISITION";save(o)
        clim,cc=climate(o,tx,ty);assert o["climate"]["sha256"]==CLIM_HASH
        o["status"]="GEDI_ACQUISITION";save(o)
        veg,vc=gedi(o,tx,ty)
        assert {k:v["sha256"] for k,v in o["GEDI"]["metrics"].items()}==ENV_HASH
        cell=t.cell.to_numpy(int)
        ok=(cc[cell]>=.5)&(vc[cell]>=.5)&(veg[cell,0]>5)&(veg[cell,1]>=.3)&np.isfinite(clim[cell]).all(1)&np.isfinite(veg[cell]).all(1)
        t=t.loc[ok].reset_index(drop=True);o["post_environment"]=support(t)
        if not admitted(o["post_environment"]):o["status"]="ENVIRONMENT_SUPPORT_STOP";save(o);return
        cell=t.cell.to_numpy(int)
        angle=2*np.pi*(t.month.to_numpy()-1)/12
        X=np.column_stack([np.log(t.n),np.log(t.k),t.cov,t.nights,t.night_sd,np.log1p(t.micHt),t.source.eq("nabat"),t.countType.eq("a"),np.sin(angle),np.cos(angle),t.year,np.abs(t.lat),clim[cell],np.log1p(veg[cell,0]),veg[cell,1],np.log1p(veg[cell,2]),cc[cell],vc[cell],t.expected,np.log1p(total[cell]),np.log1p(wr[cell]),veg[cell,3]]).astype(float)
        Y=t[["Y0","Y1","Y2"]].to_numpy(float)
        assert X.shape[1]==len(FEATURES) and np.isfinite(X).all() and np.isfinite(Y).all()
        o["tests"]={"spatial_2":score(t,X,Y,2),"spatial_4":score(t,X,Y,4),"strict_source_spatial_2":score(t,X,Y,2,True)}
        o["primary_pass"]=all(v.get("primary_pass",False) for v in o["tests"].values())
        o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__
        # omit exception URLs / sensitive values
        save(o)
if __name__=="__main__":main()
