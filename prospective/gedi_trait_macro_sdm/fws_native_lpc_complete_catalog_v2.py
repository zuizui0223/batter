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
O=pathlib.Path("fws_native_lpc_complete_catalog");O.mkdir(exist_ok=True)
URL="https://index.nationalmap.gov/arcgis/rest/services/3DEPElevationIndex/MapServer/8"
CSV_SHA=n.CSV_SHA;INDEX_SHA=n.INDEX_SHA
COLS=["OBJECTID","workunit","workunit_id","collect_start","collect_end","ql","p_method","vert_crs","lpc_link","lpc_category"]
R={"stage":"official USGS LPC REST polygon strict support V3","status":"START","url":URL,"actual_geometry_admitted":False,"transfers":[],"limitations":["Official REST polygon coverage, not decoded LAZ coverage or physical accessibility.","Exact CSV metadata match only, no inferred EPT aliases.","No precise FWS locations transmitted or exported; queries use only public workunit IDs.","No ecological fit."]}
S=requests.Session()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))
    (O/"report.json").write_text(s+"\n");print("FWS_COMPLETE_CATALOG_REPORT="+s,flush=True)
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
import io, urllib.parse
from pyproj import CRS
from shapely.geometry import box, Point
from shapely.ops import unary_union
TNM="https://tnmaccess.nationalmap.gov/api/v1/"
DATASET="Lidar Point Cloud (LPC)"
TILE_CAP=64*1024**2
TOTAL_LAZ_CAP=512*1024**2
TILE_META_CAP=256*1024**2
ALLOWED={"rockyweb.usgs.gov","prd-tnm.s3.amazonaws.com","s3.amazonaws.com","s3.us-west-2.amazonaws.com"}
def canon(u):
    if not isinstance(u,str):return None
    p=urllib.parse.urlparse(u.strip())
    if p.scheme!="https" or p.hostname not in ALLOWED or p.username or p.password or p.query or p.fragment:return None
    path=urllib.parse.unquote(p.path)
    if not path.startswith("/") or any(x in (".","..") for x in path.split("/")):return None
    return p.hostname,path.rstrip("/")
def belongs(u,link):
    a,b=canon(u),canon(link)
    return bool(a and b and a[0]==b[0] and a[1].startswith(b[1]+"/") and a[1].lower().endswith(".laz"))
import time
LAST_REQUEST=0.
def meta_get(endpoint,params,rec):
    global LAST_REQUEST
    log=R["tile_catalog_transfers"]
    cap=min(16*1024**2,512*1024**2-sum(x.get("bytes",0) for x in log))
    need(len(log)<240 and cap>0,"complete catalog budget")
    row={"endpoint":endpoint,"workunit_id":rec.get("workunit_id"),"offset":params.get("offset")};log.append(row)
    delay=1.-(time.monotonic()-LAST_REQUEST)
    if delay>0:time.sleep(delay)
    LAST_REQUEST=time.monotonic()
    with S.get(TNM+endpoint,params=params,stream=True,timeout=(20,75),allow_redirects=False) as q:
        row["http"]=q.status_code
        row["retry_after"]=q.headers.get("Retry-After")
        if q.status_code in (401,403,429):
            R["tile_stage"]="STOP_CATALOG_ACCESS_OR_RATE_LIMIT"
            save();raise ValueError("catalog access/rate-limit stop "+str(q.status_code))
        need(q.status_code==200,"catalog HTTP "+str(q.status_code))
        data=bytearray()
        for chunk in q.iter_content(65536):
            data.extend(chunk);row["bytes"]=len(data)
            need(len(data)<=cap,"catalog response byte cap")
        row["sha256"]=hashlib.sha256(data).hexdigest()
    return json.loads(data)
def find_tags(j):
    tags=set()
    def visit(x):
        if isinstance(x,dict):
            if isinstance(x.get("sbDatasetTag"),str):tags.add(x["sbDatasetTag"])
            for y in x.values():visit(y)
        elif isinstance(x,list):
            for y in x:visit(y)
    visit(j);return tags
def fixed_cells(d,geoms):
    tree=STRtree(geoms);rows=[];touched=set()
    for x,y in sorted(map(tuple,d[f.K].drop_duplicates().itertuples(index=False,name=None))):
        poly=box(x*6000,y*6000,(x+1)*6000,(y+1)*6000)
        ids=tree.query(poly,predicate="intersects")
        pieces=[geoms[int(i)].intersection(poly) for i in ids]
        ar=unary_union(pieces).area/poly.area if pieces else 0.
        pts=[Point((x+u)*6000,(y+v)*6000) for u in (1/6,1/2,5/6) for v in (1/6,1/2,5/6)]
        if ar>=.95 and all(len(tree.query(p,predicate="covered_by"))>0 for p in pts):
            rows.append((x,y,poly,pts))
            touched.update(int(i) for i in ids if geoms[int(i)].intersection(poly).area>0)
    return rows,sorted(touched)
def tile_gate(d,geoms,names,validids,t):
    prior=json.loads((pathlib.Path(__file__).resolve().parent/"FWS_NATIVE_LPC_TILE_GATE_RECEIPT_V1.json").read_text())
    old={x["workunit_id"]:x for x in prior["tile_workunits"]}
    need(prior["audit"]["run_id"]==45770786282 and len(old)==14,"prior receipt identity")
    need(sum(x["reported_total"] for x in old.values())==110808 and sum(math.ceil(x["reported_total"]/500) for x in old.values())==229,"frozen page budget")
    cells,touched=fixed_cells(d,geoms)
    need(len(cells)==57 and len(touched)==14 and set(validids[i] for i in touched)==set(old),"strict cell and workunit replay")
    R.update(tile_catalog_transfers=[],tile_workunits=[],tile_stage="COMPLETE_CATALOG_START",original_strict_candidate_cells=57,relevant_workunits=14,prior_run=45770786282,prior_reported_total=110808,prior_page_budget=229,no_native_LAZ_requests=True)
    save()
    tags=find_tags(meta_get("datasets",{},{}))
    need(DATASET in tags,"official LPC dataset tag missing")
    R["dataset_tag_verified"]=True
    to4326=Transformer.from_crs(6933,4326,always_xy=True)
    to6933=Transformer.from_crs(4326,6933,always_xy=True)
    pts=[p for _,_,_,ps in cells for p in ps];pointtree=STRtree(pts)
    tile_geoms=[];tile_urls=[];all_urls=set()
    for i in touched:
        key=validids[i];nm=names[i];row=t.loc[key];link=str(row.lpc_link).strip();p=old[key]
        need(nm==p["workunit_name"] and link==p["official_lpc_link"] and canon(link) is not None,"official workunit lineage replay")
        total=int(p["reported_total"]);pages=math.ceil(total/500)
        rec={"workunit_id":key,"workunit_name":nm,"status":"START","expected_total":total,"planned_pages":pages,"pages":0,"returned_products":0,"strict_url_products":0,"valid_bbox_products":0,"prior_prefix_verified":False}
        R["tile_workunits"].append(rec);save()
        bb=to4326.transform_bounds(*geoms[i].bounds,densify_pts=21)
        seen=set();products={};stops=collections.Counter()
        for page in range(pages):
            q=meta_get("products",{"datasets":DATASET,"bbox":",".join(map(str,bb)),"q":nm,"prodFormats":"LAZ","max":500,"offset":page*500},rec)
            need(isinstance(q,dict) and isinstance(q.get("items"),list) and "errorMessage" not in q,"product schema")
            need(int(q.get("total",-1))==total,"catalog total changed")
            items=q["items"]
            need(len(items)==min(500,total-page*500),"premature or oversized page")
            rec["pages"]+=1;rec["returned_products"]+=len(items)
            for item in items:
                url=item.get("downloadURL")
                need(isinstance(url,str) and bool(url) and url not in seen,"missing or duplicate product URL")
                seen.add(url)
                if not belongs(url,link):
                    stops["not_exact_official_lpc_descendant"]+=1;continue
                rec["strict_url_products"]+=1
                try:
                    box0=item["boundingBox"];lo,bo,hi,top=[float(box0[k]) for k in ("minX","minY","maxX","maxY")]
                    need(-180<=lo<hi<=180 and -90<=bo<top<=90,"product bbox")
                    geom=transform(to6933.transform,box(lo,bo,hi,top)).intersection(geoms[i])
                    need(not geom.is_empty and geom.area>0 and geom.is_valid and geom.geom_type in ("Polygon","MultiPolygon"),"tile clipped bbox")
                except Exception:
                    stops["invalid_product_bbox"]+=1;continue
                rec["valid_bbox_products"]+=1;products[url]=geom
            if rec["pages"]==p["pages"]:
                need(all(rec[k]==p[k] for k in ("returned_products","strict_url_products","valid_bbox_products")),"prior catalog prefix count changed")
                rec["prior_prefix_verified"]=True
            rec["stops"]=dict(stops)
            if rec["pages"]%10==0:
                print("CATALOG_V2_PAGE",key,rec["pages"],pages,flush=True);save()
        need(rec["prior_prefix_verified"] and len(seen)==total,"incomplete inventory")
        need(not set(products)&all_urls,"duplicate valid URL across workunits")
        all_urls.update(products)
        tile_geoms.extend(products.values());tile_urls.extend(products.keys())
        rec["bbox_tiles_covering_candidate_centers"]=sum(bool(len(pointtree.query(g,predicate="intersects"))) for g in products.values())
        rec.update(status="EXHAUSTED_REPORTED_CATALOG",search_exhausted=True)
        print("CATALOG_V2_WORKUNIT="+json.dumps(rec),flush=True);save()
    need(sum(x["returned_products"] for x in R["tile_workunits"])==110808 and sum(x["pages"] for x in R["tile_workunits"])==229,"full fixed page census")
    u=pd.DataFrame([(x,y) for x,y,_,_ in cells],columns=f.K)
    q=d.merge(u,on=f.K,validate="many_to_one")
    R["tile_catalog_bbox_support"]=n.arm(q,tile_geoms,tile_urls)
    R["catalog_summary"]={"valid_tile_bboxes":len(tile_geoms),"workunits_exhausted":len(R["tile_workunits"]),"returned_products":110808,"actual_catalog_bytes":sum(x.get("bytes",0) for x in R["tile_catalog_transfers"])}
    R["tile_stage"]="COMPLETE_CATALOG_ONLY";R["actual_geometry_admitted"]=False
    save()
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
    native=R["arms"]["native_LPC_strict"]
    need(len(validids)==575 and native["cells"]==57 and native["support"]["comparisons"]==2595 and native["support"]["comparison_blocks"]==9 and native["passes_original_support"],"strict REST replay")
    tile_gate(d,geoms,names,validids,t)
    R["status"]="COMPLETE_CATALOG_ONLY";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180]);save();raise
    finally:f.src.P.unlink(missing_ok=True)
