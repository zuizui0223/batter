"""V29: community replacement across fixed matched heterogeneous landscapes."""
import collections as C,hashlib,json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from combine_v6b_coverage import acquire,COARSE
from macro_fd_v7_multidomain import mapping
from macro_fd_v5_structure import edges,check_overlap,climate
from gedi_landscape_heterogeneity_v28 import gedi_heterogeneity
from macro_fd_v16_batamp_structure import ENV_HASH,CLIM_HASH
from macro_fd_v28_structural_heterogeneity import match,REG
from macro_fd_v26_global_structural_replacement import metrics,decomp,blockkeys,weights
OUT=Path("macro_fd_v29_result.json")
RESP=["Simpson_replacement","Sorensen_total","nestedness_resultant"]
PIN={"North_America":133,"East_Asia":180,"South_America":315,"Africa":181}
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V29_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def beta(R,i,j):
    x=R[:,i];y=R[:,j]
    a=(x&y).sum(0).astype(float);b=(x&~y).sum(0).astype(float);c=(~x&y).sum(0).astype(float)
    m=np.minimum(b,c)
    assert ((a+m)>0).all()
    sim=m/(a+m);sor=(b+c)/(2*a+b+c);nest=sor-sim
    z=np.column_stack([sim,sor,np.maximum(nest,0)])
    assert np.allclose(z[:,1],z[:,0]+z[:,2]) and (z>=0).all() and (z<=1).all()
    return z
def summarize(sc,reg,b,mask):
    w=weights(reg,b,mask)[mask]
    return np.einsum("i,ijk->jk",w,sc[mask])
def score(X,Y,reg,rc,ep,nd,nb,grain,transfer=False):
    b=blockkeys(rc,reg,grain);rf=sorted(set(reg))
    if transfer:split=reg;folds=rf
    else:
        lookup={}
        for r in rf:
            bb=sorted({v for v in b if v[0]==r},key=lambda x:hashlib.sha256(repr(x).encode()).hexdigest())
            for j,v in enumerate(bb):lookup[v]=j%5
        split=np.array([lookup[k] for k in b]);folds=list(range(5))
    sc=np.full((len(Y),4,Y.shape[1]),np.nan);unc=sc.copy();fs=[]
    for f in folds:
        te=split==f;tr=~te
        if len({b[k] for k in np.flatnonzero(te)})<5 or tr.sum()<100 or len(set(reg[tr]))<(3 if transfer else 4):
            return {"status":"insufficient_fold_support","fold":str(f),"grain":grain}
        if not transfer:assert set(reg[tr])==set(reg[te])==set(rf)
        assert not set(ep[tr].ravel())&set(ep[te].ravel())
        w=weights(reg,b,tr)[tr];x=X[tr];mu=w@x;sd=np.sqrt(w@((x-mu)**2));act=sd>1e-12;sd[~act]=1
        z=(x-mu)/sd;zt=(X[te]-mu)/sd;z[:,~act]=0;zt[:,~act]=0
        y=Y[tr];ym=w@y;pred=[np.tile(ym,(te.sum(),1))]
        for n in (nd,nb,X.shape[1]):
            a=z[:,:n];coef=np.linalg.solve(a.T@(w[:,None]*a)+.1*np.eye(n),a.T@(w[:,None]*(y-ym)))
            assert np.max(abs(a.T@(w[:,None]*(a@coef-y+ym))+.1*coef))<1e-8
            pred.append(ym+zt[:,:n]@coef)
        raw=np.stack(pred,axis=1)
        sc[te]=(np.clip(raw,0,1)-Y[te,None,:])**2
        unc[te]=(raw-Y[te,None,:])**2
        m=summarize(sc,reg,b,te)
        fs.append({"fold":str(f),"pairs":int(te.sum()),"blocks":len({b[k] for k in np.flatnonzero(te)}),"V_B":(m[2]-m[3]).tolist(),"V_N":(m[0]-m[3]).tolist(),"V_heterogeneity_standardized_coefficients":coef[-2:].tolist(),"out_of_range_fraction_V":((raw[:,3]<0)|(raw[:,3]>1)).mean(0).tolist()})
    assert np.isfinite(sc).all() and np.isfinite(unc).all()
    mask=np.ones(len(Y),bool);w=weights(reg,b,mask);m=summarize(sc,reg,b,mask);u=summarize(unc,reg,b,mask);gain=m[2]-m[3]
    by=C.defaultdict(list)
    for i,k in enumerate(b):by[k].append(i)
    bw=np.array([w[v].sum() for v in by.values()]);diff=np.array([(sc[v,2]-sc[v,3]).mean(0) for v in by.values()])
    assert np.allclose(bw@diff,gain)
    loo=(gain-bw[:,None]*diff)/(1-bw[:,None])
    r={"status":"scored","grain":grain,"transfer":transfer,"pairs":len(Y),"region_blocks":len(by),"mse":dict(zip(["N","D","B","V"],m.tolist())),"unclipped_mse":dict(zip(["N","D","B","V"],u.tolist())),"V_B":gain.tolist(),"V_N":(m[0]-m[3]).tolist(),"B_D":(m[1]-m[2]).tolist(),"relative_V_B":np.divide(gain,m[2],out=np.zeros_like(gain),where=m[2]>1e-12).tolist(),"positive_blocks":(diff>0).sum(0).tolist(),"positive_folds":sum(f["V_B"][0]>0 for f in fs),"folds":fs,"delete_one_region_block_range":[loo.min(0).tolist(),loo.max(0).tolist()],"regions":{}}
    for k in rf:
        q=summarize(sc,reg,b,reg==k)
        r["regions"][k]={"pairs":int((reg==k).sum()),"V_B":(q[2]-q[3]).tolist(),"V_N":(q[0]-q[3]).tolist(),"mse":dict(zip(["N","D","B","V"],q.tolist()))}
    r["primary_pass"]=bool(gain[0]>0 and m[0,0]>m[3,0] and r["positive_folds"]>=(3 if transfer else 4) and (transfer or r["positive_blocks"][0]/len(by)>=.6) and loo[:,0].min()>0)
    return r
def functional(o,R,names,ep,reg,rc):
    w=wing(o);a,b,_=acquire(o);tab=mapping(a,b,names,w,o)
    tab=tab.loc[tab.index.intersection(w.index)].sort_index();assert len(tab)==234
    nm=tab.index.tolist();ids=[names.index(k) for k in nm];X=R[ids]
    full=R.sum(0);rich=X.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    a=w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float);a[:,1:]=np.log(a[:,1:]);a=(a-a.mean(0))/a.std(0)
    S=np.eye(4)[[["A","Ar","G","S"].index(x) for x in tab.stratum]]
    J=(tab[COARSE].to_numpy(float)[:,:,None]*S[:,None,:]).reshape(len(tab),12)
    assert np.allclose(J.sum(1),1);J=J-J.mean(0);J/=np.sqrt((J*J).sum(1).mean())
    Z=np.column_stack([a[:,:2]/np.sqrt(2),J,a[:,2]])
    assert np.allclose(metrics(Z).mean(0),1)
    g=np.array([k.split("_")[0] for k in nm]);G=np.zeros_like(Z)
    for k in np.unique(g):G[g==k]=Z[g==k].mean(0)
    out={"species":len(nm),"genera":len(set(g)),"domain_order":["joint","wing","strategy","mass"],"component_order":["raw_squared_contrast","genus_squared_contrast","within_genus_squared_residual","cross_term"],"cohorts":{}}
    for cut in (.2,.5):
        i,j=ep.T;ok=(rich[i]>=5)&(rich[j]>=5)&(cov[i]>=cut)&(cov[j]>=cut)
        i=i[ok];j=j[ok];rr=reg[ok];xy=rc[ok]
        report={"pairs":len(i),"region_counts":dict(C.Counter(rr)),"regions":{}}
        out["cohorts"][str(cut)]=report
        if not len(i):continue
        d=X[:,j].T/rich[j,None]-X[:,i].T/rich[i,None]
        _,_,_,p=decomp(d,Z,G);be=beta(X,i,j);b5=blockkeys(xy,rr,5)
        for k in [*sorted(set(rr)),"equal_region_block"]:
            m=rr==k if k!="equal_region_block" else np.ones(len(i),bool)
            ww=weights(rr,b5,m)[m]
            v=np.einsum("i,ijk->jk",ww,p[m])
            report["regions"][k]={"pairs":int(m.sum()),"mean_beta":(ww@be[m]).tolist(),"squared_components":v.tolist(),"residual_over_raw":np.divide(v[2],v[0],out=np.zeros(4),where=v[0]>1e-12).tolist()}
    return out
def main():
    o={"stage":"global matched landscape heterogeneity and community replacement","status":"START","response_order":RESP,"limits":["potential mapped assemblages, not surveys or observed temporal turnover","same source and matched pairs as V28, new estimand not independent replication","between-12km pixel mean SD, not within-footprint structure or 3D airspace","predictive association only; source maps may encode prior environment assumptions","functional characterization secondary and descriptive"]}
    try:
        check_overlap()
        names,R,shape,crs,T=read_ranges(o);assert len(names)==1141 and R.dtype==bool
        rc=np.array(np.unravel_index(np.arange(R.shape[1]),shape)).T
        rev=Transformer.from_crs(crs,4326,always_xy=True)
        lon,lat=rev.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        _,la=rev.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e);_,lb=rev.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)
        reg=np.full(len(rc),"other",dtype="U24")
        for r,(l,h,bot,top) in REGIONS.items():
            ok=(lon>=l)&(lon<=h)&(lat>=bot)&(lat<top);assert np.all(reg[ok]=="other");reg[ok]=r
        tx,ty=edges(T,shape)
        o["status"]="CLIMATE_ACQUISITION";save(o);clim,cc=climate(o,tx,ty);assert o["climate"]["sha256"]==CLIM_HASH
        o["status"]="GEDI_ACQUISITION";save(o);veg,vc=gedi_heterogeneity(o,tx,ty)
        assert {k:v["sha256"] for k,v in o["GEDI"]["metrics"].items()}==ENV_HASH and o["GEDI"]["common_native_pixels"]==749456
        rich=R.sum(0)
        keep=(np.maximum(la,lb)<=51.6)&(np.minimum(la,lb)>=-51.6)&(cc>=.5)&(vc>=.5)&(veg[:,0]>5)&(veg[:,1]>=.3)&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)&(rich>0)&np.isin(reg,REG)
        B=np.column_stack([clim,veg[:,:4],cc,vc])
        o["region_support"]={};parts=[]
        for r in REG:
            e,a=match(reg==r,rc,shape,B,keep)
            assert len(e)==PIN[r]
            o["region_support"][r]=a;parts.append(e)
        ep=np.concatenate(parts);i,j=ep.T;rr=reg[i];xy=rc[i]
        assert len(ep)==809 and len(set(ep.ravel()))==1618 and np.array_equal(rr,reg[j])
        assert np.array_equal(rc[i]//5,rc[j]//5) and np.array_equal(rc[i]//10,rc[j]//10)
        Y=beta(R,i,j);assert np.allclose(Y,beta(R,j,i))
        def mid(v):return (v[i]+v[j])/2
        def dif(v):return np.abs(v[i]-v[j])
        D=np.column_stack([np.log(np.minimum(rich[i],rich[j])),np.log(np.maximum(rich[i],rich[j])),np.abs(mid(lat)),dif(lat),(rc[i,0]==rc[j,0]).astype(float),mid(cc),dif(cc),mid(vc),dif(vc)])
        env=np.column_stack([clim,veg[:,:4]])
        Xb=np.column_stack([D,mid(env),dif(env),mid(veg[:,4:6])])
        X=np.column_stack([Xb,dif(veg[:,4:6])])
        assert np.isfinite(X).all() and np.isfinite(Y).all()
        envnames=["bio1","bio4","bio5","bio6","bio12","bio15","RH98","cover","PAI","bottom_PAVD_fraction"]
        o["feature_order"]=["log_min_richness","log_max_richness","absolute_mid_latitude","latitude_contrast","east_orientation","mean_climate_support","contrast_climate_support","mean_GEDI_support","contrast_GEDI_support"]+["mean_"+k for k in envnames]+["contrast_"+k for k in envnames]+["mean_RH98_SD","mean_PAVD_SD","contrast_RH98_SD","contrast_PAVD_SD"]
        assert len(o["feature_order"])==X.shape[1]
        o["response_support"]={"pairs":len(ep),"zero_Simpson":int((Y[:,0]==0).sum()),"regions":{r:{"pairs":int((rr==r).sum()),"mean":Y[rr==r].mean(0).tolist(),"zero_Simpson":int((Y[rr==r,0]==0).sum())} for r in REG}}
        o["status"]="MATCH_REPLAY_COMPLETE";save(o)
        o["tests"]={"spatial_5":score(X,Y,rr,xy,ep,D.shape[1],Xb.shape[1],5),"spatial_10":score(X,Y,rr,xy,ep,D.shape[1],Xb.shape[1],10),"region_transfer":score(X,Y,rr,xy,ep,D.shape[1],Xb.shape[1],5,True)}
        o["primary_pass"]=all(v.get("primary_pass",False) for v in o["tests"].values())
        o["status"]="PRIMARY_SCORED";save(o)
        try:o["functional_characterization"]=functional(o,R,names,ep,rr,xy)
        except Exception as e:o["functional_characterization"]={"status":"STOP","error_type":type(e).__name__}
        o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__;save(o)
if __name__=="__main__":main()
