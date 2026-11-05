#!/usr/bin/env python3
"""Independent original-Movebank GPS A/B anchor reversal receipts and source summary.

No animal IDs, exact GPS positions or calendar dates are present in either
input. Source original publisher MD5, source positional multiset and SHA256
were checked in the source runs. 12 seeds/3 radii/2 gap thresholds are
dependent diagnostic resamplings, not p-values or biological population
replication. Do not infer social encounters from GPS nearness.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from collections import Counter
from statistics import fmean

ROOT=Path(__file__).resolve().parent
SPEC={
'turkey':{
  'reverse':'a5f61ffd8d34b2ac267fdf3f7d49eea508adafc690a306c9c8adbb2a1f985b5e',
  'old':'c3a4c74160f79f58ed44ef0a81fda6a2c23b39a272aa522812d115729fc9aedb',
  'fixes':435214,'doi':'10.5441/001/1.671',
  'counts':{2019:{900:(112,112,112,19),1800:(112,112,112,19)},
            2020:{900:(21,21,21,7),1800:(21,21,21,7)}}},
'black_bear':{
  'reverse':'d7fae22468baf408265d1fe39da31c3688ae1c9ff06c7947ce3a568b4e4a5a37',
  'old':'f13129ab5927ec7085b9b148a14a45f31ed394f829d3bdc06932a49006f415ab',
  'fixes':148394,'doi':'10.5441/001/1.706',
  'counts':{2019:{900:(0,0,0,0),1800:(0,0,0,0)},
            2020:{900:(6,5,5,4),1800:(6,8,6,4)}}},
'white_tailed_deer':{
  'reverse':'d7066327a4329cae149ae85b3f57013e72fc81a6b6e65b8a47af4d0c932fe7d6',
  'old':'84d4fd9a9c03663b7fecdd733e1d826d78ab7f66260d33230bbf1bcc7d7752f6',
  'fixes':371080,'doi':'10.5441/001/1.718',
  'counts':{2019:{900:(55,55,55,11),1800:(55,55,55,11)},
            2020:{900:(205,205,205,21),1800:(205,205,205,21)}}}}
DIRECTIONS=('original_A_to_B','reversed_B_to_A')
GAPS=(900,1800)
RADII=(.5,1.,2.)
SEEDS=tuple(range(12))
FIELDS=('same','previous_day','next_day','adjacent_day_reference','same_minus_adjacent')
EPS=2e-10

def close(a,b):
    return math.isclose(a,b,abs_tol=EPS,rel_tol=1e-10)

def from_path(directory,source,kind):
    root=Path(directory)
    if kind=='old':
        paths=[root/(source+'_day_shift_control_20261021.json'),
            root/('DAY_SHIFT_PRESERVED_TRAJECTORY_'+source.upper()+'_2026_10_21.json')]
    else:
        paths=[root/(source+'_day_shift_two_anchors_20261021.json'),
            root/('DAY_SHIFT_DUAL_ANCHOR_'+source.upper()+'_2026_10_21.json')]
    existing=[p for p in paths if p.exists()]
    if not existing:
        raise AssertionError('Missing original-source GPS aggregate')
    if len(existing)==2 and existing[0].read_bytes()!=existing[1].read_bytes():
        raise AssertionError('Published aggregate content differs from staged original')
    payload=existing[-1].read_bytes()
    if hashlib.sha256(payload).hexdigest()!=SPEC[source][kind]:
        raise AssertionError('Original-source complete analysis SHA256 mismatch')
    return json.loads(payload)

def sign(values):
    c=Counter(1 if x>1e-12 else -1 if x<-1e-12 else 0 for x in values)
    return {'positive':c[1],'negative':c[-1],'near_zero':c[0]}

def validate(old_dir=ROOT,reverse_dir=ROOT):
    output={'schema_version':1,'as_of':'2026-10-21',
       'status':'POST_INSPECTION_ORIGINAL_MOVE_BANK_DUAL_ANCHOR_SENSITIVITY',
       'source_sha256':{s:{'original':d['old'],'dual_anchor':d['reverse']}
                        for s,d in SPEC.items()},
       'n_source_documents':0,'n_year_gap_groups':0,'n_estimable_groups':0,
       'n_STOP_groups':0,'n_orientation_seed_radius_rows':0,
       'rows':[],'stops':[],'stability_gates':[],
       'nonclaims':['Original-ID lexicographic source direction is arbitrary',
         'GPS recording <=15/30min within distance radius is NOT a physical encounter',
         'GPS source clock basis, location uncertainty and true local populations are unverified',
         'Source dates, tracking days and dyads are dependent, not randomized population repetitions',
         'Same pair IDs in both anchors do not imply identical A/B fix/date observations',
         'One-day original B path shifts preserve daily path ordering, not all ecological autocorrelation']}
    for source,constants in SPEC.items():
        old=from_path(old_dir,source,'old')
        d=from_path(reverse_dir,source,'reverse')
        if not (d['source']==old['source']==source and d['source_doi']==constants['doi']
                and d['n_original_source_GPS_fixes']==constants['fixes']
                and d['time_tolerances_seconds']==[900,1800]
                and d['radii_km']==[.5,1.,2.] and d['n_seeds']==12
                and d['complete_original_publisher_MD5_pinned_SHA256_verified']
                and d['independent_native_original_GPS_time_position_multiset_verified']
                and not d['native_clock_offset_UTC_verified']
                and not d['GPS_position_accuracy_quantified']
                and not d['biological_local_population_membership_verified']):
            raise AssertionError('Original-source provenance or limits changed')
        originals={x['year']:x for x in old['year_results']}
        news={x['year']:x for x in d['source_year_results']}
        if set(originals)!={2019,2020} or set(news)!={2019,2020}:
            raise AssertionError('Source year coverage incomplete')
        for year in (2019,2020):
            oo={x['max_gap_seconds']:x for x in originals[year]['time_tolerance_results']}
            nn={x['max_abs_original_GPS_time_gap_seconds']:x
                for x in news[year]['time_tolerance_results']}
            if set(oo)!=set(GAPS) or set(nn)!=set(GAPS):
                raise AssertionError('Missing source gap thresholds')
            for tol in GAPS:
                previous,cohort=oo[tol],nn[tol]
                f,r,n,na=constants['counts'][year][tol]
                if ((cohort['n_forward_day_shift_dyads'],
                     cohort['n_reversed_day_shift_dyads'],
                     cohort['n_both_orientation_supported_dyads'],
                     cohort['n_distinct_animals_in_shared_pair_set'])!=(f,r,n,na)):
                    raise AssertionError('Source anchor risk-set masks differ from source receipts')
                if cohort['n_original_same_day_GPS_dyads']!=previous['n_original_same_day_supported_dyads']:
                    raise AssertionError('Original source same-day eligibility changed')
                if f and not close(cohort['fraction_forward_pairs_remaining'],n/f):
                    raise AssertionError('Cross-anchor shared dyad fraction invalid')
                if not f and cohort['fraction_forward_pairs_remaining'] is not None:
                    raise AssertionError('Missing shared dyad fraction coded as zero')
                output['n_year_gap_groups']+=1
                if n<8 or na<3:
                    if (cohort['status']!='STOP_SMALL_DUAL_ANCHOR_COMMON_GPS_SUPPORT'
                            or cohort['orientation_seed_radius_aggregates']):
                        raise AssertionError('Unsupported source cohort incorrectly promoted')
                    output['n_STOP_groups']+=1
                    output['stops'].append({'source':source,'year':year,'time_gap_seconds':tol,
                        'forward_dyads':f,'reverse_dyads':r,'intersection_dyads':n,
                        'status':cohort['status']})
                    continue
                if cohort['status']!='DESCRIPTIVE_DUAL_ANCHOR_SAME_DYADS_ORIGINAL_GPS':
                    raise AssertionError('Valid dual-anchor cohort suppressed')
                samples=cohort['orientation_seed_radius_aggregates']
                index={(x['direction'],x['seed'],x['radius_km']):x for x in samples}
                if len(samples)!=72 or set(index)!={(di,se,ra) for di in DIRECTIONS
                                                     for se in SEEDS for ra in RADII}:
                    raise AssertionError('Missing fixed directional/seed/radius crossproduct')
                output['n_estimable_groups']+=1
                output['n_orientation_seed_radius_rows']+=len(samples)
                if n==f:
                    replay=[{key:value for key,value in x.items() if key!='direction'}
                            for x in samples if x['direction']==DIRECTIONS[0]]
                    if replay!=previous['sampled_geodesic_seed_results']:
                        raise AssertionError('Forward source GPS measurements fail exact replay')
                for di in DIRECTIONS:
                    for se in SEEDS:
                        rows=[index[(di,se,ra)] for ra in sorted(RADII)]
                        baseline_gaps=rows[0]['mean_abs_source_clock_gap_seconds']
                        for ra,row in zip(sorted(RADII),rows):
                            allowed=set(('source_year','tolerance_seconds','radius_km','seed',
                               'n_dyads','n_sampled_pair_dates','n_sampled_fix_triples',
                               'winter','summer','winter_minus_summer',
                               'mean_abs_source_clock_gap_seconds','direction'))
                            if set(row)!=allowed or (row['source_year'],row['tolerance_seconds'],row['radius_km'])!=(year,tol,ra):
                                raise AssertionError('Unexpected original GPS source fields/year')
                            if (row['n_dyads'],row['n_sampled_pair_dates'],row['n_sampled_fix_triples'])!=(n,n*28,n*84):
                                raise AssertionError('Original fixed dyad/date/position denominators changed')
                            if row['mean_abs_source_clock_gap_seconds']!=baseline_gaps:
                                raise AssertionError('Position radius modified source timestamp sampling')
                            for seas in ('winter','summer'):
                                result=row[seas]
                                if set(result)!=set(FIELDS):
                                    raise AssertionError('Unexpected GPS time treatment fields')
                                for k in FIELDS:
                                    if isinstance(result[k],bool) or not isinstance(result[k],(int,float)) or not math.isfinite(result[k]):
                                        raise AssertionError('Invalid source movement statistic')
                                for k in FIELDS[:4]:
                                    if not 0<=result[k]<=1:
                                        raise AssertionError('GPS nearby fraction not in [0,1]')
                                if not close(result['adjacent_day_reference'],
                                      (result['previous_day']+result['next_day'])/2):
                                    raise AssertionError('Same-day reference averaging error')
                                if not close(result['same_minus_adjacent'],
                                      result['same']-result['adjacent_day_reference']):
                                    raise AssertionError('GPS adjacent day L not reconciled')
                                for seconds in row['mean_abs_source_clock_gap_seconds'][seas].values():
                                    if not 0<=seconds<=tol+EPS:
                                        raise AssertionError('Original fix source-clock gap exceeds tolerance')
                            for k in FIELDS:
                                if not close(row['winter_minus_summer'][k],
                                    row['winter'][k]-row['summer'][k]):
                                    raise AssertionError('Seasonal GPS contrast differs')
                        for seas in ('winter','summer'):
                            for key in FIELDS[:4]:
                                vals=[r[seas][key] for r in rows]
                                if any(a>b+EPS for a,b in zip(vals,vals[1:])):
                                    raise AssertionError('Radius increases but GPS nearness decreases')
                for ra in RADII:
                    result={'source':source,'year':year,'time_gap_seconds':tol,'radius_km':ra,
                            'n_shared_original_dyads':n,'directions':[]}
                    for di in DIRECTIONS:
                        x=[index[(di,se,ra)] for se in SEEDS]
                        diff=[r['winter_minus_summer']['same_minus_adjacent'] for r in x]
                        result['directions'].append({
                            'orientation':di,
                            'winter_L':fmean(r['winter']['same_minus_adjacent'] for r in x),
                            'summer_L':fmean(r['summer']['same_minus_adjacent'] for r in x),
                            'delta_L':fmean(diff),
                            'delta_L_signs':sign(diff),
                            'delta_L_range':[min(diff),max(diff)]})
                    result['both_positive_at_least_10_of_12']=all(
                        v['delta_L_signs']['positive']>=10 for v in result['directions'])
                    output['rows'].append(result)
        output['n_source_documents']+=1
    if (output['n_source_documents']!=3 or output['n_year_gap_groups']!=12 or
        output['n_estimable_groups']!=8 or output['n_STOP_groups']!=4 or
        output['n_orientation_seed_radius_rows']!=576 or len(output['rows'])!=24):
        raise AssertionError('Missing original-source/year/gap/radius/orientation rows')
    for source in ('turkey','white_tailed_deer'):
        for year in (2019,2020):
            for tol in GAPS:
                q=[r for r in output['rows'] if
                   (r['source'],r['year'],r['time_gap_seconds'])==(source,year,tol)
                   and r['radius_km'] in (.5,1.)]
                if len(q)!=2:raise AssertionError('Missing predeclared 500m/1km checks')
                output['stability_gates'].append({
                    'source':source,'year':year,'time_gap_seconds':tol,
                    'passes_both_orientations_500m_and_1km':all(
                        r['both_positive_at_least_10_of_12'] for r in q)})
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--old-dir',type=Path,default=ROOT)
    p.add_argument('--reverse-dir',type=Path,default=ROOT)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=validate(args.old_dir,args.reverse_dir)
    content=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:args.output.write_text(content)
    else:print(content)
    print(json.dumps({'status':'PASS_DUAL_ANCHOR_SOURCE_GPS_SYMMETRY',
      'n_verified_documents':result['n_source_documents'],
      'n_source_year_gap_groups':result['n_year_gap_groups'],
      'n_stop':result['n_STOP_groups'],
      'n_orientation_seed_radius_rows':result['n_orientation_seed_radius_rows']}))


if __name__=='__main__':
    main()
