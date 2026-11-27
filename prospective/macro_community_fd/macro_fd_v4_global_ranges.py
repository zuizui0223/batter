"""V4 global expert range and wing-trait macroecology. Aggregate-only outputs."""
import collections as C,hashlib,io,itertools,json,math,os,subprocess,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import requests,rasterio
from pyproj import CRS,Transformer,Geod
from scipy.spatial import cKDTree
from macro_fd_v2_geography import expected_distance,permutations

PIN="db6f0a5584ef5b0d899770d231476c6589cb16b8"
META="Data/Ranges/Spatial_metadata.csv"
ZIP="fa45d435204439bd4600143540bc6960e0b814405cec938c3275c19ebbd2fb09"
TRAIT="99a19c169e18a0bafa4a518b7f844b56d2fe846cac13d5c035f4eae562a74c7b"
REGIONS={"Europe":(-12,40,35,72),"North_America":(-170,-50,15,70),"East_Asia":(73,146,15,60),"South_America":(-90,-30,-60,15),"Africa":(-20,52,-35,35),"Australasia":(110,180,-50,-10)}
METRICS=["combined","flight","size"]
GEOD=Geod(ellps="WGS84")
SEED=20261127
NREP=10000
def save(out):
    Path("macro_fd_v4_result.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V4_REPORT="+json.dumps(out,allow_nan=False),flush=True)
def git(p,*a):
    return subprocess.check_output(["git","-C",str(p),*a],timeout=45)
def blob(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def wing(out):
    repo=os.environ["GITHUB_REPOSITORY"];assert repo=="zuizui0223/batter"
    with requests.get(f"https://api.github.com/repos/{repo}/actions/artifacts/15069663941/zip",headers={"Authorization":"Bearer "+os.environ["GH_TOKEN"],"Accept":"application/vnd.github+json"},stream=True,timeout=(20,90)) as r:
        if r.status_code!=200:raise RuntimeError(f"trait artifact HTTP {r.status_code}")
        b=bytearray()
        for x in r.iter_content(1024*1024):
            b.extend(x)
            if len(b)>2*1024**2:raise ValueError("trait archive budget")
    assert hashlib.sha256(b).hexdigest()==ZIP
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        f=[i for i in z.infolist() if Path(i.filename).name=="primary_LSA_physical.csv"];assert len(f)==1 and f[0].file_size<2*1024**2
        raw=z.read(f[0]);assert hashlib.sha256(raw).hexdigest()==TRAIT
    w=pd.read_csv(io.BytesIO(raw));n="scientificName.iucn"
    assert len(w)==280 and not w[n].duplicated().any()
    w["name"]=w[n].str.strip().str.replace(r"\s+","_",regex=True).str.casefold()
    assert not w.name.duplicated().any()
    assert np.isfinite(w[["AR","WL_N_m2","mass_g_physical"]]).all().all() and (w[["AR","WL_N_m2","mass_g_physical"]]>0).all().all()
    out["trait_source"]={"artifact":15069663941,"zip_sha256":ZIP,"member_sha256":TRAIT,"species":len(w)}
    return w.set_index("name")
def read_ranges(out):
    p=Path("phylacine");assert git(p,"rev-parse","HEAD").decode().strip()==PIN
    tree={}
    for s in git(p,"ls-tree","-r","HEAD","Data/Ranges/Current",META).decode().splitlines():
        head,path=s.split("\t",1);mode,typ,sha=head.split()
        if typ=="blob":tree[path]=sha
    assert len([k for k in tree if k.startswith("Data/Ranges/Current/")])==5831
    def verified(k):
        b=(p/k).read_bytes()
        assert blob(b)==tree[k],"Git blob mismatch"
        return b
    mb=verified(META);assert tree[META]=="f2538374945f602f7c148d1a534be491895cd6e1"
    d=pd.read_csv(io.BytesIO(mb));assert len(d)==5831 and not d["Binomial.1.2"].duplicated().any()
    d=d[d["Order.1.2"]=="Chiroptera"].copy()
    d["name"]=d["Binomial.1.2"].str.strip().str.casefold()
    assert not d.name.duplicated().any()
    names=[];arrays=[];shape=None;crs=None;transform=None;countstat=C.Counter();mismatch=[];npositive=0
    for row in d[["Binomial.1.2","name","Number.Cells.Current.Range"]].itertuples(index=False,name=None):
        rawname,name,expected=row
        fn="Data/Ranges/Current/"+rawname+".tif"
        b=verified(fn)
        with rasterio.MemoryFile(b) as m:
            with m.open() as ds:
                assert ds.count==1 and ds.crs is not None
                if shape is None:
                    shape=ds.shape;crs=ds.crs;transform=ds.transform
                    cc=CRS.from_user_input(crs)
                    assert cc.is_projected and all(abs(a.unit_conversion_factor-1)<1e-6 for a in cc.axis_info[:2])
                    assert abs(transform.a-96500)<1000 and abs(transform.e+96500)<1000 and abs(transform.b)<1e-8 and abs(transform.d)<1e-8
                assert ds.shape==shape and ds.crs==crs and ds.transform.almost_equals(transform,precision=1e-6)
                a=ds.read(1,masked=True);v=a.compressed()
                assert np.isfinite(v).all() and np.isin(v,[0,1]).all(),"nonbinary range"
                mask=np.asarray(a.filled(0)==1);n=int(mask.sum())
                countstat["verified_maps"]+=1;npositive+=int(n>0)
                if not np.isfinite(expected) or n!=int(expected):
                    mismatch.append({"species":rawname,"raster_count":n,"metadata_count":int(expected) if np.isfinite(expected) else None});continue
                countstat["exact_count"]+=1
                if n==0:countstat["zero_maps"]+=1;continue
                names.append(name);arrays.append(mask.ravel())
    out["range_source"]={"commit":PIN,"metadata_blob":tree[META],"all_current_maps":5831,"chiroptera_metadata":len(d),"positive_maps_before_count_gate":npositive,"verified_maps":countstat["verified_maps"],"exact_count":countstat["exact_count"],"zero_maps":countstat["zero_maps"],"count_mismatches":mismatch,"exact_positive_maps":len(names),"grid_shape":list(shape),"pixel_m":[float(transform.a),float(-transform.e)],"crs":str(crs)}
    assert npositive>=1000 and countstat["exact_count"]/len(d)>=.95
    X=np.asarray(arrays,bool)
    assert X.shape==(len(names),shape[0]*shape[1])
    return names,X,shape,crs,transform
def metric(raw):
    Z=raw.copy();Z[:,1:]=np.log(Z[:,1:])
    Z=(Z-Z.mean(0))/Z.std(0)
    sq=(Z[:,None,:]-Z[None,:,:])**2
    flight=sq[:,:,:2].mean(2);size=sq[:,:,2]
    return Z,np.stack([(flight+size)/2,flight,size],axis=-1)
def domain(a):
    flight=a[..., :2].mean(-1);size=a[...,2];return np.stack([(flight+size)/2,flight,size],axis=-1)
def weighted_pair(p,q,Z):
    d=p-q;t=.5*np.abs(d).sum(1)
    assert np.all(t>1e-12)
    L=np.maximum(d,0)/t[:,None];G=np.maximum(-d,0)/t[:,None]
    assert np.allclose(L.sum(1),1) and np.allclose(G.sum(1),1) and np.allclose((L*G).sum(1),0)
    R=domain(L@(Z*Z)+G@(Z*Z)-2*(L@Z)*(G@Z))
    C0=domain(((L-G)@Z)**2);raw=domain((d@Z)**2)
    assert np.allclose(raw,t[:,None]**2*C0)
    return L,G,t,R,C0,raw
def evalmatrix(M,D):
    return np.einsum("ij,ijc->c",M,D)
def summarize_region(P,rc,lon,lat,Z,D,E,seed):
    # Enumerate spherical candidates with generous minimum Earth radius and exact geodesic distances.
    latr=np.radians(lat);lonr=np.radians(lon);xyz=np.c_[np.cos(latr)*np.cos(lonr),np.cos(latr)*np.sin(lonr),np.sin(latr)]
    cand=cKDTree(xyz).query_pairs(2*np.sin(1500/(2*6335)),output_type="ndarray")
    _,_,dist=GEOD.inv(lon[cand[:,0]],lat[cand[:,0]],lon[cand[:,1]],lat[cand[:,1]])
    dist=dist/1000;good=(dist>=100)&(dist<1500)
    cand=cand[good];dist=dist[good]
    # exact set equality for zero turnover (p is uniform). Avoid treating equal sets as positive.
    codes=[np.packbits(a>0).tobytes() for a in P]
    z=np.array([codes[i]==codes[j] for i,j in cand])
    groups=C.defaultdict(list);census=C.Counter()
    block=[tuple(a//5) for a in rc]
    for k,(i,j) in enumerate(cand):
        cls="near" if dist[k]<500 else "far"
        census[cls+"_all"]+=1
        if z[k]:census[cls+"_zero"]+=1;continue
        a,b=sorted((block[i],block[j]));groups[cls,a,b].append((i,j))
    rng=np.random.default_rng(seed);matrices={};report={"pair_census":dict(census),"classes":{}}
    n=P.shape[1]
    for cls in ["near","far"]:
        keys=sorted(k for k in groups if k[0]==cls);nb=len(keys);accW=np.zeros((n,n));accV=accW.copy();values=[];residual=[];ns=0
        for key in keys:
            v=np.asarray(groups[key],int)
            if len(v)>64:v=v[np.sort(rng.choice(len(v),64,replace=False))]
            ns+=len(v)
            l,g,t,r,c,raw=weighted_pair(P[v[:,0]],P[v[:,1]],Z)
            w=(l.T@g+g.T@l)/(2*len(v));dd=l-g;vv=-(dd.T@dd)/(2*len(v))
            assert abs(w.sum()-1)<1e-10 and abs(vv.sum())<1e-10
            assert np.allclose(evalmatrix(w,D),r.mean(0)) and np.allclose(evalmatrix(vv,D),c.mean(0))
            accW+=w;accV+=vv
            values.append(np.r_[t.mean(),r.mean(0),c.mean(0),raw.mean(0)])
            residual.append(np.r_[evalmatrix(w,D-E),evalmatrix(vv,D-E)])
        st={"blockpairs":nb,"sampled_positive_pairs":ns,"positive_pairs":census[cls+"_all"]-census[cls+"_zero"]}
        if nb<30 or ns<100:st["status"]="insufficient_support";report["classes"][cls]=st;continue
        v=np.asarray(values);res=np.asarray(residual);W=accW/nb;V=accV/nb
        assert np.allclose(evalmatrix(W,D),v.mean(0)[1:4]) and np.allclose(evalmatrix(V,D),v.mean(0)[4:7])
        st.update(status="admitted",mean=v.mean(0).tolist(),genus_residual_R_C=res.mean(0).tolist(),negative_blockpair_residual=(res<0).sum(0).tolist())
        matrices[cls]=(W,V);report["classes"][cls]=st
    if len(matrices)==2:
        a=report["classes"]["near"];b=report["classes"]["far"]
        report["far_minus_near"]=(np.asarray(b["mean"])-a["mean"]).tolist()
        report["genus_residual_far_minus_near"]=(np.asarray(b["genus_residual_R_C"])-a["genus_residual_R_C"]).tolist()
    return report,matrices
def null(cases,Z,D,groups):
    if not cases:return {}
    E=expected_distance(D,groups);n=len(Z);pp=permutations(groups,n)
    out={}
    # Linear squared-distance identity avoids materializing n*n distance matrices for every draw.
    zz=Z[pp]
    for name,M in cases:
        obs=evalmatrix(M,D);ex=evalmatrix(M,E);sims=[]
        rows=M.sum(1)
        for i in range(0,NREP,256):
            a=zz[i:i+256]
            v=np.empty((len(a),3))
            for j in range(3):
                x=a[:,:,j]
                v[:,j]=2*((x*x)@rows-np.sum((x@M)*x,axis=1))
            sims.append(domain(v))
        v=np.concatenate(sims)
        sd=v.std(0);mean=v.mean(0)
        assert np.all(np.abs(mean-ex)<=7*sd/np.sqrt(NREP)+1e-8)
        assert np.allclose(domain(2*((Z*Z).T@rows-np.sum(Z*(M@Z),axis=0))),obs)
        out[name]={"observed":obs.tolist(),"analytic_expectation":ex.tolist(),"excess":(obs-ex).tolist(),"null_mean":mean.tolist(),"q025":np.quantile(v,.025,axis=0).tolist(),"q975":np.quantile(v,.975,axis=0).tolist(),"rank_le":np.mean(v<=obs+1e-12,axis=0).tolist()}
    return out
def main():
    out={"stage":"global expert-range potential assemblages; matched wing-trait subset","metric_order":METRICS,"pair_mean_order":["T"]+["R_"+k for k in METRICS]+["C_"+k for k in METRICS]+["raw_C_"+k for k in METRICS],"seed":SEED}
    try:
        w=wing(out);names,X,shape,crs,T=read_ranges(out)
        matched=[i for i,n in enumerate(names) if n in w.index]
        assert len(matched)>=150
        nm=[names[i] for i in matched];raw=w.loc[nm,["AR","WL_N_m2","mass_g_physical"]].to_numpy(float)
        Z,D=metric(raw);assert np.isfinite(Z).all()
        g=C.defaultdict(list)
        for i,n in enumerate(nm):g[n.split("_")[0]].append(i)
        groups=list(g.values());E=expected_distance(D,groups)
        count=X.sum(0);match=X[matched].sum(0);occupied=count>0
        cover=np.divide(match,count,out=np.zeros_like(count,float),where=occupied)
        eligible=(match>=5)&(cover>=.2)
        out["global_support"]={"verified_positive_bat_maps":len(names),"matched_trait_species":len(matched),"genera":len(groups),"occupied_cells":int(occupied.sum()),"cells_with_any_traits":int((match>0).sum()),"eligible_cells":int(eligible.sum()),"median_trait_coverage_occupied":float(np.median(cover[occupied])),"median_trait_coverage_eligible":float(np.median(cover[eligible])) if eligible.any() else None,"median_bat_richness_occupied":float(np.median(count[occupied]))}
        rc=np.array(np.unravel_index(np.arange(count.size),shape)).T
        x=T.c+(rc[:,1]+.5)*T.a;y=T.f+(rc[:,0]+.5)*T.e
        lon,lat=Transformer.from_crs(crs,4326,always_xy=True).transform(x,y)
        lon=np.asarray(lon);lat=np.asarray(lat)
        # All boxes nonoverlapping in their specified coordinate support.
        used=np.zeros(len(lon),bool);report={};cases=[];diffs=[]
        for j,(name,(lo,hi,bot,top)) in enumerate(REGIONS.items()):
            region=(lon>=lo)&(lon<=hi)&(lat>=bot)&(lat<top);assert not np.any(used&region);used|=region
            rr=occupied&region;q=eligible&region
            full=int(np.any(X[:,rr],axis=1).sum());mt=int(np.any(X[matched][:,rr],axis=1).sum());nt=int(np.any(X[matched][:,q],axis=1).sum())
            s={"occupied_cells":int(rr.sum()),"eligible_cells":int(q.sum()),"full_species":full,"matched_species":mt,"eligible_matched_species":nt,"median_coverage":float(np.median(cover[rr])) if rr.any() else None,"eligible_median_coverage":float(np.median(cover[q])) if q.any() else None,"blocks":len({tuple(a//5) for a in rc[q]})}
            report[name]=s
            if q.sum()<100 or nt<20 or s["blocks"]<10:s["status"]="insufficient_support";continue
            P=X[matched][:,q].T.astype(float);P/=P.sum(1,keepdims=True)
            m,mat=summarize_region(P,rc[q],lon[q],lat[q],Z,D,E,SEED+j)
            s.update(m)
            if len(mat)!=2:s["status"]="insufficient_pair_support";continue
            s["status"]="admitted"
            for cls in ["near","far"]:
                for k,M in zip(["R","C"],mat[cls]):cases.append((name+"_"+cls+"_"+k,M))
            delta=mat["far"][1]-mat["near"][1]
            cases.append((name+"_far_minus_near_C",delta));diffs.append(delta)
        out["regions"]=report
        if diffs:cases.append(("region_equal_far_minus_near_C",np.mean(diffs,axis=0)))
        out["genus_null"]=null(cases,Z,D,groups);out["unrestricted_null"]=null(cases,Z,D,[list(range(len(Z)))])
        good=[k for k,s in report.items() if s["status"]=="admitted" and s["far_minus_near"][5]<0 and s["genus_residual_far_minus_near"][4]<0]
        # C flight: pair vector index 5; residual R3 then C3 index 4.
        rank=out["genus_null"].get("region_equal_far_minus_near_C",{}).get("rank_le",[None]*3)[1]
        out["primary_screen"]={"supporting_regions":good,"region_equal_genus_rank":rank,"pass":bool(len(good)>=4 and "Europe" in good and bool(set(good)&{"North_America","East_Asia"}) and rank is not None and rank<=.025)}
        out["status"]="completed"
    except Exception as e:
        out.update(status="stopped",error_type=type(e).__name__,error="transport error" if isinstance(e,requests.RequestException) else str(e)[:180])
    save(out)
if __name__=="__main__":main()
