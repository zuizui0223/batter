"""V56: bounded independent Maui nightly effort-aware concordance.
Stop before numeric analysis if source semantics are not uniquely documented.
"""
import csv,io,json,hashlib,math,re
from collections import Counter
from datetime import datetime
from pathlib import PurePosixPath
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import numpy as np
from scipy.stats import rankdata
import requests
from roost_fd_source_audit_v2 import OUT
from airspace_usgs_visual_acoustic_v52 import fsize,check
DOI="10.5066/P937H9LQ"
ID="5eab79dc82cefae35a225636"
HEAD={"User-Agent":"batter-Maui-paired-night-audit-v56/1.0"}
CAP=2_000_000
def sha(b):return hashlib.sha256(b).hexdigest()
def get(u):
    r=requests.get(u,headers=HEAD,timeout=(15,45));r.raise_for_status();return r.json()
def tag(n):return n.tag.rsplit("}",1)[-1].lower()
def norm(x):return re.sub(r"\s+"," ",str(x or "").strip().casefold())
def child(n,k):
    for x in n:
        if tag(x)==k:return " ".join("".join(x.itertext()).split())
    return ""
def safe(x):
    x=" ".join(str(x or "").split())
    if re.search(r"latitude|longitude|coordinates|https?://|@|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",x,re.I):return "[redacted definition "+sha(x.encode())[:12]+"]"
    return x[:450]
def publicname(x):
    x=str(x or "")
    return x if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_(). /%-]{0,100}",x) and not re.search(r"\d{4,}|latitude|longitude",x,re.I) else "field_"+sha(x.encode())[:12]
def dictionary(b):
    root=ET.fromstring(b);out={}
    for n in root.iter():
        if tag(n)!="attr":continue
        k=child(n,"attrlabl")
        if not k:continue
        if k in out:raise ValueError("duplicate_dictionary_field")
        u=[" ".join("".join(x.itertext()).split()) for x in n.iter() if tag(x) in ("attrunit","rdommin","rdommax","udom")]
        e=[(child(x,"edomv"),child(x,"edomvd")) for x in n.iter() if tag(x)=="edom"]
        out[k]={"definition":child(n,"attrdef"),"units_and_domains":u,"enumerated":e}
    return out
def fetch(o):
    j=get("https://api.datacite.org/dois/"+DOI)["data"]["attributes"]
    assert j["doi"].casefold()==DOI.casefold() and "geological survey" in str(j.get("publisher")).casefold()
    assert any("maui island" in norm(t.get("title")) and "bat behavior at wind turbines" in norm(t.get("title")) for t in j["titles"])
    o["release_identity_verified"]=True
    x=get("https://www.sciencebase.gov/catalog/item/"+ID+"?format=json")
    assert x["id"]==ID and "nightly acoustic-visual detections and conditions" in norm(x["title"]) and "maui" in norm(x["title"])
    ff=x.get("files") or []
    files=[f for f in ff if PurePosixPath(str(f.get("name") or "")).suffix.lower() in (".csv",".xml")]
    o["inventory"]=[{"name":publicname(f.get("name")),"size":fsize(f),"extension":PurePosixPath(str(f.get("name") or "")).suffix.lower(),"download_link_advertised":bool(f.get("downloadUri") or f.get("url"))} for f in ff]
    assert len(files)==2 and {PurePosixPath(f["name"]).suffix.lower() for f in files}=={".csv",".xml"}
    result={};o["receipts"]={};o["file_transport_status"]={}
    exact_sizes={".csv":31144,".xml":27066}
    for f in files:
        ext=PurePosixPath(f["name"]).suffix.lower();n=fsize(f);u=f.get("downloadUri") or f.get("url")
        assert n==exact_sizes[ext] and 0<n<=CAP and isinstance(u,str)
        if ext==".csv":assert f["name"]=="Hawaii hoary bat nightly acoustic-visual detections and conditions.csv"
        if ext==".xml":assert "field_"+sha(f["name"].encode())[:12]=="field_aeca0fe098f9"
        p=urlparse(u);assert p.scheme=="https" and (p.hostname or "").endswith((".usgs.gov",".sciencebase.gov"))
        try:
            data=bytearray()
            with requests.get(u,headers=HEAD,stream=True,timeout=(15,65)) as r:
                r.raise_for_status()
                for c in r.iter_content(65536):
                    data.extend(c);assert len(data)<=n
            b=bytes(data);assert len(b)==n
            hashes=check(f,b)
            o["receipts"][ext]={"bytes":len(b),"sha256":sha(b),"publisher_hashes_verified":hashes}
            o["file_transport_status"][ext]={"status":"received"}
            result[ext]=b
        except requests.HTTPError as e:
            o["file_transport_status"][ext]={"status":"blocked","http_status":int(e.response.status_code) if e.response is not None else None}
        except requests.RequestException as e:
            o["file_transport_status"][ext]={"status":"blocked","error_type":type(e).__name__}
    if set(result)!={".csv",".xml"}:raise RuntimeError("exact_source_transport_incomplete")
    return result[".csv"],result[".xml"]
def role_candidates(h,d):
    res={k:[] for k in ("turbine","date","a_count","v_count","a_effort","v_effort")}
    for c in h:
        if c not in d:continue
        defn=norm(d[c]["definition"]);un=norm(" ".join(d[c]["units_and_domains"]))
        name=norm(re.sub(r"[_-]+"," ",c))
        # Match documentary semantics only, not row values or observed associations.
        alltext=name+" "+defn
        if name in ("turbine","turbine id","turbine number","wtg","wtg id") and re.search(r"turbine",defn):res["turbine"].append((c,1.))
        elif re.search(r"(?:turbine|wind turbine).{0,40}(?:identifier|identity|number| id\b)|(?:identifier|identity|number| id\b).{0,40}turbine",defn) and not re.search(r"rotation|rotor|rpm|operation|speed|start|stop",defn):res["turbine"].append((c,1.))
        if name in ("date","night","sample date","sampling date","night date") and re.search(r"date|night",defn):res["date"].append((c,1.))
        elif re.search(r"\bdate\b.{0,40}(?:sample|sampling|monitoring|recording|survey|night)|(?:sample|sampling|monitoring|recording|survey|night).{0,40}\bdate\b",defn) and not re.search(r"time of day|sunrise|sunset",defn):res["date"].append((c,1.))
        modes=[]
        if re.search(r"acoustic|audio|ultrasonic",alltext):modes.append("a")
        if re.search(r"video|visual|thermal",alltext):modes.append("v")
        if len(modes)!=1:continue
        mode=modes[0]
        count=bool(re.search(r"(?:number|count|total|tally).{0,65}(?:bat|detect|event|pass)|(?:detect|event|pass).{0,30}(?:count|number|total)",defn))
        if count and re.search(r"bat|detection|event",defn) and not re.search(r"\b(?:rate|per hour|per minute|binary|presence.absence|file count|sound files|wav files)\b",defn):
            res[mode+"_count"].append((c,1.))
        effort=bool(re.search(r"duration|effort|hours|minutes|length of|total time",defn+" "+un)) and bool(re.search(r"record|sampl|monitor|effort|survey|operat",defn))
        hours=bool(re.search(r"\bhours?\b|\bhrs?\b",defn+" "+un))
        minutes=bool(re.search(r"\bminutes?\b|\bmins?\b",defn+" "+un))
        if effort and hours!=minutes and not re.search(r"per hour|per minute|time of detection|time of day|bat event|duration of bat|flight duration|duration of detection",defn):
            res[mode+"_effort"].append((c,1. if hours else 1/60.))
    return res
def val(s):
    s=norm(s)
    if s in ("","na","n/a","nan","null"):return None
    x=float(s)
    if not math.isfinite(x) or x<0:raise ValueError("invalid_nonnegative_numeric")
    return x
def count(s):
    a=val(s)
    if a is None:return None
    if not a.is_integer():raise ValueError("count_not_integer")
    return int(a)
def day(s):
    s=str(s).strip()
    for p in ("%Y-%m-%d","%m/%d/%Y","%m/%d/%y"):
        try:d=datetime.strptime(s,p).date();break
        except ValueError:continue
    else:raise ValueError("unsupported_date_format")
    if d.year!=2018 or not 8<=d.month<=11:raise ValueError("outside_documented_date_scope")
    return d.isoformat()
def pearson(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    x=a-a.mean();y=b-b.mean();den=np.linalg.norm(x)*np.linalg.norm(y)
    return float(x@y/den) if den>0 else None
def spearman(a,b):return pearson(rankdata(a,method="average"),rankdata(b,method="average"))
def quartile(a):
    a=np.asarray(a,float);n=len(a);k=math.ceil(n/4)
    cut=np.sort(a)[-k];hi=a>cut;eq=a==cut
    out=hi.astype(float);out[eq]=(k-hi.sum())/eq.sum()
    assert np.isclose(out.sum(),k) and (out>=0).all() and (out<=1).all()
    return out,k,bool((eq.sum()>1) and (0<out[eq][0]<1))
def metrics(a,b,ea,eb):
    a=np.asarray(a,float);b=np.asarray(b,float);ea=np.asarray(ea,float);eb=np.asarray(eb,float)
    x=a/ea;y=b/eb;r=spearman(x,y)
    if r is None:return None
    p,k,t=quartile(x);q,k2,t2=quartile(y);assert k==k2
    m=np.minimum(p,q).sum();ma=np.maximum(p,q).sum()
    return {"spearman_rates":r,"pearson_log1p_rates":pearson(np.log1p(x),np.log1p(y)),
        "pearson_counts":pearson(a,b),"spearman_counts":spearman(a,b),
        "top_quartile_fractional_overlap":float(m/k),"top_quartile_jaccard":float(m/ma),
        "top_quartile_product_overlap":float(p@q/k),"independent_label_product_reference":k/len(a),
        "cutoff_ties":int(t)+int(t2),"positive_acoustic":int((a>0).sum()),"positive_video":int((b>0).sum()),
        "both_zero":int(((a==0)&(b==0)).sum())}
def describe(m):
    return {"equal_turbine_mean":float(np.mean(m)),"min":float(np.min(m)),"max":float(np.max(m)),
      "positive_count":int(sum(x>0 for x in m))}
def tests():
    assert np.allclose(quartile([0,0,0,0])[0],[.25]*4)
    assert np.allclose(quartile([0,1,1,2,3,3,3,3])[0],[0,0,0,0,.5,.5,.5,.5])
    assert np.isclose(spearman([1,2,3],[3,2,1]),-1) and np.isclose(spearman([1,2,3],[1,2,3]),1)
    assert count("0")==0 and count("NA") is None
    try:count("1.5")
    except ValueError:pass
    else:raise AssertionError("fractional count accepted")
    assert np.isclose(metrics([1,2,6],[1,2,3],[1,1,2],[1,1,1])["spearman_rates"],1)
    assert all(not v for v in role_candidates(["a"],{"a":{"definition":"unknown","units_and_domains":[]}}).values())
def main():
    dest=OUT/"audit_v56_maui_night_concordance.json"
    o={"status":"admission_in_progress","source_doi":DOI,"source_item":ID,"claim_boundary":"Separate 2018 field campaign, same taxon/research group; rates per own observed effort, not common air volume or matched time window, no latent activity inference."}
    def save():dest.write_text(json.dumps(o,indent=2,allow_nan=False))
    def stop(s):o["status"]=s;save();print(dest.read_text());return 0
    save()
    try:
        tests();o["synthetic_checks"]="pass"
        b,xml=fetch(o);save()
        ds=dictionary(xml)
        text=b.decode("utf-8-sig")
        rd=csv.reader(io.StringIO(text,newline=""));h=next(rd);rows=[z for z in rd if any(norm(x) not in ("","na","null","nan","n/a") for x in z)]
        o["schema"]={"rows":len(rows),"column_count":len(h),"wrong_width":sum(len(z)!=len(h) for z in rows),
            "header_duplicate_count":len(h)-len(set(h)),"fields":[{"name":publicname(c),"missing":sum(norm(z[i]) in ("","na","null","nan","n/a") for z in rows if len(z)==len(h)),
                "definition":safe(ds.get(c,{}).get("definition","")),"units_and_domains":[safe(x) for x in ds.get(c,{}).get("units_and_domains",[])][:6]} for i,c in enumerate(h)]}
        save()
        if o["schema"]["wrong_width"] or o["schema"]["header_duplicate_count"]:return stop("STOP_TABLE_STRUCTURE")
        candidates=role_candidates(h,ds)
        o["documented_role_candidates"]={k:[{"field":publicname(c),"unit_to_hours":v} for c,v in q] for k,q in candidates.items()}
        save()
        if not all(len(q)==1 for q in candidates.values()):return stop("STOP_AMBIGUOUS_ROLE_OR_EFFORT")
        k={r:h.index(v[0][0]) for r,v in candidates.items()};scale={r:v[0][1] for r,v in candidates.items()}
        if len(set(k.values()))!=6:return stop("STOP_NONUNIQUE_ROLE")
        seen=set();data=[];bad_eff=0
        for z in rows:
            t=z[k["turbine"]].strip();assert norm(t) not in ("","na","n/a","nan","null")
            key=(t,day(z[k["date"]]))
            if key in seen:return stop("STOP_DUPLICATE_TURBINE_NIGHT")
            seen.add(key)
            a=count(z[k["a_count"]]);v=count(z[k["v_count"]]);ea=val(z[k["a_effort"]]);ev=val(z[k["v_effort"]])
            if ea is not None:ea*=scale["a_effort"]
            if ev is not None:ev*=scale["v_effort"]
            if (a is not None and a>0 and (ea is None or ea<=0)) or (v is not None and v>0 and (ev is None or ev<=0)):bad_eff+=1
            data.append((t,a,v,ea,ev))
        sites={x[0] for x in data}
        ta=sum(x[1] for x in data if x[1] is not None);tv=sum(x[2] for x in data if x[2] is not None)
        ea=sum(x[3] for x in data if x[3] is not None);ev=sum(x[4] for x in data if x[4] is not None)
        o["source_QA"]={"turbines":len(sites),"acoustic_total_events":ta,"visual_total_events":tv,
            "acoustic_total_effort_hours":ea,"visual_total_effort_hours":ev,"effort_diff_from_rounded_report_hours":[ea-3036,ev-5066],
            "positive_count_without_positive_effort_rows":bad_eff,
            "complete_positive_effort_nights_acoustic":sum(x[1] is not None and x[3] is not None and x[3]>0 for x in data),
            "complete_positive_effort_nights_video":sum(x[2] is not None and x[4] is not None and x[4]>0 for x in data)}
        save()
        if len(sites)!=4 or (ta,tv)!=(244,384) or bad_eff:return stop("STOP_REPORT_RECONCILIATION_OR_EFFORT")
        paired=[x for x in data if all(v is not None for v in x[1:]) and x[3]>0 and x[4]>0]
        c=Counter(x[0] for x in paired);eligible={s for s,n in c.items() if n>=20};kept=[x for x in paired if x[0] in eligible]
        o["paired_support"]={"all_nights":len(data),"both_positive_effort_with_counts":len(paired),
            "turbines_with_ge20_paired_nights":len(eligible),"retained_nights":len(kept),
            "paired_nights_per_turbine_min_median_max":[min([c[s] for s in sites]),float(np.median([c[s] for s in sites])),max([c[s] for s in sites])]}
        save()
        if len(eligible)<3:return stop("STOP_PAIRED_SUPPORT")
        folds=[]
        for s in sorted(eligible):
            x=np.array([z[1:] for z in kept if z[0]==s],float)
            m=metrics(*x.T)
            if m is None:return stop("STOP_CONSTANT_RATE")
            folds.append(m)
        m={k:describe([x[k] for x in folds]) for k in ("spearman_rates","pearson_log1p_rates","pearson_counts","spearman_counts","top_quartile_fractional_overlap","top_quartile_jaccard","top_quartile_product_overlap","independent_label_product_reference") if all(x[k] is not None for x in folds)}
        x=np.array([z[1:] for z in kept],float)
        o["result"]={"equal_turbine_metrics":m,"paired_pooled_spearman_rates":spearman(x[:,0]/x[:,2],x[:,1]/x[:,3]),
            "top_quartile_cutoff_ties":sum(z["cutoff_ties"] for z in folds),"positive_acoustic_rows":sum(z["positive_acoustic"] for z in folds),
            "positive_video_rows":sum(z["positive_video"] for z in folds),"both_zero_rows":sum(z["both_zero"] for z in folds),
            "leave_one_turbine_spearman_mean_range":[float(min(np.mean([z["spearman_rates"] for j,z in enumerate(folds) if i!=j]) for i in range(len(folds)))),
                float(max(np.mean([z["spearman_rates"] for j,z in enumerate(folds) if i!=j]) for i in range(len(folds))))],
            "incomplete_rank_agreement_descriptive_criterion":bool(m["spearman_rates"]["equal_turbine_mean"]<.5 and m["top_quartile_product_overlap"]["equal_turbine_mean"]<.75)}
        o["status"]="SCORED_SOURCE_LOCAL_NIGHT_CONCORDANCE"
    except Exception as e:
        import traceback
        o["status"]="blocked";o["error_type"]=type(e).__name__;o["failure_functions"]=[x.name for x in traceback.extract_tb(e.__traceback__)[-5:]]
        if isinstance(e,requests.HTTPError) and e.response is not None:o["http_status"]=e.response.status_code
    save();print(dest.read_text())
    return 2 if o["status"]=="blocked" else 0
if __name__=="__main__":raise SystemExit(main())
