"""V54B timestamp ambiguity audit; not a reconstruction of the published cohort."""
import csv,io,json,math,re
from datetime import date
from bisect import bisect_left,bisect_right
from collections import Counter,defaultdict
import numpy as np
from airspace_visual_cohort_v53 import fetch,docs,HEADER,norm,missing
from roost_fd_source_audit_v2 import OUT

def day(s):
    s=str(s).strip()
    m=re.fullmatch(r"(2014)-(\d{2})-(\d{2})",s)
    if m:y,mo,d=map(int,m.groups());fmt="ISO"
    else:
        m=re.fullmatch(r"(\d{1,2})/(\d{1,2})/(2014|14)",s)
        if not m:raise ValueError("unsupported_date")
        mo,d,y=map(int,m.groups());y=2014;fmt="US_slash"
    return date(y,mo,d).isoformat(),fmt
def clock(s):
    s=str(s).strip()
    m=re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})(\.\d+)?(?:\s*([AaPp][Mm]))?",s)
    if not m:raise ValueError("unsupported_time")
    h,mi,se=map(int,m.groups()[:3]);frac=m.group(4);am=m.group(5)
    if am:
        if not 1<=h<=12:raise ValueError("invalid_12h")
        h=h%12+12*int(am.lower()=="pm")
    if not(0<=h<24 and 0<=mi<60 and 0<=se<60):raise ValueError("invalid_clock")
    return h*3600+mi*60+se+(float(frac) if frac else 0),("12h" if am else "24h")+("_fractional" if frac else "_whole_seconds")
def mask(s):
    return "".join("D" if c.isdigit() else "L" if c.isalpha() else c if c in ":./- +" else "?" for c in str(s).strip()[:60])
def site(s):
    a=float(s)
    if not math.isfinite(a) or not a.is_integer() or not 1<=a<=10:raise ValueError("site_domain")
    return int(a)
def candidate(a,t):
    lo=bisect_left(a,t-30);hi=bisect_right(a,t+30)
    p=bisect_left(a,t)
    closest=min([abs(a[i]-t) for i in (p-1,p) if 0<=i<len(a)],default=None)
    return hi-lo,closest
def quant(a):
    if not a:return {}
    return {k:float(v) for k,v in zip(("min","q25","median","q75","q90","q95","max"),np.quantile(a,[0,.25,.5,.75,.9,.95,1]))}
def test():
    assert day("9/8/14")[0]==day("2014-09-08")[0]
    assert clock("12:00:01 AM")[0]==1 and clock("12:00:01 PM")[0]==43201
    assert candidate([0.,30.,30.,60.,61.],30.)==(4,0.)
    assert candidate([],30.)==(0,None)
    assert candidate([1.],86399.)[0]==0 and candidate([86401.],86399.)[0]==1
    for bad in ("24:00:00","01:02","01:60:00"):
        try:clock(bad)
        except ValueError:continue
        raise AssertionError("clock accepted invalid")
def main():
    o={"status":"timing_diagnostic_only","original_published_cohort_reconciled":False,"ecological_model_fitted":False,
       "claim_boundary":"All documented release events; candidate time coincidences within same recorded site/date only, not identified acoustic emissions, causal matching or full observation effort."}
    dest=OUT/"audit_v54b_temporal_correspondence.json"
    def save():dest.write_text(json.dumps(o,indent=2,allow_nan=False))
    def stop(reason):
        o["status"]=reason;save();print(dest.read_text());return 0
    save()
    try:
        test();o["synthetic_checks"]="pass"
        b,xml=fetch();o["source_hashes_verified"]=True
        ds=docs(xml)
        ed={norm(k):norm(v) for k,v in ds["Match_video_acoustic"]["enumerated"].items()}
        assert "no match" in ed["0"] and "positive match" in ed["1"]
        for field,expected in (("Confidence",{"h":"high confidence","m":"medium confidence","l":"low confidence"}),
                               ("Proximity",{"n":"near-range","m":"mid-range","f":"far-range"}),
                               ("Flight",{"s":"straight flight","c":"curved flight","e":"erratic flight"})):
            e={norm(k):norm(v) for k,v in ds[field]["enumerated"].items()}
            assert all(v in e[k] for k,v in expected.items())
        o["dictionary_codes_verified"]=True
        o["time_video_dictionary_inconsistency"]=("acoustic sampling" in norm(ds["Time_video"]["definition"]))
        r=csv.reader(io.StringIO(b.decode("utf-8-sig"),newline=""));h=next(r)
        rows=[z for z in r if any(not missing(x) for x in z)]
        assert h==HEADER and len(rows)==2744 and all(len(z)==13 for z in rows)
        ac=[];vi=[];patterns={k:Counter() for k in ("acoustic_date","acoustic_time","video_date","video_time")}
        fmt={k:Counter() for k in patterns};errors=Counter()
        counts=Counter()
        for z in rows:
            for mode,inds in (("acoustic",range(0,4)),("video",range(4,12))):
                nn=sum(not missing(z[i]) for i in inds)
                counts[(mode,nn)]+=1
                if nn==0:continue
                if nn!=len(inds):raise ValueError("partial_block")
                i=0 if mode=="acoustic" else 4
                for kind,off,parser in (("date",1,day),("time",2,clock)):
                    k=mode+"_"+kind;value=z[i+off];patterns[k][mask(value)]+=1
                    try:
                        v,f=parser(value);fmt[k][f]+=1
                    except (ValueError,OverflowError):errors[k]+=1
                if errors:continue
                key=(site(z[i]),day(z[i+1])[0]);t=clock(z[i+2])[0]
                y=norm(z[i+3])
                if y not in ("0","1"):raise ValueError("unknown_match_flag")
                if mode=="acoustic":ac.append((key,t,int(y)))
                else:
                    if norm(z[8]) not in ("h","m","l") or norm(z[9]) not in ("n","m","f") or norm(z[10]) not in ("s","c","e"):raise ValueError("unknown_video_category")
                    vi.append((key,t,int(y)))
        o["source_blocks"]={m:{str(k):v for (x,k),v in counts.items() if x==m} for m in ("acoustic","video")}
        o["masked_timestamp_patterns"]={k:dict(c.most_common(15)) for k,c in patterns.items()}
        o["timestamp_formats"]={k:dict(v) for k,v in fmt.items()}
        o["timestamp_parse_errors"]=dict(errors)
        save()
        if errors:return stop("STOP_UNSUPPORTED_TIMESTAMP_FORMAT")
        assert len(ac)==2535 and len(vi)==949 and sum(x[2] for x in vi)==387
        groups=defaultdict(list)
        for k,t,y in ac:groups[k].append(t)
        for a in groups.values():a.sort()
        table={str(y):Counter() for y in (0,1)}
        nearest={str(y):[] for y in (0,1)};cand=[]
        unique={str(y):[] for y in (0,1)}
        no_acoustic_group=0;midnight=0;wrap_add=0;wrap_new=0
        for k,t,y in vi:
            a=groups.get(k,[]);n,nd=candidate(a,t)
            cand.append(n)
            table[str(y)]["zero" if n==0 else "one" if n==1 else "multiple"]+=1
            if not a:no_acoustic_group+=1
            if nd is not None:nearest[str(y)].append(nd)
            if n==1:unique[str(y)].append(nd)
            if t<30 or t>86400-30:
                midnight+=1
                # Explicit alternative circular-clock diagnostic, not a link correction.
                w=(bisect_right(a,t+30-86400) if t>86400-30 else len(a)-bisect_left(a,t-30+86400))
                if w>0:
                    wrap_add+=1
                    if n==0:wrap_new+=1
        def dup(x):
            c=Counter((k,t) for k,t,y in x);return sum(n-1 for n in c.values())
        o["results"]={"visual_records":len(vi),"acoustic_records":len(ac),
          "visual_groups":len({k for k,t,y in vi}),"acoustic_groups":len(groups),
          "duplicate_visual_keys_extra_rows":dup(vi),"duplicate_acoustic_keys_extra_rows":dup(ac),
          "reported_video_match_count":387,"candidate_count_by_reported_match_flag":{k:{j:int(c[j]) for j in ("zero","one","multiple")} for k,c in table.items()},
          "candidate_exists_count":sum(n>0 for n in cand),"multiple_candidate_count":sum(n>1 for n in cand),
          "reported_positive_without_candidate":table["1"]["zero"],
          "reported_negative_with_candidate":table["0"]["one"]+table["0"]["multiple"],
          "video_records_without_acoustic_site_date_group":no_acoustic_group,
          "candidate_count_distribution":quant(cand),"nearest_candidate_time_s_by_reported_flag":{k:quant(v) for k,v in nearest.items()},
          "unique_candidate_time_s_by_reported_flag":{k:quant(v) for k,v in unique.items()},
          "midnight_wrap_diagnostic":{"video_records_within_30s_of_midnight":midnight,"would_gain_candidate_on_circular_clock":wrap_add,"would_change_zero_to_nonzero":wrap_new}}
        o["status"]="TIMING_DIAGNOSTIC_COMPLETE"
    except Exception as e:
        import traceback
        o["status"]="blocked";o["error_type"]=type(e).__name__;o["failure_functions"]=[x.name for x in traceback.extract_tb(e.__traceback__)[-5:]]
    save();print(dest.read_text())
    return 2 if o["status"]=="blocked" else 0
if __name__=="__main__":raise SystemExit(main())
