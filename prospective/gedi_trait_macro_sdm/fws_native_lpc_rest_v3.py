"""Official LPC workunit geometry REST support; exact dated metadata bridge, no model."""
import collections,datetime as dt,hashlib,json,math,pathlib,re
import numpy as np,pandas as pd,requests
from pyproj import Transformer
from shapely import make_valid
from shapely.geometry import shape
from shapely.ops import transform
from shapely.strtree import STRtree
import fws_native_lpc_wesm_v2 as n
import fws_ept_wesm_date_support_v1 as w
import fws_ept_colocation_v1 as c
f=w.f
O=pathlib.Path("fws_native_lpc_rest");O.mkdir(exist_ok=True)
URL="https://index.nationalmap.gov/arcgis/rest/services/3DEPElevationIndex/MapServer/8"
CSV_SHA=n.CSV_SHA;INDEX_SHA=n.INDEX_SHA
COLS=["OBJECTID","workunit","workunit_id","collect_start","collect_end","ql","p_method","vert_crs","lpc_link","lpc_category"]
R={"stage":"official USGS LPC REST polygon strict support V3","status":"START","url":URL,"actual_geometry_admitted":False,"transfers":[],"limitations":["Official REST polygon coverage, not decoded LAZ coverage or physical accessibility.","Exact CSV metadata match only, no inferred EPT aliases.","No precise FWS locations transmitted or exported; queries use only public workunit IDs.","No ecological fit."]}
S=requests.Session()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))
    (O/"report.json").write_text(s+"\n");print("FWS_NATIVE_REST_REPORT="+s,flush=True)
def need(ok,msg):
    if not ok:raise ValueError(msg)
def get(url,params):
    limit=min(16*1024**2,256*1024**2-sum(x.get("bytes",0) for x in R["transfers"]))
    need(limit>0 and len(R["transfers"])<160,"REST byte/request cap")
    rec={"endpoint":url,"where_sha256":hashlib.sha256(params.get("where","").encode()).hexdigest()};R["transfers"].append(rec)
    with S.get(url,params=params,stream=True,timeout=(20,100),allow_redirects=False) as r:
        rec["http"]=r.status_code;need(r.status_code==200,"REST HTTP "+str(r.status_code))
        a=bytearray()
        for q in r.iter_content(65536):
            a.extend(q);need(len(a)<=limit,"REST response cap")
        rec.update(bytes=len(a),sha256=hashlib.sha256(a).hexdigest(),etag=r.headers.get("ETag"),last_modified=r.headers.get("Last-Modified"))
    j=json.loads(a);need(isinstance(j,dict) and "error" not in j,"REST response error/schema")
    return j
def dates(v):
    if isinstance(v,(int,float,np.integer,np.floating)) and not isinstance(v,bool):
        if not np.isfinite(v) or int(v)!=v:return pd.NaT
        try:
            z=pd.Timestamp(v,unit="ms",tz="UTC")
            if z.hour or z.minute or z.second or z.microsecond or z.nanosecond:return pd.NaT
            return pd.Timestamp(z.date())
        except Exception:return pd.NaT
    return n.date(v)
def assert_tests():
    need(dates(1586304000000)==pd.Timestamp("2020-04-08"),"epoch-ms test")
    need(pd.isna(dates(1586304000001)),"nonmidnight test")
    need(dates("2020/04/08")==pd.Timestamp("2020-04-08"),"date lexical test")
    need(pd.isna(dates("04/08/2020")),"ambiguous date test")
def main():
    assert_tests()
    d=f.source_rows();_,_,_,_,_,s=f.labels_and_pairs(d)
    need(len(d)==8816 and len(d[f.K].drop_duplicates())==241 and s["comparisons"]==10480 and s["comparison_blocks"]==24,"fixed FWS support")
    t=w.fetch();need(w.R["wesm_sha256"]==CSV_SHA,"WESM CSV changed");R["csv_sha256"]=CSV_SHA
    t["key"]=t.workunit_id.map(n.idkey)
    R["csv_missing_or_duplicate_ids"]=int((t.key.isna()|t.key.duplicated(False)).sum())
    t=t[t.key.notna() & ~t.key.duplicated(False)].copy()
    start=t.collect_start.map(dates);end=t.collect_end.map(dates)
    mask=start.notna()&end.notna()&(start<=end)&(start>=pd.Timestamp("2019-04-17"))&(end<=pd.Timestamp("2023-03-16"))
    mask&=t.ql.str.strip().isin(["QL 0","QL 1","QL 2"])&t.p_method.str.strip().str.lower().eq("linear-mode lidar")&t.vert_crs.map(w.units).notna()&t.lpc_link.map(w.official)
    t=t[mask].set_index("key",drop=False);ids=sorted(t.index,key=int)
    R["strict_csv_workunit_count"]=len(ids)
    need(len(ids)>0 and math.ceil(len(ids)/25)+1<=160,"strict ID roster/budget")
    meta=get(URL,{"f":"json"})
    fs={x["name"]:x["type"] for x in meta["fields"]}
    need(meta.get("id")==8 and meta.get("name")=="Lidar Point Cloud" and meta.get("geometryType")=="esriGeometryPolygon","layer identity")
    need(set(COLS)<=set(fs) and fs["workunit_id"]=="esriFieldTypeInteger" and fs["collect_start"]==fs["collect_end"]=="esriFieldTypeDate" and int(meta["maxRecordCount"])>=25,"layer fields/limits")
    R["service_metadata"]={"name":meta["name"],"fields":{x:fs[x] for x in COLS},"maxRecordCount":meta["maxRecordCount"],"extent_spatial_reference":meta.get("extent",{}).get("spatialReference"),"editingInfo":meta.get("editingInfo"),"currentVersion":meta.get("currentVersion")};save()
    features=[];seen_obj=set()
    for i in range(0,len(ids),25):
        batch=ids[i:i+25]
        q=get(URL+"/query",{"where":"workunit_id IN ("+",".join(batch)+")","outFields":",".join(COLS),"returnGeometry":"true","outSR":"4326","f":"geojson"})
        need(q.get("type")=="FeatureCollection" and isinstance(q.get("features"),list) and not q.get("exceededTransferLimit"),"incomplete GeoJSON")
        if q.get("crs"):
            crsname=str(q["crs"].get("properties",{}).get("name","")).upper()
            need(crsname.endswith("4326") or crsname.endswith("CRS84"),"GeoJSON CRS")
        for v in q["features"]:
            p=v.get("properties",{});key=n.idkey(p.get("workunit_id"))
            need(key in batch,"unexpected public workunit ID")
            obj=p.get("OBJECTID")
            need(obj is not None and obj not in seen_obj,"duplicate/missing object ID")
            seen_obj.add(obj);features.append(v)
        if (i//25+1)%10==0:print("REST_BATCH_PROGRESS",i+len(batch),len(features),flush=True)
    keys=[n.idkey(v["properties"]["workunit_id"]) for v in features];counts=collections.Counter(keys)
    R["service_returned_features"]=len(features);R["missing_strict_csv_ids"]=len(set(ids)-set(keys));R["ambiguous_workunit_ids"]=sum(x>1 for x in counts.values())
    stops=collections.Counter();cats=[];geoms=[];names=[];validids=[];repair=0
    tr=Transformer.from_crs(4326,6933,always_xy=True)
    for v,key in zip(features,keys):
        if counts[key]!=1:stops["ambiguous_service_id"]+=1;continue
        p=v["properties"];row=t.loc[key];name=n.text(p.get("workunit"))
        if not name or name!=n.text(row.workunit):stops["name_disagreement"]+=1;continue
        st,ed=dates(p.get("collect_start")),dates(p.get("collect_end"))
        cs,ce=dates(row.collect_start),dates(row.collect_end)
        if any(pd.isna(a) for a in (st,ed,cs,ce)) or st!=cs or ed!=ce:stops["date_disagreement_or_invalid"]+=1;continue
        if any(n.text(p.get(k))!=n.text(row[k]) for k in ["ql","p_method","vert_crs","lpc_link","lpc_category"]):
            stops["attribute_disagreement"]+=1;continue
        stops["exact_metadata_bridge_pass"]+=1
        try:
            g=shape(v["geometry"]);lo,bo,hi,to=g.bounds
            need(-180<=lo<=hi<=180 and -90<=bo<=to<=90,"invalid geographic bounds")
            if not g.is_valid:g=make_valid(g);repair+=1
            if g.is_empty or g.geom_type not in ("Polygon","MultiPolygon"):raise ValueError("nonpolygon")
            g=transform(tr.transform,g)
            if g.is_empty or not g.is_valid or not math.isfinite(g.area) or g.area<=0:raise ValueError("invalid projected geometry")
        except Exception:stops["invalid_geometry"]+=1;continue
        geoms.append(g);names.append(name);validids.append(key);cats.append(n.text(p.get("lpc_category")))
    R["attrition_counts"]=dict(stops);R["geometry_repaired"]=repair;R["qualified_geometry_ids"]=len(validids);R["arms"]={}
    R["arms"]["native_LPC_strict"]=n.arm(d,geoms,validids);save()
    pick=[i for i,v in enumerate(cats) if v in ("Meets","Meets with variance")]
    R["arms"]["native_LPC_strict_meets_category"]=n.arm(d,[geoms[i] for i in pick],[validids[i] for i in pick]);save()
    eg,en=c.index();need(c.R["index_sha256"]==INDEX_SHA,"EPT index changed");R["ept_index_sha256"]=INDEX_SHA
    em={nm:g for g,nm in zip(eg,en)};need(len(em)==len(en),"duplicate EPT names")
    cc=collections.Counter(names);ig=[];ii=[]
    for g,nm,key in zip(geoms,names,validids):
        if cc[nm]!=1 or nm not in em:continue
        h=g.intersection(em[nm])
        if not h.is_empty and h.geom_type in ("Polygon","MultiPolygon") and h.area>0:ig.append(h);ii.append(key)
    R["arms"]["EPT_exact_name_intersect_official_strict"]=n.arm(d,ig,ii)
    R["status"]="COMPLETE_METADATA_ONLY";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180]);save();raise
    finally:f.src.P.unlink(missing_ok=True)
