"""Gomes original paired recording-unit support audit. No ecological response fit."""
import collections,csv,hashlib,json,math,pathlib
ROOT=pathlib.Path("source_artifact/verified_public_inputs/gomes_2020")
OUT=pathlib.Path("gomes_stratum_audit");OUT.mkdir(exist_ok=True)
PINS={"Bats.csv":"5e09a20dbc80d9405f522a576d42f85c4b8f0a19d35dda8c50f8a26135b0fa14","Bats_Unconsolidated.csv":"2fc73130d23ae4bbc173ce2c7d92bad50a171eb8887b9af64d1f22d88d26a902","Headers.txt":"0233dd99a7f335b4f28133a526ac72aa860cde5756d4bc1726c151d87b17b73b","Headers_Unconsolidated.txt":"1928e4879b0227e2cca8a9dcd49adce3505820bf483f5a44be06f06a9d456d41","Nunez_etal_2019.csv":"ca75813d91dd6e4dbcbe6b2e18d780ca8c00b3c0638870aa599c3a01eebd278f"}
report={"stage":"source support only; no new ecological fit","doi":"10.5281/zenodo.4265167","source_hashes":{},"status":"START"}
def save():
    (OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print("GOMES_SUPPORT_REPORT="+json.dumps(report,allow_nan=False),flush=True)
def read(name):
    with (ROOT/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
try:
    for name,pin in PINS.items():
        h=hashlib.sha256((ROOT/name).read_bytes()).hexdigest();assert h==pin,name;report["source_hashes"][name]=h
    report["header_documentation"]={k:(ROOT/k).read_text(encoding="utf-8-sig").strip() for k in ("Headers.txt","Headers_Unconsolidated.txt")}
    r=read("Bats.csv");raw=read("Bats_Unconsolidated.csv");traits=read("Nunez_etal_2019.csv")
    assert len(r)==7854 and len(raw)==16123 and len(traits)==27
    fields=["DAY","HOUR","Tower","Canopy","Bat","Number","Date"]
    assert all(k in r[0] for k in fields)
    assert all(all(v[k].strip() for k in fields) for v in r)
    report["consolidated_rows"]=len(r);report["unconsolidated_rows"]=len(raw)
    report["design_levels"]={k:sorted({v[k] for v in r}) for k in ("DAY","HOUR","Tower","Canopy","Bat")}
    # Pair only the two documented detector positions, never an inferred physical altitude.
    layers=set(v["Canopy"] for v in r)
    if len(layers)!=2:raise ValueError("expected two canopy labels")
    counts={};dups=0
    for v in r:
        key=(v["DAY"],v["Date"],v["HOUR"],v["Tower"],v["Bat"],v["Canopy"])
        n=float(v["Number"])
        assert math.isfinite(n) and n>=0 and n==int(n)
        if key in counts:dups+=1
        else:counts[key]=int(n)
    report["duplicate_design_keys"]=dups
    if dups:raise ValueError("ambiguous duplicate detector keys")
    groups=collections.defaultdict(dict);events=collections.defaultdict(set)
    for k,n in counts.items():
        groups[k[:-1]][k[-1]]=n;events[k[:4]].add(k[-1])
    paired={k:v for k,v in groups.items() if set(v)==layers}
    positive={k:v for k,v in paired.items() if sum(v.values())>0}
    by_species={}
    for s in sorted({k[-1] for k in groups}):
        p=[k for k in paired if k[-1]==s];a=[k for k in positive if k[-1]==s]
        by_species[s]={"paired_units":len(p),"positive_paired_units":len(a),"positive_nights":len({k[1] for k in a}),"positive_towers":len({k[3] for k in a})}
    report.update(paired_species_units=len(paired),unpaired_species_units=len(groups)-len(paired),explicit_all_zero_paired_units=len(paired)-len(positive),positive_paired_units=len(positive),candidate_detector_events=len(events),paired_detector_events=sum(v==layers for v in events.values()),candidate_nights=len({k[1] for k in groups}),candidate_towers=len({k[3] for k in groups}),by_species_support=by_species)
    # Trait rows are not assumed to correspond to an acoustic complex.
    assert all(k in traits[0] for k in ("code","Species","AR","WL"))
    code_rows=collections.Counter(v["code"].strip() for v in traits if v["code"].strip() and v["code"].strip().lower() not in ("na","nan"))
    report["trait_code_support"]={"rows":len(traits),"nonempty_code_rows":sum(code_rows.values()),"distinct_nonempty_codes":len(code_rows),"ambiguous_codes":sum(v>1 for v in code_rows.values()),"unique_codes_exactly_matching_acoustic_labels":sorted(k for k,v in code_rows.items() if v==1 and k in by_species)}
    report["raw_design_levels"]={"position_codes":sorted({v["Position_color"] for v in raw}),"manual_id_cardinality":len({v["MANUAL_ID"] for v in raw}),"calendar_date_cardinality":len({v["DATE"] for v in raw})}
    report["status"]="PAIR_SUPPORT_READY_REQUIRES_EFFORT_SEMANTICS"
    report["limits"]=["Explicit table zeros are recording counts, not biological absence or verified detector operation.","DAY/Date semantics, twilight boundary and partial hours require source documentation; paired table rows do not prove matched exposure.","Acoustic complex names require validated mapping; exact trait code matches are only candidates.","One study; no cross-study fit or calibrated altitude response."]
except Exception as e:
    report.update(status="STOP",error_type=type(e).__name__,error=str(e)[:180]);save();raise
save()
