"""Outcome-blind FWS survey-cell overlap with public 3DEP EPT index."""
import collections,hashlib,json,pathlib,sys,urllib.parse
import numpy as np,pandas as pd,requests
from pyproj import Transformer
from shapely.geometry import shape,box,Point
from shapely.ops import transform,unary_union
from shapely.strtree import STRtree
from shapely import make_valid
import fws_coarse_profile_diagnostic_v1 as f
O=pathlib.Path("fws_ept_colocation");O.mkdir(exist_ok=True)
URL="https://raw.githubusercontent.com/hobu/usgs-lidar/master/boundaries/resources.geojson"
R={"stage":"FWS fixed 6km cell candidate EPT footprint overlap, no fit","status":"START","index_url":URL,"limitations":["Footprint metadata overlap is not decoded point coverage; no verified acquisition dates, vertical units or forest support.","No precise survey cells, source rows or route IDs exported.","No biological prediction, flight height or physical passability."]}
def save():
    (O/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False)+"\n")
    print("FWS_EPT_COLOCATION="+json.dumps(R,allow_nan=False),flush=True)
def need(q,msg):
    if not q:raise ValueError(msg)
def public_ept(u):
    if not isinstance(u,str):return False
    a=urllib.parse.urlparse(u)
    if a.scheme not in ("http","https") or a.username or a.password:return False
    h=a.hostname or "";p=a.path
    if h in {"s3-us-west-2.amazonaws.com","s3.us-west-2.amazonaws.com","s3.amazonaws.com"}:
        return p.startswith("/usgs-lidar-public/") and p.rstrip("/").endswith("/ept.json")
    return h in {"usgs-lidar-public.s3.amazonaws.com","usgs-lidar-public.s3-us-west-2.amazonaws.com","usgs-lidar-public.s3.us-west-2.amazonaws.com"} and p.rstrip("/").endswith("/ept.json")
def index():
    with requests.get(URL,stream=True,timeout=(20,60),allow_redirects=True) as r:
        R["index_http"]=r.status_code;need(r.status_code==200,"index HTTP")
        a=bytearray()
        for q in r.iter_content(65536):
            a.extend(q);need(len(a)<=64*1024**2,"index byte cap")
        R["index_bytes"]=len(a);R["index_sha256"]=hashlib.sha256(a).hexdigest();R["index_etag"]=r.headers.get("ETag")
    j=json.loads(a);need(j.get("type")=="FeatureCollection" and isinstance(j.get("features"),list),"index GeoJSON schema")
    fs=j["features"];need(100<=len(fs)<=20000,"index feature count")
    R["index_features"]=len(fs);R["property_keys"]=sorted(set().union(*(v.get("properties",{}).keys() for v in fs)))
    geoms=[];names=[];urls=[];stops=collections.Counter();bad=[]
    project=Transformer.from_crs(4326,6933,always_xy=True)
    for v in fs:
        p=v.get("properties",{});name=p.get("name");u=p.get("url")
        if not isinstance(name,str) or not name.strip() or not public_ept(u):
            stops["invalid_project_or_public_ept_url"]+=1;continue
        try:
            g=shape(v["geometry"])
            if not g.is_valid:g=make_valid(g)
            if g.is_empty or g.geom_type not in ("Polygon","MultiPolygon"):raise ValueError("nonpolygon")
            lo,bo,hi,to=g.bounds
            if not(-180<=lo<=hi<=180 and -90<=bo<=to<=90):raise ValueError("not WGS84 bounds")
            gg=transform(project.transform,g)
            if gg.is_empty or not gg.is_valid or not np.isfinite(gg.area) or gg.area<=0:raise ValueError("invalid transformed geometry")
        except Exception as e:stops["invalid_geometry"]+=1;continue
        names.append(name);urls.append(u);geoms.append(gg)
    R["index_exclusions"]=dict(stops);R["usable_features"]=len(geoms);R["unique_project_names"]=len(set(names));R["duplicate_project_names"]=len(names)-len(set(names))
    need(len(geoms)>=100,"insufficient recognized public EPT polygons")
    # Multiple features for a project are retained as geometry parts; conflicting URLs stop.
    nn=collections.defaultdict(set)
    for n,u in zip(names,urls):nn[n].add(u)
    need(all(len(v)==1 for v in nn.values()),"conflicting URL for project name")
    save();return geoms,names
def main():
    d=f.source_rows()
    ct,z,gb,gr,taxa,s=f.labels_and_pairs(d);R["original_support"]=s
    need(len(d)==8816 and len(d[f.K].drop_duplicates())==241 and s["comparisons"]==10480 and s["comparison_blocks"]==24,"frozen observation support")
    geoms,names=index();tree=STRtree(geoms);out=[]
    for x,y in sorted(map(tuple,d[f.K].drop_duplicates().itertuples(index=False,name=None))):
        cell=box(x*6000,y*6000,(x+1)*6000,(y+1)*6000)
        ids=tree.query(cell,predicate="intersects")
        gg=[geoms[int(i)].intersection(cell) for i in ids]
        ar=float(unary_union(gg).area/cell.area) if gg else 0.
        need(-1e-8<=ar<=1+1e-8,"area range")
        n=0;proj=set()
        for u in (1/6,1/2,5/6):
            for v in (1/6,1/2,5/6):
                pt=Point((x+u)*6000,(y+v)*6000)
                pp=tree.query(pt,predicate="covered_by")
                n+=int(len(pp)>0);proj.update(names[int(i)] for i in pp)
        out.append((x,y,min(1.,max(0.,ar)),n,len(proj),tuple(sorted(proj))))
    u=pd.DataFrame(out,columns=f.K+["area_fraction","covered_positions","project_count","project_names"])
    assert len(u)==241
    R["area_fraction_quantiles"]=np.quantile(u.area_fraction,[0,.05,.25,.5,.75,.95,1]).tolist()
    R["covered_position_histogram"]={str(k):int(v) for k,v in sorted(u.covered_positions.value_counts().items())}
    R["cell_project_count_histogram"]={str(k):int(v) for k,v in sorted(u.project_count.value_counts().items())}
    R["matched_project_names_count"]=len(set().union(*map(set,u.project_names)))
    arms={"any_position":u.covered_positions.ge(1),"at_least_5_positions":u.covered_positions.ge(5),"all_9_positions":u.covered_positions.eq(9),"area95":u.area_fraction.ge(.95),"all_9_and_area95":u.covered_positions.eq(9)&u.area_fraction.ge(.95)}
    R["arms"]={}
    for k,m in arms.items():
        q=d.merge(u.loc[m,f.K],on=f.K,validate="many_to_one")
        _,_,_,_,_,s=f.labels_and_pairs(q)
        R["arms"][k]={"cells":int(m.sum()),"records":len(q),"projects":len(set().union(*map(set,u.loc[m,"project_names"]))) if m.any() else 0,"support":s,"passes_original_support":bool(f.passes(s))}
    R["status"]="COMPLETE_CANDIDATE_SUPPORT_ONLY";R["actual_point_geometry_admitted"]=False;save()
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:250]);save();raise
    finally:f.src.P.unlink(missing_ok=True)
