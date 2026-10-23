#!/usr/bin/env python3
"""Original-source turkey 2019 component replication and 2020 winter location-centre test.

Original GPS raw identifiers/coordinates/times exist ONLY on temporary runner
during calculation. Only source-year/group n, spatial distances and L1 score
aggregates are exported. A connected GPS-centre graph is not a confirmed
independent animal population. A within-15/30-min GPS location is NOT direct
animal contact. Post-inspection exploratory study, not preregistered.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
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
import source_spatial_influence_v1 as spatial

SOURCE = 'turkey'
DOI = '10.5441/001/1.671'
YEARS = (2019, 2020)
GAPS = (900, 1800)
SEEDS = tuple(range(12))
RADII = (.5, 1., 2.)
SEASONS = {'winter': (1,2,12), 'summer': (6,7,8),
           'jan_feb': (1,2), 'dec_only': (12,)}
MIN_PAIRED_DAYS = 7
MIN_ESTIMABLE_DYADS = 8
EARTH_RADIUS_KM = 6371.

def _close(a,b,atol=2e-10):
    return math.isclose(a,b,abs_tol=atol,rel_tol=1e-10)

def _xyz(lat,lon):
    phi,theta=math.radians(lat),math.radians(lon)
    c=math.cos(phi)
    return (c*math.cos(theta),c*math.sin(theta),math.sin(phi))

def _normalize(vector):
    norm=math.sqrt(sum(v*v for v in vector))
    return tuple(v/norm for v in vector) if norm>1e-12 else None

def _unit_day_mean(points):
    """Each original observation within a day has equal weight; one day one vote."""
    if not points:return None
    return _normalize(tuple(math.fsum(x[i] for x in points) for i in range(3)))

def _unit_season_mean(day_vectors):
    return _normalize(tuple(math.fsum(v[i] for v in day_vectors) for i in range(3)))

def seasonal_source_centres(events,months, min_dates=MIN_PAIRED_DAYS):
    """Equal recorded-GPS-date, unit-sphere original GPS centers per year, animal."""
    byday=defaultdict(list)
    for fix in events:
        if fix.month in months:
            byday[(fix.year,fix.animal,fix.day)].append(_xyz(fix.lat,fix.lon))
    byanimal=defaultdict(list)
    for (year,animal,_day),vecs in byday.items():
        v=_unit_day_mean(vecs)
        if v is not None:byanimal[(year,animal)].append(v)
    out=defaultdict(dict)
    counts=defaultdict(dict)
    for (year,animal),vectors in byanimal.items():
        if len(vectors)<min_dates:continue
        center=_unit_season_mean(vectors)
        if center is not None:
            out[year][animal]=center
            counts[year][animal]=len(vectors)
    return out,counts

def _components(edges):
    """Internal member collections, original animal IDs NEVER serialized."""
    graph=defaultdict(set)
    for a,b in edges:
        graph[a].add(b)
        graph[b].add(a)
    seen=set();result=[]
    for root in sorted(graph):
        if root in seen:continue
        stack=[root];seen.add(root);members={root}
        while stack:
            v=stack.pop()
            for n in graph[v]-seen:
                seen.add(n);members.add(n);stack.append(n)
        part={p for p in edges if p[0] in members and p[1] in members}
        result.append((members,part))
    result.sort(key=lambda group:(-len(group[0]),-len(group[1])))
    return result

def _describe_pair_season_distances(pairs, centers):
    vals=[]
    for a,b in sorted(pairs):
        ca,cb=centers.get(a),centers.get(b)
        if ca is None or cb is None:continue
        vals.append(geo.centroid_distance_km(ca,cb))
    if not vals:
        return {'n_supported':0,'mean_km':None,'median_km':None,'min_km':None,'max_km':None}
    return {'n_supported':len(vals),'mean_km':statistics.fmean(vals),
            'median_km':statistics.median(vals),
            'min_km':min(vals),'max_km':max(vals)}

def _pairwise_season_distance(pairs, season_centers, year, first='winter',
                              second='summer'):
    left=season_centers[first].get(year,{})
    right=season_centers[second].get(year,{})
    w=[];s=[];dif=[]
    for a,b in sorted(pairs):
        if a not in left or b not in left or a not in right or b not in right:
            continue
        dw=geo.centroid_distance_km(left[a],left[b])
        ds=geo.centroid_distance_km(right[a],right[b])
        w.append(dw);s.append(ds);dif.append(dw-ds)
    if not dif:
        return {'status':'NOT_ESTIMABLE_NO_BOTH_SEASON_CENTRES',
                'n_pairs_with_both_centres':0,
                'winter_distances_km':_describe_pair_season_distances(pairs,left),
                'comparator_distances_km':_describe_pair_season_distances(pairs,right)}
    return {'status':'DESCRIPTIVE_SOURCE_SEASON_CENTROID_SEPARATION',
            'n_pairs_with_both_centres':len(dif),
            'winter_distances_km':{
                'mean':statistics.fmean(w),'median':statistics.median(w),
                'min':min(w),'max':max(w)},
            'comparator_distances_km':{
                'mean':statistics.fmean(s),'median':statistics.median(s),
                'min':min(s),'max':max(s)},
            'winter_minus_comparator_distance_km':{
                'mean':statistics.fmean(dif),'median':statistics.median(dif),
                'min':min(dif),'max':max(dif)},
            'fraction_pairs_winter_centres_closer':sum(x<0 for x in dif)/len(dif),
            'fraction_pairs_winter_centres_farther':sum(x>0 for x in dif)/len(dif)}

def _group_sets(year,pairs,annual_dist):
    near5={p for p in pairs if annual_dist[p]<=5+1e-10}
    near10={p for p in pairs if annual_dist[p]<=10+1e-10}
    outer5=pairs-near5
    groups={'all_annual_0_to25km':pairs,'annual_0_to5km':near5,
            'annual_5_to10km':near10-near5,
            'annual_10_to25km':pairs-near10,
            'annual_5_to25km':outer5}
    components=_components(near5)
    if year==2019:
        if [(len(animals),len(edges)) for animals,edges in components]!=[(11,53),(7,20)]:
            raise AssertionError('Source 2019 two disconnected 5km components changed')
        groups['2019_large_5km_component']=components[0][1]
        groups['2019_small_5km_component']=components[1][1]
        if len(pairs)!=112 or len(near5)!=73:
            raise AssertionError('Source 2019 full/5km fixed pair counts changed')
    elif year==2020:
        if [(len(animals),len(edges)) for animals,edges in components]!=[(6,14)]:
            raise AssertionError('Source 2020 5km connected component changed')
        if (len(pairs),len(near5),len(near10-near5),len(pairs-near10))!=(21,14,2,5):
            raise AssertionError('Source 2020 distance-band fixed pair counts changed')
        groups['2020_5km_component']=components[0][1]
    return groups

def _matched_selected_season_center(months, season, direction_pair,
                                    source,year,tol,seed):
    """Actual 3 original same-day time-matched positions on exact old 2x7 days."""
    valid_months=[m for m in SEASONS[season] if m in months]
    a,b=direction_pair
    chosen=day._draw(valid_months,2,'MONTH',source,year,tol,seed,direction_pair,season)
    original_by_animal=([],[])
    for month in chosen:
        dates=day._draw(list(months[month]),7,'DAY',source,year,tol,seed,
                        direction_pair,season,month)
        for date in dates:
            positions=day._draw(months[month][date],3,'FIX',source,year,tol,
                                seed,direction_pair,season,month,date)
            for idx in (0,1):
                # The original A position is tuple index 0. The original
                # B position on the *same* date is tuple index 1.
                points=[_xyz(record[idx][1],record[idx][2]) for record in positions]
                vector=_unit_day_mean(points)
                if vector is None:
                    raise AssertionError('Original daily GPS unit center undefined')
                original_by_animal[idx].append(vector)
    if any(len(x)!=14 for x in original_by_animal):
        raise AssertionError('Frozen pair common date support differs')
    return tuple(_unit_season_mean(x) for x in original_by_animal)

def _paired_sample_center_deltas(eligible, group_pairs, source, year, tol):
    # eligible: fixed pair-> original A->B day-shift support
    outcome=[]
    for seed in SEEDS:
        win=[];sumr=[]
        for pair in sorted(group_pairs):
            support=eligible[pair]
            ca=_matched_selected_season_center(support,'winter',pair,source,year,tol,seed)
            cb=_matched_selected_season_center(support,'summer',pair,source,year,tol,seed)
            win.append(geo.centroid_distance_km(ca[0],ca[1]))
            sumr.append(geo.centroid_distance_km(cb[0],cb[1]))
        if win:
            outcome.append({'seed':seed,'n_pairs':len(win),
                'median_winter_center_distance_km':statistics.median(win),
                'median_summer_center_distance_km':statistics.median(sumr),
                'mean_winter_center_distance_km':statistics.fmean(win),
                'mean_summer_center_distance_km':statistics.fmean(sumr),
                'fraction_pairs_winter_centers_closer':
                    sum(w<s for w,s in zip(win,sumr))/len(win)})
    if len(outcome)!=12:
        return {'status':'NOT_ESTIMABLE_PAIR_SAMPLES',
                'n_pairs':len(group_pairs),'seed_summaries':[]}
    return {'status':'DESCRIPTIVE_PAIRED_SOURCE_OBSERVATION_CENTRES',
            'n_pairs':len(group_pairs),
            'seed_summaries':outcome,
            'median_winter_distance_across_seeds_km':
                statistics.median(x['median_winter_center_distance_km'] for x in outcome),
            'median_summer_distance_across_seeds_km':
                statistics.median(x['median_summer_center_distance_km'] for x in outcome),
            'n_seeds_winter_mean_center_separation_lower':
                sum(x['mean_winter_center_distance_km']<
                    x['mean_summer_center_distance_km'] for x in outcome)}

def analyze(cache):
    timed,events,pinned=clock.get_original(SOURCE,cache)
    # Independent exact source clock/date/position multiset; do not assume
    # original UTC offset independently calibrated.
    byday=near._native_positions(SOURCE,cache,events)
    legacy=spatial._source_dual_archive(SOURCE)
    legacy_by_year={r['year']:r for r in legacy['source_year_results']}
    annual=geo.annual_day_balanced_centroids(events)
    season_centers={};season_dates={}
    for label,months in SEASONS.items():
        season_centers[label],season_dates[label]=seasonal_source_centres(events,months)
    output={
        'schema_version':1,'as_of':'2026-10-22',
        'status':'POST_INSPECTION_TURKEY_COMPONENT_AND_SOURCE_SEASON_CENTRES',
        'original_movebank_DOI':DOI,'source':'turkey',
        'source_original_MD5_and_pinned_SHA256_verified':True,
        'original_full_source_time_position_multiset_verified':True,
        'original_prior_L1_results_exactly_replayed':True,
        'original_accepted_GPS_fixes':len(events),
        'distance_filters_annual_centroid_km':[5,10,25],
        'nearby_position_radii_km':list(RADII),
        'native_clock_tolerances_seconds':list(GAPS),
        'n_source_seeds':len(SEEDS),
        'clock_UTC_offset_verified':False,
        'GPS_location_error_calibrated':False,
        'biological_population_independence_verified':False,
        'original_source_windows':{k:list(v) for k,v in SEASONS.items()},
        'annual_cohorts':[],
        'limitations':[
           'A source GPS centroid graph component is NOT an independently verified biological population',
           'Jan/Feb/Dec in same calendar year is not one connected winter or measured migration stage',
           'Exact original GPS sample time schedules and location accuracy are not independently calibrated',
           'A same-clock GPS near-position within 500m is not an animal physical encounter',
           'Paired dates and day-shift original path are observational and autocorrelated, not a causal randomized null',
           'Geographic annulus groups with <8 dyads are exploratory distances only; no supported independent L1 inference',
           'Animals/dyads/source years and 12 finite-source seeded samples are not independent biological replication',
           'Only anonymous group-level source aggregates are serialized; raw animal identities/positions are never stored']
    }
    for year in YEARS:
        baseline=clock._base_pair_set(events,year,annual)
        if len(baseline)!=(112 if year==2019 else 21):
            raise AssertionError('Original fixed turkey source/year pair mask changed')
        year_result={'year':year,'n_original_25km_pairs':len(baseline),
                     'time_tolerance_results':[]}
        previous={r['max_abs_original_GPS_time_gap_seconds']:r
                  for r in legacy_by_year[year]['time_tolerance_results']}
        for tol in GAPS:
            same_day=near._derive_opportunity(byday,baseline,year,tol)
            a=day.eligible_day_shift(byday,set(same_day),year,tol)
            b=day.eligible_day_shift(byday,{(y,x) for x,y in same_day},year,tol)
            eligible=set(a)&{(y,x) for x,y in b}
            expected=112 if year==2019 else 21
            if len(eligible)!=expected:
                raise AssertionError('Original pinned two-direction source dyad set changed')
            f={pair:a[pair] for pair in sorted(eligible)}
            rev={(p[1],p[0]):b[(p[1],p[0])] for p in sorted(eligible)}
            per_pair=spatial._per_pair_and_replay(
                f,rev,SOURCE,year,tol,
                previous[tol]['orientation_seed_radius_aggregates'])
            annual_dist={p:geo.centroid_distance_km(annual[year][p[0]],
                                                  annual[year][p[1]])
                         for p in eligible}
            groups=_group_sets(year,eligible,annual_dist)
            t={'time_tolerance_seconds':tol,'n_time_eligible_source_dyads':len(eligible),
               'geographic_groups':[]}
            for name,pairs in groups.items():
                summary=spatial._summary_for_edges(per_pair,pairs)
                if name.endswith('_component') and len(pairs)<MIN_ESTIMABLE_DYADS:
                    raise AssertionError('Source component is too small for fixed descriptive source test')
                row={'name':name,'n_pairs':len(pairs),
                     'n_source_animals':len(spatial._animals(pairs)),
                     'status':summary['status'],
                     'L1_relative_same_day_gps_proximity':summary['radii'],
                     'full_original_season_center_distances':{
                        'winter_vs_summer':
                            _pairwise_season_distance(pairs,season_centers,year),
                        'jan_feb_vs_summer':
                            _pairwise_season_distance(pairs,season_centers,year,
                                                     first='jan_feb'),
                        'dec_only_vs_summer':
                            _pairwise_season_distance(pairs,season_centers,year,
                                                     first='dec_only')},
                     'paired_source_time_supported_centroid_sensitivity':
                        _paired_sample_center_deltas(f,pairs,SOURCE,year,tol)}
                t['geographic_groups'].append(row)
            year_result['time_tolerance_results'].append(t)
            print(json.dumps({
                'source':'turkey','year':year,'time_gap_seconds':tol,
                'eligible_dyads':len(eligible),
                'components_within_5km':[
                   {'name':g['name'],'n_pairs':g['n_pairs'],
                    'n_animals':g['n_source_animals']}
                   for g in t['geographic_groups'] if 'component' in g['name']],
                'full_prior_A_B_scores_replayed':True},sort_keys=True),flush=True)
        output['annual_cohorts'].append(year_result)
    if output['original_accepted_GPS_fixes']!=435214:
        raise AssertionError('Full original source retained-fix count changed')
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='source_turkey_centres_') as temp:
        result=analyze(Path(temp))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({
        'status':result['status'],'original_fixes':result['original_accepted_GPS_fixes'],
        'aggregate_SHA256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'n_source_years':len(result['annual_cohorts'])},sort_keys=True))

if __name__=='__main__':
    main()
