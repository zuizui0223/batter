"""V13: season-specific roost species-pool comparisons, not community assembly tests.
Public sources only. No contact, no protected localities, no site-level data.
"""
import io,json,re,hashlib,zipfile
import numpy as np
import pandas as pd
from roost_fd_source_audit_v2 import OUT,S
from roost_fd_source_audit_v3 import label,quant
from roost_fd_source_audit_v4 import name,wing
from roost_fd_study_wing_v7 import study_wing
from roost_fd_empirical_null_v5 import numeric,SEED
from roost_fd_independent_roost_v12 import get_euro,norm
from roost_fd_independent_roost_v11 import download

STABLE="thermally_stable_underground_roosts"
UNSTABLE="thermally_unstable_underground_roosts"
TYPES={STABLE,UNSTABLE,"human-made_roost","tree_roost","rock_crevices"}
NREP=1999
def countdict(s):return {str(k):int(v) for k,v in s.value_counts(dropna=False).items()}
def taxonomy(t):
    a=pd.DataFrame({"species":t.verbatimScientificName.map(name),"family":t.Family.map(label)}).dropna()
    assert a.species.is_unique and len(a)==len(t)
    a["genus"]=a.species.str.split().str[0]
    return a
def roost(r,t):
    a=pd.DataFrame({"species":r.verbatimScientificName.map(name),"trait":r.verbatimTraitName,"value":r.verbatimTraitValue.map(label)})
    a=a[a.species.isin(t.species)&a.value.notna()].copy()
    out=t.copy();audit={}
    for season in ("Maternity","Hibernation"):
        for rank in ("First","Second","Third"):
            tr=rank+"Main"+season+"Roost";z=a[a.trait==tr]
            g=z.groupby("species").value.agg(lambda s:sorted(set(s)))
            good={k:v[0] for k,v in g.items() if len(v)==1 and v[0] in TYPES}
            out[tr]=out.species.map(good)
            audit[tr]={"rows":len(z),"species":len(g),"valid_unique":len(good),"conflicting_or_invalid":len(g)-len(good),"categories":countdict(out[tr].dropna())}
    a=out.FirstMainMaternityRoost;b=out.FirstMainHibernationRoost
    both=a.notna()&b.notna()
    audit["season_cross_tab"]={str(k):countdict(g.FirstMainHibernationRoost) for k,g in out.loc[both].groupby("FirstMainMaternityRoost")}
    audit["both_known"]=int(both.sum());audit["same_first_roost"]=int((both&(a==b)).sum())
    return out,audit
def trait_metadata(d,category):
    q=d[d.Category.map(label)==category]
    return q[["Name","Unit","Type","Definition"]].fillna("").to_dict("records")
def euro_morph(d,desc):
    q=desc[desc.Category.map(label)=="morphology"].copy()
    specs={}
    for target,aliases,units in [
        ("mass",{"bodymass","bodyweight","mass","adultbodymass","meanbodymass"},{"g","gram","grams"}),
        ("euro_ar",{"aspectratio","wingaspectratio","wingar"},{"","1","dimensionless","unitless","ratio","none","na","n/a"})]:
        cand=q[q.Name.map(norm).isin(aliases)]
        if len(cand)!=1:specs[target]={"status":"no_unique_documented_trait","candidates":cand.Name.tolist()};continue
        row=cand.iloc[0];unit=label(row.Unit) or ""
        if unit not in units:specs[target]={"status":"unit_review_required","trait":row.Name,"unit":unit};continue
        z=d[d.verbatimTraitName==row.Name].copy()
        vals=pd.to_numeric(z.verbatimTraitValue,errors="coerce")
        z["species"]=z.verbatimScientificName.map(name)
        z["value"]=vals.where(np.isfinite(vals)&(vals>0))
        z["ref"]=z.ShortReference.map(label)
        typ=z.verbatimTraitValueType.map(label)
        actual_unit=z.verbatimTraitUnit.map(label).fillna("")
        # Do not pool minima/maxima, unlabelled individual measures or wrong units.
        allowed={"mean","median","arithmetic mean","arithmetic_mean"}
        good=z[typ.isin(allowed)&actual_unit.isin(units)].dropna(subset=["species","value","ref"])
        pool=good.groupby(["species","ref"]).value.median().groupby(level=0).median()
        specs[target]={"status":"ok" if len(pool) else "no_eligible_values","trait":row.Name,
          "unit":unit,"definition":str(row.Definition),"rows":len(z),"value_types":countdict(typ),
          "units":countdict(actual_unit),"eligible_rows":len(good),"species":len(pool),
          "values":quant(pool)}
        if len(pool):specs[target]["pool"]=pool
    return specs
def mpd(a):
    a=np.asarray(a,float);i,j=np.triu_indices(len(a),1)
    return float(np.mean(abs(a[i]-a[j])))
def stat(z,a):
    return np.array([mpd(z[a])-mpd(z[~a]),float(z[a].mean()-z[~a].mean())])
def test():
    assert np.isclose(mpd([0,1,3]),2)
    assert np.allclose(stat(np.array([0,1,2,5]),np.array([True,True,False,False])),[-2,-3])
def compare(df,roostfield,field,exposure):
    types={STABLE} if exposure=="stable" else {STABLE,UNSTABLE}
    a=df[df[roostfield].isin(TYPES)].dropna(subset=[field,"family","genus"]).copy()
    assert a.species.is_unique
    y=np.log(a[field].to_numpy(float));z=a[roostfield].isin(types).to_numpy()
    n1=int(z.sum());n0=len(a)-n1
    out={"n":len(a),"underground":n1,"other_main":n0,"families":int(a.family.nunique()),"status":"insufficient_group_size",
         "complete_types":countdict(a[roostfield])}
    if min(n1,n0)<5:return out
    out["status"]="species_pool_only"
    out["group_mpd_log"]={"underground":mpd(y[z]),"other_main":mpd(y[~z])}
    out["group_geometric_mean"]={"underground":float(np.exp(y[z].mean())),"other_main":float(np.exp(y[~z].mean()))}
    observed=stat(y,z);out["observed"]={"mpd_difference":float(observed[0]),"log_mean_difference":float(observed[1])}
    out["permutations"]={}
    for block in ("unrestricted","family","genus"):
        if block=="unrestricted":indices=[np.arange(len(a))]
        else:
            b=a[block].to_numpy()
            indices=[np.flatnonzero(b==k) for k in sorted(set(b))]
        mixed=[i for i in indices if z[i].any() and (~z[i]).any()]
        mixed_n=sum(len(i) for i in mixed)
        row={"mixed_blocks":len(mixed),"mixed_species":mixed_n,"status":"insufficient_mixed_blocks"}
        if block!="unrestricted" and (len(mixed)<2 or mixed_n<10):
            out["permutations"][block]=row;continue
        rng=np.random.default_rng(SEED);sim=[]
        for _ in range(NREP):
            zz=z.copy()
            for i in mixed:zz[i]=rng.permutation(z[i])
            assert zz.sum()==z.sum()
            sim.append(stat(y,zz))
        sim=np.asarray(sim);mu=sim.mean(axis=0);sd=sim.std(axis=0,ddof=1)
        row["status"]="exploratory";row["statistics"]={}
        for i,k in enumerate(("mpd_difference","log_mean_difference")):
            lower=(1+int((sim[:,i]<=observed[i]+1e-12).sum()))/(NREP+1)
            upper=(1+int((sim[:,i]>=observed[i]-1e-12).sum()))/(NREP+1)
            row["statistics"][k]={"null_mean":float(mu[i]),"null_sd":float(sd[i]),
              "null_95":[float(v) for v in np.quantile(sim[:,i],[.025,.975])],
              "SES":float((observed[i]-mu[i])/sd[i]) if sd[i]>1e-12 else None,
              "p_two_sided":min(1.,2*min(lower,upper)) if sd[i]>1e-12 else None}
        out["permutations"][block]=row
    return out
def run_contrasts(df,fields):
    result={}
    for season in ("Maternity","Hibernation"):
        rf="FirstMain"+season+"Roost"
        result[season]={}
        for exposure in ("stable","any_underground"):
            result[season][exposure]={f:compare(df,rf,f,exposure) for f in fields}
    return result
def landing_supplement():
    # Public, article-linked supplemental data archive (Data S1), not the restricted API.
    urls=["https://ars.els-cdn.com/content/image/1-s2.0-S2589004224016067-mmc8.zip",
          "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11263957/supplementaryFiles"]
    errors=[]
    for u in urls:
        try:
            b,m=download(u,30_000_000)
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                entries=[{"name":i.filename,"bytes":i.file_size} for i in z.infolist() if not i.is_dir()]
                if not entries:raise ValueError("empty archive")
                out={"status":"public_supplement_inventory","source":m,"members":entries[:150]}
                # Archive can itself include Data S1 zip. Read only bounded nested archive.
                inner=[i for i in z.infolist() if i.filename.lower().endswith("mmc8.zip") and i.file_size<25_000_000]
                if len(inner)==1:
                    with zipfile.ZipFile(io.BytesIO(z.read(inner[0]))) as zz:
                        out["data_s1_members"]=[{"name":i.filename,"bytes":i.file_size} for i in zz.infolist() if not i.is_dir()][:150]
                return out
        except Exception as e:errors.append({"url":u,"type":type(e).__name__,"detail":str(e)[:200]})
    return {"status":"blocked","errors":errors}
def main():
    test()
    report={"status":"started","claim_boundary":"Recorded first main roost classes, including caves AND mines; not obligacy, communities or causal selection."}
    dest=OUT/"audit_v13.json"
    def save():dest.write_text(json.dumps(report,indent=2,allow_nan=False))
    try:
        f,audit=get_euro();report["euro_sources"]=audit
        assert all(k in f for k in ("taxon","roost","description","morphology","foraging"))
        df,report["roost_audit"]=roost(f["roost"],taxonomy(f["taxon"]))
        report["morphology_definitions"]=trait_metadata(f["description"],"morphology")
        report["foraging_definitions"]=trait_metadata(f["description"],"foraging_habitat")
        report["foraging_value_vocab"]={str(k):countdict(g.verbatimTraitValue) for k,g in f["foraging"].groupby("verbatimTraitName") if g.verbatimTraitValue.nunique()<=15}
        morph=euro_morph(f["morphology"],f["description"])
        for k,v in morph.items():
            if "pool" in v:df[k]=df.species.map(v.pop("pool"))
        report["euro_morph_qc"]=morph
        fields=[k for k in ("mass","euro_ar") if k in df]
        report["euro_only"]=run_contrasts(df,fields)
        report["status"]="euro_roost_and_morphology_audited";save()
        wdata=None;errors=[]
        for _ in range(3):
            try:
                wdata,wm=wing();break
            except Exception as e:errors.append(type(e).__name__+": "+str(e)[:200])
        report["wing_attempt_errors"]=errors
        if wdata is not None:
            raw=wdata["wingReview_wm_data_final.csv"];report["wing_hash"]=wm["wingReview_wm_data_final.csv"]["sha256"]
            result={}
            for mode in ("direct_or_formula","direct_only"):
                w,qc=study_wing(raw,mode);w["species"]=w["scientificName.iucn"].map(name)
                assert w.species.is_unique
                q=df.merge(w[["species","aspectRatio","wingLoading_Nm2"]],on="species",how="left",validate="one_to_one")
                q=q.rename(columns={"aspectRatio":"ar","wingLoading_Nm2":"wl"})
                result[mode]={"n_AR":int(q.ar.notna().sum()),"n_WL":int(q.wl.notna().sum()),
                    "contrasts":run_contrasts(q,["ar"]+fields)}
                if "mass" in q:
                    joint=q.dropna(subset=["ar","mass"])
                    result[mode]["joint_AR_mass"]=run_contrasts(joint,["ar","mass"])
            report["wing_contrasts"]=result;report["status"]="species_pool_comparison_completed"
        else:report["wing_status"]="unavailable"
        save()
    except Exception as e:
        report["error"]=type(e).__name__+": "+str(e)[:300];report["status"]="blocked";save()
    try:report["landing_supplement"]=landing_supplement()
    except Exception as e:report["landing_supplement"]={"status":"blocked","error":type(e).__name__}
    save();print(json.dumps(report,indent=2,allow_nan=False))
    return 0 if report["status"]=="species_pool_comparison_completed" else 2
if __name__=="__main__":raise SystemExit(main())
