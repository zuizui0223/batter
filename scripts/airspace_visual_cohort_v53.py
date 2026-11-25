"""V53 fixed USGS visual cohort reconciliation and conditional whole-site prediction."""
import csv,io,re,json,hashlib,math
from collections import Counter,defaultdict
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
import requests
from roost_fd_source_audit_v2 import OUT
ID="5bae6e45e4b08583a5d310ce"
PINS={
"Hawaiian_hoary_bat_acoustic_visual_detections.csv":(109816,"b3923a6ae96c76072c8146808ca56e09a4069fcb46b36fa34185847f9548a7ca"),
"Hawaiian_hoary_bat_acoustic_visual_detections_FGDC.xml":(32787,"223948ec5183a89213afb1b078e35f6c1d521a067052759a47eb87f13c156dac")}
HEADER=["Site__acoustic_sample","Date_acoustic","Time_acoustic","Match_acoustic_video","Site__video_sample","Date_video","Time_video","Match_video_acoustic","Confidence","Proximity","Flight","Multiple_bats","Difference"]
TABLE=np.array([[[153,114],[116,29],[15,7]],[[22,122],[45,78],[9,33]],[[5,0],[11,11],[7,7]]],int)
NIGHTS=sorted([(24,12),(43,13),(20,13),(7,4),(3,2),(19,3),(47,21),(27,9),(56,0),(24,1),(13,1),(17,1),(22,0),(20,0),(15,5),(16,3),(243,232),(107,49),(32,10),(29,4)])
HEAD={"User-Agent":"batter-USGS-cohort-reconciliation-v53/1.0"}
def sha(b):return hashlib.sha256(b).hexdigest()
def fetch():
    r=requests.get("https://www.sciencebase.gov/catalog/item/"+ID+"?format=json",headers=HEAD,timeout=(10,30));r.raise_for_status();j=r.json()
    assert j["id"]==ID and j.get("parentId")=="59725a0ee4b0ec1a4885ee40"
    out={}
    for f in j["files"]:
        name=f["name"]
        if name not in PINS:continue
        size,digest=PINS[name];assert int(f["size"])==size
        url=f.get("downloadUri") or f.get("url")
        u=urlparse(url);assert u.scheme=="https" and (u.hostname or "").endswith((".sciencebase.gov",".usgs.gov"))
        data=bytearray()
        with requests.get(url,headers=HEAD,stream=True,timeout=(15,60)) as rr:
            rr.raise_for_status()
            for c in rr.iter_content(65536):
                data.extend(c);assert len(data)<=size
        b=bytes(data);assert len(b)==size and sha(b)==digest
        if name.endswith(".xml"):assert hashlib.md5(b).hexdigest()=="a0da6ba07b6f4cf51f1bae01d1b91672"
        out[name]=b
    assert set(out)==set(PINS)
    return next(v for k,v in out.items() if k.endswith(".csv")),next(v for k,v in out.items() if k.endswith(".xml"))
def tag(x):return x.tag.rsplit("}",1)[-1].lower()
def child(n,k):
    for x in n:
        if tag(x)==k:return " ".join("".join(x.itertext()).split())
    return ""
def docs(b):
    root=ET.fromstring(b);a={}
    for n in root.iter():
        if tag(n)!="attr":continue
        label=child(n,"attrlabl")
        if label not in HEADER:continue
        ed={}
        for d in n.iter():
            if tag(d)=="edom":
                k=child(d,"edomv");v=child(d,"edomvd")
                if k:ed[k]=v
        a[label]={"definition":child(n,"attrdef"),"enumerated":ed}
    return a
def norm(s):
    return re.sub(r"\s+"," ",str(s or "").strip().casefold())
def safe_text(s):
    # Only public semantic descriptions, never literal observed values or sites.
    s=" ".join(str(s or "").split())
    if re.search(r"latitude|longitude|coordinate|https?://|@|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",s,re.I):
        return {"redacted":True,"sha256":sha(s.encode())}
    return s[:450]
def metadata_summary(a):
    keep=("Match_video_acoustic","Confidence","Proximity","Flight","Site__video_sample","Date_video","Time_video","Multiple_bats","Difference")
    return {k:{"definition":safe_text(a[k]["definition"]),
              "enumerated":[{"label":safe_text(x),"definition":safe_text(y)} for x,y in a[k]["enumerated"].items()]} for k in keep if k in a}
def missing(x):return norm(x) in ("","na","n/a","nan","null")
def categorical_counts(rows,i,allowed):
    c=Counter(norm(r[i]) for r in rows)
    return {k if k in allowed else "label_"+sha(k.encode())[:10]:n for k,n in c.items()}
def confidence_key(d):
    # Only an explicit, uniquely documented positive-confidence code.
    e={norm(k):norm(v) for k,v in d["enumerated"].items()}
    hits=[]
    for k,v in e.items():
        if k in ("high","certain","confirmed","definite","high confidence"):
            if re.search(r"\b(?:bat|identif\w*|confiden\w*|certain\w*|definite\w*)\b",v+" "+norm(d["definition"])):hits.append(k)
        elif re.search(r"\b(?:high confidence|certain(?:ly)? (?:a )?bat|confirmed bat|definite bat|unambiguous bat)\b",v) and not re.search(r"\b(?:not|low|medium|uncertain|possible|probable)\b",v):hits.append(k)
    if len(hits)==1:return hits[0]
    return None
def binary_map(d):
    e={norm(k):norm(v) for k,v in d["enumerated"].items()}
    m={}
    for k,v in e.items():
        # Recognize only explicit semantic yes/no correspondence.
        neg=bool(re.search(r"\b(?:no (?:match\w*|acoustic\w*|correspond\w*)|not match\w*|unmatch\w*|without (?:acoustic\w*|match\w*)|no|absen\w*)\b",v))
        pos=bool(re.search(r"\b(?:match\w*|correspond\w*|yes|present|synchron\w*)\b",v))
        if neg:m[k]=0
        elif pos:m[k]=1
        elif k in ("yes","no"):m[k]=int(k=="yes")
    if set(m.values())=={0,1} and len(m)==2:return m
    definition=norm(d["definition"])
    if re.search(r"\b0\s*[:=–-]\s*(?:no|not match\w*|unmatch\w*|absen\w*)\b",definition) and re.search(r"\b1\s*[:=–-]\s*(?:yes|match\w*|present)\b",definition):
        return {"0":0,"1":1}
    return None
def category_map(d,names):
    # Literal documented labels, or explicit enum definition with the exact category word.
    out={x:i for i,x in enumerate(names)}
    for k,v in d.get("enumerated",{}).items():
        a=norm(k);v=norm(v)
        found=[i for i,x in enumerate(names) if re.search(r"\b"+re.escape(x)+r"\b",v)]
        if a not in out and len(found)==1:out[a]=found[0]
    return out
def duplicate_keys(rows,inds):
    c=Counter(tuple(r[i] for i in inds) for r in rows)
    return sum(n-1 for n in c.values())
def equalweights(s):
    c=Counter(s.tolist());w=np.array([1/(len(c)*c[k]) for k in s],float)
    assert np.isclose(w.sum(),1);return w
def features(d,f,kind):
    a=np.ones((len(d),1))
    if kind>=1:a=np.column_stack((a,np.eye(3)[d]))
    if kind>=2:a=np.column_stack((a,np.eye(3)[f]))
    return a
def loss_grad(b,X,y,w):
    eta=X@b;pen=.02
    loss=float(np.sum(w*(np.logaddexp(0,eta)-y*eta))+.5*pen*np.sum(b[1:]**2))
    grad=X.T@(w*(expit(eta)-y))
    grad[1:]+=pen*b[1:]
    return loss,grad
def fit(X,y,w):
    assert set(y.tolist())=={0,1}
    m=minimize(lambda b:loss_grad(b,X,y,w),np.zeros(X.shape[1]),jac=True,method="L-BFGS-B",options={"ftol":1e-12,"gtol":1e-9,"maxiter":1000})
    assert m.success and np.isfinite(m.x).all() and np.isfinite(m.fun)
    return m.x
def score(y,eta):
    return y*eta-np.logaddexp(0,eta),(y-expit(eta))**2
def evaluate(s,y,d,f):
    a=Counter(s.tolist());keep={x for x,n in a.items() if n>=10}
    mask=np.array([x in keep for x in s]);o={"eligible_sites":len(keep),"retained_visual_rows":int(mask.sum()),"excluded_visual_rows":int((~mask).sum())}
    if len(keep)<6:return {**o,"status":"STOP_SITE_SUPPORT"}
    s,y,d,f=[v[mask] for v in (s,y,d,f)]
    folds=[]
    for k in sorted(keep):
        te=s==k;tr=~te
        if set(y[tr].tolist())!={0,1}:return {**o,"status":"STOP_TRAIN_OUTCOME_SUPPORT"}
        w=equalweights(s[tr]);r=[]
        for i in range(3):
            X=features(d,f,i);b=fit(X[tr],y[tr],w)
            l,br=score(y[te],X[te]@b);r.append((float(l.mean()),float(br.mean())))
        folds.append(r)
    z=np.array(folds,float)
    def contrast(old,new):
        g=z[:,new,0]-z[:,old,0];b=z[:,old,1]-z[:,new,1]
        omit=(g.sum()-g)/(len(g)-1)
        return {"equal_site_mean_log_score_gain_nats":float(g.mean()),"equal_site_mean_brier_reduction":float(b.mean()),
          "sites_improved_log_score":int((g>0).sum()),"sites_improved_brier":int((b>0).sum()),
          "leave_one_site_omission_mean_range":[float(omit.min()),float(omit.max())],
          "descriptive_concordance":bool(g.mean()>0 and (g>0).sum()>len(g)/2)}
    return {**o,"status":"SCORED","models":{f"Q{i}":{"mean_log_score":float(z[:,i,0].mean()),"mean_brier":float(z[:,i,1].mean())} for i in range(3)},
      "distance_Q1_vs_Q0":contrast(0,1),"flight_Q2_vs_Q1":contrast(1,2)}
def test():
    s=np.array(["a","a","b","b"]);d=np.array([0,0,1,1]);f=np.array([1,2,0,1]);y=np.array([0,1,0,1])
    w=equalweights(s)
    assert np.allclose(w,.25) and np.allclose(equalweights(np.array(["a","a","b"])),[.25,.25,.5])
    assert [features(d,f,i).shape[1] for i in range(3)]==[1,4,7]
    assert abs(fit(features(d,f,0),y,w)[0])<1e-10
    X=features(d,f,2);b=np.arange(X.shape[1],dtype=float)/10
    l,g=loss_grad(b,X,y,w)
    for i in range(len(b)):
        delta=np.zeros(len(b));delta[i]=1e-6
        assert abs((loss_grad(b+delta,X,y,w)[0]-loss_grad(b-delta,X,y,w)[0])/2e-6-g[i])<1e-6
def main():
    dest=OUT/"audit_v53_visual_cohort_prediction.json"
    o={"status":"cohort_audit_only","ecological_claim_boundary":"Acoustic correspondence conditional on visually detected passes; not call emission or true occupancy."}
    def save():dest.write_text(json.dumps(o,indent=2,allow_nan=False))
    def stop(reason):
        o["status"]=reason;save();print(dest.read_text());return 0
    save()
    try:
        test();o["synthetic_checks"]="pass"
        b,xml=fetch();o["source_hashes_verified"]=True
        ds=docs(xml);o["dictionary"]=metadata_summary(ds);save()
        r=csv.reader(io.StringIO(b.decode("utf-8-sig"),newline=""));h=next(r);rows=[x for x in r if any(not missing(k) for k in x)]
        assert h==HEADER and len(rows)==2744 and all(len(x)==13 for x in rows)
        block=lambda z,ii:sum(not missing(z[i]) for i in ii)
        ac=Counter(block(z,range(0,4)) for z in rows);vc=Counter(block(z,range(4,12)) for z in rows)
        video=[z for z in rows if block(z,range(4,12))==8]
        o["raw_structure"]={"rows":len(rows),"acoustic_nonmissing_fields_per_row":dict(ac),"video_nonmissing_fields_per_row":dict(vc),
          "video_rows":len(video),"duplicate_full_rows":len(rows)-len({tuple(z) for z in rows}),
          "duplicate_video_site_date_time_keys":duplicate_keys(video,(4,5,6)),
          "video_confidence_counts":categorical_counts(video,8,{"high","medium","low","certain","confirmed","definite","high confidence","uncertain","probable","possible"}),
          "video_match_code_counts":categorical_counts(video,7,{"0","1","yes","no"}),
          "video_proximity_counts":categorical_counts(video,9,{"near","mid","far"}),
          "video_flight_counts":categorical_counts(video,10,{"straight","curved","erratic"})}
        save()
        if set(ac)-{0,4} or set(vc)-{0,8} or len(video)!=949:return stop("STOP_INCOMPLETE_OR_CHANGED_BLOCKS")
        if not all(k in ds for k in ("Confidence","Match_video_acoustic","Proximity","Flight")):return stop("STOP_DICTIONARY")
        hi=confidence_key(ds["Confidence"]);bm=binary_map(ds["Match_video_acoustic"])
        o["semantic_gate"]={"unique_documented_high_confidence":hi is not None,"explicit_documented_binary_match":bm is not None}
        save()
        if hi is None or bm is None:return stop("STOP_AMBIGUOUS_COHORT_OR_MATCH_SEMANTICS")
        # Exactly one high-confidence candidate; no other filters, no search over categories.
        rr=[z for z in video if norm(z[8])==hi]
        dm=category_map(ds["Proximity"],("near","mid","far"));fm=category_map(ds["Flight"],("straight","curved","erratic"))
        if any(norm(z[7]) not in bm or norm(z[9]) not in dm or norm(z[10]) not in fm for z in rr):return stop("STOP_UNKNOWN_CATEGORY")
        d=np.array([dm[norm(z[9])] for z in rr],int);f=np.array([fm[norm(z[10])] for z in rr],int);y=np.array([bm[norm(z[7])] for z in rr],int)
        table=np.zeros((3,3,2),int)
        for i,j,k in zip(d,f,y):table[i,j,1-k]+=1
        s=np.array([norm(z[4]) for z in rr])
        ng=defaultdict(list)
        for z,v in zip(rr,y):ng[(norm(z[4]),norm(z[5]))].append(int(v))
        actual=sorted((len(v),sum(v)) for v in ng.values())
        dup=duplicate_keys(rr,(4,5,6))
        exact=bool(len(rr)==784 and y.sum()==383 and np.array_equal(table,TABLE) and len(set(s.tolist()))==10 and len(ng)==20 and actual==NIGHTS and dup==0)
        o["reconciliation"]={"candidate_rows":len(rr),"matches":int(y.sum()),"sites":len(set(s.tolist())),"site_date_groups":len(ng),
          "duplicate_candidate_site_date_time_keys":dup,"table2_count_difference":(table-TABLE).tolist(),
          "table2_exact":bool(np.array_equal(table,TABLE)),"table1_nightly_multiset_exact":actual==NIGHTS,
          "sites_with_ge10_visual_rows":sum(n>=10 for n in Counter(s.tolist()).values()),"all_gates_pass":exact}
        save()
        if not exact:return stop("STOP_PUBLISHED_COHORT_RECONCILIATION")
        o["prediction"]=evaluate(s,y,d,f);o["status"]="reconciled_cohort_scored" if o["prediction"]["status"]=="SCORED" else o["prediction"]["status"]
    except Exception as e:
        import traceback
        o["status"]="blocked";o["error_type"]=type(e).__name__;o["failure_functions"]=[x.name for x in traceback.extract_tb(e.__traceback__)[-5:]]
        if isinstance(e,requests.HTTPError) and e.response is not None:o["http_status"]=e.response.status_code
    save();print(dest.read_text())
    return 2 if o["status"]=="blocked" else 0
if __name__=="__main__":raise SystemExit(main())
