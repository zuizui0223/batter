"""V28: mapped range sorting across matched landscape heterogeneity transitions."""
import collections as C,json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from combine_v6b_coverage import acquire,COARSE
from macro_fd_v7_multidomain import mapping
from macro_fd_v5_structure import edges,check_overlap,climate,aggregate
from gedi_landscape_heterogeneity_v28 import gedi_heterogeneity
from macro_fd_v16_batamp_structure import ENV_HASH,CLIM_HASH
OUT=Path("macro_fd_v28_result.json")
REG=["North_America","East_Asia","South_America","Africa"]
NREP=4999
SEED=20261128
AXES=["joint","RH98_between_12km_SD","bottom_PAVD_fraction_between_12km_SD"]
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V28_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def quant(x):
    return np.quantile(x,[0,.25,.5,.75,1]).tolist() if len(x) else None
def blocks(rc,g):
    return np.unique(rc//g,axis=0,return_inverse=True)[1]
def match(region,rc,shape,baseline,keep):
    ix=np.flatnonzero(keep&region)
    x=baseline[ix];sd=x.std(0);sd[sd<1e-10]=1
    z=(x-x.mean(0))/sd
    look={int(v):k for k,v in enumerate(ix)}
    cand=[];n=0
    for i in ix:
        r,c=rc[i]
        for rr,cc in ((r+1,c),(r,c+1)):
            if rr>=shape[0] or cc>=shape[1] or r//5!=rr//5 or c//5!=cc//5:continue
            j=int(rr*shape[1]+cc)
            if j not in look:continue
            n+=1
            d=np.abs(z[look[int(i)]]-z[look[j]])
            rms=float(np.sqrt(np.mean(d*d)))
            if rms<=.5 and d.max()<=1:cand.append((rms,int(i),j))
    cand.sort();used=set();p=[];v=[]
    for rms,i,j in cand:
        if i in used or j in used:continue
        used.update((i,j));p.append((i,j));v.append(rms)
    ep=np.asarray(p,int).reshape(-1,2)
    q=rc[ep[:,0]]
    assert len(used)==2*len(ep)
    assert np.all(rc[ep[:,0]]//5==rc[ep[:,1]]//5)
    return ep,{"cells":len(ix),"adjacent_candidates":n,"caliper_candidates":len(cand),"disjoint_pairs":len(ep),"blocks5":len(np.unique(q//5,axis=0)),"blocks10":len(np.unique(q//10,axis=0)),"baseline_RMS_quantiles":quant(v)}
def block_vectors(sign,delta,b):
    # sign=+1 where species occurs only in first endpoint, -1 second, 0 otherwise.
    ns=len(sign);nb=int(b.max()+1);n=np.zeros((ns,nb),int);v=np.zeros((ns,nb,2))
    for k in range(nb):
        m=b==k;a=sign[:,m]
        cnt=np.count_nonzero(a,axis=1);n[:,k]=cnt
        v[:,k]=np.divide(a@delta[m],cnt[:,None],out=np.zeros((ns,2)),where=cnt[:,None]>0)
    return v,n
def genusweights(names):
    g=np.array([x.split("_")[0] for x in names]);_,ix,c=np.unique(g,return_inverse=True,return_counts=True)
    w=1/(len(c)*c[ix]);assert np.isclose(w.sum(),1)
    return w
def kernel(v,n,names):
    w=genusweights(names);B=(n>0).sum(1)
    assert (B>=2).all()
    coeff=w/(B*(B-1))
    K=[];u=[]
    for j in range(2):
        a=v[:,:,j];k=(a.T*coeff)@a
        np.fill_diagonal(k,0)
        direct=np.sum(coeff*(a.sum(1)**2-(a*a).sum(1)))
        assert np.isclose(k.sum(),direct,atol=1e-10)
        K.append(k);u.append(float(direct))
    return np.stack([(K[0]+K[1])/2,*K]),np.array([np.mean(u),*u])
def null(K,seed):
    rng=np.random.default_rng(seed)
    s=rng.choice(np.array([-1.,1.]),size=(NREP,K.shape[1]))
    return np.stack([((s@k)*s).sum(1) for k in K],axis=1)
def trait_bridge(v,n,names,tab,wings):
    loc={k:i for i,k in enumerate(names)}
    ss=sorted(set(names)&set(tab.index)&set(wings.index))
    if not ss:return {"matched_species":0}
    g=C.defaultdict(list)
    for x in ss:g[x.split("_")[0]].append(x)
    ss=[x for a in g.values() if len(a)>=2 for x in a]
    if len(ss)<2:return {"matched_species_with_congeners":len(ss)}
    a=np.array([v[loc[x]].sum(0)/np.count_nonzero(n[loc[x]]) for x in ss])
    z=wings.loc[ss,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float);z[:,1:]=np.log(z[:,1:])
    p=tab.loc[ss];S=np.eye(4)[[["A","Ar","G","S"].index(x) for x in p.stratum]]
    J=(p[COARSE].to_numpy(float)[:,:,None]*S[:,None,:]).reshape(len(ss),12)
    g=np.array([x.split("_")[0] for x in ss]);ww=genusweights(ss)
    for k in np.unique(g):
        ix=g==k;a[ix]-=a[ix].mean(0);z[ix]-=z[ix].mean(0);J[ix]-=J[ix].mean(0)
    def corr(x):
        cov=x.T@(ww[:,None]*a)
        den=np.sqrt((ww@(x*x))[:,None]*(ww@(a*a))[None,:])
        return [[float(cov[i,j]/den[i,j]) if den[i,j]>1e-12 else None for j in range(2)] for i in range(len(x))]
    return {"matched_species_with_congeners":len(ss),"genera":len(set(g)),"physical_trait_order":["AR","log_WL","log_mass"],"within_genus_centered_correlations":corr(z),"strategy_covariance_norm":float(np.linalg.norm(J.T@(ww[:,None]*a))),"limits":"descriptive only; eligible species shared across blocks; not statistical inference"}
def main():
    o={"stage":"global mapped range-edge sorting by landscape structural heterogeneity","status":"START","axis_order":AXES,"limits":["range-map occupancy, not observed presence/absence or actual boundaries at fine scale","between-12km means SD, not within-footprint complexity or navigable volume","same source archives, new estimand not independent replication","matched-pair block sign null not complete spatial exchangeability","descriptive trait bridge only"]}
    try:
        check_overlap()
        v,f=aggregate([np.array([[1.,3.]]),np.array([[1.,9.]])],np.ones((1,2),bool),[0,1,2],[0,1],[0,2],[0,1])
        assert np.allclose(v,[2.,5.]) and np.allclose(np.sqrt(v[...,1]-v[...,0]**2),1)
        names,R,shape,crs,T=read_ranges(o);assert len(names)==1141
        rc=np.array(np.unravel_index(np.arange(R.shape[1]),shape)).T
        rev=Transformer.from_crs(crs,4326,always_xy=True)
        lon,lat=rev.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        _,la=rev.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e);_,lb=rev.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)
        reg=np.full(len(rc),"other",dtype="U24")
        for r,(l,h,bot,top) in REGIONS.items():
            ok=(lon>=l)&(lon<=h)&(lat>=bot)&(lat<top);assert np.all(reg[ok]=="other");reg[ok]=r
        tx,ty=edges(T,shape);o["status"]="CLIMATE_ACQUISITION";save(o)
        clim,cc=climate(o,tx,ty);assert o["climate"]["sha256"]==CLIM_HASH
        o["status"]="GEDI_ACQUISITION";save(o);veg,vc=gedi_heterogeneity(o,tx,ty)
        assert {k:v["sha256"] for k,v in o["GEDI"]["metrics"].items()}==ENV_HASH and o["GEDI"]["common_native_pixels"]==749456
        keep=(np.maximum(la,lb)<=51.6)&(np.minimum(la,lb)>=-51.6)&(cc>=.5)&(vc>=.5)&(veg[:,0]>5)&(veg[:,1]>=.3)&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)&(R.sum(0)>0)&np.isin(reg,REG)
        B=np.column_stack([clim,veg[:,:4],cc,vc])
        o["region_support"]={};pairs={}
        for r in REG:
            ep,a=match(reg==r,rc,shape,B,keep)
            pairs[r]=ep;o["region_support"][r]=a
        o["status"]="MATCH_COMPLETE";save(o)
        if not all(x["disjoint_pairs"]>=50 and x["blocks5"]>=8 and x["blocks10"]>=5 for x in o["region_support"].values()):
            o["status"]="MATCH_SUPPORT_STOP";save(o);return
        data={};unique=set()
        for r in REG:
            ep=pairs[r];i,j=ep.T
            x=veg[keep&(reg==r),4:6];sd=x.std(0);assert (sd>0).all()
            delta=(veg[i,4:6]-veg[j,4:6])/sd
            sign=R[:,i].astype(np.int8)-R[:,j].astype(np.int8)
            b5=blocks(rc[i],5);b10=blocks(rc[i],10)
            v5,n5=block_vectors(sign,delta,b5);v10,n10=block_vectors(sign,delta,b10)
            eligible=(np.count_nonzero(sign,axis=1)>=8)&((n5>0).sum(1)>=4)&((n10>0).sum(1)>=3)
            ns=np.flatnonzero(eligible);unique.update(ns.tolist())
            nm=[names[k] for k in ns]
            data[r]=(nm,{5:(v5[ns],n5[ns]),10:(v10[ns],n10[ns])})
            o["region_support"][r].update(eligible_species=len(ns),eligible_genera=len(set(n.split("_")[0] for n in nm)),exclusive_pairs_quantiles=quant(np.count_nonzero(sign[ns],axis=1)),RH98_SD_quantiles=quant(x[:,0]),PAVD_SD_quantiles=quant(x[:,1]),matched_absolute_standardized_difference_quantiles=[quant(np.abs(delta[:,k])) for k in range(2)])
        o["unique_species"]=len(unique)
        o["status"]="SPECIES_SUPPORT_COMPLETE";save(o)
        if len(unique)<100 or not all(len(x[0])>=20 for x in data.values()):
            o["status"]="SPECIES_SUPPORT_STOP";save(o);return
        o["tests"]={}
        for g in (5,10):
            obs=[];sim=[];rr={}
            for k,r in enumerate(REG):
                nm,b=data[r];v,n=b[g];K,u=kernel(v,n,nm)
                z=null(K,SEED+g+100*k);obs.append(u);sim.append(z)
                rr[r]={"score":u.tolist(),"null_quantiles":np.quantile(z,[.025,.5,.975],axis=0).tolist(),"null_rank_le":np.mean(z<=u+1e-12,axis=0).tolist(),"blocks":n.shape[1],"species":len(nm)}
            obs=np.array(obs);total=obs.mean(0);sim=np.mean(sim,axis=0)
            q=np.quantile(sim,[.025,.5,.975],axis=0);loo=(total*len(REG)-obs)/(len(REG)-1)
            o["tests"][str(g)]={"region_scores":rr,"observed":total.tolist(),"null_quantiles":q.tolist(),"null_rank_le":np.mean(sim<=total+1e-12,axis=0).tolist(),"positive_regions":(obs>0).sum(0).tolist(),"delete_one_region_min":loo.min(0).tolist(),"delete_one_region_max":loo.max(0).tolist(),"primary_pass":bool(total[0]>0 and total[0]>q[2,0] and (obs[:,0]>0).sum()>=3 and loo[:,0].min()>0)}
        o["primary_pass"]=all(v["primary_pass"] for v in o["tests"].values())
        # Descriptive functional extension after primary scoring, source failure does not erase primary.
        try:
            w=wing(o);a,b,_=acquire(o);tab=mapping(a,b,names,w,o);tab=tab.loc[tab.index.intersection(w.index)].sort_index();assert len(tab)==234
            o["functional_bridge"]={r:trait_bridge(*data[r][1][5],data[r][0],tab,w) for r in REG}
        except Exception as e:o["functional_bridge"]={"status":"STOP","error_type":type(e).__name__}
        o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__;save(o)
if __name__=="__main__":main()
