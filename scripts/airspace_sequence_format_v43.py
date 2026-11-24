"""V43 structural sequence diagnostic; no new physical or ecological admission."""
import csv,io,json,math,re
from collections import Counter,defaultdict
from airspace_temporal_geometry_v42 import get,rows,fmt,time_parse,stats,sha
from roost_fd_source_audit_v2 import OUT

def road():
    h,rr=rows(get("omalley_csv"),",");assert len(rr)==23554
    assert {"Site","Date","Survey","BatID","TrackID","Frame","Time"}<=set(h)
    contexts=defaultdict(set);local_tracks=defaultdict(set)
    a=defaultdict(list);b=defaultdict(list)
    for r in rr:
        s=tuple(r[k] for k in ("Site","Date","Survey"))
        k=s+(r["BatID"],)
        contexts[r["BatID"]].add(s)
        local_tracks[k].add(r["TrackID"])
        f=float(r["Frame"]);assert math.isfinite(f) and f.is_integer()
        a[k].append((int(f),r["Time"],tuple(r[x] for x in h)))
        b[k+(r["TrackID"],)].append((int(f),r["Time"],tuple(r[x] for x in h)))
    def summarize(g):
        dup=0;keys=0;identical=0;different=0;same_time=0;noninc=0;back=0;gaps=0;runs=[]
        for k,rs in g.items():
            fs=[x[0] for x in rs]
            noninc+=sum(v<=u for u,v in zip(fs,fs[1:]))
            back+=sum(v<u for u,v in zip(fs,fs[1:]))
            d=defaultdict(list)
            for f,t,r in rs:d[f].append((t,r))
            for v in d.values():
                if len(v)<=1:continue
                keys+=1;dup+=len(v)-1
                n=len(set(x[1] for x in v));identical+=len(v)-n;different+=n-1
                same_time+=int(len(set(x[0] for x in v))==1)
            # Unique sorted frames describe support, not chronology or an admitted path.
            fs=sorted(d);n=0
            for i,f in enumerate(fs):
                if i and f!=fs[i-1]+1:runs.append(n);n=0;gaps+=1
                n+=1
            if n:runs.append(n)
        return {"candidate_groups":len(g),"duplicate_frame_keys":keys,"duplicate_extra_rows":dup,
          "identical_extra_rows":identical,"different_extra_rows":different,"duplicate_keys_same_time_label":same_time,
          "nonincreasing_adjacent_frames":noninc,"backward_adjacent_frames":back,
          "sorted_unique_frame_gap_count":gaps,"sorted_unique_run_lengths":stats(runs)}
    return {"rows":len(rr),"BatID_cross_site_date_survey":sum(len(x)>1 for x in contexts.values()),
       "context_BatID_multiple_TrackID":sum(len(x)>1 for x in local_tracks.values()),
       "TrackID_count_per_context_BatID":stats([len(x) for x in local_tracks.values()]),
       "V42_key":summarize(a),"full_candidate_key":summarize(b),
       "physical_availability_admitted":False,"new_kinematic_gate_admitted":False}
def r_audit():
    txt=get("omalley_R").decode("utf-8-sig",errors="replace")
    result=[]
    for i,l in enumerate(txt.splitlines(),1):
        l=l.split("#",1)[0]
        if not re.search(r"\b(?:BatID|TrackID|Frame|Frames)\b",l):continue
        ops=re.findall(r"\b(?:group_by|arrange|order|filter|subset|distinct|unique|diff|lag|lead|summarise|summarize|split|aggregate)\b",l)
        ids=re.findall(r"\b(?:Site|Date|Survey|BatID|TrackID|Frame|Frames|Time|Time_s)\b",l)
        if ops:result.append({"line":i,"operations":sorted(set(ops)),"identifiers":sorted(set(ids))})
    return {"lines":len(txt.splitlines()),"whitelisted_provenance":result[:100]}
def mask(s):
    # Never return source digits, words or unapproved delimiters.
    s=str(s or "").strip()[:100]
    return "".join("D" if c.isdigit() else ("L" if c.isalpha() else c if c in ":., -_+" else "?" ) for c in s)
def parse(s):
    s=str(s or "").strip()
    f=fmt(s)
    if f.startswith(("clock","datetime")):
        return f,time_parse(s)
    patterns=[("clock_minutes",r"(\d{1,2}):(\d{2})"),
      ("clock_hms_letters",r"(\d{1,2})[hH](\d{2})[mM](\d{2}(?:[.,]\d+)?)[sS]?"),
      ("clock_hms_dash",r"(\d{1,2})-(\d{2})-(\d{2}(?:[.,]\d+)?)")]
    for label,p in patterns:
        m=re.fullmatch(p,s)
        if not m:continue
        vals=m.groups();hh=int(vals[0]);mm=int(vals[1]);ss=float(vals[2].replace(",",".")) if len(vals)==3 else 0.
        if not(0<=hh<24 and 0<=mm<60 and 0<=ss<60):return "invalid_clock",None
        return label+("_fractional" if len(vals)==3 and re.search(r"[.,]",vals[2]) else ""),hh*3600+mm*60+ss
    if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}[:_-]\d+",s):return "four_field_clock_unknown_last_unit",None
    if f=="numeric":return "numeric_unknown_unit",None
    return "unknown",None
def solar():
    h,rr=rows(get("barre_csv"),";");assert len(rr)==15346
    g=defaultdict(list);arm=defaultdict(set);patterns=Counter();types=Counter()
    for r in rr:
        k=tuple(r[v] for v in ("id_site","date","Trajectory_identifier"))
        s=r["time"];t,v=parse(s);g[k].append((s,t,v));patterns[mask(s)]+=1;types[t]+=1
        a=str(r["typeSite"]).strip().casefold()
        label=a if a in ("control","solar","solar farm","solar farms","solarpark","solar park","pv","photovoltaic","treatment") else "unrecognized_"+sha(a.encode())[:10]
        arm[label].add(r["id_site"])
    nstr=[];nparsed=[];dup=0;unparsed=0;noninc=0;back=0;parsed_groups=0
    for a in g.values():
        nstr.append(len(set(x[0] for x in a)))
        v=[x[2] for x in a if x[2] is not None];unparsed+=len(a)-len(v)
        if len(v)!=len(a):continue
        # Only complete tracks with a single unambiguous format.
        if len(set(x[1] for x in a))!=1:continue
        parsed_groups+=1;nparsed.append(len(set(v)));dup+=len(v)-len(set(v))
        noninc+=sum(y<=x for x,y in zip(v,v[1:]));back+=sum(y<x for x,y in zip(v,v[1:]))
    return {"rows":len(rr),"tracks":len(g),"masked_time_patterns":dict(patterns.most_common(20)),
       "recognized_format_counts":dict(types),"exact_string_distinct_times_per_track":stats(nstr),
       "exact_string_duplicate_rows":len(rr)-sum(nstr),"tracks_one_exact_string_time":sum(x==1 for x in nstr),
       "unparsed_rows":unparsed,"complete_single_format_parsed_tracks":parsed_groups,
       "parsed_distinct_times_per_complete_track":stats(nparsed),"parsed_duplicate_rows_complete_tracks":dup if parsed_groups else None,
       "parsed_nonincrease_complete_tracks":noninc if parsed_groups else None,"parsed_backward_complete_tracks":back if parsed_groups else None,
       "site_counts_by_arm":{k:len(v) for k,v in arm.items()},"physical_availability_admitted":False}
def main():
    assert parse("12h34m56,25s")[0]=="clock_hms_letters_fractional"
    assert parse("12:34:56:25")[1] is None
    assert parse("12:34")[1]==45240
    assert mask("12:34:56:25")=="DD:DD:DD:DD"
    o={"status":"structural_diagnostic_only","ecological_outcomes_analyzed":False,"synthetic_checks":"pass","sources":{}}
    dest=OUT/"audit_v43_sequence_format.json"
    for k,f in [("road",road),("road_R",r_audit),("solar",solar)]:
        try:o["sources"][k]=f()
        except Exception as e:o["sources"][k]={"status":"blocked","error_type":type(e).__name__}
        dest.write_text(json.dumps(o,indent=2,allow_nan=False))
    print(dest.read_text())
    return 0 if all(v.get("status")!="blocked" for v in o["sources"].values()) else 2
if __name__=="__main__":raise SystemExit(main())
