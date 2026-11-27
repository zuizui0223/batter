"""V7: source-verified, matched functional-domain prediction on native range cells."""
import collections as C, json,math
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS
from macro_fd_v5_structure import check_overlap,edges,climate,gedi,score,FEATURES
from macro_fd_v2_geography import expected_distance
from combine_v6b_coverage import acquire,norm,present,COARSE
ROOT=Path(__file__).resolve().parent
OUT=Path("macro_fd_v7_result.json")
COLS=["adult_mass_g",*COARSE,"foraging_stratum"]
def save(out):
    OUT.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("V7_STAGE="+out["status"],flush=True)
def expected(D,names):
    groups=C.defaultdict(list)
    for i,n in enumerate(names):groups[n.split("_")[0]].append(i)
    g=list(groups.values());n=len(names)
    H=np.zeros((n,len(g)))
    for j,v in enumerate(g):H[v,j]=1
    sz=H.sum(0);assert np.all(H.sum(1)==1)
    a=(H.T@D@H)/np.outer(sz,sz)
    # D diagonal zero, conditional draws are without replacement within a genus.
    f=np.divide(sz,sz-1,out=np.zeros_like(sz),where=sz>1)
    a[np.diag_indices(len(g))]*=f
    E=H@a@H.T;np.fill_diagonal(E,0)
    assert np.allclose(E,E.T) and np.allclose(np.diag(E),0)
    return E
def distance(z):
    # Squared Euclidean distance, normalised across different species pairs.
    z=np.asarray(z,float)
    d=(z*z).sum(1);D=d[:,None]+d[None,:]-2*z@z.T
    assert np.min(D)>-1e-8
    D=np.maximum(D,0);np.fill_diagonal(D,0)
    n=len(D);mu=D.sum()/(n*(n-1))
    assert mu>0 and np.isfinite(D).all()
    return D/mu
def self_test():
    z=np.array([[0.,1.],[1.,2.],[4.,3.],[2.,5.],[2.,2.]])
    D=distance(z);n=["a_a","a_b","b_a","b_b","c_a"]
    E=expected(D,n)
    ref=expected_distance(D[:,:,None],[[0,1],[2,3],[4]])[:,:,0]
    assert np.allclose(E,ref,atol=1e-12)
    assert abs(D.sum()/20-1)<1e-12
def mapping(a,b,names,w,out):
    bat=a.order.str.strip().str.casefold().eq("chiroptera")
    z=a.phylacine_binomial.map(norm)
    valid=bat&present(a.phylacine_binomial)&z.isin(names)
    counts=z[valid].value_counts();amb=set(counts[counts!=1].index)
    uni=valid&~z.isin(amb)
    assert int(valid.sum())==1256 and len(amb)==72 and int(uni.sum())==1069
    m=uni.copy();no_transfer=uni.copy()
    for k in COLS:
        flag=b[k].str.strip()
        m&=present(a[k])&present(flag)&~flag.str.contains("imput",case=False,regex=False)
        no_transfer&=~flag.str.contains("split from",case=False,regex=False)&~flag.str.contains("imput",case=False,regex=False)
    mass=pd.to_numeric(a.adult_mass_g,errors="coerce")
    diet=a[COARSE].apply(pd.to_numeric,errors="coerce")
    m&=np.isfinite(mass)&mass.gt(0)&np.isfinite(diet).all(1)&diet.ge(0).all(1)&diet.le(100).all(1)&np.isclose(diet.sum(1),100)&a.foraging_stratum.isin(["A","Ar","G","S"])
    assert int(m.sum())==1034
    f=pd.DataFrame({"name":z[m],"mass":mass[m],"stratum":a.loc[m,"foraging_stratum"],"no_transfer":no_transfer[m]})
    for k in COARSE:f[k]=diet.loc[m,k]/100
    f=f.set_index("name");assert not f.index.duplicated().any()
    common=f.index.intersection(w.index);assert len(common)==234
    out["trait_mapping"]={"exact_unique_matches":1069,"ambiguous_labels":72,"broad_species":len(f),"common_wing_species":len(common),"broad_without_split_annotations":int(f.no_transfer.sum()),"stratum_codes":dict(C.Counter(f.stratum))}
    return f
def cohort(tag,tab,X,names,rc,reg,lat,cohort_env,clim,veg,vegcov,full,w,out):
    pos={n:i for i,n in enumerate(names)};ids=[pos[n] for n in tab.index];n=len(ids)
    m=X[ids];rich=m.sum(0);cov=np.divide(rich,full,out=np.zeros_like(full,float),where=full>0)
    threshold=.20 if tag=="wing_common" else .80
    ok=(rich>=5)&(cov>=threshold)
    dom=cohort_env&ok
    report={"species":n,"coverage_threshold":threshold,"native_ge5_ge80":int(((rich>=5)&(cov>=.8)).sum()),"native_eligible":int(ok.sum()),"coverage_by_region":{}}
    use=[]
    for name in REGIONS:
        r=reg==name;c=r&dom;blocks=len({tuple(a//5) for a in rc[c]})
        s={"range_eligible":int((ok&r).sum()),"environment_complete":int(c.sum()),"blocks_5":blocks,"median_trait_coverage":float(np.median(cov[c])) if c.any() else None,"matched_species_in_complete_cells":int(np.any(m[:,c],axis=1).sum())}
        s["admitted"]=bool(c.sum()>=100 and blocks>=10)
        report["coverage_by_region"][name]=s
        if s["admitted"]:use.append(name)
    keep=dom&np.isin(reg,use);report["analysis_cells"]=int(keep.sum());report["admitted_regions"]=use
    if keep.sum()<1000 or len(use)<4:report["status"]="insufficient_support";return report
    p=m[:,keep].T.astype(float);p/=p.sum(1,keepdims=True);den=1-(p*p).sum(1)
    assert np.all(den>0)
    raw={"mass":np.log(tab.mass.to_numpy(float))[:,None],"diet":tab[COARSE].to_numpy(float),"stratum":np.eye(4)[[["A","Ar","G","S"].index(v) for v in tab.stratum]]}
    if tag=="wing_common":
        z=w.loc[tab.index,["AR","WL_N_m2"]].to_numpy(float);z[:,1]=np.log(z[:,1]);z=(z-z.mean(0))/z.std(0)
        raw["wing"]=z
    domain=list(raw);responses=[];resname=[];stats={}
    for k,z in raw.items():
        D=distance(z);E=expected(D,tab.index.tolist())
        a=np.sum((p@D)*p,axis=1)/den;e=np.sum((p@E)*p,axis=1)/den
        assert np.isfinite(a-e).all()
        responses.extend([a-e,a]);resname.extend([k+"_genus_residual",k+"_raw_MPD"])
        stats[k]={"mean_raw":float(a.mean()),"mean_genus_expectation":float(e.mean()),"residual_sd":float((a-e).std()),"raw_sd":float(a.std())}
    Y=np.column_stack(responses)
    A=np.c_[np.log(full[keep]),np.log(rich[keep]),cov[keep],np.abs(lat[keep]),clim[keep],np.log1p(veg[keep,0]),veg[keep,1],np.log1p(veg[keep,2]),vegcov[keep],veg[keep,3]]
    assert A.shape[1]==len(FEATURES) and np.isfinite(A).all() and np.isfinite(Y).all()
    report["response_order"]=resname;report["domain_summary"]=stats
    report["tests"]={f"spatial_{g}":score(A,Y,reg[keep],rc[keep],g) for g in (5,10)}
    report["tests"]["region_transfer"]=score(A,Y,reg[keep],rc[keep],5,True)
    report["domain_screens"]={}
    for j,k in enumerate(domain):
        i=2*j;v={}
        for nm,t in report["tests"].items():
            if t["status"]!="scored":v[nm]={"status":t["status"],"pass":False};continue
            b=t["mse"]["B"][i];gain=t["V_B"][i];vn=t["V_N"][i];nf=sum(f["V_B"][i]>0 for f in t["folds"])
            npb=t["positive_region_blocks"][i];nb=t["region_blocks"];relative=gain/b if b>1e-12 else None
            passed=bool(gain>0 and vn>0 and (nf>=4 if nm=="region_transfer" else nf>=4 and npb/nb>=.6))
            v[nm]={"status":"scored","gain":gain,"relative_gain":relative,"V_N":vn,"positive_folds":nf,"total_folds":len(t["folds"]),"positive_region_blocks":npb,"region_blocks":nb,"pass":passed}
        report["domain_screens"][k]={"by_test":v,"pass":all(x["pass"] for x in v.values())}
    ss=report["domain_screens"];st=ss["stratum"]
    report["stratum_strongest_all_tests"]=bool(st["pass"] and all(st["by_test"][test]["relative_gain"] is not None and all(ss[k]["by_test"][test].get("relative_gain") is not None and st["by_test"][test]["relative_gain"]>ss[k]["by_test"][test]["relative_gain"] for k in domain if k!="stratum") for test in report["tests"]))
    report["status"]="scored"
    return report
def main():
    out={"stage":"V7 global measured environment multidomain potential-assemblage FD","status":"START"}
    try:
        self_test()
        names,X,shape,crs,T=read_ranges(out);assert len(names)==1141
        w=wing(out);assert sum(n in w.index for n in names)==264
        a,b,c=acquire(out);tab=mapping(a,b,names,w,out)
        rc=np.array(np.unravel_index(np.arange(X.shape[1]),shape)).T;tx,ty=edges(T,shape)
        pj=Transformer.from_crs(crs,4326,always_xy=True)
        lon,lat=pj.transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        lat0=pj.transform(np.zeros(len(rc)),T.f+rc[:,0]*T.e)[1];lat1=pj.transform(np.zeros(len(rc)),T.f+(rc[:,0]+1)*T.e)[1]
        domain=(np.maximum(lat0,lat1)<=51.6)&(np.minimum(lat0,lat1)>=-51.6)
        reg=np.full(len(rc),"other",dtype="U24")
        for name,(l,h,bottom,t) in REGIONS.items():
            q=(lon>=l)&(lon<=h)&(lat>=bottom)&(lat<t);assert np.all(reg[q]=="other");reg[q]=name
        prior=json.loads((ROOT/"MACRO_FD_V5_MEASURED_STRUCTURE_RESULT.json").read_text())
        out["status"]="CLIMATE_DOWNLOAD";save(out)
        check_overlap();clim,climcov=climate(out,tx,ty)
        assert out["climate"]["sha256"]==prior["climate"]["sha256"] and out["climate"]["members"]==prior["climate"]["members"]
        out["status"]="CLIMATE_HASH_VERIFIED";save(out)
        veg,vegcov=gedi(out,tx,ty)
        assert out["GEDI"]["common_native_pixels"]==749456
        for k,v in out["GEDI"]["metrics"].items():assert v["sha256"]==prior["GEDI"]["metrics"][k]["sha256"]
        env=domain&(climcov>=.5)&(vegcov>=.5)&(veg[:,0]>5)&(veg[:,1]>=.3)&np.isfinite(clim).all(1)&np.isfinite(veg).all(1)
        full=X.sum(0)
        wm=np.array([n in w.index for n in names]);mt=X[wm].sum(0);cov=np.divide(mt,full,out=np.zeros_like(full,float),where=full>0)
        chk=env&(mt>=5)&(cov>=.2)
        for name in REGIONS:assert int((chk&(reg==name)).sum())==prior["coverage_by_region"][name]["woody_complete"]
        out["V5_environment_replay"]=True;out["environment_cells"]=int(env.sum());out["cohorts"]={}
        for tag,t in [("broad",tab),("broad_without_split",tab[tab.no_transfer]),("wing_common",tab.loc[tab.index.intersection(w.index)])]:
            out["status"]="COHORT_"+tag;save(out)
            out["cohorts"][tag]=cohort(tag,t,X,names,rc,reg,lat,env,clim,veg,vegcov,full,w,out)
        out["primary_screen"]=out["cohorts"]["broad"].get("stratum_strongest_all_tests",False)
        out["status"]="COMPLETE"
    except Exception as e:
        out["last_status"]=out["status"];out["status"]="STOP";out["error_type"]=type(e).__name__
        # Never include auth-bearing URLs from exceptions.
    save(out);print("GLOBAL_V7_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
