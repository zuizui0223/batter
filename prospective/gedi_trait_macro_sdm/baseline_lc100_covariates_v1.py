"""Separate LC100 forest-class sensitivity source. Full source MD5; no DLT equivalence."""
import collections,hashlib,json,math,pathlib
import numpy as np,pandas as pd,rasterio,requests
from rasterio.windows import Window,from_bounds
from pyproj import Transformer
OUT=pathlib.Path("baseline_lc100");OUT.mkdir(exist_ok=True)
SRC=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
PIN="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
NAME="PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
MD5="6898fbe3fb46a1110cd65e3a81ed7624"
BUDGET=2_100_000_000
DOI="10.5281/zenodo.3939050"
CLASSES={
 "lc100_broadleaf_class_fraction":[112,114,122,124],
 "lc100_needleleaf_class_fraction":[111,113,121,123],
 "lc100_mixed_class_fraction":[115,125],
 "lc100_other_forest_class_fraction":[116,126]}
KNOWN=[20,30,40,50,60,70,80,90,100,200,*[x for v in CLASSES.values() for x in v]]
report={"stage":"alternative forest-class covariates, no ecological fit","mode":"leaf","source_variant":"LC100_2019_DISCRETE_NOT_DLT","source_doi":DOI,"source_name":NAME,"published_md5":MD5,"source_semantics":"Whole-landscape area fractions of 100m open/closed forest classes, not canopy leaf cover; distinct alternative to DLT","input_sha256":PIN,"status":"START","classes":CLASSES,"unknown_codes":[0,255],"valid_classes":KNOWN}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("LC100_ENV_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def acquire():
    response=requests.get("https://zenodo.org/api/records/3939050",timeout=(20,60))
    response.raise_for_status();doc=response.json()
    assert doc.get("doi")==DOI and doc.get("metadata",{}).get("access_right") in ("open",None)
    f=[v for v in doc["files"] if v["key"]==NAME];assert len(f)==1
    f=f[0];size=int(f["size"]);assert 0<size<=BUDGET and f["checksum"]=="md5:"+MD5
    # Official record file endpoint; no authorization supplied or bypass.
    url="https://zenodo.org/records/3939050/files/"+NAME+"?download=1"
    report["source_metadata"]={"record_id":doc["id"],"size":size,"checksum":f["checksum"],"url":url,"license":doc.get("metadata",{}).get("license")};save()
    p=pathlib.Path(NAME)
    m=hashlib.md5();h=hashlib.sha256();n=0;next_log=200_000_000
    with requests.get(url,headers={"Accept-Encoding":"identity"},stream=True,timeout=(20,120)) as r:
        r.raise_for_status()
        if r.status_code!=200 or "text/html" in r.headers.get("Content-Type","").lower():raise ValueError("not original raster download")
        with p.open("wb") as out:
            for b in r.iter_content(2**20):
                if not b:continue
                n+=len(b)
                if n>size or n>BUDGET:raise ValueError("download exceeds published size")
                m.update(b);h.update(b);out.write(b)
                if n>=next_log:print("LC100_DOWNLOAD_BYTES",n,size,flush=True);next_log+=200_000_000
    assert n==size and m.hexdigest()==MD5,"published source integrity check failed"
    report["download"]={"bytes":n,"md5":m.hexdigest(),"sha256":h.hexdigest(),"full_published_md5_verified":True};save()
    return p
def main():
    assert sha(SRC)==PIN
    roster=sorted(["5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"])
    a=pd.read_csv(SRC,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
    a=a[a.forest_profile_support.astype(str).str.lower().eq("true")&a.species_key.isin(roster)&a.dataset_key.ne("")&a.year.str.fullmatch(r"20[0-9]{2}")]
    K=["cell_x","cell_y"];u=a[K].drop_duplicates().sort_values(K).reset_index(drop=True);assert len(u)==1796
    report["candidate_cells"]=len(u);save()
    p=acquire()
    I=Transformer.from_crs(6933,4326,always_xy=True);P=Transformer.from_crs(4326,6933,always_xy=True)
    ans=np.full((len(u),1+len(CLASSES)),np.nan,float);codes=collections.Counter()
    masks=hashlib.sha256()
    with rasterio.open(p) as s:
        assert s.count==1 and s.crs.to_epsg()==4326 and s.transform.a>0 and s.transform.e<0 and s.transform.b==s.transform.d==0
        assert .0008<=s.transform.a<=.0012 and .0008<=-s.transform.e<=.0012,"unexpected native nominal 100m grid"
        assert math.isclose(s.scales[0],1,abs_tol=1e-8) and math.isclose(s.offsets[0],0,abs_tol=1e-8)
        report["raster"]={"shape":[s.height,s.width],"crs":str(s.crs),"transform":list(s.transform),"dtype":s.dtypes[0],"nodata":s.nodata,"scale":float(s.scales[0]),"offset":float(s.offsets[0])};save()
        for i,row in enumerate(u.itertuples(index=False)):
            x,y=int(row.cell_x),int(row.cell_y)
            l,b,r,t=I.transform(x*1000,y*1000)[0],I.transform(x*1000,y*1000)[1],I.transform((x+1)*1000,(y+1)*1000)[0],I.transform((x+1)*1000,(y+1)*1000)[1]
            if l<s.bounds.left or r>s.bounds.right or b<s.bounds.bottom or t>s.bounds.top:continue
            w=from_bounds(l,b,r,t,s.transform)
            c0=max(0,math.floor(w.col_off));c1=min(s.width,math.ceil(w.col_off+w.width))
            r0=max(0,math.floor(w.row_off));r1=min(s.height,math.ceil(w.row_off+w.height))
            if c1<=c0 or r1<=r0:continue
            z=s.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
            xs=s.transform.c+np.arange(c0,c1+1)*s.transform.a;ys=s.transform.f+np.arange(r0,r1+1)*s.transform.e
            xx,_=P.transform(xs,np.zeros_like(xs));_,yy=P.transform(np.zeros_like(ys),ys)
            wx=np.maximum(0,np.minimum((x+1)*1000,xx[1:])-np.maximum(x*1000,xx[:-1]))
            wy=np.maximum(0,np.minimum((y+1)*1000,yy[:-1])-np.maximum(y*1000,yy[1:]))
            area=wy[:,None]*wx[None,:]
            assert abs(area.sum()-1e6)<1e-3,"native projected area accounting"
            a=z.data;obs=~np.ma.getmaskarray(z)&np.isfinite(a)&(area>0)
            cv,ct=np.unique(a[obs],return_counts=True)
            assert np.isin(cv,KNOWN+[0,255]).all(),"unpublished class codes"
            codes.update({str(int(k)):int(n) for k,n in zip(cv,ct)})
            valid=obs&np.isin(a,KNOWN)
            den=float(area[valid].sum());ans[i,0]=den/1e6
            masks.update(np.ascontiguousarray(a).tobytes());masks.update(np.ascontiguousarray(valid).tobytes())
            if .95<=den/1e6<=1.000001:
                ans[i,1:]=[float(area[valid&np.isin(a,cl)].sum())/den for cl in CLASSES.values()]
                assert (ans[i,1:]>=0).all() and ans[i,1:].sum()<=1.000001
        report["selected_window_value_mask_sha256"]=masks.hexdigest()
    u["leaf_valid_fraction"]=ans[:,0]
    for j,k in enumerate(CLASSES,1):u[k]=ans[:,j]
    u["leaf_support"]=np.isfinite(ans).all(1)&(ans[:,0]>=.95)&(ans[:,0]<=1.000001)
    q=OUT/"cell_covariates.csv.gz";u.to_csv(q,index=False,compression={"method":"gzip","mtime":0})
    report.update(status="LC100_ALTERNATIVE_COMPLETE",valid_cells=int(u.leaf_support.sum()),observed_codes=dict(codes),output_sha256=sha(q),original_DLT_acquired=False)
    save()
try:main()
except Exception as e:
    report.update(status="LC100_SOURCE_STOP",error_type=type(e).__name__,error=str(e)[:240] if not isinstance(e,requests.RequestException) else "public source transport failure",http_status=e.response.status_code if isinstance(e,requests.HTTPError) and e.response is not None else None)
    save();raise
