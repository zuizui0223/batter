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
O=pathlib.Path("fws_native_lpc_vpc_index");O.mkdir(exist_ok=True)
URL="https://index.nationalmap.gov/arcgis/rest/services/3DEPElevationIndex/MapServer/8"
CSV_SHA=n.CSV_SHA;INDEX_SHA=n.INDEX_SHA
COLS=["OBJECTID","workunit","workunit_id","collect_start","collect_end","ql","p_method","vert_crs","lpc_link","lpc_category"]
R={"stage":"official USGS LPC REST polygon strict support V3","status":"START","url":URL,"actual_geometry_admitted":False,"transfers":[],"limitations":["Official REST polygon coverage, not decoded LAZ coverage or physical accessibility.","Exact CSV metadata match only, no inferred EPT aliases.","No precise FWS locations transmitted or exported; queries use only public workunit IDs.","No ecological fit."]}
S=requests.Session()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))
    (O/"report.json").write_text(s+"\n");print("FWS_VPC_REPORT="+s,flush=True)
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
import gzip
from html.parser import HTMLParser
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__();self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="a":
            h=dict(attrs).get("href")
            if isinstance(h,str):self.hrefs.append(h)
class SourceStop(Exception):pass
LAST_VPC_REQUEST=0.
def get_asset(url,kind,key):
    global LAST_VPC_REQUEST
    log=R["vpc_transfers"]
    limit=min(2*1024**2 if kind=="directory" else 128*1024**2,768*1024**2-sum(x.get("bytes",0) for x in log))
    need(len(log)<28 and limit>0,"VPC metadata budget")
    need(canon(url) is not None,"unverified official URL")
    row={"workunit_id":key,"kind":kind,"url":url};log.append(row)
    delay=2.-(time.monotonic()-LAST_VPC_REQUEST)
    if delay>0:time.sleep(delay)
    LAST_VPC_REQUEST=time.monotonic()
    try:
        with S.get(url,headers={"Accept-Encoding":"identity"},stream=True,timeout=(20,100),allow_redirects=False) as q:
            row["http"]=q.status_code;row["retry_after"]=q.headers.get("Retry-After");row["etag"]=q.headers.get("ETag");row["last_modified"]=q.headers.get("Last-Modified")
            if q.status_code in (401,403,429) or q.status_code>=500:raise SourceStop("official metadata HTTP "+str(q.status_code))
            if q.status_code!=200:return None
            declared=q.headers.get("Content-Length")
            if declared is not None:need(int(declared)<=limit,"VPC declared cap")
            data=bytearray()
            for chunk in q.iter_content(1024**2):
                data.extend(chunk);row["bytes"]=len(data)
                need(len(data)<=limit,"VPC response cap")
            if declared is not None and q.headers.get("Content-Encoding","identity")=="identity":need(len(data)==int(declared),"VPC truncated")
            row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            return data
    except requests.RequestException as e:
        row["error_type"]=type(e).__name__
        raise SourceStop("metadata transport stop") from e
def choose_vpc(raw,link,nm):
    p=LinkParser();p.feed(raw.decode("utf-8",errors="strict"))
    urls=set()
    for href in p.hrefs:
        u=urllib.parse.urljoin(link.rstrip("/")+"/",href);a,b=canon(u),canon(link)
        if a and b and a[0]==b[0] and a[1].startswith(b[1]+"/") and a[1].rsplit("/",1)[-1]==nm+".vpc":urls.add(u)
    return next(iter(urls)) if len(urls)==1 else None,len(urls)
def feature_bbox(v):
    b=v.get("bbox")
    if isinstance(b,list) and len(b) in (4,6):
        try:
            z=[float(x) for x in b];need(np.isfinite(z).all(),"bbox finite")
            lo,bo,hi,top=(z[0],z[1],z[2],z[3]) if len(z)==4 else (z[0],z[1],z[3],z[4])
            need(-180<=lo<hi<=180 and -90<=bo<top<=90,"bbox ranges")
            return (lo,bo,hi,top),"bbox"
        except Exception:pass
    g=shape(v.get("geometry"))
    need(not g.is_empty and g.is_valid and g.geom_type in ("Polygon","MultiPolygon"),"fallback polygon")
    lo,bo,hi,top=g.bounds;need(-180<=lo<hi<=180 and -90<=bo<top<=90,"geometry WGS84")
    return (lo,bo,hi,top),"geometry_bounds"
def public_checkpoint(rec,rows):
    out=O/"public_tile_indices";out.mkdir(exist_ok=True)
    p=out/(rec["workunit_id"]+".jsonl.gz")
    with p.open("wb") as h:
        with gzip.GzipFile(fileobj=h,mode="wb",mtime=0,filename="") as f:
            for r in rows:f.write((json.dumps(r,separators=(",",":"),allow_nan=False)+"\n").encode())
    rec["public_index_sha256"]=hashlib.sha256(p.read_bytes()).hexdigest()
    rec["public_index_path"]=str(p.relative_to(O))
    rec["public_index_rows"]=len(rows)
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
    cells,touched=fixed_cells(d,geoms)
    need(len(cells)==57 and len(touched)==14 and set(validids[i] for i in touched)==set(old),"strict cell/workunit replay")
    R.update(vpc_transfers=[],vpc_workunits=[],tile_stage="VPC_INDEX_START",original_strict_candidate_cells=57,relevant_workunits=14,no_native_LAZ_requests=True)
    save()
    to6933=Transformer.from_crs(4326,6933,always_xy=True)
    tile_geoms=[];tile_urls=[];all_urls=set();global_stop=None
    for i in touched:
        key=validids[i];nm=names[i];link=str(t.loc[key].lpc_link).strip();p=old[key]
        need(nm==p["workunit_name"] and link==p["official_lpc_link"] and canon(link) is not None,"official link replay")
        rec={"workunit_id":key,"workunit_name":nm,"expected_TNM_catalog_count":int(p["reported_total"]),"status":"START"}
        R["vpc_workunits"].append(rec)
        try:
            raw=get_asset(link.rstrip("/")+"/","directory",key)
            if raw is None:rec["status"]="STOP_DIRECTORY_UNAVAILABLE";save();continue
            url,nlinks=choose_vpc(raw,link,nm)
            rec["explicit_vpc_links_matching_name"]=nlinks
            if not url:rec["status"]="STOP_NO_UNIQUE_LISTED_VPC";save();continue
            rec["vpc_url"]=url
            raw=get_asset(url,"vpc",key)
            if raw is None:rec["status"]="STOP_VPC_UNAVAILABLE";save();continue
            rec["vpc_sha256"]=hashlib.sha256(raw).hexdigest()
            j=json.loads(raw);need(j.get("type")=="FeatureCollection" and isinstance(j.get("features"),list),"VPC item collection")
            features=j["features"];need(0<len(features)<=100000,"VPC feature count gate")
            rec["features"]=len(features);rec["count_difference_vs_TNM"]=len(features)-int(p["reported_total"])
            rows=[];local_geoms=[];local_urls=[];stops=collections.Counter();seen=set()
            for v in features:
                if v.get("type")!="Feature":stops["invalid_feature"]+=1;continue
                props=v.get("properties") or {};asset=(v.get("assets") or {}).get("data") or {};href=asset.get("href")
                if not isinstance(href,str):stops["missing_data_asset"]+=1;continue
                u=urllib.parse.urljoin(url,href)
                if not belongs(u,link):stops["asset_not_exact_public_LPC_descendant"]+=1;continue
                if u in seen:stops["duplicate_url"]+=1;continue
                seen.add(u)
                try:bb,kind=feature_bbox(v)
                except Exception:stops["invalid_geographic_bbox"]+=1;continue
                pc=props.get("pc:count")
                if not isinstance(pc,int) or isinstance(pc,bool) or pc<0:pc=None
                native=any(props.get(k) is not None for k in ("proj:epsg","proj:code","proj:wkt2","proj:projjson"))
                stops["native_crs_metadata_present"]+=int(native);stops["point_count_metadata_present"]+=int(pc is not None);stops["bbox_source_"+kind]+=1
                rows.append({"url":u,"bbox":list(bb),"pc_count":pc,"native_crs_metadata_present":native})
                g=transform(to6933.transform,box(*bb)).intersection(geoms[i])
                if g.is_empty or g.area<=0 or not g.is_valid or g.geom_type not in ("Polygon","MultiPolygon"):
                    stops["invalid_or_empty_clipped_bbox"]+=1;continue
                if u in all_urls:stops["duplicate_across_workunits"]+=1;continue
                local_geoms.append(g);local_urls.append(u)
            rec["counts"]=dict(stops);rec["valid_public_bbox_assets"]=len(rows);rec["valid_clipped_bboxes"]=len(local_geoms)
            public_checkpoint(rec,rows)
            all_urls.update(local_urls);tile_geoms.extend(local_geoms);tile_urls.extend(local_urls)
            rec["status"]="VPC_RECEIVED_AND_AUDITED" if rows else "STOP_NO_VERIFIED_ASSETS"
            print("VPC_WORKUNIT="+json.dumps(rec),flush=True);save()
        except SourceStop as e:
            rec.update(status="STOP_METADATA_ACCESS_OR_TRANSPORT",reason=str(e)[:180]);global_stop=str(e);save();break
        except Exception as e:
            rec.update(status="STOP_VPC_SCHEMA_OR_BUDGET",error_type=type(e).__name__,reason=str(e)[:180]);global_stop=str(e);save();break
    u=pd.DataFrame([(x,y) for x,y,_,_ in cells],columns=f.K)
    q=d.merge(u,on=f.K,validate="many_to_one")
    R["tile_catalog_bbox_support"]=n.arm(q,tile_geoms,tile_urls) if tile_geoms else {"cells":0,"records":0,"passes_original_support":False,"support":{}}
    received=sum(x["status"]=="VPC_RECEIVED_AND_AUDITED" for x in R["vpc_workunits"])
    R["vpc_summary"]={"workunits_received_and_audited":received,"valid_tile_bboxes":len(tile_geoms),"workunits_attempted":len(R["vpc_workunits"]),"metadata_bytes":sum(x.get("bytes",0) for x in R["vpc_transfers"]),"complete_14_workunits":received==14}
    R["tile_stage"]="COMPLETE_VPC_INDEX_ONLY" if received==14 and not global_stop else "PARTIAL_VPC_LOWER_BOUND"
    R["actual_geometry_admitted"]=False
    R["global_stop"]=global_stop
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
    R["status"]=R["tile_stage"];save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:180]);save();raise
    finally:f.src.P.unlink(missing_ok=True)
