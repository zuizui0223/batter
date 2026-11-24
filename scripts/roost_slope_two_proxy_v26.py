"""V26: two terrain proxies, shared-error identifiability diagnostic on V25 windows."""
import json
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
SEED=20261124  # identical frozen V5 seed; avoid unrelated wing-source imports
from roost_slope_matched_panels_v21 import summary
from roost_slope_error_dem_v25 import reconstruct,Copernicus,load,tadarida,EXPECTED,K

SHARED={"tadarida":(1306,7),"phyllostomus_2016":(752,8),"phyllostomus_2023":(1315,11)}
HASHES={
 "tadarida":{"bbad4c516282421b4cc5f2e1e243462613897827206fd79b60a1c7b6627125c9",
 "bab932f240c66b54fa5c2c314c3e1f4c222212a06cdf03edae298d5447e6eced",
 "860fb53b25e4ebc2a519458e8e457211e808c7f0f10d80a3b0dc4d4c03e22715"},
 "phyllostomus_2016":{"920b8aac0c1e1dea741424ba9feccf8608abd572673a9162ca3c0f52b22648d4"},
 "phyllostomus_2023":{"920b8aac0c1e1dea741424ba9feccf8608abd572673a9162ca3c0f52b22648d4"}}
# Published V25 raw traces/sums (on shared roster).
TARGET={
 "tadarida":(.19957151883663704,.2660340100623415,.19555747806030332,.26342443251954106),
 "phyllostomus_2016":(.5932216336514483,.7074371585980134,.6176143863064919,.7050259025649617),
 "phyllostomus_2023":(.504075644674179,.850507111744045,.6186172778933534,.8763736593808853)}
def build(panel):
    d,_=tadarida() if panel=="tadarida" else load(panel)
    d["alternate"]=np.nan
    W,S,L,raw=reconstruct(d)
    assert (len(W),W.animal.nunique())==EXPECTED[panel]
    by_window=W.set_index("window")
    dem=Copernicus();rows=[]
    for k,meta,g in raw:
        z=[dem.value(float(r.lat),float(r.lon)) for r in g]
        if any(v is None for v in z):continue
        r=by_window.loc[k]
        old=[float(v.ground) for v in g]
        assert np.allclose([r.x1,r.x2],np.diff(old),rtol=0,atol=1e-8)
        rows.append({"animal":meta["animal"],"a1":r.x1,"a2":r.x2,"b1":z[1]-z[0],"b2":z[2]-z[1],
          "y1":r.y1,"y2":r.y2,"d0":z[0]-old[0],"d1":z[1]-old[1],"d2":z[2]-old[2]})
    assert {r["sha256"] for r in dem.receipts}==HASHES[panel]
    x=pd.DataFrame(rows);n=x.animal.value_counts()
    x=x[x.animal.isin(n[n>=50].index)].copy()
    assert (len(x),x.animal.nunique())==SHARED[panel]
    return x

def moments(d):
    blocks=[]
    for _,g in d.groupby("animal"):
        A=g[["a1","a2"]].to_numpy(float);B=g[["b1","b2"]].to_numpy(float);Y=g[["y1","y2"]].to_numpy(float)
        for x in (A,B,Y):x-=x.mean(axis=0)
        n=len(g)
        blocks.append(np.array([A.T@A,B.T@B,Y.T@Y,A.T@B,A.T@Y,B.T@Y])/n)
    return np.asarray(blocks)

def rel(E,C):
    den=np.linalg.norm(C)
    return float(np.linalg.norm(E)/den) if den>0 else None
def ratio(a,b):
    return float(a/b) if b>0 and np.isfinite(a) and np.isfinite(b) else None
def evaluate(M):
    A,B,Y,AB,AY,BY=M
    S=(AB+AB.T)/2;C=(AY+BY)/2
    c=float(np.trace(C));D=float(C.sum());V=float(np.trace(S));L=float(S.sum())
    b60=ratio(c,V);b120=ratio(D,L)
    r={"original_raw_beta60":ratio(np.trace(AY),np.trace(A)),
       "original_raw_beta120":ratio(AY.sum(),A.sum()),
       "copernicus_raw_beta60":ratio(np.trace(BY),np.trace(B)),
       "copernicus_raw_beta120":ratio(BY.sum(),B.sum()),
       "two_proxy_beta60":b60,"two_proxy_beta120":b120,
       "two_proxy_delta":b120-b60 if b120 is not None and b60 is not None else None,
       "C_AB_asymmetry_relative":rel(AB-AB.T,S),
       "C_AY_minus_C_BY_relative":rel(AY-BY,C)}
    den=2*L-V
    if abs(den)<1e-12:r["status"]="singular";return r
    b=(2*D-c)/den
    if not np.isfinite(b) or b<=0:r["status"]="nonpositive_beta";return r
    s=(V-c/b)/4
    T=S-s*K
    latent_eig=float(np.linalg.eigvalsh(T).min())
    y_eig=float(np.linalg.eigvalsh(Y-b*b*T).min())
    unique_a=float(np.linalg.eigvalsh(A-S).min())
    unique_b=float(np.linalg.eigvalsh(B-S).min())
    r.update(constant_beta=float(b),shared_endpoint_variance_m2=float(s),
        shared_endpoint_sd_m=float(np.sqrt(s)) if s>=0 else None,
        min_eigen_latent_terrain=latent_eig,min_eigen_vertical_residual=y_eig,
        min_eigen_unique_A=unique_a,min_eigen_unique_B=unique_b,
        AY_covariance_residual_relative=rel(AY-b*T,AY),
        BY_covariance_residual_relative=rel(BY-b*T,BY),
        averaged_covariance_residual_relative=rel(C-b*T,C),
        covariance_residual=(C-b*T).tolist(),
        status="necessary_PSD_pass" if min(s,latent_eig,y_eig,unique_a,unique_b)>=-1e-8 else "necessary_PSD_fail")
    return r

def summarize_resampling(rows):
    keys=["two_proxy_beta60","two_proxy_beta120","two_proxy_delta","constant_beta","shared_endpoint_sd_m","averaged_covariance_residual_relative"]
    o={}
    for k in keys:
        a=[r[k] for r in rows if r.get(k) is not None and np.isfinite(r[k])]
        o[k]={"n":len(a),"quantiles_025_50_975":np.quantile(a,[.025,.5,.975]).tolist() if a else [],
              "min_max":[min(a),max(a)] if a else []}
    o["necessary_PSD_pass_count"]=sum(r.get("status")=="necessary_PSD_pass" for r in rows)
    o["draws"]=len(rows)
    return o

def audit(panel,d):
    M=moments(d);point=evaluate(M.mean(axis=0))
    raw=tuple(point[k] for k in ["original_raw_beta60","original_raw_beta120","copernicus_raw_beta60","copernicus_raw_beta120"])
    assert np.allclose(raw,TARGET[panel],rtol=0,atol=1e-8)
    n=len(M);rng=np.random.default_rng(SEED)
    folds=[evaluate(np.delete(M,i,axis=0).mean(axis=0)) for i in range(n)]
    boot=[evaluate(M[rng.integers(0,n,n)].mean(axis=0)) for _ in range(1999)]
    D=d[["d0","d1","d2"]].to_numpy(float)
    center=d.groupby("animal")[["d0","d1","d2"]].transform("mean").to_numpy(float)
    rms=float(np.sqrt(np.mean((D-center)**2)))
    return {"windows":len(d),"animals":n,"source_match":True,
       "covariance_matrices":dict(zip(["S_A","S_B","S_Y","C_AB","C_AY","C_BY"],M.mean(axis=0).tolist())),
       "centered_endpoint_disagreement_RMS_m":rms,"point":point,
       "leave_one_animal_out":summarize_resampling(folds),
       "paired_animal_bootstrap":summarize_resampling(boot),
       "caution":"Independent-proxy ratios are assumption-conditional; shared-error PSD checks are necessary, not sufficient. No common-error upper bound from DEM disagreement."}

def test():
    T=np.array([[9.,2.],[2.,5.]])
    b=.8;s=2.
    S=T+s*K
    A=S+np.eye(2);B=S+2*np.eye(2);Y=b*b*T+3*np.eye(2)
    C=b*T
    r=evaluate(np.array([A,B,Y,S,C,C]))
    assert np.isclose(r["constant_beta"],b) and np.isclose(r["shared_endpoint_variance_m2"],s)
    assert r["status"]=="necessary_PSD_pass"
    assert r["averaged_covariance_residual_relative"]<1e-12

def main():
    r={"status":"two_proxy_measurement_diagnostic","synthetic_test":"pending","panels":{},
       "claim_boundary":"No instrument validity or latent biological slope established; no coordinates, IDs, or individual results."}
    dest=OUT/"audit_v26_slope.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save();test();r["synthetic_test"]="pass";save()
    for p in SHARED:
        try:r["panels"][p]={"status":"computed",**audit(p,build(p))}
        except Exception as e:r["panels"][p]={"status":"blocked","error_type":type(e).__name__}
        save()
    print(dest.read_text())
    return 0 if all(p["status"]=="computed" for p in r["panels"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
