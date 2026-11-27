"""V8 global range assemblage diet/stratum coupling, aggregate-only outputs."""
import collections as C, itertools,json
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from macro_fd_v7_multidomain import mapping,distance
from combine_v6b_coverage import acquire,COARSE

SEED=20261127
NREP=4999
DOMAINS=("diet","mass")
STRATA=("A","Ar","G","S")

def group_codes(names):
    return np.unique([n.split("_")[0] for n in names],return_inverse=True)[1]

def expectation(labels,g):
    """Expected stratum mismatch for a random assignment without replacement within group."""
    n=len(labels);ng=int(g.max())+1
    h=np.zeros((ng,len(STRATA)),float);np.add.at(h,(g,labels),1)
    sz=h.sum(1);assert np.all(sz>0)
    prop=h/sz[:,None];S=1-prop@prop.T
    S[np.diag_indices(ng)]*=np.divide(sz,sz-1,out=np.zeros_like(sz),where=sz>1)
    E=S[g[:,None],g[None,:]];np.fill_diagonal(E,0)
    assert np.min(E)>=-1e-10 and np.max(E)<=1+1e-10 and np.allclose(E,E.T)
    return E

def permute(labels,g):
    rng=np.random.default_rng(SEED)
    a=np.tile(labels,(NREP,1));vary=np.zeros(len(labels),bool)
    for k in range(int(g.max())+1):
        ix=np.flatnonzero(g==k)
        if len(np.unique(labels[ix]))>1:
            vary[ix]=True
            a[:,ix]=labels[ix][np.argsort(rng.random((NREP,len(ix))),axis=1)]
            assert np.all(np.sort(a[:,ix],axis=1)==np.sort(labels[ix]))
    return a,vary

def null_score(W,labels,A,vary):
    """W symmetric; evaluate sum W_ij * (label_i != label_j)."""
    active=np.any(np.abs(W)>1e-16,axis=0)
    # Inactive rows from numerical zero have negligible bounded omitted weight.
    assert np.sum(np.abs(W[~active]))<1e-9
    vi=np.flatnonzero(vary&active);fi=np.flatnonzero(~vary&active)
    z=np.eye(len(STRATA))[labels[fi]]
    constant=np.sum(z*(W[np.ix_(fi,fi)]@z))
    if len(vi)==0:return np.full(len(A),W.sum()-constant)
    Q=W[np.ix_(vi,vi)]
    L=2*W[np.ix_(vi,fi)]@z
    out=np.empty(len(A))
    for i in range(0,len(A),128):
        h=np.eye(len(STRATA))[A[i:i+128,vi]]
        v=h.transpose(0,2,1).reshape(-1,len(vi))
        s=np.sum((v@Q)*v,axis=1).reshape(len(h),len(STRATA)).sum(1)
        linear=np.sum(h*L[None,:,:],axis=(1,2))
        out[i:i+len(h)]=W.sum()-constant-s-linear
    return out

def check():
    labels=np.array([0,1,0,2,1]);g=np.array([0,0,1,1,2])
    d=distance(np.array([[0.],[1.],[4.],[2.],[3.]]))
    W=d.copy();W-=d.sum()/20;np.fill_diagonal(W,0);W/=20
    # Exhaustive independent permutations of the two nonsingleton groups.
    p=np.array([np.r_[x,y,labels[4]] for x in itertools.permutations(labels[:2]) for y in itertools.permutations(labels[2:4])])
    q=np.array([np.sum(W*(v[:,None]!=v[None,:])) for v in p])
    a=null_score(W,labels,p,np.array([1,1,1,1,0],bool))
    assert np.allclose(a,q) and np.isclose(q.mean(),np.sum(W*expectation(labels,g)))
    assert np.isclose(np.sum(W*expectation(labels,np.zeros(5,int))),0)
    # Local example with a subset and singleton genus.
    ix=np.array([0,1,3,4]);dg=d[np.ix_(ix,ix)]
    ww=dg-dg.sum()/12;np.fill_diagonal(ww,0);ww/=12
    lab=labels[ix];gg=np.unique(g[ix],return_inverse=True)[1]
    pp=[lab.copy(),lab[[1,0,2,3]]]
    assert np.isclose(np.mean([np.sum(ww*(v[:,None]!=v[None,:])) for v in pp]),np.sum(ww*expectation(lab,gg)))

def cell_stats(M,D,labels,g,E):
    """Columns per domain: dbar, sbar, K, global E[K], local E[K]."""
    ncell=M.shape[0];out=np.empty((ncell,len(D),5))
    for j in range(ncell):
        ix=M.indices[M.indptr[j]:M.indptr[j+1]];k=len(ix);den=k*(k-1);assert k>=5
        s=(labels[ix,None]!=labels[ix][None,:]).astype(float)
        sg=E[np.ix_(ix,ix)]
        gg=np.unique(g[ix],return_inverse=True)[1]
        sl=expectation(labels[ix],gg)
        sb=s.sum()/den
        for m,d in enumerate(D):
            dd=d[np.ix_(ix,ix)];db=dd.sum()/den
            w=dd-db;np.fill_diagonal(w,0);w/=den
            assert abs(w.sum())<1e-10
            val=np.sum(w*s)
            assert abs(val-(np.sum(dd*s)/den-db*sb))<1e-10
            out[j,m]=[db,sb,val,np.sum(w*sg),np.sum(w*sl)]
    assert np.isfinite(out).all()
    return out

def weight_matrix(M,D,stat,weights):
    """Aggregated covariance coefficient for each domain, exact sparse co-occurrence sums."""
    size=np.asarray(M.sum(1)).ravel();den=size*(size-1)
    assert np.all(den>0) and abs(weights.sum()-1)<1e-10
    a=(M.T@M.multiply((weights/den)[:,None])).toarray()
    W=[]
    for k,d in enumerate(D):
        b=(M.T@M.multiply((weights*stat[:,k,0]/den)[:,None])).toarray()
        w=a*d-b;np.fill_diagonal(w,0)
        assert np.allclose(w,w.T,atol=1e-12) and abs(w.sum())<1e-9
        W.append(w)
    return np.asarray(W)

def weighted_stats(stat,w):
    return np.einsum("i,idk->dk",w,stat)

def region_weight(rc):
    blocks,which=np.unique(rc,axis=0,return_inverse=True)
    cnt=np.bincount(which);w=1/(len(cnt)*cnt[which])
    return w,which,len(cnt)

def summarize_perm(W,labels,A,vary,E,obs):
    analytic=np.sum(W*E);assert abs(np.sum(W*(labels[:,None]!=labels[None,:]))-obs)<1e-9
    v=null_score(W,labels,A,vary);mean=float(v.mean());sd=float(v.std())
    assert abs(mean-analytic)<=7*sd/np.sqrt(NREP)+1e-9
    return {"observed":float(obs),"expected":float(analytic),"residual":float(obs-analytic),
        "null_mean":mean,"null_sd":sd,"q025":float(np.quantile(v,.025)),"q975":float(np.quantile(v,.975)),
        "rank_le":float(np.mean(v<=obs+1e-12))}

def run_cohort(tag,tab,X,names,rc,reg,full):
    index={v:i for i,v in enumerate(names)};ids=[index[n] for n in tab.index]
    raw=X[ids];rich=raw.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    ok=(rich>=5)&(cov>=.8)
    if tag=="broad":assert int(ok.sum())==9631
    # no-transfer coverage is recomputed without a guessed count.
    M=csr_matrix(raw[:,ok].T.astype(float));M.sort_indices()
    names0=tab.index.tolist();labels=np.array([STRATA.index(v) for v in tab.stratum]);g=group_codes(names0)
    D=[distance(tab[COARSE].to_numpy(float)),distance(np.log(tab.mass.to_numpy(float))[:,None])]
    E=expectation(labels,g);E0=expectation(labels,np.zeros(len(labels),int))
    stat=cell_stats(M,D,labels,g,E)
    A,vary=permute(labels,g);B,vary0=permute(labels,np.zeros(len(labels),int))
    out={"species":len(ids),"eligible_cells":int(ok.sum()),"variable_stratum_species_genus_null":int(vary.sum()),
         "global_eligible_unweighted":stat.mean(0).tolist(),"global_monomorphic_diet_cells":int(np.sum(stat[:,0,0]<1e-12)),
         "global_monomorphic_stratum_cells":int(np.sum(stat[:,0,1]<1e-12)),
         "metric_order":["diet","mass"],"stat_order":["mean_domain_distance","mean_stratum_mismatch","K","global_genus_expected_K","local_genus_expected_K"],
         "region_support":{},"grains":{}}
    regs=reg[ok];rco=rc[ok];admitted=[]
    for name in REGIONS:
        take=regs==name
        n=int(take.sum());b5=len(np.unique(rco[take]//5,axis=0));b10=len(np.unique(rco[take]//10,axis=0))
        support={"eligible_cells":n,"blocks_5":b5,"blocks_10":b10,
                 "median_coverage":float(np.median(cov[ok][take])) if n else None,
                 "matched_species":int(np.any(raw[:,ok][:,take],axis=1).sum()) if n else 0,
                 "admitted":bool(n>=100 and b5>=10 and b10>=10)}
        out["region_support"][name]=support
        if support["admitted"]:admitted.append(name)
    out["admitted_regions"]=admitted
    if len(admitted)<4:out["status"]="insufficient_regions";return out
    for grain in (5,10):
        cases=[];reports={}
        for name in admitted:
            ix=np.flatnonzero(regs==name);s=stat[ix];w,b,nb=region_weight(rco[ix]//grain)
            v=weighted_stats(s,w);W=weight_matrix(M[ix],D,s,w)
            block=np.array([s[b==k].mean(0) for k in range(nb)])
            assert np.allclose(v,block.mean(0))
            resid=block[:,:,2]-block[:,:,3];local=block[:,:,2]-block[:,:,4]
            report={"cells":len(ix),"blocks":nb,"mean":v.tolist(),
                    "global_genus_residual_positive_blocks":(resid>1e-12).sum(0).tolist(),
                    "local_genus_residual_positive_blocks":(local>1e-12).sum(0).tolist(),
                    "global_genus_residual_mean":resid.mean(0).tolist(),
                    "local_genus_residual_mean":local.mean(0).tolist(),
                    "monomorphic_diet_cells":int(np.sum(s[:,0,0]<1e-12)),
                    "monomorphic_stratum_cells":int(np.sum(s[:,0,1]<1e-12)),
                    "null":{}}
            for j,k in enumerate(DOMAINS):
                q=summarize_perm(W[j],labels,A,vary,E,v[j,2])
                q0=summarize_perm(W[j],labels,B,vary0,E0,v[j,2])
                assert abs(q["expected"]-v[j,3])<1e-9 and abs(q0["expected"])<1e-9
                report["null"][k]={"genus":q,"unrestricted":q0}
            reports[name]=report;cases.append((W,v,resid,local,nb))
        W=np.mean([r[0] for r in cases],axis=0);v=np.mean([r[1] for r in cases],axis=0)
        gr=np.asarray([r[2].mean(0) for r in cases]);lr=np.asarray([r[3].mean(0) for r in cases])
        rr={"region_equal_mean":v.tolist(),"global_genus_residual":gr.mean(0).tolist(),"local_genus_residual":lr.mean(0).tolist(),
            "positive_region_block_fraction":np.mean([(r[2]>1e-12).mean(0) for r in cases],axis=0).tolist(),
            "positive_regions_global":[k for k,q in reports.items() if q["global_genus_residual_mean"][0]>0],
            "positive_regions_local":[k for k,q in reports.items() if q["local_genus_residual_mean"][0]>0],
            "leave_one_region_global_residual_range":[((gr.sum(0)-gr)/(len(gr)-1)).min(0).tolist(),((gr.sum(0)-gr)/(len(gr)-1)).max(0).tolist()],
            "regions":reports,"null":{}}
        for j,k in enumerate(DOMAINS):
            q=summarize_perm(W[j],labels,A,vary,E,v[j,2]);q0=summarize_perm(W[j],labels,B,vary0,E0,v[j,2])
            assert abs(q["expected"]-v[j,3])<1e-9
            rr["null"][k]={"genus":q,"unrestricted":q0}
        rr["screen"]=bool(len(rr["positive_regions_global"])>=4 and bool(set(rr["positive_regions_global"])&{"North_America","East_Asia"}) and
             rr["positive_region_block_fraction"][0]>=.6 and rr["null"]["diet"]["genus"]["rank_le"]>=.975 and
             rr["leave_one_region_global_residual_range"][0][0]>0 and len(rr["positive_regions_local"])>=4 and rr["local_genus_residual"][0]>0)
        out["grains"][str(grain)]=rr
    out["status"]="scored";return out

def main():
    out={"stage":"global diet-stratum coupling, range-defined potential assemblages","status":"START","seed":SEED,"permutations":NREP}
    try:
        check();names,X,shape,crs,T=read_ranges(out);assert len(names)==1141
        w=wing(out);a,b,c=acquire(out);tab=mapping(a,b,names,w,out);assert len(tab)==1034 and int(tab.no_transfer.sum())==998
        rc=np.array(np.unravel_index(np.arange(X.shape[1]),shape)).T
        lon,lat=Transformer.from_crs(crs,4326,always_xy=True).transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        reg=np.full(len(rc),"other",dtype="U24")
        for name,(l,r,b,t) in REGIONS.items():
            q=(lon>=l)&(lon<=r)&(lat>=b)&(lat<t);assert np.all(reg[q]=="other");reg[q]=name
        full=X.sum(0);out["cohorts"]={}
        for tag,t in [("broad",tab),("without_split",tab[tab.no_transfer])]:
            print("V8_COHORT="+tag,flush=True)
            out["cohorts"][tag]=run_cohort(tag,t,X,names,rc,reg,full)
        a=out["cohorts"]["broad"];b=out["cohorts"]["without_split"]
        sensitivity=bool(b["status"]=="scored" and set(b["admitted_regions"])==set(a["admitted_regions"]) and all(v["global_genus_residual"][0]>0 and v["local_genus_residual"][0]>0 for v in b["grains"].values()))
        out["primary_screen"]={"broad":bool(a["status"]=="scored" and all(v["screen"] for v in a["grains"].values())),"sensitivity":sensitivity}
        out["primary_screen"]["pass"]=all(out["primary_screen"].values())
        out["status"]="COMPLETE"
    except Exception as e:out.update(status="STOP",error_type=type(e).__name__,error=str(e)[:160])
    Path("macro_fd_v8_result.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V8_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
