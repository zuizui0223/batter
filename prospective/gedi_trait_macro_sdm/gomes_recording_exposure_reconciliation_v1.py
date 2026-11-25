"""Reconcile authenticated original Gomes detector counts, calendar semantics and pair support.
No model fit; no raw file names, locations or response rows emitted."""
import collections,csv,datetime as dt,hashlib,json,math,pathlib,re
ROOT=pathlib.Path("source_artifact/verified_public_inputs/gomes_2020")
HERE=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path("gomes_exposure_audit");OUT.mkdir(exist_ok=True)
receipt=json.loads((HERE/"MULTISTUDY_VERTICAL_STRATUM_SOURCE_RECEIPT_V1.json").read_text())
pins={f["name"]:f["sha256"] for f in receipt["sources"]["gomes_2020"]["files"]}
required=["Bats.csv","Bats_Unconsolidated.csv","Headers.txt","Headers_Unconsolidated.txt","Hourly_Models.R","Species_DensityPlots.R","Nunez_etal_2019.csv"]
report={"stage":"source-count and nominal-exposure reconciliation; no ecological fit","source_doi":"10.5281/zenodo.4265167","status":"START","source_hashes":{}}
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("GOMES_EXPOSURE_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def read(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def date(s):
    s=s.strip()
    for fmt in ("%Y-%m-%d","%Y/%m/%d","%m/%d/%Y","%m/%d/%y","%Y%m%d","%Y-%m-%d %H:%M:%S"):
        try:return dt.datetime.strptime(s,fmt).date()
        except ValueError:pass
    raise ValueError("unknown source date format")
def raw_date(s):
    # Species_DensityPlots.R line 7 explicitly reads DD?MM?YYYY by positions.
    # Consolidated Dates use the separate documented calendar convention.
    s=s.strip()
    m=re.fullmatch(r"(\d{2})([/.-])(\d{2})\2(\d{4})",s)
    if not m:raise ValueError("raw DATE does not match author documented DD/MM/YYYY shape")
    d=dt.date(int(m[4]),int(m[3]),int(m[1]))
    if not dt.date(2018,4,10)<=d<=dt.date(2018,4,19):raise ValueError("raw date outside documented study window")
    return d
def integer(s):
    x=float(s);assert math.isfinite(x) and x==int(x);return int(x)
def evening(d,h):return d-dt.timedelta(days=1) if h<12 else d
def keydate(d,h,day,mode):
    if mode=="calendar":return d
    if mode=="evening":return evening(d,h)
    if mode=="day_label":
        if day==d.day:return d
        e=d-dt.timedelta(days=1)
        if day==e.day:return e
        raise ValueError("DAY is not date or preceding date")
    raise ValueError("unknown date convention")
try:
    for k in required:
        h=hashlib.sha256((ROOT/k).read_bytes()).hexdigest()
        assert len(pins[k])==64 and h==pins[k],k
        report["source_hashes"][k]=h
    # Original source-code semantic excerpts, not executed. Include source line numbers.
    pattern=re.compile(r"\b(DAY|Date|DATE|HOUR|Hour|hour|MANUAL_ID|Position_color|Number|Tower|Canopy|Bat|buzz|sunset|filter|subset|aggregate|group_by|summari[sz]e|recode|mutate|ifelse|read.csv|read_csv|complete|as.Date|as.POSIXct)\b")
    report["original_code_semantics"]={}
    for k in ("Hourly_Models.R","Species_DensityPlots.R"):
        lines=(ROOT/k).read_text(encoding="utf-8-sig",errors="replace").splitlines()
        report["original_code_semantics"][k]=[{"line":i+1,"text":line.strip()[:250]} for i,line in enumerate(lines) if pattern.search(line)][:65]
    c=read("Bats.csv");r=read("Bats_Unconsolidated.csv")
    assert len(c)==7854 and len(r)==16123
    cr=[];rr=[]
    for v in c:
        d=date(v["Date"]);h=integer(v["HOUR"]);day=integer(v["DAY"]);n=integer(v["Number"])
        assert 0<=h<=23 and n>=0 and v["Tower"] in ("green","red") and v["Canopy"] in ("above","below")
        cr.append((d,h,day,v["Tower"],v["Canopy"],v["Bat"],n))
    for v in r:
        d=raw_date(v["DATE"]);h=integer(v["HOUR"])
        canopy,tower=v["Position_color"].split(".")
        assert 0<=h<=23 and canopy in ("above","below") and tower in ("green","red")
        rr.append((d,h,tower,canopy,v["MANUAL_ID"],v["buzz"]))
    assert all(dt.date(2018,4,10)<=v[0]<=dt.date(2018,4,19) for v in cr),"consolidated date outside documented study window"
    report["table_counts"]={"raw_rows":len(rr),"consolidated_rows":len(cr),"consolidated_sum":sum(v[-1] for v in cr),"raw_by_position":dict(collections.Counter(v[3] for v in rr)),"consolidated_by_position":{k:sum(v[-1] for v in cr if v[4]==k) for k in ("above","below")},"published_pass_count_check":len(rr)==16123}
    report["date_semantics"]={"consolidated_date_cardinality":len({v[0] for v in cr}),"raw_date_cardinality":len({v[0] for v in rr}),"DAY_equals_calendar_date_rows":sum(v[0].day==v[2] for v in cr),"DAY_equals_evening_date_rows":sum(evening(v[0],v[1]).day==v[2] for v in cr),"consolidated_hour_levels":sorted({v[1] for v in cr}),"raw_hour_levels":sorted({v[1] for v in rr})}
    report["acoustic_code_support"]={"raw_only_codes":sorted({v[4] for v in rr}-{v[5] for v in cr}),"consolidated_only_codes":sorted({v[5] for v in cr}-{v[4] for v in rr}),"raw_codes":len({v[4] for v in rr}),"consolidated_codes":len({v[5] for v in cr}),"buzz_recorded_code_levels":sorted({v[5] for v in rr})}
    # Small, frozen mapping candidates. Exact manual acoustic codes retained.
    mappings={}
    for cm in ("calendar","evening","day_label"):
        try:
            cc={}
            for d,h,day,t,z,b,n in cr:
                k=(keydate(d,h,day,cm),h,t,z,b)
                assert k not in cc,"duplicate consolidated key after date mapping"
                cc[k]=n
        except (ValueError,AssertionError) as e:
            mappings[cm]={"status":"CONSOLIDATED_KEY_STOP","reason":str(e)};continue
        for rm in ("calendar","evening"):
            rc=collections.Counter(((d if rm=="calendar" else evening(d,h)),h,t,z,b) for d,h,t,z,b,_ in rr)
            common=set(cc)&set(rc);outside=set(rc)-set(cc)
            expected_positive={k for k,n in cc.items() if n>0}
            mismatches=[k for k,n in cc.items() if rc.get(k,0)!=n]
            diff=sum(abs(cc[k]-rc.get(k,0)) for k in cc)
            mappings[cm+"__"+rm]={"consolidated_keys":len(cc),"raw_positive_keys":len(rc),"common_positive_keys":len(common),"exact_consolidated_keys":len(cc)-len(mismatches),"mismatched_consolidated_keys":len(mismatches),"positive_consolidated_keys_without_raw":len(expected_positive-set(rc)),"raw_keys_outside_consolidated":len(outside),"raw_counts_outside_consolidated":sum(rc[k] for k in outside),"sum_absolute_count_difference_on_consolidated":diff,"exact_full_reconciliation":not mismatches and not outside}
    report["candidate_date_reconciliations"]=mappings
    # Use native DAY label only for recording-grid support, without deciding calendar interpretation.
    layers=collections.defaultdict(set);roster=collections.defaultdict(set)
    for d,h,day,t,z,b,n in cr:
        layers[(day,h,t)].add(z);roster[(day,h,t,z)].add(b)
    days=sorted({v[2] for v in cr});hours=sorted({v[1] for v in cr});towers=sorted({v[3] for v in cr})
    expected={(day,h,t) for day in days for h in hours for t in towers}
    pairs={k for k,z in layers.items() if z=={"above","below"}}
    singles=set(layers)-pairs;absent=expected-set(layers)
    labels={v[5] for v in cr}
    report["nominal_grid_support"]={"day_labels":len(days),"hour_labels":len(hours),"tower_labels":len(towers),"cartesian_event_keys":len(expected),"present_events":len(layers),"paired_events":len(pairs),"one_sided_events":len(singles),"absent_events":len(absent),"complete_label_roster_on_all_present_detector_events":all(v==labels for v in roster.values()),"per_hour_support":{str(h):{"paired":sum(k[1]==h for k in pairs),"one_sided":sum(k[1]==h for k in singles),"absent":sum(k[1]==h for k in absent)} for h in hours},"nominal_schedule_microphone_hours":432,"verified_actual_detector_hours":None}
    assert len(expected)==len(pairs)+len(singles)+len(absent)
    report["status"]="EXPOSURE_AUDIT_COMPLETE_ACTUAL_UPTIME_UNKNOWN"
    report["limits"]=["Original article documents programmed sunset-to-sunrise recording, not independently verified hourly uptime.","Explicit zero detector counts may not imply a working detector, and unpaired hours remain excluded.","Raw-versus-consolidated reconciliation is an arithmetic check; do not resolve acoustic aliases by matching outcome patterns.","Two recording heights are detector placement, not actual flight altitude; no cross-study model admitted."]
except Exception as e:
    report.update(status="STOP",error_type=type(e).__name__,error=str(e)[:180]);save();raise
save()
