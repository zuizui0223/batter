#!/usr/bin/env python3
"""Does one tagged wild turkey account for 2020 annual-far winter-centre convergence?

Original public Movebank DOI 10.5441/001/1.671 complete GPS/reference
MD5+SHA256 and independent source time/position QC checked before analysis.
Only source-year / anonymous GPS-center graph group statistics exported.
No original animal ID, map coordinate, exact date/time or source dyad-level
tracks leave the GitHub Actions runner.

Post-inspection exploratory geometric mechanism discriminator:
different 2020 original dyads sharing one tag are NOT independent
observed animal social interactions or direct encounters.
"""
from __future__ import annotations

import argparse
from collections import Counter
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
import turkey_component_season_centers_v1 as seasonal

SOURCE='turkey'
YEARS=(2019,2020)
TOL=900
EXPECTED_YEAR={2019:112,2020:21}
EARTH=6371.0

def _distance(a,b):
    return geo.centroid_distance_km(a,b)

def _distances_stats(values, *, signed=False):
    if not values:
        return {'n':0,'mean':None,'median':None,'min':None,'max':None}
    values=sorted(values)
    if not all((abs(x)<=math.pi*EARTH+1e-6 if signed else 0<=x<=math.pi*EARTH+1e-6) for x in values):
        raise AssertionError('Source seasonal centroid great-circle distance outside globe')
    return {'n':len(values),'mean':statistics.fmean(values),
            'median':statistics.median(values),
            'min':values[0],'max':values[-1]}

def _pair_annual_season_stats(pairs,annual,early,summer,year):
    vals={k:[] for k in ('annual','jan_feb','summer','jan_feb_minus_summer')}
    missing=[]
    for a,b in sorted(pairs):
        if a not in annual.get(year,{}) or b not in annual.get(year,{}):
            raise AssertionError('Original annual centroid expected for eligible original pair')
        annual_d=_distance(annual[year][a],annual[year][b])
        vals['annual'].append(annual_d)
        if (a not in early.get(year,{}) or b not in early.get(year,{})
                or a not in summer.get(year,{}) or b not in summer.get(year,{})):
            missing.append((a,b))
            continue
        w=_distance(early[year][a],early[year][b])
        s=_distance(summer[year][a],summer[year][b])
        vals['jan_feb'].append(w)
        vals['summer'].append(s)
        vals['jan_feb_minus_summer'].append(w-s)
    return {'n_original_source_pairs':len(pairs),
            'n_without_both_supported_source_season_centers':len(missing),
            'annual_centroid_separation_km':_distances_stats(vals['annual']),
            'jan_feb_centroid_separation_km':_distances_stats(vals['jan_feb']),
            'summer_centroid_separation_km':_distances_stats(vals['summer']),
            'jan_feb_minus_summer_distance_km':_distances_stats(vals['jan_feb_minus_summer'],signed=True),
            'n_source_pairs_closer_in_jan_feb':
                sum(v<0 for v in vals['jan_feb_minus_summer']),
            'n_source_pairs_farther_in_jan_feb':
                sum(v>0 for v in vals['jan_feb_minus_summer'])}

def _individual_seasonal_movement(animals,early,summer,year):
    displacement=[]
    for a in animals:
        if a in early.get(year,{}) and a in summer.get(year,{}):
            displacement.append(_distance(early[year][a],summer[year][a]))
    return _distances_stats(displacement)

def analyze(events,pinned,byday):
    if len(events)!=435214:
        raise AssertionError('Original turkey Movebank accepted 2019-20 GPS count changed')
    annual=geo.annual_day_balanced_centroids(events)
    early,earlydays=seasonal.seasonal_source_centres(events,(1,2))
    summer,summerdays=seasonal.seasonal_source_centres(events,(6,7,8))
    dec,dec_days=seasonal.seasonal_source_centres(events,(12,))
    result={
       'schema_version':1,'as_of':'2026-10-22',
       'status':'POST_INSPECTION_SINGLE_ORIGINAL_TURKEY_SEASONAL_MOVER_GEOGRAPHY',
       'source':'turkey','doi':'10.5441/001/1.671',
       'complete_original_source_MD5_SHA256_reference_verified':True,
       'independent_original_time_position_multiset_verified':True,
       'original_2019_2020_complete_GPS_fix_count':len(events),
       'source_native_clock_UTC_offset_calibrated':False,
       'original_GPS_location_error_calibrated':False,
       'source_population_labels_biologically_verified':False,
       'fixed_time_tolerance_seconds':900,
       'source_group_geometry_threshold_km':5,
       'annual_source_centroid_bands_km':(5,10,25),
       'data_windows':{'early_year':[1,2],'summer':[6,7,8],'december':[12]},
       'groups':[],
       'caveats':['One source 2020 animal with no <=5km eligible annual-centroid dyad is assigned by geometric graph, not local population or behavior',
                  'One 2020 tagged animal may occur in several distinct dyads; pair counts are not independent biological observations',
                  'Original GPS medians need not equal animal true position: fix accuracy/time clock unverified',
                  'Date-weighted source GPS centers describe observed seasonal geography, not contact/flocking/feeding',
                  'January-February is separated from December and is not a continuous overwintering stage',
                  'All source results post-inspection ecological mechanisms hypotheses only, not causal or population inference'],
    }
    by_year={}
    for year in YEARS:
        annual_pairs=clock._base_pair_set(events,year,annual)
        if len(annual_pairs)!=EXPECTED_YEAR[year]:
            raise AssertionError('Original source 25km dyad risk set changed')
        same=near._derive_opportunity(byday,annual_pairs,year,TOL)
        forward=day.eligible_day_shift(byday,set(same),year,TOL)
        backward=day.eligible_day_shift(byday,{(b,a) for a,b in same},year,TOL)
        eligible=set(forward)&{(b,a) for a,b in backward}
        if len(eligible)!=EXPECTED_YEAR[year]:
            raise AssertionError('Original source dual-anchor source dyad denominator changed')
        if year==2019:
            subset={p for p in eligible if
                 _distance(annual[year][p[0]],annual[year][p[1]])<=5+1e-10}
            comps=seasonal._components(subset)
            if [(len(a),len(p)) for a,p in comps]!=[(11,53),(7,20)]:
                raise AssertionError('Original source 2019 sample geographic structure changed')
            group={'year':2019,'total_dual_anchor_dyads':len(eligible),
                   'n_original_eligible_animals':len(seasonal.spatial._animals(eligible)),
                   'anonymous_5km_components':[]}
            for idx,(members,edges) in enumerate(comps):
                group['anonymous_5km_components'].append({
                    'size_rank':idx+1,'n_source_animals':len(members),
                    'n_original_dyads':len(edges),
                    'individual_jan_feb_to_summer_movement_km':
                        _individual_seasonal_movement(members,early,summer,year),
                    'pair_source_centers':
                        _pair_annual_season_stats(edges,annual,early,summer,year)})
            result['groups'].append(group)
        else:
            members=seasonal.spatial._animals(eligible)
            near5={p for p in eligible if
                   _distance(annual[year][p[0]],annual[year][p[1]])<=5+1e-10}
            near_graph=seasonal._components(near5)
            if len(members)!=7 or len(eligible)!=21 or len(near_graph)!=1:
                raise AssertionError('2020 source original fixed 7-animal 25km complete graph changed')
            core,core_edges=near_graph[0]
            if len(core)!=6 or len(core_edges)!=14:
                raise AssertionError('2020 original GPS annual5 core source structure changed')
            isolated=members-core
            if len(isolated)!=1:
                raise AssertionError('2020 annual 5km graph did not leave exactly one source animal')
            isolated_animal=next(iter(isolated))
            core_core={p for p in eligible if p[0] in core and p[1] in core}
            isolated_core={p for p in eligible if isolated_animal in p}
            if len(core_core)!=15 or len(isolated_core)!=6:
                raise AssertionError('2020 source 7-animal complete graph decomposition changed')
            outer5={p for p in eligible if
                    _distance(annual[year][p[0]],annual[year][p[1]])>5+1e-10}
            outer10={p for p in eligible if
                     _distance(annual[year][p[0]],annual[year][p[1]])>10+1e-10}
            between5_10=outer5-outer10
            if (len(outer5),len(outer10),len(between5_10))!=(7,5,2):
                raise AssertionError('Original 2020 source outer dyad classes changed')
            if (isolated_animal not in early.get(2020,{})
                 or isolated_animal not in summer.get(2020,{})):
                raise AssertionError('Unique source islanded animal lacks sufficient recorded season dates')
            displaced=_distance(early[2020][isolated_animal],
                                summer[2020][isolated_animal])
            core_shifts=[_distance(early[2020][a],summer[2020][a])
                          for a in core if a in early.get(2020,{})
                          and a in summer.get(2020,{})]
            if len(core_shifts)!=6:
                raise AssertionError('One or more of six source graph core animals lack season fixes')
            group={
               'year':2020,'total_dual_anchor_dyads':len(eligible),
               'n_original_eligible_animals':7,
               'annual_5km_graph_core_n_animals':len(core),
               'annual_5km_graph_core_n_dyads':len(core_edges),
               'unique_annual5_isolated_original_animal_n':1,
               'original_source_graph_topology':{
                   'n_all_25km_dyads':len(eligible),
                   'n_core_core_dyads_all_25km':len(core_core),
                   'n_isolated_core_dyads_all_25km':len(isolated_core),
                   'n_annual5_to25km_dyads':len(outer5),
                   'n_outer5_dyads_incident_to_isolated_animal':
                       sum(isolated_animal in p for p in outer5),
                   'n_annual10_to25km_dyads':len(outer10),
                   'n_outer10_dyads_incident_to_isolated_animal':
                       sum(isolated_animal in p for p in outer10),
                   'n_annual5_to10km_dyads':len(between5_10),
                   'n_outer5_to10_dyads_incident_to_isolated_animal':
                       sum(isolated_animal in p for p in between5_10),
               },
               'unique_annual5_isolated_individual_janfeb_to_summer_center_shift_km':
                   displaced,
               'six_animal_annual5_core_individual_janfeb_to_summer_shift_km':
                   _distances_stats(core_shifts),
               'n_core_animals_with_greater_seasonal_shift_than_isolated':
                   sum(x>displaced for x in core_shifts),
               'source_geographic_groups':{
                   'all_eligible_25km':_pair_annual_season_stats(
                        eligible,annual,early,summer,2020),
                   'within_core_15_pairs':_pair_annual_season_stats(
                        core_core,annual,early,summer,2020),
                   'isolate_to_core_6_pairs':_pair_annual_season_stats(
                        isolated_core,annual,early,summer,2020),
                   'annual_5_to25km_7_pairs':_pair_annual_season_stats(
                        outer5,annual,early,summer,2020),
                   'annual_10_to25km_5_pairs':_pair_annual_season_stats(
                        outer10,annual,early,summer,2020),
               },
               'n_2020_animals_with_at_least7_source_december_observed_dates':
                    sum(a in dec.get(2020,{}) for a in members),
               'n_2020_animals_with_at_least7_janfeb_dates':
                    sum(a in early.get(2020,{}) for a in members),
               'n_2020_animals_with_at_least7_summer_dates':
                    sum(a in summer.get(2020,{}) for a in members),
            }
            result['groups'].append(group)
        by_year[year]=eligible
    reused=len(seasonal.spatial._animals(by_year[2019]) &
               seasonal.spatial._animals(by_year[2020]))
    if reused!=0:
        raise AssertionError('Previously verified distinct 2019/2020 original turkey tags overlap')
    result['n_reused_original_animal_IDs_between_years']=reused
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='turkey_source_single_mover_') as tmp:
        timed,accepted,pinned=clock.get_original(SOURCE,Path(tmp))
        byday=near._native_positions(SOURCE,Path(tmp),accepted)
        report=analyze(accepted,pinned,byday)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    g=next(g for g in report['groups'] if g['year']==2020)
    print(json.dumps({'status':report['status'],'source':'turkey',
                      'original_fixes':report['original_2019_2020_complete_GPS_fix_count'],
                      'n_2020_outer5_incident_to_isolate':
                        g['original_source_graph_topology']['n_outer5_dyads_incident_to_isolated_animal'],
                      'n_2020_outer10_incident_to_isolate':
                        g['original_source_graph_topology']['n_outer10_dyads_incident_to_isolated_animal'],
                      'output_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()},sort_keys=True))

if __name__=='__main__':
    main()
