#!/usr/bin/env python3
"""Independent aggregate-only validation of wild turkey calendar-month GPS geometry.

Checks exact original source receipt, all 2019/2020 month/source group
denominators, monthly time-support gates and no original animal identifiers
or source coordinates, plus previously pinned single-mover source receipt.
This is a SOURCE-STUDY observation, not a biological migrant/interaction test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE_SHA256='2e2ec358078475c7a45a2fdb8f332ae35497cd351048ac333c904325df6d7cd2'
ROOT=Path(__file__).resolve().parent
EXPECTED_GROUPS={
    2019:{'all_25km_source_pairs':(112,19),
          '2019_larger_annual5_component':(53,11),
          '2019_smaller_annual5_component':(20,7)},
    2020:{'all_25km_source_pairs':(21,7),
          '2020_six_member_annual5_core':(15,6),
          '2020_annual5_isolate_vs_core':(6,7),
          '2020_annual10_to25_isolate_pairs':(5,7)}
}
EARTH=6371.


def close(x,y,eps=2e-8):
    return math.isclose(x,y,abs_tol=eps,rel_tol=1e-10)


def _distance_stats(record):
    if record is None:
        return
    if set(record)!={'min','median','mean','max'}:
        raise AssertionError('Unexpected source GPS monthly summary schema')
    v=[record[k] for k in ('min','median','mean','max')]
    if any(isinstance(x,bool) or not isinstance(x,(int,float))
           or not math.isfinite(x) or not 0<=x<=math.pi*EARTH+1e-5
           for x in v):
        raise AssertionError('Bad source-GPS monthly great-circle distance')
    if not (record['min']<=record['median']<=record['max']
            and record['min']<=record['mean']<=record['max']):
        raise AssertionError('Monthly source-GPS distance summary order invalid')


def _check_group(g,label,n_pairs,n_animals,n_7day):
    allowed={'group_label','original_graph_n_animals','n_original_pairs',
             'n_valid_monthly_pairs','n_animals_in_valid_monthly_pairs',
             'eligible_pair_fraction','status','distance_km'}
    if set(g)!=allowed or g['group_label']!=label:
        raise AssertionError('Unrecognized original GPS source group or sensitive extra field')
    if g['original_graph_n_animals']!=n_animals or g['n_original_pairs']!=n_pairs:
        raise AssertionError('Original source graph denominator changed')
    n=g['n_valid_monthly_pairs'];a=g['n_animals_in_valid_monthly_pairs']
    if not (0<=n<=n_pairs and 0<=a<=min(n_animals,n_7day)):
        raise AssertionError('Monthly observed GPS support differs from eligible source graph')
    if not close(g['eligible_pair_fraction'],n/n_pairs):
        raise AssertionError('Pair support fraction denominator changed')
    valid=(n>=3 and a>=3)
    want=('DESCRIPTIVE_SOURCE_MONTH_CENTROID_DISTANCE' if valid
          else 'NOT_ESTIMABLE_MONTHLY_SOURCE_SUPPORT')
    if g['status']!=want:
        raise AssertionError('Unsupported monthly GPS sample turned into evidence')
    if valid:
        _distance_stats(g['distance_km'])
        if g['distance_km'] is None:
            raise AssertionError('Monthly source geographic statistic wrongly omitted')
    elif g['distance_km'] is not None:
        raise AssertionError('Unsupported monthly source GPS distance imputed')


def _transition_check(months, reported):
    states=[(r['month'],r['isolate_vs_core_monthly_state']) for r in months]
    valid=[x for x in states if x[1]!='UNOBSERVED']
    predicted={'status':'NO_SUPPORTED_CLOSE_TO_SEPARATED_BRACKET'}
    for index,(month,state) in enumerate(valid):
        if state!='SEPARATED':
            continue
        earlier=[r for r in valid[:index] if r[1]=='CLOSE']
        if not earlier:continue
        first=earlier[-1][0]
        intervening=[s for m,s in states if first<m<month]
        predicted={
            'status':'OBSERVATION_BRACKET_NOT_TRACKED_TRANSITION_TIME',
            'last_observed_close_month':first,
            'first_later_observed_separated_month':month,
            'months_strictly_between':len(intervening),
            'unobserved_months_in_bracket':intervening.count('UNOBSERVED'),
            'observed_intermediate_months_in_bracket':intervening.count('INTERMEDIATE')
        }
        break
    if predicted!=reported:
        raise AssertionError('Observed source-month chronology or gap bracket inconsistent')


def validate(path):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=SOURCE_SHA256:
        raise AssertionError('Original public Movebank monthly aggregate SHA256 changed')
    d=json.loads(data)
    allowed_top={
     'schema_version','as_of','source','source_doi','status',
     'complete_original_source_MD5_and_pinned_SHA256_verified',
     'independent_original_time_position_multiset_verified',
     'original_2019_2020_GPS_fixes',
     'original_source_clock_UTC_basis_calibrated',
     'original_tag_GPS_error_calibrated',
     'independent_local_populations_verified',
     'monthly_original_date_support_threshold',
     'source_year_eligible_animals','source_year_eligible_pairs',
     'same_original_animal_IDs_in_2019_and_2020',
     'known_source_GPS_2020_isolate_janfeb_summer_shift_km',
     'known_source_GPS_2020_six_core_median_shift_km',
     'month_results','transition_bracket_2020',
     'n_2020_months_full_seven_animal_support',
     'n_2020_months_isolate_vs_core_observed',
     'limits'
    }
    if set(d)!=allowed_top:
        raise AssertionError('Unexpected top-level fields; sensitive original GPS data risk')
    if not (d['schema_version']==1 and d['source']=='turkey'
            and d['source_doi']=='10.5441/001/1.671'
            and d['status']=='POST_INSPECTION_ORIGINAL_GPS_ANONYMOUS_MONTHLY_CORE_GEOGRAPHY'
            and d['original_2019_2020_GPS_fixes']==435214
            and d['monthly_original_date_support_threshold']==7
            and d['source_year_eligible_animals']=={'2019':19,'2020':7}
            and d['source_year_eligible_pairs']=={'2019':112,'2020':21}
            and d['same_original_animal_IDs_in_2019_and_2020']==0
            and d['complete_original_source_MD5_and_pinned_SHA256_verified']
            and d['independent_original_time_position_multiset_verified']
            and d['original_tag_GPS_error_calibrated'] is False
            and d['original_source_clock_UTC_basis_calibrated'] is False
            and d['independent_local_populations_verified'] is False):
        raise AssertionError('Original source and its scientific boundaries changed')
    if not close(d['known_source_GPS_2020_isolate_janfeb_summer_shift_km'],
                 14.52355751362658,eps=2e-6):
        raise AssertionError('Earlier 2020 isolate original mover receipt changed')
    if not close(d['known_source_GPS_2020_six_core_median_shift_km'],
                 .4550351589540801,eps=2e-6):
        raise AssertionError('Earlier six original turkey core movement reference changed')
    years={r['year']:r for r in d['month_results']}
    if set(years)!={2019,2020}:
        raise AssertionError('All source calendar years required')
    summary={'year_month_rows':0,'group_months':0,'fully_2020':0,
             'observed_2020':0,'year_support':[]}
    for year in (2019,2020):
        y=years[year]
        allowed={'year','n_source_eligible_animals','n_source_eligible_dyads',
                 'original_annual5_component_animal_sizes',
                 'original_annual5_component_edge_sizes','months'}
        if set(y)!=allowed:
            raise AssertionError('Unexpected source-year privacy/scope fields')
        n=19 if year==2019 else 7
        target_graph=([11,7],[53,20]) if year==2019 else ([6],[14])
        if (y['n_source_eligible_animals']!=n or y['n_source_eligible_dyads']!=
            (112 if year==2019 else 21) or
            (y['original_annual5_component_animal_sizes'],
             y['original_annual5_component_edge_sizes'])!=target_graph):
            raise AssertionError('Previously pinned GPS component mask differed')
        rows={r['month']:r for r in y['months']}
        if len(y['months'])!=12 or set(rows)!=set(range(1,13)):
            raise AssertionError('Skipped or duplicated source calendar month')
        for month in range(1,13):
            r=rows[month]
            base={'month','n_eligible_animals_with_7_observed_days',
                  'n_eligible_animals_with_any_fix',
                  'n_eligible_animal_calendar_dates',
                  'n_eligible_original_GPS_fixes',
                  'n_source_animals_7day_centroid_supported',
                  'group_centroid_pair_distances'}
            newer={'n_annual5_core_animals_7day_supported',
                   'annual5_isolated_animal_7day_supported',
                   'source_tracking_completeness',
                   'isolate_vs_core_monthly_state'}
            if set(r)!=(base|newer if year==2020 else base):
                raise AssertionError('Unexpected monthly source GPS schema')
            sampled=r['n_eligible_animals_with_7_observed_days']
            anyfix=r['n_eligible_animals_with_any_fix']
            dates=r['n_eligible_animal_calendar_dates']
            fixes=r['n_eligible_original_GPS_fixes']
            if not (0<=sampled<=anyfix<=n and fixes>=dates>=sampled*7
                    and r['n_source_animals_7day_centroid_supported']==sampled):
                raise AssertionError('Original GPS fix/day sampling support invalid')
            groups={g['group_label']:g for g in r['group_centroid_pair_distances']}
            if len(groups)!=len(EXPECTED_GROUPS[year]) or set(groups)!=set(EXPECTED_GROUPS[year]):
                raise AssertionError('Monthly source grouping changed')
            for label,(pairs,animals) in EXPECTED_GROUPS[year].items():
                _check_group(groups[label],label,pairs,animals,sampled)
                summary['group_months']+=1
            if year==2020:
                ncore=r['n_annual5_core_animals_7day_supported']
                isolate=r['annual5_isolated_animal_7day_supported']
                if (not isinstance(isolate,bool) or not 0<=ncore<=6
                        or ncore+int(isolate)!=sampled):
                    raise AssertionError('2020 source core/month support impossible')
                fully='FULLY_TRACKED_7_OF_7_MONTHLY_CENTRES' if sampled==7 else 'PARTIAL_OR_NO_MONTHLY_CENTRE_SUPPORT'
                if r['source_tracking_completeness']!=fully:
                    raise AssertionError('Incorrect source full-month tracking label')
                iso=groups['2020_annual5_isolate_vs_core']
                if iso['n_valid_monthly_pairs']!=(ncore if isolate else 0):
                    raise AssertionError('Isolate-core source pair cover differs from original bird-date support')
                state='UNOBSERVED'
                if isolate and ncore>=4:
                    median=iso['distance_km']['median']
                    state=('CLOSE' if median<=1 else
                           'SEPARATED' if median>=5 else 'INTERMEDIATE')
                if r['isolate_vs_core_monthly_state']!=state:
                    raise AssertionError('Recorded monthly source geographic state does not match median')
                summary['observed_2020']+=state!='UNOBSERVED'
                summary['fully_2020']+=sampled==7
            summary['year_month_rows']+=1
        summary['year_support'].append({'year':year,'months_with_at_least_3_animals':
             sum(x['n_eligible_animals_with_7_observed_days']>=3 for x in y['months']),
             'months_no_valid_animal_centers':
             sum(x['n_eligible_animals_with_7_observed_days']==0 for x in y['months'])})
    if (summary['year_month_rows']!=24 or summary['group_months']!=84 or
        summary['fully_2020']!=d['n_2020_months_full_seven_animal_support'] or
        summary['observed_2020']!=d['n_2020_months_isolate_vs_core_observed']):
        raise AssertionError('Monthly/source-group total mismatched')
    _transition_check(years[2020]['months'],d['transition_bracket_2020'])
    summary['transition_bracket']=d['transition_bracket_2020']
    summary['original_source_sha256']=SOURCE_SHA256
    summary['status']='SOURCE_GPS_MONTHLY_CENTROID_AGGREGATE_VERIFIED'
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,
                   default=ROOT/'TURKEY_MONTHLY_CORE_SEPARATION_SOURCE_2026_10_28.json')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=validate(args.source)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:args.output.write_text(payload)
    else:print(payload)
    print('PASS source original turkey monthly centre/year/pair support and no individual tracks')


if __name__=='__main__':
    main()
