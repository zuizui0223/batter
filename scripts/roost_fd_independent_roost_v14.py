"""V14: restricted within-family and forest-habitat diagnostics; public landing S4.
Exploratory, distinct from V13 confirmatory gate. No locations or contact actions.
"""
import io,json,hashlib,re,zipfile
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT
from roost_fd_source_audit_v3 import label,quant
from roost_fd_source_audit_v4 import name,wing
from roost_fd_study_wing_v7 import study_wing
from roost_fd_empirical_null_v5 import numeric,SEED
from roost_fd_independent_roost_v11 import download,contrast
from roost_fd_independent_roost_v12 import get_euro,norm,readcsv
from roost_fd_independent_euro_v13 import taxonomy,roost,STABLE,TYPES,mpd

NREP=1999
URL="https://ars.els-cdn.com/content/image/1-s2.0-S2589004224016067-mmc8.zip"
HASH="5bb3c84f47b108f72558594df91a209914eadb36af2d886f4a737adf04a067b3"
CODES={"CST","EST","FOL-UF","FOL-TB","FOL-LT","TAN","R/C","CREV","CFT"}
def load_wing():
    errors=[]
    for _ in range(3):
        try:
            data,meta=wing()
            raw=data["wingReview_wm_data_final.csv"];w,qc=study_wing(raw,"direct_or_formula")
            t=pd.DataFrame({"species":w["scientificName.iucn"].map(name),"ar":numeric(w.aspectRatio)})
            r=pd.DataFrame({"species":raw["scientificName.iucn"].map(name),"family":raw.familyName.map(label),
                "mass":numeric(raw.mass_g),"ref":raw.refID}).dropna(subset=["species","ref"])
            m=r.groupby(["species","ref"]).mass.median().groupby(level=0).median()
            f=r.groupby("species").family.agg(lambda x:sorted(set(x.dropna())))
            t["mass"]=t.species.map(m);t["wing_family"]=t.species.map({k:v[0] for k,v in f.items() if len(v)==1})
            return t,meta["wingReview_wm_data_final.csv"]["sha256"],errors
        except Exception as e:errors.append(type(e).__name__+": "+str(e)[:120])
    return None,None,errors

def forest_status(d):
    q=d[d.verbatimTraitName=="CriticalFeedingAreasForest"].copy()
    q["species"]=q.verbatimScientificName.map(name);q["value"]=q.verbatimTraitValue.map(label)
    x=q.dropna(subset=["species","value"]).groupby("species").value.agg(lambda s:sorted(set(s)))
    good={k:v[0] for k,v in x.items() if len(v)==1 and v[0] in {"y","n"}}
    return good,{"rows":len(q),"valid_species":len(good),"categories":pd.Series(good).value_counts().to_dict()}

def diagnostic(df,rf,block):
    d=df[df[rf].isin(TYPES)].dropna(subset=["ar","family","forest"]).copy()
    d["u"]=d[rf]==STABLE
    inds=[]
    for _,g in d.groupby(block,sort=True):
        if g.u.nunique()==2:inds.extend(g.index.tolist())
    q=d.loc[inds].reset_index(drop=True)
    n1=int(q.u.sum());n0=len(q)-n1
    out={"forest_complete_roster":len(d),"informative_species":len(q),"underground":n1,"other":n0,
         "informative_families":int(q.family.nunique()),"status":"insufficient_support"}
    if min(n1,n0)<5:return out
    groups=[g.index.to_numpy() for _,g in q.groupby(block,sort=True)]
    out["strata"]=[{"n":len(i),"underground":int(q.u.iloc[i].sum()),"other":int((~q.u.iloc[i]).sum())} for i in groups]
    y=np.log(q.ar.to_numpy(float));z=q.u.to_numpy(bool)
    def stat(p):
        vals=[float(y[i][p[i]].mean()-y[i][~p[i]].mean()) for i in groups]
        return np.array([np.average(vals,weights=[len(i) for i in groups]),mpd(y[p])-mpd(y[~p])])
    obs=stat(z);rng=np.random.default_rng(SEED);sim=[]
    for _ in range(NREP):
        p=z.copy()
        for i in groups:p[i]=rng.permutation(z[i])
        sim.append(stat(p))
    sim=np.asarray(sim);mu=sim.mean(axis=0);sd=sim.std(axis=0,ddof=1)
    out["status"]="exploratory_informative_subset"
    out["statistics"]={}
    for j,key in enumerate(["within_stratum_logmean","pooled_subset_mpd_difference"]):
        lo=(1+int((sim[:,j]<=obs[j]+1e-12).sum()))/(NREP+1)
        hi=(1+int((sim[:,j]>=obs[j]-1e-12).sum()))/(NREP+1)
        out["statistics"][key]={"observed":float(obs[j]),"null_mean":float(mu[j]),
            "SES":float((obs[j]-mu[j])/sd[j]) if sd[j]>1e-12 else None,
            "p":min(1.,2*min(lo,hi)) if sd[j]>1e-12 else None}
    return out

def euro(t):
    f,audit=get_euro()
    d,roost_audit=roost(f["roost"],taxonomy(f["taxon"]))
    forest,fa=forest_status(f["foraging"]);d["forest"]=d.species.map(forest)
    d=d.merge(t[["species","ar"]],on="species",how="left",validate="one_to_one")
    o={"forest_audit":fa,"n_AR":int(d.ar.notna().sum()),"sources":{k:v.get("sha256") for k,v in audit.items()},"seasons":{}}
    for season in ("Maternity","Hibernation"):
        rf="FirstMain"+season+"Roost"
        o["seasons"][season]={"family":diagnostic(d,rf,["family"]),
            "family_forest":diagnostic(d,rf,["family","forest"])}
    return o

def landing():
    b,m=download(URL,25_000_000)
    assert hashlib.sha256(b).hexdigest()==HASH
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        matches=[n for n in z.namelist() if not n.startswith("__MACOSX") and n.endswith("Bat landing roosting data.csv")]
        assert len(matches)==1
        d=readcsv(z.read(matches[0]))
        rnames=[n for n in z.namelist() if not n.startswith("__MACOSX") and n.endswith("Bat_Landing-Roosting_ACE.R")]
        code=z.read(rnames[0]).decode("utf8",errors="replace") if len(rnames)==1 else ""
    # Explicit source columns only; print schema and relevant code fragments when not recognized.
    o={"source":m,"rows":len(d),"columns":list(map(str,d.columns)),
       "categorical_values":{str(c):{str(k):int(v) for k,v in d[c].value_counts().items()} for c in d if d[c].nunique()<=15},
       "code_column_references":[s[:250] for s in code.splitlines() if re.search(r"roost|landing|read.csv",s,re.I)][:35]}
    cand=[c for c in d if norm(c) in {"species","taxon","scientificname","speciesname","spp","binomial","taxa"} and d[c].map(name).notna().sum()>=25]
    if len(cand)!=1:o["status"]="species_schema_review";return None,o
    species=d[cand[0]].map(name)
    # Parse complete categorical lists only if every observed token is a documented guild.
    def codes(s):
        s=label(s)
        if not s:return None
        x=set(re.split(r"[\s,;|+]+",s.upper()))
        return x if x and x<=CODES else None
    candidates=[]
    for c in d:
        if not re.search(r"roost|ecolog|guild",str(c),re.I):continue
        x=d[c].map(codes)
        if x.notna().sum()>=25:candidates.append((c,x))
    if len(candidates)==1:
        col,cs=candidates[0];o["coding"]={"list_column":str(col)}
    else:
        # Explicit binary columns with canonical guild names. Require all 8 major guilds.
        lookup={str(c).upper():c for c in d}
        major=CODES-{"CFT"}
        if not major<=set(lookup):
            o["status"]="roost_schema_review";return None,o
        cols=sorted(major|({"CFT"} if "CFT" in lookup else set()))
        x=d[[lookup[c] for c in cols]].apply(pd.to_numeric,errors="coerce")
        if not x.isin([0,1]).all(axis=None):
            o["status"]="nonbinary_or_missing_guilds";return None,o
        cs=pd.Series([{c for c,v in zip(cols,row) if v==1} for row in x.to_numpy()],index=d.index)
        o["coding"]={"binary_columns":cols}
    r=pd.DataFrame({"species":species,"codes":cs}).dropna(subset=["species","codes"])
    r=r[r.codes.map(bool)].copy()
    if not r.species.is_unique:o["status"]="duplicate_species_review";return None,o
    r["group"]=r.codes.map(lambda x:"rock_cave_only" if x=={"R/C"} else ("rock_cave_mixed" if "R/C" in x else "other_recorded_roost"))
    o["status"]="parsed";o["groups"]={str(k):int(v) for k,v in r.group.value_counts().items()};return r,o

def main():
    result={"status":"exploratory_diagnostics","V13_primary":"not supported","caution":"Single informative family is not independent family replication. Rock/cave classes are not cave obligacy."}
    dest=OUT/"audit_v14.json"
    def save():dest.write_text(json.dumps(result,indent=2,allow_nan=False,default=lambda v:int(v) if isinstance(v,np.integer) else float(v)))
    t,h,errors=load_wing();result["wing_hash"]=h;result["wing_attempt_errors"]=errors;save()
    if t is not None:
        try:result["euro"]=euro(t)
        except Exception as e:result["euro_error"]=type(e).__name__+": "+str(e)[:220]
    save()
    try:
        d,result["landing"]=landing()
        if d is not None and t is not None:
            j=d.merge(t,on="species",how="left",validate="one_to_one").rename(columns={"wing_family":"family"})
            result["landing"]["AR_matches"]=int(j.ar.notna().sum())
            result["landing"]["AR_mass_family_matches"]=int(j[["ar","mass","family"]].notna().all(axis=1).sum())
            result["landing"]["contrast"]=contrast(j)
    except Exception as e:result["landing_error"]=type(e).__name__+": "+str(e)[:220]
    save();print(dest.read_text())
    return 0 if "euro" in result else 2
if __name__=="__main__":raise SystemExit(main())
