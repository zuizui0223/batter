"""Joint four-guild *captured-composition* heldout prediction in Ducke.

Known source-open, post-outcome comparison. No original data embedded.
One observed site is one score unit; do not treat captures or guild
components as independent replicates. A single Sanguivore capture is
reported separately and excluded, NOT assigned to another guild.
"""
from __future__ import annotations

import math
from ducke_guild_cv_engine_v1 import _solve, _standardize, RIDGE

GUILDS=("frug","glean","nectar","aerial")
BASE=("elevation_m","design_added_riparian_plot","n_matched_nights")
FEATURES={
    "baseline":BASE,
    "candidate12":BASE+("fruit_batfood_12",),
    "remaining10":BASE+("fruit_other",),
    "both_separate":BASE+("fruit_batfood_12","fruit_other"),
    "total22":BASE+("fruit_all",),
}


def _shares(rows):
    y=[]
    for r in rows:
        if any(type(r.get(g)) is not int or r[g]<0 for g in GUILDS+("sanguivore",)):
            raise ValueError("STOP_SOURCE_GUILD_COUNT_INVALID")
        n=math.fsum(r[g] for g in GUILDS)
        if n<=0 or n+r["sanguivore"]!=r["captures"]:
            raise ValueError("STOP_GUILD_SUM_OR_CAPTURE_DENOMINATOR")
        y.append([r[g]/n for g in GUILDS])
    return y


def _softmax(logits):
    a=list(logits)+[0.0]  # Aerial insectivores are fixed reference guild
    high=max(a)
    exps=[math.exp(t-high) for t in a]
    den=math.fsum(exps)
    return [e/den for e in exps]


def _objective(x,y,b):
    n=len(y);k=len(x[0]);g=len(GUILDS)-1
    if len(b)!=k*g:
        raise ValueError("STOP_MULTINOMIAL_PARAMETER_DIMENSION")
    ps=[]
    loss=0.0
    grad=[0.0]*(k*g)
    hess=[[0.0]*(k*g) for _ in range(k*g)]
    for row,truth in zip(x,y):
        probs=_softmax([math.fsum(b[i*k+j]*row[j] for j in range(k)) for i in range(g)])
        ps.append(probs)
        loss-=math.fsum(truth[i]*math.log(max(probs[i],1e-14)) for i in range(g+1))/n
        for i in range(g):
            delta=(probs[i]-truth[i])/n
            for a in range(k):
                ia=i*k+a
                grad[ia]+=delta*row[a]
                for h in range(g):
                    hfac=probs[i]*((1.0 if i==h else 0.0)-probs[h])/n
                    for c in range(k):
                        hess[ia][h*k+c]+=hfac*row[a]*row[c]
    for i in range(g):
        for a in range(1,k):
            j=i*k+a
            loss+=RIDGE*b[j]*b[j]/2
            grad[j]+=RIDGE*b[j]
            hess[j][j]+=RIDGE
    return loss,grad,hess


def fit_predict(train,test,features):
    if len(train)<20 or not test:
        raise ValueError("STOP_INSUFFICIENT_SOURCE_PLOTS")
    y=_shares(train)
    _shares(test)
    if any(math.fsum(r[i] for r in y)<=0 for i in range(len(GUILDS))):
        raise ValueError("STOP_GUILD_ABSENT_FROM_TRAINING")
    x,v=_standardize(train,test,features)
    k=len(x[0]);n_free=len(GUILDS)-1
    means=[math.fsum(t[i] for t in y)/len(y) for i in range(len(GUILDS))]
    ref=max(means[-1],1e-6)
    b=[0.0]*(n_free*k)
    for i in range(n_free):
        b[i*k]=math.log(max(means[i],1e-6)/ref)
    for _ in range(100):
        old,grad,hess=_objective(x,y,b)
        if max(abs(z) for z in grad)<1e-9:
            break
        step=_solve(hess,grad)
        alpha=1.0
        while alpha>1e-8:
            candidate=[u-alpha*s for u,s in zip(b,step)]
            if _objective(x,y,candidate)[0]<=old+1e-13:
                b=candidate
                break
            alpha/=2
        else:
            raise ValueError("STOP_MULTINOMIAL_LINE_SEARCH")
    else:
        raise ValueError("STOP_MULTINOMIAL_NOT_CONVERGED")
    return [_softmax([math.fsum(b[i*k+j]*row[j] for j in range(k))
                      for i in range(n_free)]) for row in v]


def score(test,pred):
    target=_shares(test)
    return math.fsum(
        math.fsum(q*math.log(max(p,1e-14)) for q,p in zip(y,prs))
        for y,prs in zip(target,pred)
    )/len(test)


def grouped_cv(rows,exclude_PO=False):
    data=list(rows)
    if exclude_PO:
        data=[r for r in data if r["block"]!="PO"]
    if len(data)<29 or len({r["plot"] for r in data})!=len(data):
        raise ValueError("STOP_SOURCE_GRAIN_OR_SIZE")
    groups=sorted({r["block"] for r in data})
    if len(groups)!=(6 if exclude_PO else 7):
        raise ValueError("STOP_SOURCE_BLOCK_UNIVERSE_CHANGED")
    folds=[]
    for group in groups:
        train=[r for r in data if r["block"]!=group]
        test=[r for r in data if r["block"]==group]
        sc={name:score(test,fit_predict(train,test,cov))
            for name,cov in FEATURES.items()}
        contrasts={
            "both_minus_baseline":sc["both_separate"]-sc["baseline"],
            "both_minus_total":sc["both_separate"]-sc["total22"],
            "candidate12_given_remaining10":sc["both_separate"]-sc["remaining10"],
            "remaining10_given_candidate12":sc["both_separate"]-sc["candidate12"],
            "candidate12_minus_baseline":sc["candidate12"]-sc["baseline"],
            "remaining10_minus_baseline":sc["remaining10"]-sc["baseline"],
        }
        folds.append({"fold_ordinal":len(folds)+1,"n_source_plots":len(test),
                      "n_source_4guild_captures":sum(sum(r[g] for g in GUILDS) for r in test),
                      "contrasts":contrasts})
    names=list(folds[0]["contrasts"])
    return {
       "schema":"batter.ducke.multinomial_captured_guild_source_local.v3",
       "status":"POST_OUTCOME_SOURCE_LOCAL_MULTINOMIAL_PREDICTION",
       "n_original_source_plots":len(data),
       "n_heldout_source_blocks":len(groups),
       "observed_4guild_captures":sum(sum(r[g] for g in GUILDS) for r in data),
       "excluded_sanguivore_captures":sum(r["sanguivore"] for r in data),
       "equal_source_block_log_score_gain":{
          z:math.fsum(f["contrasts"][z] for f in folds)/len(folds) for z in names},
       "equal_source_plot_log_score_gain":{
          z:math.fsum(f["contrasts"][z]*f["n_source_plots"] for f in folds)/len(data) for z in names},
       "n_positive_source_blocks":{z:sum(f["contrasts"][z]>0 for f in folds) for z in names},
       "folds_without_source_location_ids":folds,
       "independent_study_replication":False,
       "raw_original_plot_ids_or_coordinates_included":False,
       "resource_conditioned_3D_animal_height_gain":None
    }


def run(original_private_plots):
    data=list(original_private_plots)
    if len(data)!=46 or sum(r["captures"] for r in data)!=810 or sum(r["sanguivore"] for r in data)!=1:
        raise ValueError("STOP_ORIGINAL_SOURCE_ELIGIBILITY_DRIFT")
    return {"source_original_doi":"10.5061/dryad.9rb48c5",
            "four_guilds":list(GUILDS),
            "seven_all_source_blocks":grouped_cv(data),
            "six_L3_L8_source_blocks":grouped_cv(data,exclude_PO=True),
            "real_bat_resource_height_effect":None}


def main():
    import argparse,json
    from pathlib import Path
    arg=argparse.ArgumentParser()
    arg.add_argument("--private-qualified-source-plots",required=True)
    arg.add_argument("--aggregate-output",required=True)
    a=arg.parse_args()
    obj=run(json.loads(Path(a.private_qualified_source_plots).read_text()))
    Path(a.aggregate_output).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    for scope in ("seven_all_source_blocks","six_L3_L8_source_blocks"):
        x=obj[scope]
        print("DUCKE_MULTIGUILD_SOURCE_LOCAL",scope,x["status"],
              x["equal_source_block_log_score_gain"],
              x["n_positive_source_blocks"])


if __name__=="__main__":
    main()
