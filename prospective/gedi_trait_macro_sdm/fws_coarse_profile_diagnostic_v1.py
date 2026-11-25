"""Independent FWS roadside recorded-label diagnostic; NOT 1-km SDM or altitude use.
Frozen FWS_COARSE_PROFILE_DIAGNOSTIC_CONTRACT_V1.md.
All source points/route IDs stay on the runner. Only aggregate report exported.
"""
import collections,hashlib,itertools,json,math,pathlib
import numpy as np,pandas as pd,requests,rasterio
from pyproj import Transformer
from rasterio.windows import Window,from_bounds,transform
from scipy.special import expit
from scipy.optimize import minimize
import fws_mobile_acoustic_relation_audit_v1 as audit
import fws_mobile_acoustic_source_gate_v1 as src
OUT=pathlib.Path("fws_coarse_profile");OUT.mkdir(exist_ok=True)
GRAIN=6000;AREA=GRAIN**2;K=["cell_x","cell_y"];B=["bx","by"]
P=Transformer.from_crs(4326,6933,always_xy=True);I=Transformer.from_crs(6933,4326,always_xy=True)
R={"stage":"independent 6-km FWS roadside recorded-label diagnostic","status":"START","source_sha256":audit.PIN,"grain_km":6,"original_SDM_admitted":False,"limits":["Source MABM usable GPS time difference <=5 seconds, not verified absolute metre accuracy. Six-km aggregation reduces sensitivity to detector coordinate error but does not calibrate it.","BCID automated acoustic labels, not actual occupancy, abundance, or flight altitude; unknown uptime/QA semantics.","LC100 classified forest area, not WorldCover or directly measured forest leaf cover.","Source-specific known-label prediction, not transport of trained European coefficients. No causal effect.","Native point locations, route and event IDs, per-cell detections not exported. Stored Access count and enumerated CSV differ by two."]}
def save():
    (OUT/"report.json").write_text(json.dumps(R,indent=2,allow_nan=False))
    print("FWS_COARSE_REPORT="+json.dumps(R,allow_nan=False),flush=True)
def sha(p,alg="sha256"):
    with p.open("rb") as f:return hashlib.file_digest(f,alg).hexdigest()
def source_rows():
    src.acquire();assert src.R["source_sha256"]==audit.PIN
    e=audit.read("tbl_Events",["Event_ID","Location_ID","Date Start"])
    c=audit.read("tbl_BatCallID_Classification",["Event_ID","LAT","LONG","Date Start","FILENAME","A_SP","A_pulse","gps_diff"])
    t=audit.read("tlu_Species_BatCallID",["A_SP","Genus","Species"])
    assert (len(e),len(c),len(t))==(1277,57473,18)
    for d in [e,c]:d["Event_ID"]=audit.text(d,"Event_ID")
    assert e.Event_ID.ne("").all() and not e.Event_ID.duplicated().any()
    e["event_date"]=audit.dates(e["Date Start"]);c["call_date"]=audit.dates(c["Date Start"])
    t["code"]=audit.text(t,"A_SP").str.upper();t["name"]=audit.text(t,"Genus")+" "+audit.text(t,"Species")
    valid=t.name.str.fullmatch(r"[A-Z][a-z]+ [a-z][a-z]+")&~audit.text(t,"Species").str.lower().isin(["sp","spp","unknown","none","unidentified"])
    tm=t[t.code.ne("")&~t.code.duplicated(False)&valid].set_index("code").name.to_dict();assert len(tm)==16
    c["species"]=audit.text(c,"A_SP").str.upper().map(tm)
    c["filename"]=audit.text(c,"FILENAME")
    c["lat"]=audit.num(c.LAT);c["lon"]=audit.num(c.LONG)
    c["gps_seconds"]=audit.num(c.gps_diff);c["pulses"]=audit.num(c.A_pulse)
    c["unique_event_file"]=c.Event_ID.ne("")&c.filename.ne("")&~c.duplicated(["Event_ID","filename"],False)
    z=c.merge(e[["Event_ID","Location_ID","event_date"]],on="Event_ID",how="left",validate="many_to_one",indicator=True)
    assert len(z)==len(c)
    tests=[("joined",z._merge.eq("both")),("same_date",z.event_date.notna()&z.event_date.eq(z.call_date)),("period",z.event_date.between("2019-04-17","2023-03-16")),("unique_event_file",z.unique_event_file),("source_binomial",z.species.notna()),("finite_regional_coords",np.isfinite(z.lat)&np.isfinite(z.lon)&z.lat.between(15,51.6)&z.lon.between(-130,-60)),("documented_gps_time_match_5s",np.isfinite(z.gps_seconds)&z.gps_seconds.abs().le(5)),("numeric_pulses_ge5",np.isfinite(z.pulses)&z.pulses.ge(5)),("route_id_present",audit.text(z,"Location_ID").ne(""))]
    keep=pd.Series(True,index=z.index);flow=[]
    for name,check in tests:
        keep&=check.fillna(False);flow.append({"step":name,"rows":int(keep.sum())})
        if name=="finite_regional_coords":assert keep.sum()==10069
    d=z[keep].copy()
    R["source_attrition"]=flow;R["source_reconciliation"]=audit.R["source_row_reconciliation"];save()
    if d.empty:return pd.DataFrame(columns=["species","Event_ID","Location_ID",*K,*B])
    x,y=P.transform(d.lon.to_numpy(),d.lat.to_numpy())
    assert np.isfinite(x).all() and np.isfinite(y).all()
    cx=np.floor(x/GRAIN).astype(int);cy=np.floor(y/GRAIN).astype(int)
    bx=np.floor(cx*GRAIN/200000).astype(int);by=np.floor(cy*GRAIN/200000).astype(int)
    block_ok=(bx==np.floor(((cx+1)*GRAIN-1e-6)/200000))&(by==np.floor(((cy+1)*GRAIN-1e-6)/200000))
    _,hi=I.transform(cx*GRAIN,(cy+1)*GRAIN)
    d["cell_x"]=cx;d["cell_y"]=cy;d["bx"]=bx;d["by"]=by
    d=d[block_ok&(hi<=51.6)][["species","Event_ID","Location_ID",*K,*B]].copy()
    R["source_georeferenced_domain_records"]=len(d)
    R["source_georeferenced_domain_routes"]=int(d.Location_ID.nunique());R["source_georeferenced_domain_species"]=int(d.species.nunique())
    R["source_georeferenced_domain_cells"]=len(d[K].drop_duplicates())
    src.P.unlink(missing_ok=True)
    return d
def labels_and_pairs(d):
    rows=d.drop_duplicates(["species","Event_ID",*K]).copy()
    tax=[]
    for name,v in rows.groupby("species",sort=True):
        nc=len(v[K].drop_duplicates());nr=v.Location_ID.nunique()
        tax.append({"species":name,"cells":nc,"routes":int(nr),"eligible":bool(nc>=10 and nr>=3)})
    taxa=sorted(x["species"] for x in tax if x["eligible"])
    rows=rows[rows.species.isin(taxa)].copy()
    ct=rows[K].drop_duplicates().sort_values(K).reset_index(drop=True);ct["ci"]=np.arange(len(ct))
    rows=rows.merge(ct,on=K,validate="many_to_one")
    ix={s:i for i,s in enumerate(taxa)};rng=np.random.default_rng(20261126)
    ps=[];gb=[];gr=[]
    for key,v in rows.groupby(["Event_ID","Location_ID",*B],sort=True):
        by={s:np.sort(w.ci.unique()) for s,w in v.groupby("species",sort=True)}
        for s,t in itertools.combinations(sorted(by),2):
            ca=np.repeat(by[s],len(by[t]));cb=np.tile(by[t],len(by[s]));ok=ca!=cb;ca,cb=ca[ok],cb[ok]
            if len(ca)==0:continue
            if len(ca)>128:
                pick=np.sort(rng.choice(len(ca),128,replace=False));ca,cb=ca[pick],cb[pick]
            g=len(gb);gb.append((int(key[2]),int(key[3])));gr.append(str(key[1]))
            ps.extend((ix[s],ix[t],int(x),int(y),g) for x,y in zip(ca,cb))
    z=np.asarray(ps,dtype=int).reshape(-1,5)
    support={"taxon_support":tax,"eligible_taxa":len(taxa),"comparison_taxa":int(len(np.unique(z[:,:2]))),"comparison_routes":len(set(gr)),"comparison_blocks":len(set(gb)),"comparisons":len(z),"comparison_cells":int(len(np.unique(z[:,2:4]))),"groups":len(gb)}
    return ct,z,gb,gr,taxa,support
def passes(s):
    return s["eligible_taxa"]>=6 and s["comparison_taxa"]>=6 and s["comparison_routes"]>=10 and s["comparison_blocks"]>=8 and s["comparisons"]>=300 and s["comparison_cells"]>=30
def weights(s,xe,ye,cx,cy):
    x0,x1=cx*GRAIN,(cx+1)*GRAIN;y0,y1=cy*GRAIN,(cy+1)*GRAIN
    j0=max(0,int(np.searchsorted(xe,x0,side="right")-1));j1=min(s[1],int(np.searchsorted(xe,x1,side="left")))
    i0=max(0,int(np.searchsorted(-ye,-y1,side="right")-1));i1=min(s[0],int(np.searchsorted(-ye,-y0,side="left")))
    wx=np.maximum(0,np.minimum(x1,xe[j0+1:j1+1])-np.maximum(x0,xe[j0:j1]))
    wy=np.maximum(0,np.minimum(y1,ye[i0:i1])-np.maximum(y0,ye[i0+1:i1+1]))
    return (slice(i0,i1),slice(j0,j1)),wy[:,None]*wx[None,:]
LEVELS=[10,25,50,75,90,98];CLIM=["bio1","bio4","bio5","bio6","bio12","bio15"]
def stack_to_cells(u,spec,group):
    # Bound the remote window by actual candidate cell extent. No full global read.
    x0=int(u.cell_x.min())*GRAIN;x1=(int(u.cell_x.max())+1)*GRAIN
    y0=int(u.cell_y.min())*GRAIN;y1=(int(u.cell_y.max())+1)*GRAIN
    l,b=I.transform(x0,y0);r,t=I.transform(x1,y1)
    arrays=[];ref=None
    for label,url,scale,offset,nodata,declared in spec:
        with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",GDAL_HTTP_TIMEOUT="75",GDAL_HTTP_MAX_RETRY="2",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif"):
            with rasterio.open(url) as s:
                assert s.crs.to_epsg()==4326 and s.count==1 and s.transform.b==s.transform.d==0
                assert s.transform.a>0 and s.transform.e<0
                if nodata is not None:assert s.nodata==nodata
                if declared:
                    assert math.isclose(s.scales[0],scale,abs_tol=1e-8) and math.isclose(s.offsets[0],offset,abs_tol=1e-6)
                else:assert math.isclose(s.transform.a,.01,abs_tol=1e-7)
                w=from_bounds(l,b,r,t,transform=s.transform)
                c0=max(0,math.floor(w.col_off)-1);c1=min(s.width,math.ceil(w.col_off+w.width)+1)
                r0=max(0,math.floor(w.row_off)-1);r1=min(s.height,math.ceil(w.row_off+w.height)+1)
                win=Window(c0,r0,c1-c0,r1-r0);tr=transform(win,s.transform);g=(tr,int(win.height),int(win.width))
                assert g[1]*g[2]<=14_000_000,("source window budget",group,g[1:])
                if ref is None:ref=g
                else:assert g==ref,label
                raw=s.read(1,window=win,masked=True);ok=~np.ma.getmaskarray(raw)&np.isfinite(raw.data)
                v=np.where(ok,raw.data.astype(np.float32)*scale+offset,np.nan).astype(np.float32)
                arrays.append(v)
                R.setdefault("raster_source_windows",{})[label]={"url":url,"shape":list(g[1:]),"transform":list(tr),"scale":scale,"offset":offset,"value_sha256":hashlib.sha256(raw.data.tobytes()).hexdigest(),"mask_sha256":hashlib.sha256(ok.tobytes()).hexdigest()}
                print("FWS_WINDOW_READY",label,g[1:],flush=True)
    a=np.stack(arrays);del arrays
    tr,h,w=ref;xs=tr.c+np.arange(w+1)*tr.a;ys=tr.f+np.arange(h+1)*tr.e
    xe,_=P.transform(xs,np.zeros_like(xs));_,ye=P.transform(np.zeros_like(ys),ys)
    assert np.all(np.diff(xe)>0) and np.all(np.diff(ye)<0)
    valid=np.isfinite(a).all(0)
    if group=="profile":
        bad=valid&np.any(np.diff(a,axis=0)<0,axis=0)
        R["native_profile_order_errors"]=int(bad.sum());valid&=~bad
    ans=np.full((len(u),len(spec)),np.nan);fraction=np.zeros(len(u))
    for i,(cx,cy) in enumerate(u[K].itertuples(index=False,name=None)):
        sl,A=weights((h,w),xe,ye,cx,cy);mask=valid[sl]&(A>0)
        q=A[mask];fraction[i]=q.sum()/AREA
        if .95<=fraction[i]<=1.000001:ans[i]=np.sum(a[:,sl[0],sl[1]][:,mask].astype(float)*q[None,:],axis=1)/q.sum()
    save();return ans,fraction
LC_NAME="PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.tif"
LC_MD5="6898fbe3fb46a1110cd65e3a81ed7624"
LC_SHA="b2203d6dd8b6918e27cd1413e7dfec4a9e4ce03dbf50f209d7f04c550c23cf53"
GROUPS={"broadleaf":[112,114,122,124],"needleleaf":[111,113,121,123],"mixed":[115,125],"other_forest":[116,126],"shrub":[20],"herb":[30],"crop":[40],"built":[50],"bare":[60],"water":[80,200],"wetland":[90]}
LC_COLS=["LC_"+k for k in GROUPS]
def landcover(u):
    p=pathlib.Path(LC_NAME)
    if not(p.exists() and p.stat().st_size==1713345228 and sha(p,"md5")==LC_MD5 and sha(p)==LC_SHA):
        p.unlink(missing_ok=True)
        x=requests.get("https://zenodo.org/api/records/3939050",timeout=(20,60));x.raise_for_status();doc=x.json();assert doc["doi"]=="10.5281/zenodo.3939050"
        f=[v for v in doc["files"] if v["key"]==LC_NAME];assert len(f)==1 and f[0]["checksum"]=="md5:"+LC_MD5 and f[0]["size"]==1713345228
        url="https://zenodo.org/records/3939050/files/"+LC_NAME+"?download=1"
        tmp=p.with_suffix(".part");n=0
        with requests.get(url,stream=True,timeout=(20,120),headers={"Accept-Encoding":"identity"}) as resp:
            resp.raise_for_status();assert resp.status_code==200
            with tmp.open("wb") as w:
                for v in resp.iter_content(4*1024*1024):
                    n+=len(v);assert n<=1713345228;w.write(v)
        assert n==1713345228 and sha(tmp,"md5")==LC_MD5 and sha(tmp)==LC_SHA
        tmp.replace(p)
    R["LC100"]={"doi":"10.5281/zenodo.3939050","bytes":p.stat().st_size,"md5":LC_MD5,"sha256":LC_SHA,"groups":GROUPS};save()
    known=[70,100,*[v for x in GROUPS.values() for v in x]]
    ans=np.full((len(u),len(GROUPS)),np.nan);fraction=np.zeros(len(u));observed=collections.Counter()
    with rasterio.open(p) as s:
        assert s.count==1 and s.crs.to_epsg()==4326 and s.transform.b==s.transform.d==0
        assert .0008<=s.transform.a<=.0012 and .0008<=-s.transform.e<=.0012
        assert s.scales[0]==1 and s.offsets[0]==0
        for i,(cx,cy) in enumerate(u[K].itertuples(index=False,name=None)):
            l,b=I.transform(cx*GRAIN,cy*GRAIN);r,t=I.transform((cx+1)*GRAIN,(cy+1)*GRAIN)
            w=from_bounds(l,b,r,t,s.transform)
            c0=max(0,math.floor(w.col_off));c1=min(s.width,math.ceil(w.col_off+w.width));r0=max(0,math.floor(w.row_off));r1=min(s.height,math.ceil(w.row_off+w.height))
            if c1<=c0 or r1<=r0:continue
            z=s.read(1,window=Window(c0,r0,c1-c0,r1-r0),masked=True)
            xs=s.transform.c+np.arange(c0,c1+1)*s.transform.a;ys=s.transform.f+np.arange(r0,r1+1)*s.transform.e
            xe,_=P.transform(xs,np.zeros_like(xs));_,ye=P.transform(np.zeros_like(ys),ys)
            _,A=weights(z.shape,xe,ye,cx,cy)
            assert A.shape==z.shape and abs(A.sum()-AREA)<.1
            v=z.data;ok=~np.ma.getmaskarray(z)&np.isfinite(v)&(A>0)
            codes,counts=np.unique(v[ok],return_counts=True);observed.update({str(int(k)):int(n) for k,n in zip(codes,counts)})
            assert np.isin(codes,known+[0,255]).all()
            good=ok&np.isin(v,known);den=A[good].sum();fraction[i]=den/AREA
            if .95<=fraction[i]<=1.000001:ans[i]=[A[good&np.isin(v,g)].sum()/den for g in GROUPS.values()]
    R["LC100"]["observed_class_counts"]=dict(observed);save()
    return ans,fraction
def environment(d):
    u=d[K].drop_duplicates().sort_values(K).reset_index(drop=True)
    R["candidate_environment_cells"]=len(u);save()
    gv=[(f"RH{v}",f"https://data.source.coop/geoai-ucph/gvsm/mosaics/2020/RH{v}_Q1.tif",.1,0,32767,False) for v in LEVELS]
    cl=[(k,f"https://os.zhdk.cloud.switch.ch/chelsav2/GLOBAL/climatologies/1981-2010/bio/CHELSA_{k}_1981-2010_V.2.1.tif",.1,-273.15 if k in {"bio1","bio5","bio6"} else 0,None,True) for k in CLIM]
    g,ga=stack_to_cells(u,gv,"profile");c,ca=stack_to_cells(u,cl,"climate");lc,la=landcover(u)
    good=np.isfinite(g).all(1)&np.isfinite(c).all(1)&np.isfinite(lc).all(1)
    forest=good&(lc[:,:4].sum(1)>=.30)&(g[:,-1]>5)
    R["environment_support"]={"joint_profile_cells":int(np.isfinite(g).all(1).sum()),"joint_climate_cells":int(np.isfinite(c).all(1).sum()),"landcover_cells":int(np.isfinite(lc).all(1).sum()),"common_cells":int(good.sum()),"forest_cells":int(forest.sum())}
    for j,k in enumerate(CLIM):u[k]=c[:,j]
    for j,k in enumerate(LC_COLS):u[k]=lc[:,j]
    u["RH98"]=g[:,-1];u["R50"]=np.divide(g[:,2],g[:,-1],out=np.full(len(u),np.nan),where=g[:,-1]>5)
    u=u[forest].copy()
    assert np.isfinite(u[CLIM+LC_COLS+["RH98","R50"]]).all().all()
    save()
    return d.merge(u,on=K,validate="many_to_one"),u
def fit(ct,z,gb,gr,taxa,u):
    sa,sb,ca,cb,gi=z.T
    blocks=sorted(set(gb),key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest())
    bm={b:i for i,b in enumerate(blocks)};gbi=np.array([bm[b] for b in gb]);block=gbi[gi]
    routes=np.array(gr);proute=routes[gi];fold=block%5
    A=np.eye(len(taxa))[sa]-np.eye(len(taxa))[sb]
    raw=ct.merge(u,on=K,validate="one_to_one").sort_values("ci")[CLIM+LC_COLS+["RH98","R50"]].to_numpy(float)
    assert np.isfinite(raw).all();assert len(z)<=200000,("pair memory budget",len(z))
    def wgt(m):
        ng=np.bincount(gi[m],minlength=len(gb));bg=np.bincount(gbi[ng>0],minlength=len(blocks))
        w=1/(ng[gi[m]]*bg[block[m]]*len(np.unique(block[m])))
        assert np.isclose(w.sum(),1);return w
    def obj(p,X,w):
        h=X@p
        return float(w@np.logaddexp(0,-h)+.1*(p@p)),X.T@(-w*expit(-h))+.2*p
    scores=np.full((len(z),2),np.nan);folds=[];skips={}
    for k in range(5):
        te=(fold==k);tr=(fold!=k)&~np.isin(proute,np.unique(proute[te]))
        taxa_train=np.unique(np.r_[sa[tr],sb[tr]])
        te=te&np.isin(sa,taxa_train)&np.isin(sb,taxa_train)
        if tr.sum()<300 or len(taxa_train)<6 or len(np.unique(block[tr]))<6 or len(np.unique(proute[tr]))<8 or te.sum()<10 or len(np.unique(block[te]))<1:
            skips[str(k+1)]={"train_pairs":int(tr.sum()),"train_taxa":len(taxa_train),"train_blocks":len(np.unique(block[tr])),"train_routes":len(np.unique(proute[tr])),"test_pairs":int(te.sum())};continue
        assert not set(proute[tr])&set(proute[te]) and not set(block[tr])&set(block[te])
        use=np.unique(np.r_[ca[tr],cb[tr]]);sd=raw[use].std(0);zero=sd<=1e-12;sd[zero]=1
        D=(raw[ca]-raw[cb])/sd;D[:,zero]=0
        base=(A[:,:,None]*D[:,:-1][:,None,:]).reshape(len(z),-1);profile=np.column_stack([base,A*D[:,-1,None]])
        out=[]
        for X in (base,profile):
            Xtr=np.ascontiguousarray(X[tr]);w=wgt(tr)
            f=minimize(obj,np.zeros(X.shape[1]),args=(Xtr,w),method="L-BFGS-B",jac=True,options={"maxiter":400,"ftol":1e-12,"gtol":1e-7})
            assert f.success or np.max(np.abs(f.jac))<1e-6
            out.append(-np.logaddexp(0,-X[te]@f.x))
        scores[te]=np.stack(out,axis=1)
        folds.append({"fold":k+1,"train_pairs":int(tr.sum()),"test_pairs":int(te.sum()),"train_routes":len(np.unique(proute[tr])),"test_routes":len(np.unique(proute[te])),"test_blocks":len(np.unique(block[te])),"scores":dict(zip(["B","R"],map(float,wgt(te)@scores[te])))})
    ok=np.isfinite(scores).all(1);scored_blocks=len(np.unique(block[ok]))
    R["evaluation_support"]={"scored_comparisons":int(ok.sum()),"fraction":float(ok.mean()),"scored_blocks":scored_blocks,"scored_taxa":len(np.unique(np.r_[sa[ok],sb[ok]])),"scored_routes":len(np.unique(proute[ok])),"completed_folds":len(folds),"folds":folds,"skips":skips}
    if len(folds)<3 or scored_blocks<8:R["status"]="STOP_INSUFFICIENT_DISJOINT_SCORED_SUPPORT";save();return
    w=wgt(ok);mean=w@scores[ok];delta=scores[ok,1]-scores[ok,0]
    den=np.bincount(block[ok],weights=w,minlength=len(blocks));live=den>0
    bg=np.bincount(block[ok],weights=w*delta,minlength=len(blocks))[live]/den[live]
    boot=np.random.default_rng(20261126).choice(bg,size=(2000,len(bg)),replace=True).mean(1)
    R["result"]={"neutral":-math.log(2),"baseline":float(mean[0]),"profile":float(mean[1]),"profile_gain":float(mean[1]-mean[0]),"profile_minus_neutral":float(mean[1]+math.log(2)),"positive_blocks":int((bg>0).sum()),"conditional_block_bootstrap_95":np.quantile(boot,[.025,.975]).tolist(),"block_quantiles":np.quantile(bg,[.05,.5,.95]).tolist()}
    R["status"]="COMPLETE_DESCRIPTIVE_INDEPENDENT_ROADSIDE_DIAGNOSTIC";save()
def main():
    d=source_rows()
    ct,z,gb,gr,taxa,s=labels_and_pairs(d);R["pre_environment_comparison_support"]=s;save()
    if not passes(s):R["status"]="STOP_INSUFFICIENT_PRE_ENVIRONMENT_SUPPORT";save();return
    d,u=environment(d)
    ct,z,gb,gr,taxa,s=labels_and_pairs(d);R["forest_comparison_support"]=s;save()
    if not passes(s):R["status"]="STOP_INSUFFICIENT_FOREST_COMPARISON_SUPPORT";save();return
    fit(ct,z,gb,gr,taxa,u)
if __name__=="__main__":
    try:main()
    except Exception as e:
        R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:250]);save();raise
    finally:src.P.unlink(missing_ok=True)
