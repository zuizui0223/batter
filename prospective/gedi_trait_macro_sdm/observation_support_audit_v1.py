"""Audit cross-species spatial/source overlap; no environmental response models."""
import pathlib,hashlib,json,itertools,collections
import numpy as np
import pandas as pd
P=pathlib.Path("census"); T=pathlib.Path("traits"); O=pathlib.Path("observation_support"); O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=P/"complete_species_cell_source_year.csv.gz";t=T/"physical_trait_crosswalk.csv"
assert sha(p)=="a3bac38f1961240a235e351207b1497712585fc9d2f8506ab0209d28019354b9"
assert sha(t)=="43bb5284308a9fe732beda51886172cb87268e5d00620eb27956d5808dae809f"
a=pd.read_csv(p,dtype={"species_key":str,"dataset_key":str,"year":str,"license":str},keep_default_na=False)
traits=pd.read_csv(t,dtype={"species_key":str},keep_default_na=False)
traits["AR"]=pd.to_numeric(traits.AR,errors="coerce")
traits=traits.loc[traits.species_key.ne("")&traits.AR.gt(0)].copy()
traits=traits.loc[~traits.species_key.duplicated(keep=False)]
assert len(traits)==28 and set(a.species_key)<=set(traits.species_key)
keys=["species_key","cell_x","cell_y","dataset_key","year","license"]
assert not a.duplicated(keys).any()
assert a.records.gt(0).all() and a.records.mod(1).eq(0).all()
assert int(a.records.sum())==20784
a["bx"]=a.cell_x//200;a["by"]=a.cell_y//200
a=a.merge(traits[["species_key","source_name","AR"]],on="species_key",validate="many_to_one")
allcells=a[["species_key","cell_x","cell_y"]].drop_duplicates()
assert len(allcells)==4854 and a.species_key.nunique()==26
s=a.loc[a.dataset_key.ne("")&a.year.str.fullmatch(r"20[0-9]{2}")].copy()
rpt={"stage":"observation-support diagnosis only","input_records":int(a.records.sum()),"input_species_cells":len(allcells),"input_species":a.species_key.nunique(),"missing_dataset_records":int(a.loc[a.dataset_key.eq(""),"records"].sum()),"missing_or_invalid_year_records":int(a.loc[~a.year.str.fullmatch(r"20[0-9]{2}"),"records"].sum()),"missing_license_records":int(a.loc[a.license.eq(""),"records"].sum()),"usable_source_year_records":int(s.records.sum()),"source_count":s.dataset_key.nunique(),"source_year_count":len(s[["dataset_key","year"]].drop_duplicates()),"limitations":["Same source/year/block is not equal detection probability, joint survey effort, or true coexistence.","No environmental mask, causal inference, background absence or model fit.","Geographic support based on exact narrow-domain queries; no inference about broader Europe."]}
sp=[]
for k,v in a.groupby("species_key"):
    c=v[["cell_x","cell_y","bx","by"]].drop_duplicates()
    b=c.groupby(["bx","by"]).size()
    q=s.loc[s.species_key.eq(k)]
    n=len(c)
    ds=q[["dataset_key","cell_x","cell_y"]].drop_duplicates().groupby("dataset_key").size()
    sy=q[["dataset_key","year","cell_x","cell_y"]].drop_duplicates().groupby(["dataset_key","year"]).size()
    sp.append({"species_key":k,"species":str(v.source_name.iloc[0]),"records":int(v.records.sum()),"cells":n,"blocks_ge5":int((b>=5).sum()),"geographic_gate":bool(n>=30 and (b>=5).sum()>=4),"sources":int(ds.size),"source_years":int(sy.size),"largest_source_cell_share":float(ds.max()/n) if len(ds) else None,"largest_source_year_cell_share":float(sy.max()/n) if len(sy) else None})
sp.sort(key=lambda v:(-v["cells"],v["species"]))
gate={x["species_key"] for x in sp if x["geographic_gate"]};assert len(gate)==14
rpt["species"]=sp
keyblock=["dataset_key","year","bx","by"];keycell=["dataset_key","year","cell_x","cell_y"]
def strata(df):
    out=df.groupby(keyblock).agg(species=("species_key","nunique"),min_AR=("AR","min"),max_AR=("AR","max"))
    counts=df[keyblock+["cell_x","cell_y"]].drop_duplicates().groupby(keyblock).size()
    out=out.join(counts.rename("cells"))
    cellsp=df.groupby(keycell).species_key.nunique()
    return {"total_strata":len(out),"multi_species_strata":int(out.species.ge(2).sum()),"trait_variable_strata":int(out.max_AR.gt(out.min_AR).sum()),"strata_with_ge2_species_and_ge5_cells":int((out.species.ge(2)&out.cells.ge(5)).sum()),"total_source_year_cells":len(cellsp),"multi_species_source_year_cells":int(cellsp.ge(2).sum()),"distinct_blocks_with_multispecies_strata":len(out.loc[out.species.ge(2)].reset_index()[["bx","by"]].drop_duplicates())}
rpt["all_species_strata"]=strata(s)
f=s.loc[s.species_key.isin(gate)];rpt["geographic_gate_species_strata"]=strata(f)
def sets(df,ks):
    return {k:set(map(tuple,v[ks].drop_duplicates().itertuples(index=False,name=None))) for k,v in df.groupby("species_key")}
B=sets(f,keyblock);C=sets(f,keycell)
names={x["species_key"]:x["species"] for x in sp}
pairs=[]
for k,l in itertools.combinations(sorted(gate),2):
    b=B.get(k,set())&B.get(l,set());c=C.get(k,set())&C.get(l,set())
    pairs.append({"species_a":names[k],"species_b":names[l],"shared_source_year_block_strata":len(b),"shared_distinct_blocks":len({(x[2],x[3]) for x in b}),"shared_source_year_cells":len(c),"shared_source_year_groups":len({(x[0],x[1]) for x in b}),"keys":[k,l]})
def components(min_blocks):
    adj={k:set() for k in gate}
    for p in pairs:
        if p["shared_distinct_blocks"]>=min_blocks:
            k,l=p["keys"];adj[k].add(l);adj[l].add(k)
    un=set(adj);cc=[]
    while un:
        todo=[min(un)];got=set()
        while todo:
            k=todo.pop()
            if k in got:continue
            got.add(k);todo.extend(adj[k]-got)
        un-=got;cc.append(sorted(names[k] for k in got))
    return sorted(cc,key=lambda v:(-len(v),v))
rpt["pairs"]=len(pairs);rpt["pairs_ge1_shared_block"]=sum(p["shared_distinct_blocks"]>=1 for p in pairs);rpt["pairs_ge4_shared_blocks"]=sum(p["shared_distinct_blocks"]>=4 for p in pairs);rpt["pairs_shared_cell"]=sum(p["shared_source_year_cells"]>0 for p in pairs)
rpt["components_ge1_block"]=components(1);rpt["components_ge4_blocks"]=components(4)
pd.DataFrame([{k:v for k,v in p.items() if k!="keys"} for p in pairs]).to_csv(O/"pair_overlap.csv",index=False)
rpt["pair_overlap_sha256"]=sha(O/"pair_overlap.csv")
(O/"report.json").write_text(json.dumps(rpt,indent=2)+"\n")
print("OBSERVATION_SUPPORT_REPORT="+json.dumps(rpt),flush=True)
