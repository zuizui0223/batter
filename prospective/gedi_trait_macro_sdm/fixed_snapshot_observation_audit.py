"""Outcome-blind observation/source quality audit, fixed 2026-08-01 GBIF snapshot.
No precise record locations or recorder identities published in audit summaries.
Unknown metadata never construed as absence of roosting or equal effort.
"""
import collections,hashlib,json,pathlib,math,sys
import duckdb,pandas as pd,numpy as np
from pyproj import Transformer
OUT=pathlib.Path("snapshot_observation_audit");OUT.mkdir(exist_ok=True)
root=pathlib.Path("fixed")
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
assert sha(root/"checkpoint.json")=="0071a731cd65bf68db09d514a9107572e16b738ccfc52d9b4edb908ca56293b9"
parts=json.loads((root/"checkpoint.json").read_text())
assert len(parts)==8 and sum(x["rows"] for x in parts)==219960
for x in parts:assert sha(root/"subsets"/x["file"])==x["sha256"]
con=duckdb.connect()
files=[str(root/"subsets"/x["file"]) for x in parts]
raw=con.execute("SELECT gbifid,species,CAST(specieskey AS VARCHAR) species_key,CAST(datasetkey AS VARCHAR) dataset_key,year(TRY_CAST(eventdate AS DATE)) yr,TRY_CAST(eventdate AS DATE) date,decimallongitude lon,decimallatitude lat,CAST(eventid AS VARCHAR) event_id,CAST(samplingprotocol AS VARCHAR) protocol,CAST(establishmentmeans AS VARCHAR) establishment,CAST(occurrenceremarks AS VARCHAR) remarks,CAST(habitat AS VARCHAR) habitat,CAST(locality AS VARCHAR) locality,CAST(behavior AS VARCHAR) behavior,CAST(license AS VARCHAR) license,CAST(basisofrecord AS VARCHAR) basis,CAST(identificationqualifier AS VARCHAR) id_qualifier,CAST(taxonomicstatus AS VARCHAR) taxonomic_status FROM read_parquet(?,hive_partitioning=false)",[files]).df()
assert len(raw)==raw.gbifid.nunique()==219960
P=Transformer.from_crs(4326,6933,always_xy=True);I=Transformer.from_crs(6933,4326,always_xy=True)
x,y=P.transform(raw.lon.to_numpy(),raw.lat.to_numpy());assert np.isfinite(x).all() and np.isfinite(y).all()
raw["cx"]=np.floor(x/1000).astype(int);raw["cy"]=np.floor(y/1000).astype(int)
raw["bx"]=raw.cx//200;raw["by"]=raw.cy//200
def normalized(col):
    return raw[col].fillna("").astype(str).str.strip().str.lower()
def filled(col):
    return ~normalized(col).isin(["","na","n/a","null","unknown","not recorded","not available","none"])
cols=["event_id","protocol","establishment","remarks","habitat","locality","behavior","id_qualifier","taxonomic_status"]
report={"stage":"observation metadata audit, no ecological model","snapshot_doi":"10.15468/dl.8yrbe7","raw_records":len(raw),"unique_keys":int(raw.gbifid.nunique()),"datasets":int(raw.dataset_key.nunique()),"species":int(raw.species.nunique()),"metadata_nonempty":{k:int(filled(k).sum()) for k in cols},"by_basis":{str(k):int(v) for k,v in raw.basis.value_counts(dropna=False).items()},"by_taxonomic_status":{str(k):int(v) for k,v in raw.taxonomic_status.value_counts(dropna=False).items()},"by_establishment":{str(k):int(v) for k,v in raw.establishment.value_counts(dropna=False).items()},"limits":["Keyword flags are screening candidates, not verified observation classes. Missing text is unknown, not evidence of flight or wild status.","EventID scoped by dataset; shared IDs/locations do not establish standardized effort or complete species checklists.","No inference of absence from unreported taxa. License review required before redistribution of derived records."]}
# Use explicit strings rather than treating habitat='cave' as proof of a roost observation.
txt=normalized("protocol")+" "+normalized("remarks")+" "+normalized("behavior")
raw["flag_explicit_captive"]=txt.str.contains(r"\b(captive|captivity|zoo specimen|in captivity|rehabilitation|animal rescue)\b",regex=True)|normalized("establishment").str.contains(r"captive|cultivated|managed",regex=True)
raw["flag_roost_context"]=txt.str.contains(r"\b(roost|roosting|roost count|hibernaculum|hibernation|winter census|maternity colony|emergence count|cave count|bat box check|bat box inspection)\b",regex=True)
raw["flag_acoustic_context"]=txt.str.contains(r"\b(acoustic|ultrasound|ultrasonic|echolocation|bat detector|sound recording|audio|bat pass|bat passes|passive acoustic)\b",regex=True)
raw["flag_capture_context"]=txt.str.contains(r"\b(mist net|mist-net|harp trap|captured|capture|ringing|banding|hand net)\b",regex=True)
raw["event_present"]=filled("event_id")
raw["protocol_present"]=filled("protocol")
flags=["flag_explicit_captive","flag_roost_context","flag_acoustic_context","flag_capture_context","event_present","protocol_present"]
report["flags"]={k:int(raw[k].sum()) for k in flags}
report["context_overlap"]={f"{a}_{b}":int((raw[a]&raw[b]).sum()) for i,a in enumerate(flags[:4]) for b in flags[:4][i+1:]}
ev=raw[raw.event_present]
e=ev.groupby(["dataset_key","event_id"],dropna=False).agg(records=("gbifid","size"),species=("species_key","nunique"),date_count=("date","nunique"),cell_x_count=("cx","nunique"),cell_y_count=("cy","nunique"))
report["event_structure"]={"unique_dataset_event_ids":len(e),"multi_species_events":int((e.species>=2).sum()),"single_day_single_cell_events":int(((e.date_count==1)&(e.cell_x_count==1)&(e.cell_y_count==1)).sum()),"multi_species_single_day_single_cell_events":int(((e.species>=2)&(e.date_count==1)&(e.cell_x_count==1)&(e.cell_y_count==1)).sum()),"multi_date_events":int((e.date_count>1).sum()),"multi_cell_events":int(((e.cell_x_count>1)|(e.cell_y_count>1)).sum())}
# Dataset-level counts, protocol completeness and taxon breadth. No raw observation text or individual identifiers.
ds=[]
for key,z in raw.groupby("dataset_key",dropna=False):
    counts={k:int(z[k].sum()) for k in flags}
    ds.append({"dataset_key":str(key),"records":len(z),"species":int(z.species_key.nunique()),"cells":len(z[["cx","cy"]].drop_duplicates()),"source_years":int(z.yr.nunique()),**counts})
ds.sort(key=lambda a:-a["records"])
pd.DataFrame(ds).to_csv(OUT/"dataset_observation_metadata_audit.csv",index=False)
report["largest_sources"]=ds[:10]
report["n_sources_event_id_for_all_records"]=sum(a["event_present"]==a["records"] for a in ds)
report["n_sources_protocol_for_all_records"]=sum(a["protocol_present"]==a["records"] for a in ds)
# Coverage sensitivity only, exact same frozen geometry criterion.
p=pathlib.Path("traits/physical_trait_crosswalk.csv")
assert sha(p)=="43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"
tr=pd.read_csv(p,dtype=str,keep_default_na=False)
tr=tr[tr.AR.ne("")&tr.species_key.ne("")];norm=lambda v:" ".join(str(v).split()).casefold()
tr["norm"]=tr.source_name.map(norm);tr=tr[~tr.norm.duplicated(keep=False)]
raw["norm"]=raw.species.map(norm)
names=set(tr.norm)
keys=raw.groupby("norm").species_key.nunique()
names=names-set(keys[keys!=1].index)
_,lat_hi=I.transform((raw.cx.to_numpy()+1)*1000,(raw.cy.to_numpy()+1)*1000)
raw["training_latitude"]=lat_hi<=51.6
scenarios={"all":np.ones(len(raw),bool),"exclude_explicit_captive":~raw.flag_explicit_captive,"exclude_captive_and_roost_flag":~(raw.flag_explicit_captive|raw.flag_roost_context),"explicit_acoustic_no_captive_roost":raw.flag_acoustic_context&~(raw.flag_explicit_captive|raw.flag_roost_context)}
result={}
for name,mask in scenarios.items():
    result[name]={}
    for domain,dom in [("all_latitudes",np.ones(len(raw),bool)),("training_latitude",raw.training_latitude)]:
        v=raw[mask&dom&raw.norm.isin(names)]
        c=v[["species","cx","cy","bx","by"]].drop_duplicates()
        sp=[]
        for s,z in c.groupby("species"):
            n=len(z);nb=int(z.groupby(["bx","by"]).size().ge(5).sum())
            sp.append({"species":s,"cells":n,"blocks_ge5":nb,"pass":bool(n>=30 and nb>=4)})
        result[name][domain]={"records":len(v),"species_cells":len(c),"species_with_geographic_pass":sum(z["pass"] for z in sp),"species":sp}
report["geographic_support_sensitivity"]=result
# Preserve derived flags at source/cell/year/species level for matching with environment; no raw free text.
flags_group=raw.groupby(["species","species_key","cx","cy","dataset_key","yr","license"],dropna=False).agg(records=("gbifid","size"),**{k:(k,"sum") for k in flags}).reset_index()
flags_group=flags_group.rename(columns={"cx":"cell_x","cy":"cell_y","yr":"year","species_key":"snapshot_species_key"})
flags_group.to_csv(OUT/"source_cell_year_observation_flags.csv.gz",index=False,compression={"method":"gzip","mtime":0})
report["outputs"]={p.name:sha(p) for p in OUT.iterdir() if p.is_file()}
report["status"]="OBSERVATION_AUDIT_COMPLETE_NOT_EFFORT_CALIBRATED"
(OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
print("OBSERVATION_AUDIT="+json.dumps({**report,"geographic_support_sensitivity":{k:{d:{x:y for x,y in v.items() if x!="species"} for d,v in z.items()} for k,z in result.items()}},allow_nan=False),flush=True)
