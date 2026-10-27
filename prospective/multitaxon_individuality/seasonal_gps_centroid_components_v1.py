#!/usr/bin/env python3
"""Original-Movebank seasonal GPS center separation and geographic-component L1.

Post-inspection source-specific ecological geometry, not a population
significance or causal test. Complete published GPS/reference files and exact
source SHA256/MD5 are reverified; source animal IDs, positions and exact
dates never enter output. A disconnected graph of annual GPS-use centers
is NOT necessarily an independent biological population or social flock.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import tempfile

import cross_source_seasonal_x_v2 as geo
import same_clock_bin_couse_v1 as clock
import subhour_geodesic_proximity_v1 as near
import day_shift_preserved_trajectory_v1 as day
import source_spatial_influence_v1 as source_influence

SOURCES=day.SOURCES
YEARS=day.YEARS
TIME_TOLS=day.TOLERANCES
WINTER=day.WINTER
SUMMER=day.SUMMER
THRESHOLDS=(5.,10.,25.)
RADII=(.5,1.,2.)
SEEDS=tuple(range(12))
SOURCE_PREVIOUS_SHA256={
'turkey':'8182bf56b2d8e25d3f5ead3ffc89cd74d5d57c78bc171c954438a585ee8f63e2',
'white_tailed_deer':'19e035aa578ff4954a425201c9eb8074b89ed0a8753f71a1610a6db272d671b9',
'black_bear':'2252cc771c8f8337d452cadc5c2abd5bd9d7ca5a2350e6893f9a98f547540bac',
}


def _norm(vec):
    n=math.sqrt(sum(v*v for v in vec))
    if n < 1e-12:return None
    return tuple(v/n for v in vec)


def _unit(lat,lon):
    phi,theta=math.radians(lat),math.radians(lon)
    return math.cos(phi)*math.cos(theta),math.cos(phi)*math.sin(theta),math.sin(phi)


def seasonal_day_equal_centroids(events):
    """Original source GPS: each observed animal/date carries equal seasonal mass.

    We do not interpolate missing months and require >=7 original animal dates
    in at least two separately represented months in each seasonal category.
    """
    dates=defaultdict(lambda:[0.,0.,0.,0])
    for row in events:
        if row.month in WINTER:
            season='winter'
        elif row.month in SUMMER:
            season='summer'
        else:
            continue
        key=(row.year,row.animal,season,row.month,row.day)
        v=_unit(row.lat,row.lon)
        state=dates[key]
        for i in range(3):
            state[i]+=v[i]
        state[3]+=1
    aggregated=defaultdict(lambda:[0.,0.,0.])
    months=defaultdict(lambda:defaultdict(int))
    for (year,animal,season,month,_),val in dates.items():
        vec=_norm(val[:3])
        if vec is None:continue
        key=(year,animal,season)
        for i in range(3):
            aggregated[key][i]+=vec[i]
        months[key][month]+=1
    output={}
    for key,raw in aggregated.items():
        if sum(count>=7 for count in months[key].values())<2:
            continue
        v=_norm(raw)
        if v is not None:output[key]=v
    return output


def _components(pairset):
    """Private graph components; rank only by anonymous component size."""
    adjacency=defaultdict(set)
    for a,b in pairset:
        adjacency[a].add(b)
        adjacency[b].add(a)
    remaining=set(adjacency)
    comps=[]
    while remaining:
        seed=min(remaining)
        queue=[seed];members={seed};remaining.remove(seed)
        while queue:
            for other in adjacency[queue.pop()] & remaining:
                remaining.remove(other)
                members.add(other)
                queue.append(other)
        edges={p for p in pairset if p[0] in members and p[1] in members}
        comps.append((members,edges))
    comps.sort(key=lambda x:(-len(x[0]),-len(x[1]),min(x[0])))
    if sum(len(x[1]) for x in comps)!=len(pairset):
        raise AssertionError('Geographic component membership incomplete')
    return comps


def _quantile(values,p):
    if not values:return None
    xs=sorted(values)
    a=(len(xs)-1)*p
    low=int(a);high=min(low+1,len(xs)-1)
    return xs[low]+(xs[high]-xs[low])*(a-low)


def _summarize_season_centroid_distances(pairs,year,centers):
    """Cohort-only paired winter vs summer original GPS seasonal use centers."""
    wd,sd=[],[]
    for animal1,animal2 in sorted(pairs):
        need=((year,animal1,'winter'),(year,animal2,'winter'),
              (year,animal1,'summer'),(year,animal2,'summer'))
        if any(key not in centers for key in need):
            continue
        w=geo.centroid_distance_km(centers[need[0]],centers[need[1]])
        s=geo.centroid_distance_km(centers[need[2]],centers[need[3]])
        wd.append(w)
        sd.append(s)
    n=len(wd)
    deltas=[w-s for w,s in zip(wd,sd)]
    return {
        'n_source_pairs_requested':len(pairs),
        'n_source_pairs_with_both_season_centers':n,
        'n_unavailable_source_pair_season_centers':len(pairs)-n,
        'status':'DESCRIPTIVE_SOURCE_SEASON_CENTROID_DISTANCE'
                 if n>=2 else 'NOT_ESTIMABLE_SOURCE_SEASON_CENTER_SUPPORT',
        'winter_km':{'mean':statistics.fmean(wd),'median':statistics.median(wd),
                     'q10':_quantile(wd,.1),'q90':_quantile(wd,.9)} if n else None,
        'summer_km':{'mean':statistics.fmean(sd),'median':statistics.median(sd),
                     'q10':_quantile(sd,.1),'q90':_quantile(sd,.9)} if n else None,
        'winter_minus_summer_km':{
           'mean':statistics.fmean(deltas),'median':statistics.median(deltas),
           'q10':_quantile(deltas,.1),'q90':_quantile(deltas,.9)}
           if n else None,
        'n_pairs_winter_centers_closer':sum(v < -1e-8 for v in deltas),
        'n_pairs_summer_centers_closer':sum(v > 1e-8 for v in deltas),
        'fraction_pairs_winter_centers_closer':
           sum(v < -1e-8 for v in deltas)/n if n else None,
        'season_center_comparison_is_not_real_time_encounter':True,
    }


def _get_previous(source):
    path=Path(__file__).resolve().with_name(
        'SOURCE_SPATIAL_INFLUENCE_'+source.upper()+'_2026_10_22.json')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_PREVIOUS_SHA256[source]:
        raise AssertionError('Prior full-original source geography source SHA256 changed')
    return json.loads(raw)


def analyze(source,cache):
    timed,events,pinned=clock.get_original(source,cache)
    byday=near._native_positions(source,cache,events)
    previous=_get_previous(source)
    if (not previous['full_original_GPS_and_reference_MD5_SHA256_verified'] or
        not previous['full_source_GPS_position_and_timestamp_multiset_replayed'] or
        previous['source']!=source or previous['source_original_fixes']!=len(events)):
        raise AssertionError('Pinned original source lineage is unavailable')
    seasonal_centers=seasonal_day_equal_centroids(events)
    annual_centers=geo.annual_day_balanced_centroids(events)
    archives=source_influence._source_dual_archive(source)
    oldyears={x['year']:x for x in previous['original_year_results']}
    archiveyears={x['year']:x for x in archives['source_year_results']}
    response={
        'schema_version':1,'as_of':'2026-10-22',
        'status':'POST_INSPECTION_ORIGINAL_SOURCE_SEASON_CENTROID_AND_SPATIAL_COMPONENT',
        'source':source,'source_doi':geo.SOURCES[source][1],
        'accepted_complete_original_GPS_fix_count':len(events),
        'publisher_original_MD5_and_prior_source_SHA256_verified':True,
        'independent_full_source_time_position_multiset_verified':True,
        'prior_original_source_geo_summary_SHA256_verified':True,
        'original_dual_anchor_replay_for_all_scored_component_dyads':True,
        'native_GPS_source_clock_absolute_UTC_verified':False,
        'local_biological_population_membership_verified':False,
        'tag_specific_GPS_location_error_verified':False,
        'fixed_geo_pair_distance_thresholds_km':list(THRESHOLDS),
        'original_clock_tolerances_seconds':list(TIME_TOLS),
        'near_position_radii_km':list(RADII),
        'n_source_sampling_seeds':len(SEEDS),
        'year_groups':[],
        'limitations':['Disconnected original annual GPS-use-centroid graphs are not verified distinct populations',
                       'Seasonal centers average original days equally and use nonconsecutive Jan/Feb/Dec calendar-year winter months',
                       'Original GPS location error and source UTC-vs-GPS clock basis not independently resolved',
                       'Previously inspected source proximity drives this exploratory grouping; not a preregistration or causal test',
                       'All within-source dyads may share animals and all seed draws reuse GPS records',
                       'No source animal identity, exact original GPS date, timestamp or position is published'],
    }
    for year in YEARS:
        geodyads=clock._base_pair_set(events,year,annual_centers)
        expected_geo=day.EXPECTED_V2_COUNTS[source][year][0]
        if len(geodyads)!=expected_geo:
            raise AssertionError('Previously source-verified original geography pair set changed')
        yearout={'year':year,'original_25km_source_dyads':len(geodyads),
                 'tolerance_groups':[]}
        oldbytol={x['tolerance_seconds']:x for x in oldyears[year]['time_tolerance_rows']}
        prevbytol={x['max_abs_original_GPS_time_gap_seconds']:x
                  for x in archiveyears[year]['time_tolerance_results']}
        for tol in TIME_TOLS:
            same=near._derive_opportunity(byday,geodyads,year,tol)
            forward=day.eligible_day_shift(byday,set(same),year,tol)
            reverse=day.eligible_day_shift(byday,{(b,a) for a,b in same},year,tol)
            pairs=set(forward) & {(b,a) for a,b in reverse}
            old=oldbytol[tol]
            archived=prevbytol[tol]
            if len(pairs)!=old['n_both_direction_day_shift_dyads'] or \
                len(pairs)!=archived['n_both_orientation_supported_dyads']:
                raise AssertionError('Previously fixed original source time risk set changed')
            group={'source_year':year,'tolerance_seconds':tol,
                   'n_original_matched_source_dyads':len(pairs),
                   'status':'DESCRIPTIVE_GPS_GEOMETRIC_COMPONENTS_AND_SEASON_CENTERS'
                            if archived['status'].startswith('DESCRIPTIVE_')
                            else 'STOP_INSUFFICIENT_MATCHED_ORIGINAL_GPS',
                   'annual_center_bands':[],
                   'components_by_annual_center_threshold':[]}
            if group['status'].startswith('STOP'):
                yearout['tolerance_groups'].append(group)
                continue
            f={p:forward[p] for p in sorted(pairs)}
            b={(p[1],p[0]):reverse[(p[1],p[0])] for p in sorted(pairs)}
            per_pair=source_influence._per_pair_and_replay(
                f,b,source,year,tol,archived['orientation_seed_radius_aggregates'])
            annual_d={p:geo.centroid_distance_km(
                annual_centers[year][p[0]],annual_centers[year][p[1]])
                      for p in pairs}
            for label,low,high in (('[0,5] km',0.,5.),
                                   ('(5,10] km',5.,10.),
                                   ('(10,25] km',10.,25.),
                                   ('[0,25] km',0.,25.)):
                if low==0.:
                    included={p for p in pairs if annual_d[p]<=high+1e-10}
                else:
                    included={p for p in pairs
                              if low<annual_d[p]<=high+1e-10}
                measures=_summarize_season_centroid_distances(included,year,seasonal_centers)
                group['annual_center_bands'].append({
                    'annual_centroid_pair_separation_band':label,
                    'n_qualified_source_dyads':len(included),
                    **measures,
                })
            for distance in THRESHOLDS:
                filtered={p for p in pairs if annual_d[p]<=distance+1e-10}
                pieces=_components(filtered)
                comps=[]
                for rank,(members,edges) in enumerate(pieces,1):
                    estimate=source_influence._summary_for_edges(per_pair,edges)
                    comps.append({
                        'anonymous_geographic_component_rank_by_animals':rank,
                        'n_component_original_animals':len(members),
                        'n_component_original_dyads':len(edges),
                        'original_source_component_L1_by_radius_direction':estimate,
                    })
                group['components_by_annual_center_threshold'].append({
                    'centroid_pair_distance_cutoff_km':distance,
                    'n_source_centroid_components_with_edges':len(comps),
                    'component_support':comps,
                })
                prior=next(r for r in old['spatial_filters'] if r['threshold_km']==distance)
                if [p['n_component_original_animals'] for p in comps] != prior['component_animal_counts'] or \
                   [p['n_component_original_dyads'] for p in comps] != prior['component_dyad_counts']:
                    raise AssertionError('Independent source geographic graph components differ from prior audit')
                if sum(x['n_component_original_dyads'] for x in comps)!=len(filtered):
                    raise AssertionError('Original source geographic component edges do not exhaust risk set')
            yearout['tolerance_groups'].append(group)
            print(json.dumps({'source':source,'year':year,'time_gap_seconds':tol,
                'n_geographic_dyads':len(pairs),
                'n_5km_components':group['components_by_annual_center_threshold'][0]['n_source_centroid_components_with_edges'],
                'n_10_to_25km_source_dyads':group['annual_center_bands'][2]['n_qualified_source_dyads'],
                'original_source_dual_anchor_replayed':True},sort_keys=True),flush=True)
        response['year_groups'].append(yearout)
    return response


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',choices=SOURCES,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='original_source_season_geography_') as tmp:
        outcome=analyze(args.source,Path(tmp))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(outcome,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'source':args.source,
       'accepted_original_source_fixes':outcome['accepted_complete_original_GPS_fix_count'],
       'original_source_result_SHA256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
       'status':outcome['status']},sort_keys=True))


if __name__=='__main__':
    main()
