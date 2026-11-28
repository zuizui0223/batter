"""Measured GEDI landscape variation from pinned V5 rasters; not within-shot FHD."""
from macro_fd_v5_structure import GEDI,aggregate,edges,download
import os
from pathlib import Path
import numpy as np,requests,rasterio
def save(out):
    # Stage only; full receipt is persisted by V28.
    print("V28_ENV_STAGE="+out["status"],flush=True)
def gedi_heterogeneity(out,tx,ty):
    if not os.getenv("EARTHDATA_TOKEN"):raise RuntimeError("existing Earthdata credential unavailable")
    import earthaccess
    auth=earthaccess.login(strategy="environment",persist=False)
    if not auth.authenticated:raise RuntimeError("Earthdata session not authenticated")
    session=earthaccess.get_requests_https_session()
    rr=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"collection_concept_id":"C3043630107-ORNL_CLOUD","page_size":2000},timeout=45)
    rr.raise_for_status();entries=rr.json()["feed"]["entry"]
    out["GEDI"]={"doi":"10.3334/ORNLDAAC/2339","metrics":{}}
    arr=[];valid=[];ref=None
    for m in GEDI:
        name=f"gediv002_{m}_vf_20190417_20230316_12000m.tif"
        hit=[a for a in entries if a.get("title","").endswith(name)]
        if len(hit)!=1:
            out["GEDI"]["inventory_match"]={"metric":m,"n":len(hit),"related_titles":[a.get("title","") for a in entries if "12000m" in a.get("title","") and ("bot" in a.get("title","") or m in a.get("title",""))][:12]}
            raise ValueError("CMR exact metric not unique")
        e=hit[0];urls=sorted({v["href"] for v in e.get("links",[]) if v.get("href","").startswith("https://") and v["href"].endswith(".tif") and not v.get("inherited") and "/data#" in v.get("rel","")})
        assert len(urls)==1
        out["status"]="GEDI_DOWNLOAD_"+m;save(out)
        p=Path(name);receipt=download(session,urls[0],p,200*1024**2)
        receipt.update(granule_id=e.get("id"),title=e.get("title"));out["GEDI"]["metrics"][m]=receipt
        with rasterio.open(p) as s:
            assert s.crs.to_epsg()==6933 and s.shape==(965,2881) and s.transform.a==12000 and s.transform.e==-12000 and s.count==8
            grid=(s.shape,s.transform,s.crs)
            if ref is None:ref=grid
            assert grid==ref
            lookup={}
            for j,desc in enumerate(s.descriptions,1):
                tags=s.tags(j);labels={str(x).lower().strip().replace(" ","_") for x in [desc or "",tags.get("name",""),tags.get("long_name",""),tags.get("DESCRIPTION","")]}
                if labels&{"mean","arithmetic_mean"}:lookup["mean"]=j
                if labels&{"countf","shot_count","count","number_of_shots"}:lookup["count"]=j
            receipt["descriptions"]=list(s.descriptions);receipt["band_lookup"]=lookup
            assert set(lookup)=={"mean","count"} and len(set(lookup.values()))==2
            assert all(s.scales[j-1]==1 and s.offsets[j-1]==0 for j in lookup.values())
            a,c=s.read([lookup["mean"],lookup["count"]],masked=True).astype(float).filled(np.nan)
            g=np.isfinite(a)&np.isfinite(c)&(a>=0)&(c>=10)&(abs(c-np.rint(c))<1e-5)
            if m in ("cover-a0","pavd-bot-frac"):g&=a<=1
            arr.append(a);valid.append(g);receipt["native_valid"]=int(g.sum())
        p.unlink()
    g=np.logical_and.reduce(valid)
    sx,sy=edges(ref[1],ref[0]);v,f=aggregate(arr+[arr[0]**2,arr[3]**2],g,sx,sy,tx,ty)
    var=v[:,:,4:6]-v[:,:,[0,3]]**2
    assert np.nanmin(var)>=-1e-8
    sd=np.sqrt(np.maximum(var,0))
    v=np.concatenate([v[:,:,:4],sd],axis=2)
    out["GEDI"].update(common_native_pixels=int(g.sum()),native_shape=list(ref[0]),range_cells_ge50pct=int((f>=.5).sum()))
    return v.reshape(-1,6),f.ravel()

