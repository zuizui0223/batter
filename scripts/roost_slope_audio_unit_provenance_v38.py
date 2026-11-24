"""V38: separate relative IPI correspondence from published-scale physical unit QA.
No ecological response model, raw observations, locations, or identifiers exported.
"""
import json,re,tempfile,zipfile
from collections import Counter
from importlib.metadata import version
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_slope_prior_audio_gate_v37 import (
    TARGET,SCALE,group_audio,inspect_species,valid_clips,prior_coverage,
    fetch,FILES,gps_source,source_audit,identity,read,sha,SOURCE_SHAS)

def source_provenance(b):
    r=[]
    with zipfile.ZipFile(__import__("io").BytesIO(b)) as z:
        for i in z.infolist():
            if i.is_dir() or not i.filename.lower().endswith(".m"):continue
            raw=z.read(i);h=sha(raw)
            if h not in SOURCE_SHAS:continue
            hits=[]
            for n,line in enumerate(raw.decode("utf-8-sig",errors="replace").splitlines(),1):
                s=line.split("%",1)[0]
                if not re.search(r"\bipi\b|timeInFile",s,re.I):continue
                events=[]
                # Only source timing literals with an explicit IPI context.
                m=re.search(r"\b(?:audioAll|audio|data)\.ipi\s*(?:>|>=|<|<=)\s*([0-9]+(?:\.[0-9]+)?)\b",s,re.I)
                if m:events.append({"type":"ipi_comparison_literal","value":float(m.group(1))})
                if re.search(r"\bipi\b[^;\n]{0,50}\*\s*1000\b|1000\s*\*\s*[^;\n]{0,50}\bipi\b",s,re.I):events.append({"type":"ipi_times_1000"})
                if re.search(r"\bipi\b[^;\n]{0,50}/\s*1000\b",s,re.I):events.append({"type":"ipi_div_1000"})
                if re.search(r"\b(?:histogram|histcounts|hist)\s*\(",s,re.I) and re.search(r"\bipi\b",s,re.I):events.append({"type":"ipi_histogram_call"})
                if events:hits.append({"line":n,"events":events})
            r.append({"sha256":h,"timing_evidence":hits})
    return r

def relative_candidates(clips):
    dt=[];pv=[];nv=[]
    for _,_,_,d,p,n in clips:
        dt.extend(d);pv.extend(p);nv.extend(n)
    dt=np.asarray(dt,float)
    result=[]
    for ratio in (.001,1.,1000.):
        for align,p in [("previous",pv),("next",nv)]:
            p=np.asarray(p,float)
            ok=np.isfinite(dt)&(dt>0)&np.isfinite(p)&(p>0)
            d=dt[ok];q=p[ok]*ratio
            e=np.abs(d-q)/np.maximum(d,q)
            n=int(len(e));n1=int((e<=.01).sum());n01=int((e<=.001).sum())
            result.append({"ipi_to_time_raw_scale":ratio,"ipi_alignment":align,
              "comparisons":n,"agreement_relative_1pct":n1/n if n else None,
              "agreement_relative_point1pct":n01/n if n else None,
              "passes":bool(n>=100 and n1/n>=.95)})
    return result

def absolute_unit(x):
    vals=x.ipi.to_numpy(float)
    vals=vals[np.isfinite(vals)&(vals>0)]
    results=[]
    for unit,scale in SCALE.items():
        q=vals*scale;n=len(q);nmid=int(((q>=.05)&(q<=.35)).sum())
        results.append({"unit":unit,"positive_finite":n,"within_published_scale_fraction":nmid/n if n else None,
          "passes":bool(n and nmid/n>=.5)})
    return vals,results

def evaluate(s,x,clips,meta,tracks,m):
    rel=relative_candidates(clips)
    a=x.loc[x.key.map(lambda k:k[0]==s)]
    vals,absolute=absolute_unit(a)
    rr=[v for v in rel if v["passes"]];aa=[v for v in absolute if v["passes"]]
    r={"relative_alignment_candidates":rel,"absolute_IPI_unit_candidates":absolute,
        "relative_passing_count":len(rr),"absolute_passing_count":len(aa)}
    if len(rr)!=1 or len(aa)!=1:
        r["status"]="blocked_unit_or_alignment";return r
    ipu=aa[0]["unit"];ratio=rr[0]["ipi_to_time_raw_scale"]
    tu=[u for u,scale in SCALE.items() if np.isclose(SCALE[ipu]/scale,ratio,rtol=0,atol=1e-12)]
    if len(tu)!=1:r["status"]="blocked_inconsistent_units";return r
    candidate={"time_unit":tu[0],"ipi_unit":ipu,"ipi_alignment":rr[0]["ipi_alignment"]}
    r["admitted_timing_candidate"]=candidate
    r["median_IPI_s_unit_QA_only"]=float(np.median(vals*SCALE[ipu]))
    if s not in TARGET:r["status"]="unit_QA_only_not_target";return r
    t,c=valid_clips(clips,candidate,meta,s)
    r["validated_clip_counts"]=c
    r["prior_audio_coverage"]=prior_coverage(s,tracks,m,t)
    r["status"]="conditional_coverage_only"
    return r

def test():
    d=np.array([.1,.2,.3]*100);p=d*1.005;n=np.ones(len(d))*.01
    c=[(None,0,np.array([]),d,n,p)]
    r=relative_candidates(c)
    passed=[(v["ipi_to_time_raw_scale"],v["ipi_alignment"]) for v in r if v["passes"]]
    assert passed==[(1.,"next")]
    c2=[(None,0,np.array([]),d*.001,n*.001,p*.001)]
    rr=relative_candidates(c2)
    assert [v["passes"] for v in rr]==[v["passes"] for v in r]
    _,u=absolute_unit(pd.DataFrame({"ipi":d}))
    assert [v["unit"] for v in u if v["passes"]]==["s"]
    _,u=absolute_unit(pd.DataFrame({"ipi":d*1000}))
    assert [v["unit"] for v in u if v["passes"]]==["ms"]

def main():
    r={"status":"timing_QA_only","numeric_ecological_outcomes_analyzed":False,"species":{},
        "versions":{k:version(k) for k in ("mat-io","numpy","pandas","scipy","h5py")},
        "claim_boundary":"Published timing scale and relative correspondence only. Conditional clock convention and unchanged guarded prior-clip coverage. No ecology model."}
    dest=OUT/"audit_v38_unit_provenance.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save();test();r["synthetic_tests"]="pass";save()
    try:
        b=fetch(FILES["data_zip"]);meta,_=source_audit(b);m,tracks=gps_source()
        assert set(m)==set(meta)
        r["static_source_timing_evidence"]=source_provenance(b)
        with tempfile.TemporaryDirectory() as td:
            a=read(fetch(FILES["audio_mat"]),td,"audio.mat")["audioAll"]
        assert isinstance(a,pd.DataFrame) and a.shape==(74782,29)
        keys,ids=identity(a,m);assert ids["match_counts"]["exact_pair"]==68443
        x=group_audio(a,keys)
        for s in sorted(TARGET):
            p,clips,_=inspect_species(x,s)
            r["species"][s]=evaluate(s,x,clips,meta,tracks,m);save()
        r["exact_identity_match_reproduced"]=True
    except Exception as e:
        r["status"]="blocked";r["error_type"]=type(e).__name__
    save();print(dest.read_text())
    return 0 if r["status"]=="timing_QA_only" else 2
if __name__=="__main__":raise SystemExit(main())
