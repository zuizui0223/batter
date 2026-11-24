"""V37 timing and prior-audio coverage QA; no ecological response analysis."""
import io,json,re,tempfile,zipfile
from collections import Counter,defaultdict
from pathlib import PurePosixPath
from bisect import bisect_left,bisect_right
from importlib.metadata import version
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_slope_acoustic_sync_v36 import (
    read,fetch,FILES,gps_source,source_audit,identity,origins,valid_date,quant,sha,KNOWN)
from roost_slope_native_nmea_v33 import decode,anchors_and_windows,dist
from roost_slope_acoustic_gps_schema_v32 import SOURCE_SHAS

TARGET={"myotis myotis":(8,67880,1486),"rhinopoma microphyllum":(6,7975,758)}
SCALE={"s":1.0,"ms":0.001}
MAXCLIP={"myotis myotis":.5,"rhinopoma microphyllum":5.}

def source_units(b):
    out=[]
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        for i in z.infolist():
            if i.is_dir() or not i.filename.lower().endswith(".m"):continue
            raw=z.read(i);h=sha(raw)
            if h not in SOURCE_SHAS:continue
            lines=raw.decode("utf-8-sig",errors="replace").splitlines()
            events=[]
            for j,l in enumerate(lines,1):
                a=l.split("%",1)[0]
                if not re.search(r"\bipi\b|timeInFile|(?:xlabel|ylabel)\(",a,re.I):continue
                e=[]
                # Return only explicit unit conversion and label tokens, not arbitrary code.
                if re.search(r"\bipi\b[^;\n]{0,50}\*\s*1000\b|1000\s*\*\s*[^;\n]{0,50}\bipi\b",a,re.I):e.append("ipi_times_1000")
                if re.search(r"\bipi\b[^;\n]{0,50}/\s*1000\b",a,re.I):e.append("ipi_div_1000")
                if re.search(r"(?:xlabel|ylabel)\([^;\n]*\bIPI\b[^;\n]*(?:\bms\b|millisecond)",a,re.I):e.append("ipi_axis_ms")
                if re.search(r"(?:xlabel|ylabel)\([^;\n]*\bIPI\b[^;\n]*(?:\bseconds?\b|\(s\)|\[s\])",a,re.I):e.append("ipi_axis_seconds")
                if re.search(r"timeInFile[^;\n]{0,50}\*\s*1000\b",a,re.I):e.append("timeInFile_times_1000")
                if re.search(r"timeInFile[^;\n]{0,50}/\s*1000\b",a,re.I):e.append("timeInFile_div_1000")
                if e:events.append({"line":j,"tokens":e})
            out.append({"sha256":h,"unit_tokens":events})
    return out

def number_col(a,c):
    return pd.to_numeric(a[c],errors="coerce").to_numpy(dtype=float)

def group_audio(a,keys):
    x=pd.DataFrame({"key":keys,"start":number_col(a,"fileStartTime"),
       "call":number_col(a,"callNum"),"time":number_col(a,"timeInFile"),"ipi":number_col(a,"ipi")})
    x=x.loc[x.key.notna()&np.isfinite(x.start)].copy()
    return x

def pairs_for_clip(g):
    # Unique integer call indices only; don't connect across missing or duplicate indices.
    c=g.call.to_numpy(float)
    valid=np.isfinite(c)&(c==np.floor(c))
    h=g.loc[valid].copy()
    h=h.loc[~h.call.duplicated(keep=False)].sort_values("call",kind="stable")
    a=h.call.to_numpy(float);t=h.time.to_numpy(float);p=h.ipi.to_numpy(float)
    if len(a)<2:return (np.array([]),)*4
    dt=np.diff(t)
    ok=(np.diff(a)==1)&np.isfinite(dt)&(dt>0)
    return dt[ok],p[:-1][ok],p[1:][ok],np.diff(t)[ok]

def inspect_species(x,s):
    x=x.loc[x.key.map(lambda k:k[0]==s)].copy()
    # retain file metadata and interval-QA pairs internally
    clips=[];dt_all=[];prev_all=[];next_all=[];gaps=[]
    for k,g in x.groupby("key",sort=True):
        starts=np.array(sorted(g.start.unique()))
        gaps.extend((np.diff(starts)*86400).tolist())
        for st,h in g.groupby("start",sort=True):
            ts=h.time.to_numpy(float);finite=ts[np.isfinite(ts)]
            dt,prev,nxt,_=pairs_for_clip(h)
            dt_all.extend(dt);prev_all.extend(prev);next_all.extend(nxt)
            clips.append((k,float(st),finite,dt,prev,nxt))
    dt=np.asarray(dt_all,float);ips={"previous":np.asarray(prev_all,float),"next":np.asarray(next_all,float)}
    report={"exact_rows":len(x),"identities":int(x.key.nunique()),"clips":len(clips),
        "observed_file_start_gap_s":quant(gaps),"positive_adjacent_call_time_pairs":len(dt),
        "clip_duration_checks":{},"unit_alignment_candidates":[]}
    gp=np.asarray(gaps,float);gp=gp[np.isfinite(gp)&(gp>0)]
    for step in (5,30):
        near=np.abs(gp/step-np.round(gp/step))*step<=.1
        report["gap_near_multiple_"+str(step)+"s"]=int((near&(np.round(gp/step)>=1)).sum())
    for tu,tsc in SCALE.items():
        maxclip=MAXCLIP.get(s,5.)
        supported=sum(int(bool(len(t)) and np.min(t)>=0 and np.max(t)*tsc<=maxclip+.01) for _,_,t,*_ in clips)
        report["clip_duration_checks"][tu]={"clips_with_finite_time":sum(bool(len(t)) for _,_,t,*_ in clips),"compatible_clips":supported,"nominal_max_s":maxclip}
        for pu,psc in SCALE.items():
            for align,pp in ips.items():
                ok=np.isfinite(pp)&(pp>0)&np.isfinite(dt)&(dt>0)
                d=dt[ok]*tsc;p=pp[ok]*psc
                agreement=np.abs(d-p)<=np.maximum(.001,.01*d)
                n=int(len(d));agree=int(agreement.sum())
                report["unit_alignment_candidates"].append({"time_unit":tu,"ipi_unit":pu,"ipi_alignment":align,
                  "comparisons":n,"agree":agree,"agreement_fraction":float(agree/n) if n else None,
                  "passes":bool(n>=100 and agree/n>=.95)})
    candidates=[r for r in report["unit_alignment_candidates"] if r["passes"]]
    # No arbitrary tie break: equality of differently scaled times may be ambiguous.
    report["passing_candidates"]=len(candidates)
    report["unit_status"]="unique_candidate" if len(candidates)==1 else "ambiguous_or_failed"
    return report,clips,candidates

def windows(chains):
    # Replay V33's 60s anchor and speed gates exactly; yield only timing and chain span.
    for chain in chains:
        times=[r[0] for r in chain];n=len(chain);i=0
        while i<n:
            ids=[i];current=i
            while True:
                target=times[current]+60_000_000
                a=bisect_left(times,target-5_000_000,current+1)
                b=bisect_right(times,target+5_000_000,a)
                if a==b:break
                current=min(range(a,b),key=lambda k:(abs(times[k]-target),times[k]))
                ids.append(current)
            i=current+1
            for j in range(0,len(ids)-2,2):
                r0,r1,r2=[chain[k] for k in ids[j:j+3]]
                dt1=(r1[0]-r0[0])/1e6;dt2=(r2[0]-r1[0])/1e6
                assert 55<=dt1<=65 and 55<=dt2<=65
                if 2<=dist(r0[1],r0[2],r1[1],r1[2])/dt1<=50 and 2<=dist(r1[1],r1[2],r2[1],r2[2])/dt2<=50:
                    yield (r0[0]/1e6,r1[0]/1e6,r2[0]/1e6)

def valid_clips(clips,candidate,meta,s):
    ts=SCALE[candidate["time_unit"]];ps=SCALE[candidate["ipi_unit"]]
    times=defaultdict(list);c=Counter()
    for k,st,t,dt,p,n in clips:
        c["files"]+=1
        if not len(t) or np.min(t)<0 or np.max(t)*ts>MAXCLIP[s]+.01:
            c["invalid_clip_span"]+=1;continue
        pp=p if candidate["ipi_alignment"]=="previous" else n
        d=dt*ts;ipi=pp*ps
        ok=np.isfinite(ipi)&(ipi>0)&(d>0)&(np.abs(d-ipi)<=np.maximum(.001,.01*d))
        if not np.any(ok):c["no_valid_IPI_pair"]+=1;continue
        off=meta.get(k)
        if off is None or abs(off)>14:c["missing_timezone"]+=1;continue
        utc=(st-719529.)*86400-off*3600
        if not bool(valid_date(np.asarray([utc]))[0]):c["invalid_date"]+=1;continue
        times[k].append(float(utc));c["validated_clips"]+=1
    return {k:np.unique(v) for k,v in times.items()},dict(c)

def prior_coverage(s,tracks,m,clip_times):
    en,ef,ew=TARGET[s];n=0;fixes=0;raw_windows=0
    totals=Counter();one=[];two=[]
    for k,v in m.items():
        if k[0]!=s or v["gps"]!="1":continue
        assert len(tracks.get(k,[]))==1
        chains,c,*_=decode(tracks[k][0]);n+=1;fixes+=c["unique_timestamp_valid_rows"]
        ww=list(windows(chains));assert len(ww)==anchors_and_windows(chains)["horizontal_eligible_windows"]
        raw_windows+=len(ww)
        t=clip_times.get(k,np.array([]))
        # The prior interval lies in the same accepted chain; conservative guard avoids both edges.
        count=np.asarray([np.searchsorted(t,b-20,side="right")-np.searchsorted(t,a+15,side="left") for a,b,_ in ww])
        n1=int((count>=1).sum());n2=int((count>=2).sum());one.append(n1);two.append(n2)
        totals["windows_ge1_clip"]+=n1;totals["windows_ge2_clips"]+=n2
    assert (n,fixes,raw_windows)==(en,ef,ew)
    return {"source_replay":True,"raw_windows":raw_windows,"animals":n,"counts":dict(totals),
      "per_animal_windows_ge1_clip":quant(one),"per_animal_windows_ge2_clips":quant(two),
      "animals_ge50_windows_ge1_clip":sum(v>=50 for v in one),
      "animals_ge50_windows_ge2_clips":sum(v>=50 for v in two),
      "primary_coverage_gate":bool(sum(v>=50 for v in one)>=6)}

def main():
    r={"status":"prior_audio_QA_only","numeric_acoustic_ecological_outcomes_analyzed":False,
       "claim_boundary":"IPI values used only for timing unit QA; no flight height outcomes opened. Local UTC convention remains conditional.","species":{},
       "versions":{k:version(k) for k in ("mat-io","numpy","pandas","scipy","h5py")}}
    dest=OUT/"audit_v37_prior_audio.json"
    def save():dest.write_text(json.dumps(r,indent=2,allow_nan=False))
    save()
    try:
        b=fetch(FILES["data_zip"]);meta,code=source_audit(b)
        m,tracks=gps_source();assert set(m)==set(meta)
        r["source_unit_tokens"]=source_units(b)
        with tempfile.TemporaryDirectory() as td:
            a=read(fetch(FILES["audio_mat"]),td,"audio.mat")["audioAll"]
        assert isinstance(a,pd.DataFrame) and a.shape==(74782,29)
        keys,ids=identity(a,m);assert ids["match_counts"]["exact_pair"]==68443
        r["exact_identity_match_reproduced"]=True
        x=group_audio(a,keys)
        for s in sorted(KNOWN):
            p,clips,cs=inspect_species(x,s)
            if s in TARGET:
                if len(cs)!=1:p["prior_audio_gate"]="blocked_unit_alignment_ambiguity"
                else:
                    t,c=valid_clips(clips,cs[0],meta,s);p["validated_clip_counts"]=c
                    p["prior_audio_coverage"]=prior_coverage(s,tracks,m,t)
                    p["prior_audio_gate"]="conditional_coverage_only"
            r["species"][s]=p;save()
    except Exception as e:
        r["status"]="blocked";r["error_type"]=type(e).__name__;save()
    print(dest.read_text())
    return 0 if r["status"]=="prior_audio_QA_only" else 2
if __name__=="__main__":raise SystemExit(main())
