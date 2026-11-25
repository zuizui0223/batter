"""Outcome-blind support audit: measured GEDI cells and GBIF observation methods."""
import collections,hashlib,itertools,json,pathlib
import duckdb,numpy as np,pandas as pd
from pyproj import Transformer
ROOT=pathlib.Path(__file__).resolve().parent
OUT=pathlib.Path("gedi_method_support");OUT.mkdir(exist_ok=True)
def sha(p):
    with pathlib.Path(p).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
root=pathlib.Path("fixed")
assert sha(root/"checkpoint.json")=="0071a731cd65bf68db09d514a9107572e16b738ccfc52d9b4edb908ca56293b9"
parts=json.loads((root/"checkpoint.json").read_text())
assert len(parts)==8 and sum(x["rows"] for x in parts)==219960
for x in parts:assert sha(root/"subsets"/x["file"])==x["sha256"]
grid=pathlib.Path("gedi_grid/cell_gedi_profiles.csv.gz")
assert sha(grid)=="35fd3897562e9b8a6ee909d86b3d36c429098d939ace120016d76f1815a6fa7c"
g=pd.read_csv(grid);K=["cell_x","cell_y"]
assert len(g)==1796 and not g.duplicated(K).any()
g=g[g.gedi_support.astype(str).str.lower().eq("true")][K]
assert len(g)==1587
roster={"5218524","5218507","2432439","5218522","2432359","5218471","5218464","2432389","2432416","2432655","2432614","2432470","9754263","2432564"}
ob=json.loads((ROOT/"OBSERVATION_SUPPORT_RECEIPT_V1.json").read_text())
names={r["species"] for r in ob["species"] if str(r["species_key"]) in roster}
assert len(names)==14
con=duckdb.connect()
p=[str(root/"subsets"/x["file"]) for x in parts]
d=con.execute("SELECT gbifid,species,CAST(specieskey AS VARCHAR) species_key,CAST(datasetkey AS VARCHAR) dataset_key,year(TRY_CAST(eventdate AS DATE)) yr,decimallongitude lon,decimallatitude lat,CAST(samplingprotocol AS VARCHAR) protocol,CAST(establishmentmeans AS VARCHAR) establishment,CAST(occurrenceremarks AS VARCHAR) remarks,CAST(behavior AS VARCHAR) behavior,CAST(license AS VARCHAR) license,CAST(basisofrecord AS VARCHAR) basis FROM read_parquet(?,hive_partitioning=false)",[p]).df()
assert len(d)==d.gbifid.nunique()==219960
d=d[d.species.isin(names)].copy()
assert d.groupby("species").species_key.nunique().max()==1 and d.groupby("species_key").species.nunique().max()==1
assert d.species.nunique()==14
P=Transformer.from_crs(4326,6933,always_xy=True)
x,y=P.transform(d.lon.to_numpy(),d.lat.to_numpy());assert np.isfinite(x).all() and np.isfinite(y).all()
d["cell_x"]=np.floor(x/1000).astype(int);d["cell_y"]=np.floor(y/1000).astype(int)
d=d.merge(g,on=K,how="inner",validate="many_to_one")
d["bx"]=d.cell_x//200;d["by"]=d.cell_y//200
d["year"]=d.yr.astype("Int64").astype(str)
report={"stage":"method-specific support only, no ecological fit","status":"START","snapshot_doi":"10.15468/dl.8yrbe7","grid_sha256":sha(grid),"grid_eligible_cells":1587,"matched_raw_records":len(d),"matched_raw_taxa":int(d.species.nunique()),"category_support":{},"overlap":{}}
def norm(col):return d[col].fillna("").astype(str).str.strip().str.lower()
txt=norm("protocol")+" "+norm("remarks")+" "+norm("behavior")
captive=txt.str.contains(r"\b(captive|captivity|zoo specimen|in captivity|rehabilitation|animal rescue)\b",regex=True)|norm("establishment").str.contains(r"captive|cultivated|managed",regex=True)
roost=txt.str.contains(r"\b(roost|roosting|roost count|hibernaculum|hibernation|winter census|maternity colony|emergence count|cave count|bat box check|bat box inspection)\b",regex=True)
d["acoustic"]=txt.str.contains(r"\b(acoustic|ultrasound|ultrasonic|echolocation|bat detector|sound recording|audio|bat pass|bat passes|passive acoustic)\b",regex=True)
d["capture"]=txt.str.contains(r"\b(mist net|mist-net|harp trap|captured|capture|ringing|banding|hand net)\b",regex=True)
validsrc=d.dataset_key.notna()&d.dataset_key.ne("")&d.year.str.fullmatch(r"20[0-9]{2}")&d.license.isin(["CC_BY_4_0","CC0_1_0","CC_BY_NC_4_0"])
report["explicit_roost_or_captive_excluded"]=int((captive|roost).sum())
report["invalid_source_year_license"]=int((~validsrc).sum())
d=d[validsrc&~(captive|roost)].copy()
report["screened_records"]=len(d)
G=["dataset_key","year","bx","by"];SK=["species",*K];B=["bx","by"]
cats={"all":d,"human_basis":d[d.basis.eq("HUMAN_OBSERVATION")],"machine_basis":d[d.basis.eq("MACHINE_OBSERVATION")],"acoustic_only":d[d.acoustic&~d.capture],"capture_only":d[d.capture&~d.acoustic],"both_flags":d[d.acoustic&d.capture],"unknown_method":d[~d.acoustic&~d.capture]}
assert len(cats["acoustic_only"])+len(cats["capture_only"])+len(cats["both_flags"])+len(cats["unknown_method"])==len(d)
def tuples(q,cols):return set(map(tuple,q[cols].drop_duplicates().itertuples(index=False,name=None)))
# Use the fixed spatial folds of the original European pilot, not new data-dependent folds.
pilot=pathlib.Path("pilot/species_cell_source_year_environment.csv.gz")
assert sha(pilot)=="5bd65cd8c56bac84c033a4972064622c172554a676d198868ef0776c49a2786b"
orig=pd.read_csv(pilot,dtype={"species_key":str,"dataset_key":str,"year":str},keep_default_na=False)
orig=orig[orig.forest_profile_support.astype(str).str.lower().eq("true")&orig.species_key.isin(roster)&orig.dataset_key.ne("")&orig.year.str.fullmatch(r"20[0-9]{2}")]
blocks=set()
for key,q in orig.groupby(G,sort=True):
    by={s:tuples(t,K) for s,t in q.groupby("species_key")}
    if any(len(by[a])*len(by[b])-len(by[a]&by[b])>0 for a,b in itertools.combinations(sorted(by),2)):blocks.add((int(key[2]),int(key[3])))
blocks=sorted(blocks,key=lambda b:hashlib.sha256(f"{b[0]},{b[1]}".encode()).hexdigest());assert len(blocks)==51
fold={b:i%5 for i,b in enumerate(blocks)}
def stats(q):
    sp=[]
    for name,v in q.groupby("species"):
        c=v[K+B].drop_duplicates();nb=int(c.groupby(B).size().ge(5).sum())
        sp.append({"species":name,"records":len(v),"cells":len(c),"blocks_ge5":nb,"geographic_pass":bool(len(c)>=30 and nb>=4)})
    n=0;ng=0;bs=set();sources=set();multi=0;pairtax=set();outside=0;comp_by_fold=[0]*5
    for key,v in q.groupby(G,sort=True):
        by={s:tuples(t,K) for s,t in v.groupby("species")}
        multi+=int(len(by)>=2)
        b=(int(key[2]),int(key[3]))
        for a,c in itertools.combinations(sorted(by),2):
            k=len(by[a])*len(by[c])-len(by[a]&by[c])
            if not k:continue
            m=min(k,128);n+=m;ng+=1;bs.add(b);sources.add(str(key[0]));pairtax.update([a,c])
            if b in fold:comp_by_fold[fold[b]]+=m
            else:outside+=m
    return {"records":len(q),"taxa":int(q.species.nunique()),"species_cells":len(tuples(q,SK)),"cells":len(tuples(q,K)),"sources":int(q.dataset_key.nunique()),"blocks":len(tuples(q,B)),"source_year_block_strata":len(tuples(q,G)),"multispecies_strata":multi,"capped_comparison_support":n,"comparison_groups":ng,"comparison_blocks":len(bs),"comparison_sources":len(sources),"comparison_taxa":len(pairtax),"original_fold_comparisons":comp_by_fold,"comparisons_outside_original_comparison_blocks":outside,"taxa_geographic_pass":sum(v["geographic_pass"] for v in sp),"species":sp}
for name,q in cats.items():report["category_support"][name]=stats(q)
for a,b in [("human_basis","machine_basis"),("acoustic_only","capture_only")]:
    u,v=cats[a],cats[b]
    report["overlap"][a+"_vs_"+b]={label:len(tuples(u,cols)&tuples(v,cols)) for label,cols in [("species",["species"]),("cells",K),("blocks",B),("providers",["dataset_key"]),("species_cells",SK),("species_source_year_block",["species",*G]),("species_cell_source_year",["species",*K,"dataset_key","year"])]}
report.update(status="COMPLETE_SUPPORT_ONLY",limitations=["BasisOfRecord is not measurement protocol; explicit keywords are screening evidence only.","Unflagged method unknown; no imputed non-acoustic records or observed absences.","These are overlapping fixed-snapshot records, not independent biological replication or a detection calibration.","Capped counts are support diagnostics; no fitted model, effect, or primary SDM admission."])
(OUT/"report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
print("GEDI_METHOD_SUPPORT="+json.dumps({**report,"category_support":{k:{a:b for a,b in v.items() if a!="species"} for k,v in report["category_support"].items()}},allow_nan=False),flush=True)
