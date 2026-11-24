"""V15: acquisition repair for V14, preserving the V14 statistical definitions.
Use the exact published study-level file (verified SHA-256), cache only that file.
Public data only; no data applications or contacts.
"""
import hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT,S
from roost_fd_source_audit_v3 import label
from roost_fd_source_audit_v4 import name
from roost_fd_study_wing_v7 import study_wing
from roost_fd_empirical_null_v5 import numeric
from roost_fd_independent_roost_v11 import download,contrast
from roost_fd_independent_roost_v12 import readcsv
from roost_fd_independent_roost_v14 import euro,landing,URL,HASH
from remotezip import RemoteZip

RECORD=4309199
MEMBER="Supplementary Files/Code and Data/Data/wingReview_wm_data_final.csv"
EXPECTED_SHA="60666f4892dfe536534ad953bc1810b93ded33ce454373ec1e1b410a97ba2c97"
EXPECTED_BYTES=154253
ARCHIVE_SIZE=647936639
ARCHIVE_MD5="3b34b6cf8b466190537b9a13ea57d459"
API_URL="https://zenodo.org/api/records/4309199/files/Supplementary%20Files.zip/content"
FILE_URL="https://zenodo.org/records/4309199/files/Supplementary%20Files.zip?download=1"
CACHE=Path(".roost_public_source_cache")/"wingReview_wm_data_final.csv"

def verify(b):
    if len(b)!=EXPECTED_BYTES or hashlib.sha256(b).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Study-level member did not match V4/V7 pinned bytes")
    d=pd.read_csv(io.BytesIO(b))
    if len(d)!=932 or not {"scientificName.iucn","refID","aspectRatio","wingLoading_Nm2","mass_g","wingArea_cm2","wingSpan_cm"}<=set(d):
        raise ValueError("Pinned wing table schema mismatch")
    return d

def archive_member(url):
    path=Path("wing_archive_v15.tmp")
    try:
        h=hashlib.md5();n=0
        with S.get(url,stream=True,timeout=(20,70),headers={"Accept-Encoding":"identity"}) as r:
            r.raise_for_status()
            if r.headers.get("Content-Length") and int(r.headers["Content-Length"])!=ARCHIVE_SIZE:
                raise ValueError("Full archive response length does not match published file")
            with path.open("wb") as f:
                for chunk in r.iter_content(1024*1024):
                    n+=len(chunk)
                    if n>ARCHIVE_SIZE:raise ValueError("Archive size limit")
                    h.update(chunk);f.write(chunk)
        if n!=ARCHIVE_SIZE or h.hexdigest()!=ARCHIVE_MD5:raise ValueError("Full archive checksum mismatch")
        with zipfile.ZipFile(path) as z:
            return z.read(MEMBER)
    finally:
        path.unlink(missing_ok=True)

def retrieve(report,save):
    report["wing_acquisition"]={"expected_sha256":EXPECTED_SHA,"attempts":[]}
    info=report["wing_acquisition"]
    if CACHE.exists():
        try:
            d=verify(CACHE.read_bytes());info["method"]="validated_cache";save();return d
        except Exception as e:
            info["attempts"].append({"method":"cache","error":type(e).__name__})
            CACHE.unlink(missing_ok=True)
    attempts=[("range_member",API_URL),("full_archive",FILE_URL),("full_archive",API_URL)]
    for mode,url in attempts:
        try:
            info["attempts"].append({"method":mode,"url":url,"status":"started"});save()
            if mode=="range_member":
                with RemoteZip(url,support_suffix_range=False,session=S,timeout=30) as z:b=z.read(MEMBER)
            else:b=archive_member(url)
            d=verify(b)
            CACHE.parent.mkdir(exist_ok=True);CACHE.write_bytes(b)
            info["attempts"][-1]["status"]="verified";info["method"]=mode;save();return d
        except Exception as e:
            info["attempts"][-1].update(status="failed",error=type(e).__name__+": "+str(e)[:150]);save()
    return None

def wing_table(raw):
    w,qc=study_wing(raw,"direct_or_formula")
    t=pd.DataFrame({"species":w["scientificName.iucn"].map(name),"ar":numeric(w.aspectRatio)})
    r=pd.DataFrame({"species":raw["scientificName.iucn"].map(name),"family":raw.familyName.map(label),
       "mass":numeric(raw.mass_g),"ref":raw.refID}).dropna(subset=["species","ref"])
    m=r.groupby(["species","ref"]).mass.median().groupby(level=0).median()
    f=r.groupby("species").family.agg(lambda x:sorted(set(x.dropna())))
    t["mass"]=t.species.map(m);t["wing_family"]=t.species.map({k:v[0] for k,v in f.items() if len(v)==1})
    assert t.species.is_unique
    return t,qc

def load_landing_physics():
    b,m=download(URL,25_000_000)
    assert hashlib.sha256(b).hexdigest()==HASH
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        fn=[n for n in z.namelist() if not n.startswith("__MACOSX") and n.endswith("Bat landing roosting data.csv")]
        assert len(fn)==1
        d=readcsv(z.read(fn[0]))
    d["species"]=d.Taxon.map(name)
    d["roost_regime"]=d.Roosting_Regime.map(label)
    d["landing_regime"]=d.Landing_Regime.map(label)
    assert len(d)==36 and d.species.notna().all() and d.species.is_unique
    assert set(d.roost_regime)=={"stiff-horiz","comp-crev-vert"}
    assert set(d.landing_regime)=={"high","low"}
    return d,m

def physics_description(d):
    # Reproduce a known source-data association only. Not a new mechanistic result.
    c=pd.crosstab(d.roost_regime,d.landing_regime)
    return {"n":len(d),"source_crosstab":{str(k):{str(i):int(v) for i,v in row.items()} for k,row in c.to_dict("index").items()},
        "status":"source_data_check_only"}

def main():
    report={"status":"acquisition_repair","V13_primary":"not_supported","V14":"wing_acquisition_blocked",
       "claim_boundary":"No cave-specific causation or community inference. V14 exploratory definitions unchanged."}
    dest=OUT/"audit_v15.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False,default=lambda v:int(v) if isinstance(v,np.integer) else float(v)))
    d=None
    try:
        d,report["landing"]=landing()
        p,m=load_landing_physics()
        report["landing_physics"]={**physics_description(p),"source":m}
    except Exception as e:report["landing_error"]=type(e).__name__+": "+str(e)[:200]
    save()
    raw=retrieve(report,save)
    if raw is not None:
        t,qc=wing_table(raw)
        report["wing_qc"]=qc
        try:report["euro"]=euro(t)
        except Exception as e:report["euro_error"]=type(e).__name__+": "+str(e)[:200]
        save()
        if d is not None:
            try:
                j=d.merge(t,on="species",how="left",validate="one_to_one").rename(columns={"wing_family":"family"})
                report["landing"]["AR_matches"]=int(j.ar.notna().sum())
                report["landing"]["AR_mass_family_matches"]=int(j[["ar","mass","family"]].notna().all(axis=1).sum())
                report["landing"]["contrast"]=contrast(j)
            except Exception as e:report["landing_contrast_error"]=type(e).__name__+": "+str(e)[:200]
        report["status"]="V14_comparisons_recovered" if "euro" in report and "contrast" in report.get("landing",{}) else "partial"
    else:report["status"]="wing_acquisition_blocked"
    save();print(dest.read_text())
    return 0 if report["status"]=="V14_comparisons_recovered" else 2
if __name__=="__main__":raise SystemExit(main())
