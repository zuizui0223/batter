#!/usr/bin/env python3
"""Audit the pinned 2020 single-mover source-GPS ecological geometry result.

Consumes a completed, publisher-MD5 and original-SHA256-verified Movebank
wild-turkey *aggregate-only* JSON. Never downloads or serializes original
animal IDs, exact dates, locations or individual tracking paths.
Any same-animal dependent dyads are explicitly NOT independent populations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = '7b84c27d0b05449e0a53dc465964c7fd0c8c3aed81478556387cb706598f4225'
ORIGINAL_NAME = 'TURKEY_SINGLE_MOVER_ORIGINAL_GPS_2026_10_22.json'
PUBLISHED_NAME = ORIGINAL_NAME
EPS = 1e-8


def close(x,y):
    return math.isclose(x,y,rel_tol=1e-10,abs_tol=EPS)


def _size_stats(stats, n, signed=False):
    if set(stats) != {'n','mean','median','min','max'}:
        raise AssertionError('Unexpected group summary schema')
    if stats['n'] != n or n < 1:
        raise AssertionError('Wrong animal or dyad sample denominator')
    vals=(stats['min'],stats['mean'],stats['median'],stats['max'])
    if any(isinstance(v,bool) or not isinstance(v,(int,float))
           or not math.isfinite(v) for v in vals):
        raise AssertionError('Invalid distance summary')
    if vals[0] > vals[1]+EPS or vals[1] > vals[3]+EPS or not vals[0]-EPS <= vals[2] <= vals[3]+EPS:
        raise AssertionError('Source distance summary order invalid')
    if not signed and stats['min'] < -EPS:
        raise AssertionError('Negative unsigned geodesic distance')
    if max(abs(v) for v in vals) > math.pi*6371.0+1e-6:
        raise AssertionError('Interanimal great-circle separation beyond globe')


def _pair_group(g, expected_n, *, expected_closer=None):
    keys={'n_original_source_pairs','n_without_both_supported_source_season_centers',
          'annual_centroid_separation_km','jan_feb_centroid_separation_km',
          'summer_centroid_separation_km','jan_feb_minus_summer_distance_km',
          'n_source_pairs_closer_in_jan_feb','n_source_pairs_farther_in_jan_feb'}
    if set(g)!=keys or g['n_original_source_pairs']!=expected_n:
        raise AssertionError('Geographic group source-year dyad count changed')
    m=g['n_without_both_supported_source_season_centers']
    if not isinstance(m,int) or m<0 or m>expected_n:
        raise AssertionError('Missing winter/summer centers must not be coded zero')
    valid=expected_n-m
    _size_stats(g['annual_centroid_separation_km'],expected_n)
    if not valid:
        return
    for name in ('jan_feb_centroid_separation_km','summer_centroid_separation_km'):
        _size_stats(g[name],valid)
    _size_stats(g['jan_feb_minus_summer_distance_km'],valid,signed=True)
    if not close(g['jan_feb_centroid_separation_km']['mean']
                 -g['summer_centroid_separation_km']['mean'],
                 g['jan_feb_minus_summer_distance_km']['mean']):
        raise AssertionError('Paired seasonal-centre distance delta not additive')
    near,far=(g['n_source_pairs_closer_in_jan_feb'],g['n_source_pairs_farther_in_jan_feb'])
    if any(not isinstance(v,int) or v<0 or v>valid for v in (near,far)):
        raise AssertionError('Source dyad seasonal center labels invalid')
    if near+far>valid:
        raise AssertionError('A dyad classified as both closer and farther')
    if expected_closer is not None and near!=expected_closer:
        raise AssertionError('Original source winter center-nearer tally mismatch')


def _source_document(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=SOURCE_SHA256:
        raise AssertionError('Original GPS source output SHA256 mismatch')
    d=json.loads(b)
    required={'annual_source_centroid_bands_km','as_of','caveats',
              'complete_original_source_MD5_SHA256_reference_verified',
              'data_windows','doi','fixed_time_tolerance_seconds','groups',
              'independent_original_time_position_multiset_verified',
              'n_reused_original_animal_IDs_between_years',
              'original_2019_2020_complete_GPS_fix_count',
              'original_GPS_location_error_calibrated','schema_version','source',
              'source_group_geometry_threshold_km',
              'source_native_clock_UTC_offset_calibrated',
              'source_population_labels_biologically_verified','status'}
    if set(d)!=required:
        raise AssertionError('Unexpected source schema; possible unsupported source fields')
    if (d['schema_version']!=1 or d['source']!='turkey'
        or d['doi']!='10.5441/001/1.671'
        or d['status']!='POST_INSPECTION_SINGLE_ORIGINAL_TURKEY_SEASONAL_MOVER_GEOGRAPHY'
        or d['original_2019_2020_complete_GPS_fix_count']!=435214
        or d['n_reused_original_animal_IDs_between_years']!=0
        or not d['complete_original_source_MD5_SHA256_reference_verified']
        or not d['independent_original_time_position_multiset_verified']
        or d['original_GPS_location_error_calibrated']
        or d['source_native_clock_UTC_offset_calibrated']
        or d['source_population_labels_biologically_verified']
        or d['fixed_time_tolerance_seconds']!=900
        or d['source_group_geometry_threshold_km']!=5
        or d['annual_source_centroid_bands_km']!=[5,10,25]
        or d['data_windows']!={'early_year':[1,2],'summer':[6,7,8],'december':[12]}
        or len(d['groups'])!=2):
        raise AssertionError('Original source manifest or biological STOP facts have changed')
    return d


def derive(path):
    d=_source_document(path)
    groups={g['year']:g for g in d['groups']}
    if set(groups)!={2019,2020}:
        raise AssertionError('Missing 2019/2020 source cohorts')
    old=groups[2019]
    if (old['n_original_eligible_animals'],old['total_dual_anchor_dyads'])!=(19,112):
        raise AssertionError('2019 original GPS cohort changed')
    comps=old['anonymous_5km_components']
    if len(comps)!=2:
        raise AssertionError('Expected two disconnected 2019 source geographic components')
    summary2019=[]
    for comp,(na,np,closer) in zip(comps,[(11,53,38),(7,20,17)]):
        if (comp['n_source_animals'],comp['n_original_dyads'])!=(na,np):
            raise AssertionError('Original component structure changed')
        _size_stats(comp['individual_jan_feb_to_summer_movement_km'],na)
        _pair_group(comp['pair_source_centers'],np,expected_closer=closer)
        summary2019.append({
            'n_source_animals':na,'n_original_annual5_geographic_dyads':np,
            'jan_feb_closer_than_summer_dyads':closer,
            'median_janfeb_pair_center_distance_km':
                comp['pair_source_centers']['jan_feb_centroid_separation_km']['median'],
            'median_summer_pair_center_distance_km':
                comp['pair_source_centers']['summer_centroid_separation_km']['median'],
        })
    if sum(s['n_original_annual5_geographic_dyads'] for s in summary2019)!=73:
        raise AssertionError('2019 source annual5 component pair count mismatches')

    new=groups[2020]
    if (new['n_original_eligible_animals'],new['total_dual_anchor_dyads'],
        new['annual_5km_graph_core_n_animals'],
        new['annual_5km_graph_core_n_dyads'],
        new['unique_annual5_isolated_original_animal_n'])!=(7,21,6,14,1):
        raise AssertionError('2020 one outsider plus six source GPS core animals changed')
    topo=new['original_source_graph_topology']
    expect={'n_all_25km_dyads':21,'n_core_core_dyads_all_25km':15,
        'n_isolated_core_dyads_all_25km':6,'n_annual5_to25km_dyads':7,
        'n_outer5_dyads_incident_to_isolated_animal':6,
        'n_annual10_to25km_dyads':5,
        'n_outer10_dyads_incident_to_isolated_animal':5,
        'n_annual5_to10km_dyads':2,
        'n_outer5_to10_dyads_incident_to_isolated_animal':1}
    if topo!=expect:
        raise AssertionError('Source GPS repeated one animal in five far dyads is not reproducible')
    if topo['n_core_core_dyads_all_25km']+topo['n_isolated_core_dyads_all_25km']!=21:
        raise AssertionError('Original complete dyad graph partition inconsistent')
    if topo['n_annual5_to25km_dyads']!=topo['n_annual5_to10km_dyads']+topo['n_annual10_to25km_dyads']:
        raise AssertionError('Annulus source dyads not a partition')
    if new['n_2020_animals_with_at_least7_janfeb_dates']!=7 or new['n_2020_animals_with_at_least7_summer_dates']!=7:
        raise AssertionError('Missing sample support for seasonal original GPS centers')
    if new['n_2020_animals_with_at_least7_source_december_observed_dates']!=0:
        raise AssertionError('Unsupported December seasonal location contrast introduced')
    core=new['six_animal_annual5_core_individual_janfeb_to_summer_shift_km']
    _size_stats(core,6)
    moved=new['unique_annual5_isolated_individual_janfeb_to_summer_center_shift_km']
    if not isinstance(moved,(int,float)) or not 0<=moved<=math.pi*6371.0:
        raise AssertionError('Isolated animal seasonal center shift invalid')
    if new['n_core_animals_with_greater_seasonal_shift_than_isolated']!=0 or moved<=core['max']:
        raise AssertionError('Unique original mover not larger than all six core shifts')
    group_n={'all_eligible_25km':21,'within_core_15_pairs':15,
        'isolate_to_core_6_pairs':6,'annual_5_to25km_7_pairs':7,
        'annual_10_to25km_5_pairs':5}
    seasonal=new['source_geographic_groups']
    if set(seasonal)!=set(group_n):
        raise AssertionError('Missing declared original GPS source annulus')
    for key,n in group_n.items():
        _pair_group(seasonal[key],n,expected_closer={
           'all_eligible_25km':18,'within_core_15_pairs':12,
           'isolate_to_core_6_pairs':6,'annual_5_to25km_7_pairs':7,
           'annual_10_to25km_5_pairs':5}[key])
    outer=seasonal['annual_10_to25km_5_pairs']
    isolate=seasonal['isolate_to_core_6_pairs']
    if (not outer['jan_feb_centroid_separation_km']['median']<
             outer['summer_centroid_separation_km']['median']):
        raise AssertionError('Published winter convergence did not reproduce')
    if not close(isolate['jan_feb_centroid_separation_km']['median'],
                 0.1007565627245268):
        raise AssertionError('Frozen original isolate-core Jan-Feb center summary altered')
    return {
       'schema_version':1,'as_of':'2026-10-23',
       'status':'PINNED_ORIGINAL_GPS_TURKEY_SOURCE_SINGLE_MOVER_VERIFIED',
       'source_doi':'10.5441/001/1.671','source_original_GPS_fixes':435214,
       'source_result_sha256':SOURCE_SHA256,
       'source_CI':'https://github.com/zuizui0223/batter/actions/runs/39722998742',
       'source_populations_independent_verified':False,
       'GPS_clock_and_location_error_calibrated':False,
       'yearly_eligible_animal_ID_sets_reused':0,
       'year_2019_components':summary2019,
       'year_2020':{
         'tracked_animals':7,'all_pairs':21,
         'near5_annual_center_core_animals':6,'near5_annual_center_core_edges':14,
         'annual5_isolated_animal_count':1,
         'n_annual10_to25km_pairs':5,
         'n_annual10_to25km_pairs_sharing_isolated_source_animal':5,
         'n_annual5_to25km_pairs_sharing_isolated_source_animal':6,
         'isolated_original_animal_janfeb_to_summer_center_shift_km':moved,
         'six_core_animal_source_shift_median_km':core['median'],
         'six_core_animal_source_shift_max_km':core['max'],
         'isolated_shift_relative_to_core_median':moved/core['median'],
         'annual10_to25km_pairs_summer_center_median_km':
             outer['summer_centroid_separation_km']['median'],
         'annual10_to25km_pairs_janfeb_center_median_km':
             outer['jan_feb_centroid_separation_km']['median'],
         'n_far_pairs_closer_in_janfeb_than_summer':outer['n_source_pairs_closer_in_jan_feb'],
         'isolated_core_6pairs_JF_median_km':
             isolate['jan_feb_centroid_separation_km']['median'],
         'isolated_core_6pairs_summer_median_km':
             isolate['summer_centroid_separation_km']['median'],
         'december_2020_supported_original_animals':0,
       },
       'nonclaims':[
          'Five original far pair records are one focal animal appearing five times, NOT independent biological events',
          '2020 isolate in annual5 GPS graph is not independently proven migrant, flock member or local population',
          'GPS centers describe recorded usage, not the mechanism of movement or social interactions',
          '2019 geographically disconnected groups are not verified independent demographic populations',
          'GPS accuracy, source clock calibration, resources and predation are not controlled',
          'Seasonal early-year means Jan-Feb, NOT continuous winter; December 2020 unavailable',
       ],
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,default=HERE)
    p.add_argument('--output',type=Path)
    p.add_argument('--compare',type=Path)
    args=p.parse_args()
    source=args.input_dir/PUBLISHED_NAME
    result=derive(source)
    text=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.compare:
        if json.loads(args.compare.read_text())!=result:
            raise AssertionError('Saved aggregate interpretation differs from pinned original-source receipt')
    if args.output:args.output.write_text(text)
    else:print(text,end='')
    print('PASS pinned turkey source original GPS single-mover geography, one tag repeated across five dyads')


if __name__=='__main__':
    main()
