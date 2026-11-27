"""V3 continental functional replacement along geographic distances; aggregate output only."""
import collections as C
import itertools,json,math
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from pyproj import Transformer,Geod
from macro_fd_v1 import source,traits,yes,K,JOIN,DOM
from macro_fd_v2_geography import null_results

GEOD=Geod(ellps="WGS84")
INV=Transformer.from_crs(6933,4326,always_xy=True)
BINS=("0_250","250_500","500_1000","1000_plus")
def units(f,ix,grain):
    d=f[["snapshot_species_key","dataset_key","year",*K]].copy()
    d["period"]=d.year.astype(int)//5
    d=d.drop_duplicates(["snapshot_species_key",*K,"dataset_key","period"])
    d["gx"]=d.cell_x//grain;d["gy"]=d.cell_y//grain
    out=[];taxa=set();drop=C.Counter();nc=0
    for (provider,period,gx,gy),q in d.groupby(["dataset_key","period","gx","gy"],sort=True):
        nc+=1
        nf=len(q[K].drop_duplicates());cnt=q.groupby("snapshot_species_key").size();ok=cnt.index.isin(ix)
        if nf<5:drop["fine_cells_lt5"]+=1;continue
        if ok.sum()<3:drop["complete_taxa_lt3"]+=1;continue
        if min(ok.mean(),cnt[ok].sum()/cnt.sum())<.8:drop["coverage_lt80pct"]+=1;continue
        ids=np.array([ix[k] for k in cnt.index[ok]])
        taxa.update(ids.tolist());p=np.zeros(len(ix));w=p.copy()
        p[ids]=1/len(ids);w[ids]=cnt[ok].to_numpy(float)/cnt[ok].sum()
        cell=(int(gx),int(gy));block=(cell[0]*grain//200,cell[1]*grain//200)
        xy=INV.transform((cell[0]+.5)*grain*1000,(cell[1]+.5)*grain*1000)
        assert np.isfinite(xy).all() and -90<=xy[1]<=90
        out.append(dict(provider=provider,period=int(period),cell=cell,block=block,xy=xy,equal=p,incidence=w))
    return out,{"candidate":nc,"eligible":len(out),"taxa":len(taxa),"providers":len({r["provider"] for r in out}),"blocks":len({r["block"] for r in out}),"excluded":dict(drop)}

def pairs(u,D,mode):
    g=C.defaultdict(list)
    for v in u:g[v["provider"],v["period"]].append(v)
    rows=[]
    for key,values in sorted(g.items()):
        for a,b in itertools.combinations(sorted(values,key=lambda v:v["cell"]),2):
            assert a["cell"]!=b["cell"]
            _,_,meters=GEOD.inv(*a["xy"],*b["xy"])
            km=meters/1000
            db=BINS[int(np.searchsorted([250,500,1000],km,side="right"))]
            ep=tuple(sorted((a["block"],b["block"])))
            p,q=a[mode],b[mode];delta=p-q;t=float(np.abs(delta).sum()/2)
            assert abs(delta.sum())<1e-10 and 0<=t<=1+1e-10
            r=dict(stratum=key,blockpair=ep,bin=db,km=float(km),T=t)
            if t>1e-12:
                l=np.maximum(delta,0)/t;h=np.maximum(-delta,0)/t
                assert abs(l.sum()-1)<1e-10 and abs(h.sum()-1)<1e-10 and abs(l@h)<1e-10
                W=(np.outer(l,h)+np.outer(h,l))/2
                V=-.5*np.outer(l-h,l-h)
                R=np.einsum("ij,ijc->c",W,D);cent=np.einsum("ij,ijc->c",V,D)
                ql=np.einsum("i,ijc,j->c",l,D,l);qh=np.einsum("i,ijc,j->c",h,D,h)
                raw=-.5*np.einsum("i,ijc,j->c",delta,D,delta)
                assert abs(W.sum()-1)<1e-10 and np.allclose(np.diag(W),0) and np.allclose(W,W.T)
                assert np.allclose(cent,R-(ql+qh)/2) and np.allclose(raw,t*t*cent) and min(cent)>=-1e-9
                r.update(R=R,C=cent,raw=raw,W=W,V=V)
            else:
                r["raw"]=np.zeros(4)
            rows.append(r)
    return rows

def hierarchy(rows,keyfirst,keysecond,get):
    groups=C.defaultdict(list)
    for r in rows:groups[keyfirst(r),keysecond(r)].append(get(r))
    outer=C.defaultdict(list)
    for (a,b),v in groups.items():outer[a].append(np.mean(v,axis=0))
    values=np.asarray([np.mean(v,axis=0) for _,v in sorted(outer.items())])
    return values

def support(rows):
    pos=[r for r in rows if "W" in r]
    blocks={b for r in pos for b in r["blockpair"]}
    return dict(pairs=len(rows),positive_pairs=len(pos),zero_pairs=len(rows)-len(pos),providers=len({r["stratum"][0] for r in pos}),strata=len({r["stratum"] for r in pos}),blockpairs=len({r["blockpair"] for r in pos}),individual_blocks=len(blocks))

def aggregate(rows,tag,main,ntaxa):
    stat=support(rows);p=[r for r in rows if "W" in r]
    if rows:
        vv=hierarchy(rows,lambda r:r["blockpair"],lambda r:r["stratum"],lambda r:np.r_[r["T"],r["km"],r["raw"]])
        stat["all_pair_mean_T_km_raw_centroid"]=vv.mean(0).tolist()
    gate=(stat["positive_pairs"]>=100 and stat["providers"]>=15 and stat["blockpairs"]>=20 and stat["individual_blocks"]>=15 and ntaxa>=10) if main else (stat["positive_pairs"]>=20 and stat["providers"]>=3 and stat["blockpairs"]>=5)
    stat["status"]="admitted" if gate else "insufficient_support"
    if not gate:return stat,[]
    # Identical hierarchy for each positive-pair endpoint.
    W=hierarchy(p,lambda r:r["blockpair"],lambda r:r["stratum"],lambda r:np.stack([r["W"],r["V"]]))
    assert np.allclose(W[:,0].sum((1,2)),1)
    assert np.allclose(W[:,1].sum((1,2)),0,atol=1e-9)
    stats=hierarchy(p,lambda r:r["blockpair"],lambda r:r["stratum"],lambda r:np.r_[r["T"],r["R"],r["C"]])
    stat["conditional_positive_mean_T_R_C"]=stats.mean(0).tolist()
    return stat,[(tag+"_R",W[:,0].mean(0),W[:,0]),(tag+"_C",W[:,1].mean(0),W[:,1])]

def gradient(rows):
    groups=C.defaultdict(lambda:C.defaultdict(list))
    for r in rows:
        if "W" in r:groups[r["stratum"]]["near" if r["km"]<500 else "far"].append(r)
    common={k:v for k,v in groups.items() if set(v)=={"near","far"}}
    near=[r for v in common.values() for r in v["near"]];far=[r for v in common.values() for r in v["far"]]
    ns,fs=support(near),support(far)
    ret={"common_strata":len(common),"providers":len({k[0] for k in common}),"near":ns,"far":fs}
    if len(common)<5 or ret["providers"]<3 or min(ns["positive_pairs"],fs["positive_pairs"])<20 or min(ns["blockpairs"],fs["blockpairs"])<10:
        return {**ret,"status":"insufficient_support"}
    nearv=[];farv=[]
    for k,v in sorted(common.items()):
        def av(a):
            return hierarchy(a,lambda r:r["blockpair"],lambda r:r["stratum"],lambda r:np.r_[r["T"],r["raw"],r["R"],r["C"]]).mean(0)
        nearv.append(av(v["near"]));farv.append(av(v["far"]))
    a,b=np.array(nearv),np.array(farv);d=b-a;om=(d.sum(0)-d)/(len(d)-1)
    ret.update(status="descriptive",order=["T"]+[f"raw_C_{k}" for k in DOM]+[f"R_{k}" for k in DOM]+[f"C_{k}" for k in DOM],near_mean=a.mean(0).tolist(),far_mean=b.mean(0).tolist(),far_minus_near=d.mean(0).tolist(),positive_strata=(d>0).sum(0).tolist(),delete_one_stratum_range=[om.min(0).tolist(),om.max(0).tolist()])
    return ret

def main():
    out={"stage":"continental recorded species replacement, functional gap conditional on observed turnover","metric_order":DOM+["sensory_minus_flight"],"seed":20261127,"null_draws":10000}
    try:
        p=source(out);dtype={k:str for k in JOIN if k not in K}
        e=pd.read_csv(p["environment"],dtype=dtype,keep_default_na=False,low_memory=False)
        a=pd.read_csv(p["flags"],dtype=dtype,keep_default_na=False,low_memory=False)
        assert e.records.sum()==a.records.sum()==219960 and len(e[K].drop_duplicates())==11006 and e.snapshot_species_key.nunique()==39
        assert not e.duplicated(JOIN).any() and not a.duplicated(JOIN).any()
        ix,D=traits(p["physical"],p["crosswalk"],e,out);assert len(ix)==27 and np.allclose(out["trait_roster"]["uniform_pair_reference"],[54/26]*4)
        gs=C.defaultdict(list)
        for i,v in enumerate(out["trait_roster"]["species"]):gs[v.split()[0].casefold()].append(i)
        groups=list(gs.values());out["genus_group_sizes"]=sorted(map(len,groups),reverse=True)
        f=e.merge(a[JOIN+["records","flag_explicit_captive","flag_roost_context"]].rename(columns={"records":"audit_records"}),on=JOIN,how="outer",validate="one_to_one",indicator=True)
        assert f._merge.eq("both").all() and f.records.eq(f.audit_records).all() and f.flag_explicit_captive.sum()==0 and f.flag_roost_context.sum()==684
        f["clean_records"]=f.records-f.flag_roost_context;assert f.clean_records.ge(0).all()
        f=f[f.clean_records.gt(0)&f.dataset_key.ne("")&f.year.str.fullmatch(r"20[0-9]{2}")&f.license.isin(["CC_BY_4_0","CC0_1_0","CC_BY_NC_4_0"])].copy()
        assert int(f.clean_records.sum())==219276 and len(f[K].drop_duplicates())==10880 and f.dataset_key.nunique()==240
        forest=f[yes(f.forest_profile_support)].copy();assert int(forest.clean_records.sum())==56512 and len(forest[K].drop_duplicates())==6710
        out["support"]={"all_records":219276,"all_cells":10880,"forest_records":56512,"forest_cells":6710,"labels":39}
        out["units"]={};out["pair_support"]={};out["gradient"]={};cases=[]
        exp={("all",100):(228,70),("all",200):(180,76),("forest",100):(173,66),("forest",200):(148,69)}
        for grain in [100,200]:
            for name,data in [("all",f),("forest",forest)]:
                u,st=units(data,ix,grain);assert (st["eligible"],st["blocks"])==exp[name,grain]
                out["units"][f"{name}_{grain}"]=st
                for mode in ["equal","incidence"]:
                    tag=f"{name}_{grain}_{mode}";r=pairs(u,D,mode)
                    stat,c=aggregate(r,tag,True,st["taxa"]);out["pair_support"][tag]=stat;cases.extend(c)
                    for b in BINS:
                        namebin=tag+"_"+b
                        s,c=aggregate([v for v in r if v["bin"]==b],namebin,False,st["taxa"])
                        out["pair_support"][namebin]=s;cases.extend(c)
                    out["gradient"][tag]=gradient(r)
        out["unrestricted_null"]=null_results(cases,D,[list(range(len(ix)))])
        out["genus_conditioned_null"]=null_results(cases,D,groups)
        ng=out["genus_conditioned_null"];screens=[]
        for grain in [100,200]:
            a=ng.get(f"all_{grain}_equal_R");b=ng.get(f"all_{grain}_incidence_R")
            screens.append(bool(a and b and a["excess"][0]<0 and a["rank_le"][0]<=.025 and a["negative_blocks"][0]/a["blocks"]>=.6 and a["delete_one_block_mean_range"][1][0]<0 and b["excess"][0]<0))
        out["primary_screen"]={"by_grain":screens,"pass":all(screens)}
        out["status"]="completed"
    except Exception as e:
        out.update(status="stopped",error_type=type(e).__name__,error="transport error" if isinstance(e,requests.RequestException) else str(e)[:180])
    Path("macro_fd_v3_result.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    # Small console receipt; full aggregate JSON is separately retained.
    print("MACRO_FD_V3_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
