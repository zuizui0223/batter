"""Official WESM geometry/native LPC support on fixed FWS cells; no ecological fit."""
import collections,datetime as dt,hashlib,math,pathlib,re
import numpy as np,pandas as pd,requests,pyogrio
from pyproj import CRS,Transformer
from shapely import make_valid
from shapely.geometry import box,Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
import fws_ept_wesm_date_support_v1 as w
import fws_ept_colocation_v1 as c
f=w.f
O=pathlib.Path("fws_native_lpc_wesm");O.mkdir(exist_ok=True)
P=pathlib.Path("wesm_private.gpkg")
URL="https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/metadata/WESM.gpkg"
CSV_SHA="87f5d330a8953f32fa2682529029b48c844df06f43e8d11f55e46670021fcfa9"
INDEX_SHA="b0510390f8090e46f77b3b8c7c82e24a720157fd8ad31c7345bf2764959148f7"
R={"stage":"official native LPC WESM footprint metadata gate V2","status":"START","url":URL,"actual_geometry_admitted":False,"limits":["Native official LPC route, not a proof of EPT alias identity.","WESM polygon and public LPC link do not establish downloaded LAZ or point density, flight-line timing, leaf conditions, or flight accessibility.","No coordinates, raw FWS rows, site identifiers, or ecological fit exported."]}
def save():
    import json
    s=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))
    (O/"report.json").write_text(s+"\n")
    print("FWS_NATIVE_LPC_REPORT="+s,flush=True)
def need(ok,msg):
    if not ok:raise ValueError(msg)
def text(v):
    if pd.isna(v):return ""
    return str(v).strip()
def idkey(v):
    if pd.isna(v):return None
    if isinstance(v,(int,np.integer)):return str(int(v)) if v>0 else None
    if isinstance(v,(float,np.floating)):
        return str(int(v)) if np.isfinite(v) and v>0 and v.is_integer() else None
    q=str(v).strip()
    return str(int(q)) if re.fullmatch(r"[0-9]+",q) and int(q)>0 else None
def date(v):
    if pd.isna(v):return pd.NaT
    if isinstance(v,(dt.datetime,dt.date,pd.Timestamp,np.datetime64)):
        a=pd.Timestamp(v)
        if a.hour or a.minute or a.second or a.microsecond or a.nanosecond:return pd.NaT
        if a.tzinfo is not None and a.utcoffset()!=dt.timedelta(0):return pd.NaT
        return pd.Timestamp(a.date())
    return w.date_only(str(v))
def download():
    h=hashlib.sha256();n=0
    with requests.get(URL,stream=True,timeout=(20,100),allow_redirects=False) as r:
        R["http"]=r.status_code;save()
        r.raise_for_status();need(r.status_code==200,"GPKG HTTP")
        cap=512*1024**2
        declared=r.headers.get("Content-Length")
        if declared is not None:need(int(declared)<=cap,"GPKG declared size cap")
        with P.open("wb") as out:
            for q in r.iter_content(1024**2):
                n+=len(q);need(n<=cap,"GPKG byte cap");h.update(q);out.write(q)
        if declared is not None:need(n==int(declared),"GPKG truncated")
        R.update(gpkg_bytes=n,gpkg_sha256=h.hexdigest(),gpkg_etag=r.headers.get("ETag"),gpkg_last_modified=r.headers.get("Last-Modified"))
    with P.open("rb") as p:need(p.read(16)==b"SQLite format 3\x00","not SQLite")
    save()
def arm(d,geoms,names):
    if not geoms:return {"candidate_workunits":0,"workunits_intersecting_cells":0,"cells":0,"records":0,"passes_original_support":False,"support":{}}
    tree=STRtree(geoms)
    touched=set()
    for x,y in d[f.K].drop_duplicates().itertuples(index=False,name=None):
        cell=box(x*6000,y*6000,(x+1)*6000,(y+1)*6000)
        touched.update(names[int(i)] for i in tree.query(cell,predicate="intersects") if geoms[int(i)].intersection(cell).area>0)
    return {"candidate_workunits":len(set(names)),"workunits_intersecting_cells":len(touched),**w.coverage(d,geoms,names,set(names))}
def main():
    d=f.source_rows();_,_,_,_,_,s=f.labels_and_pairs(d)
    need(len(d)==8816 and len(d[f.K].drop_duplicates())==241 and s["comparisons"]==10480 and s["comparison_blocks"]==24,"fixed FWS support")
    t=w.fetch();need(w.R["wesm_sha256"]==CSV_SHA,"WESM CSV changed")
    R["csv_sha256"]=CSV_SHA
    t["key"]=t.workunit_id.map(idkey)
    t=t[t.key.notna() & ~t.key.duplicated(False)].set_index("key",drop=False)
    download()
    layers=pyogrio.list_layers(P)
    R["layers"]=layers.tolist();save()
    cols=["workunit","workunit_id","collect_start","collect_end","ql","p_method","vert_crs","lpc_link","lpc_category"]
    candidate=[]
    for l,typ in layers:
        if typ is None:continue
        meta=pyogrio.read_info(P,layer=l)
        if set(cols)<=set(meta["fields"]):candidate.append((l,meta))
    need(len(candidate)==1,"unique official WESM layer with fields")
    layer,meta=candidate[0]
    crs=CRS.from_user_input(meta["crs"])
    R["layer"]={"name":layer,"crs":crs.to_string(),"fields":meta["fields"].tolist(),"feature_count":int(meta["features"]),"geometry_type":meta["geometry_type"]};save()
    cells=d[f.K].drop_duplicates()
    xmin=int(cells.cell_x.min())*6000;ymin=int(cells.cell_y.min())*6000
    xmax=(int(cells.cell_x.max())+1)*6000;ymax=(int(cells.cell_y.max())+1)*6000
    bb=Transformer.from_crs(6933,crs,always_xy=True).transform_bounds(xmin,ymin,xmax,ymax,densify_pts=21)
    g=pyogrio.read_dataframe(P,layer=layer,columns=cols,bbox=bb)
    need(g.crs is not None and len(g)>0,"no official polygons in FWS extent")
    R["bbox_polygon_rows"]=len(g)
    g["key"]=g.workunit_id.map(idkey)
    R["missing_or_duplicate_local_ids"]=int((g.key.isna()|g.key.duplicated(False)).sum())
    g=g[g.key.notna() & ~g.key.duplicated(False)].copy()
    g=g.to_crs(6933)
    lo=pd.Timestamp("2019-04-17");hi=pd.Timestamp("2023-03-16")
    stops=collections.Counter();statuses=collections.Counter();geoms=[];names=[];cats=[];ids=[]
    repaired=0
    for row in g.itertuples(index=False):
        key=row.key
        if key not in t.index:stops["not_unique_csv_id"]+=1;continue
        q=t.loc[key]
        name=text(row.workunit)
        if not name or name!=text(q.workunit):stops["name_disagreement"]+=1;continue
        st,ed=date(row.collect_start),date(row.collect_end)
        cs,ce=date(q.collect_start),date(q.collect_end)
        if any(pd.isna(a) for a in (st,ed,cs,ce)) or st!=cs or ed!=ce or ed<st:
            stops["date_disagreement_or_invalid"]+=1;continue
        if any(text(getattr(row,k))!=text(q[k]) for k in ("ql","p_method","vert_crs","lpc_link","lpc_category")):
            stops["attribute_disagreement"]+=1;continue
        stops["exact_metadata_bridge_pass"]+=1;statuses[text(row.lpc_category)]+=1
        if text(row.ql) not in ("QL 0","QL 1","QL 2"):stops["ql_stop"]+=1;continue
        if text(row.p_method).lower()!="linear-mode lidar":stops["linear_mode_stop"]+=1;continue
        if w.units(text(row.vert_crs)) is None:stops["unit_stop"]+=1;continue
        if not w.official(text(row.lpc_link)):stops["official_url_stop"]+=1;continue
        stops["quality_pass"]+=1
        if st<lo or ed>hi:stops["strict_period_stop"]+=1;continue
        stops["strict_period_pass"]+=1
        geom=row.geometry
        if geom is None or geom.is_empty:stops["empty_geometry"]+=1;continue
        if not geom.is_valid:
            geom=make_valid(geom);repaired+=1
        if geom.geom_type not in ("Polygon","MultiPolygon") or not geom.is_valid or geom.is_empty or not math.isfinite(geom.area) or geom.area<=0:
            stops["invalid_geometry"]+=1;continue
        geoms.append(geom);names.append(name);cats.append(text(row.lpc_category));ids.append(key)
    R["attrition_counts"]=dict(stops);R["lpc_status_exact_bridge"]=dict(statuses);R["geometry_repaired"]=repaired
    R["strict_workunits"]=len(names);R["strict_unique_names"]=len(set(names));R["arms"]={}
    need(len(set(ids))==len(ids),"duplicate qualified IDs")
    # Ambiguous names cannot serve as EPT bridge, but native workunit IDs remain unique.
    R["arms"]["native_LPC_strict"]=arm(d,geoms,ids);save()
    pick=[i for i,v in enumerate(cats) if v in ("Meets","Meets with variance")]
    R["arms"]["native_LPC_strict_meets_category"]=arm(d,[geoms[i] for i in pick],[ids[i] for i in pick]);save()
    eg,en=c.index();need(c.R["index_sha256"]==INDEX_SHA,"EPT index changed")
    R["ept_index_sha256"]=INDEX_SHA
    em={n:g for g,n in zip(eg,en)};need(len(em)==len(en),"duplicate EPT project names")
    counts=collections.Counter(names)
    ig=[];ii=[]
    for g,n,key in zip(geoms,names,ids):
        if counts[n]!=1 or n not in em:continue
        h=g.intersection(em[n])
        if h.is_empty or h.area<=0:continue
        if h.geom_type not in ("Polygon","MultiPolygon"):continue
        ig.append(h);ii.append(key)
    R["arms"]["EPT_exact_name_intersect_official_strict"]=arm(d,ig,ii);save()
    R["status"]="COMPLETE_METADATA_ONLY";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180]);save();raise
    finally:P.unlink(missing_ok=True);f.src.P.unlink(missing_ok=True)
