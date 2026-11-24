"""V11 independent roost ecology source audit and species-level landing-study contrast.
Species pools are not roost assemblages. No protected locations exported.
"""
import io,json,hashlib,re,zipfile
from collections import Counter
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import S,OUT,clean
from roost_fd_source_audit_v3 import quant,label
from roost_fd_source_audit_v4 import wing,name
from roost_fd_study_wing_v7 import study_wing
from roost_fd_empirical_null_v5 import numeric,SEED

def download(url,cap=30_000_000):
    with S.get(url,stream=True,timeout=(15,40)) as r:
        r.raise_for_status()
        b=bytearray()
        for chunk in r.iter_content(1024*1024):
            b.extend(chunk)
            if len(b)>cap:raise ValueError("download cap")
    return bytes(b),{"url":url,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}

def schema(d):
    return {"rows":len(d),"columns":list(map(str,d.columns))}
def tables(b,fn):
    if fn.lower().endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(b),sheet_name=None,dtype=str)
    if fn.lower().endswith((".csv",".tsv",".tab",".txt")):
        for e in ("utf-8-sig","cp1252","latin1"):
            try:return {"table":pd.read_csv(io.BytesIO(b),sep=None,engine="python",encoding=e,dtype=str)}
            except (UnicodeError,pd.errors.ParserError):pass
    return {}

def euro():
    url="https://api.figshare.com/v2/articles/21777161/versions/2"
    b,m=download(url,2_000_000);j=json.loads(b)
    report={"doi":j.get("doi"),"title":j.get("title"),"license":j.get("license"),"files":[]}
    for f in j["files"]:
        fn=f["name"]; item={"name":fn,"id":f["id"],"size":f["size"]}
        # Inventory spreadsheets and compressed tables; skip individual-level
        # observations unless explicitly relevant to roost, trait definitions or taxon.
        if f["size"]<=25_000_000 and (re.search(r"roost|trait|taxon|metadata|data|eurobat",fn,re.I)):
            try:
                b,m=download(f["downloadUrl"],25_000_000);item["download"]=m
                if fn.lower().endswith(".zip"):
                    with zipfile.ZipFile(io.BytesIO(b)) as z:
                        item["members"]=[{"name":x.filename,"bytes":x.file_size} for x in z.infolist() if not x.is_dir()]
                        ts={}
                        for x in z.infolist():
                            if x.file_size<5_000_000 and re.search(r"roost|description|taxon|metadata",x.filename,re.I):
                                for n,d in tables(z.read(x),x.filename).items():ts[x.filename+"::"+n]=d
                else:ts=tables(b,fn)
                item["tables"]={}
                for n,d in ts.items():
                    q=schema(d)
                    # Only metadata field names and small categorical vocabularies, not raw localities.
                    if re.search(r"roost|trait.?description|metadata",fn+" "+n,re.I):
                        q["categorical_vocab"]={str(c):sorted(set(d[c].dropna().astype(str)))[:40] for c in d if re.search(r"trait|category|unit|depend|type|value|season|name",str(c),re.I) and 0<d[c].nunique()<=40}
                        q["roost_definition_rows"]=[]
                        for _,v in d.iterrows():
                            if any(re.search(r"roost|hibernacul|maternity",str(v[c]),re.I) for c in d if re.search(r"trait|category|description",str(c),re.I)):
                                if re.search(r"description|metadata",fn+" "+n,re.I):
                                    q["roost_definition_rows"].append({str(c):str(v[c])[:300] for c in d if re.search(r"trait|category|description|definition|unit|type",str(c),re.I)})
                        q["roost_definition_rows"]=q["roost_definition_rows"][:30]
                    item["tables"][n]=q
            except Exception as e:item["error"]=type(e).__name__+": "+str(e)[:200]
        report["files"].append(item)
    return report

def landing_table():
    b,m=download("https://www.ebi.ac.uk/europepmc/webservices/rest/MED/39045098/fullTextXML",10_000_000)
    # Europe PMC fullTextXML generally uses PMCID endpoint; this is attempted separately.
    return b,m
def read_landing():
    b,m=download("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11263957/fullTextXML",10_000_000)
    root=ET.fromstring(b)
    text=lambda e:" ".join("".join(e.itertext()).split())
    choices=[]
    for tw in root.iter("table-wrap"):
        cap=text(tw.find("caption")) if tw.find("caption") is not None else ""
        rr=[]
        for r in tw.iter("tr"):
            cells=[text(td) for td in r if td.tag in ("td","th")]
            if len(cells)<2:continue
            if re.fullmatch(r"(?:[A-Z][a-z-]+) [a-z-]+(?:\s*[a-d])?",cells[0]) and "R/C" in cells[-1]:
                pass
            # Extract exact binomial prefix from table's first cell; footnote letters may be appended.
            hit=re.match(r"^([A-Z][a-z-]+ [a-z-]+?)(?:\s+[a-d]|\s*[\u2020*]+)?$",cells[0])
            if not hit:continue
            species=name(hit.group(1))
            codes=set(re.findall(r"(?<![A-Z])(?:CST|EST|FOL-UF|FOL-TB|FOL-LT|TAN|R/C|CREV|CFT)(?![A-Z])",cells[-1]))
            if species and codes:rr.append((species,",".join(sorted(codes))))
        if 25<=len(rr)<=40:choices.append((cap,rr))
    if len(choices)!=1:raise ValueError("landing table candidate count "+str(len(choices)))
    cap,rr=choices[0]
    d=pd.DataFrame(rr,columns=["species","codes"])
    assert d.species.is_unique
    # R/C means rock and/or cave, not cave-obligate. Mixed classes kept separate.
    d["group"]=d.codes.map(lambda x:"rock_cave_only" if x=="R/C" else ("rock_cave_mixed" if "R/C" in x.split(",") else "other_recorded_roost"))
    return d,{"source":m,"table_caption":cap,"n_extracted":len(d),"codes":dict(Counter(c for x in d.codes for c in x.split(","))),
        "groups":{str(k):int(v) for k,v in d.group.value_counts().items()}}

def mpd(x):
    x=np.asarray(x,float);i,j=np.triu_indices(len(x),1)
    return float(np.mean(np.abs(x[i]-x[j]))) if len(i) else None
def contrast(d):
    # Primary: compare rock/cave-only to other listed roosts, exclude mixed.
    # Sensitivity: any rock/cave vs no rock/cave listed. No absence inference.
    out={}
    for mode in ("exclusive","any"):
        x=d.copy()
        if mode=="exclusive":x=x[x.group!="rock_cave_mixed"].copy()
        x["rock"]=x.group!="other_recorded_roost"
        x=x.dropna(subset=["ar","mass","family"]).copy()
        n=x.rock.value_counts().to_dict()
        a=x.rock.to_numpy();A=np.log(x.ar.to_numpy());M=np.log(x.mass.to_numpy())
        o={"n":len(x),"rock":int(a.sum()),"other":int((~a).sum()),"families":int(x.family.nunique()),
           "AR_rock_mpd":mpd(A[a]),"AR_other_mpd":mpd(A[~a]),"mass_rock_mpd":mpd(M[a]),"mass_other_mpd":mpd(M[~a])}
        if min(a.sum(),(~a).sum())<5:
            o["status"]="too_few_species";out[mode]=o;continue
        # Fix number in each group within family. This is a limited diagnostic
        # on selected sampled species, not a full phylogenetic analysis.
        fam=x.family.to_numpy();blocks=[np.flatnonzero(fam==f) for f in sorted(set(fam))]
        mixed=[i for i in blocks if a[i].any() and (~a[i]).any()]
        o["mixed_family_count"]=len(mixed);o["mixed_family_species"]=sum(len(i) for i in mixed)
        if len(mixed)<2 or o["mixed_family_species"]<10:
            o["status"]="insufficient_within_family_contrast";out[mode]=o;continue
        observed=np.array([mpd(A[a])-mpd(A[~a]),mpd(M[a])-mpd(M[~a])])
        rng=np.random.default_rng(SEED);sim=[]
        for _ in range(1999):
            p=a.copy()
            for i in mixed:p[i]=rng.permutation(a[i])
            sim.append([mpd(A[p])-mpd(A[~p]),mpd(M[p])-mpd(M[~p])])
        sim=np.asarray(sim);sd=sim.std(axis=0,ddof=1)
        o["status"]="exploratory_species_pool_only"
        o["contrasts"]={k:{"observed_difference":float(observed[i]),"null_mean":float(sim[:,i].mean()),
             "SES":float((observed[i]-sim[:,i].mean())/sd[i]) if sd[i]>1e-12 else None} for i,k in enumerate(["AR","mass"])}
        out[mode]=o
    return out
def main():
    report={"status":"source_audit_and_species_pool_pilot","caution":"No non-cave community sampled; no inference of cave-specific community filtering."}
    try:report["EuroBaTrait"]=euro()
    except Exception as e:report["EuroBaTrait"]={"error":type(e).__name__+": "+str(e)[:200]}
    try:
        d,meta=read_landing();report["landing"]=meta
        data,wm=wing();raw=data["wingReview_wm_data_final.csv"];w,qc=study_wing(raw,"direct_or_formula")
        w=pd.DataFrame({"species":w["scientificName.iucn"].map(name),"ar":numeric(w.aspectRatio)})
        r=pd.DataFrame({"species":raw["scientificName.iucn"].map(name),"family":raw.familyName.map(label),
             "mass":numeric(raw.mass_g),"ref":raw.refID}).dropna(subset=["species","ref"])
        mass=r.groupby(["species","ref"]).mass.median().groupby(level=0).median()
        fam=r.groupby("species").family.agg(lambda x:sorted(set(x.dropna())))
        tr=w.assign(mass=w.species.map(mass),family=w.species.map({k:v[0] for k,v in fam.items() if len(v)==1}))
        j=d.merge(tr,on="species",how="left",validate="one_to_one")
        report["landing"]["wing_exact_matches"]=int(j.ar.notna().sum())
        report["landing"]["complete_AR_mass_family"]=int(j[["ar","mass","family"]].notna().all(axis=1).sum())
        report["landing"]["contrast"]=contrast(j)
        report["wing_source_hash"]=wm["wingReview_wm_data_final.csv"]["sha256"]
    except Exception as e:report["landing_error"]=type(e).__name__+": "+str(e)[:300]
    (OUT/"audit_v11.json").write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps(report,indent=2,allow_nan=False))
if __name__=="__main__":main()
