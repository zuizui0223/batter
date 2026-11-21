"""Known-error GPS height observation likelihood over a discrete 3D use grid.

Source-free method experiment. No Goldshtein original source rows and NO
continuous ssf3D/region-wide occupancy claim. Uses existing nested M0-M3
movement/resource features, but marginalizes an independently calibrated
GPS AGL measurement error before fitting and scoring observed XY+height.

Only complete *enumerated* XY x Z candidate grids are supported in v1.
Do not apply Gaussian convolution to q-sampled control *labels*: there the
choice-set construction/proposal and error observation process differ.
"""
from __future__ import annotations
from collections import defaultdict
import math

from paired_3d_ssf_resource_benchmark_v1 import (
    LEVELS, RIDGE, MIN_BATS, _train_scale, _matrix, _weights, fit as hard_choice_fit,
)

SCHEMA="batter.gps_height_error_likelihood.v1"
FIELDS=("joint","horizontal","height_given_horizontal")
_LOG_SQRT_2PI=0.5*math.log(2*math.pi)


def _logsumexp(items):
    if not items:
        raise ValueError("STOP_EMPTY_PROBABILITY_SUPPORT")
    mx=max(items)
    return mx+math.log(math.fsum(math.exp(v-mx) for v in items))


def validate_observed_noisy_events(events, include_state=False):
    if not isinstance(events,(list,tuple)) or len(events)<MIN_BATS*3:
        raise ValueError("STOP_NO_SOURCE_GPS_HEIGHT_EVENTS")
    bats=set()
    keys=set()
    for e in events:
        if not isinstance(e,dict):
            raise ValueError("STOP_INVALID_OBSERVATION_RECORD")
        for key in ("bat","site","night","step","observed_xy"):
            if not isinstance(e.get(key),str) or not e[key].strip():
                raise ValueError("STOP_MISSING_BAT_NIGHT_OR_XY_KEY")
        serial=tuple(e[k] for k in ("bat","site","night","step"))
        if serial in keys:
            raise ValueError("STOP_DUPLICATE_SOURCE_EVENT")
        keys.add(serial)
        bats.add(e["bat"])
        if "observed_choice" in e or "latent_z_truth" in e:
            raise ValueError("STOP_LATENT_TRUE_HEIGHT_LEAKS_INTO_TRAINING")
        if any(e.get(flag) is not True for flag in (
                "original_fix","regular_interval_verified",
                "sensor_agl_datum_verified","sensor_sigma_from_independent_calibration",
                "candidate_grid_independent_of_test_height",
                "resource_measured_independently","fixed_complete_xy_z_support")):
            raise ValueError("STOP_UNVERIFIED_SENSOR_GPS_OR_RISKSET_PROVENANCE")
        obs=e.get("observed_agl_m")
        sig=e.get("sensor_sigma_m")
        if (type(obs) not in (int,float) or not math.isfinite(obs) or
            type(sig) not in (int,float) or not math.isfinite(sig) or sig<=0):
            raise ValueError("STOP_MISSING_OR_UNCALIBRATED_HEIGHT_OBSERVATION")
        if e.get("resource_kind") not in ("cactus_location_proxy","dated_measured_flower"):
            raise ValueError("STOP_UNKNOWN_SOURCE_RESOURCE_KIND")
        if e["resource_kind"]=="dated_measured_flower" and not all(
                e.get(flag) is True for flag in (
                "resource_same_night_observed",
                "resource_survey_effort_verified",
                "resource_no_simulated_imputation")):
            raise ValueError("STOP_UNVERIFIED_DIRECT_DATED_BLOOM_JOIN")
        if include_state and not (
            type(e.get("state_context")) is int and
            e["state_context"] in (0,1) and
            e.get("state_annotation_height_blind") is True):
            raise ValueError("STOP_STATE_USES_RESPONSE_HEIGHT_OR_UNVERIFIED")
        choices=e.get("choices")
        if not isinstance(choices,list) or len(choices)<4:
            raise ValueError("STOP_UNVERIFIED_DISCRETE_3D_AVAILABILITY")
        cells=defaultdict(set)
        seen=set()
        atxy={}
        for c in choices:
            if not isinstance(c,dict):
                raise ValueError("STOP_INVALID_3D_CANDIDATE_RECORD")
            xy,z=c.get("xy_cell"),c.get("z_level")
            if not isinstance(xy,str) or not xy or not isinstance(z,str) or not z:
                raise ValueError("STOP_NO_CANDIDATE_XY_Z_LABEL")
            if (xy,z) in seen:
                raise ValueError("STOP_DUPLICATE_3D_CANDIDATE_CELL")
            seen.add((xy,z))
            cells[xy].add(z)
            for field in ("agl_m","step_m","cos_turn","omega_delta",
                          "forest_structure","resource_count"):
                v=c.get(field)
                if type(v) not in (int,float) or not math.isfinite(v):
                    raise ValueError("STOP_MISSING_3D_MOVEMENT_RESOURCE_INPUT")
            if c["agl_m"]<0 or c["step_m"]<=0 or c["resource_count"]<0:
                raise ValueError("STOP_NEGATIVE_AGL_RESOURCE_OR_STEP")
            if xy not in atxy:
                atxy[xy]=c["resource_count"]
            elif abs(atxy[xy]-c["resource_count"])>1e-10:
                raise ValueError("STOP_HEIGHT_DEFINED_RESOURCE_COVARIATE")
            if c.get("is_control_built_from_test_endpoint") is not False:
                raise ValueError("STOP_TEST_OBSERVED_HEIGHT_USED_FOR_CANDIDATES")
        if (len(cells)<2 or e["observed_xy"] not in cells or
            min(map(len,cells.values()))<2 or
            len({frozenset(z) for z in cells.values()})!=1):
            raise ValueError("STOP_UNBALANCED_OR_ABSENT_3D_XY_Z_SUPPORT")
    if len(bats)<MIN_BATS:
        raise ValueError("STOP_TOO_FEW_INDEPENDENT_BATS")
    return tuple(events)


def _emission(e,c):
    if c["xy_cell"]!=e["observed_xy"]:
        return float("-inf")
    s=e["sensor_sigma_m"]
    r=(e["observed_agl_m"]-c["agl_m"])/s
    return -0.5*r*r-math.log(s)-_LOG_SQRT_2PI


def _prob_from_log(scores):
    z=_logsumexp(scores)
    return [math.exp(s-z) for s in scores], z


def _precomputed(data,fields,center,scale):
    out=[]
    for e in data:
        x=_matrix(e,fields,center,scale)
        log_emission=[_emission(e,c) for c in e["choices"]]
        if not any(math.isfinite(a) for a in log_emission):
            raise ValueError("STOP_OBSERVATION_XY_HAS_NO_CANDIDATE_SUPPORT")
        out.append((x,log_emission))
    return tuple(out)


def _loss_gradient(beta,table,weights):
    p=len(beta)
    total=RIDGE*math.fsum(t*t for t in beta)/2
    grad=[RIDGE*t for t in beta]
    for (x,obs),w in zip(table,weights):
        eta=[math.fsum(row[j]*beta[j] for j in range(p)) for row in x]
        probs,den=_prob_from_log(eta)
        post,obsden=_prob_from_log([
            (eta[i]+obs[i]) if math.isfinite(obs[i]) else float("-inf")
            for i in range(len(eta))])
        total+=w*(den-obsden)
        for j in range(p):
            grad[j]+=w*math.fsum(
                (probs[k]-post[k])*x[k][j] for k in range(len(eta)))
    return total,grad


def _dot(a,b):
    return math.fsum(x*y for x,y in zip(a,b))


def _mmul(m,v):
    return [_dot(row,v) for row in m]


def fit_error_aware(events,fields,max_iter=110):
    """Ridge mixture-likelihood BFGS; tests are synthetic only."""
    if len(events)<10:
        raise ValueError("STOP_TOO_FEW_TRAINING_EVENTS")
    center,scale=_train_scale(events,fields)
    table=_precomputed(events,fields,center,scale)
    weights=_weights(events)
    p=len(fields)
    H=[[float(i==j) for j in range(p)] for i in range(p)]
    beta=[0.]*p
    objective,gradient=_loss_gradient(beta,table,weights)
    for iteration in range(max_iter):
        if max(map(abs,gradient))<3e-7:
            break
        direction=[-v for v in _mmul(H,gradient)]
        if _dot(direction,gradient)>=-1e-14:
            direction=[-v for v in gradient]
            H=[[float(i==j) for j in range(p)] for i in range(p)]
        factor=1.
        accepted=False
        for _ in range(34):
            trial=[beta[i]+factor*direction[i] for i in range(p)]
            newloss,newgradient=_loss_gradient(trial,table,weights)
            if newloss<=objective+1e-4*factor*_dot(gradient,direction):
                accepted=True
                break
            factor*=0.5
        if not accepted:
            if max(map(abs,gradient))<1e-5:
                break
            raise ValueError("STOP_GPS_MIXTURE_OPTIMIZER_LINESEARCH")
        s=[trial[i]-beta[i] for i in range(p)]
        y=[newgradient[i]-gradient[i] for i in range(p)]
        ys=_dot(y,s)
        if ys>1e-12:
            hy=_mmul(H,y)
            yhy=_dot(y,hy)
            H=[[H[i][j]+(ys+yhy)/(ys*ys)*s[i]*s[j]-
                (s[i]*hy[j]+hy[i]*s[j])/ys
                for j in range(p)] for i in range(p)]
        else:
            H=[[float(i==j) for j in range(p)] for i in range(p)]
        beta,objective,gradient=trial,newloss,newgradient
    else:
        if max(map(abs,gradient))>1e-4:
            raise ValueError("STOP_GPS_MIXTURE_OPTIMIZER_MAX_ITER")
    return {"fields":tuple(fields),"center":center,"scale":scale,
            "beta":beta,"training_method":"known_sigma_mixture",
            "height_observation_likelihood":"normal_AGL_error"}


def fit_hard_bin_naive(events,fields):
    """For comparison only: round noisy GPS height to the nearest candidate Z."""
    training=[]
    for e in events:
        chosen=min(
            (i for i,c in enumerate(e["choices"]) if c["xy_cell"]==e["observed_xy"]),
            key=lambda i:abs(e["choices"][i]["agl_m"]-e["observed_agl_m"]))
        d=dict(e)
        d["observed_choice"]=chosen
        training.append(d)
    model=hard_choice_fit(training,fields)
    model["training_method"]="hard_bin_naive"
    return model


def score_observed(model,event):
    rows=_matrix(event,model["fields"],model["center"],model["scale"])
    eta=[_dot(x,model["beta"]) for x in rows]
    xy=event["observed_xy"]
    sum_all=_logsumexp(eta)
    sum_xy=_logsumexp([eta[i] for i,c in enumerate(event["choices"])
                       if c["xy_cell"]==xy])
    sum_obs=_logsumexp([eta[i]+_emission(event,c)
                         for i,c in enumerate(event["choices"])
                         if c["xy_cell"]==xy])
    joint=sum_obs-sum_all
    horizontal=sum_xy-sum_all
    conditional_height=sum_obs-sum_xy
    if abs(joint-horizontal-conditional_height)>1e-9:
        raise AssertionError("BROKEN_GPS_ERROR_HEIGHT_DECOMPOSITION")
    return {"joint":joint,"horizontal":horizontal,
            "height_given_horizontal":conditional_height}


def _foldkey(e,holdout):
    if holdout=="bat":
        return e["bat"]
    if holdout=="bat_night":
        return (e["bat"],e["site"],e["night"])
    if holdout=="site":
        return e["site"]
    raise ValueError("STOP_UNKNOWN_HEIGHT_SENSOR_HOLDOUT")


def _balanced_test_score(events,model):
    bybat=defaultdict(lambda:defaultdict(list))
    for e in events:
        d=score_observed(model,e)
        bybat[e["bat"]][(e["site"],e["night"])].append(d)
    return {field:math.fsum(
        math.fsum(math.fsum(d[field] for d in night)/len(night)
                  for night in nights.values())/len(nights)
        for nights in bybat.values())/len(bybat)
        for field in FIELDS}


def evaluate_error_noise(risksets,holdout="bat",include_state=False):
    """Identical observed XY/continuous noisy AGL target for every model."""
    events=validate_observed_noisy_events(risksets,include_state)
    names=tuple(LEVELS) if include_state else tuple(LEVELS)[:3]
    groups=sorted({_foldkey(e,holdout) for e in events},key=str)
    if len(groups)<2:
        raise ValueError("STOP_TOO_FEW_INDEPENDENT_HEIGHT_HOLDOUTS")
    result=[]
    for ordinal,g in enumerate(groups,1):
        tr=[e for e in events if _foldkey(e,holdout)!=g]
        te=[e for e in events if _foldkey(e,holdout)==g]
        if len({e["bat"] for e in tr})<3:
            raise ValueError("STOP_FEWER_THAN_THREE_TRAINING_BATS")
        scores={}
        for name in names:
            fields=LEVELS[name]
            aware=fit_error_aware(tr,fields)
            naive=fit_hard_bin_naive(tr,fields)
            scores[name]={"sensor_aware":_balanced_test_score(te,aware),
                          "hard_bin_naive":_balanced_test_score(te,naive)}
        gains={}
        for a,b in zip(names[1:],names[:-1]):
            key=a+"_minus_"+b
            gains[key]={method:{field:scores[a][method][field]-scores[b][method][field]
                                for field in FIELDS}
                        for method in ("sensor_aware","hard_bin_naive")}
        result.append({"fold_ordinal":ordinal,
                       "n_bats":len({e["bat"] for e in te}),
                       "n_bat_nights":len({(e["bat"],e["site"],e["night"]) for e in te}),
                       "n_observed_xy_agl":len(te),
                       "paired_gains":gains,
                       "per_model_scores":scores})
    summary={}
    for contrast in result[0]["paired_gains"]:
        summary[contrast]={}
        for method in ("sensor_aware","hard_bin_naive"):
            summary[contrast][method]={field:math.fsum(
                r["paired_gains"][contrast][method][field] for r in result)/len(result)
                for field in FIELDS}
    return {"schema":SCHEMA,
            "status":"KNOWN_NOISE_SOURCE_FREE_OBSERVATION_LIKELIHOOD_ONLY",
            "n_fictional_or_source_bats":len({e["bat"] for e in events}),
            "n_observed_events":len(events),"n_holdout_groups":len(result),
            "heldout_unit":holdout,
            "model_terms":list(names),
            "heldout_outcome":"observed XY and continuous noisy AGL, not latent true height",
            "height_noise_model":"independently calibrated Gaussian SD per original fix",
            "sensor_sd_values_m":sorted({e["sensor_sigma_m"] for e in events}),
            "candidate_mode":"prespecified complete XY×Z enumerated grid ONLY",
            "q_sampled_control_correction_integrated":False,
            "true_regional_horizontal_species_sdm_estimated":False,
            "real_goldshtein_source_verified_by_code":False,
            "empirical_3d_resource_height_gain_claim_allowed":False,
            "fix_level_inference":False,
            "fold_aggregates_without_identifying_keys":result,
            "group_equal_gains_nats_per_recorded_fix":summary}
