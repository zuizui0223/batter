"""Reported-only COMBINE domain coverage on the audited PHYLACINE current range grid."""
import collections as C,hashlib,io,json,math,re,urllib.request
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing,REGIONS

FILES={
 "trait_data_reported.csv":(27703263,1612538,"14ace2dff03b71c20dc923a9eb293aaadc29934e21c6f11fa30d1b70e5abab92"),
 "trait_data_sources.csv":(27703260,3552819,"f0d8ba1e42fabed49ffd0d4e61a577c3bfee0a787b9886c5891f8707112a1200"),
 "trait_data_imputed.csv":(27703266,1891897,"b576cfd9f12b1441eb564bbf7acb65f06e676108aa0651aed9594585e7ff65f9")}
KEY=["iucn2020_binomial","phylacine_binomial","order"]
BODY=["adult_mass_g","adult_forearm_length_mm","adult_body_length_mm"]
COARSE=["dphy_plant","dphy_vertebrate","dphy_invertebrate"]
DETAIL=["det_inv","det_vend","det_vect","det_vfish","det_vunk","det_scav","det_fruit","det_nect","det_seed","det_plantother"]
CAT=["foraging_stratum","activity_cycle","hibernation_torpor"]
FIELDS=BODY+COARSE+DETAIL+["det_diet_breadth_n","trophic_level"]+CAT
MISSING={"","na","n/a","nan","none","null","unknown","not recognised","not recognized","not available","-"}
def norm(v):return "_".join(str(v).strip().casefold().replace("_"," ").split())
def present(s):return ~s.str.strip().str.casefold().isin(MISSING)
def get(url,cap):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-public-source-audit/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(cap+1)
    if len(b)>cap:raise ValueError("source size cap")
    return b
def acquire(out):
    m=json.loads(get("https://api.figshare.com/v2/articles/13028255/versions/4",2*1024**2))
    assert m["doi"]=="10.6084/m9.figshare.13028255.v4" and int(m["version"])==4
    out["sources"]={};tabs=[]
    for n,(fid,size,sha) in FILES.items():
        hits=[f for f in m["files"] if f["name"]==n];assert len(hits)==1
        f=hits[0];assert int(f["id"])==fid and int(f["size"])==size
        url=f.get("download_url") or f.get("downloadUrl");assert url and url.startswith("https://")
        b=get(url,size);md=f.get("computed_md5") or f.get("supplied_md5")
        assert len(b)==size and hashlib.sha256(b).hexdigest()==sha and hashlib.md5(b).hexdigest()==md
        d=pd.read_csv(io.BytesIO(b),dtype=str,keep_default_na=False)
        assert len(d)==6263 and set(KEY)<=set(d)
        dup=int(d.duplicated(KEY,keep=False).sum())
        out["sources"][n]={"id":fid,"bytes":size,"sha256":sha,"md5":md,"rows":len(d),"duplicate_key_rows":dup}
        tabs.append(d)
    # Reject all ambiguous key groups from joining; no arbitrary first-row selection.
    for d in tabs:assert not d.duplicated(KEY).any(),"duplicate source composite keys"
    a,b,c=[d.set_index(KEY).sort_index() for d in tabs]
    assert a.index.equals(b.index) and a.index.equals(c.index),"different source row keys"
    return a.reset_index(),b.reset_index(),c.reset_index()
def summarize_numeric(s,m):
    x=pd.to_numeric(s[m],errors="coerce");v=x[np.isfinite(x)]
    return {"finite_numeric":int(len(v)),"non_numeric":int(m.sum()-len(v)),"quantiles":np.quantile(v,[0,.25,.5,.75,1]).tolist() if len(v) else None}
def count_coverage(X,mask,rg,full_rich):
    base=rg&(full_rich>0);rich=X[mask].sum(0)
    f=np.divide(rich,full_rich,out=np.zeros_like(full_rich,float),where=full_rich>0)
    return {"species":int(np.any(X[mask][:,base],axis=1).sum()),"occupied_cells":int(base.sum()),"any_domain_cells":int((base&(rich>0)).sum()),"eligible_ge5_ge20":int((base&(rich>=5)&(f>=.2)).sum()),"eligible_ge5_ge80":int((base&(rich>=5)&(f>=.8)).sum()),"median_coverage":float(np.median(f[base])) if base.any() else None}
def main():
    out={"status":"START","scope":"range-domain coverage only; no biological effect fit","doi":"10.6084/m9.figshare.13028255.v4"}
    try:
        a,b,c=acquire(out)
        assert all(k in a and k in c for k in FIELDS)
        bat=a["order"].str.strip().str.casefold().eq("chiroptera")
        out["table_bat_rows"]=int(bat.sum())
        names,X,shape,crs,T=read_ranges(out);assert len(names)==1141
        w=wing(out);wm=np.array([n in w.index for n in names]);assert int(wm.sum())==264
        z=a["phylacine_binomial"].map(norm)
        valid=bat&present(a["phylacine_binomial"])&z.isin(names)
        counts=z[valid].value_counts()
        amb=set(counts[counts!=1].index)
        uni=valid&~z.isin(amb)
        out["name_mapping"]={"positive_range_species":len(names),"COMBINE_bat_rows":int(bat.sum()),"exact_matching_rows":int(valid.sum()),"ambiguous_range_labels":len(amb),"exact_unique_matches":int(uni.sum()),"unmatched_or_ambiguous_range_labels":len(names)-int(uni.sum())}
        pos={v:i for i,v in enumerate(names)};rowids=np.flatnonzero(uni.to_numpy());mapidx=np.array([pos[v] for v in z[uni]],int)
        reported={};strict={};num={};out["field_coverage"]={}
        for k in FIELDS:
            pr=present(a[k])&uni;pi=present(c[k])&uni
            reported[k]=pr.to_numpy()
            if k in b:
                flag=b[k].str.strip();isimp=flag.str.contains("imput",case=False,regex=False)
                ok=present(flag)&~isimp
                st=pr&ok
                src=dict(C.Counter(flag[pr].replace("", "<blank>")))
                out["field_coverage"][k]={"reported_nonmissing":int(pr.sum()),"strict_reported":int(st.sum()),"imputed_table_nonmissing":int(pi.sum()),"imputed_flag_with_reported_value":int((pr&isimp).sum()),"source_annotations_for_reported_values":src}
            else:
                st=pd.Series(False,index=a.index)
                out["field_coverage"][k]={"reported_nonmissing":int(pr.sum()),"strict_reported":None,"imputed_table_nonmissing":int(pi.sum()),"source_status":"exact source field absent"}
            strict[k]=st.to_numpy()
            if k in CAT:
                out["field_coverage"][k]["reported_levels"]=dict(C.Counter(a.loc[pr,k]))
            else:
                v=pd.to_numeric(a[k],errors="coerce").to_numpy(float);num[k]=v
                out["field_coverage"][k]["reported_numeric"]=summarize_numeric(a[k],pr)
        out["source_schema_difference"]=sorted(set(FIELDS)-set(b.columns))
        def numeric_mask(keys,positive=False,src=True):
            masks=[]
            for k in keys:
                v=num[k];m=strict[k] if src else reported[k]
                masks.append(m&np.isfinite(v)&(v>0 if positive else v>=0))
            return np.logical_and.reduce(masks)
        md=numeric_mask(BODY,True);diet=numeric_mask(COARSE);d10=numeric_mask(DETAIL,src=False)
        d9=numeric_mask([k for k in DETAIL if k in b]);forage=strict["foraging_stratum"];act=strict["activity_cycle"]
        mass=numeric_mask(["adult_mass_g"],True)
        rowm={"body_morphology_strict":md,"coarse_diet_strict":diet,"detailed_diet_reported_10":d10,"detailed_diet_strict_9":d9,"detailed_diet_reported10_strict9":d10&d9,"foraging_stratum_strict":forage,"activity_cycle_strict":act,"body_mass_strict":mass,"mass_coarse_diet_stratum_strict":mass&diet&forage}
        masks={}
        for k,m in rowm.items():
            v=np.zeros(len(names),bool);v[mapidx]=m[rowids];masks[k]=v
        masks["LSA_wing"]=wm;masks["exact_COMBINE_match"]=np.isin(names,z[uni])
        for k,v in list(masks.items()):
            if k not in ("LSA_wing","exact_COMBINE_match"):masks["wing_and_"+k]=wm&v
        out["domain_species_counts"]={k:int(v.sum()) for k,v in masks.items()}
        out["diet_sum_diagnostic"]={}
        for label,keys,mask in [("coarse_strict",COARSE,diet),("detailed_reported10",DETAIL,d10),("detailed_reported10_strict9",DETAIL,d10&d9)]:
            v=np.stack([num[k] for k in keys],axis=1)[mask].sum(1)
            out["diet_sum_diagnostic"][label]={"n":len(v),"sum_quantiles":np.quantile(v,[0,.25,.5,.75,1]).tolist() if len(v) else None,"sums_1":int(np.isclose(v,1).sum()),"sums_100":int(np.isclose(v,100).sum())}
        rc=np.array(np.unravel_index(np.arange(X.shape[1]),shape)).T
        lon,lat=Transformer.from_crs(crs,4326,always_xy=True).transform(T.c+(rc[:,1]+.5)*T.a,T.f+(rc[:,0]+.5)*T.e)
        full=X.sum(0);rgs={"all":np.ones(len(full),bool)}
        for n,(l,r,b,t) in REGIONS.items():rgs[n]=(lon>=l)&(lon<=r)&(lat>=b)&(lat<t)
        out["range_coverage"]={r:{k:count_coverage(X,m,q,full) for k,m in masks.items()} for r,q in rgs.items()}
        out["status"]="COMPLETE_COVERAGE_ONLY"
    except Exception as e:
        out.update(status="STOP",error_type=type(e).__name__,error=str(e)[:150])
    Path("combine_v6b_coverage.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    print("COMBINE_V6B_REPORT="+json.dumps(out,allow_nan=False),flush=True)
if __name__=="__main__":main()
