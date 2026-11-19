#!/usr/bin/env python3
"""Reproduce published 2015/2016 bat distress-call source data transparently.

Original source is fetched and checksum verified on a transient GitHub runner.
No raw original CSV/XLSX is committed or sent as a workflow artifact.
Session-level derived contrasts may be uploaded; colony/site identities unresolved.
"""
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile

import h1_2016_context_source_gate as gate

URL_2016="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4892459/supplementaryFiles"
URL_2015="https://ndownloader.figshare.com/files/2126435"
SHA_2016="28402ac6c969f7a6c13acf5f90192afbfa4b6c5158e1bbc8f657b55f255b05ef"
MD5_2015="991be124c47f48a955fa5a0a40dd864c"
OUT=Path(os.getenv("H1_CONTEXT_EMPIRICAL_RESULT","/tmp/h1_2015_2016_context_aggregate.json"))
COLS={"A","B","C","D","E","F"}
NS=gate.NS

def read_2016():
    package,http=gate.fetch(URL_2016)
    raw,kind=gate.original_xlsx(package)
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=SHA_2016:raise ValueError("2016 original source checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        shared=[]
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("x:si",NS):
                shared.append("".join(t.text or "" for t in si.findall(".//x:t",NS)))
        root=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        records=[]
        for row in root.findall(".//x:sheetData/x:row",NS):
            cells={}
            for c in row.findall("x:c",NS):
                m=re.match(r"^[A-Z]+",c.attrib.get("r",""))
                if not m or m.group() not in COLS:continue
                key=m.group()
                val=c.find("x:v",NS)
                text=val.text if val is not None else None
                if c.attrib.get("t")=="s" and text is not None:text=shared[int(text)]
                if c.attrib.get("t")=="inlineStr":
                    text="".join(t.text or "" for t in c.findall(".//x:t",NS))
                cells[key]=text
            if cells:records.append(cells)
    if len(records)!=115:raise ValueError("Expected 114 original observation rows")
    raw=records[1:]
    assert records[0]["A"]=="colony"
    assert records[0]["B"]=="location"
    assert records[0]["C"]=="stimulus typ"
    assert {r["B"] for r in raw}=={"within","close","foraging"}
    assert {r["C"] for r in raw}=={"S. bilineata","M. molossus"}
    info=defaultdict(dict)
    unverified_f=0;f_disagreements=[]
    for r in raw:
        session=int(r["A"]);location=r["B"];caller=r["C"]
        if session not in range(1,20):raise ValueError("unexpected 2016 session label")
        if (location,caller) in info[session]:raise ValueError("duplicate original session x treatment")
        pre=float(r["D"]);reaction=float(r["E"])
        if not (math.isfinite(pre) and math.isfinite(reaction)) or min(pre,reaction)<0:
            raise ValueError("missing/nonfinite pre/reaction original counts")
        score=reaction-pre
        if r.get("F") not in (None,""):
            f=float(r["F"])
            if math.isfinite(f) and abs(f-score)>1e-4:
                f_disagreements.append({"session":session,"location":location,"caller":caller,"diff":float(f-score)})
        else:unverified_f+=1
        info[session][(location,caller)]=score
    if len(info)!=19 or any(len(v)!=6 for v in info.values()):
        raise ValueError("incomplete original within-session cross design")
    if f_disagreements:
        # Signed raw F is author's published calculation. A mismatch is an
        # unresolved provenance/data quality issue, NOT silently repaired.
        raise ValueError("2016 original responsiveness column F != reaction-pre; n="+str(len(f_disagreements))+" maxabs="+str(max(abs(x["diff"]) for x in f_disagreements)))

    session_rows=[]
    for i in sorted(info):
        v=info[i]
        s=lambda where,caller:v[(where,caller)]
        x=(s("within","S. bilineata")-s("within","M. molossus"))-(s("foraging","S. bilineata")-s("foraging","M. molossus"))
        near=(s("close","S. bilineata")-s("close","M. molossus"))-(s("foraging","S. bilineata")-s("foraging","M. molossus"))
        cons=s("within","S. bilineata")-s("foraging","S. bilineata")
        cons_near=s("close","S. bilineata")-s("foraging","S. bilineata")
        session_rows.append({"session_code":i,"specificity_within_minus_foraging":x,
                             "specificity_close_minus_foraging":near,
                             "conspecific_within_minus_foraging":cons,
                             "conspecific_close_minus_foraging":cons_near})
    cond={
       loc:{caller:float(statistics.mean(info[i][(loc,caller)] for i in info))
            for caller in ["S. bilineata","M. molossus"]}
       for loc in ["within","close","foraging"]
    }
    def summarize(column):
        x=[row[column] for row in session_rows]
        y=sorted(x)
        S=sum(x)
        lower=(S+sum(y[:3]))/22
        upper=(S+sum(y[-3:]))/22
        return {"n_session_labels":19,"session_equal_mean":float(statistics.mean(x)),
                "session_median":float(statistics.median(x)),
                "n_positive":sum(v>0 for v in x),
                "n_negative":sum(v<0 for v in x),
                "n_zero":sum(v==0 for v in x),
                "unknown_colony_mapping_11_colony_equal_mean_bounds":[lower,upper],
                "bounds_assumption":"8 twice-sampled physical colonies + 3 once; mapping among 19 labels unknown",
                "actual_colony_cluster_p":"STOP_UNIDENTIFIED"}
    return {
       "n_original_rows":len(raw),"n_session_labels":len(info),
       "n_real_colonies_published":11,"data_file_sha256":digest,
       "response_column_F_cached_missing":unverified_f,
       "response_column_F_checks_pass":True,
       "mean_responsiveness_by_location_and_caller":cond,
       "primary_call_by_location":summarize("specificity_within_minus_foraging"),
       "secondary_call_by_location_close":summarize("specificity_close_minus_foraging"),
       "published_location_within":summarize("conspecific_within_minus_foraging"),
       "published_location_close":summarize("conspecific_close_minus_foraging"),
       "session_contrasts":session_rows,
       "causal_order_identification":"STOP_LOCATION_ORDER_DAWN_DUSK_CONFOUNDED"
    }

def read_2015():
    payload,http=gate.fetch(URL_2015)
    digest=hashlib.md5(payload).hexdigest()
    if digest!=MD5_2015:raise ValueError("2015 original MD5 mismatch")
    text=payload.decode("utf-8-sig")
    rows=list(csv.DictReader(io.StringIO(text,newline=""),delimiter=","))
    if len(rows)!=308:raise ValueError("2015 total trial n should be 308")
    if Counter(r["Treatment"] for r in rows)!=Counter({"distress":155,"noise":153}):
        raise ValueError("2015 distress/noise totals don't match paper")
    expected=("c molossus","t molossus","c saccopteryx","t saccopteryx")
    for r in rows:
        for col in expected:
            r[col]=float(r[col])
            if not math.isfinite(r[col]) or r[col]<0:raise ValueError("invalid original pass data")
        r["session"]=int(r["session"])
    sessions=defaultdict(list)
    for r in rows:sessions[r["session"]].append(r)
    if len(sessions)!=12:raise ValueError("not 12 source playback sessions")
    result={}
    for rec,pre_col,play_col in [("M. molossus","c molossus","t molossus"),
                                 ("S. bilineata","c saccopteryx","t saccopteryx")]:
        per_session=[]
        for session,rr in sorted(sessions.items()):
            d={}
            for treatment in ("distress","noise"):
                sub=[r for r in rr if r["Treatment"]==treatment]
                if not sub:raise ValueError("session without both control and treatment")
                vals=[r[play_col]-r[pre_col] for r in sub]
                d[treatment]=statistics.mean(vals)
            per_session.append({"session_code":session,"n_trials":len(rr),
                    "distress_n":sum(r["Treatment"]=="distress" for r in rr),
                    "noise_n":sum(r["Treatment"]=="noise" for r in rr),
                    "distress_minus_noise_change":d["distress"]-d["noise"]})
        values=[x["distress_minus_noise_change"] for x in per_session]
        all_mean=lambda t:float(statistics.mean(r[play_col]-r[pre_col] for r in rows if r["Treatment"]==t))
        # author-selected nonzero pre OR playback: sensitivity only
        nonzero=[r for r in rows if (r[pre_col]!=0 or r[play_col]!=0)]
        filtered_zeros={"observations_retained":len(nonzero),
                        "distress_change_mean":float(statistics.mean(r[play_col]-r[pre_col] for r in nonzero if r["Treatment"]=="distress")),
                        "noise_change_mean":float(statistics.mean(r[play_col]-r[pre_col] for r in nonzero if r["Treatment"]=="noise"))}
        result[rec]={
           "session_equal_mean_distress_minus_noise":float(statistics.mean(values)),
           "session_median_distress_minus_noise":float(statistics.median(values)),
           "n_session_labels":len(values),"n_positive_sessions":sum(v>0 for v in values),
           "n_negative_sessions":sum(v<0 for v in values),"n_zero_sessions":sum(v==0 for v in values),
           "all_trials_distress_change_mean":all_mean("distress"),
           "all_trials_noise_change_mean":all_mean("noise"),
           "published_outcome_selected_sensitivity":filtered_zeros,
           "per_session":per_session,
           "n_independent_physical_sites_claimed":8,
           "site_mapping_in_original_fields":"NOT_VERIFIED_NO_INDEPENDENT_SITE_INFERENCE"
        }
    return {"n_trials":len(rows),"n_source_sessions":len(sessions),
            "published_independent_sites":8,"md5":digest,
            "proximity_counts":dict(Counter(r["Roost proximity"] for r in rows)),
            "treatment_counts":dict(Counter(r["Treatment"] for r in rows)),
            "by_recipient":result,
            "causal_treatment_order":"DISTRESS_NOISE_ALTERNATE_NOT_FULLY_RANDOM"}

def run():
    a=read_2016()
    b=read_2015()
    return {"status":"ORIGINAL_FILES_CHECKSUM_VERIFIED_SINGLE_STUDY_REANALYSES",
            "prior_art_not_novel_independent_experiments":True,
            "registered_contracts":["H1_CONTEXT_MAPPING_AMBIGUITY_PREOUTCOME_V1.md",
                                     "H1_CARTER_2015_ORIGINAL_ANALYSIS_CONTRACT_V1.md"],
            "source_2016":a,"source_2015":b,
            "not_comparable_to_2019_buzz_x_baseline":True,
            "species_level_meta_analysis":"STOP_DIFFERENT_STIMULUS_CONTROL_RESPONSES",
            "remembered_personal_information_or_reciprocity_measured":False}

if __name__=="__main__":
    data=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    x=data["source_2016"];print("ORIGINAL 2016 SHA256",x["data_file_sha256"])
    print("2016 mean responsiveness by location+caller:",json.dumps(x["mean_responsiveness_by_location_and_caller"]))
    for key in ("primary_call_by_location","secondary_call_by_location_close",
                "published_location_within","published_location_close"):
        print("2016",key,json.dumps(x[key]))
    y=data["source_2015"];print("ORIGINAL 2015 MD5",y["md5"])
    for k,v in y["by_recipient"].items():
        print("2015",k,"n",v["n_session_labels"],
              "session mean",v["session_equal_mean_distress_minus_noise"],
              "positive",v["n_positive_sessions"],
              "all trial means",v["all_trials_distress_change_mean"],v["all_trials_noise_change_mean"],
              "filtered retained",v["published_outcome_selected_sensitivity"])
