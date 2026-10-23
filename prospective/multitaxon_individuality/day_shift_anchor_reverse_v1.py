#!/usr/bin/env python3
"""Reversed A/B GPS anchor sensitivity of published-source day-shift control.

POST-INSPECTION original-GPS temporal trajectory diagnostic, not a
randomized social encounter null. Exact original published Movebank files,
source identity/reference tables and MD5/pinned SHA256 are verified
before the original time/position multiset is accepted.
Output contains only source/year/tolerance/orientation/radius/seed aggregates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile

import cross_source_seasonal_x_v2 as geography
import same_clock_bin_couse_v1 as clock
import subhour_geodesic_proximity_v1 as near
import day_shift_preserved_trajectory_v1 as day

SOURCES = day.SOURCES
TOLS = day.TOLERANCES
YEARS = day.YEARS
RADII_KM = day.RADII_KM
SEEDS = day.SEEDS
REQUIRED_MIN_DYADS = day.MIN_SUPPORTED_DYADS
REQUIRED_MIN_ANIMALS = day.MIN_SUPPORTED_ANIMALS
EXPECTED_FORWARD={
    'turkey':{2019:(112,112),2020:(21,21)},
    'black_bear':{2019:(0,0),2020:(6,6)},
    'white_tailed_deer':{2019:(55,55),2020:(205,205)},
}


def analyze(source,byday,untimed,pinned):
    centers=geography.annual_day_balanced_centroids(untimed)
    answer={
        'schema_version':1,'as_of':'2026-10-21','source':source,
        'source_doi':geography.SOURCES[source][1],
        'status':'POST_INSPECTION_DUAL_ANCHOR_ORIGINAL_GPS_TRAJECTORY_CONTROL',
        'complete_original_publisher_MD5_pinned_SHA256_verified':True,
        'independent_native_original_GPS_time_position_multiset_verified':True,
        'native_clock_offset_UTC_verified':False,
        'biological_local_population_membership_verified':False,
        'GPS_position_accuracy_quantified':False,
        'n_original_source_GPS_fixes':len(untimed),
        'time_tolerances_seconds':list(TOLS),'radii_km':list(RADII_KM),
        'n_seeds':len(SEEDS),'reverse_focal_animals_evaluated':True,
        'source_year_results':[],
        'caveats':[
            'Same individual pair identities, not identical source GPS recording times across orientations',
            'Original animal lexicographic label selected the direction; source-year pairs and seeds are dependent',
            'One-day shifts preserve original within-day path order, not full ecological or between-day autocorrelation',
            'Predeclared two-anchor stability gate is descriptive only; no biological p-values or encounter proof',
            'No verified source clock UTC offset, GPS accuracy, source population membership or resource exposure'],
    }
    for year in YEARS:
        source_geo_pairs=clock._base_pair_set(untimed,year,centers)
        if len(source_geo_pairs)!=day.EXPECTED_V2_COUNTS[source][year][0]:
            raise AssertionError('Original source geometric dyad mask changed')
        year_result={'year':year,'n_source_geographic_dyads':len(source_geo_pairs),
                     'time_tolerance_results':[]}
        mask_by_gap={}
        for index,tol in enumerate(TOLS):
            same_day=near._derive_opportunity(byday,source_geo_pairs,year,tol)
            expected_same=day.EXPECTED_V2_COUNTS[source][year][index+1]
            if len(same_day)!=expected_same:
                raise AssertionError('Original source same-day GPS support changed')
            forward=day.eligible_day_shift(byday,set(same_day),year,tol)
            if len(forward)!=EXPECTED_FORWARD[source][year][index]:
                raise AssertionError('Source previous/next-day primary anchor support changed')
            reversed_dyads={(b,a) for a,b in same_day}
            reversed_q=day.eligible_day_shift(byday,reversed_dyads,year,tol)
            reverse_normal={(b,a) for a,b in reversed_q}
            both=set(forward)&reverse_normal
            if not both.issubset(set(same_day)):
                raise AssertionError('Dual-orientation risk set leaked unsupported source GPS pair')
            mask_by_gap[tol]=both
            n=len(both)
            animals=len({a for p in both for a in p})
            status=('DESCRIPTIVE_DUAL_ANCHOR_SAME_DYADS_ORIGINAL_GPS'
                    if n>=REQUIRED_MIN_DYADS and animals>=REQUIRED_MIN_ANIMALS
                    else 'STOP_SMALL_DUAL_ANCHOR_COMMON_GPS_SUPPORT')
            outcome={
                'max_abs_original_GPS_time_gap_seconds':tol,
                'status':status,
                'n_original_same_day_GPS_dyads':len(same_day),
                'n_forward_day_shift_dyads':len(forward),
                'n_reversed_day_shift_dyads':len(reversed_q),
                'n_both_orientation_supported_dyads':n,
                'n_distinct_animals_in_shared_pair_set':animals,
                'fraction_forward_pairs_remaining':n/len(forward) if forward else None,
                'orientation_seed_radius_aggregates':[],
            }
            if status.startswith('DESCRIPTIVE_'):
                f={p:forward[p] for p in sorted(both)}
                r={(b,a):reversed_q[(b,a)] for a,b in sorted(both)}
                for seed in SEEDS:
                    af=day._one_seed(f,source,year,tol,seed)
                    rb=day._one_seed(r,source,year,tol,seed)
                    if len(af)!=len(RADII_KM) or len(rb)!=len(RADII_KM):
                        raise AssertionError('Incomplete source radius estimate')
                    for label, rows in (('original_A_to_B',af),
                                        ('reversed_B_to_A',rb)):
                        for row in rows:
                            if row['n_dyads']!=n:
                                raise AssertionError('Source common pair denominator changed')
                            outcome['orientation_seed_radius_aggregates'].append({
                                'direction':label,
                                **row,
                            })
                if len(outcome['orientation_seed_radius_aggregates']) != (
                        len(SEEDS)*len(RADII_KM)*2):
                    raise AssertionError('Incomplete dual-anchor sample factorial')
            year_result['time_tolerance_results'].append(outcome)
            print(json.dumps({
                'source':source,'year':year,'time_gap_seconds':tol,
                'forward_eligible_pairs':len(forward),
                'reversed_eligible_pairs':len(reversed_q),
                'same_pair_set':n,'animals':animals,
                'n_scenarios':len(outcome['orientation_seed_radius_aggregates']),
                'status':status},sort_keys=True),flush=True)
        if not mask_by_gap[TOLS[0]].issubset(mask_by_gap[TOLS[1]]):
            raise AssertionError('15min dual-anchor pair mask not subset of 30min mask')
        answer['source_year_results'].append(year_result)
    return answer


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',choices=SOURCES,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='dual_anchor_original_source_') as temporary:
        cache=Path(temporary)
        timed,untimed,pinned=clock.get_original(args.source,cache)
        byday=near._native_positions(args.source,cache,untimed)
        results=analyze(args.source,byday,untimed,pinned)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'source':args.source,
                      'original_fixes':results['n_original_source_GPS_fixes'],
                      'output_SHA256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'status':results['status']},sort_keys=True))


if __name__=='__main__':
    main()
