#!/usr/bin/env python3
"""Calendar-month geometry of source-verified original wild-turkey GPS tracks.

Post-inspection study of the single 2020 original tagged bird shared by
all five 10–25-km annual-center pairs, plus the two anonymous 2019 graph
components. Complete ORIGINAL Movebank GPS/reference publisher MD5 and
pinned SHA256, source calendar time/position QC and previous 2020 mover
receipts are reverified. NO original animal IDs, original exact dates,
individual monthly trajectories, GPS positions or GPS centroids are output.

Month-level descriptions are observations of one source's GPS geography,
NOT independently replicated local populations, proven migration, social
flock formation, resource partitioning or observed encounters.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
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
import turkey_component_season_centers_v1 as geometry

SOURCE='turkey'
DOI='10.5441/001/1.671'
YEAR_COUNTS={2019:112,2020:21}
MONTHS=tuple(range(1,13))
MIN_DATES_PER_ANIMAL_MONTH=7
PRIMARY_TOLERANCE_SECONDS=900
MIN_SUMMARY_PAIRS=3
MIN_SUMMARY_ANIMALS=3
MIN_ISOLATE_SUPPORT_CORE_ANIMALS=4
CLOSE_KM=1.
SEPARATED_KM=5.
EARTH_RADIUS_KM=6371.


def month_centroids(events,months=MONTHS,min_days=MIN_DATES_PER_ANIMAL_MONTH):
    """Compute date-equal unit-sphere animal/month center with explicit no-data.

    Private dict keys are original biological individual identifiers and may
    NEVER be serialized. One original observed day has one vote irrespective
    of 1-versus-100 GPS fixes; no interpolation of unobserved dates.
    """
    available={}
    dates={}
    for m in months:
        center,counts=geometry.seasonal_source_centres(events,(m,),min_dates=min_days)
        for year,group in center.items():
            available[(year,m)]=group
            dates[(year,m)]=counts[year]
    return available,dates


def _distance(a,b):
    return geo.centroid_distance_km(a,b)


def describe_distances(pairs,month_animal_centres,min_pairs=MIN_SUMMARY_PAIRS,
                       min_animals=MIN_SUMMARY_ANIMALS):
    """Aggregate monthly pair distances only. Never return pair IDs/coordinates."""
    values=[]
    covered=set()
    for a,b in pairs:
        if a not in month_animal_centres or b not in month_animal_centres:
            continue
        d=_distance(month_animal_centres[a],month_animal_centres[b])
        if not 0<=d<=math.pi*EARTH_RADIUS_KM+1e-6:
            raise AssertionError('Original GPS monthly great-circle distance invalid')
        values.append(d)
        covered.add(a); covered.add(b)
    result={'n_original_pairs':len(pairs),'n_valid_monthly_pairs':len(values),
            'n_animals_in_valid_monthly_pairs':len(covered),
            'eligible_pair_fraction':len(values)/len(pairs) if pairs else None}
    if len(values)<min_pairs or len(covered)<min_animals:
        result.update({'status':'NOT_ESTIMABLE_MONTHLY_SOURCE_SUPPORT',
                       'distance_km':None})
        return result
    result.update({'status':'DESCRIPTIVE_SOURCE_MONTH_CENTROID_DISTANCE',
                   'distance_km':{
                       'min':min(values),'median':statistics.median(values),
                       'mean':statistics.fmean(values),'max':max(values)}})
    return result


def transition_bracket(months):
    """First measured close-to-separated observation bracket, not a movement date."""
    supported=[r for r in months if r['state']!='UNOBSERVED']
    first=None
    for i,row in enumerate(supported):
        if row['state']!='SEPARATED':
            continue
        earlier=[candidate for candidate in supported[:i]
                 if candidate['state']=='CLOSE']
        if earlier:
            close=earlier[-1]
            inside=[r for r in months
                    if close['month']<r['month']<row['month']]
            first={'last_observed_close_month':close['month'],
                   'first_later_observed_separated_month':row['month'],
                   'months_strictly_between':len(inside),
                   'unobserved_months_in_bracket':sum(x['state']=='UNOBSERVED'
                                                      for x in inside),
                   'observed_intermediate_months_in_bracket':
                       sum(x['state']=='INTERMEDIATE' for x in inside),
                   'status':'OBSERVATION_BRACKET_NOT_TRACKED_TRANSITION_TIME'}
            break
    return first if first else {'status':'NO_SUPPORTED_CLOSE_TO_SEPARATED_BRACKET'}


def _pair_sets(events,byday):
    annual=geo.annual_day_balanced_centroids(events)
    result={}
    eligible_year={}
    for year in (2019,2020):
        geo_pairs=clock._base_pair_set(events,year,annual)
        if len(geo_pairs)!=YEAR_COUNTS[year]:
            raise AssertionError('Original published GPS prior geographic pairs changed')
        same=near._derive_opportunity(byday,geo_pairs,year,PRIMARY_TOLERANCE_SECONDS)
        f=day.eligible_day_shift(byday,set(same),year,PRIMARY_TOLERANCE_SECONDS)
        backward=day.eligible_day_shift(byday,{(b,a) for a,b in same},
                                        year,PRIMARY_TOLERANCE_SECONDS)
        eligible=set(f)&{(b,a) for a,b in backward}
        if len(eligible)!=YEAR_COUNTS[year]:
            raise AssertionError('Original source dual-anchor eligibility changed')
        eligible_year[year]=eligible
        members={a for a,b in eligible}|{b for a,b in eligible}
        annual_5km={p for p in eligible
                    if _distance(annual[year][p[0]],annual[year][p[1]])<=5+1e-10}
        components=geometry._components(annual_5km)
        if year==2019:
            if len(members)!=19 or [(len(a),len(p)) for a,p in components]!=[(11,53),(7,20)]:
                raise AssertionError('Known 2019 separated source graph components changed')
            labels=[
                ('all_25km_source_pairs',eligible,members),
                ('2019_larger_annual5_component',components[0][1],components[0][0]),
                ('2019_smaller_annual5_component',components[1][1],components[1][0]),
            ]
            result[year]={'groups':labels,'animals':members,
                          'component_animal_sizes':[11,7],
                          'component_pair_sizes':[53,20],
                          'components':components}
        else:
            if len(members)!=7 or len(components)!=1:
                raise AssertionError('2020 source original 7-animal sample was changed')
            core,graph_edges=components[0]
            isolated=members-core
            if len(core)!=6 or len(graph_edges)!=14 or len(isolated)!=1:
                raise AssertionError('Original 2020 <=5km annual-center core definition changed')
            iso=next(iter(isolated))
            within_core={p for p in eligible if p[0] in core and p[1] in core}
            iso_pairs={p for p in eligible if iso in p}
            far_pairs={p for p in eligible if
                       _distance(annual[year][p[0]],annual[year][p[1]])>10+1e-10}
            if len(within_core)!=15 or len(iso_pairs)!=6 or len(far_pairs)!=5:
                raise AssertionError('Original core/isolate source dyad denominators changed')
            if not far_pairs.issubset(iso_pairs):
                raise AssertionError('Five far dyads do not all share single original animal')
            labels=[
                ('all_25km_source_pairs',eligible,members),
                ('2020_six_member_annual5_core',within_core,core),
                ('2020_annual5_isolate_vs_core',iso_pairs,members),
                ('2020_annual10_to25_isolate_pairs',far_pairs,members),
            ]
            result[year]={'groups':labels,'animals':members,'core':core,
                          'isolate':iso,'far_pairs':far_pairs,
                          'component_animal_sizes':[6],
                          'component_pair_sizes':[14],
                          'components':components}
    common=result[2019]['animals'] & result[2020]['animals']
    if common:
        raise AssertionError('Different original turkey 2019/2020 year animal IDs unexpectedly reused')
    return result,annual


def analyze_original(events,byday,pinned):
    if len(events)!=435214:
        raise AssertionError('Original accepted turkey source fixes changed')
    groups,annual=_pair_sets(events,byday)
    centers,days=month_centroids(events)
    # Verify the original-source published single mover seasonal receipts.
    early,_=geometry.seasonal_source_centres(events,(1,2))
    summer,_=geometry.seasonal_source_centres(events,(6,7,8))
    iso=groups[2020]['isolate']
    core=groups[2020]['core']
    if not all(animal in early.get(2020,{}) and animal in summer.get(2020,{})
               for animal in groups[2020]['animals']):
        raise AssertionError('2020 core original seasonal GPS support changed')
    shift=_distance(early[2020][iso],summer[2020][iso])
    core_shift=statistics.median(
        _distance(early[2020][a],summer[2020][a]) for a in core)
    if not math.isclose(shift,14.52355751362658,abs_tol=3e-7) or not math.isclose(
            core_shift,.4550351589540801,abs_tol=3e-7):
        raise AssertionError('Prior published original-source 2020 mover receipt changed')
    report={
        'schema_version':1,'as_of':'2026-10-28',
        'source':'turkey','source_doi':DOI,
        'status':'POST_INSPECTION_ORIGINAL_GPS_ANONYMOUS_MONTHLY_CORE_GEOGRAPHY',
        'complete_original_source_MD5_and_pinned_SHA256_verified':True,
        'independent_original_time_position_multiset_verified':True,
        'original_2019_2020_GPS_fixes':len(events),
        'original_source_clock_UTC_basis_calibrated':False,
        'original_tag_GPS_error_calibrated':False,
        'independent_local_populations_verified':False,
        'monthly_original_date_support_threshold':MIN_DATES_PER_ANIMAL_MONTH,
        'source_year_eligible_animals':{'2019':19,'2020':7},
        'source_year_eligible_pairs':{'2019':112,'2020':21},
        'same_original_animal_IDs_in_2019_and_2020':0,
        'known_source_GPS_2020_isolate_janfeb_summer_shift_km':shift,
        'known_source_GPS_2020_six_core_median_shift_km':core_shift,
        'month_results':[],
        'transition_bracket_2020':None,
        'limits':[
            'Monthly SOURCE GEO centroid separation summarizes observed GPS habitat geometry, not social encounters',
            'One original tag generates all five far annual-center source pairs, not five biological replication events',
            'No original bird ID, calendar date/time, exact GPS or individual-level monthly trajectory is published',
            'Original source month coverage and GPS schedule/accuracy may affect observed seasonal geography',
            'Original animal group / capture-site membership not certified by published reference fields',
            'Change-point bracket identifies observed month categories only; do not infer actual movement dates or causes',
            '2019 two annual5 GPS components are not verified independent ecological populations',
            'No inferential p-value, true animal encounter, resource niche or taxon-general seasonal law'],
    }
    year_rows=[]
    for year in (2019,2020):
        animals=groups[year]['animals']
        result={'year':year,'n_source_eligible_animals':len(animals),
                'n_source_eligible_dyads':len(groups[year]['groups'][0][1]),
                'original_annual5_component_animal_sizes':groups[year]['component_animal_sizes'],
                'original_annual5_component_edge_sizes':groups[year]['component_pair_sizes'],
                'months':[]}
        for month in MONTHS:
            current=centers.get((year,month),{})
            source_counts=days.get((year,month),{})
            subset=animals & set(current)
            monthly_fixes=[v for v in events if v.year==year and v.month==month
                           and v.animal in animals]
            original_calendar_dates={(v.animal,v.day) for v in monthly_fixes}
            item={'month':month,
                  'n_eligible_animals_with_7_observed_days':len(subset),
                  'n_eligible_animals_with_any_fix':len({v.animal for v in monthly_fixes}),
                  'n_eligible_animal_calendar_dates':len(original_calendar_dates),
                  'n_eligible_original_GPS_fixes':len(monthly_fixes),
                  'n_source_animals_7day_centroid_supported':len(subset),
                  'group_centroid_pair_distances':[]}
            for label,pairs,member_set in groups[year]['groups']:
                pair_distance=describe_distances(pairs,current)
                item['group_centroid_pair_distances'].append(
                    {'group_label':label,'original_graph_n_animals':len(member_set),
                     **pair_distance})
            if year==2020:
                ncore=len(core&set(current))
                item['n_annual5_core_animals_7day_supported']=ncore
                item['annual5_isolated_animal_7day_supported']=iso in current
                item['source_tracking_completeness']=(
                    'FULLY_TRACKED_7_OF_7_MONTHLY_CENTRES'
                    if len(subset)==7 else 'PARTIAL_OR_NO_MONTHLY_CENTRE_SUPPORT')
                iso_stats=next(r for r in item['group_centroid_pair_distances']
                               if r['group_label']=='2020_annual5_isolate_vs_core')
                if (iso not in current or ncore<MIN_ISOLATE_SUPPORT_CORE_ANIMALS
                        or iso_stats['n_valid_monthly_pairs']<
                            MIN_ISOLATE_SUPPORT_CORE_ANIMALS):
                    state='UNOBSERVED'
                elif iso_stats['distance_km']['median']<=CLOSE_KM:
                    state='CLOSE'
                elif iso_stats['distance_km']['median']>=SEPARATED_KM:
                    state='SEPARATED'
                else:
                    state='INTERMEDIATE'
                item['isolate_vs_core_monthly_state']=state
            result['months'].append(item)
        year_rows.append(result)
    report['month_results']=year_rows
    states=[{'month':m['month'],'state':m['isolate_vs_core_monthly_state']}
            for m in year_rows[1]['months']]
    report['transition_bracket_2020']=transition_bracket(states)
    report['n_2020_months_full_seven_animal_support']=sum(
        m['source_tracking_completeness']=='FULLY_TRACKED_7_OF_7_MONTHLY_CENTRES'
        for m in year_rows[1]['months'])
    report['n_2020_months_isolate_vs_core_observed']=sum(
        m['isolate_vs_core_monthly_state']!='UNOBSERVED'
        for m in year_rows[1]['months'])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='original_turkey_monthly_geometry_') as temporary:
        cache=Path(temporary)
        timed,events,pinned=clock.get_original(SOURCE,cache)
        byday=near._native_positions(SOURCE,cache,events)
        result=analyze_original(events,byday,pinned)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps({
      'status':result['status'],'original_gps_fixes':result['original_2019_2020_GPS_fixes'],
      'month_rows':sum(len(y['months']) for y in result['month_results']),
      'monthly_2020_full_animal_support':result['n_2020_months_full_seven_animal_support'],
      'monthly_2020_isolate_core_support':result['n_2020_months_isolate_vs_core_observed'],
      'transition_bracket':result['transition_bracket_2020'],
      'output_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()},sort_keys=True))


if __name__=='__main__':
    main()
