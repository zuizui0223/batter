"""Official England 30m woodland metric admission; public 5km rectangles only; no model."""
import collections,csv,hashlib,io,json,math,pathlib,re,sys,tempfile,time,zipfile
import numpy as np,pandas as pd,requests,rasterio,pyogrio
from rasterio.windows import Window
from rasterio.enums import MaskFlags
from rasterio.crs import CRS
from contextlib import ExitStack
M=1024**2
O=pathlib.Path("england_woodland_structure");O.mkdir(exist_ok=True)
U="https://environment.data.gov.uk/api/file/download?fileDataSetId=3d0fd208-9069-4166-808e-875d951b8ebe&fileName=FR_E_FRD20_ReForeSt_Data_Files.zip"
LIMIT_URL="https://environment.data.gov.uk/api/file/download?fileDataSetId=5d4b2584-53b2-49f7-b96a-a7d9252e439a&fileName=ARD limitations statement 2025-12-05.pdf"
S=requests.Session()
R={"status":"START","source_url":U,"ecological_fit":False,"actual_bat_height":False,"requests":[],"limits":["Published public rectangles only; no NFI localization.","Forest raster summaries are not airspace geometry.","Date-catalog schema only, not temporal admission."]}
CSV_SHA="8556647d60d288a3e98a872afd9a5623f5c6a0d09fae84388e81b2fb47b61bd7"
PDF_SHA="7d24f15b1e4cbae840e393c28fdfeaa784f765074942f7490cd7db528f824c8c"
CSV="National Woodland Bat Survey Data 2021-24.csv"
PDF="National Woodland Bat Survey Evidence Pack 2021-24.pdf"
COL=["boundingBox_SW_x_coordinate","boundingBox_SW_y_coordinate","boundingBox_NE_x_coordinate","boundingBox_NE_y_coordinate"]
LAST=0.
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as q:
        for c in iter(lambda:q.read(4*M),b""):h.update(c)
    return h.hexdigest()
def save():
    (O/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+"\n")
    print("ENGLAND_STRUCTURE_REPORT="+json.dumps(R,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),flush=True)
def request(url,kind,rng=None):
    global LAST
    if len(R["requests"])>=180:raise ValueError("request cap")
    t=1.-(time.monotonic()-LAST)
    if t>0:time.sleep(t)
    LAST=time.monotonic()
    h={"Accept-Encoding":"identity"}
    if rng is not None:h["Range"]="bytes=%d-%d"%rng
    e={"kind":kind,"range":list(rng) if rng is not None else None};R["requests"].append(e)
    q=S.get(url,headers=h,stream=True,timeout=(20,100),allow_redirects=False)
    e.update(http=q.status_code,etag=q.headers.get("ETag"),last_modified=q.headers.get("Last-Modified"),content_length=q.headers.get("Content-Length"),content_range=q.headers.get("Content-Range"),retry_after=q.headers.get("Retry-After"))
    if q.status_code in (401,403,429) or q.status_code>=500:
        q.close();raise ValueError("official source access stop HTTP "+str(q.status_code))
    return q,e
def read_body(q,e,cap,expected=None,path=None):
    cap=min(cap,1024*M-sum(x.get("bytes",0) for x in R["requests"]))
    need(cap>0,"total transfer cap")
    h=hashlib.sha256();n=0
    f=open(path,"wb") if path else io.BytesIO()
    try:
        for c in q.iter_content(M):
            n+=len(c);e["bytes"]=n;need(n<=cap,"transfer cap")
            h.update(c);f.write(c)
        if expected is not None:need(n==expected,"truncated body")
        if q.headers.get("Content-Length") is not None and q.headers.get("Content-Encoding","identity")=="identity":need(n==int(q.headers["Content-Length"]),"declared length mismatch")
        e["sha256"]=h.hexdigest()
        return None if path else f.getvalue()
    finally:f.close()
class RemoteZip(io.RawIOBase):
    def __init__(self,total,tag,last):
        self.total=total;self.tag=tag;self.last=last;self.pos=0;self.start=-1;self.buffer=b""
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        x=offset if whence==0 else self.pos+offset if whence==1 else self.total+offset if whence==2 else -1
        need(x>=0,"invalid archive seek");self.pos=x;return x
    def read(self,n=-1):
        if n is None or n<0:n=self.total-self.pos
        n=min(n,max(0,self.total-self.pos))
        if n<=0:return b""
        ans=bytearray()
        while n>0:
            if not self.start<=self.pos<self.start+len(self.buffer):
                # Read forward from a requested offset, not entire file.
                lo=self.pos;hi=min(self.total-1,lo+8*M-1)
                q,e=request(U,"zip_range",(lo,hi))
                with q:
                    need(q.status_code==206 and q.headers.get("Content-Range")==f"bytes {lo}-{hi}/{self.total}","invalid range response")
                    need(self.tag==q.headers.get("ETag") and self.last==q.headers.get("Last-Modified"),"source version changed")
                    self.buffer=read_body(q,e,8*M,hi-lo+1);self.start=lo
            k=self.pos-self.start;c=min(n,len(self.buffer)-k)
            need(c>0,"invalid cached range")
            ans.extend(self.buffer[k:k+c]);self.pos+=c;n-=c
        return bytes(ans)
def archive(tmp):
    q,e=request(U,"zip_probe",(0,0))
    with q:
        if q.status_code==206:
            m=re.fullmatch(r"bytes 0-0/([0-9]+)",q.headers.get("Content-Range",""))
            need(m is not None and int(m.group(1))>1,"invalid range probe")
            read_body(q,e,1,1);total=int(m.group(1));R.update(zip_total_bytes=total,zip_access="bounded_ranges")
            return RemoteZip(total,e["etag"],e["last_modified"])
        need(q.status_code==200 and e["content_length"] is not None,"unsupported archive response")
        size=int(e["content_length"]);need(0<size<=1024*M,"full archive exceeds budget")
        p=tmp/"source.zip";read_body(q,e,1024*M,size,p)
        R.update(zip_total_bytes=size,zip_access="full_archive",zip_sha256=e["sha256"])
        return p
def norm(n):return re.sub(r"[^a-z0-9]","",n.lower())
def classify(n):
    a=norm(pathlib.PurePosixPath(n).stem)
    if n.lower().endswith((".tif",".tiff")):
        if "foliageheightdiversity" in a or re.search(r"(?:^|[_ -])fhd(?:[_ -]|$)",pathlib.PurePosixPath(n).stem.lower()):return "FHD"
        if "canopygapfraction" in a or re.search(r"(?:^|[_ -])cgf(?:[_ -]|$)",pathlib.PurePosixPath(n).stem.lower()):return "gap"
        if ("canopyheight" in a and ("90" in a or "p90" in a)) or re.search(r"(?:^|[_ -])(?:ch90|h90)(?:[_ -]|$)",pathlib.PurePosixPath(n).stem.lower()):return "H90"
    if n.lower().endswith(".gpkg"):
        if a=="nationallidarprogrammetilecatalogvom20172023":return "catalog_VOM"
        if a=="nationallidarprogrammetilecatalog20172024":return "catalog_FHD"
    return None
def extract(z,info,p):
    h=hashlib.sha256();n=0
    with z.open(info) as q,p.open("wb") as f:
        for b in iter(lambda:q.read(4*M),b""):
            n+=len(b);need(n<=info.file_size,"member overrun")
            f.write(b);h.update(b)
    need(n==info.file_size,"member truncation")
    return {"archive_member":info.filename,"bytes":n,"compressed_bytes":info.compress_size,"crc32":f"{info.CRC:08x}","crc_checked":True,"sha256":h.hexdigest()}
def load_support():
    p=pathlib.Path("nwbs")
    need(sha(p/CSV)==CSV_SHA and sha(p/PDF)==PDF_SHA,"NWBS pin")
    d=pd.read_csv(p/CSV)
    need(len(d)==1813 and d.siteNumber.nunique()==310 and d.locationID.nunique()==289,"source census")
    need(d.occurrenceID.is_unique and not d.duplicated(["siteNumber","scientificName"]).any(),"unique source rows")
    need(d.SRS.eq("EPSG:27700").all() and np.isfinite(d[COL]).all().all() and (d[COL]%5000==0).all().all(),"public grid")
    need((d.groupby("siteNumber")[COL+["locationID","higherGeography","startDate","endDate","monitoringPointNights"]].nunique()==1).all().all(),"source site context")
    need((d.groupby("locationID")[COL+["higherGeography"]].nunique()==1).all().all(),"public grid metadata")
    p=d[(d[COL[2]]-d[COL[0]]==5000)&(d[COL[3]]-d[COL[1]]==5000)].copy()
    u=p[["locationID","higherGeography",*COL]].drop_duplicates().sort_values("locationID")
    need(len(p)==1298 and p.siteNumber.nunique()==221 and len(u)==208 and u.higherGeography.nunique()==8,"frozen primary roster")
    R["support_input"]={"rows":len(p),"sites":p.siteNumber.nunique(),"public_grid_ids":len(u),"unique_rectangles":len(u[COL].drop_duplicates()),"regions":u.higherGeography.nunique()}
    return u
def window_grid(ds,rect,ref):
    x0,y0,x1,y1=rect
    c0=math.floor((x0-ref.c)/30);c1=math.ceil((x1-ref.c)/30)
    r0=math.floor((ref.f-y1)/30);r1=math.ceil((ref.f-y0)/30)
    xs=ref.c+30*np.arange(c0,c1);ys=ref.f-30*np.arange(r0,r1)
    wx=np.maximum(0,np.minimum(x1,xs+30)-np.maximum(x0,xs))
    wy=np.maximum(0,np.minimum(y1,ys)-np.maximum(y0,ys-30))
    w=wy[:,None]*wx[None,:];need(abs(w.sum()-25e6)<1e-5,"fractional rectangle area")
    dx=int(round((ref.c-ds.transform.c)/30));dy=int(round((ds.transform.f-ref.f)/30))
    v=ds.read(1,window=Window(c0+dx,r0+dy,c1-c0,r1-r0),boundless=True,masked=True)
    need(v.shape==w.shape,"common window shape")
    return np.asarray(v.data,dtype=float),~np.ma.getmaskarray(v),w
def summarize(paths,u):
    with ExitStack() as s:
        ds={k:s.enter_context(rasterio.open(paths[k])) for k in ("H90","gap","FHD")}
        ref=ds["H90"].transform
        R["raster_schema"]={}
        for k,d in ds.items():
            t=d.transform
            R["raster_schema"][k]={"crs":str(d.crs),"shape":[d.height,d.width],"transform":list(t),"dtype":d.dtypes[0],"nodata":str(d.nodata),"mask_flags":[str(v) for v in d.mask_flag_enums[0]],"scale":d.scales[0],"offset":d.offsets[0]}
            need(d.count==1 and d.crs==CRS.from_epsg(27700) and (t.a,t.b,t.d,t.e)==(30.,0.,0.,-30.),"native raster CRS/lattice "+k)
            need(abs((t.c-ref.c)/30-round((t.c-ref.c)/30))<1e-7 and abs((t.f-ref.f)/30-round((t.f-ref.f)/30))<1e-7,"unaligned native grids")
            need(MaskFlags.all_valid not in d.mask_flag_enums[0],"no explicit raster validity mask "+k)
            need(d.scales[0]==1 and d.offsets[0]==0,"nonidentity stored scale "+k)
        rows=[];supports={str(t):{"cells":0,"regions":set(),"blocks":set()} for t in (.5,.7,.9)}
        for rr in u.itertuples(index=False,name=None):
            key,region,*rect=rr
            arrays={};masks={};weight=None
            for k,d in ds.items():
                a,m,w=window_grid(d,rect,ref);weight=w if weight is None else weight
                need(np.array_equal(weight,w),"weight lattice mismatch")
                ok=m&(w>0);hi={"H90":150,"gap":1,"FHD":6}[k]
                need(np.isfinite(a[ok]).all() and (a[ok]>=0).all() and (a[ok]<=hi).all(),"metric out of range "+k)
                arrays[k]=a;masks[k]=ok
            common=np.logical_and.reduce(list(masks.values()));union=np.logical_or.reduce(list(masks.values()))
            cm=float(weight[common].sum());un=float(weight[union].sum())
            need(cm<=un+1e-8 and un<=25e6+1e-8,"common support area")
            row={"public_location_sha256":hashlib.sha256(str(key).encode()).hexdigest(),"common_area_ha":cm/10000,"valid_union_area_ha":un/10000,"common_fraction_of_union":cm/un if un>0 else 0.0}
            for k,a in arrays.items():row[k+"_area_weighted_mean"]=float(np.average(a[common],weights=weight[common])) if cm>0 else None
            for t,ss in supports.items():
                passed=cm>=1e6 and un>0 and cm/un>=float(t);row["passes_"+t]=passed
                if passed:ss["cells"]+=1;ss["regions"].add(region);ss["blocks"].add(((rect[0]+2500)//50000,(rect[1]+2500)//50000))
            rows.append(row)
        R["support"]={k:{"cells":v["cells"],"regions":len(v["regions"]),"blocks50":len(v["blocks"]),"passes":v["cells"]>=150 and len(v["regions"])>=6 and len(v["blocks"])>=12} for k,v in supports.items()}
        pd.DataFrame(rows).to_csv(O/"public_grid_structure.csv",index=False)
        R["derived_sha256"]=sha(O/"public_grid_structure.csv")
        R["common_area_summary_ha"]=np.quantile([r["common_area_ha"] for r in rows],[0,.25,.5,.75,1]).tolist()
def main():
    u=load_support()
    with tempfile.TemporaryDirectory() as t:
        tmp=pathlib.Path(t)
        with zipfile.ZipFile(archive(tmp)) as z:
            infos=[x for x in z.infolist() if not x.is_dir()]
            need(len(infos)<=2000 and len(set(x.filename for x in infos))==len(infos),"archive inventory gate")
            R["inventory"]=[{"name":i.filename,"bytes":i.file_size,"compressed_bytes":i.compress_size,"crc32":f"{i.CRC:08x}"} for i in infos];save()
            selected=collections.defaultdict(list)
            for i in infos:
                k=classify(i.filename)
                if k:selected[k].append(i)
            R["metric_candidates"]={k:[i.filename for i in v] for k,v in selected.items()}
            keys=("H90","gap","FHD","catalog_VOM","catalog_FHD")
            need(all(len(selected[k])==1 for k in keys),"ambiguous or missing published metric/catalog members")
            roster={k:selected[k][0] for k in keys}
            need(sum(i.file_size for i in roster.values())<=8*1024*M,"expanded member cap")
            need(sum(i.compress_size for i in roster.values())<=1024*M,"compressed member cap")
            paths={k:tmp/(k+(".gpkg" if k.startswith("catalog") else ".tif")) for k in keys}
            R["members"]={}
            for k in keys:
                R["members"][k]=extract(z,roster[k],paths[k]);save()
        R["catalog_schema"]={}
        for k in ("catalog_VOM","catalog_FHD"):
            p=paths[k];layers=pyogrio.list_layers(p)
            R["catalog_schema"][k]=[]
            for nm,typ in layers:
                info=pyogrio.read_info(p,layer=nm)
                R["catalog_schema"][k].append({"layer":nm,"geometry_type":typ,"features":info["features"],"fields":info["fields"].tolist(),"dtypes":info["dtypes"].tolist(),"crs":info["crs"]})
            # Only official survey catalog, no bat location or joint rows.
            (O/(k+".gpkg")).write_bytes(p.read_bytes())
        summarize(paths,u)
        R["status"]="COMPLETE_STRUCTURAL_SUPPORT_ONLY"
def limitations():
    q,e=request(LIMIT_URL,"NCEA_limitations")
    with q:
        need(q.status_code==200,"limitations HTTP "+str(q.status_code))
        b=read_body(q,e,16*M)
        need(b[:5]==b"%PDF-","limitations not PDF")
        (O/"NCEA_limitations.pdf").write_bytes(b)
    R["status"]="LIMITATIONS_BYTES_READY_REQUIRES_REVIEW"
if __name__=="__main__":
    try:
        if len(sys.argv)>1 and sys.argv[1]=="limitations":limitations()
        else:main()
    except Exception as e:R.update(status="STOP_SOURCE_OR_QC",error_type=type(e).__name__,reason=str(e)[:250])
    finally:save()
