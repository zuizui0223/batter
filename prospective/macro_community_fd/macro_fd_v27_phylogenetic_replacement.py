"""V27: leave-focal-species-out phylogenetic reconstruction of geographic replacement."""
import collections as C,hashlib,json,math
from pathlib import Path
import numpy as np
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from combine_v6b_coverage import acquire,COARSE
from macro_fd_v7_multidomain import mapping
from macro_fd_v10_phylo import tree_source,partition_tree,AGES,INDICES
from macro_fd_v11_wing_phylogeography import geography
from macro_fd_v26_global_structural_replacement import metrics,blockkeys,weights
OUT=Path("macro_fd_v27_result.json")
SEED=20261128
NREP=499
DOM=["joint","wing","strategy","mass"]
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V27_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def canonical(g):return np.unique(g,return_inverse=True)[1]
def predict(z,g,loo=True):
    g=canonical(g);n=len(g);k=g.max()+1;cnt=np.bincount(g,minlength=k)
    a=np.zeros((k,z.shape[1]));np.add.at(a,g,z)
    if not loo:return (a/cnt[:,None])[g]
    den=cnt[g]-1
    p=np.divide(a[g]-z,den[:,None],out=np.zeros_like(z),where=den[:,None]>0)
    p[den==0]=(z.sum(0)-z[den==0])/(n-1)
    return p
def normloss(Q,z):
    v=np.sum(z*(Q@z),axis=0)
    w=v[:2].sum();s=v[2:14].sum();m=v[14]
    a=np.array([(w+s)/2,w,s,m]);assert np.all(a>=-1e-9)
    return np.maximum(a,0)
def ratio(Q,z,res):
    den=normloss(Q,z);assert (den>1e-12).all()
    return normloss(Q,res)/den
def qmatrix(d,reg,b,mask):
    w=weights(reg,b,mask)[mask]
    u=d[mask]*np.sqrt(w[:,None])
    Q=u.T@u
    assert np.allclose(Q,Q.T)
    return Q
def qcohort(R,full,rc,reg,shape,threshold):
    rich=R.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    eligible=(rich>=5)&(cov>=.2)
    keep=eligible&(cov>=threshold)&np.isin(reg,list(REGIONS))
    ep=[]
    for i in np.flatnonzero(keep):
        x,y=rc[i]
        for xx,yy in ((x+1,y),(x,y+1)):
            if xx>=shape[0] or yy>=shape[1] or x//5!=xx//5 or y//5!=yy//5:continue
            j=int(xx*shape[1]+yy)
            if keep[j] and reg[i]==reg[j]:ep.append((i,j))
    ep=np.asarray(ep,int);i,j=ep.T
    p=R[:,i].T/rich[i,None];q=R[:,j].T/rich[j,None];T=.5*np.abs(q-p).sum(1)
    ok=T>=.05;ep=ep[ok];T=T[ok];d=(q[ok]-p[ok])/T[:,None];i,j=ep.T
    assert np.allclose(d.sum(1),0) and np.allclose(np.maximum(d,0).sum(1),1)
    rr=reg[i];xy=rc[i]
    support={};use=[]
    for r in REGIONS:
        m=rr==r;b5=len(set(blockkeys(xy[m],rr[m],5)));b10=len(set(blockkeys(xy[m],rr[m],10)))
        a={"cells":int((keep&(reg==r)).sum()),"edges":int(m.sum()),"endpoints":len(set(ep[m].ravel())),"blocks5":b5,"blocks10":b10}
        a["admitted"]=bool(m.sum()>=100 and b5>=10 and b10>=5);support[r]=a
        if a["admitted"]:use.append(r)
    k=np.isin(rr,use);d=d[k];rr=rr[k];xy=xy[k];ep=ep[k];T=T[k]
    report={"coverage_threshold":threshold,"eligible_cells_global":int((eligible&(cov>=threshold)).sum()),"regions":support,"admitted_regions":use,"edges":len(d),"endpoints":len(set(ep.ravel()))}
    if len(use)<(6 if threshold==.2 else 4) or len(d)<1000:report["status"]="INSUFFICIENT_SUPPORT";return None,report
    Q={};sub={}
    for g in (5,10):
        b=blockkeys(xy,rr,g);Q[g]=qmatrix(d,rr,b,np.ones(len(d),bool))
        sub[g]={r:qmatrix(d,rr,b,rr==r) for r in use}
        assert np.allclose(Q[g],np.mean(list(sub[g].values()),axis=0))
    report["status"]="ADMITTED"
    report["turnover_quantiles"]=np.quantile(T,[0,.25,.5,.75,1]).tolist()
    return (Q,sub,d,rr,xy),report
def evaluate(g,z,Q,sub,geoseq,seed,do_null=True):
    g=canonical(g);counts=np.bincount(g)
    residual=z-predict(z,g,True);ins=z-predict(z,g,False)
    result={"groups":len(counts),"singleton_species":int((counts==1).sum()),"designs":{}}
    for grain in (5,10):
        a=ratio(Q[grain],z,residual);b=ratio(Q[grain],z,ins)
        regional={r:ratio(q,z,residual).tolist() for r,q in sub[grain].items()}
        omit={}
        for r in regional:
            q=np.mean([x for k,x in sub[grain].items() if k!=r],axis=0)
            u=ratio(q,z,residual);omit[r]=float(u[1]-u[2])
        result["designs"][str(grain)]={"loo_ratio":a.tolist(),"in_sample_ratio":b.tolist(),"raw_denominator":normloss(Q[grain],z).tolist(),"gap":float(a[1]-a[2]),"region_ratios":regional,"positive_regions":sum(v[1]>v[2] for v in regional.values()),"omit_region_gap":omit}
    if not do_null:return result
    blocks=[np.flatnonzero(geoseq==k) for k in np.unique(geoseq)]
    mutable=[ix for ix in blocks if len(set(g[ix]))>1]
    mutable_frac=sum(len(ix) for ix in mutable)/len(g)
    rng=np.random.default_rng(seed)
    vals={5:[],10:[]};change=[]
    for i in range(NREP):
        p=g.copy()
        for ix in mutable:p[ix]=rng.permutation(g[ix])
        assert np.array_equal(np.bincount(p,minlength=len(counts)),counts)
        change.append(np.mean(p!=g))
        r=z-predict(z,p,True)
        for grain in (5,10):
            a=ratio(Q[grain],z,r);vals[grain].append([*a,float(a[1]-a[2])])
    result["null_support"]={"permutations":NREP,"mutable_fraction":float(mutable_frac),"changed_label_fraction_quantiles":np.quantile(change,[0,.5,1]).tolist()}
    for grain in (5,10):
        a=result["designs"][str(grain)];v=np.array(vals[grain]);obs=np.r_[a["loo_ratio"],a["gap"]]
        q=np.quantile(v,[.025,.5,.975],axis=0)
        a["null_quantiles"]=q.tolist();a["null_rank_le"]=(v<=obs+1e-12).mean(0).tolist()
        a["pass"]=bool(mutable_frac>=.5 and obs[4]>0 and obs[4]>q[2,4] and obs[1]<1 and obs[2]<1 and obs[1]<q[0,1] and obs[2]<q[0,2] and a["positive_regions"]>=math.ceil(.8*len(sub[grain])) and min(a["omit_region_gap"].values())>0)
    result["pass"]=all(x["pass"] for x in result["designs"].values())
    return result
def selftest():
    z=np.arange(20,dtype=float).reshape(4,5);g=np.array([0,0,1,2]);p=predict(z,g)
    assert np.array_equal(p[0],z[1]) and np.array_equal(p[1],z[0])
    assert np.allclose(p[2],z[[0,1,3]].mean(0))
def main():
    o={"stage":"global phylogenetic reconstruction of geographic functional replacement","status":"START","domain_order":DOM,"null_order":[*DOM,"wing_minus_strategy"],"limits":["potential range assemblages, not observed coexistence or temporal change","same source rosters as V26, not independent data","leave-focal-species-out not whole-community cold-start","trait scaling on fixed full roster","correlated posterior trees, not independent replicates","coarse strategy coding and shared provenance may contribute","no structural predictor or causal inference"]}
    try:
        selftest()
        names,X,shape,crs,T=read_ranges(o);assert len(names)==1141
        w=wing(o);a,b,_=acquire(o);tab=mapping(a,b,names,w,o)
        tab=tab.loc[tab.index.intersection(w.index)].sort_index();assert len(tab)==234
        nm=tab.index.tolist();ids=[names.index(n) for n in nm];R=X[ids];full=X.sum(0)
        a=w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float);a[:,1:]=np.log(a[:,1:]);a=(a-a.mean(0))/a.std(0)
        strata=np.eye(4)[[["A","Ar","G","S"].index(v) for v in tab.stratum]]
        J=(tab[COARSE].to_numpy(float)[:,:,None]*strata[:,None,:]).reshape(len(tab),12)
        assert np.allclose(J.sum(1),1)
        J=J-J.mean(0);J/=np.sqrt((J*J).sum(1).mean())
        z=np.column_stack([a[:,:2]/np.sqrt(2),J,a[:,2]])
        assert np.allclose(metrics(z).mean(0),1)
        rc=np.array(np.unravel_index(np.arange(R.shape[1]),shape)).T
        lon,lat=Transformer.from_crs(crs,4326,always_xy=True).transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        reg=np.full(len(rc),"other",dtype="U24")
        for r,(l,h,bot,top) in REGIONS.items():
            ok=(lon>=l)&(lon<=h)&(lat>=bot)&(lat<top);assert np.all(reg[ok]=="other");reg[ok]=r
        geo,inf=geography(R,reg);o["geography_bins"]=inf
        o["roster"]={"species":len(nm),"genera":len({n.split("_")[0] for n in nm})}
        data={};o["cohorts"]={}
        for k,threshold in (("primary",.2),("higher_coverage",.5)):
            res,rec=qcohort(R,full,rc,reg,shape,threshold)
            o["cohorts"][k]=rec
            if res is None:continue
            Q,sub,d,rr,xy=res
            for g in (5,10):
                b=blockkeys(xy,rr,g);wt=weights(rr,b,np.ones(len(d),bool))
                assert np.allclose(normloss(Q[g],z),wt@metrics(d@z),atol=1e-10)
            data[k]=(Q,sub)
            gn=np.array([n.split("_")[0] for n in nm])
            rec["genus_descriptive"]=evaluate(gn,z,Q,sub,geo,SEED,False)
        assert o["cohorts"]["primary"]["eligible_cells_global"]==9018
        o["status"]="SUPPORT_COMPLETE";save(o)
        if "primary" not in data:o["status"]="SUPPORT_STOP";save(o);return
        o["status"]="TREE_ACQUISITION";save(o)
        trees=tree_source(o)
        assert o["tree_source"]["release_sha256"]=="6f37526e6b5871d1a24fac5aa868835735359af902e1f555d1d7dfd1c8075e01"
        for k in data:o["cohorts"][k]["trees"]=[]
        for idx,tree in zip(INDICES,trees):
            p,meta=partition_tree(tree,names,{"common":nm})
            for k,(Q,sub) in data.items():
                out={"index":idx,"tree_metadata":meta,"ages":{}}
                for age in AGES:
                    out["ages"][str(age)]=evaluate(p["common"][str(age)],z,Q,sub,geo,SEED+idx,age==20)
                o["cohorts"][k]["trees"].append(out)
        for k in data:
            c=o["cohorts"][k];a=[v["ages"]["20"] for v in c["trees"]]
            c["pass_trees"]=sum(v["pass"] for v in a);c["primary_pass"]=c["pass_trees"]>=18
            c["summary"]={}
            for age in AGES:
                c["summary"][str(age)]={}
                for grain in (5,10):
                    gs=[v["ages"][str(age)]["designs"][str(grain)] for v in c["trees"]]
                    c["summary"][str(age)][str(grain)]={"loo_ratio_min_median_max":np.quantile([v["loo_ratio"] for v in gs],[0,.5,1],axis=0).tolist(),"in_sample_ratio_min_median_max":np.quantile([v["in_sample_ratio"] for v in gs],[0,.5,1],axis=0).tolist(),"gap_min_median_max":np.quantile([v["gap"] for v in gs],[0,.5,1]).tolist(),"positive_region_counts":dict(C.Counter(str(v["positive_regions"]) for v in gs))}
                    if age==20:c["summary"][str(age)][str(grain)].update(pass_trees=sum(v["pass"] for v in gs),gap_null_rank_min_median_max=np.quantile([v["null_rank_le"][4] for v in gs],[0,.5,1]).tolist(),wing_null_rank_median=float(np.median([v["null_rank_le"][1] for v in gs])),strategy_null_rank_median=float(np.median([v["null_rank_le"][2] for v in gs])))
            # avoid gigantic per-tree age results in Actions logs; exact full 20Ma values retained.
            for v in c["trees"]:v["ages"]={"20":v["ages"]["20"]}
        o["primary_pass"]=o["cohorts"]["primary"]["primary_pass"]
        o["coverage_robust"]=bool(o["primary_pass"] and o["cohorts"]["higher_coverage"].get("primary_pass",False))
        o["status"]="COMPLETE";save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__;save(o)
if __name__=="__main__":main()
