"""Physical scale audit only; 2026-11-26.
Use same 399 QC-passed raw LSA measurements and equal-reference aggregation.
Half span is a numerical probe, not a clearance requirement or flight model.
A Euclidean center-distance transform at voxel pitch h has attainable distances
h*sqrt(i^2+j^2+k^2); radii below h have the exact same mask as radius zero.
No point-cloud/biological outcome selection, no change to frozen topology runs.
"""
import hashlib,json,math,pathlib
import numpy as np,pandas as pd
O=pathlib.Path("wing_span_scale");O.mkdir(exist_ok=True)
N="scientificName.iucn"
PINS={"lineage":("wing/source_row_lineage.csv","681e6f1b92f163cfa789632b6136b3892468a800076f2c171e76fcbdc533f5ca"),"traits":("wing/primary_LSA_physical.csv","99a19c169e18a0bafa4a518b7f844b56d2fe846cac13d5c035f4eae562a74c7b"),"domain":("domain/frozen_trait_domain.csv","6d9ba6bbada4e103606f09f15f25fab9cde13e26c2a15d6e3366fa48808f9f06")}
R={"stage":"measured wing-span versus voxel lattice numerical resolution","status":"START","inputs":PINS,"new_fit":False,"limits":["Half span is an illustrative physical length, not an isotropic required clearance radius. Wing motion, body width, turning geometry, behavior and detection remain unknown.","Point returns do not establish occupied solid volume or absence of obstacles. Even sufficiently fine numerical resolution is not evidence of true flight passability.","Quantization audit is about voxel-center masks only; source point density, registration and vertical uncertainties may impose stricter resolution limits.","Reference medians are compiled measurements, not independent individuals; no imputation or guessed synonyms."]}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save():
    s=json.dumps(R,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist() if isinstance(v,np.ndarray) else None)
    (O/"report.json").write_text(s+"\n");print("WING_SPAN_SCALE_REPORT="+s,flush=True)
def truth(v):
    t=v.astype(str).str.lower();assert t.isin(["true","false"]).all()
    return t.eq("true")
def quant(v):
    return dict(zip(["min","q05","q25","median","q75","q95","max"],np.quantile(v,[0,.05,.25,.5,.75,.95,1]).tolist()))
def main():
    for p,h in PINS.values():assert sha(p)==h,p
    q=pd.read_csv(PINS["lineage"][0],dtype={"refID":str},keep_default_na=False)
    assert len(q)==404 and q.areaDefinition.eq("LSA").all()
    q=q[~truth(q.aspectRatio_conflict)&~truth(q.wingLoading_Nm2_conflict)].copy();assert len(q)==399
    V=["wingSpan_cm","mass_g","wingArea_cm2","AR","WL_N_m2"]
    q[V]=q[V].apply(pd.to_numeric,errors="raise")
    assert np.isfinite(q[V]).all().all() and q[V].gt(0).all().all()
    q["span_m"]=q.wingSpan_cm/100
    row_span=np.sqrt(q.AR*9.81*(q.mass_g/1000)/q.WL_N_m2)
    assert np.allclose(row_span,q.span_m,rtol=1e-10)
    ref=q.groupby([N,"refID"]).span_m.median()
    d=ref.groupby(level=0).median().rename("span_m").to_frame()
    d["span_min_reference_m"]=ref.groupby(level=0).min()
    d["span_max_reference_m"]=ref.groupby(level=0).max()
    d["reference_count"]=ref.groupby(level=0).size()
    d["half_span_m"]=d.span_m/2
    t=pd.read_csv(PINS["traits"][0]).set_index(N);assert len(d)==len(t)==280 and set(d.index)==set(t.index)
    t=t.loc[d.index];assert (d.reference_count==t.reference_count).all()
    d["span_reconstructed_from_separate_medians_m"]=np.sqrt(t.AR*9.81*t.mass_g_physical/1000/t.WL_N_m2)
    ratio=d.span_reconstructed_from_separate_medians_m/d.span_m
    R["separate_medians_reconstruction_ratio"]=quant(ratio)
    R["same_row_identity_max_abs_error_m"]=float(np.max(abs(row_span-q.span_m)))
    dom=pd.read_csv(PINS["domain"][0]).set_index(N);assert set(dom.index)==set(d.index)
    e=dom[truth(dom.training_species)].index.tolist()
    f=["Eptesicus fuscus","Lasiurus borealis","Lasiurus cinereus","Myotis lucifugus","Nycticeius humeralis","Perimyotis subflavus"]
    assert len(e)==14 and set(f)<=set(d.index)
    def audit(names):
        v=d.loc[names];radius=v.half_span_m.to_numpy()
        out={"species":len(v),"span_m":quant(v.span_m),"half_span_m":quant(radius),"voxel_pitch_diagnostics":{}}
        for h in [2.,1.,.5,.25,.1]:
            # Count distinct attainable squared lattice distances that are <=r.
            # Finite patches can have fewer realized shells, never more.
            limit=int(math.ceil(float(radius.max()/h)))
            seq=np.arange(limit+1,dtype=int)**2
            shells=np.unique((seq[:,None,None]+seq[None,:,None]+seq[None,None,:]).ravel())
            k=np.searchsorted(shells,(radius/h)**2,side="right")-1
            out["voxel_pitch_diagnostics"][str(h)]={"half_span_below_one_voxel":int((radius<h).sum()),"full_span_below_one_voxel":int((v.span_m<h).sum()),"distinct_center_distance_cutoffs":int(len(set(k))),"largest_cutoff_group":int(pd.Series(k).value_counts().max()),"median_span_in_voxels":float(np.median(v.span_m/h))}
        return out
    R["global_280"]=audit(d.index);R["europe_14"]=audit(e);R["FWS_6_external"]=audit(f)
    R["FWS_spans"]=json.loads(d.loc[f,["span_m","half_span_m","reference_count"]].reset_index().to_json(orient="records"))
    p=O/"physical_wing_span.csv";d.reset_index().to_csv(p,index=False);R["output_sha256"]=sha(p)
    R["status"]="COMPLETE_SCALE_AUDIT_NO_PASSABILITY_CLAIM";save()
if __name__=="__main__":
    try:main()
    except Exception as e:R.update(status="INCOMPLETE",error_type=type(e).__name__,error=str(e)[:180]);save();raise
