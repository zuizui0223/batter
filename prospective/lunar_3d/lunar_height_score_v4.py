#!/usr/bin/env python3
"""Frozen (v4) whole-night lunar conditional raw-height scoring.

IMPORTANT: Numeric heights are read only AFTER a source-only v3-equivalent
eligibility set is reconstructed; see LUNAR_V4_HEIGHT_SCORE_PREOPEN_FREEZE.md.
Never interpret GPS MSL/ellipsoid as independently calibrated AGL.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from bisect import bisect_left
import itertools
import json
import math
from pathlib import Path
import random
from statistics import median, mean

from prospective.lunar_3d.lunar_source_gate_v1 import (
    as_utc, canon, classify_fix, local_solar_night, OUTLIERS, truthy
)
from prospective.lunar_3d.lunar_source_admission_v3 import (
    get_csv, build_reference, match_counts,
    CONTRACTS, CELL_DEG, CLOCK_HOURS, MIN_FIX_NIGHT,
    MIN_TOTAL_PER_EXPOSURE, MIN_NIGHTS_PER_EXPOSURE, MIN_MATCHED_ANIMALS,
)

EDGES = (-100.0, -25.0, 25.0, 100.0)
ALPHA = 0.5
MAX_ABS_HEIGHT = 10000.0
BOOTSTRAP_N = 5000
SEED = 20261122
SENS_DOP_MIN_COVERAGE = 0.8

def safe_num(x):
    try:
        n=float(x)
    except (TypeError,ValueError):
        return None
    return n if math.isfinite(n) else None

def candidate_records(contract, rows, headers, refs):
    """Rebuild the frozen v3 data-support universe, without reading heights."""
    height_field=contract["vertical"]["field"]
    if height_field not in headers:
        raise ValueError("expected source native height field missing")
    refmap=build_reference(refs)
    cache={}
    candidates=[]
    counts=defaultdict(lambda: {"bright":Counter(), "dark":Counter()})
    explicit=any(x in headers for x in OUTLIERS)
    for row in rows:
        animal=str(row.get("individual_local_identifier") or row.get("animal_id") or row.get("individual_id") or "").strip()
        meta=refmap.get(animal)
        if not meta or not meta["ok"]:
            continue
        if explicit and any(truthy(row.get(f)) for f in OUTLIERS):
            continue
        if not explicit and "visible" in row and str(row.get("visible") or "").strip() and not truthy(row["visible"]):
            continue
        if not str(row.get(height_field) or "").strip(): # height PRESENCE only
            continue
        try:
            lat,lon=float(row["location_lat"]),float(row["location_long"])
            if not (math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
                continue
            dt=as_utc(row["timestamp"])
        except (KeyError,TypeError,ValueError,OverflowError):
            continue
        exp=classify_fix(dt,lat,lon,cache)
        if exp not in ("bright","dark"):
            continue
        night=local_solar_night(dt,lon)
        local_hour=(dt+timedelta(hours=lon/15)).hour
        key=(animal,meta["site"],night[:4],math.floor(lat/CELL_DEG),math.floor(lon/CELL_DEG),local_hour//CLOCK_HOURS)
        data={"key":key, "animal":animal, "site":meta["site"],"year":night[:4],
              "night":night, "exposure":exp,
              "height_raw_string":row[height_field],
              "dop":row.get("gps_dop"),
              "hdop":row.get("gps_hdop"),
              "vdop":row.get("gps_vdop")}
        candidates.append(data)
        counts[key][exp][night]+=1
    matches={p[0] for p in match_counts(counts)}
    return candidates, matches

def keep_admitted_fixes(candidates, matched):
    """Independent of numeric heights; eligible >=8-fix nights in v3 cells."""
    if not matched:
        return []
    counts=defaultdict(Counter)
    for r in candidates:
        if r["key"] in matched:
            counts[(r["key"],r["exposure"])][r["night"]]+=1
    return [r for r in candidates if r["key"] in matched
            and counts[(r["key"],r["exposure"])][r["night"]]>=MIN_FIX_NIGHT]

def add_numeric_height(records):
    """First and only conversion from source height-string to numeric outcome."""
    good=[]
    invalid=Counter()
    for r in records:
        h=safe_num(r["height_raw_string"])
        if h is None:
            invalid["missing_or_nonfinite_numeric_height"]+=1
            continue
        if abs(h)>MAX_ABS_HEIGHT:
            invalid["implausible_abs_gt_10000m"]+=1
            continue
        good.append({**r,"z":h})
    return good,dict(invalid)

def quality_ok(r, source_doi):
    if source_doi == "10.5441/001/1.321":
        h=safe_num(r.get("hdop"))
        v=safe_num(r.get("vdop"))
        return (h is not None and v is not None), (h is not None and v is not None and 0<=h<=5 and 0<=v<=8)
    d=safe_num(r.get("dop"))
    return (d is not None), (d is not None and 0<=d<=8)

def requalify_quality_rows(rows, original_matched, doi):
    """Source-availability only, after DOP filter, never fitted-height-selected."""
    good=[]
    covered=0
    for r in rows:
        has,ok=quality_ok(r,doi)
        covered+=int(has)
        if ok:
            good.append(r)
    coverage=covered/len(rows) if rows else 0
    if coverage < SENS_DOP_MIN_COVERAGE:
        return coverage, [], set(), "gps_dop_coverage_below_80pct"
    counts=defaultdict(lambda: {"bright": Counter(), "dark": Counter()})
    for r in good:
        if r["key"] in original_matched:
            counts[r["key"]][r["exposure"]][r["night"]]+=1
    eligible={r[0] for r in match_counts(counts)}
    if len({k[0] for k in eligible})<MIN_MATCHED_ANIMALS:
        return coverage, [], eligible, "fewer_than_five_dop_qualified_individuals"
    return coverage,keep_admitted_fixes(good,eligible),eligible,"ready"

def cat(z):
    return bisect_left(EDGES,z)

def hist(vals):
    c=[0]*5
    for x in vals:
        c[cat(x)]+=1
    return c

def prob(counts, bin_index):
    return (counts[bin_index]+ALPHA)/(sum(counts)+5*ALPHA)

def quantile(values,q):
    if not values:
        return None
    a=sorted(values)
    x=q*(len(a)-1)
    lo,hi=math.floor(x),math.ceil(x)
    return a[lo]+(x-lo)*(a[hi]-a[lo])

def score_height_records(records, shape=False):
    """Heldout full-night conditional binned log scores, same rows for B0/B1."""
    if not records:
        return {"status":"no_valid_numeric_height","scored_animals":0}
    by_key=defaultdict(list)
    by_animal_cohort=defaultdict(list)
    by_key_night=defaultdict(list)
    for r in records:
        by_key[r["key"]].append(r)
        by_animal_cohort[r["key"][:3]].append(r)
        by_key_night[(r["key"],r["night"])].append(r)
    med_by_night={}
    if shape:
        for pair,items in by_key_night.items():
            med_by_night[pair]=median(x["z"] for x in items)
    folded=[]
    for key,items in by_key.items():
        all_nights=sorted({r["night"] for r in items})
        group_by_night=defaultdict(list)
        for r in items: group_by_night[r["night"]].append(r)
        for target_night in all_nights:
            trained=[r for r in items if r["night"]!=target_night]
            holdout=group_by_night[target_night]
            # No target-night values used for training-only median.
            if not trained:
                continue
            if not shape:
                other=by_animal_cohort[key[:3]]
                other_heights=[r["z"] for r in other if r["night"]!=target_night]
                if not other_heights:
                    continue
                center=median(other_heights)
            for exp in ("bright","dark"):
                test=[r for r in holdout if r["exposure"]==exp]
                train_class=[r for r in trained if r["exposure"]==exp]
                # Must not hallucinate a fitted conditional model when class has no other night.
                if not test or not train_class:
                    continue
                if shape:
                    train_values=[r["z"]-med_by_night[(r["key"],r["night"])] for r in trained]
                    class_values=[r["z"]-med_by_night[(r["key"],r["night"])] for r in train_class]
                    test_values=[r["z"]-med_by_night[(r["key"],r["night"])] for r in test]
                else:
                    train_values=[r["z"]-center for r in trained]
                    class_values=[r["z"]-center for r in train_class]
                    test_values=[r["z"]-center for r in test]
                b=hist(train_values)
                a=hist(class_values)
                sb=sum(math.log(prob(b,cat(y))) for y in test_values)/len(test_values)
                sa=sum(math.log(prob(a,cat(y))) for y in test_values)/len(test_values)
                folded.append({"animal":key[0],"night":target_night,"exposure":exp,
                               "stratum":key,"nfix":len(test),"b0":sb,"b1":sa})
    # Equal stratum within animal/night/exposure -> equal night within exposure
    by_animal_exp_night=defaultdict(list)
    for f in folded:
        by_animal_exp_night[(f["animal"],f["exposure"],f["night"])].append(f)
    by_animal_exp=defaultdict(list)
    for (animal,exp,_night),group in by_animal_exp_night.items():
        by_animal_exp[(animal,exp)].append((
            mean(f["b0"] for f in group),mean(f["b1"] for f in group)
        ))
    by_animal=defaultdict(dict)
    for (animal,exp),scores in by_animal_exp.items():
        by_animal[animal][exp]=(mean(x[0] for x in scores),mean(x[1] for x in scores))
    animals=[]
    for animal,classes in by_animal.items():
        if "bright" not in classes or "dark" not in classes:
            continue
        baseline=(classes["bright"][0]+classes["dark"][0])/2
        augmented=(classes["bright"][1]+classes["dark"][1])/2
        animals.append((animal,baseline,augmented,augmented-baseline))
    if len(animals)<MIN_MATCHED_ANIMALS:
        return {"status":"insufficient_scored_animals","scored_animals":len(animals),
                "heldout_night_stratum_exposure_folds":len(folded)}
    eff=[x[3] for x in animals]
    baseline=mean(x[1] for x in animals)
    augmented=mean(x[2] for x in animals)
    rng=random.Random(SEED)
    bootstrap=[mean(rng.choice(eff) for _ in eff) for _ in range(BOOTSTRAP_N)]
    obs=mean(eff)
    flips=(sum(1 for signs in itertools.product((-1,1),repeat=len(eff))
               if mean(s*v for s,v in zip(signs,eff)) >= obs-1e-12)/(2**len(eff)))
    return {"status":"scored_unvalidated_native_altitude" if not shape else "secondary_centered_session_shape",
            "scored_animals":len(animals),
            "animals_with_positive_lunar_increment":sum(v>0 for v in eff),
            "number_of_heldout_night_stratum_exposure_folds":len(folded),
            "distinct_heldout_animal_nights":len({(f["animal"],f["night"]) for f in folded}),
            "heldout_scored_fix_instances":sum(f["nfix"] for f in folded),
            "equal_animal_baseline_logscore_nats_per_fix":baseline,
            "equal_animal_lunar_logscore_nats_per_fix":augmented,
            "equal_animal_delta_nats_per_fix":obs,
            "animal_bootstrap_95pct": [quantile(bootstrap,.025),quantile(bootstrap,.975)],
            "animal_signflip_one_sided_tail":flips,
            "individual_effect_minmax": [min(eff),max(eff)],
            "fit_rule":"Dirichlet0.5_5bins_whole-night-heldout",
            "fold_anchor":"training-only_animal_median" if not shape else "within-night_centered_target",
            "class_edges_relative_to_anchor_m":list(EDGES),
            "aggregation":"stratum_equal/night_equal/exposure_equal/animal_equal",
    }

def source_run(contract):
    gps,headers=get_csv(contract["source"]["gps"])
    refs,_=get_csv(contract["source"]["reference"])
    candidates,qualifying=candidate_records(contract,gps,headers,refs)
    # Enforce the separately authenticated and already reported v3 source admission.
    admitted_animals=len({key[0] for key in qualifying})
    expected=9 if contract["repository_doi"]=="10.5441/001/1.321" else 6
    if admitted_animals!=expected:
        raise RuntimeError(f"height-blind v3 gate changed: {admitted_animals} vs frozen {expected}")
    selected=keep_admitted_fixes(candidates,qualifying)
    # Quality sensitivity support uses DOP, before opening numeric heights:
    coverage,qual_filtered,qual_sens,reason=requalify_quality_rows(selected,qualifying,contract["repository_doi"])
    good,invalid=add_numeric_height(selected)
    qgood,qinvalid=add_numeric_height(qual_filtered) if qual_filtered else ([],{})
    q_bright=[r["z"] for r in good if r["exposure"]=="bright"]
    q_dark=[r["z"] for r in good if r["exposure"]=="dark"]
    metrics=score_height_records(good)
    shape=score_height_records(good,shape=True)
    qmetrics=score_height_records(qgood) if reason=="ready" else {"status":"not_estimable","reason":reason}
    if reason=="ready" and qmetrics.get("status")=="insufficient_scored_animals":
        qmetrics["reason"]="fewer_than_five_scored_animals_after_predefined_dop_screen"
    return {
        "source_doi":contract["repository_doi"],"taxon":contract["taxon"],
        "native_height_field":contract["vertical"]["field"],
        "native_height_semantics":contract["vertical"]["semantics"],
        "raw_height_is_ground_corrected":False,
        "height_blind_v3_matched_individuals":admitted_animals,
        "height_blind_v3_matched_strata":len(qualifying),
        "selected_height_presence_fix_count":len(selected),
        "valid_plausible_native_height_fix_count":len(good),
        "excluded_numeric_height_reasons":invalid,
        "selected_bright_native_height_quantiles_m":[quantile(q_bright,q) for q in (.05,.5,.95)],
        "selected_dark_native_height_quantiles_m":[quantile(q_dark,q) for q in (.05,.5,.95)],
        "dop_available_fraction_selected":coverage,
        "dop_sensitivity_admitted_individuals":len({key[0] for key in qual_sens}),
        "dop_sensitivity_selected_height_presence_fixes":len(qual_filtered),
        "dop_sensitivity_invalid_heights":qinvalid,
        "raw_altitude_predictive_test":metrics,
        "sensor_dop_quality_sensitivity":qmetrics,
        "secondary_within_night_centered_shape":shape,
    }

def main():
    payload={"protocol":"LUNAR_V4_HEIGHT_SCORE_PREOPEN_FREEZE.md",
             "analysis":"lunar-v4-pre-frozen-score",
             "source_height_is_calibrated_agl":False,
             "source_applied_after_protocol_freeze":True,
             "results":[]}
    for p in CONTRACTS:
        contract=json.loads(Path(p).read_text(encoding="utf-8"))
        payload["results"].append(source_run(contract))
    out=Path("results/lunar_3d_height_heldout_v4.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(payload,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
