"""Authenticated NASA GEDI access: measured gridded profiles and direct L2B smoke test."""
import collections, hashlib, json, logging, math, os, pathlib, sys
import numpy as np
import pandas as pd
import requests
logging.disable(logging.CRITICAL)
OUT=pathlib.Path("gedi_"+sys.argv[1]);OUT.mkdir(exist_ok=True)
report={"mode":sys.argv[1],"status":"START","token_present":bool(os.getenv("EARTHDATA_TOKEN"))}
def save():
    (OUT/"receipt.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("GEDI_STATUS",report["status"],flush=True)
def sha(path):
    with open(path,"rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def need(ok,label):
    if not ok:raise ValueError(label)
def grid(fs,session):
    import rasterio
    from rasterio.windows import Window
    report.update(doi="10.3334/ORNLDAAC/2339",concept_id="C3043630107-ORNL_CLOUD",period="2019-04-17/2023-03-16",sources={})
    src=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
    need(sha(src)=="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b","pilot hash")
    d=pd.read_csv(src,dtype={"species_key":str,"dataset_key":str,"year":str},keep_default_na=False,low_memory=False)
    roster={"5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"}
    d=d[d.forest_profile_support.astype(str).str.lower().eq("true")&d.species_key.isin(roster)&d.dataset_key.ne("")&d.year.str.fullmatch(r"20[0-9]{2}")]
    cells=d[["cell_x","cell_y"]].drop_duplicates().sort_values(["cell_x","cell_y"]).reset_index(drop=True)
    need(len(cells)==1796,"cohort")
    metrics=[f"pavd-{z}-{z+5}" for z in range(0,80,5)]+["rh-98-a0","pai-a0","cover-a0"]
    response=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"collection_concept_id":report["concept_id"],"page_size":2000},timeout=45)
    response.raise_for_status()
    entries=response.json()["feed"]["entry"]
    urls={}
    for m in metrics:
        name=f"gediv002_{m}_vf_20190417_20230316_1000m.tif"
        hits=[e for e in entries if e.get("title","").endswith(name)]
        need(len(hits)==1,"CMR inventory "+m)
        e=hits[0]
        links=sorted({l["href"] for l in e.get("links",[]) if l.get("href","").startswith("https://") and l["href"].endswith(".tif") and not l.get("inherited") and "/data#" in l.get("rel","")})
        need(len(links)==1,"CMR data link "+m)
        urls[m]=links[0]
        report["sources"][m]={"cmr_granule_id":e.get("id"),"title":e.get("title")}
    report["candidate_cells"]=len(cells);report["inventory_complete"]=True;save()
    with session.get(urls[metrics[0]],headers={"Range":"bytes=0-16383"},stream=True,timeout=(30,45)) as r:
        report["first_http_status"]=r.status_code
        magic=next(r.iter_content(chunk_size=16384),b"")[:4]
        report["tiff_magic"]=magic in (b"II*\x00",b"MM\x00*",b"II+\x00",b"MM\x00+")
        need(r.status_code==206 and report["tiff_magic"],"authenticated range")
    report["status"]="AUTHENTICATED_TIFF_RANGE_OK";save()
    ref=None;overlaps=None;native=None;values=[];counts=[]
    for m in metrics:
        report["current_metric"]=m;save()
        with rasterio.open(urls[m],opener=fs.open) as s:
            need(s.crs.to_epsg()==6933 and s.transform.a==1000 and s.transform.e==-1000 and s.transform.b==s.transform.d==0 and s.count==8,"native grid")
            g=(s.width,s.height,tuple(s.transform),str(s.crs))
            if ref is None:
                ref=g;overlaps=[];keys=set()
                for x,y in cells.itertuples(index=False,name=None):
                    l,b,r,t=x*1000,y*1000,(x+1)*1000,(y+1)*1000
                    c0=math.floor((l-s.transform.c)/1000);c1=math.ceil((r-s.transform.c)/1000)
                    r0=math.floor((s.transform.f-t)/1000);r1=math.ceil((s.transform.f-b)/1000)
                    q=[]
                    for i in range(r0,r1):
                        for j in range(c0,c1):
                            xl=s.transform.c+1000*j;yt=s.transform.f-1000*i
                            a=max(0,min(r,xl+1000)-max(l,xl))*max(0,min(t,yt)-max(b,yt-1000))/1e6
                            if a>0 and 0<=i<s.height and 0<=j<s.width:q.append(((i,j),a));keys.add((i,j))
                    overlaps.append(q)
                native=sorted(keys);ix={k:i for i,k in enumerate(native)}
                overlaps=[[(ix[k],w) for k,w in q] for q in overlaps]
                report["native_grid"]={"width":s.width,"height":s.height,"transform":list(s.transform),"crs":str(s.crs),"native_pixels":len(native)}
            need(g==ref,"grid mismatch")
            meta=report["sources"][m]
            meta["descriptions"]=list(s.descriptions)
            lookup={}
            for j,desc in enumerate(s.descriptions,1):
                tags=s.tags(j)
                labels={str(x).lower().strip().replace(" ","_") for x in [desc or "",tags.get("name",""),tags.get("long_name",""),tags.get("DESCRIPTION","")]}
                if labels.intersection({"mean","arithmetic_mean"}):lookup["mean"]=j
                if labels.intersection({"countf","shot_count","count","number_of_shots"}):lookup["countf"]=j
            meta["band_lookup"]=lookup;save()
            need(set(lookup)=={"mean","countf"} and len(set(lookup.values()))==2,"unverified band semantics")
            need(all(s.scales[j-1]==1 and s.offsets[j-1]==0 for j in lookup.values()),"scale/offset")
            vi=np.full(len(native),np.nan);co=np.full(len(native),np.nan)
            tiles=collections.defaultdict(list)
            bh,bw=s.block_shapes[lookup["mean"]-1]
            for j,(i,k) in enumerate(native):tiles[i//bh,k//bw].append((j,i,k))
            for _,qs in sorted(tiles.items()):
                i0=min(i for j,i,k in qs);i1=max(i for j,i,k in qs)
                k0=min(k for j,i,k in qs);k1=max(k for j,i,k in qs)
                a=s.read([lookup["mean"],lookup["countf"]],window=Window(k0,i0,k1-k0+1,i1-i0+1),masked=True).astype(float).filled(np.nan)
                for j,i,k in qs:vi[j],co[j]=a[:,i-i0,k-k0]
            good=np.isfinite(vi)&np.isfinite(co)&(vi>=0)&(co>=10)&(np.abs(co-np.rint(co))<1e-5)
            values.append(vi);counts.append(co)
            meta["native_valid_ge10"]=int(good.sum());meta["sample_sha256"]=hashlib.sha256(np.stack([vi,co]).tobytes()).hexdigest()
            print("GEDI_METRIC_COMPLETE",m,int(good.sum()),flush=True)
    vs=np.stack(values,axis=1);cs=np.stack(counts,axis=1)
    native_good=(np.isfinite(vs)&np.isfinite(cs)&(vs>=0)&(cs>=10)&(np.abs(cs-np.rint(cs))<1e-5)).all(1)
    # Preserve full cohort; mask jointly across all 19 layers, not separately.
    result=[]
    for q in overlaps:
        valid=[(i,w) for i,w in q if native_good[i]]
        area=sum(w for i,w in valid)
        a=np.full(len(metrics),np.nan);minc=np.nan
        if area>=.95 and area<=1.000001:
            ix=[i for i,w in valid];w=np.array([w for i,w in valid]);a=w@vs[ix]/area;minc=float(cs[ix].min())
        result.append([*a,area,minc])
    out=cells.join(pd.DataFrame(result,columns=metrics+["joint_valid_area_fraction","minimum_native_shot_count"]))
    total=out[metrics[:16]].sum(axis=1,min_count=16)
    out["PAVD_lower_fraction"]=out[metrics[:2]].sum(axis=1,min_count=2)/total.where(total>0)
    out["PAVD_centroid_m"]=(out[metrics[:16]].to_numpy()@np.arange(2.5,80,5))/total.where(total>0)
    out["gedi_support"]=out["PAVD_lower_fraction"].notna()&out["rh-98-a0"].gt(5)&out["joint_valid_area_fraction"].ge(.95)
    path=OUT/"cell_gedi_profiles.csv.gz";out.to_csv(path,index=False,compression={"method":"gzip","mtime":0})
    report.update(status="GRID_PROFILE_SUPPORT_READY",joint_native_pixels=int(native_good.sum()),eligible_cells=int(out.gedi_support.sum()),output_sha256=sha(path))
    save()
def raw(fs,session):
    import h5py
    report.update(doi="10.5067/GEDI/GEDI02_B.002",concept_id="C2142776747-LPCLOUD",note="source/schema test only, not representative sampling")
    # One deterministic granule and bounded beam slices; no full granule downloads.
    r=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"collection_concept_id":report["concept_id"],"bounding_box":"-5,39,1,44","temporal":"2020-06-01T00:00:00Z,2020-06-30T23:59:59Z","page_size":10,"sort_key":"start_date"},timeout=45)
    r.raise_for_status();entries=r.json()["feed"]["entry"];need(bool(entries),"raw inventory")
    e=sorted(entries,key=lambda a:a["title"])[0]
    links=sorted({l["href"] for l in e.get("links",[]) if l.get("href","").startswith("https://") and l["href"].endswith(".h5") and not l.get("inherited") and "/data#" in l.get("rel","")})
    need(len(links)==1,"raw data link");url=links[0]
    report["granule"]={"id":e.get("id"),"title":e.get("title")}
    with session.get(url,headers={"Range":"bytes=0-16383"},stream=True,timeout=(30,45)) as r:
        report["http_status"]=r.status_code
        magic=next(r.iter_content(chunk_size=16384),b"")[:8]
        report["hdf5_magic"]=magic==b"\x89HDF\r\n\x1a\n"
        need(r.status_code==206 and report["hdf5_magic"],"HDF5 range")
    report["status"]="AUTHENTICATED_HDF5_RANGE_OK";save()
    records=[];beam_report=[]
    with fs.open(url,mode="rb",block_size=1024*1024,cache_type="blockcache") as f:
        with h5py.File(f,"r") as h:
            for name in sorted(k for k in h if k.startswith("BEAM")):
                b=h[name];n=len(b["shot_number"]);p=b["pavd_z"];need(p.ndim==2 and p.shape[0]==n,"PAVD shape")
                # Explicit fixed sample, evenly spaced chunks of 512.
                for start in np.linspace(0,max(0,n-512),8,dtype=int):
                    sl=slice(int(start),int(start)+512)
                    lat=b["geolocation/lat_lowestmode"][sl];lon=b["geolocation/lon_lowestmode"][sl]
                    v=p[sl];q=b["l2b_quality_flag"][sl];degrade=b["geolocation/degrade_flag"][sl];sens=b["sensitivity"][sl]
                    pai=b["pai"][sl];cover=b["cover"][sl];fhd=b["fhd_normal"][sl]
                    shot=b["shot_number"][sl]
                    valid=(q==1)&(degrade==0)&(sens>=.9)&(sens<=1)&np.isfinite(lat)&np.isfinite(lon)&(abs(lat)<=90)&(abs(lon)<=180)&np.isfinite(v).all(1)&(v>=0).all(1)&np.isfinite(pai)&(pai>=0)&np.isfinite(cover)&(cover>=0)&(cover<=1)&np.isfinite(fhd)&(fhd>=0)
                    for j in np.flatnonzero(valid):
                        records.append([name,str(int(shot[j])),float(lat[j]),float(lon[j]),float(sens[j]),float(pai[j]),float(cover[j]),float(fhd[j]),*map(float,v[j])])
                    if len(records)>=256:break
                beam_report.append({"beam":name,"n_total_shots":n,"profile_bins":int(p.shape[1]),"vertical_resolution_m":float(np.asarray(b["ancillary/dz"][()]).ravel()[0])})
                if len(records)>=256:break
    report["beam_schema"]=beam_report;report["valid_shots_sample"]=len(records)
    need(bool(records),"no quality-screened sample")
    out=pd.DataFrame(records,columns=["beam","shot_number","lat","lon","sensitivity","pai","cover","fhd",*[f"pavd_z_{j}" for j in range(len(records[0])-8)]]).drop_duplicates("shot_number")
    path=OUT/"l2b_quality_sample.csv.gz";out.to_csv(path,index=False,compression={"method":"gzip","mtime":0})
    report.update(status="DIRECT_L2B_PROFILE_READ_OK",unique_shots=len(out),output_sha256=sha(path));save()
def main():
    if not report["token_present"]:report["status"]="STOP_NO_SECRET";save();return 2
    try:
        import earthaccess
        auth=earthaccess.login(strategy="environment",persist=False)
        need(auth.authenticated,"earthaccess session")
        fs=earthaccess.get_fsspec_https_session();session=earthaccess.get_requests_https_session()
        if report["mode"]=="grid":grid(fs,session)
        elif report["mode"]=="raw":raw(fs,session)
        else:raise ValueError("mode")
        return 0
    except Exception as e:
        report["last_status"]=report["status"];report["status"]="STOP_SOURCE_OR_QC";report["error_type"]=type(e).__name__
        # Do not log raw exception messages, headers, credentials, or signed URLs.
        save();return 1
if __name__=="__main__":sys.exit(main())
