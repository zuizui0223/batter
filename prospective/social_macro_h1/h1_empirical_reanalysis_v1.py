#!/usr/bin/env python3
"""Source-pinned, data-local reanalysis of Lewanzik et al. 2019.

No animal-level file is written to the output directory. Requires numpy,
scipy and artifact_tool. Originally executed 2026-11-19 on the uploaded Dryad
v20190410 XLSX; results are single-study ecological evidence, not a macro test.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t
from artifact_tool import Blob, SpreadsheetFile

SOURCE_SHA256 = 'fbabb5021c613aa7033ad13bc1a357a68700a7d3683ec16ae1bcf4a65e121c86'
EXPECTED_COLUMNS = [
    'response_species','date','location','minutes_after_sunset','playback_no',
    'playback_species','buzz.rate_broadcast','buzz.rate_model',
    'pre_playback_activity','playback_activity','post_playback_activity',
    'playback_minus_pre.playback'
]
GROUPS = ['Myotis','NEV','Pnat','Ppip']
SOURCE_STRUCTURAL_ABSENCE = {('Pnat','Maistaettenweiher_Paehl')}


def load_source(path):
    path=Path(path)
    actual_sha=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_sha!=SOURCE_SHA256:
        raise ValueError('Source SHA256 mismatch: expected pinned original XLSX; observed '+actual_sha)
    book=SpreadsheetFile.import_xlsx(Blob.load(str(path)))
    sheets=book.inspect({'kind':'sheet','include':'id,name'}).ndjson
    sheet_info=json.loads(sheets)
    if not isinstance(sheet_info,dict) or sheet_info.get('range')!='A1:L1441':
        raise ValueError('Unexpected source workbook range/sheets')
    a=book.worksheets.get_item_at(0).get_range('A1:L1441').values
    if a[0]!=EXPECTED_COLUMNS:
        raise ValueError('Unexpected original workbook column schema')
    data=[dict(zip(EXPECTED_COLUMNS,r)) for r in a[1:]]
    if len(data)!=1440 or any(any(v is None for v in row.values()) for row in data):
        raise ValueError('Missing or unexpected original row count')
    return data,actual_sha


def validate_source(rows):
    blocks=defaultdict(dict)
    for r in rows:
        g=r['response_species']
        assert g in GROUPS
        key=(r['location'],int(r['playback_no']))
        assert g not in blocks[key], 'Duplicate group within original 3-minute playback block'
        assert int(r['buzz.rate_broadcast']) in (0,12,24,48,96)
        assert int(r['buzz.rate_model']) in (1,2,3,4,5)
        assert int(r['buzz.rate_model'])=={0:1,12:2,24:3,48:4,96:5}[int(r['buzz.rate_broadcast'])]
        assert abs(float(r['playback_activity'])-float(r['pre_playback_activity'])-float(r['playback_minus_pre.playback']))<1e-10
        blocks[key][g]=r
    assert len(blocks)==360 and all(set(v)==set(GROUPS) for v in blocks.values())
    sites=sorted({r['location'] for r in rows})
    senders=sorted({r['playback_species'] for r in rows})
    assert len(sites)==12 and len(senders)==6
    for site in sites:
        for sender in senders:
            actual={int(v['Myotis']['buzz.rate_broadcast']) for (loc,no),v in blocks.items()
                    if loc==site and v['Myotis']['playback_species']==sender}
            assert actual=={0,12,24,48,96}, 'Lost randomized rate×sender combination'
    for group in GROUPS:
        assert sum(r['response_species']==group for r in rows)==360
    for r in rows:
        pre_by_group=blocks[(r['location'],int(r['playback_no']))]
        r['other_pre_present']=int(any(v['pre_playback_activity']>0 for g,v in pre_by_group.items() if g!=r['response_species']))
    for g,site in SOURCE_STRUCTURAL_ABSENCE:
        subset=[r for r in rows if r['response_species']==g and r['location']==site]
        assert len(subset)==30 and all(r['pre_playback_activity']==0 and r['playback_activity']==0 and r['post_playback_activity']==0 for r in subset)
    eligible_counts={g:sum(r['response_species']==g and (r['pre_playback_activity']>0 or r['playback_activity']>0) for r in rows) for g in GROUPS}
    assert eligible_counts=={'Myotis':250,'NEV':94,'Pnat':110,'Ppip':180}, 'Authors selected sample mismatch'
    return {'rows':len(rows),'original_blocks':len(blocks),'independent_sites':len(sites),
            'response_groups':GROUPS,'caller_types':senders,
            'original_author_filtered_counts':eligible_counts,
            'Pnathusii_absent_lake':'Maistaettenweiher_Paehl',
            'source_has_missing_cells':False,'complete_randomized_sender_buzz_cells':True}


def array_xy(rows,sites,senders,params=None,interaction=True,site_fe=False,quadratic=False):
    if params is None:
        p=np.array([math.log1p(r['pre_playback_activity']) for r in rows],float)
        tm=np.array([r['minutes_after_sunset'] for r in rows],float)
        params={'pmean':float(p.mean()),'pstd':float(p.std()),'tmean':float(tm.mean()),'tstd':float(tm.std())}
    matrix=[]
    fe_sites=sorted({r['location'] for r in rows}) if site_fe else []
    for r in rows:
        p=(math.log1p(r['pre_playback_activity'])-params['pmean'])/(params['pstd'] or 1)
        ti=(r['minutes_after_sunset']-params['tmean'])/(params['tstd'] or 1)
        b=(r['buzz.rate_model']-1)/4
        sender=[int(r['playback_species']==s) for s in senders[1:]]
        row=[1,p,b,ti,r['other_pre_present']]+sender+[b*x for x in sender]
        if interaction:row.append(b*p)
        if site_fe:row +=[int(r['location']==s) for s in fe_sites[1:]]
        if quadratic:row += [b*b]+[b*b*x for x in sender]
        matrix.append(row)
    cols=['intercept','log1p_pre_z','buzz_0to1','time_z','other_pre_present']+[f'sender_{s}' for s in senders[1:]]+[f'buzz_sender_{s}' for s in senders[1:]]
    if interaction:cols+=['buzz_x_log1p_pre_z']
    if site_fe:cols += [f'FE_{s}' for s in fe_sites[1:]]
    if quadratic:cols += ['buzz_sq']+[f'buzz_sq_sender_{s}' for s in senders[1:]]
    return np.asarray(matrix,float),np.asarray([math.log1p(r['playback_activity']) for r in rows],float),cols,params


def cluster_interval(rows, X, resid, beta, col_idx):
    g=sorted({r['location'] for r in rows});n,p=X.shape
    bread=np.linalg.pinv(X.T@X); meat=np.zeros((p,p))
    for site in g:
        ix=[i for i,r in enumerate(rows) if r['location']==site]
        score=X[ix].T@resid[ix]
        meat+=np.outer(score,score)
    cov=bread@meat@bread * len(g)/(len(g)-1)*(n-1)/(n-p)
    se=float(np.sqrt(max(0,cov[col_idx,col_idx])))
    b=float(beta[col_idx]); df=len(g)-1
    q=student_t.ppf(.975,df)
    return {'beta':b,'cluster_se':se,'CI95_t':[b-q*se,b+q*se],
            'p_two_sided_t':float(2*student_t.sf(abs(b/se),df)) if se>0 else None,
            'df':df,'n_lakes':len(g),'n_rows':n,'model_rank':int(np.linalg.matrix_rank(X))}


def analyze_one(rows,sites,senders,quadratic=False,filter_original=False):
    if filter_original:
        rows=[r for r in rows if r['pre_playback_activity']>0 or r['playback_activity']>0]
    X,y,cols,params=array_xy(rows,sites,senders,site_fe=True,quadratic=quadratic)
    coef=np.linalg.lstsq(X,y,rcond=None)[0]
    ci=cluster_interval(rows,X,y-X@coef,coef,cols.index('buzz_x_log1p_pre_z'))
    records=[]
    for test_site in sites:
        tr=[r for r in rows if r['location']!=test_site]
        te=[r for r in rows if r['location']==test_site]
        if not te:continue
        scores=[]
        for active in [False,True]:
            X0,y0,names,p=array_xy(tr,sites,senders,interaction=active,quadratic=quadratic)
            b=np.linalg.lstsq(X0,y0,rcond=None)[0]
            sigma2=float(np.sum((y0-X0@b)**2)/(len(y0)-len(b)))
            Xt,yt,_,_=array_xy(te,sites,senders,params=p,interaction=active,quadratic=quadratic)
            mu=Xt@b
            scores.append(float(np.mean(-.5*np.log(2*math.pi*sigma2)-(yt-mu)**2/(2*sigma2))))
        records.append({'lake':test_site,'n':len(te),'logscore_gain':scores[1]-scores[0]})
    gains=np.array([r['logscore_gain'] for r in records],float)
    pre=np.array([r['pre_playback_activity'] for r in rows],float)
    q25,q75=np.quantile(pre,[.25,.75])
    if q25==q75:
        contrast=None
    else:
        contrast=float(ci['beta']*(np.log1p(q75)-np.log1p(q25))/(params['pstd'] or 1))
    return {'n':len(rows),'n_sites_evaluated':len(records),
            'inferential_interaction':ci,'baseline_q25':float(q25),'baseline_q75':float(q75),
            'q75_minus_q25_cue_moderation_log1p_activity':contrast,
            'external_score_equal_lake_mean':float(gains.mean()),
            'lakes_with_positive_score_gain':int(np.sum(gains>0)),
            'per_lake':records,'sensitivity':{'quadratic_sender':quadratic,'original_author_outcome_filter':filter_original}}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--xlsx',required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    rows,sha=load_source(args.xlsx)
    schema=validate_source(rows)
    sites=sorted({r['location'] for r in rows});senders=sorted({r['playback_species'] for r in rows})
    results={'source_doi':'10.5061/dryad.gp65g2t','source_sha256':sha,
             'status':'EMPIRICAL_SINGLE_STUDY_ONLY',
             'scope':'12 Southern German lakes in 2016; not global phylogenetic macro-evidence',
             'schema':schema,
             'model':'Gaussian log1p(playback_activity); train-only z(log1p(pre)) and z(time); within-source sender×buzz; other-pre-presence; fixed lake effects for CIs; training without lake intercept when predicting a held-out lake; baseline×buzz interaction compared to no-interaction model',
             'scale':'buzz=(buzz.rate_model-1)/4; 0 and 96 buzz treatments are not zero-versus-silence',
             'primary':{},'quadratic_nuisance_sensitivity':{},'authors_outcome_filter_sensitivity':{},
             'limitations':['NEV pooled genera, not species','baseline activity is not randomized competition','lakes not widely separated regions','LOLO fold training sets overlap',
                            'original authors exclusion conditions on Y, so not primary','no directly observed individual memory or food benefit']}
    for group in GROUPS:
        source=[r for r in rows if r['response_species']==group and (group,r['location']) not in SOURCE_STRUCTURAL_ABSENCE]
        results['primary'][group]=analyze_one(source,sites,senders)
        results['quadratic_nuisance_sensitivity'][group]=analyze_one(source,sites,senders,quadratic=True)
        results['authors_outcome_filter_sensitivity'][group]=analyze_one(source,sites,senders,filter_original=True)
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for g in GROUPS:
        a=results['primary'][g];i=a['inferential_interaction'];v=a['external_score_equal_lake_mean']
        print(f'{g}: n={a["n"]} sites={a["n_sites_evaluated"]}, beta={i["beta"]:+.5f}, 95%CI [{i["CI95_t"][0]:+.5f},{i["CI95_t"][1]:+.5f}], delta-LOLO={v:+.6f}, positive sites={a["lakes_with_positive_score_gain"]}')


if __name__=='__main__':
    main()
