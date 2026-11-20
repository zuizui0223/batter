"""Ducke source-local, plot-equal fractional-binomial guild predictor.

Use only with separately qualified plot data from original Dryad. Captured
guild fractions are NOT species occupancy, actual feeding or vertical SDM.
All original plot identifiers must be kept out of public result receipts.
"""
import math

RIDGE=0.15
FEATURES={
 "baseline":("elevation_m","design_added_riparian_plot","n_matched_nights"),
 "generic_fruit":("elevation_m","design_added_riparian_plot","n_matched_nights","fruit_all"),
 "food_12":("elevation_m","design_added_riparian_plot","n_matched_nights","fruit_batfood_12"),
 "other_10":("elevation_m","design_added_riparian_plot","n_matched_nights","fruit_other"),
 "insect":("elevation_m","design_added_riparian_plot","n_matched_nights","insect_mass_g"),
 "food_insect":("elevation_m","design_added_riparian_plot","n_matched_nights","fruit_batfood_12","insect_mass_g"),
}
LOG_FIELDS={"fruit_all","fruit_batfood_12","fruit_other","insect_mass_g"}

def _encode(items, names):
    out=[]
    for row in items:
        rr=[]
        for k in names:
            v=row.get(k)
            if k=="design_added_riparian_plot" and type(v) is not bool:
                raise ValueError("STOP_UNKNOWN_DESIGN")
            if type(v) not in (int,float,bool) or not math.isfinite(float(v)):
                raise ValueError("STOP_MISSING_SOURCE_PREDICTOR")
            v=float(v)
            if k in LOG_FIELDS:
                if v<0:raise ValueError("STOP_NEGATIVE_RESOURCE")
                v=math.log1p(v)
            rr.append(v)
        out.append(rr)
    return out

def _standardize(train,test,names):
    a=_encode(train,names);b=_encode(test,names);n=len(a)
    mean=[math.fsum(r[j] for r in a)/n for j in range(len(names))]
    sd=[max(math.sqrt(math.fsum((r[j]-mean[j])**2 for r in a)/n),1e-8)
        for j in range(len(names))]
    return ([[1.0]+[(r[j]-mean[j])/sd[j] for j in range(len(names))] for r in a],
            [[1.0]+[(r[j]-mean[j])/sd[j] for j in range(len(names))] for r in b])

def _logistic(a):
    if a>=0:
        b=math.exp(-min(a,40))
        return 1/(1+b)
    b=math.exp(max(a,-40))
    return b/(1+b)

def _solve(m,v):
    n=len(v);a=[list(m[i])+[v[i]] for i in range(n)]
    for j in range(n):
        k=max(range(j,n),key=lambda i:abs(a[i][j]))
        if abs(a[k][j])<1e-14:raise ValueError("STOP_SINGULAR_MODEL")
        a[k],a[j]=a[j],a[k]
        b=a[j][j]
        for t in range(j,n+1):a[j][t]/=b
        for i in range(j+1,n):
            z=a[i][j]
            for t in range(j,n+1):a[i][t]-=z*a[j][t]
    out=[0.]*n
    for i in range(n-1,-1,-1):
        out[i]=a[i][n]-math.fsum(a[i][j]*out[j] for j in range(i+1,n))
    return out

def _obj(x,y,b):
    n=len(y);k=len(b)
    p=[_logistic(math.fsum(r[j]*b[j] for j in range(k))) for r in x]
    loss=math.fsum(-v*math.log(max(u,1e-14))-(1-v)*math.log(max(1-u,1e-14)) for u,v in zip(p,y))/n
    loss+=RIDGE/2*math.fsum(z*z for z in b[1:])
    g=[math.fsum(r[j]*(u-v) for r,u,v in zip(x,p,y))/n+(RIDGE*b[j] if j else 0.) for j in range(k)]
    h=[[math.fsum(r[i]*r[j]*u*(1-u) for r,u in zip(x,p))/n+(RIDGE if i==j and i else 0.) for j in range(k)] for i in range(k)]
    return loss,g,h

def predict(train,test,names,response="frug"):
    if len(train)<20 or not test:raise ValueError("STOP_TOO_FEW_TRAINING_PLOTS")
    for row in train+test:
        a=row.get("captures");b=row.get(response)
        if type(a) is not int or a<=0 or type(b) is not int or not 0<=b<=a:
            raise ValueError("STOP_UNKNOWN_GUILD_DENOMINATOR")
    x,v=_standardize(train,test,names)
    y=[r[response]/r["captures"] for r in train]
    avg=max(min(math.fsum(y)/len(y),1-1e-6),1e-6)
    b=[math.log(avg/(1-avg))]+[0.]*len(names)
    for _ in range(80):
        loss,g,h=_obj(x,y,b)
        if max(abs(q) for q in g)<1e-10:break
        step=_solve(h,g);scale=1.
        while scale>=1e-7:
            new=[bb-scale*q for bb,q in zip(b,step)]
            if _obj(x,y,new)[0]<=loss+1e-13:
                b=new;break
            scale/=2
        else:raise ValueError("STOP_NEWTON_LINESEARCH")
    else:raise ValueError("STOP_NEWTON_NONCONVERGENCE")
    return [_logistic(math.fsum(a[j]*b[j] for j in range(len(b)))) for a in v]

def _score(test,pred,response):
    s=0.
    for row,p in zip(test,pred):
        y=row[response]/row["captures"]
        p=max(min(p,1-1e-13),1e-13)
        s+=y*math.log(p)+(1-y)*math.log1p(-p)
    return s/len(test)

def grouped_cv(rows,response="frug",heldout="block"):
    data=list(rows)
    if len(data)<40:raise ValueError("STOP_TOO_FEW_SOURCE_PLOTS")
    ids=[r.get("plot") for r in data]
    if len(set(ids))!=len(ids):raise ValueError("STOP_DUPLICATE_PLOT")
    if heldout not in ("plot","block"):raise ValueError("STOP_INVALID_HOLDOUT")
    groups=sorted(set(r[heldout] for r in data))
    if len(groups)<5:raise ValueError("STOP_TOO_FEW_INDEPENDENT_GROUPS")
    result=[]
    for g in groups:
        training=[r for r in data if r[heldout]!=g]
        testing=[r for r in data if r[heldout]==g]
        scores={name:_score(testing,predict(training,testing,fields,response),response) for name,fields in FEATURES.items()}
        result.append({"fold_number":len(result)+1,"n_plots":len(testing),
                       "gains":{k:scores[k]-scores["baseline"] for k in scores if k!="baseline"}})
    keys=[k for k in FEATURES if k!="baseline"]
    return {"status":"EXPLORATORY_SOURCE_LOCAL_CAPTURE_GUILD_ONLY",
            "heldout_unit":heldout,"n_sites":len(data),"n_folds":len(groups),
            "equal_fold_gains":{k:math.fsum(r["gains"][k] for r in result)/len(result) for k in keys},
            "equal_site_gains":{k:math.fsum(r["gains"][k]*r["n_plots"] for r in result)/len(data) for k in keys},
            "positive_folds":{k:sum(r["gains"][k]>0 for r in result) for k in keys},
            "folds_without_identifiers":result if heldout=="block" else [],
            "raw_source_rows_or_coordinates_included":False,
            "empirical_5D_resource_height_gain":None}
