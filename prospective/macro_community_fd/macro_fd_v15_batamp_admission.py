"""V15: support-only audit of public BatAMP detector-height monthly aggregates."""
import calendar,collections as C,hashlib,json,re,subprocess,itertools
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer
from macro_fd_v4_global_ranges import wing
from macro_fd_v7_multidomain import mapping
from combine_v6b_coverage import acquire

PIN="15e2bf60d63aea0246fcec178ebd152b4164f367"
ROOT=Path("batamp")
OUT=Path("macro_fd_v15_result.json")
FILES={"ui/static/data/detectors.feather":(915034,"d7a8a122e47e2a116be975765760c8376a801b91"),"ui/static/data/spp_detections.feather":(2387282,"b293bacbd1c0eedf0be67231f982c6eb1fb41c47")}
PHYL="db6f0a5584ef5b0d899770d231476c6589cb16b8"
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V15_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def verify(root,ref,filename,expected=None):
    assert subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"]).decode().strip()==ref
    b=(root/filename).read_bytes()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse",f"HEAD:{filename}"]).decode().strip()
    assert blob(b)==sha
    if expected:assert (len(b),sha)==expected
    return {"bytes":len(b),"git_blob":sha,"sha256":hashlib.sha256(b).hexdigest()}
def numbers(d,keys):
    for k in keys:d[k]=pd.to_numeric(d[k].astype(object),errors="coerce")
def q(v):
    a=np.asarray(v,float)
    return np.quantile(a,[0,.25,.5,.75,1]).tolist() if len(a) else None
def dictionary(s):
    a=s.split("export const SPECIES = {",1)[1].split("export const SPECIES_REMAP",1)[0]
    a=re.sub(r"(?m)^\s*//.*$","",a)
    names=dict(re.findall(r"(?m)^\s*([a-z]{4}):\s*\{\s*sciName:\s*'([^']+)'",a))
    b=s.split("export const SPECIES_ID = {",1)[1].split("export const METRICS",1)[0]
    ids={int(k):v for k,v in re.findall(r"(?m)^\s*'?([0-9]+)'?:\s*'([a-z]{4})'",b)}
    assert len(ids)==45 and len(names)==45 and set(ids.values())==set(names)
    return {i:names[k].lower().replace(" ","_") for i,k in ids.items()}
def main():
    o={"stage":"public BatAMP detector-height monthly audit","status":"START","source_commit":PIN,"limits":["monthly summaries not simultaneous nights","microphone heights not animal flight heights","source coordinates can be GRTS centroids; no local structural join","upstream merging and imputation of survey zeros; no occupancy inference","dataset strings are not necessarily independent studies","no raw locations, IDs, or detector metadata values exported","support only; no ecological outcome fit"]}
    try:
        o["files"]={k:verify(ROOT,PIN,k,v) for k,v in FILES.items()}
        for k in ("analysis/README.md","analysis/merge.py","ui/src/config.js","ui/data/summary.json"):o["files"][k]=verify(ROOT,PIN,k)
        spec=dictionary((ROOT/"ui/src/config.js").read_text())
        summary=json.loads((ROOT/"ui/data/summary.json").read_text())
        d=pd.read_feather(ROOT/"ui/static/data/detectors.feather")
        s=pd.read_feather(ROOT/"ui/static/data/spp_detections.feather")
        o["schemas"]={"detectors":{k:str(v) for k,v in d.dtypes.items()},"species":{k:str(v) for k,v in s.dtypes.items()}}
        dc=["id","siteId","micHt","source","countType","dataset","detType","micType","callId","lat","lon"]
        sc=["detId","year","month","species","detections","detectionNights","detectorNights"]
        assert set(dc)<=set(d) and set(sc)<=set(s),"schema missing"
        numbers(d,["id","siteId","micHt","lat","lon","detectorNights","detectionNights"])
        numbers(s,sc)
        assert d.id.notna().all() and d.id.is_unique
        assert s[sc].notna().all().all() and not s.duplicated(["detId","year","month","species"]).any()
        assert s.detId.isin(d.id).all() and s.species.isin(spec).all()
        assert (s.detections>=0).all() and (s.detectorNights>=s.detectionNights).all() and (s.detectionNights>=0).all()
        assert s.month.between(1,12).all() and s.detectorNights.le(31).all()
        assert ((s.detections>0)==(s.detectionNights>0)).all()
        s["name"]=s.species.map(spec)
        s["days"]=[calendar.monthrange(int(y),int(m))[1] for y,m in zip(s.year,s.month)]
        assert (s.detectorNights<=s.days).all()
        exact=s.name.str.fullmatch(r"[a-z]+_[a-z-]+")
        o["source_census"]={"detectors":len(d),"species_month_rows":len(s),"sites":int(d.siteId.nunique()),"total_detections":int(s.detections.sum()),"species_detected":int(s.loc[s.detections>0,"name"].nunique()),"species_monitored":int(s.name.nunique()),"reported_detector_nights":int(d.detectorNights.sum()),"year_min":int(s.year.min()),"year_max":int(s.year.max()),"height_finite_positive_detectors":int((np.isfinite(d.micHt)&d.micHt.gt(0)).sum()),"exact_binomial_codes":int(len(set(s.loc[exact,"name"]))),"count_types":{str(k):int(v) for k,v in d.countType.value_counts().items() if v>0},"sources":{str(k):int(v) for k,v in d.source.value_counts().items() if v>0},"coordinate_precision_field_present":any("centroid" in k.lower() or "precision" in k.lower() for k in d.columns)}
        o["summary_checks"]={"detectors_match":len(d)==summary["detectors"],"detections_match":int(s.detections.sum())==summary["speciesDetections"],"species_detected_match":int(s.loc[s.detections>0,"name"].nunique())==summary["speciesDetected"],"species_monitored_match":int(s.name.nunique())==summary["speciesSurveyed"],"nights_match":int(d.detectorNights.sum())==summary["detectorNights"]}
        o["status"]="SOURCE_VERIFIED";save(o)
        meta=Path("phylacine/Data/Ranges/Spatial_metadata.csv")
        o["range_metadata"]=verify(Path("phylacine"),PHYL,"Data/Ranges/Spatial_metadata.csv")
        assert o["range_metadata"]["git_blob"]=="f2538374945f602f7c148d1a534be491895cd6e1"
        m=pd.read_csv(meta);names=m.loc[(m["Order.1.2"]=="Chiroptera")&(m["Number.Cells.Current.Range"]>0),"Binomial.1.2"].str.lower().tolist()
        assert len(names)==1141 and len(set(names))==1141
        w=wing(o);a,b,_=acquire(o);f=mapping(a,b,names,w,o)
        wingnames=set(w.index)&set(names);broad=set(f.index)
        o["matched_trait_species"]={"wing":int(s.loc[exact,"name"].isin(wingnames).groupby(s.name).any().sum()),"broad":int(s.loc[exact,"name"].isin(broad).groupby(s.name).any().sum())}
        region=d.lon.between(-170,-50)&d.lat.between(15,51.6)
        hgood=np.isfinite(d.micHt)&d.micHt.gt(0)&d.siteId.notna()
        for k in ("source","countType","dataset","detType","micType","callId"):
            d[k]=d[k].astype(object).fillna("").astype(str).str.strip()
        dgood=region&hgood&d.source.isin(["batamp","nabat"])&d.countType.isin(["a","p"])
        dd=d.loc[dgood,dc].copy()
        tr=Transformer.from_crs(4326,6933,always_xy=True)
        xx,yy=tr.transform(dd.lon.to_numpy(),dd.lat.to_numpy())
        dd["bx"]=np.floor(xx/200000).astype(int);dd["by"]=np.floor(yy/200000).astype(int)
        # For each site/source/count-type/month select maximal height separation BEFORE trait/outcome gating.
        fields=["siteId","source","countType","year","month"]
        meta_keys=["dataset","detType","micType","callId"]
        ss=s.loc[exact&s.year.between(2019,2022)&s.detectorNights.ge(5),["detId","year","month","name","detectorNights","days"]].merge(dd,left_on="detId",right_on="id",validate="many_to_one")
        def run(sub):
            ans=[];loose=0
            for _,g in sub.groupby(fields,sort=False,observed=True):
                info=g.drop_duplicates("detId")
                if len(info)<2:continue
                rows=info.to_dict("records")
                allpairs=[(u,v) if u["micHt"]<v["micHt"] else (v,u) for u,v in itertools.combinations(rows,2) if abs(u["micHt"]-v["micHt"])>=5]
                if not allpairs:continue
                loose+=1
                pairs=[(u,v) for u,v in allpairs if all(u[k] and u[k]==v[k] for k in meta_keys)]
                if not pairs:continue
                L,H=sorted(pairs,key=lambda z:(-(z[1]["micHt"]-z[0]["micHt"]),z[0]["detId"],z[1]["detId"]))[0]
                p=g[g.detId.eq(L["detId"])].set_index("name").detectorNights
                q0=g[g.detId.eq(H["detId"])].set_index("name").detectorNights
                assert p.index.is_unique and q0.index.is_unique
                common=set(p.index)&set(q0.index)
                days=int(g.days.iloc[0])
                overlap={k:max(0,int(p[k]+q0[k]-days)) for k in common}
                ans.append({"site":int(L["siteId"]),"source":L["source"],"year":int(L["year"]),"month":int(L["month"]),"dataset":L["dataset"],"block":(int(L["bx"]),int(L["by"])),"height_difference":float(H["micHt"]-L["micHt"]),"lower":float(L["micHt"]),"higher":float(H["micHt"]),"species":len(common),"wing":len(common&wingnames),"broad":len(common&broad),"all_overlap":bool(common) and all(v>0 for v in overlap.values()),"wing_overlap":len(common&wingnames)>=5 and all(overlap[k]>0 for k in common&wingnames),"broad_overlap":len(common&broad)>=5 and all(overlap[k]>0 for k in common&broad),"monitor_min":min([min(p[k],q0[k]) for k in common],default=0),"monitor_max":max([max(p[k],q0[k]) for k in common],default=0)})
            def report(a,trait=None):
                n=len({x["site"] for x in a});bl=len({x["block"] for x in a});ds=len({x["dataset"] for x in a})
                ov=len({x["site"] for x in a if x[(trait+"_overlap") if trait else "all_overlap"]})
                return {"site_month_pairs":len(a),"sites":n,"blocks200":bl,"dataset_strings":ds,"sites_all_included_species_positive_overlap_bound":ov,"height_gap_quantiles_m":q([x["height_difference"] for x in a]),"low_height_quantiles_m":q([x["lower"] for x in a]),"high_height_quantiles_m":q([x["higher"] for x in a]),"common_monitored_species_quantiles":q([x["species"] for x in a]),"monitor_night_min_quantiles":q([x["monitor_min"] for x in a]),"monitor_night_max_quantiles":q([x["monitor_max"] for x in a]),"year_counts":dict(C.Counter(str(x["year"]) for x in a)),"source_counts":dict(C.Counter(x["source"] for x in a)),"admitted":bool(trait and n>=60 and bl>=10 and ds>=10 and ov>=20)}
            return {"candidate_site_source_type_months_height_gap":loose,"strict_metadata_matched":report(ans),"at_least_two":report([x for x in ans if x["species"]>=2]),"at_least_five":report([x for x in ans if x["species"]>=5]),"wing":report([x for x in ans if x["species"]>=5 and x["wing"]>=5],"wing"),"broad":report([x for x in ans if x["species"]>=5 and x["broad"]>=5],"broad")}
        o["period_census"]={"regional_positive_height_detectors":len(dd),"2019_22_month_species_rows_ge5_nights":len(ss),"detectors_on_support":int(ss.detId.nunique()),"sites_on_support":int(ss.siteId.nunique())}
        o["primary"]=run(ss[ss.month.between(5,9)])
        o["calendar_sensitivity"]=run(ss)
        o["status"]="HEIGHT_SUPPORT_ADMITTED" if any(o["primary"][k]["admitted"] for k in ("wing","broad")) else "HEIGHT_SUPPORT_STOP"
        save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__;o["validation"]=str(e)[:300];save(o)
if __name__=="__main__":main()
