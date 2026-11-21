"""Hendel independent Black Forest bat-insect ecology: source-free prediction engine.

NO original Hendel XLSX values included or loaded. Raw publisher bytes remain
HTTP401 in current Action source gate. This is a frozen predictive analysis
interface, NOT a measured out-of-source gain.
Four acoustic output channels can overlap; NEVER normalize as a multinomial.
"""
from __future__ import annotations
import math
from collections import Counter
from ducke_guild_cv_engine_v1 import _solve

MIN_SOURCE_SITES=50
RIDGE=0.15
TARGETS=("SRE","MRE","Ppip","LRE")
BASE=("elevation","DOY","temp_min","Opn_mean","ndsm_sd","ForMI")
MODELS={
    "forest_weather_time":BASE,
    "plus_moth_abundance":BASE+("mothcount",),
    "plus_moth_richness":BASE+("moth_richness",),
    "plus_moth_abundance_and_richness":BASE+("mothcount","moth_richness"),
    "plus_ground_beetle_abundance":BASE+("carabidae",),
    "plus_ground_beetle_richness":BASE+("carabidae_S",),
    "plus_ground_beetle_abundance_and_richness":BASE+("carabidae","carabidae_S"),
}
LOG_COUNTS={"mothcount","moth_richness","carabidae","carabidae_S"}
CONTRASTS={
    "moth_abundance_given_forest":("plus_moth_abundance","forest_weather_time"),
    "moth_richness_given_abundance":("plus_moth_abundance_and_richness","plus_moth_abundance"),
    "moth_abundance_given_richness":("plus_moth_abundance_and_richness","plus_moth_richness"),
    "beetle_abundance_given_forest":("plus_ground_beetle_abundance","forest_weather_time"),
    "beetle_richness_given_abundance":("plus_ground_beetle_abundance_and_richness","plus_ground_beetle_abundance"),
    "beetle_abundance_given_richness":("plus_ground_beetle_abundance_and_richness","plus_ground_beetle_richness"),
}


def validate_original_source_rows(rows):
    if not isinstance(rows,(list,tuple)) or len(rows)<MIN_SOURCE_SITES:
        raise ValueError("STOP_INDEPENDENT_HENDEL_N_SOURCE_TOO_SMALL")
    sites=[]
    for item in rows:
        if not isinstance(item,dict):
            raise ValueError("STOP_HENDEL_INVALID_RECORD_TYPE")
        label=item.get("plotID")
        if not isinstance(label,(str,int)) or not str(label).strip():
            raise ValueError("STOP_HENDEL_SITE_LABEL_MISSING")
        sites.append(str(label))
        for name in set(BASE)|LOG_COUNTS|set(TARGETS):
            val=item.get(name)
            if type(val) not in (int,float) or not math.isfinite(float(val)):
                raise ValueError("STOP_HENDEL_FIELD_MISSING_OR_NONFINITE:"+name)
            if (name in LOG_COUNTS or name in TARGETS) and val<0:
                raise ValueError("STOP_HENDEL_NEGATIVE_PREY_OR_ACTIVITY")
    if len(set(sites))!=len(rows):
        raise ValueError("STOP_HENDEL_DUPLICATE_OR_REUSED_FOREST_PLOT")
    return tuple(rows)


def _raw_input(row,columns):
    return [math.log1p(row[k]) if k in LOG_COUNTS else float(row[k]) for k in columns]


def _train_scale(train,test,fields,target):
    xraw=[_raw_input(r,fields) for r in train]
    test_raw=[_raw_input(r,fields) for r in test]
    n=len(train)
    mu=[math.fsum(row[j] for row in xraw)/n for j in range(len(fields))]
    sd=[math.sqrt(math.fsum((row[j]-mu[j])**2 for row in xraw)/n) for j in range(len(fields))]
    sd=[x if x>1e-8 else 1. for x in sd]
    x=[[1.]+[(row[j]-mu[j])/sd[j] for j in range(len(fields))] for row in xraw]
    z=[[1.]+[(row[j]-mu[j])/sd[j] for j in range(len(fields))] for row in test_raw]
    raw_y=[math.log1p(r[target]) for r in train]
    mean_y=math.fsum(raw_y)/n
    var_y=math.fsum((v-mean_y)**2 for v in raw_y)/n
    if var_y<1e-10:
        raise ValueError("STOP_HENDEL_TRAINING_TARGET_CONSTANT:"+target)
    sd_y=math.sqrt(var_y)
    y=[(v-mean_y)/sd_y for v in raw_y]
    test_y=[(math.log1p(r[target])-mean_y)/sd_y for r in test]
    return x,z,y,test_y


def _fit_predict(train,test,fields,target):
    x,z,y,target_y=_train_scale(train,test,fields,target)
    n=len(x);k=len(x[0])
    # Fixed ridge on all standardized predictors except intercept.
    matrix=[[math.fsum(row[i]*row[j] for row in x)/n+
             (RIDGE if i==j and i>0 else 0.) for j in range(k)]
            for i in range(k)]
    v=[math.fsum(row[i]*label for row,label in zip(x,y))/n for i in range(k)]
    beta=_solve(matrix,v)
    pred=[math.fsum(row[j]*beta[j] for j in range(k)) for row in z]
    return pred,target_y


def evaluate_heldout_sites(original_qualified_rows):
    """LOSO is within one study, *not* independent geographic transport."""
    rows=validate_original_source_rows(original_qualified_rows)
    if len(rows)>70:
        raise ValueError("STOP_HENDEL_UNEXPECTED_SITE_UNIVERSE")
    fold_scores={target:{label:[] for label in MODELS} for target in TARGETS}
    fold_gain={target:{label:[] for label in CONTRASTS} for target in TARGETS}
    for test_idx in range(len(rows)):
        train=[r for i,r in enumerate(rows) if i!=test_idx]
        test=[rows[test_idx]]
        for target in TARGETS:
            scores={}
            for label,fields in MODELS.items():
                p,y=_fit_predict(train,test,fields,target)
                scores[label]=-math.fsum((a-b)**2 for a,b in zip(p,y))/len(y)
                fold_scores[target][label].append(scores[label])
            for label,(a,b) in CONTRASTS.items():
                fold_gain[target][label].append(scores[a]-scores[b])
    return {
        "schema":"batter.hendel_forest_vs_prey_source_predictor_gains.v1",
        "status":"CALCULATED_WITHIN_STUDY_NOT_EXTERNAL_TRANSPORT",
        "site_heldout_unit":"one entire site",
        "n_source_sites":len(rows),
        "n_source_studies":1,
        "acoustic_guilds_are_mutually_exclusive":False,
        "source_guild_channels":list(TARGETS),
        "predictor_models":{k:list(v) for k,v in MODELS.items()},
        "ridge_lambda":RIDGE,
        "source_method":"training-only standardized log1p(activity) ridge Gaussian squared error",
        "score_unit":"negative squared standardized log activity, dimensionless",
        "per_guild_equal_site_gain":{
           target:{label:math.fsum(vals)/len(vals)
                   for label,vals in fold_gain[target].items()}
           for target in TARGETS
        },
        "per_guild_sites_with_gain_positive":{
           target:{label:sum(val>0 for val in vals)
                   for label,vals in fold_gain[target].items()}
           for target in TARGETS
        },
        "original_site_ids_and_response_data_returned":False,
        "geographically_independent_test":False,
        "guild_activity_is_not_population_abundance":True,
        "true_bat_diet_or_prey_capture":None,
        "resource_conditioned_individual_3D_height_gain":None,
        "Ducke_2018_original_4guild_log_score_directly_comparable":False,
    }
