"""V17: matched reported-effort species sorting by wing x measured PAVD."""
import collections as C, hashlib, itertools, json
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer
from scipy.optimize import minimize
from scipy.special import expit
from macro_fd_v15_batamp_admission import ROOT,PIN,FILES,verify,numbers,dictionary
from macro_fd_v4_global_ranges import read_ranges,wing,metric
from macro_fd_v5_structure import edges,check_overlap,climate,gedi
from macro_fd_v16_batamp_structure import ENV_HASH,CLIM_HASH,keyfold
OUT=Path("macro_fd_v17_result.json")
MODELS=("N","B","M","W","V")
RIDGE=.1
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V17_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def components(t):
    parent={}
    def root(x):
        parent.setdefault(x,x)
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x
    def union(a,b):
        a,b=root(a),root(b)
        if a!=b:parent[max(a,b)]=min(a,b)
    tokens=[]
    for src,ds in zip(t.source,t.dataset):
        z=sorted({(str(src),v.strip()) for v in str(ds).split(",") if v.strip()})
        assert z
        for x in z[1:]:union(z[0],x)
        root(z[0]);tokens.append(z[0])
    return [root(x) for x in tokens]
def blockkeys(t,g):
    return [(int(r)//g,int(c)//g) for r,c in zip(t.row,t.col)]
def support(t,sp):
    return {"units":len(t),"sites":int(t.siteId.nunique()),"native_cells":int(t.cell.nunique()),"blocks2":len(set(blockkeys(t,2))),"source_components":len(set(components(t))),"pairs":int(sum(len(x) for x in t.pairs)),"species":len(sp)}
def admitted(a):
    return a["units"]>=100 and a["sites"]>=60 and a["native_cells"]>=20 and a["blocks2"]>=15 and a["source_components"]>=10 and a["species"]>=8
def unit_weights(t,b,mask):
    groups=C.defaultdict(lambda:C.defaultdict(lambda:C.defaultdict(list)))
    for i in np.flatnonzero(mask):
        groups[b[i]][int(t.cell.iloc[i])][int(t.siteId.iloc[i])].append(i)
    w=np.zeros(len(t))
    for cells in groups.values():
        for sites in cells.values():
            for u in sites.values():w[u]=1/(len(groups)*len(cells)*len(sites)*len(u))
    assert abs(w.sum()-1)<1e-10
    return w
def fit(A,y,w):
    assert len(y)==len(w)==len(A) and abs(w.sum()-1)<1e-10
    scale=np.sqrt(w@(A*A));scale[scale<1e-10]=1.
    X=A/scale
    def fun(b):
        z=X@b
        loss=w@(np.logaddexp(0,z)-y*z)+.5*RIDGE*(b@b)
        grad=X.T@(w*(expit(z)-y))+RIDGE*b
        return loss,grad
    f=minimize(fun,np.zeros(X.shape[1]),jac=True,method="L-BFGS-B",options={"maxiter":500,"gtol":1e-9,"ftol":1e-12})
    assert np.isfinite(f.x).all() and np.linalg.norm(fun(f.x)[1],ord=np.inf)<1e-5
    return f.x/scale
def score(t,A,y,ui,paircounts,cols,g,strict=False):
    b=blockkeys(t,g);src=components(t)
    bf=keyfold(b);sf=keyfold(src)
    folds=[];out=np.full((len(t),len(MODELS)),np.nan)
    combos=list(itertools.product(range(5),repeat=2)) if strict else [(i,None) for i in range(5)]
    for i,j in combos:
        te=(bf==i)&(sf==j) if strict else bf==i
        tr=(bf!=i)&(sf!=j) if strict else bf!=i
        testblocks={b[k] for k in np.flatnonzero(te)}
        ts=int(t.loc[te,"siteId"].nunique());rs=int(t.loc[tr,"siteId"].nunique())
        if len(testblocks)<2 or ts<2 or rs<30:continue
        assert not {b[k] for k in np.flatnonzero(tr)}&testblocks
        if strict:assert not {src[k] for k in np.flatnonzero(tr)}&{src[k] for k in np.flatnonzero(te)}
        trp=tr[ui];tep=te[ui]
        w=unit_weights(t,b,tr)[ui[trp]]/paircounts[ui[trp]]
        out[te,0]=-np.log(2)
        for k,name in enumerate(MODELS[1:],1):
            f=cols[name];beta=fit(A[trp][:,f],y[trp],w)
            z=A[tep][:,f]@beta
            ls=y[tep]*z-np.logaddexp(0,z)
            avg=np.bincount(ui[tep],weights=ls,minlength=len(t))/paircounts
            out[te,k]=avg[te]
        wte=unit_weights(t,b,te)
        a=wte[te]@out[te]
        folds.append({"fold":[i,j],"units":int(te.sum()),"test_blocks":len(testblocks),"test_sites":ts,"training_sites":rs,"V_M":float(a[4]-a[2]),"V_B":float(a[4]-a[1]),"V_N":float(a[4]-a[0]),"M_B":float(a[2]-a[1]),"W_B":float(a[3]-a[1])})
    ok=np.isfinite(out).all(1);okblocks={b[i] for i in np.flatnonzero(ok)}
    r={"status":"insufficient_fold_support","grain":g,"strict":strict,"folds":folds,"scored_units":int(ok.sum()),"scored_fraction":float(ok.mean()),"scored_blocks":len(okblocks)}
    if len(folds)<(10 if strict else 5) or ok.mean()<(.7 if strict else 1.) or len(okblocks)<10:return r
    w=unit_weights(t,b,ok);a=w[ok]@out[ok]
    by=C.defaultdict(list)
    for i in np.flatnonzero(ok):by[b[i]].append(i)
    bw=np.array([w[v].sum() for v in by.values()])
    bd=np.array([w[v]@(out[v,4]-out[v,2])/w[v].sum() for v in by.values()])
    gain=float(bw@bd);assert abs(gain-(a[4]-a[2]))<1e-10
    om=(gain-bw*bd)/(1-bw)
    r.update(status="scored",log_scores=dict(zip(MODELS,a.tolist())),V_M=gain,V_B=float(a[4]-a[1]),V_N=float(a[4]-a[0]),M_B=float(a[2]-a[1]),W_B=float(a[3]-a[1]),positive_blocks=int((bd>0).sum()),positive_folds=sum(f["V_M"]>0 for f in folds),delete_one_block_range=[float(om.min()),float(om.max())])
    r["primary_pass"]=bool(r["V_M"]>0 and r["V_B"]>0 and r["V_N"]>0 and r["positive_blocks"]/len(by)>=.6 and r["positive_folds"]/len(folds)>=.8 and om.min()>0)
    r["subgroups"]={}
    for name,flag in [("woody",t.woody.to_numpy(bool)),("other",~t.woody.to_numpy(bool))]:
        q=ok&flag
        if q.any():
            z=unit_weights(t,b,q)[q]@out[q]
            r["subgroups"][name]={"units":int(q.sum()),"blocks":len({b[i] for i in np.flatnonzero(q)}),"V_M":float(z[4]-z[2]),"V_B":float(z[4]-z[1]),"V_N":float(z[4]-z[0])}
    return r
def selftest():
    a=np.array([[1.,2.],[2.,3.],[0.,-1.]])
    y=np.array([0.,1.,0.]);w=np.ones(3)/3
    b=fit(a,y,w);b2=fit(-a,1-y,w)
    assert np.allclose(b,b2,atol=1e-7)
def main():
    o={"stage":"matched monitored species sorting, wing x vertical vegetation allocation","status":"START","source_commit":PIN,"limits":["equal reported nights not necessarily the same nights","conditional published detections, not occupancy or true habitat selection","not measured bat flight height or competitive partitioning","same public archive as V15/V16; independent of all earlier US data not established","coarse-grid nominal edge guard not calibrated coordinate precision","woody subgroup descriptive; all-cover primary landscape test","no raw locations, identifiers or pair records exported"]}
    try:
        selftest()
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
        ids=[i for i,n in enumerate(names) if n in w.index];nm=[names[i] for i in ids];assert len(nm)==264
        Z,_=metric(w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float))
        pos={n:i for i,n in enumerate(nm)}
        for k in ("source","countType","dataset"):d[k]=d[k].astype(object).fillna("").astype(str).str.strip()
        good=d.lon.between(-170,-50)&d.lat.between(15,51.6)&np.isfinite(d.micHt)&d.micHt.gt(0)&d.siteId.notna()&d.source.isin(["batamp","nabat"])&d.countType.isin(["a","p"])&d.dataset.ne("")
        d=d.loc[good,["id","siteId","micHt","lat","lon","source","countType","dataset"]].copy()
        tr=Transformer.from_crs(4326,crs,always_xy=True);rev=Transformer.from_crs(crs,4326,always_xy=True)
        x,y=tr.transform(d.lon.to_numpy(),d.lat.to_numpy());col,row=(~T)*(x,y)
        d["col"]=np.floor(col).astype(int);d["row"]=np.floor(row).astype(int)
        interior=(np.minimum(col%1,1-col%1)*T.a>=15000)&(np.minimum(row%1,1-row%1)*abs(T.e)>=15000)
        _,a=rev.transform(np.zeros(len(d)),T.f+d.row.to_numpy()*T.e);_,b=rev.transform(np.zeros(len(d)),T.f+(d.row.to_numpy()+1)*T.e)
        grid=d.row.between(0,shape[0]-1)&d.col.between(0,shape[1]-1)&(np.maximum(a,b)<=51.6)&(np.minimum(a,b)>=-51.6)
        o["detector_support"]={"regional":len(d),"grid_interior_whole_GEDI_latitude":int((interior&grid).sum())}
        d=d.loc[interior&grid].copy();d["cell"]=d.row*shape[1]+d.col
        keep=s.name.isin(pos)&s.year.between(2019,2022)&s.month.between(5,9)&s.detectorNights.ge(5)
        s=s.loc[keep,["detId","year","month","name","detectorNights","detectionNights"]].merge(d,left_on="detId",right_on="id",validate="many_to_one")
        units=[]
        for _,g in s.groupby(["detId","year","month"],sort=False,observed=True):
            assert g.name.is_unique
            r=g.iloc[0][["detId","siteId","row","col","cell","lat","micHt","year","month","source","countType","dataset"]].to_dict()
            m=sorted([(n,int(night),int(dn)>0) for n,night,dn in zip(g.name,g.detectorNights,g.detectionNights)])
            r.update(n=len(m),sum_nights=sum(x[1] for x in m),monitored=m);units.append(r)
        o["detector_months_before_dedup"]=len(units)
        if not units:o["status"]="OBSERVATION_SUPPORT_STOP";save(o);return
        t=pd.DataFrame(units).sort_values(["n","sum_nights","detId"],ascending=[False,False,True]).drop_duplicates(["siteId","source","countType","year","month"]).reset_index(drop=True)
        o["deduplicated_units"]=len(t)
        t["pairs"]=t.monitored.map(lambda m:[(pos[a],pos[b],n,int(da)) for (a,n,da),(b,k,db) in itertools.combinations(m,2) if n==k and da!=db])
        t=t.loc[t.pairs.map(bool)].reset_index(drop=True)
        def spp(t):return {i for p in t.pairs for a,b,_,_ in p for i in (a,b)}
        o["pre_environment"]=support(t,spp(t));o["status"]="OBSERVATION_SUPPORT_COMPLETE";save(o)
        if not admitted(o["pre_environment"]):o["status"]="OBSERVATION_SUPPORT_STOP";save(o);return
        check_overlap();tx,ty=edges(T,shape)
        o["status"]="CLIMATE_ACQUISITION";save(o);clim,cc=climate(o,tx,ty);assert o["climate"]["sha256"]==CLIM_HASH
        o["status"]="GEDI_ACQUISITION";save(o);veg,vc=gedi(o,tx,ty)
        assert {k:v["sha256"] for k,v in o["GEDI"]["metrics"].items()}==ENV_HASH
        cell=t.cell.to_numpy(int);ok=(cc[cell]>=.5)&(vc[cell]>=.5)&(veg[cell,2]>0)&np.isfinite(clim[cell]).all(1)&np.isfinite(veg[cell]).all(1)
        t=t.loc[ok].reset_index(drop=True);o["post_environment"]=support(t,spp(t))
        cell=t.cell.to_numpy(int);t["woody"]=(veg[cell,0]>5)&(veg[cell,1]>=.3)
        o["woody_units"]=int(t.woody.sum())
        if not admitted(o["post_environment"]):o["status"]="ENVIRONMENT_SUPPORT_STOP";save(o);return
        active=sorted(spp(t));speciesidx={j:i for i,j in enumerate(active)}
        pc=t.pairs.map(len).to_numpy(int)
        ui=np.repeat(np.arange(len(t)),pc)
        arr=np.array([x for p in t.pairs for x in p],int);a,b,night,y=arr.T
        diff=Z[a]-Z[b]
        sp=np.zeros((len(arr),len(active)));ix=np.arange(len(arr))
        sp[ix,[speciesidx[k] for k in a]]=1;sp[ix,[speciesidx[k] for k in b]]=-1
        nab=t.source.eq("nabat").to_numpy(float)[ui];act=t.countType.eq("a").to_numpy(float)[ui]
        c=cell[ui];ang=2*np.pi*(t.month.to_numpy()[ui]-1)/12
        context=np.column_stack([clim[c],np.abs(t.lat.to_numpy()[ui]),np.sin(ang),np.cos(ang),t.year.to_numpy()[ui],np.log1p(t.micHt.to_numpy()[ui]),np.log1p(night),nab,act,np.log1p(veg[c,0]),veg[c,1],np.log1p(veg[c,2]),cc[c],vc[c]])
        interactions=(context[:,:,None]*diff[:,None,:]).reshape(len(arr),-1)
        rng=R[np.array(ids)[a],c].astype(float)-R[np.array(ids)[b],c].astype(float)
        B=np.column_stack([sp,sp*nab[:,None],sp*act[:,None],interactions,rng])
        tail=diff*veg[c,3,None]
        A=np.column_stack([B,tail]);nb=B.shape[1]
        cols={"B":np.arange(nb),"M":np.r_[np.arange(nb),nb+2],"W":np.r_[np.arange(nb),nb,nb+1],"V":np.arange(nb+3)}
        assert np.isfinite(A).all() and np.isin(y,[0,1]).all()
        o["features"]={"baseline_columns":nb,"vertical_columns":["AR_x_PAVD","logWL_x_PAVD","logmass_x_PAVD"],"context_order":["bio1","bio4","bio5","bio6","bio12","bio15","abs_lat","month_sin","month_cos","year","log1p_mic_height","log1p_reported_nights","nabat","activity","log1p_RH98","cover","log1p_PAI","climate_area_support","GEDI_area_support"],"ridge":RIDGE,"outcome":"one label positive and one zero, identical reported effort"}
        o["tests"]={"spatial_2":score(t,A,y,ui,pc,cols,2),"spatial_4":score(t,A,y,ui,pc,cols,4),"strict_source_spatial_2":score(t,A,y,ui,pc,cols,2,True)}
        o["primary_pass"]=all(v.get("primary_pass",False) for v in o["tests"].values())
        o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__;save(o)
if __name__=="__main__":main()
