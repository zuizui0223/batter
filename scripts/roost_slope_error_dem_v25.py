"""V25: measurement-error compatibility and matched alternative DSM sensitivity.
No raw coordinates, tag identifiers, tile names or individual records emitted.
"""
import hashlib, json, math
import numpy as np
import pandas as pd
import requests
from rasterio.io import MemoryFile
from pyproj import CRS
from roost_fd_source_audit_v2 import OUT
from roost_slope_device_matched_scale_v24 import BASE, interval, decompose, association, load, tadarida, anchors, compare
from roost_slope_matched_panels_v21 import summary

EXPECTED={"tadarida":(1308,7),"phyllostomus_2016":(752,8),"phyllostomus_2023":(1315,11)}
K=np.array([[2.,-1.],[-1.,2.]])
def reconstruct(d):
    a,info=anchors(d,60,5)
    W=[];S=[];L=[];raw=[]
    for (animal,session),g in a.groupby(["animal","session"],sort=True):
        g=g.sort_values("time").reset_index(drop=True)
        for i in range(0,len(g)-2,2):
            r0,r1,r2=[g.iloc[j].copy() for j in (i,i+1,i+2)]
            s1=interval(r0,r1);s2=interval(r1,r2);l=interval(r0,r2)
            if s1 is None or s2 is None or l is None:continue
            if not(55<=s1["dt"]<=65 and 55<=s2["dt"]<=65 and 110<=l["dt"]<=130):continue
            k=len(W);meta={"animal":str(animal),"session":session,"window":k}
            assert np.isclose(l["dh"],s1["dh"]+s2["dh"],rtol=0,atol=1e-8)
            assert np.isclose(l["dg"],s1["dg"]+s2["dg"],rtol=0,atol=1e-8)
            W.append({**meta,"x1":s1["dg"],"x2":s2["dg"],"y1":s1["dh"],"y2":s2["dh"]})
            S.extend([{**s1,**meta},{**s2,**meta}]);L.append({**l,**meta})
            raw.append((k,meta,[r0,r1,r2]))
    W=pd.DataFrame(W);S=pd.DataFrame(S);L=pd.DataFrame(L)
    n=W.animal.value_counts();keep=set(W.loc[W.animal.isin(n[n>=50].index),"window"])
    return (W[W.window.isin(keep)],S[S.window.isin(keep)],L[L.window.isin(keep)],
            [r for r in raw if r[0] in keep])

def moments(W):
    a=[]
    for _,g in W.groupby("animal"):
        X=g[["x1","x2"]].to_numpy(float);Y=g[["y1","y2"]].to_numpy(float)
        X-=X.mean(axis=0);Y-=Y.mean(axis=0)
        a.append([X.T@X/len(X),Y.T@Y/len(X),X.T@Y/len(X)])
    return np.mean(a,axis=0)
def fit_error(W):
    X,Y,C=moments(W);V=float(np.trace(X));L=float(X.sum());c=float(np.trace(C));D=float(C.sum())
    den=2*L-V
    r={"Sx":X.tolist(),"Sy":Y.tolist(),"Cxy":C.tolist(),
       "raw_beta60":c/V if V>0 else None,"raw_beta120":D/L if L>0 else None,
       "cross_asymmetry_m2":float(C[0,1]-C[1,0])}
    if abs(den)<1e-12:return {**r,"status":"singular"}
    b=(2*D-c)/den
    if abs(b)<1e-12:return {**r,"status":"zero_slope"}
    s=(V-c/b)/4
    T=X-s*K;R=Y-b*b*T;E=C-b*T
    r.update(beta=float(b),endpoint_variance_m2=float(s),endpoint_sd_m=math.sqrt(s) if s>=0 else None,
             min_eigen_latent_terrain=float(np.linalg.eigvalsh(T).min()),
             min_eigen_residual_vertical=float(np.linalg.eigvalsh(R).min()),
             covariance_residual=E.tolist(),
             relative_covariance_residual=float(np.linalg.norm(E)/np.linalg.norm(C)) if np.linalg.norm(C)>0 else None,
             status="aggregate_feasible" if s>=0 and np.linalg.eigvalsh(T).min()>=-1e-8 and np.linalg.eigvalsh(R).min()>=-1e-8 else "aggregate_infeasible")
    return r
def error_audit(W):
    r=fit_error(W);lo=[fit_error(W[W.animal!=a]) for a in sorted(W.animal.unique())]
    r["leave_one_animal_out"]={"folds":len(lo),
        "beta":summary([x["beta"] for x in lo if x.get("beta") is not None]),
        "endpoint_sd_m":summary([x["endpoint_sd_m"] for x in lo if x.get("endpoint_sd_m") is not None]),
        "feasible_folds":sum(x["status"]=="aggregate_feasible" for x in lo),
        "relative_covariance_residual":summary([x["relative_covariance_residual"] for x in lo if x.get("relative_covariance_residual") is not None])}
    return r

class Copernicus:
    def __init__(self):
        self.tiles={};self.receipts=[];self.failures=0
    def tile(self,lat,lon):
        la=int(math.floor(lat));lo=int(math.floor(lon))
        key=(la,lo)
        if key in self.tiles:return self.tiles[key]
        if len(self.tiles)>=20:return None
        ns=("N" if la>=0 else "S")+f"{abs(la):02d}"
        ew=("E" if lo>=0 else "W")+f"{abs(lo):03d}"
        name=f"Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM"
        url=f"https://copernicus-dem-30m.s3.amazonaws.com/{name}/{name}.tif"
        self.tiles[key]=None
        try:
            with requests.get(url,stream=True,timeout=(15,90)) as r:
                r.raise_for_status()
                b=bytearray()
                for part in r.iter_content(1024*1024):
                    b.extend(part)
                    if len(b)>150*1024*1024:raise ValueError("size gate")
                etag=r.headers.get("ETag","").strip('"')
            with MemoryFile(bytes(b)) as mem:
                with mem.open() as ds:
                    crs=CRS.from_user_input(ds.crs)
                    assert crs.to_2d().equals(CRS.from_epsg(4326),ignore_axis_order=True)
                    assert ds.count==1 and abs(ds.transform.b)<1e-12 and abs(ds.transform.d)<1e-12
                    assert ds.transform.a>0 and ds.transform.e<0
                    data=ds.read(1,masked=True).astype(float).filled(np.nan)
                    data[(data<=-32767)|(~np.isfinite(data))]=np.nan
                    item=(data,~ds.transform)
                    self.receipts.append({"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),
                         "etag":etag,"shape":[ds.height,ds.width],"pixel_degrees":[ds.transform.a,ds.transform.e]})
            self.tiles[key]=item
        except Exception:
            self.failures+=1
        return self.tiles[key]
    def value(self,lat,lon):
        item=self.tile(lat,lon)
        if item is None:return None
        data,inv=item;col,row=inv*(lon,lat)
        col-=.5;row-=.5;i=int(math.floor(row));j=int(math.floor(col))
        if i<0 or j<0 or i+1>=data.shape[0] or j+1>=data.shape[1]:return None
        v=data[i:i+2,j:j+2]
        if not np.isfinite(v).all():return None
        u=row-i;t=col-j
        return float((1-u)*((1-t)*v[0,0]+t*v[0,1])+u*((1-t)*v[1,0]+t*v[1,1]))

def alt_compare(W,S,L,raw,dem):
    rows=[];ss=[];ll=[];diff=[]
    for k,meta,g in raw:
        z=[dem.value(float(r.lat),float(r.lon)) for r in g]
        if any(v is None for v in z):continue
        delta=[v-float(r.ground) for v,r in zip(z,g)]
        h=[r.copy() for r in g]
        for r,v in zip(h,z):r["ground"]=v
        s1=interval(h[0],h[1]);s2=interval(h[1],h[2]);l=interval(h[0],h[2])
        if s1 is None or s2 is None or l is None:continue
        rows.append({**meta,"x1":s1["dg"],"x2":s2["dg"],"y1":s1["dh"],"y2":s2["dh"]})
        ss.extend([{**s1,**meta},{**s2,**meta}]);ll.append({**l,**meta})
        diff.append({**meta,"d0":delta[0],"d1":delta[1],"d2":delta[2]})
    r={"candidate_windows":len(W),"complete_DEM_windows":len(rows)}
    if not rows:return {**r,"status":"no_complete_DEM_windows"}
    A=pd.DataFrame(rows);AS=pd.DataFrame(ss);AL=pd.DataFrame(ll);D=pd.DataFrame(diff)
    cnt=A.animal.value_counts();keep=set(A.loc[A.animal.isin(cnt[cnt>=50].index),"window"])
    A=A[A.window.isin(keep)];AS=AS[AS.window.isin(keep)];AL=AL[AL.window.isin(keep)];D=D[D.window.isin(keep)]
    O=W[W.window.isin(keep)];OS=S[S.window.isin(keep)];OL=L[L.window.isin(keep)]
    r.update(retained_windows=len(A),animals=int(A.animal.nunique()))
    if r["animals"]<6:return {**r,"status":"insufficient_animals"}
    assert len(A)==len(O)==len(AL)==len(OL) and len(AS)==len(OS)==2*len(A)
    assert np.array_equal(A.window.to_numpy(),O.window.to_numpy())
    endpoint=D[["d0","d1","d2"]].to_numpy()
    center=D.groupby("animal")[["d0","d1","d2"]].transform("mean").to_numpy()
    d1=AS.dg.to_numpy()-OS.dg.to_numpy();d2=AL.dg.to_numpy()-OL.dg.to_numpy()
    r.update(status="computed",
      endpoint_difference_centered_RMS_m=float(np.sqrt(np.mean((endpoint-center)**2))),
      signed_increment_difference_60_m=summary(d1),signed_increment_difference_120_m=summary(d2),
      original={"60":compare(OS,BASE),"120":compare(OL,BASE),"error_audit":error_audit(O)},
      copernicus={"60":compare(AS,BASE),"120":compare(AL,BASE),"error_audit":error_audit(A)})
    return r

def main():
    report={"status":"bounded_measurement_diagnostic","claim_boundary":"Same prior windows; DEMs are surface models with different vertical datums, not independent ground truth. Constant-slope model assumptions unverified.","panels":{}}
    dest=OUT/"audit_v25_slope.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    save()
    for p,(expected,nanimals) in EXPECTED.items():
        q={}
        try:
            d,_=tadarida() if p=="tadarida" else load(p)
            d["alternate"]=np.nan
            W,S,L,raw=reconstruct(d)
            assert len(W)==expected and W.animal.nunique()==nanimals
            q.update(status="moments_computed",windows=len(W),animals=int(W.animal.nunique()),
                covariance_decomposition=decompose(W),error_model=error_audit(W))
            report["panels"][p]=q;save()
            dem=Copernicus()
            try:q["alternative_DEM"]=alt_compare(W,S,L,raw,dem)
            except Exception as e:q["alternative_DEM"]={"status":"blocked","error_type":type(e).__name__}
            q["DEM_receipts"]={"tiles_attempted":len(dem.tiles),"failures":dem.failures,"verified_objects":dem.receipts}
        except Exception as e:q.update(status="blocked",error_type=type(e).__name__)
        report["panels"][p]=q;save()
    print(dest.read_text())
    return 0 if any(p.get("status")=="moments_computed" for p in report["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
