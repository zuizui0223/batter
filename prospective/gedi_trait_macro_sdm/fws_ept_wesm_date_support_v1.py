"""Metadata-only date/quality gate. No raw observations, point clouds or model fit."""
import collections,hashlib,io,json,pathlib,re,urllib.parse
import numpy as np,pandas as pd,requests
from shapely.geometry import box,Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
from pyproj import CRS
import fws_ept_colocation_v1 as c
f=c.f
O=pathlib.Path("fws_wesm_support");O.mkdir(exist_ok=True)
URL="https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/metadata/WESM.csv"
INDEX="b0510390f8090e46f77b3b8c7c82e24a720157fd8ad31c7345bf2764959148f7"
R={"stage":"FWS EPT exact WESM workunit/date quality metadata support","status":"START","url":URL,"index_sha256_expected":INDEX,"actual_point_geometry_admitted":False,"limitations":["Exact name match is provisional lineage, not proven spatial identity.","WESM native vertical CRS does not establish transformed EPT Z unit.","Metadata date intervals do not establish simultaneous observation or leaf phenology. No biological fit."]}
def save():
    s=json.dumps(R,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist() if isinstance(v,np.ndarray) else None)
    (O/"report.json").write_text(s+"\n");print("FWS_WESM_REPORT="+s,flush=True)
def fetch():
    with requests.get(URL,timeout=(20,75),stream=True,allow_redirects=False) as q:
        R["http"]=q.status_code
        q.raise_for_status()
        assert q.status_code==200
        data=bytearray()
        for x in q.iter_content(65536):
            data.extend(x);assert len(data)<=64*1024**2
        R.update(wesm_bytes=len(data),wesm_sha256=hashlib.sha256(data).hexdigest(),wesm_etag=q.headers.get("ETag"),last_modified=q.headers.get("Last-Modified"))
    t=pd.read_csv(io.BytesIO(data),dtype=str,keep_default_na=False,encoding="utf-8-sig")
    R["columns"]=t.columns.tolist();R["rows"]=len(t);save()
    cols=["workunit","workunit_id","collect_start","collect_end","ql","p_method","horiz_crs","vert_crs","geoid","lpc_pub_date","lpc_link"]
    assert set(cols)<=set(t.columns) and 100<=len(t)<=100000
    return t
def units(x):
    if not re.fullmatch(r"[0-9]{4,6}",x.strip()):return None
    try:
        crs=CRS.from_epsg(int(x))
        if not crs.is_vertical or len(crs.axis_info)!=1:return None
        u=crs.axis_info[0].unit_name.lower()
        return u if u in {"metre","meter","foot","us survey foot"} else None
    except Exception:return None
def official(u):
    p=urllib.parse.urlparse(u)
    return p.scheme=="https" and p.hostname in {"rockyweb.usgs.gov","prd-tnm.s3.amazonaws.com","s3.amazonaws.com","s3.us-west-2.amazonaws.com"} and not p.username and not p.password
def coverage(d,geoms,names,allowed):
    live=[g for g,n in zip(geoms,names) if n in allowed]
    tree=STRtree(live);out=[]
    for x,y in sorted(map(tuple,d[f.K].drop_duplicates().itertuples(index=False,name=None))):
        cell=box(x*6000,y*6000,(x+1)*6000,(y+1)*6000)
        ids=tree.query(cell,predicate="intersects")
        gg=[live[int(i)].intersection(cell) for i in ids]
        ar=float(unary_union(gg).area/cell.area) if gg else 0.
        n=sum(bool(len(tree.query(Point((x+u)*6000,(y+v)*6000),predicate="covered_by"))) for u in (1/6,1/2,5/6) for v in (1/6,1/2,5/6))
        if ar>=.95 and n==9:out.append((x,y))
    u=pd.DataFrame(out,columns=f.K)
    q=d.merge(u,on=f.K,validate="many_to_one")
    if q.empty:return {"cells":0,"records":0,"passes_original_support":False,"support":{}}
    _,_,_,_,_,s=f.labels_and_pairs(q)
    return {"cells":len(u),"records":len(q),"support":s,"passes_original_support":bool(f.passes(s))}
def main():
    d=f.source_rows();_,_,_,_,_,s=f.labels_and_pairs(d)
    assert len(d)==8816 and len(d[f.K].drop_duplicates())==241 and s["comparisons"]==10480
    geoms,names=c.index();assert c.R["index_sha256"]==INDEX and len(set(names))==2284
    tree=STRtree(geoms);matched=set()
    for x,y in d[f.K].drop_duplicates().itertuples(index=False,name=None):
        for u in (1/6,1/2,5/6):
            for v in (1/6,1/2,5/6):
                matched.update(names[int(i)] for i in tree.query(Point((x+u)*6000,(y+v)*6000),predicate="covered_by"))
    assert len(matched)==99
    R["overlap_project_count"]=len(matched);save()
    t=fetch();q=t[t.workunit.isin(matched)].copy()
    ids=q.groupby("workunit").size();unique=set(ids[ids==1].index)
    R["exact_name_match"]={"matched_names":len(ids),"unique":len(unique),"ambiguous":int((ids>1).sum()),"unmatched":len(matched-set(ids.index))}
    q=q[q.workunit.isin(unique)].copy()
    # No modification of project IDs or resolution of multiple source rows.
    start=pd.to_datetime(q.collect_start,format="%Y-%m-%d",errors="coerce")
    end=pd.to_datetime(q.collect_end,format="%Y-%m-%d",errors="coerce")
    mask=start.notna()&end.notna()&(start<=end)
    masks=[("ordered_date",mask),("ql_0_1_2",q.ql.str.strip().isin(["QL 0","QL 1","QL 2"])),("linear_mode",q.p_method.str.strip().str.lower().eq("linear-mode lidar")),("recognized_native_vertical_units",q.vert_crs.map(units).notna()),("official_lpc_link",q.lpc_link.map(official))]
    R["metadata_distributions"]={"ql":q.ql.value_counts().to_dict(),"p_method":q.p_method.value_counts().to_dict(),"vertical_units":q.vert_crs.map(units).fillna("unrecognized").value_counts().to_dict()}
    status_cols=[k for k in t.columns if re.search(r"lpc.*(status|category|reason|cat|code)",k,re.I)]
    R["status_columns_observed"]={k:q[k].value_counts().head(20).to_dict() for k in status_cols}
    m=pd.Series(True,index=q.index);flow=[]
    for label,a in masks:
        m&=a;flow.append({"stage":label,"workunits":int(m.sum())})
    R["attrition"]=flow
    lo=pd.Timestamp("2019-04-17");hi=pd.Timestamp("2023-03-16")
    a={"exact_unique":unique,"metadata_qualified":set(q.loc[m,"workunit"]),"strict_period":set(q.loc[m&(start>=lo)&(end<=hi),"workunit"]),"period_overlap":set(q.loc[m&(start<=hi)&(end>=lo),"workunit"])}
    R["arms"]={}
    for k,v in a.items():
        R["arms"][k]={"projects":len(v),**coverage(d,geoms,names,v)}
        save()
    R["status"]="COMPLETE_METADATA_ONLY";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180]);save();raise
    finally:f.src.P.unlink(missing_ok=True)
