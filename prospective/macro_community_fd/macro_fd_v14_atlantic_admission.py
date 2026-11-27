"""V14 source admission for original regional bat surveys; aggregate-only."""
import collections as C, hashlib,io,json,re,subprocess,sys
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer
from macro_fd_v4_global_ranges import read_ranges,wing
from macro_fd_v7_multidomain import mapping
from combine_v6b_coverage import acquire,norm

PIN="136aa78f49e14a4160b40b4456f21b7677c625c4"
ROOT=Path("atlantic/ATLANTIC_BATS/DATASET/2018_02_d21")
FILES={"ATLANTIC_BATS_Capture.csv":(4920410,"ef1af2d4f2a3ead54bdef403c05eca6bd5fdb6b8"),"ATLANTIC_BATS_Study_site.csv":(47940,"b16f12a538ba92b8455905ab16a7a72f3f19a528"),"ATLANTIC_BATS_Reference.csv":(62158,"cee57b2287a1aabe8241f0c671de5ea76bd88524"),"ATLANTIC_BATS_2020_comp.xlsx":(167893,"2bdfc0a8eccd1906471881ec852d380e0ad28f34")}
OUT=Path("macro_fd_v14_result.json")
def save(o):
    OUT.write_text(json.dumps(o,indent=2,allow_nan=False)+"\n")
    print("GLOBAL_V14_REPORT="+json.dumps(o,allow_nan=False),flush=True)
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def read(b):
    for enc in ("utf-8-sig","cp1252"):
        try:return pd.read_csv(io.BytesIO(b),encoding=enc,dtype=str,keep_default_na=False)
        except UnicodeDecodeError:pass
    raise ValueError("unknown encoding")
def key(x):return re.sub("[^a-z0-9]","",str(x).casefold())
def pick(d,opts):
    a=[x for x in d if key(x) in opts];return a[0] if len(a)==1 else None
def main():
    o={"stage":"independent Atlantic Forest regional survey admission","status":"START","source_doi":"10.1002/ecy.2007","source_commit":PIN,"limits":["historical capture records, not 2019–2023 observations","Precise is a source category, not calibrated coordinate error","capture sample is not occupancy or vertical activity","current range maps not contemporaneous","no GEDI or ecological model fit"]}
    try:
        assert subprocess.check_output(["git","-C","atlantic","rev-parse","HEAD"]).decode().strip()==PIN
        raw={};o["sources"]={}
        for fn,(n,sha) in FILES.items():
            b=(ROOT/fn).read_bytes();assert len(b)==n and blob(b)==sha
            raw[fn]=b;o["sources"][fn]={"bytes":n,"git_blob":sha,"sha256":hashlib.sha256(b).hexdigest()}
        s,r,d=[read(raw[f"ATLANTIC_BATS_{x}.csv"]) for x in ("Study_site","Reference","Capture")]
        o["tables"]={k:{"rows":len(v),"columns":v.columns.tolist()} for k,v in [("site",s),("reference",r),("capture",d)]}
        assert set(["ID","Latitude","Longitude","Precision"])<=set(s) and set(["ID","References"])<=set(r)
        assert len(s)==205 and s.ID.is_unique and r.ID.is_unique
        o["source_sites"]={"precision":dict(C.Counter(s.Precision)),"reference_rows":len(r),"site_ref_ID_overlap":len(set(s.ID)&set(r.ID)),"distinct_nonempty_reference_texts":int(r.References.str.strip().replace("",np.nan).nunique())}
        x=pd.ExcelFile(io.BytesIO(raw["ATLANTIC_BATS_2020_comp.xlsx"]),engine="openpyxl")
        o["updated_2020_census"]={}
        for name in x.sheet_names:
            a=x.parse(name,header=None,dtype=str,keep_default_na=False)
            o["updated_2020_census"][name]={"shape":list(a.shape),"first_row_nonempty_cells":int((a.iloc[0].astype(str).str.strip()!="").sum()) if len(a) else 0}
        # Only documented exact names, no fuzzy taxonomy or guessing labels.
        sid=pick(d,{"id","siteid","studyid","studysiteid","idsite","idstudy","idlocation"})
        if sid is None:
            hits=[k for k in d if len(set(d[k])- {""})>0 and set(d[k])-{""}<=set(s.ID)]
            sid=hits[0] if len(hits)==1 else None
        tax=pick(d,{"species","scientificname","binomial","speciesname","taxon","taxonname"})
        gen=pick(d,{"genus","gen"})
        o["selected_fields"]={"site":sid,"species":tax,"genus":gen}
        if sid is None or tax is None:raise ValueError("capture schema: site/species key not unambiguous")
        vals=d[tax].str.strip()
        if gen:
            ep=vals.str.fullmatch(r"[a-z][a-z-]+",case=True)
            g=d[gen].str.strip()
            vals=vals.where(~ep,g+" "+vals)
        # Exact binomial only. Case-normalized, no subspecies, cf./aff., or aliases.
        vals=vals.str.replace("_"," ",regex=False).str.replace(r"\s+"," ",regex=True).str.strip()
        good=vals.str.fullmatch(r"[A-Z][a-zA-Z-]+ [a-z][a-z-]+",case=True)
        # Allow source lower-case binomials when no ambiguous qualifier.
        good|=vals.str.fullmatch(r"[a-z]+ [a-z][a-z-]+",case=True)
        good&=~vals.str.casefold().str.split().str[-1].isin(["sp","spp","cf","aff","unknown","indet","unidentified"])
        site_ok=d[sid].isin(s.ID)
        # Source capture table is individual capture data; no abundance inference.
        o["capture_census"]={"capture_rows":len(d),"matched_site_rows":int(site_ok.sum()),"exact_binomial_rows":int(good.sum()),"eligible_rows":int((site_ok&good).sum()),"distinct_exact_labels":int(vals[good].map(norm).nunique()),"unique_matched_sites":int(d.loc[site_ok,sid].nunique()),"missing_site_rows":int((~site_ok).sum()),"unresolved_taxon_rows":int((~good).sum())}
        if len(d)<10000 or int(site_ok.sum())<.95*len(d):raise ValueError("capture grain/site coverage not admitted")
        c=pd.DataFrame({"site":d.loc[site_ok&good,sid],"name":vals[site_ok&good].map(norm)}).drop_duplicates()
        # No source grain beyond distinct capture labels.
        o["capture_census"]["site_species_incidence"]=len(c)
        o["status"]="SOURCE_CENSUS";save(o)
        names,X,shape,crs,T=read_ranges(o);assert len(names)==1141
        w=wing(o);a,b,_=acquire(o);f=mapping(a,b,names,w,o);common=set(f.index)&set(w.index)
        wi=set(names)&set(w.index);assert len(wi)==264
        sets={"broad":set(f.index),"nosplit":set(f.index[f.no_transfer]),"wing":wi,"common":common}
        pos={n:i for i,n in enumerate(names)}
        lon=pd.to_numeric(s.Longitude,errors="coerce");lat=pd.to_numeric(s.Latitude,errors="coerce")
        ok=s.Precision.str.strip().eq("Precise")&np.isfinite(lat)&np.isfinite(lon)&lat.between(-60,15)&lon.between(-90,-30)
        tf=Transformer.from_crs(4326,crs,always_xy=True);xy=np.array(tf.transform(lon[ok].to_numpy(),lat[ok].to_numpy())).T
        ix,iy=(~T)*(xy[:,0],xy[:,1]);rows=np.floor(iy).astype(int);cols=np.floor(ix).astype(int)
        idx=s[ok].ID.tolist()
        valid=(rows>=0)&(rows<shape[0])&(cols>=0)&(cols<shape[1])
        loc={k:(int(y*shape[1]+x),int(np.floor(px/200000)),int(np.floor(py/200000))) for k,y,x,(px,py),v in zip(idx,rows,cols,xy,valid) if v}
        o["coordinate_admission"]={"precise_finite_regional":int(ok.sum()),"inside_native_grid":len(loc)}
        obs={k:set(v.name) for k,v in c.groupby("site")}
        refs=r.set_index("ID").References.to_dict()
        o["cohorts"]={}
        for tag,sp in sets.items():
            th=.8 if tag in ("broad","nosplit") else .5
            eligible=[];counts=[]
            for site,ss in obs.items():
                match=ss&sp
                counts.append(len(match)/len(ss))
                if site not in loc or len(match)<5 or len(match)/len(ss)<th:continue
                ci,bx,by=loc[site]
                present={n for n in sp if X[pos[n],ci]}
                eligible.append((site,len(match),len(present),len(match&present),bx,by))
            rr=[x for x in eligible if refs.get(x[0],"").strip()]
            rc=len({refs[x[0]].strip() for x in rr});bc=len({(x[4],x[5]) for x in eligible})
            co={"matched_species":len(set(c.name)&sp),"median_all_site_trait_coverage":float(np.median(counts)) if counts else None,"precise_eligible_sites":len(eligible),"distinct_nonempty_references":rc,"blocks_200km":bc,"matched_capture_incidence":sum(x[1] for x in eligible),"in_current_range_cell_incidence":sum(x[3] for x in eligible),"median_observed_matched_richness":float(np.median([x[1] for x in eligible])) if eligible else None,"median_potential_matched_richness":float(np.median([x[2] for x in eligible])) if eligible else None}
            co["range_overlap_fraction"]=co["in_current_range_cell_incidence"]/co["matched_capture_incidence"] if co["matched_capture_incidence"] else None
            co["admitted"]=len(eligible)>=60 and rc>=10 and bc>=10
            o["cohorts"][tag]=co
        o["status"]="REGIONAL_SUPPORT_ADMITTED" if o["cohorts"]["broad"]["admitted"] else "REGIONAL_SUPPORT_STOP"
        save(o)
    except Exception as e:
        o["last_status"]=o["status"];o["status"]="STOP";o["error_type"]=type(e).__name__;o["validation"]=str(e)[:300];save(o)
if __name__=="__main__":main()
