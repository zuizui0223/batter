#!/usr/bin/env python3
"""Independent original-source seasonal-centre and component replication audit.

Consumes ONLY source/year/group aggregated data from a completed original
Movebank GPS full-source MD5/SHA256 and time/position multiset replay.
Checks exact new output SHA256, pre-inspection fixed dyad counts, all seeded
L1/radius statuses, nested component score arithmetic, complete paired-source
date centroids and equivalence to earlier pinned 25/5-km source scores.

Neither GPS identities/positions nor physical animal interactions are exposed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parent
INPUT_SHA256='7b3c21afd96abebf2c447bab9ada37309f8c72a339770a8481e8d2bf15c11ab8'
INPUT='TURKEY_COMPONENT_SEASON_CENTERS_SOURCE_2026_10_22.json'
ORIGINAL='SOURCE_SPATIAL_INFLUENCE_TURKEY_2026_10_22.json'
GROUPS={
    2019:{
        'all_annual_0_to25km':112,'annual_0_to5km':73,
        'annual_5_to10km':5,'annual_10_to25km':34,'annual_5_to25km':39,
        '2019_large_5km_component':53,
        '2019_small_5km_component':20},
    2020:{
        'all_annual_0_to25km':21,'annual_0_to5km':14,
        'annual_5_to10km':2,'annual_10_to25km':5,'annual_5_to25km':7,
        '2020_5km_component':14},
}
TOLS=(900,1800)
RADII=(.5,1.,2.)
DIRECTIONS=('original_A_to_B','reversed_B_to_A')
SEEDS=tuple(range(12))
MAX_KM=math.pi*6371.0+1e-6


def close(x,y):
    return math.isclose(x,y,rel_tol=1e-10,abs_tol=2e-9)


def _numeric(x):
    if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x):
        raise AssertionError('Nonfinite/wrong-type numeric original-source centroid statistic')
    return float(x)


def _dist_positive(x):
    v=_numeric(x)
    if not 0<=v<=MAX_KM:
        raise AssertionError('Spherical source GPS seasonal centroid distance exceeds Earth')
    return v


def _check_center_comparison(x,group_n):
    if x['status']=='NOT_ESTIMABLE_NO_BOTH_SEASON_CENTRES':
        if x['n_pairs_with_both_centres']!=0:
            raise AssertionError('Ineligible source seasonal center counted as observed')
        return
    if x['status']!='DESCRIPTIVE_SOURCE_SEASON_CENTROID_SEPARATION':
        raise AssertionError('Unknown source seasonal center status')
    n=x['n_pairs_with_both_centres']
    if not 0<n<=group_n:
        raise AssertionError('Source seasonal comparison pair count invalid')
    for key in ('winter_distances_km','comparator_distances_km'):
        stats=x[key]
        for s in ('mean','median','min','max'):
            _dist_positive(stats[s])
        if not stats['min']-1e-8<=stats['median']<=stats['max']+1e-8:
            raise AssertionError('Season distance median beyond source min/max')
    d=x['winter_minus_comparator_distance_km']
    for key in ('mean','median','min','max'):
        _numeric(d[key])
    if not close(d['mean'],
                 x['winter_distances_km']['mean']-
                 x['comparator_distances_km']['mean']):
        raise AssertionError('Source seasonal mean distance difference inconsistent')
    for v in ('fraction_pairs_winter_centres_closer','fraction_pairs_winter_centres_farther'):
        if not 0<=_numeric(x[v])<=1:
            raise AssertionError('Season source centroid fraction beyond unit range')
    if x['fraction_pairs_winter_centres_closer']+x['fraction_pairs_winter_centres_farther']>1+1e-10:
        raise AssertionError('Fraction closer + farther > 1')


def _check_sample_seeds(record,n):
    if n==0:
        if record['seed_summaries']:
            raise AssertionError('No source-pairs but positive sampled centroids')
        return
    if record['n_pairs']!=n or record['status']!='DESCRIPTIVE_PAIRED_SOURCE_OBSERVATION_CENTRES':
        raise AssertionError('Source matched-pair seasonal center eligibility changed')
    rows=record['seed_summaries']
    if len(rows)!=12 or {r['seed'] for r in rows}!=set(SEEDS):
        raise AssertionError('Missing/duplicate original seasonal source seeds')
    for row in rows:
        if row['n_pairs']!=n:
            raise AssertionError('Centroid spatial-seed denominator changed')
        for key in ('median_winter_center_distance_km',
                    'median_summer_center_distance_km',
                    'mean_winter_center_distance_km',
                    'mean_summer_center_distance_km'):
            _dist_positive(row[key])
        f=row['fraction_pairs_winter_centers_closer']
        if not 0<=_numeric(f)<=1:
            raise AssertionError('Invalid winter-converged pair fraction')
    if not close(record['median_winter_distance_across_seeds_km'],
                 statistics.median(r['median_winter_center_distance_km'] for r in rows)):
        raise AssertionError('Wrong median sample winter geographic center')
    if not close(record['median_summer_distance_across_seeds_km'],
                 statistics.median(r['median_summer_center_distance_km'] for r in rows)):
        raise AssertionError('Wrong median sample summer geographic center')
    count=sum(r['mean_winter_center_distance_km']<
              r['mean_summer_center_distance_km'] for r in rows)
    if count!=record['n_seeds_winter_mean_center_separation_lower']:
        raise AssertionError('Incorrect seed direction of seasonal source centers')


def _check_L1(table,n):
    if n<8:
        if table:
            raise AssertionError('Source small dyad group L1 estimand promoted despite fixed STOP')
        return
    key={(float(r['radius_km']),r['orientation']):r for r in table}
    if len(table)!=6 or set(key)!={(ra,di) for ra in RADII for di in DIRECTIONS}:
        raise AssertionError('Fixed source component radius/orientation matrix incomplete')
    for r in table:
        if r['n_seed_draws']!=12:
            raise AssertionError('Wrong source-original resampling denominator')
        a=r['winter_minus_summer_L_mean']
        lower=r['winter_minus_summer_L_seed_min']
        upper=r['winter_minus_summer_L_seed_max']
        if not -1<=_numeric(a)<=1 or not lower-1e-10<=a<=upper+1e-10:
            raise AssertionError('GPS source L1 mean lies outside finite seed source range')
        signs=r['seed_signs']
        if set(signs)!={'positive','negative','near_zero'} or sum(signs.values())!=12:
            raise AssertionError('Original source resampling direction counts invalid')


def verify(directory=ROOT, historical_dir=ROOT):
    root=Path(directory)
    raw=(root/INPUT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=INPUT_SHA256:
        raise AssertionError('New source original GPS group aggregate SHA256 receipt changed')
    obj=json.loads(raw)
    if not (obj['source']=='turkey' and obj['original_movebank_DOI']=='10.5441/001/1.671'
            and obj['original_accepted_GPS_fixes']==435214 and obj['n_source_seeds']==12
            and obj['native_clock_tolerances_seconds']==[900,1800]
            and set(obj['nearby_position_radii_km'])==set(RADII)
            and obj['source_original_MD5_and_pinned_SHA256_verified']
            and obj['original_full_source_time_position_multiset_verified']
            and obj['original_prior_L1_results_exactly_replayed']
            and not obj['GPS_location_error_calibrated']
            and not obj['clock_UTC_offset_verified']
            and not obj['biological_population_independence_verified']):
        raise AssertionError('Original-source provenance or intended inference limits changed')
    old=json.loads((Path(historical_dir)/ORIGINAL).read_text())
    years={r['year']:r for r in obj['annual_cohorts']}
    oldyears={r['year']:r for r in old['original_year_results']}
    if set(years)!={2019,2020} or set(oldyears)!={2019,2020}:
        raise AssertionError('Original source years missing')
    n_gr=0;n_radii=0;n_seed_center=0
    concise=[]
    for year in (2019,2020):
        yearrow=years[year]
        expect=GROUPS[year]
        if yearrow['n_original_25km_pairs']!=expect['all_annual_0_to25km']:
            raise AssertionError('Source 25km original cohort differs')
        tset={r['time_tolerance_seconds']:r for r in yearrow['time_tolerance_results']}
        oldset={r['tolerance_seconds']:r for r in oldyears[year]['time_tolerance_rows']}
        if set(tset)!=set(TOLS) or set(oldset)!=set(TOLS):
            raise AssertionError('Missing original GPS source time tolerance')
        for tol in TOLS:
            x=tset[tol]
            if x['n_time_eligible_source_dyads']!=expect['all_annual_0_to25km']:
                raise AssertionError('Source original full dyad availability changed')
            groups={g['name']:g for g in x['geographic_groups']}
            if set(groups)!=set(expect):
                raise AssertionError('One of the predeclared source geographic groups is missing')
            orig={z['threshold_km']:z for z in oldset[tol]['spatial_filters']}
            for name,expected_n in expect.items():
                g=groups[name]
                n=g['n_pairs']
                if n!=expected_n or (n and g['n_source_animals']<2):
                    raise AssertionError('Unexpected subgroup / source sample size')
                _check_L1(g['L1_relative_same_day_gps_proximity'],n)
                _check_sample_seeds(g['paired_source_time_supported_centroid_sensitivity'],n)
                for center in g['full_original_season_center_distances'].values():
                    _check_center_comparison(center,n)
                n_gr+=1
                n_radii+=len(g['L1_relative_same_day_gps_proximity'])
                n_seed_center+=len(g['paired_source_time_supported_centroid_sensitivity']['seed_summaries'])
                for selected_name,threshold in (('all_annual_0_to25km',25),
                                                ('annual_0_to5km',5)):
                    if name != selected_name:
                        continue
                    y=orig[threshold]
                    if g['n_pairs']!=y['n_pairs']:
                        raise AssertionError('Old independent source GPS nested pair count changed')
                    references={(v['radius_km'],v['orientation']):v for v in y['radii']}
                    for new in g['L1_relative_same_day_gps_proximity']:
                        prior=references[(new['radius_km'],new['orientation'])]
                        for field in ('winter_minus_summer_L_mean','winter_minus_summer_L_seed_min',
                                      'winter_minus_summer_L_seed_max'):
                            if not close(new[field],prior[field]):
                                raise AssertionError('Stored old source effect vs new original GPS differ')
                        if new['seed_signs']!=prior['seed_signs']:
                            raise AssertionError('Old/new original source L1 signs do not match')
            if year==2019:
                big,small=groups['2019_large_5km_component'],groups['2019_small_5km_component']
                near=groups['annual_0_to5km']
                if (big['n_pairs'],small['n_pairs'],near['n_pairs'])!=(53,20,73):
                    raise AssertionError('2019 disconnected source components different')
                snear={(u['radius_km'],u['orientation']):u for u in
                       near['L1_relative_same_day_gps_proximity']}
                sbig={(u['radius_km'],u['orientation']):u for u in
                      big['L1_relative_same_day_gps_proximity']}
                ssmall={(u['radius_km'],u['orientation']):u for u in
                        small['L1_relative_same_day_gps_proximity']}
                for k,u in snear.items():
                    weighted=(53*sbig[k]['winter_minus_summer_L_mean']+
                              20*ssmall[k]['winter_minus_summer_L_mean'])/73
                    if not close(u['winter_minus_summer_L_mean'],weighted):
                        raise AssertionError('2019 component weights fail to rebuild original full 5km source')
                for group in (big,small):
                    for u in group['L1_relative_same_day_gps_proximity']:
                        if u['radius_km'] in (.5,1.) and u['seed_signs']['positive']!=12:
                            raise AssertionError('2019 source component sample support not robust')
            else:
                far=groups['annual_10_to25km']
                if far['n_pairs']!=5 or far['L1_relative_same_day_gps_proximity']:
                    raise AssertionError('2020 outer source dyads erroneously treated as independent L1 test')
                both=far['full_original_season_center_distances']['winter_vs_summer']
                if both['n_pairs_with_both_centres']!=5:
                    raise AssertionError('2020 exact source original seasonal centre data missing')
            concise.append({
                'source':'turkey','year':year,'time_tolerance_seconds':tol,
                'groups':[{'name':g['name'],'n_pairs':g['n_pairs'],
                    'n_source_animals':g['n_source_animals'],
                    'winter_summer_center_median_km':[
                        g['full_original_season_center_distances']['winter_vs_summer'].get(
                           'winter_distances_km',{}).get('median'),
                        g['full_original_season_center_distances']['winter_vs_summer'].get(
                           'comparator_distances_km',{}).get('median')],
                    'winter_center_pairs_closer_fraction':
                        g['full_original_season_center_distances']['winter_vs_summer'].get(
                             'fraction_pairs_winter_centres_closer'),
                    'paired_original_fix_n_seeds_winter_mean_centers_closer':
                        g['paired_source_time_supported_centroid_sensitivity'].get(
                             'n_seeds_winter_mean_center_separation_lower'),
                    'jan_feb_n_source_pairs':g['full_original_season_center_distances'][
                        'jan_feb_vs_summer']['n_pairs_with_both_centres'],
                    'dec_only_n_source_pairs':g['full_original_season_center_distances'][
                        'dec_only_vs_summer']['n_pairs_with_both_centres'],
                    'original_GPS_L1_500m':[
                        {'direction':a['orientation'],
                         'delta':a['winter_minus_summer_L_mean'],
                         'positive_draws':a['seed_signs']['positive']}
                        for a in g['L1_relative_same_day_gps_proximity']
                        if a['radius_km']==.5],
                    'paired_original_fix_centers_median_km':[
                        g['paired_source_time_supported_centroid_sensitivity'].get(
                             'median_winter_distance_across_seeds_km'),
                        g['paired_source_time_supported_centroid_sensitivity'].get(
                             'median_summer_distance_across_seeds_km')]}
                    for g in x['geographic_groups']]})
    if n_gr!=26 or n_seed_center!=26*12 or n_radii!=108:
        raise AssertionError('Incomplete source component/time/seed evaluation grid')
    return {'schema_version':1,'as_of':'2026-10-22',
            'status':'PINNED_ORIGINAL_SOURCE_TURKEY_COMPONENT_CENTER_AUDIT',
            'source_GPS_original_DOI':'10.5441/001/1.671',
            'original_source_result_SHA256':INPUT_SHA256,
            'n_year_time_comparisons':len(concise),
            'n_group_time_cells':n_gr,
            'n_L1_radius_orientation_rows':n_radii,
            'n_paired_fix_season_center_seed_rows':n_seed_center,
            'independent_biological_populations_verified':False,
            'original_tag_GPS_accuracy_verified':False,
            'source_comparisons':concise,
            'limits':[
                'This is a second-stage aggregate of pinned original GPS source data, not another original-source replication',
                'The two disconnected components are geographic graph subsets and are not verified independent animal populations',
                'Jan-Feb-Dec source winter is a within-calendar-year category, not a continuous season; Dec alone lacks paired support',
                '2020 annual-centre distant n=5 pairs are not independent replicates and are below n>=8 source L1 scoring gate',
                'GPS position error, source-specific native time clock and ecological resources unverified',
                'No observed physical encounters, synchronized interaction or causal niche partitioning']}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',type=Path,default=ROOT)
    p.add_argument('--old-dir',type=Path,default=ROOT)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=verify(args.source_dir,args.old_dir)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:args.output.write_text(payload,encoding='utf-8')
    else:print(payload)
    print(json.dumps({'status':'PASS_TURKEY_ORIGINAL_SOURCE_COMPONENTS',
      'source_grouptime':result['n_group_time_cells'],
      'L1_rows':result['n_L1_radius_orientation_rows'],
      'center_seed_rows':result['n_paired_fix_season_center_seed_rows']}))

if __name__=='__main__':
    main()
