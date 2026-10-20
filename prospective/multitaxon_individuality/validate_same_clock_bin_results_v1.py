#!/usr/bin/env python3
"""Independently reconcile source-verified coarse clock-bin X/T results.

Read only aggregate outputs, never GPS positions, animal identifiers or dates.
Each byte receipt was obtained in a completed original-file-GPS Actions run.
T denotes SAME SOURCE-CLOCK BIN GEOGRAPHIC CELL, NOT physical encounter.
All seed/grid results are descriptive, dependent sensitivity settings.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

SOURCES={
    'turkey':('422d52a1665ede8c31bd35b9828aa0122dc0307c92c935919f475f65e952e1bf',
              435214,'10.5441/001/1.671',{2019:(112,112,112),2020:(21,21,21)}),
    'black_bear':('a7876dddbca670235bc310f4b0bc2577070ae0abd592245b4508e90bcd3ec931',
              148394,'10.5441/001/1.706',{2019:(1,0,1),2020:(104,61,61)}),
    'white_tailed_deer':('fecfed6bc684bddc3feea88e83cfa413ee66ecc646503c4652a5bef8207a8875',
              371080,'10.5441/001/1.718',{2019:(55,55,55),2020:(205,205,205)}),
}
GRIDS={(5.,0.,0.),(1.,0.,0.),(10.,0.,0.),(5.,.5,.5)}
TOP_KEYS={'as_of','grids','hour_bin_widths','limitations','n_seeds','n_valid_original_GPS_fixes',
    'original_position_and_timestamp_multisets_exact','original_source_full_MD5_SHA256_verified',
    'reference_population_label_verified','results','schema_version','source',
    'source_clock_offset_UTC_verified','source_doi','status'}
ROW_KEYS={'clock_bin_hours','fraction_geographic_dyads_with_clock_support',
          'grid_seed_aggregates','n_joint_clock_support_dyads',
          'n_original_geographic_support_dyads','status','year'}
DRAW_KEYS={'clock_bin_hours','grid_km','mean_shared_clock_bins_per_pair_date',
           'n_pair_dates','n_supported_dyads','origin_x_fraction',
           'origin_y_fraction','seed','source_year','summer',
           'summer_positive_D_dyad_fraction','winter',
           'winter_minus_summer','winter_positive_D_dyad_fraction'}
METRIC_KEYS={'X','T','N','D'}
EPS=2e-9

def close(a,b):
    return math.isclose(a,b,abs_tol=EPS,rel_tol=1e-10)

def sign_counts(values):
    count=Counter(1 if v>1e-12 else -1 if v< -1e-12 else 0 for v in values)
    return {'positive':count[1],'negative':count[-1],'zero':count[0]}

def _validate_draw(row,year,width,npairs):
    if set(row)!=DRAW_KEYS or row['source_year']!=year or row['clock_bin_hours']!=width:
        raise AssertionError('Unexpected sample-field schema or time coordinate')
    if row['n_supported_dyads']!=npairs or row['n_pair_dates']!=npairs*28:
        raise AssertionError('Pair/date sampling denominators not fixed')
    bins=row['mean_shared_clock_bins_per_pair_date']
    if not 2-EPS<=bins<=24/width+EPS:
        raise AssertionError('Invalid number of matched source-clock bins')
    if any(not 0<=row[name]<=1 for name in
           ('winter_positive_D_dyad_fraction','summer_positive_D_dyad_fraction')):
        raise AssertionError('Positive-D dyad count outside valid range')
    for season in ('winter','summer'):
        val=row[season]
        if set(val)!=METRIC_KEYS:
            raise AssertionError('Unexpected seasonal metric fields')
        x,t,n,d=(val[k] for k in ('X','T','N','D'))
        if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (x,t,n,d)):
            raise AssertionError('Nonfinite seasonal statistic')
        if not (0<=t<=x+EPS and 0<=n<=x+EPS and x<=1+EPS):
            raise AssertionError('T or conditional time-label null exceeds X')
        if not close(t-n,d):
            raise AssertionError('Conditional clock alignment does not reconcile')
    if set(row['winter_minus_summer'])!=METRIC_KEYS:
        raise AssertionError('Unexpected seasonal delta fields')
    for k in METRIC_KEYS:
        if not close(row['winter'][k]-row['summer'][k],
                     row['winter_minus_summer'][k]):
            raise AssertionError('Seasonal difference does not reconcile')

def _validate_source(path,source):
    expected_sha,fixes,doi,paircounts=SOURCES[source]
    content=Path(path).read_bytes()
    if hashlib.sha256(content).hexdigest()!=expected_sha:
        raise AssertionError('Source original-GPS output SHA256 does not match source CI receipt')
    doc=json.loads(content)
    if set(doc)!=TOP_KEYS or doc['source']!=source or doc['source_doi']!=doi:
        raise AssertionError('Source identity/allowed aggregate schema changed')
    if doc['schema_version']!=1 or doc['n_seeds']!=12 or doc['n_valid_original_GPS_fixes']!=fixes:
        raise AssertionError('Original fixed analysis scope changed')
    if doc['hour_bin_widths']!=[6,3] or {tuple(g) for g in doc['grids']}!=GRIDS:
        raise AssertionError('Declared source-clock or spatial grids changed')
    if not (doc['original_source_full_MD5_SHA256_verified'] and
            doc['original_position_and_timestamp_multisets_exact']):
        raise AssertionError('Original-file source/clock join was not independently verified')
    if doc['reference_population_label_verified'] or doc['source_clock_offset_UTC_verified']:
        raise AssertionError('Unsupported population or absolute time inference')
    cohorts={(r['year'],r['clock_bin_hours']):r for r in doc['results']}
    if set(cohorts)!={(year,width) for year in paircounts for width in (6,3)}:
        raise AssertionError('Missing original-source year or clock-width')
    aggregate=[]
    for (year,width),row in sorted(cohorts.items()):
        if set(row)!=ROW_KEYS:
            raise AssertionError('Unexpected source-year fields')
        expected_all,expected_6,expected_3=paircounts[year]
        expected_clock=expected_6 if width==6 else expected_3
        n=row['n_joint_clock_support_dyads']
        if row['n_original_geographic_support_dyads']!=expected_all or n!=expected_clock:
            raise AssertionError('Date/time support changed relative to original source receipt')
        if not close(row['fraction_geographic_dyads_with_clock_support'],
                     n/expected_all):
            raise AssertionError('Clock support attrition fraction not reproduced')
        if n<2:
            if row['status']!='NOT_ESTIMABLE_FEWER_THAN_TWO_CLOCK_SUPPORTED_DYADS' or row['grid_seed_aggregates']:
                raise AssertionError('Low support was misreported as a zero effect')
            aggregate.append({'source':source,'year':year,'clock_bin_hours':width,
                              'n_source_dyads':expected_all,'n_timed_dyads':n,
                              'status':row['status']})
            continue
        if row['status']!='DESCRIPTIVE_COMMON_CLOCK_CONDITIONAL':
            raise AssertionError('Valid time cohort wrongly suppressed')
        draws=row['grid_seed_aggregates']
        if len(draws)!=12*len(GRIDS):
            raise AssertionError('Incomplete source clock-grid-seed crossproduct')
        by={(d['grid_km'],d['origin_x_fraction'],d['origin_y_fraction'],d['seed']):d
            for d in draws}
        if set(by)!={(km,x,y,seed) for km,x,y in GRIDS for seed in range(12)}:
            raise AssertionError('Duplicate or missing clock-grid-seed output')
        for d in draws:
            _validate_draw(d,year,width,n)
        for seed in range(12):
            baseline=None
            for grid in GRIDS:
                d=by[(*grid,seed)]
                key=(d['mean_shared_clock_bins_per_pair_date'],d['n_pair_dates'],
                     d['n_supported_dyads'])
                if baseline is None:baseline=key
                elif key!=baseline:raise AssertionError('Spatial grids changed source date/clock opportunity')
        for grid in sorted(GRIDS):
            vals=[by[(*grid,seed)] for seed in range(12)]
            def av(key): return statistics.fmean(d[key[0]][key[1]] for d in vals)
            summary={
              'source':source,'year':year,'clock_bin_hours':width,
              'grid_km':grid[0],'origin_x_fraction':grid[1],
              'origin_y_fraction':grid[2],
              'status':'DESCRIPTIVE_ORIGINAL_SOURCE_TIMED',
              'n_source_dyads':expected_all,'n_timed_dyads':n,
              'retained_temporal_opportunity_fraction':n/expected_all,
              'mean_shared_bins_per_pair_date':statistics.fmean(
                  d['mean_shared_clock_bins_per_pair_date'] for d in vals),
              'n_seed_repetitions':12,
              'winter':{k:av(('winter',k)) for k in METRIC_KEYS},
              'summer':{k:av(('summer',k)) for k in METRIC_KEYS},
              'winter_minus_summer':{k:av(('winter_minus_summer',k)) for k in METRIC_KEYS},
              'D_delta_seed_sign_counts':sign_counts(
                  [d['winter_minus_summer']['D'] for d in vals]),
              'D_winter_positive_seed_count':sum(
                  d['winter']['D']>1e-12 for d in vals),
              'D_summer_positive_seed_count':sum(
                  d['summer']['D']>1e-12 for d in vals),
            }
            for k in METRIC_KEYS:
                if not close(summary['winter'][k]-summary['summer'][k],
                             summary['winter_minus_summer'][k]):
                    raise AssertionError('Summarized seasonal difference inconsistent with draws')
            aggregate.append(summary)
    return aggregate

def validate(directory):
    aggregate=[]
    for source in SOURCES:
        path=Path(directory)/(source+'_clock_couse_20261020.json')
        aggregate.extend(_validate_source(path,source))
    if len([r for r in aggregate if r['status']=='DESCRIPTIVE_ORIGINAL_SOURCE_TIMED'])!=40:
        raise AssertionError('Expected 5 eligible source-years × 2 time widths × 4 grids')
    return {
      'schema_version':1,'as_of':'2026-10-20',
      'source_run':'https://github.com/zuizui0223/batter/actions/runs/39414865136',
      'time_alignment_definition':'one original GPS position per animal-date-common-clock-bin; same-cell match in same coarse source-clock bin, not a physical encounter',
      'exact_independent_time_label_reference':'probability of same spatial cell under random within-day permutation of each animals clock-bin labels on identical observed common bins',
      'scope':'post-inspection source-derived geography/timing only; no E, true encounters or biological p-values',
      'source_aggregate_sha256':{source:SOURCES[source][0] for source in SOURCES},
      'n_sources':3,'n_eligible_source_years':5,
      'n_eligible_source_year_timewidth_groups':10,
      'n_grid_seed_aggregate_results':480,
      'n_stop_groups':2,
      'rows':aggregate}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=validate(args.input_dir)
    content=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(content)
    else:
        print(content)
    print('PASS original-GPS conditional coarse-time verification:',
          result['n_grid_seed_aggregate_results'],'source/year/clock/grid/seed scenarios')

if __name__=='__main__':
    main()
