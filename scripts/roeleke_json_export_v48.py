"""V48 format-only adapter, exact public export, no raw data publication."""
import hashlib,json,pathlib,re,math
import pandas as pd
import numpy as np
import roeleke_functional_space_v46 as v46
from roeleke_public_export_v47 import URL,SHA,SIZE
from functional_space_external_v45 import url_same
from bayer_field_join_v17 import fetch
OUT=pathlib.Path("results/roeleke_json_export_v48.json")
PAIRS=[("location_long","location_lat"),("longitude","latitude"),("lon","lat")]
CRS_NAMES={"EPSG:4326","URN:OGC:DEF:CRS:EPSG::4326","URN:OGC:DEF:CRS:EPSG:6.6:4326","CRS84","OGC:CRS84","URN:OGC:DEF:CRS:OGC:1.3:CRS84","HTTP://WWW.OPENGIS.NET/DEF/CRS/OGC/1.3/CRS84","HTTP://WWW.OPENGIS.NET/DEF/CRS/EPSG/0/4326"}
def unique_obj(pairs):
    r={}
    for k,v in pairs:
        if k in r:raise ValueError("duplicate JSON key")
        r[k]=v
    return r
def invalid_constant(s):raise ValueError("nonstandard JSON numeric constant")
def scalar(x):
    if x is None:return ""
    if isinstance(x,(str,int,float,bool)):
        if isinstance(x,float) and not math.isfinite(x):raise ValueError("nonfinite numeric value")
        return str(x)
    raise ValueError("nested data in scalar property")
def canon_record(x):
    if not isinstance(x,dict):raise ValueError("not record object")
    y={}
    for k,v in x.items():
        n=v46.canonical(k)
        if not n or n in y:raise ValueError("ambiguous normalized field")
        y[n]=scalar(v)
    return y
def check_crs(x):
    c=x.get("crs")
    if c is None:return "RFC7946 default longitude latitude"
    if not isinstance(c,dict) or c.get("type")!="name":raise ValueError("unknown CRS encoding")
    n=str(c.get("properties",{}).get("name","")).upper()
    if n not in CRS_NAMES:raise ValueError("unsupported CRS")
    return "explicit "+n
def schema_diagnostic(x):
    o={"root_type":type(x).__name__}
    # Restrict diagnostics to structural information, not arbitrary property values.
    if isinstance(x,dict):
        known={"type","features","crs","bbox","numberMatched","numberReturned","totalFeatures","timeStamp","data","results","records","objects","download_url","url","error","detail","success","message"}
        o["recognized_root_keys"]=sorted(set(x)&known);o["root_key_count"]=len(x)
        o["known_container_shapes"]={k:{"type":type(x[k]).__name__,"length":len(x[k]) if isinstance(x[k],(list,dict)) else None} for k in known&set(x)}
        if x.get("type") in ("FeatureCollection","Feature","Point"):o["geojson_type"]=x["type"]
        if isinstance(x.get("features"),list) and x["features"]:
            f=x["features"][0]
            if isinstance(f,dict):
                p=f.get("properties")
                if isinstance(p,dict):
                    o["first_property_count"]=len(p);o["recognized_properties"]=sorted(set(v46.canonical(k) for k in p)&set(v46.REQUIRED+["altitude_asl","approach","social_calls","n_con_calls","hd_calls","ogc_fid"]))
                g=f.get("geometry");o["first_geometry_type"]=g.get("type") if isinstance(g,dict) and g.get("type") in ("Point","MultiPoint","LineString","Polygon") else type(g).__name__
    elif isinstance(x,list):
        o["length"]=len(x)
        if x and isinstance(x[0],dict):o["recognized_first_fields"]=sorted(set(v46.canonical(k) for k in x[0])&set(v46.REQUIRED+[k for p in PAIRS for k in p]))
    return o
def convert(x):
    rows=[];info={}
    if isinstance(x,dict) and x.get("type")=="FeatureCollection":
        info["format"]="GeoJSON FeatureCollection";info["coordinate_definition"]=check_crs(x)
        fs=x.get("features")
        if not isinstance(fs,list) or not fs:raise ValueError("empty or invalid feature collection")
        for f in fs:
            if not isinstance(f,dict) or f.get("type")!="Feature":raise ValueError("invalid feature")
            p=canon_record(f.get("properties"))
            if not all(k in p for k in v46.REQUIRED):raise ValueError("required feature property absent")
            g=f.get("geometry");xy=None
            if g is not None:
                if not isinstance(g,dict) or g.get("type")!="Point":raise ValueError("unsupported geometry")
                c=g.get("coordinates")
                if not isinstance(c,list) or len(c) not in (2,3) or not all(type(v) in (int,float) and math.isfinite(v) for v in c):raise ValueError("invalid Point coordinates")
                xy=c[:2]
            for a,b in PAIRS:
                if a in p or b in p:
                    if a not in p or b not in p:raise ValueError("partial redundant coordinate pair")
                    if xy is not None and p[a]!="" and p[b]!="":
                        if not np.allclose([float(p[a]),float(p[b])],xy,rtol=0,atol=1e-7):raise ValueError("coordinate disagreement")
                    del p[a];del p[b]
            p["lon"]=scalar(xy[0]) if xy is not None else "";p["lat"]=scalar(xy[1]) if xy is not None else ""
            rows.append(p)
        for k in ("numberMatched","numberReturned","totalFeatures"):
            if k in x and isinstance(x[k],int) and x[k]>=0:
                info[k]=x[k]
                if x[k]!=len(rows):raise ValueError("partial feature collection")
    elif isinstance(x,list) and x:
        info["format"]="JSON records";info["coordinate_definition"]="explicit named lon/lat fields"
        rows=[canon_record(r) for r in x]
        keys=set(rows[0]);pairs=[p for p in PAIRS if set(p)<=keys]
        if len(pairs)!=1 or not set(v46.REQUIRED)<=keys or any(set(r)!=keys for r in rows):raise ValueError("heterogeneous or unsupported records array")
    else:raise ValueError("unsupported JSON root; no guessed nesting")
    d=pd.DataFrame(rows).fillna("")
    if not all(k in d for k in v46.REQUIRED):raise ValueError("required fields absent")
    if len(d)>1000000:raise ValueError("unexpected observation count")
    return d,info
def test():
    p={k:"x" for k in v46.REQUIRED}
    f={"type":"Feature","properties":p,"geometry":{"type":"Point","coordinates":[13.5,52.]}}
    x={"type":"FeatureCollection","features":[f,{"type":"Feature","properties":p,"geometry":None}]}
    d,info=convert(x);assert len(d)==2 and d.lon.tolist()==["13.5",""]
    y=dict(x,crs={"type":"name","properties":{"name":"EPSG:3857"}})
    for bad in (y,{"type":"FeatureCollection","features":[dict(f,geometry={"type":"LineString","coordinates":[]})]}):
        try:convert(bad)
        except ValueError:pass
        else:raise AssertionError("invalid geometry/CRS accepted")
    try:json.loads('{"a":1,"a":2}',object_pairs_hook=unique_obj)
    except ValueError:pass
    else:raise AssertionError("duplicate keys accepted")
    d,_=convert([dict(p,longitude=13.5,latitude=52.)]);assert d.longitude.iloc[0]=="13.5"
def exact_json(routes,meta):
    r={"route":"previously_retrieved_public_export_JSON"}
    try:
        assert meta["download_url"]==URL and ("dataset_download",URL) in routes
        assert "download_resourcebase" in meta["perms"] and meta["is_published"]
        b,final=fetch(url_same(URL,v46.BASE),SIZE)
        r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
        assert len(b)==SIZE and r["sha256"]==SHA,"public export identity drift"
        x=json.loads(b.decode("utf-8-sig"),object_pairs_hook=unique_obj,parse_constant=invalid_constant)
        r["structure"]=schema_diagnostic(x)
        d,info=convert(x)
        r.update(status="JSON_ADMITTED",rows=len(d),headers=list(d.columns),format_info=info)
        return d,"dataset_download",[r]
    except Exception as e:
        r.update(status="STOP_ROUTE",error=type(e).__name__+":"+str(e)[:180]);return None,None,[r]
def run():
    test();v46.fetch_table=exact_json
    r=v46.run();r["version"]="V48";r["synthetic_tests"]="PASS"
    r["source_boundary"]="Exact public export only, no denied original asset, unchanged V46 analytical gates."
    return r
if __name__=="__main__":
    try:r=run()
    except Exception as e:r={"status":"STOP","error":type(e).__name__+":"+str(e)[:300]}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n");print(OUT.read_text())
