"""Source-verified, post-inspection effort and animal-influence diagnostics."""
import sys, json, hashlib, random, statistics, tempfile, time, math
from pathlib import Path
from collections import defaultdict,Counter
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import same_clock_bin_couse_v1 as clock
import subhour_geodesic_proximity_v1 as near
import turkey_monthly_core_separation_v1 as monthly
import turkey_component_season_centers_v1 as geo

# Bounded HTTP ranges repair interrupted transport; original receipt checks remain.
_original_download=clock.old._download
def ranged_download(entry,folder):
    path=folder/(entry['uuid']+'.original')
    if entry['size']>4*1024*1024 and not path.exists():
        step=4*1024*1024
        def part(start):
            end=min(start+step,entry['size'])-1
            for attempt in range(3):
                try:
                    req=Request(entry['url'],headers={'Range':f'bytes={start}-{end}','User-Agent':'source-verified-ecology/1.0'})
                    with urlopen(req,timeout=45) as r:
                        if r.status!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{entry["size"]}':
                            raise ValueError('Range response mismatch')
                        b=r.read()
                    if len(b)!=end-start+1:raise ValueError('Truncated range')
                    return b
                except Exception:
                    if attempt==2:raise
                    time.sleep(attempt+1)
        with ThreadPoolExecutor(max_workers=6) as pool,path.open('wb') as f:
            for i,b in enumerate(pool.map(part,range(0,entry['size'],step))):
                f.write(b)
                if i%8==0:print('Verified transport ranges:',i+1,flush=True)
    return _original_download(entry,folder)

DISTANCE_DIFFERENCES=[]
def mean_distance(pairs,centers):
    vals=[]
    for a,b in pairs:
        u,v=centers[a],centers[b]
        old=monthly._distance(u,v)
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        stable=6371*math.atan2(math.hypot(*cross),math.fsum(x*y for x,y in zip(u,v)))
        DISTANCE_DIFFERENCES.append(abs(old-stable))
        assert abs(old-stable)<.0001, 'Great-circle numerical diagnostic exceeds 0.1 m'
        vals.append(old)
    return statistics.fmean(vals)


def summarize(values):
    return dict(n=len(values),positive=sum(v>0 for v in values),minimum=min(values),
                mean=statistics.fmean(values),maximum=max(values))

def group_diagnostics(year,members,pairs,daily):
    members=sorted(members); pairs=sorted(pairs)
    dates={m:sorted(set.intersection(*(set(daily[(year,m,a)]) for a in members)))
           for m in (2,3,4,6,7)}
    if any(len(v)<7 for v in dates.values()):
        return {'status':'STOP_COMMON_DAY_SUPPORT','common_day_counts':{str(m):len(d) for m,d in dates.items()}}
    rows=[]
    for seed in (None,*range(24)):
        centers={}
        for m,ds in dates.items():
            chosen=ds if seed is None else sorted(random.Random(20261105+10000*year+100*m+seed).sample(ds,7))
            centers[m]={a:geo._unit_season_mean([daily[(year,m,a)][d] for d in chosen]) for a in members}
        contrasts={}
        for label,months in [('apr_minus_feb',(4,)),('mar_minus_feb',(3,)),('jun_jul_minus_feb',(6,7))]:
            def contrast(ps):
                return statistics.fmean(mean_distance(ps,centers[m]) for m in months)-mean_distance(ps,centers[2])
            loo=[contrast([p for p in pairs if a not in p]) for a in members]
            contrasts[label]={'delta_km':contrast(pairs),'leave_one_animal':summarize(loo)}
        rows.append({'sample':'all_common_days' if seed is None else seed,'contrasts':contrasts})
    return {'status':'COMPLETED_SOURCE_DIAGNOSTIC','n_animals':len(members),'n_pairs':len(pairs),
            'common_day_counts':{str(m):len(d) for m,d in dates.items()},'full_days':rows[0],
            'balanced_draws':rows[1:],
            'balanced_summary':{label:{'whole_group':summarize([r['contrasts'][label]['delta_km'] for r in rows[1:]]),
               'worst_animal_deletion':summarize([r['contrasts'][label]['leave_one_animal']['minimum'] for r in rows[1:]])}
                for label in rows[0]['contrasts']}}

def run(cache,output):
    from contextlib import nullcontext
    cache=Path(cache)
    output=Path(output)
    cache.mkdir(parents=True,exist_ok=True)
    output.mkdir(parents=True,exist_ok=True)
    DISTANCE_DIFFERENCES.clear()
    clock.old._download=ranged_download
    with nullcontext(cache) as tmp:
        print('Fetching original source and checking pinned receipts',flush=True)
        _,events,pinned=clock.get_original('turkey',Path(tmp))
        byday=near._native_positions('turkey',Path(tmp),events)
        print('Source checks passed; replaying original monthly result',flush=True)
        replay=monthly.analyze_original(events,byday,pinned)
        (output/'TURKEY_CORE_EFFORT_ORIGINAL_REPLAY.json').write_text(json.dumps(replay,indent=2),encoding='utf-8')
        expected=json.loads((ROOT/'TURKEY_MONTHLY_CORE_SEPARATION_SOURCE_2026_10_28.json').read_text(encoding='utf-8'))
        differences=[]
        def compare(a,b,path=''):
            if isinstance(a,dict):
                assert a.keys()==b.keys(),path
                for k in a:compare(a[k],b[k],path+'/'+k)
            elif isinstance(a,list):
                assert len(a)==len(b),path
                for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
            elif isinstance(a,float) and isinstance(b,(float,int)):
                if a!=b:differences.append({'path':path,'absolute_difference':abs(a-b)})
                assert abs(a-b)<=1e-4 and round(a,3)==round(b,3), (path,a,b)
            else:assert a==b,(path,a,b)
        compare(replay,expected)
        print('Baseline reconciliation:',json.dumps({'exact':replay==expected,'numeric_differences':len(differences),'maximum_absolute_difference':max((r['absolute_difference'] for r in differences),default=0)}),flush=True)
        groups,_=monthly._pair_sets(events,byday)
        refs=list(clock.old._csv_rows(Path(tmp)/'2c9dc3a2-826e-48dc-9d6d-513292b49cf6.original','reference.csv'))
        lookup=defaultdict(list)
        for r in refs:lookup[r.get('animal-id','').strip()].append(r)
        covariates=[]
        for y in (2019,2020):
            for label,members in [('whole_eligible_cohort',groups[y]['animals'])]+[(f'component_{i+1}',a) for i,(a,ps) in enumerate(groups[y]['components'])]:
                counts={}
                for col in ('animal-sex','animal-life-stage'):
                    vals=[]
                    for a in members:
                        found={r.get(col,'').strip() for r in lookup[a] if r.get(col,'').strip()}
                        vals.append(next(iter(found)) if len(found)==1 else 'missing_or_conflicting')
                    counts[col]=dict(Counter(vals))
                covariates.append({'year':y,'group':label,'n_animals':len(members),'metadata':counts})
        (output/'TURKEY_CORE_EFFORT_COVARIATES_2026_11_05.json').write_text(json.dumps({'status':'ORIGINAL_REFERENCE_COHORT_JOIN','rows':covariates,'limit':'Published metadata, not reproductive state or independently validated demographics'},indent=2),encoding='utf-8')
        points=defaultdict(list)
        for f in events:
            if f.month in (2,3,4,6,7):points[(f.year,f.month,f.animal,f.day)].append(geo._xyz(f.lat,f.lon))
        daily=defaultdict(dict)
        for (y,m,a,d),ps in points.items():daily[(y,m,a)][d]=geo._unit_day_mean(ps)
        del points
        results={}
        core=groups[2020]['core']
        results['2020_core']=group_diagnostics(2020,core,list(combinations(sorted(core),2)),daily)
        for i,(members,edges) in enumerate(groups[2019]['components']):
            results[f'2019_component_{i+1}_original_edges']=group_diagnostics(2019,members,edges,daily)
            results[f'2019_component_{i+1}_all_pairs']=group_diagnostics(2019,members,list(combinations(sorted(members),2)),daily)
        months={r['month']: {g['group_label']:g for g in r['group_centroid_pair_distances']} for r in replay['month_results'][1]['months']}
        decompositions=[]
        for later in (3,4,6,7):
            def delta(label):return months[later][label]['distance_km']['mean']-months[2][label]['distance_km']['mean']
            total=delta('all_25km_source_pairs');ic=6/21*delta('2020_annual5_isolate_vs_core');cc=15/21*delta('2020_six_member_annual5_core')
            assert abs(total-ic-cc)<1e-10
            decompositions.append({'from_month':2,'to_month':later,'total_delta_km':total,'isolate_core_term_km':ic,'core_core_term_km':cc,'isolate_pair_share_of_total':ic/total if total else None})
        out={'source_commit':'45017e0f7f35fd79468db07f16ee162816efc0d6','original_monthly_replay_exact':replay==expected,'baseline_numeric_differences':differences,'baseline_tolerance_km':1e-4,'baseline_equal_at_reported_precision_km':.001,'independent_atan2_max_pair_distance_difference_km':max(DISTANCE_DIFFERENCES,default=0),
             'original_accepted_gps_fixes':len(events),'contract_sha256':hashlib.sha256((ROOT/'TURKEY_CORE_EFFORT_DESIGN_2026_11_05.md').read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
             'status':'POST_INSPECTION_SAME_SOURCE_DIAGNOSTICS_NOT_INDEPENDENT_VALIDATION',
             'groups':results,'full_month_exact_mean_decomposition':decompositions,
             'limitations':['No independent holdout or biological p-value','Subsamples and animals/dyads dependent','Annual-group membership selected from full observed year','Monthly centers are not simultaneous locations','Fix availability and habitat/sex/age confounds remain']}
        (output/'TURKEY_CORE_EFFORT_RESULT_2026_11_05.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf-8')
        print(json.dumps({'status':out['status'],'baseline_exact':replay==expected,'groups':{k:v.get('balanced_summary') for k,v in results.items()},'decomposition':decompositions,'covariates':covariates}),flush=True)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--cache-dir',type=Path)
    args=parser.parse_args()
    try:
        if args.cache_dir:
            run(args.cache_dir,args.output_dir)
        else:
            with tempfile.TemporaryDirectory(prefix='turkey-source-') as folder:
                run(Path(folder),args.output_dir)
    finally:
        clock.old._download=_original_download

