"""Coverage-only audit: lock geographic and provider holdout masks before fixed-snapshot model fitting."""
import hashlib, pathlib, json, collections
import numpy as np,pandas as pd
from pyproj import Transformer
OUT=pathlib.Path("snapshot_holdout_support");OUT.mkdir(exist_ok=True)
P=pathlib.Path("fixed/all_bat_species_cell_source_year.csv.gz")
Q=pathlib.Path("common_forest/species_cell_source_year_environment.csv.gz")
R=pathlib.Path("traits/physical_trait_crosswalk.csv")
pins={"fixed":"f0124127cd55b7abe4ee0deab935895e150918fc0b0c6e33942ba1591e89ef53","pilot":"5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b","traits":"43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"}
def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
assert sha(P)==pins["fixed"] and sha(Q)==pins["pilot"] and sha(R)==pins["traits"]
a=pd.read_csv(P,dtype={"species":str,"snapshot_species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False)
d=pd.read_csv(Q,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False,low_memory=False)
t=pd.read_csv(R,dtype=str,keep_default_na=False)
assert int(a.records.sum())==219960 and int(d.records.sum())==20784
norm=lambda x:" ".join(str(x).split()).casefold()
t=t[t.AR.ne("")&t.species_key.ne("")].copy();t["name_norm"]=t.source_name.map(norm);t=t[~t.name_norm.duplicated(keep=False)]
a["name_norm"]=a.species.map(norm)
a=a.merge(t[["name_norm","species_key","source_name"]].rename(columns={"species_key":"legacy_species_key"}),on="name_norm",how="left",validate="many_to_one")
keys=a.groupby("name_norm").snapshot_species_key.nunique()
a["trait_match"]=a.legacy_species_key.notna()&~a.name_norm.isin(keys[keys!=1].index)
a["bx"]=a.cell_x//200;a["by"]=a.cell_y//200
roster={"5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"}
f=d[d.forest_profile_support.astype(str).str.lower().eq("true")&d.species_key.isin(roster)&d.dataset_key.ne("")&d.year.str.fullmatch(r"20[0-9]{2}")].copy()
assert len(f.species_key.unique())==14
a["species_seen_in_pilot"]=a.legacy_species_key.isin(roster)
def mask_seen(df,label):
    bl=set(map(tuple,df[["bx","by"]].drop_duplicates().itertuples(index=False,name=None)))
    src=set(df.dataset_key)-{""}
    a[label+"_block_seen"]=[(x,y) in bl for x,y in a[["bx","by"]].itertuples(index=False,name=None)]
    a[label+"_source_seen"]=a.dataset_key.isin(src)
    return {"blocks":len(bl),"providers":len(src)}
prior={"entire_narrow_archive":mask_seen(d,"archive"),"14_species_forest_pilot":mask_seen(f,"pilot")}
I=Transformer.from_crs(6933,4326,always_xy=True)
_,lat_hi=I.transform((a.cell_x.to_numpy()+1)*1000,(a.cell_y.to_numpy()+1)*1000)
_,lat_lo=I.transform(a.cell_x.to_numpy()*1000,a.cell_y.to_numpy()*1000)
a["training_latitude"]=lat_hi<=51.6
a["north_extrapolation"]=lat_lo>51.6
scenarios={"all_fixed":np.ones(len(a),bool),"outside_archive_blocks":~a.archive_block_seen,"outside_pilot_blocks":~a.pilot_block_seen,"outside_archive_providers":~a.archive_source_seen & a.dataset_key.ne(""),"outside_archive_both":~a.archive_block_seen&~a.archive_source_seen&a.dataset_key.ne(""),"outside_pilot_both":~a.pilot_block_seen&~a.pilot_source_seen&a.dataset_key.ne(""),"unseen_pilot_taxa_and_outside_pilot_blocks":~a.species_seen_in_pilot&~a.pilot_block_seen}
def summary(mask):
    v=a[mask&a.trait_match]
    c=v[["source_name","cell_x","cell_y","bx","by"]].drop_duplicates()
    s=[]
    for sp,z in c.groupby("source_name"):
        n=len(z);nb=int(z.groupby(["bx","by"]).size().ge(5).sum())
        s.append({"species":sp,"cells":n,"blocks_ge5":nb,"pass":n>=30 and nb>=4})
    u=v[["dataset_key","year","bx","by","source_name"]].drop_duplicates()
    cnt=u.groupby(["dataset_key","year","bx","by"]).source_name.nunique()
    return {"trait_records":int(v.records.sum()),"species_cells":len(c),"species":int(c.source_name.nunique()),"blocks":len(c[["bx","by"]].drop_duplicates()),"species_geographic_gate":sum(x["pass"] for x in s),"multispecies_provider_year_blocks":int(cnt.ge(2).sum()),"species_support":s}
report={"stage":"prospective geographic/provider disjointness coverage; no outcomes fitted","source_doi":"10.15468/dl.8yrbe7","source_sha256":pins,"previous_archive":prior,"fixed_records":int(a.records.sum()),"scenarios":{},"limits":["Block and provider disjointness from inspected archive is a conservative validation split, not proof of independent biological observations.","Provider metadata does not identify equal effort or absences.","No forest/environment mask yet. Northern GVSM extrapolation separate. Original 20-species model admission remains false.","No outcome-based selection of held-out regions. Fixed snapshot never merged with November observations."]}
for name,mask in scenarios.items():
    report["scenarios"][name]={domain:summary(mask&dm) for domain,dm in [("all_latitudes",np.ones(len(a),bool)),("training_latitude",a.training_latitude),("north_extrapolation",a.north_extrapolation)]}
out=a[["species","snapshot_species_key","cell_x","cell_y","dataset_key","year","license","records","trait_match","species_seen_in_pilot","archive_block_seen","archive_source_seen","pilot_block_seen","pilot_source_seen","training_latitude","north_extrapolation"]].copy()
out.to_csv(OUT/"fixed_source_cell_year_holdout_masks.csv.gz",index=False,compression={"method":"gzip","mtime":0})
report["mask_sha256"]=sha(OUT/"fixed_source_cell_year_holdout_masks.csv.gz")
(OUT/"report.json").write_text(json.dumps(report,indent=2))
print("HOLDOUT_SUPPORT="+json.dumps({**report,"scenarios":{k:{d:{x:y for x,y in v.items() if x!="species_support"} for d,v in z.items()} for k,z in report["scenarios"].items()}}),flush=True)
