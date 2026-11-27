"""Continental macro-community FD V1: digest-verified existing archive; aggregate outputs only."""
import collections as C
import csv,hashlib,io,itertools,json,math,os,pathlib,zipfile
import requests
import numpy as np
import pandas as pd
from pathlib import Path
PINS=[
("environment",15012939978,"afca6bf11fe5a75d7638a49de73b2cba1874e75d8cb24ed3f65c28957f25650a","all_bat_species_cell_source_year_environment.csv.gz","85ad737229aa7b10720a8d5c8bd0ea389f63f908c37871c7ce46ae87c9bed1d6"),
("flags",15012136742,"053567fa0cc43993aec472a3c5bc966a2c6df5306767e66ff6d65f826a7cf900","source_cell_year_observation_flags.csv.gz","de971292065a8aee3491880adb00a5623efae61bc83b2bd2ae4d663b45edf0f0"),
("crosswalk",15005261316,"7ed2df73b812f51f6376590136c79fb5acf42b41395e4e3f68830fb66120b490","physical_trait_crosswalk.csv","43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"),
("physical",15004406365,"3866df0cc71e1e5556162d26f9a757b7f31b0edddc339c1105ba7bd47e197408","physical_wing_traits_original.csv","d3ebe7656a60b44933f4da1a8302ca800bed07e0864d557698bf322eb7b85f49")]
K=["cell_x","cell_y"];JOIN=["species","snapshot_species_key",*K,"dataset_key","year","license"]
ENV=["bio1","bio4","bio5","bio6","bio12","bio15",*[f"worldcover_class_{i}_fraction" for i in [10,20,30,40,50]],"GVSM_area_mean_RH98_m","R50"]
DOM=["combined","flight","size","sensory"]
FEATURES=["log_richness","log_fine_cells","log_species_cell","trait_coverage",*ENV[:-2],"height_mean","height_sd","R50_mean","R50_sd"]
def norm(x):return " ".join(str(x).split()).casefold()
def positive(x):
    try:
        x=float(x);return x if math.isfinite(x) and x>0 else np.nan
    except (TypeError,ValueError):return np.nan
def yes(x):
    s=x.astype(str).str.lower();assert s.isin(["true","false"]).all();return s.eq("true")
def source(out):
    repo=os.environ["GITHUB_REPOSITORY"];assert repo=="zuizui0223/batter"
    tok=os.environ["GH_TOKEN"];paths={};receipts={}
    for name,aid,zipsha,member,member_sha in PINS:
        p=Path("macro_inputs")/(name+".zip");p.parent.mkdir(exist_ok=True);h=hashlib.sha256();n=0
        with requests.get(f"https://api.github.com/repos/{repo}/actions/artifacts/{aid}/zip",headers={"Authorization":"Bearer "+tok,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"},stream=True,timeout=(20,90)) as r:
            if r.status_code!=200:raise RuntimeError(f"artifact {aid} HTTP {r.status_code}")
            with p.open("wb") as f:
                for b in r.iter_content(1024*1024):
                    n+=len(b)
                    if n>50_000_000:raise ValueError("archive budget")
                    h.update(b);f.write(b)
        assert h.hexdigest()==zipsha,name+" archive digest"
        with zipfile.ZipFile(p) as z:
            matches=[i for i in z.infolist() if Path(i.filename).name==member]
            assert len(matches)==1 and matches[0].file_size<150_000_000
            b=z.read(matches[0]);assert hashlib.sha256(b).hexdigest()==member_sha
        f=p.with_name(member);f.write_bytes(b);paths[name]=f;p.unlink()
        receipts[name]={"artifact":aid,"zip_sha256":zipsha,"member_sha256":member_sha,"archive_bytes":n}
        print("VERIFIED",name,aid,n,flush=True)
    out["sources"]=receipts
    return paths

def traits(path,cwpath,env,out):
    s=path.read_text(encoding="utf-8-sig")
    physical=list(csv.DictReader(io.StringIO(s),dialect=csv.Sniffer().sniff(s[:8192],delimiters=",;\t")))
    assert len(physical)==30
    raw=C.defaultdict(list)
    for r in physical:raw[norm(r["Latin names"])].append(r)
    cw=pd.read_csv(cwpath,dtype=str,keep_default_na=False)
    cw["name"]=cw.source_name.map(norm)
    good=cw[~cw.name.duplicated(keep=False)&~cw.species_key.duplicated(keep=False)]
    names=env[["species","snapshot_species_key"]].drop_duplicates().copy();names["name"]=names.species.map(norm)
    names=names[~names.name.duplicated(keep=False)&~names.snapshot_species_key.duplicated(keep=False)]
    rows=[];drop=C.Counter()
    for r in good.itertuples():
        if r.name not in set(names.name):continue
        if len(raw[r.name])!=1:drop["no_unique_raw"]+=1;continue
        a=raw[r.name][0]
        ar,wl,ma=positive(r.AR),positive(r.WL_N_m2),positive(r.body_mass_g)
        lo,hi,du=positive(a["Echolocation frequency minimum"]),positive(a["Echolocation frequency maximum"]),positive(a["Duration call average"])
        if not np.isclose(ar,positive(a["Aspect ratio"]),rtol=1e-8,atol=1e-10) or not np.isclose(wl,positive(a["Wingloading"]),rtol=1e-8,atol=1e-10):
            drop["raw_AR_WL_disagree"]+=1;continue
        if not np.isfinite([ar,wl,ma,lo,hi,du]).all() or lo>hi:drop["incomplete"]+=1;continue
        rows.append((r.name,r.source_name,r.species_key,ar,math.log(wl),math.log(ma),.5*(math.log(lo)+math.log(hi)),math.log(du)))
    cols=["name","source_name","legacy_key","AR","log_WL","log_mass","log_frequency","log_duration"]
    t=pd.DataFrame(rows,columns=cols).merge(names[["name","snapshot_species_key"]],on="name",validate="one_to_one").sort_values("snapshot_species_key").reset_index(drop=True)
    x=t[cols[3:]].to_numpy(float)
    assert len(t)>=10 and np.all(x.std(0)>0)
    z=(x-x.mean(0))/x.std(0);d=(z[:,None,:]-z[None,:,:])**2
    flight=d[:,:,:2].mean(2);size=d[:,:,2];sens=d[:,:,3:].mean(2)
    D=np.stack([(flight+size+sens)/3,flight,size,sens],axis=2)
    assert np.allclose(np.diagonal(D,axis1=0,axis2=1),0)
    out["trait_roster"]={"complete_taxa":len(t),"species":t.source_name.tolist(),"excluded":dict(drop),"uniform_pair_reference":(D.sum((0,1))/(len(t)*(len(t)-1))).tolist()}
    return dict(zip(t.snapshot_species_key,range(len(t)))),D

def mpd(ids,weights,D):
    p=np.asarray(weights,float);p/=p.sum()
    a=D[ids][:,ids]
    den=1-float(p@p)
    assert den>0
    r=np.einsum("i,ijd,j->d",p,a,p)/den
    assert np.all(r>=-1e-10) and abs(r[0]-np.mean(r[1:]))<1e-10
    return r

def unitize(f,ix,D,grain,pooled):
    d=f.copy();d["gx"]=d.cell_x//grain;d["gy"]=d.cell_y//grain;d["period"]=d.year.astype(int)//5
    if pooled:d["dataset_key"]="pooled"
    d=d.drop_duplicates(["snapshot_species_key",*K,"dataset_key","period"])
    u=[];reasons=C.Counter();alltax=set();obsn=0
    for (provider,period,gx,gy),q in d.groupby(["dataset_key","period","gx","gy"],sort=True):
        obsn+=1
        c=q[K+ENV].drop_duplicates()
        assert not c.duplicated(K).any()
        counts=q.groupby("snapshot_species_key").size()
        ok=counts.index.isin(ix)
        coverage=float(ok.mean());inc=float(counts[ok].sum()/counts.sum())
        if len(c)<5:reasons["fewer_than_5_fine_cells"]+=1;continue
        if ok.sum()<3:reasons["fewer_than_3_complete_species"]+=1;continue
        if min(coverage,inc)<.8:reasons["trait_coverage_below_80pct"]+=1;continue
        ids=[ix[i] for i in counts.index[ok]]
        alltax.update(ids);a=c[ENV].to_numpy(float)
        feat=np.r_[math.log(len(counts)),math.log(len(c)),math.log(len(q)),coverage,a[:,:-2].mean(0),a[:,-2].mean(),a[:,-2].std(),a[:,-1].mean(),a[:,-1].std()]
        assert len(feat)==len(FEATURES)
        b=(int(gx)*grain//200,int(gy)*grain//200)
        u.append(dict(provider=provider,period=int(period),gx=int(gx),gy=int(gy),block=b,feat=feat,equal=mpd(ids,np.ones(len(ids)),D),incidence=mpd(ids,counts[ok].to_numpy(),D),richness=len(counts),fine=len(c),incidences=len(q),coverage=coverage,inc_coverage=inc))
    stat={"candidate_units":obsn,"eligible_units":len(u),"excluded":dict(reasons),"taxa":len(alltax),"providers":len({v["provider"] for v in u}),"blocks":len({v["block"] for v in u})}
    if u:
        stat["median_support"]={k:float(np.median([v[k] for v in u])) for k in ["richness","fine","incidences","coverage","inc_coverage"]}
        stat["trait_mpd_means"]={m:np.mean([v[m] for v in u],axis=0).tolist() for m in ["equal","incidence"]}
    return u,stat

def shaorder(v):return sorted(v,key=lambda b:hashlib.sha256(str(b).encode()).hexdigest())
def fits(x,y,w,tr,te):
    z=x[tr];ytr=y[tr];v=w[tr].copy();v/=v.sum()
    scale=np.sqrt(np.average(z*z,axis=0,weights=v));active=scale>1e-12;scale[~active]=1
    z=z/scale;t=x[te]/scale;z[:,~active]=0;t[:,~active]=0
    result=[np.zeros((int(te.sum()),y.shape[1]))]
    for n in [x.shape[1]-2,x.shape[1]]:
        Z=z[:,:n];T=t[:,:n]
        coef=np.linalg.solve(Z.T@(v[:,None]*Z)+.1*np.eye(n),Z.T@(v[:,None]*ytr))
        grad=Z.T@(v[:,None]*(Z@coef-ytr))+.1*coef
        assert np.max(np.abs(grad))<1e-8
        result.append(T@coef)
    return np.stack([(p-y[te])**2 for p in result],axis=1)

def compare(u,stat,mode,strict):
    grouped=C.defaultdict(list)
    for v in u:grouped[(v["provider"],v["period"],v["block"])].append(v)
    xx=[];yy=[];bk=[];src=[];grp=[]
    for k,vs in sorted(grouped.items()):
        for a,b in itertools.combinations(sorted(vs,key=lambda v:(v["gx"],v["gy"])),2):
            xx.append(a["feat"]-b["feat"]);yy.append(a[mode]-b[mode]);bk.append(k[2]);src.append(k[0]);grp.append(k)
    nb=len(set(bk));npair=len(xx);ns=len(set(src))
    ret={"pairs":npair,"blocks":nb,"providers":ns,"strata":len(set(grp))}
    if stat["taxa"]<10 or stat["eligible_units"]<50 or npair<100 or ns<10 or nb<20:return {**ret,"status":"insufficient_support"}
    x=np.asarray(xx);y=np.asarray(yy)
    blocks=shaorder(set(bk));sources=shaorder(set(src));bi={v:i for i,v in enumerate(blocks)};si={v:i for i,v in enumerate(sources)}
    b=np.array([bi[v] for v in bk]);s=np.array([si[v] for v in src]);gkeys=sorted(set(grp));gi={k:i for i,k in enumerate(gkeys)};g=np.array([gi[k] for k in grp])
    gb=np.array([bi[k[2]] for k in gkeys]);bf=b%5;sf=s%5
    def weights(mask):
        cnt=np.bincount(g[mask],minlength=len(gkeys));num=np.bincount(gb[cnt>0],minlength=nb)
        r=np.zeros(npair);r[mask]=1/(cnt[g[mask]]*num[b[mask]])
        assert abs(r.sum()-len(np.unique(b[mask])))<1e-8
        return r
    sc=np.full((npair,3,4),np.nan);splits=[]
    for k in range(5):
        for j in (range(5) if strict else [None]):
            tr=bf!=k;te=bf==k
            if strict:tr&=sf!=j;te&=sf==j
            nt,ne=len(np.unique(b[tr])),len(np.unique(b[te]))
            valid=(nt>=10 and ne>=2 and tr.sum()>=10 and te.sum()>=3) if strict else (nt>=15 and ne>=3)
            if not valid:
                splits.append({"fold":k,"source_fold":j,"status":"support_stop","train_blocks":nt,"test_blocks":ne,"test_pairs":int(te.sum())});continue
            assert not set(b[tr])&set(b[te]) and (not strict or not set(s[tr])&set(s[te]))
            sc[te]=fits(x,y,weights(tr),tr,te)
            w=weights(te)[te];v=np.average(sc[te],axis=0,weights=w)
            splits.append({"fold":k,"source_fold":j,"status":"scored","train_blocks":nt,"test_blocks":ne,"test_pairs":int(te.sum()),"mse":v.tolist(),"V_B_gain":(v[1]-v[2]).tolist()})
    keep=np.isfinite(sc).all((1,2));ret["splits"]=splits;ret["scored_pairs"]=int(keep.sum());ret["coverage"]=float(keep.mean())
    if not keep.any():return {**ret,"status":"no_scored_support"}
    w=weights(keep);use=sorted(set(b[keep]));scores=np.array([np.average(sc[keep&(b==k)],axis=0,weights=w[keep&(b==k)]) for k in use])
    mean=scores.mean(0);ret["mse"]=dict(zip(["N","B","V"],mean.tolist()))
    ret["scored_blocks"]=len(use);ret["scored_providers"]=len(set(s[keep]))
    ret["gains"]={}
    for a,c,n in [(0,1,"B-N"),(1,2,"V-B"),(0,2,"V-N")]:
        delta=scores[:,a]-scores[:,c];om=(delta.sum(0)-delta)/(len(delta)-1)
        ret["gains"][n]={"mean":delta.mean(0).tolist(),"positive_blocks":(delta>0).sum(0).tolist(),"delete_one_block_range":[om.min(0).tolist(),om.max(0).tolist()]}
    g1=ret["gains"]["V-B"];g2=ret["gains"]["V-N"];ret["positive_V_B_splits"]=sum(v["V_B_gain"][0]>0 for v in splits if v["status"]=="scored")
    ret["status"]="scored"
    ret["screen"]=bool((ret["coverage"]>=.7 and len(use)>=15 and ret["scored_providers"]>=10 and g1["mean"][0]>0 and g2["mean"][0]>0) if strict else (ret["coverage"]==1 and g1["mean"][0]>0 and g1["positive_blocks"][0]/len(use)>=.6 and ret["positive_V_B_splits"]>=4 and g1["delete_one_block_range"][0][0]>0 and g2["mean"][0]>0))
    return ret

def main():
    out={"stage":"source-conditional macro observed-assemblage trait dispersion","metric_order":DOM,"features":FEATURES}
    try:
        p=source(out)
        dtype={k:str for k in JOIN if k not in K}
        e=pd.read_csv(p["environment"],dtype=dtype,keep_default_na=False,low_memory=False);a=pd.read_csv(p["flags"],dtype=dtype,keep_default_na=False,low_memory=False)
        assert e.records.sum()==a.records.sum()==219960 and len(e[K].drop_duplicates())==11006 and e.snapshot_species_key.nunique()==39
        assert not e.duplicated(JOIN).any() and not a.duplicated(JOIN).any()
        assert int(e.loc[yes(e.forest_profile_support),"records"].sum())==56847
        ix,D=traits(p["physical"],p["crosswalk"],e,out)
        # analytic richness-conditioned reference check: each equal-weight sample of size 2 is exactly its pair distance.
        assert np.allclose(mpd([0,1],[1,1],D),D[0,1])
        f=e.merge(a[JOIN+["records","flag_explicit_captive","flag_roost_context"]].rename(columns={"records":"audit_records"}),on=JOIN,how="outer",validate="one_to_one",indicator=True)
        assert f._merge.eq("both").all() and f.records.eq(f.audit_records).all() and f.flag_explicit_captive.sum()==0 and f.flag_roost_context.sum()==684
        f["clean_records"]=f.records-f.flag_roost_context;assert f.clean_records.ge(0).all()
        m=f.clean_records.gt(0)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")&f.license.isin(["CC_BY_4_0","CC0_1_0","CC_BY_NC_4_0"])&yes(f.forest_profile_support)
        f=f[m].copy();south=yes(f.training_latitude_support)&~yes(f.north_extrapolation)&~yes(f.latitude_boundary_cell)
        f[ENV]=f[ENV].apply(pd.to_numeric,errors="raise");assert np.isfinite(f[ENV].to_numpy()).all()
        out["source_support"]={"raw_records":219960,"raw_cells":11006,"raw_taxa":39,"forest_records":56847,"forest_cells":6775,"south_rows":int(south.sum()),"south_clean_records":int(f.loc[south,"clean_records"].sum()),"south_cells":len(f.loc[south,K].drop_duplicates()),"south_taxa":int(f.loc[south,"snapshot_species_key"].nunique()),"north_rows":int(yes(f.north_extrapolation).sum()),"north_cells":len(f.loc[yes(f.north_extrapolation),K].drop_duplicates())}
        f=f[south].copy()
        out["grains"]={}
        for grain in [50,100]:
            u,stat=unitize(f,ix,D,grain,False);_,pool=unitize(f,ix,D,grain,True)
            gg={"provider_period_units":stat,"pooled_provider_census":pool,"fits":{}}
            for mode in ["equal","incidence"]:
                for strict in [False,True]:
                    key=mode+("_strict" if strict else "_spatial")
                    gg["fits"][key]=compare(u,stat,mode,strict)
            out["grains"][str(grain)]=gg
        out["primary_screen"]=all(out["grains"][str(g)]["fits"][m].get("screen",False) for g in [50,100] for m in ["equal_spatial","equal_strict"])
        out["status"]="completed"
    except Exception as exc:
        out.update(status="stopped",error_type=type(exc).__name__,error="transport error" if isinstance(exc,requests.RequestException) else str(exc)[:180])
    Path("macro_fd_v1_result.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("MACRO_FD_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
