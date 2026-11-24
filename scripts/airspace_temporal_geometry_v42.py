"""V42 structural time and geometry QA; no numeric flight outcomes or raw IDs."""
import csv,io,json,hashlib,math,re,zipfile
from collections import Counter,defaultdict
from datetime import datetime
from xml.etree import ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import requests
from airspace_schema_v41 import ITEMS,fetch,field,normalized,kind,quant_counts
from roost_fd_source_audit_v2 import OUT

PINS={"omalley_csv":"0772345a3bcbabb79e154fb6912a0e86c2d9d8dd532ab8aabee4c6f8124d6f8b",
"omalley_R":"ae3587e48b5382c9a88e063e5dabea560eee752c1361220424774b3ab1c4c7c9",
"barre_csv":"5425b39d4c36184567ec22b38a871ee27a7cf02834e021de4da82f6d0f065cdf"}
def sha(b):return hashlib.sha256(b).hexdigest()
def get(k):
    b=fetch(ITEMS[k]);assert sha(b)==PINS[k];return b
def rows(b,delimiter):
    r=csv.DictReader(io.StringIO(b.decode("utf-8-sig"),newline=""),delimiter=delimiter)
    return r.fieldnames,list(r)
def stats(values):
    a=sorted(values)
    if not a:return {"n":0}
    return {"n":len(a),"min":a[0],"median":(a[(len(a)-1)//2]+a[len(a)//2])/2,"max":a[-1]}
def fmt(s):
    s=str(s or "").strip()
    if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}(?:[.,]\d+)?",s):
        return "clock_fractional" if re.search(r"[.,]",s) else "clock_whole_seconds"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:\d{2})?",s):
        return "datetime_fractional" if re.search(r"[.,]",s) else "datetime_whole_seconds"
    if kind(s) in ("numeric_finite","numeric_decimal_comma"):return "numeric"
    return "other_or_missing"
def time_parse(s):
    s=str(s or "").strip().replace(",",".");f=fmt(s)
    if f.startswith("clock"):
        h,m,sec=s.split(":");h=int(h);m=int(m);sec=float(sec)
        if not 0<=h<24 or not 0<=m<60 or not 0<=sec<60:return None
        return h*3600+m*60+sec
    if f.startswith("datetime"):
        try:return datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()
        except ValueError:return None
    # Numeric time units not assumed.
    if f=="numeric":return float(s)
    return None
def road():
    h,rs=rows(get("omalley_csv"),",");assert len(rs)==23554
    assert {"Site","Date","Survey","BatID","TrackID","Frame","X","Y","Height","Time"}<=set(h)
    g=defaultdict(list);identity=defaultdict(set);full=Counter();bad=0
    for r in rs:
        k=tuple(r[v] for v in ("Site","Date","Survey","BatID"))
        identity[r["BatID"]].add(tuple(r[v] for v in ("Site","Date","Survey","TrackID")))
        try:
            f=float(r["Frame"])
            if not math.isfinite(f) or not f.is_integer():raise ValueError()
            f=int(f)
        except (ValueError,TypeError):bad+=1;continue
        full[k+(f,)]+=1
        g[k].append(f)
    per_site=Counter();windows=[];runs=[];nonincrease=0;paths_with_gap=0
    for k,fs in g.items():
        nonincrease+=sum(b<=a for a,b in zip(fs,fs[1:]))
        paths_with_gap+=any(b-a>1 for a,b in zip(fs,fs[1:]))
        cur=[];rr=[]
        for f in fs:
            if cur and f!=cur[-1]+1:rr.append(cur);cur=[]
            cur.append(f)
        if cur:rr.append(cur)
        # Only complete consecutive frame runs; each t0,t1,t2 exactly 5 frames apart.
        n=sum(max(0,len(run)-10) for run in rr)
        runs.extend(map(len,rr));windows.append(n)
        if n>0:per_site[k[0]]+=1
    nsites=len({k[0] for k in g})
    return {"rows":len(rs),"sites":nsites,"distinct_BatID":len(identity),"site_date_survey_path_groups":len(g),
      "BatID_spans_multiple_source_contexts":sum(len(v)!=1 for v in identity.values()),
      "bad_frame_rows":bad,"duplicate_full_key_rows":sum(v-1 for v in full.values()),
      "nonincreasing_frame_pairs_in_file_order":nonincrease,"paths_with_forward_frame_gap":paths_with_gap,
      "consecutive_run_length":stats(runs),"exact_5frame_triplets_total":sum(windows),
      "triplets_per_path":stats(windows),"eligible_paths_per_site":stats([per_site[s] for s in {k[0] for k in g}]),
      "sites_ge10_paths_with_triplet":sum(v>=10 for v in per_site.values()),
      "separate_recorded_kinematic_structural_gate":bool(sum(v>=10 for v in per_site.values())>=6 and bad==0 and all(len(v)==1 for v in identity.values()) and all(v==1 for v in full.values())),
      "time_formats":dict(Counter(fmt(r["Time"]) for r in rs)),
      "physical_availability_admitted":False}
def solar():
    h,rs=rows(get("barre_csv"),";");assert len(rs)==15346
    assert {"id_site","typeSite","date","time","Trajectory_identifier","x (m)","y (m)","z (m)"}<=set(h)
    g=defaultdict(list);site_dates=defaultdict(set);site_arms=defaultdict(set);track_sites=defaultdict(set)
    for r in rs:
        k=tuple(r[x] for x in ("id_site","date","Trajectory_identifier"))
        g[k].append(r);site_dates[r["id_site"]].add(r["date"]);site_arms[r["id_site"]].add(r["typeSite"])
        track_sites[r["Trajectory_identifier"]].add(k[:2])
    time_formats=Counter(fmt(r["time"]) for r in rs)
    per_track=[];duplicates=0;nonincrease=0;backward=0;unparseable=0;single_time=0;all_distinct=0
    per_date=defaultdict(set)
    for s,dates in site_dates.items():
        for d in dates:per_date[d].add(s)
    for k,rr in g.items():
        tt=[time_parse(r["time"]) for r in rr]
        unparseable+=sum(t is None for t in tt)
        vv=[t for t in tt if t is not None];n=len(set(vv))
        per_track.append(n);duplicates+=len(vv)-n
        single_time+=int(n==1);all_distinct+=int(n==len(rr))
        nonincrease+=sum(b<=a for a,b in zip(vv,vv[1:]));backward+=sum(b<a for a,b in zip(vv,vv[1:]))
    finite_count={}
    for c in ("x (m)","y (m)","z (m)"):
        finite_count[c]=sum(kind(r[c]) in ("numeric_finite","numeric_decimal_comma") for r in rs)
    # Treatment labels explicitly recognized; never disclose nonstandard identifier labels.
    arm_counts=Counter()
    def arm(s):
        q=normalized(s)
        if q in ("control","c","ctrl","temoin"):return "control"
        if q in ("solar","s","solarpark","solarfarm","pv","photovoltaic","treatment"):return "solar"
        return "unrecognized_"+sha(str(s).encode())[:10]
    for a in site_arms.values():
        arm_counts[arm(next(iter(a))) if len(a)==1 else "mixed"]+=1
    return {"rows":len(rs),"headers":[field(c) for c in h],"sites":len(site_dates),"dates":len(per_date),"trajectory_groups":len(g),
      "trajectory_ID_multiple_site_dates":sum(len(v)!=1 for v in track_sites.values()),
      "site_multiple_dates":sum(len(v)!=1 for v in site_dates.values()),
      "site_multiple_treatment_labels":sum(len(v)!=1 for v in site_arms.values()),
      "recognized_arm_site_counts":dict(arm_counts),"sites_per_date":stats([len(s) for s in per_date.values()]),
      "xyz_finite_counts":finite_count,"time_formats":dict(time_formats),"time_unparseable":unparseable,
      "distinct_times_per_track":stats(per_track),"duplicate_track_time_rows":duplicates,
      "tracks_one_time_value":single_time,"tracks_all_distinct_times":all_distinct,
      "nonincreasing_time_pairs_in_file_order":nonincrease,"backward_time_pairs":backward,
      "exact_documented_pair_key_present":any(normalized(x) in ("pair","pairid","pairidentifier","idpair") for x in h),
      "physical_availability_admitted":False}
def r_source():
    txt=get("omalley_R").decode("utf-8-sig",errors="replace")
    items=[]
    for i,l in enumerate(txt.splitlines(),1):
        l=l.split("#",1)[0]
        if not re.search(r"\b(?:Frame|Time_s|Frames|fps|Height|BatID)\b",l,re.I):continue
        flags=[]
        if re.search(r"(?:/|\*)\s*50\b",l):flags.append("50fps_arithmetic_candidate")
        if re.search(r"\b(?:diff|lag|lead|arrange|order|group_by|summari[sz]e)\s*\(",l):flags.append("sequence_or_group_operation")
        if re.search(r"\bBatID\b",l,re.I):flags.append("flight_label_reference")
        if re.search(r"\bFrame\b|\bFrames\b",l,re.I):flags.append("frame_reference")
        if flags:items.append({"line":i,"tokens":flags})
    return {"line_count":len(txt.splitlines()),"tokens":items[:80],"matches":len(items)}
def supplement():
    url="https://besjournals.onlinelibrary.wiley.com/doi/suppl/10.1111/1365-2664.14555/supinfo/jpe14555-sup-0001-AppendixS1.docx"
    headers={"User-Agent":"batter-public-supporting-data-audit/1.0"}
    buf=bytearray()
    try:
        with requests.get(url,headers=headers,stream=True,timeout=(15,35)) as r:
            r.raise_for_status()
            for chunk in r.iter_content(65536):
                buf.extend(chunk)
                if len(buf)>200000:return {"status":"size_cap"}
    except requests.HTTPError as e:return {"status":"publisher_blocked","http_status":e.response.status_code if e.response is not None else None}
    b=bytes(buf)
    if not b.startswith(b"PK"):return {"status":"not_docx","bytes":len(b)}
    # Only document table headers/metadata; no row values exposed.
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        f=z.getinfo("word/document.xml")
        if f.file_size>5_000_000:return {"status":"xml_size_cap"}
        root=ET.fromstring(z.read(f))
    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    def textnode(el):return " ".join(t.text or "" for t in el.findall(".//w:t",ns))
    table=[]
    terms={"pair":r"\bpair\b","site":r"\bsite\b","panel_type":r"panel type|type of panel",
           "panel_height":r"panel.{0,30}height|height.{0,30}panel","panel_width":r"panel.{0,30}width|width.{0,30}panel",
           "row_spacing":r"spacing|distance between|row gap","orientation":r"azimuth|orientation|inclination|tilt",
           "microphone_reference":r"microphone|array position","registration":r"coordinate system|registration|georeferenc",
           "calibration":r"calibration|imprecision|measurement error","geometry":r"geometry|dimension|obstacle"}
    for i,t in enumerate(root.findall(".//w:tbl",ns)):
        rr=t.findall("./w:tr",ns);hh=[textnode(x) for row in rr[:2] for x in row.findall("./w:tc",ns)]
        matches={k:sum(bool(re.search(p,x,re.I)) for x in hh) for k,p in terms.items()}
        table.append({"table_index":i,"rows":len(rr),"first_two_row_cells":len(hh),"header_term_counts":{k:v for k,v in matches.items() if v}})
    para=[textnode(p) for p in root.findall(".//w:body/w:p",ns)]
    return {"status":"structure_only","bytes":len(b),"sha256_download_receipt":sha(b),
       "tables":table,"body_term_paragraph_counts":{k:sum(bool(re.search(p,x,re.I)) for x in para) for k,p in terms.items()}}
def safe(fn):
    try:return fn()
    except Exception as e:return {"status":"blocked","error_type":type(e).__name__}
def main():
    assert fmt("12:01:02.3")=="clock_fractional" and fmt("12:01:02")=="clock_whole_seconds"
    assert time_parse("00:00:01,25")==1.25
    out={"status":"structural_time_geometry_only","movement_outcomes_read":False,"synthetic_checks":"pass","sources":{}}
    dest=OUT/"audit_v42_temporal_geometry.json"
    tasks={"road":road,"solar":solar,"road_R":r_source,"solar_supplement":supplement}
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs={k:pool.submit(safe,fn) for k,fn in tasks.items()}
        for k,f in jobs.items():
            out["sources"][k]=f.result()
            dest.write_text(json.dumps(out,indent=2,allow_nan=False))
    print(dest.read_text())
    return 0 if all(out["sources"].get(k,{}).get("status")!="blocked" for k in ("road","solar","road_R")) else 2
if __name__=="__main__":raise SystemExit(main())
