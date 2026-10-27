#!/usr/bin/env python3
"""Verify pinned original-source day-shift control and create cohort-only summaries.

This script reads only completed Movebank original-GPS aggregate JSON with
fixed known SHA256 receipts. No positions, exact recording times, original
animal/dyad identities, or raw source files are touched.
Results are descriptive; adjacent-day original tracks are an
autocorrelation-respecting sensitivity, NOT exchangeable biological nulls.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
PINS = {
    'turkey': {
        'sha256': 'c3a4c74160f79f58ed44ef0a81fda6a2c23b39a272aa522812d115729fc9aedb',
        'fixes': 435214, 'doi': '10.5441/001/1.671',
        'counts': {2019: (112, 112, 112, 19, 19),
                   2020: (21, 21, 21, 7, 7)}},
    'black_bear': {
        'sha256': 'f13129ab5927ec7085b9b148a14a45f31ed394f829d3bdc06932a49006f415ab',
        'fixes': 148394, 'doi': '10.5441/001/1.706',
        'counts': {2019: (1, 0, 0, 0, 0),
                   2020: (104, 6, 6, 4, 4)}},
    'white_tailed_deer': {
        'sha256': '84d4fd9a9c03663b7fecdd733e1d826d78ab7f66260d33230bbf1bcc7d7752f6',
        'fixes': 371080, 'doi': '10.5441/001/1.718',
        'counts': {2019: (55, 55, 55, 11, 11),
                   2020: (205, 205, 205, 21, 21)}},
}
TOLERANCES = (900, 1800)
RADII = (0.5, 1., 2.)
SEEDS = tuple(range(12))
METRICS = ('same', 'previous_day', 'next_day',
           'adjacent_day_reference', 'same_minus_adjacent')
EPS = 2e-10


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-10, abs_tol=EPS)


def numeric(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise AssertionError('Nonfinite/non-numeric source metric')
    return v


def sign_counts(values):
    c=Counter(1 if x>1e-12 else -1 if x< -1e-12 else 0 for x in values)
    return {'positive':c[1], 'negative':c[-1], 'near_zero':c[0]}


def _source_path(directory, source):
    root=Path(directory)
    staging=root/(source+'_day_shift_control_20261021.json')
    published=root/('DAY_SHIFT_PRESERVED_TRAJECTORY_'+source.upper()+'_2026_10_21.json')
    located=[p for p in (staging,published) if p.exists()]
    if not located:
        raise AssertionError('Missing source original-public-GPS output')
    if len(located)==2 and located[0].read_bytes()!=located[1].read_bytes():
        raise AssertionError('Published original aggregate differs from verified staged source')
    return located[-1]


def _verify_row(row, source, year, tol, radius, n):
    exact_keys={'source_year', 'tolerance_seconds','radius_km','seed',
        'n_dyads','n_sampled_pair_dates','n_sampled_fix_triples',
        'winter','summer','winter_minus_summer',
        'mean_abs_source_clock_gap_seconds'}
    if set(row)!=exact_keys:
        raise AssertionError('Unexpected source row keys / potential track-level leakage')
    if ((row['source_year'],row['tolerance_seconds'],row['radius_km'])
            !=(year,tol,radius)):
        raise AssertionError('Unexpected source time/year/radius')
    if row['seed'] not in SEEDS or row['n_dyads']!=n:
        raise AssertionError('Seed or cohort size changed')
    if (row['n_sampled_pair_dates']!=n*28 or
            row['n_sampled_fix_triples']!=n*84):
        raise AssertionError('Unequal source dyad/day/time paired observation denominators')
    gaps=row['mean_abs_source_clock_gap_seconds']
    if set(gaps)!={'winter','summer'}:
        raise AssertionError('Unexpected source season clock-gap records')
    for season in ('winter','summer'):
        x=row[season]
        if set(x)!=set(METRICS):
            raise AssertionError('Unexpected source-response components')
        for k in METRICS:
            numeric(x[k])
        for k in ('same','previous_day','next_day','adjacent_day_reference'):
            if not 0<=x[k]<=1:
                raise AssertionError('GPS nearby fraction outside [0,1]')
        if not close(x['adjacent_day_reference'],
                     (x['previous_day']+x['next_day'])/2):
            raise AssertionError('Adjacent-day reference did not average both original tracks')
        if not close(x['same_minus_adjacent'],x['same']-x['adjacent_day_reference']):
            raise AssertionError('Preserved-day temporal contrast not exactly additive')
        if set(gaps[season]) != {'same','previous_day','next_day'}:
            raise AssertionError('Unexpected source time-gap component')
        for metric, val in gaps[season].items():
            if not 0<=numeric(val)<=tol+EPS:
                raise AssertionError('Source original GPS match time gap exceeds fixed tolerance')
    if set(row['winter_minus_summer'])!=set(METRICS):
        raise AssertionError('Missing/extra seasonal contrast metric')
    for k in METRICS:
        if not close(row['winter'][k]-row['summer'][k],
                     row['winter_minus_summer'][k]):
            raise AssertionError('Source winter-summer contrast does not reconcile')


def _summarize_group(source,year,tol,expected,rows):
    indexed={(r['seed'],float(r['radius_km'])):r for r in rows}
    if len(rows)!=len(SEEDS)*len(RADII) or set(indexed)!={
            (s,r) for s in SEEDS for r in RADII}:
        raise AssertionError('Incomplete source seed x radius factorial')
    for seed in SEEDS:
        baseline_gaps=None
        for radius in RADII:
            row=indexed[(seed,radius)]
            _verify_row(row,source,year,tol,radius,expected)
            gap=row['mean_abs_source_clock_gap_seconds']
            if baseline_gaps is None:
                baseline_gaps=gap
            elif baseline_gaps!=gap:
                raise AssertionError('Distance cutoff changed fixed GPS observation schedule')
        for season in ('winter','summer'):
            for key in ('same','previous_day','next_day','adjacent_day_reference'):
                values=[indexed[(seed,r)][season][key] for r in sorted(RADII)]
                if any(a > b + EPS for a,b in zip(values,values[1:])):
                    raise AssertionError('GPS nearness decreases with radius on the same fix sample')
    reports=[]
    for radius in RADII:
        slices=[indexed[(seed,radius)] for seed in SEEDS]
        def avg(s,k):
            return statistics.fmean(x[s][k] for x in slices)
        season_means={season:{k:avg(season,k) for k in METRICS}
                      for season in ('winter','summer')}
        signed_diff=[x['winter_minus_summer']['same_minus_adjacent']
                     for x in slices]
        if not close(season_means['winter']['same_minus_adjacent']-
                     season_means['summer']['same_minus_adjacent'],
                     statistics.fmean(signed_diff)):
            raise AssertionError('Source retained values do not reconcile season effects')
        reports.append({
            'source':source,'year':year,'time_gap_seconds':tol,
            'radius_km':radius,'source_dyads':expected,
            'seed_count':len(SEEDS),
            'winter':season_means['winter'], 'summer':season_means['summer'],
            'winter_minus_summer':{
                k:avg('winter',k)-avg('summer',k) for k in METRICS},
            'sampled_mean_abs_clock_gap_seconds':{
                season:{method: statistics.fmean(x['mean_abs_source_clock_gap_seconds'][season][method]
                                                for x in slices)
                        for method in ('same','previous_day','next_day')}
                for season in ('winter','summer')},
            'delta_day_reference_sign_counts':sign_counts(signed_diff),
            'delta_day_reference_seed_min':min(signed_diff),
            'delta_day_reference_seed_max':max(signed_diff),
        })
    return reports


def validate(directory):
    report={
        'schema_version':1,'as_of':'2026-10-21',
        'status':'POST_INSPECTION_SOURCE_DAY_SHIFT_AGGREGATE_AUDIT',
        'source_git_run':'https://github.com/zuizui0223/batter/actions/runs/39595138997',
        'source_pinned_SHA256':{key:value['sha256'] for key,value in PINS.items()},
        'source_date_lags':[-1,0,1],
        'radii_km':list(RADII),
        'timestamp_tolerances_seconds':list(TOLERANCES),
        'n_seeds':len(SEEDS),
        'n_source_documents':0,
        'n_source_year_tolerance_groups':0,
        'n_estimable_source_year_tolerance_groups':0,
        'n_stop_source_year_tolerance_groups':0,
        'n_scenario_seed_radius_rows':0,
        'rows':[],
        'stop_groups':[],
        'limitations':[
            'Controls preserve original previous/next-day GPS path ordering but not all environmental or between-day movement autocorrelation',
            'Focal A animal was chosen by lexicographic original ID; reversing A/B is an outstanding sensitivity',
            'Native GPS source clock basis, location error, same-population membership unresolved',
            'Tracks/dyads/years and 12 seeded selections are dependent and not biological replications',
            'A within-15/30min GPS nearby match is not a physical encounter; no social, resource or causal inference',
            'This is a post-inspection sensitivity using a control fixed after viewing original GPS O/N/D outcomes',
        ],
    }
    for source,spec in PINS.items():
        path=_source_path(directory,source)
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=spec['sha256']:
            raise AssertionError('Published source original GPS aggregate SHA256 changed')
        original=json.loads(content)
        if (original['source']!=source or original['doi']!=spec['doi']
                or original['n_original_GPS_fixes']!=spec['fixes']
                or original['status']!='POST_INSPECTION_ADJACENT_SOURCE_DAY_ORIGINAL_GPS_CONTROL'
                or original['radii_km']!=list(RADII)
                or original['time_tolerances_seconds']!=list(TOLERANCES)
                or original['n_seeds']!=len(SEEDS)
                or original['lagged_B_source_days']!=[-1,0,1]
                or not original['require_same_focal_A_GPS_fix_for_all_three_source_days']
                or not original['complete_original_publisher_MD5_and_pinned_SHA256_verified']
                or not original['full_original_time_position_QC_multiset_verified']
                or original['GPS_location_error_quantified']
                or original['source_clock_absolute_UTC_offset_verified']
                or original['biological_population_membership_verified']):
            raise AssertionError('Original source provenance or frozen design was changed')
        year_groups={r['year']:r for r in original['year_results']}
        if set(year_groups)!={2019,2020}:
            raise AssertionError('Missing source year')
        for year,body in sorted(year_groups.items()):
            expected=spec['counts'][year]
            if body['n_old_geographic_pairs']!=expected[0]:
                raise AssertionError('Old source 25km pair risk set changed')
            selected={r['max_gap_seconds']:r for r in body['time_tolerance_results']}
            if set(selected)!=set(TOLERANCES):
                raise AssertionError('Missing source timestamp tolerance')
            report['n_source_year_tolerance_groups']+=len(TOLERANCES)
            for gap,expected_dyads,animals in zip(TOLERANCES,expected[1:3],expected[3:5]):
                row=selected[gap]
                if row['n_adjacent_day_supported_dyads']!=expected_dyads:
                    raise AssertionError('Matched-source adjacent day pair count changed')
                if row['n_source_animals_with_supported_pairs']!=animals:
                    raise AssertionError('Supported source animal count changed')
                if row['n_original_same_day_supported_dyads']<expected_dyads:
                    raise AssertionError('Adjacent-day controls have more dyads than original')
                if row['n_original_same_day_supported_dyads']!=(
                    {'turkey':{2019:112,2020:21},
                     'black_bear':{2019:0,2020:38 if gap==900 else 47},
                     'white_tailed_deer':{2019:55,2020:205}}[source][year]):
                    raise AssertionError('Original source fix-time denominator changed')
                if row['n_original_same_day_supported_dyads']:
                    if not close(row['fraction_matched_pairs_with_adjacent_day_support'],
                                 expected_dyads/row['n_original_same_day_supported_dyads']):
                        raise AssertionError('Supported fraction mismatch')
                elif row['fraction_matched_pairs_with_adjacent_day_support'] is not None:
                    raise AssertionError('No temporal support must have null, not zero')
                expected_status=('DESCRIPTIVE_ADJACENT_DAY_ORIGINAL_GPS_CONTROL'
                                 if expected_dyads>=8 and animals>=3
                                 else 'STOP_INSUFFICIENT_DAY_SHIFT_TEMPORAL_OPPORTUNITY')
                if row['status']!=expected_status:
                    raise AssertionError('Frozen eligibility status changed')
                if expected_status.startswith('STOP_'):
                    if row['sampled_geodesic_seed_results']:
                        raise AssertionError('Unsupported source sampled as zero instead of STOP')
                    report['n_stop_source_year_tolerance_groups']+=1
                    report['stop_groups'].append({
                        'source':source,'year':year,'time_gap_seconds':gap,
                        'n_original_same_day_supported_dyads':row['n_original_same_day_supported_dyads'],
                        'n_adjacent_day_supported_dyads':expected_dyads,
                        'status':expected_status})
                else:
                    result=_summarize_group(source,year,gap,expected_dyads,
                                            row['sampled_geodesic_seed_results'])
                    report['rows'].extend(result)
                    report['n_estimable_source_year_tolerance_groups']+=1
                    report['n_scenario_seed_radius_rows']+=len(row['sampled_geodesic_seed_results'])
        report['n_source_documents']+=1
    if (report['n_source_documents']!=3
            or report['n_source_year_tolerance_groups']!=12
            or report['n_estimable_source_year_tolerance_groups']!=8
            or report['n_stop_source_year_tolerance_groups']!=4
            or report['n_scenario_seed_radius_rows']!=288
            or len(report['rows'])!=24):
        raise AssertionError('Source study/time/seed/radius scope incomplete')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir',type=Path,default=ROOT)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    out=validate(args.input_dir)
    content=json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:args.output.write_text(content)
    else:print(content)
    print(json.dumps({'status':'PASS_PREVIOUS_NEXT_SOURCE_DAY_GPS_CONTROL',
                      'source_files':out['n_source_documents'],
                      'source_year_tolerances':out['n_source_year_tolerance_groups'],
                      'estimable_groups':out['n_estimable_source_year_tolerance_groups'],
                      'stop_groups':out['n_stop_source_year_tolerance_groups'],
                      'seed_radius_rows':out['n_scenario_seed_radius_rows']}))


if __name__=='__main__':
    main()
