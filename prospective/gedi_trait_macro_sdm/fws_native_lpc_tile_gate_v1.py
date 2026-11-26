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
O=pathlib.Path("fws_native_lpc_tile_gate");O.mkdir(exist_ok=True)
URL="https://index.nationalmap.gov/arcgis/rest/services/3DEPElevationIndex/MapServer/8"
CSV_SHA=n.CSV_SHA;INDEX_SHA=n.INDEX_SHA
COLS=["OBJECTID","workunit","workunit_id","collect_start","collect_end","ql","p_method","vert_crs","lpc_link","lpc_category"]
R={"stage":"official USGS LPC REST polygon strict support V3","status":"START","url":URL,"actual_geometry_admitted":False,"transfers":[],"limitations":["Official REST polygon coverage, not decoded LAZ coverage or physical accessibility.","Exact CSV metadata match only, no inferred EPT aliases.","No precise FWS locations transmitted or exported; queries use only public workunit IDs.","No ecological fit."]}
S=requests.Session()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))
    (O/"report.json").write_text(s+"\n");print("FWS_NATIVE_TILE_REPORT="+s,flush=True)
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
import io, urllib.parse, laspy
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
def meta_get(endpoint,params,rec):
    log=R["tile_catalog_transfers"]
    cap=min(16*1024**2,TILE_META_CAP-sum(x.get("bytes",0) for x in log))
    if len(log)>=160 or cap<=0:raise ValueError("tile catalog budget")
    row={"endpoint":endpoint,"workunit_id":rec.get("workunit_id"),"offset":params.get("offset")};log.append(row)
    with S.get(TNM+endpoint,params=params,stream=True,timeout=(20,75),allow_redirects=False) as q:
        row["http"]=q.status_code
        if q.status_code!=200:raise ValueError("catalog HTTP "+str(q.status_code))
        data=bytearray()
        for chunk in q.iter_content(65536):
            data.extend(chunk)
            if len(data)>cap:raise ValueError("catalog byte cap")
        row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
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
def sample_decode(url,declared,meta):
    row={"url":url,"declared_size":declared}
    try:
        rem=TOTAL_LAZ_CAP-sum(x.get("download_bytes",0) for x in R["native_smoke_samples"])
        cap=min(TILE_CAP,rem)
        if cap<=0 or declared>cap:return {**row,"status":"STOP_LAZ_SIZE_BUDGET"}
        with S.get(url,stream=True,timeout=(20,100),allow_redirects=False) as q:
            row["http"]=q.status_code
            if q.status_code!=200:return {**row,"status":"STOP_LAZ_HTTP"}
            length=q.headers.get("Content-Length")
            if length is not None and int(length)>cap:return {**row,"status":"STOP_LAZ_DECLARED_CAP"}
            data=bytearray()
            for chunk in q.iter_content(1024**2):
                data.extend(chunk)
                row["download_bytes"]=len(data)
                if len(data)>cap:raise ValueError("LAZ byte cap")
        row["sha256"]=hashlib.sha256(data).hexdigest()
        if len(data)!=declared or (length is not None and len(data)!=int(length)):
            return {**row,"status":"STOP_LAZ_SIZE_DISAGREEMENT"}
        if data[:4]!=b"LASF":return {**row,"status":"STOP_LASF_HEADER"}
        with laspy.open(io.BytesIO(data)) as reader:
            h=reader.header
            row.update(header_points=int(h.point_count),compressed=bool(h.are_points_compressed),point_format=int(h.point_format.id),las_version=str(h.version),scales=h.scales.tolist())
            if not h.are_points_compressed or not 0<h.point_count<=10000000:return {**row,"status":"STOP_HEADER_POINT_GATE"}
            crs=h.parse_crs()
            row["las_crs"]=crs.to_string() if crs is not None else None
            cs=crs.sub_crs_list if crs is not None and crs.is_compound else [crs] if crs is not None else []
            vc=[a for a in cs if a.is_vertical]
            hc=[a for a in cs if a.is_projected or a.is_geographic]
            try:
                expected_v=CRS.from_epsg(int(str(meta.vert_crs).strip()))
                expected_h=CRS.from_epsg(int(str(meta.horiz_crs).strip()))
                vertical_ok=len(vc)==1 and vc[0].equals(expected_v)
                horizontal_ok=len(hc)==1 and hc[0].equals(expected_h)
            except Exception:vertical_ok=False;horizontal_ok=False
            row.update(vertical_crs_matches=bool(vertical_ok),horizontal_crs_matches=bool(horizontal_ok))
            cnt=0;counts=collections.Counter();minimum=np.full(3,np.inf);maximum=np.full(3,-np.inf)
            for p in reader.chunk_iterator(250000):
                a=np.column_stack([np.asarray(p.x),np.asarray(p.y),np.asarray(p.z)])
                if not np.isfinite(a).all():return {**row,"status":"STOP_NONFINITE_XYZ"}
                if len(a):minimum=np.minimum(minimum,a.min(0));maximum=np.maximum(maximum,a.max(0))
                cnt+=len(a)
                keep=~np.asarray(p.withheld,dtype=bool)
                counts.update(np.asarray(p.classification,dtype=int)[keep].tolist())
            good=cnt==h.point_count and np.all(np.abs(minimum-h.mins)<=np.abs(h.scales)+1e-7) and np.all(np.abs(maximum-h.maxs)<=np.abs(h.scales)+1e-7)
            row.update(decoded_points=int(cnt),header_bounds_match=bool(good),retained_class_counts={str(k):int(v) for k,v in sorted(counts.items())},retained_ground_points=int(counts.get(2,0)),retained_nonground_points=int(sum(v for k,v in counts.items() if k not in (2,7,18))))
            return {**row,"status":"DECODE_OK_NATIVE_CRS_MATCH" if good and horizontal_ok and vertical_ok else "DECODE_OK_CRS_OR_BOUNDS_UNRESOLVED" if good else "STOP_DECODE_COUNT_OR_BOUNDS"}
    except Exception as e:
        return {**row,"status":"STOP_LAZ_DECODE","error_type":type(e).__name__}
def tile_gate(d,geoms,names,validids,t):
    cells,touched=fixed_cells(d,geoms)
    need(len(cells)==57,"original native strict cell replay")
    R.update(tile_catalog_transfers=[],native_smoke_samples=[],tile_workunits=[],tile_stage="CATALOG_START",original_strict_candidate_cells=len(cells),relevant_workunits=len(touched))
    save()
    tags=find_tags(meta_get("datasets",{},{}))
    R["dataset_tag_verified"]=DATASET in tags
    need(DATASET in tags,"official LPC dataset tag missing")
    to4326=Transformer.from_crs(6933,4326,always_xy=True)
    to6933=Transformer.from_crs(4326,6933,always_xy=True)
    pts=[p for _,_,_,ps in cells for p in ps];pointtree=STRtree(pts)
    tiles=[];tilekeys=[]
    for i in touched:
        key=validids[i];nm=names[i];row=t.loc[key];link=str(row.lpc_link).strip()
        rec={"workunit_id":key,"workunit_name":nm,"official_lpc_link":link,"status":"START","pages":0,"returned_products":0,"strict_url_products":0,"valid_bbox_products":0,"stops":{}};R["tile_workunits"].append(rec)
        if canon(link) is None:rec["status"]="STOP_UNSUPPORTED_OFFICIAL_LINK";save();continue
        bb=to4326.transform_bounds(*geoms[i].bounds,densify_pts=21)
        products={};seen=set();stops=collections.Counter();total=None
        try:
            for page in range(6):
                q=meta_get("products",{"datasets":DATASET,"bbox":",".join(map(str,bb)),"q":nm,"prodFormats":"LAZ","max":500,"offset":page*500},rec)
                need(isinstance(q,dict) and isinstance(q.get("items"),list) and "errorMessage" not in q,"product schema")
                items=q["items"]
                rec["pages"]+=1;rec["returned_products"]+=len(items)
                if q.get("total") is not None:
                    count=int(q["total"])
                    if total is None:total=count
                    need(total==count,"catalog total changed while paging")
                for item in items:
                    url=item.get("downloadURL")
                    if not belongs(url,link):
                        stops["not_exact_official_lpc_descendant"]+=1;continue
                    if url in seen:stops["duplicate_product_url"]+=1;continue
                    seen.add(url)
                    rec["strict_url_products"]+=1
                    try:
                        b=item["boundingBox"]
                        lo,bo,hi,top=[float(b[k]) for k in ("minX","minY","maxX","maxY")]
                        need(-180<=lo<hi<=180 and -90<=bo<top<=90,"product bbox")
                        geom=transform(to6933.transform,box(lo,bo,hi,top)).intersection(geoms[i])
                        need(not geom.is_empty and geom.area>0 and geom.is_valid and geom.geom_type in ("Polygon","MultiPolygon"),"tile clipped bbox")
                    except Exception:stops["invalid_product_bbox"]+=1;continue
                    rec["valid_bbox_products"]+=1
                    try:
                        size=int(item.get("sizeInBytes"))
                        if size<=0:raise ValueError()
                    except Exception:size=None;stops["unknown_product_size"]+=1
                    products[url]=(geom,size)
                if len(items)<500 or (total is not None and (page+1)*500>=total):break
            rec["reported_total"]=total
            rec["search_exhausted"]=bool(total is not None and rec["returned_products"]>=total)
            rec["status"]="CATALOG_DISCOVERY_COMPLETE_LOWER_BOUND"
        except Exception as e:
            rec.update(status="STOP_OR_PARTIAL_CATALOG",error_type=type(e).__name__,reason=str(e)[:120])
        rec["stops"]=dict(stops)
        for url,(geom,size) in products.items():
            tiles.append(geom);tilekeys.append(url)
        rec["bbox_tiles_covering_candidate_centers"]=sum(bool(len(pointtree.query(g,predicate="intersects"))) for g,z in products.values())
        if products:
            choices=[(not bool(len(pointtree.query(g,predicate="intersects"))),size,url) for url,(g,size) in products.items() if size is not None and size<=TILE_CAP]
            if choices:
                outside,size,url=min(choices)
                sample=sample_decode(url,size,row)
                sample.update(workunit_id=key,overlaps_catalog_candidate_center=not outside)
                R["native_smoke_samples"].append(sample)
            else:rec["smoke_stop"]="NO_SIZE_ADMITTED_PRODUCT"
        save()
    # Tile-bbox support is a catalog lower bound, never actual decoded coverage.
    need(len(tilekeys)==len(tiles),"tile roster")
    if tiles:
        u=pd.DataFrame([(x,y) for x,y,_,_ in cells],columns=f.K)
        q=d.merge(u,on=f.K,validate="many_to_one")
        R["tile_catalog_bbox_support"]=n.arm(q,tiles,tilekeys)
    else:R["tile_catalog_bbox_support"]={"cells":0,"records":0,"passes_original_support":False,"support":{}}
    R["tile_stage"]="COMPLETE_CATALOG_AND_SMOKE_ONLY"
    R["actual_geometry_admitted"]=False;save()

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
    R["status"]="COMPLETE_CATALOG_AND_SMOKE_ONLY";save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180]);save();raise
    finally:f.src.P.unlink(missing_ok=True)
