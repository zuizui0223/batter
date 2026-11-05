#!/usr/bin/env python3
"""Verify three pinned original-GPS source-only seasonal-centroid/component results.

Reconciles archived whole-original-source MD5/SHA256 lineage, unchanged
2019/2020 15/30-minute matched dyad supports, exactly predeclared
5/10/25km geographic components and three nearness radii, original
day-weighted seasonal GPS center distances and all original-size STOPs.
Never opens original GPS positions or individual source animal IDs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
RECEIPTS={
    'turkey':('092772996e15842fc91ca457ff29ee496734cb187ba4de0fd028f0f816a7d344',
              435214,'10.5441/001/1.671',{2019:112,2020:21}),
    'black_bear':('82ad383804ec897a9ddf890f4efc5961dacaf2ac6866efeb98496f15a7681f28',
                  148394,'10.5441/001/1.706',{2019:0,2020:5}),
    'white_tailed_deer':('226572d63c8eeacae189b3c1bfe6934ea4dcd4bc88b02f61bb87b79c999e93d5',
                         371080,'10.5441/001/1.718',{2019:55,2020:205})}
PRIOR_SHA256={'turkey':'8182bf56b2d8e25d3f5ead3ffc89cd74d5d57c78bc171c954438a585ee8f63e2',
              'white_tailed_deer':'19e035aa578ff4954a425201c9eb8074b89ed0a8753f71a1610a6db272d671b9',
              'black_bear':'2252cc771c8f8337d452cadc5c2abd5bd9d7ca5a2350e6893f9a98f547540bac'}
TOLS=(900,1800)
RADII=(.5,1.,2.)
CUTOFFS=(5.,10.,25.)
BANDS=('[0,5] km','(5,10] km','(10,25] km','[0,25] km')


def near(a,b):
    return math.isclose(a,b,rel_tol=1e-10,abs_tol=2e-10)


def _source_json(source,root):
    root=Path(root)
    p=root/('SEASONAL_GPS_CENTROID_COMPONENT_'+source.upper()+'_2026_10_22.json')
    temp=root/(source+'_seasonal_centroid_components_20261022.json')
    found=[x for x in (p,temp) if x.exists()]
    if not found:
        raise AssertionError('Original-source annual/season GPS geometric file unavailable')
    if len(found)==2 and found[0].read_bytes()!=found[1].read_bytes():
        raise AssertionError('Staged and published original-source study bytes differ')
    raw=found[0].read_bytes()
    if hashlib.sha256(raw).hexdigest()!=RECEIPTS[source][0]:
        raise AssertionError('Pinned original-source seasonal GPS analysis SHA256 changed')
    return json.loads(raw)


def _prior_source(source,root):
    path=Path(root)/('SOURCE_SPATIAL_INFLUENCE_'+source.upper()+'_2026_10_22.json')
    if not path.exists():
        # Staged new source outputs reside under /tmp, while the independently
        # pinned historical baseline resides in the checked-out repository.
        path=ROOT/('SOURCE_SPATIAL_INFLUENCE_'+source.upper()+'_2026_10_22.json')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PRIOR_SHA256[source]:
        raise AssertionError('Previous verified complete-source original-GPS spatial audit changed')
    return json.loads(raw)


def _season_score_check(s):
    n=s['n_source_pairs_with_both_season_centers']
    if (s['n_source_pairs_requested']!=n+s['n_unavailable_source_pair_season_centers']):
        raise AssertionError('Missing seasonal pair centered as zero distance')
    if s['season_center_comparison_is_not_real_time_encounter'] is not True:
        raise AssertionError('Actual animal encounter asserted')
    if n==0:
        if any(s.get(k) is not None for k in ('winter_km','summer_km','winter_minus_summer_km','fraction_pairs_winter_centers_closer')):
            raise AssertionError('Missing source GPS seasonal centroid coded as numeric')
        return
    if s['n_pairs_winter_centers_closer']+s['n_pairs_summer_centers_closer']>n:
        raise AssertionError('Seasonal pair distance signs exceed supported pairs')
    if not near(s['fraction_pairs_winter_centers_closer'],s['n_pairs_winter_centers_closer']/n):
        raise AssertionError('Source winter centroid closeness fraction inconsistent')
    for season in ('winter_km','summer_km'):
        x=s[season]
        if not (x['q10']<=x['median']<=x['q90'] and min(x.values())>=0):
            raise AssertionError('Source seasonal GPS geographic center-distance distribution invalid')
    delta=s['winter_minus_summer_km']
    if delta['q10']>delta['median'] or delta['median']>delta['q90']:
        raise AssertionError('Paired winter-minus-summer source GPS difference quantiles unordered')
    if not near(delta['mean'],s['winter_km']['mean']-s['summer_km']['mean']):
        raise AssertionError('Paired source GPS center distance means violate arithmetic identity')


def _component_check(row):
    n=row['n_component_original_dyads']; animals=row['n_component_original_animals']
    sub=row['original_source_component_L1_by_radius_direction']
    if sub['n_pairs']!=n or sub['n_animals']!=animals:
        raise AssertionError('Geographic component score denominators differ')
    if n<8 or animals<3:
        if sub['status']!='NOT_ESTIMABLE_INSUFFICIENT_WITHIN_SOURCE_PAIR_SUPPORT' or sub['radii']:
            raise AssertionError('Unsupported source component incorrectly scored')
        return
    if sub['status']!='DESCRIPTIVE_SOURCE_GPS_EDGE_SET_ONLY':
        raise AssertionError('Qualified original-source component not scored')
    keys={(r['radius_km'],r['orientation']) for r in sub['radii']}
    if keys!={(r,d) for r in RADII for d in ('original_A_to_B','reversed_B_to_A')} or len(sub['radii'])!=6:
        raise AssertionError('Source component lacks original A/B 12-seed radius outcomes')
    for r in sub['radii']:
        signs=r['seed_signs']
        if sum(signs.values())!=12 or r['n_seed_draws']!=12:
            raise AssertionError('Component seed comparison denominators incorrect')
        if not -1<=r['winter_minus_summer_L_mean']<=1:
            raise AssertionError('Source component proximity contrast outside [-1,1]')


def audit(directory=ROOT):
    output={'schema_version':1,'as_of':'2026-10-22',
            'status':'POST_INSPECTION_ORIGINAL_GPS_SPATIAL_COMPONENT_AND_SEASON_CENTROID_SUMMARY',
            'source_receipt_sha256':{k:v[0] for k,v in RECEIPTS.items()},
            'source_original_refs':'Movebank published publisher-MD5/whole-original pinned SHA256 and exact accepted time-position multiset checked in full source rerun',
            'n_original_GPS_source_archives':3,
            'n_source_year_time_tolerance_groups':0,
            'n_valid_source_year_time_tolerance_groups':0,
            'n_STOP_groups':0,
            'n_source_component_estimates':0,
            'n_source_season_centroid_distance_groups':0,
            'groups':[],'stops':[],
            'limits':['Spatially disconnected graph is not a biological population or social flock',
                      'Day-weighted seasonal GPS-use centroid separation is spatially descriptive, not actual synchronous animal encounter',
                      'Calendar-year Jan/Feb/Dec winter is nonconsecutive and tags have unknown GPS location error/time basis',
                      'Thresholds were fixed after previous results were inspected; no independent population p-values',
                      'Source animal/year/dyads/12 seed draws are dependent and never treated as independent field replication']}

    for source,(sha,fixes,doi,expected) in RECEIPTS.items():
        record=_source_json(source,directory)
        old=_prior_source(source,directory)
        if (record['source']!=source or record['source_doi']!=doi or
           record['accepted_complete_original_GPS_fix_count']!=fixes or
           record['status']!='POST_INSPECTION_ORIGINAL_SOURCE_SEASON_CENTROID_AND_SPATIAL_COMPONENT' or
           not record['publisher_original_MD5_and_prior_source_SHA256_verified'] or
           not record['independent_full_source_time_position_multiset_verified'] or
           not record['prior_original_source_geo_summary_SHA256_verified'] or
           not record['original_dual_anchor_replay_for_all_scored_component_dyads'] or
           record['local_biological_population_membership_verified'] or
           record['tag_specific_GPS_location_error_verified'] or
           record['native_GPS_source_clock_absolute_UTC_verified'] or
           record['fixed_geo_pair_distance_thresholds_km']!=list(CUTOFFS) or
           record['original_clock_tolerances_seconds']!=list(TOLS) or
           record['near_position_radii_km']!=list(RADII) or
           record['n_source_sampling_seeds']!=12):
            raise AssertionError('Original source/metadata/inference scope mismatch')
        current={r['year']:r for r in record['year_groups']}
        prior={r['year']:r for r in old['original_year_results']}
        if set(current)!={2019,2020} or set(prior)!={2019,2020}:
            raise AssertionError('Original source years 2019/2020 incomplete')
        for year in (2019,2020):
            now=current[year]
            past=prior[year]
            ns={r['tolerance_seconds']:r for r in now['tolerance_groups']}
            os={r['tolerance_seconds']:r for r in past['time_tolerance_rows']}
            if set(ns)!=set(TOLS) or set(os)!=set(TOLS):
                raise AssertionError('Original source time gaps missing')
            for tol in TOLS:
                row=ns[tol];ref=os[tol]
                if row['n_original_matched_source_dyads']!=ref['n_both_direction_day_shift_dyads']:
                    raise AssertionError('Source pair risk set differs from independently pinned source-year counts')
                output['n_source_year_time_tolerance_groups']+=1
                if row['status'].startswith('STOP'):
                    if row['annual_center_bands'] or row['components_by_annual_center_threshold']:
                        raise AssertionError('Stopped original time cohort exposed as effect')
                    output['n_STOP_groups']+=1
                    output['stops'].append({'source':source,'year':year,'tol_seconds':tol,
                        'n_old_original_dyads':ref['n_both_direction_day_shift_dyads'],
                        'status':row['status']})
                    continue
                if row['status']!='DESCRIPTIVE_GPS_GEOMETRIC_COMPONENTS_AND_SEASON_CENTERS':
                    raise AssertionError('Eligible original source not retained')
                output['n_valid_source_year_time_tolerance_groups']+=1
                annuli={v['annual_centroid_pair_separation_band']:v
                        for v in row['annual_center_bands']}
                if set(annuli)!=set(BANDS):
                    raise AssertionError('Source winter/summer geographic partitions not exhaustive')
                if sum(annuli[n]['n_qualified_source_dyads'] for n in BANDS[:-1]) != annuli[BANDS[-1]]['n_qualified_source_dyads']:
                    raise AssertionError('Exclusive annual centroid bands do not reproduce full original dyads')
                if annuli[BANDS[-1]]['n_qualified_source_dyads'] != ref['n_both_direction_day_shift_dyads']:
                    raise AssertionError('Annual GPS centroid pair mask changes past source denominator')
                for x in row['annual_center_bands']:
                    _season_score_check(x)
                    output['n_source_season_centroid_distance_groups']+=1
                comp_by_cut={x['centroid_pair_distance_cutoff_km']:x for x in
                             row['components_by_annual_center_threshold']}
                if set(comp_by_cut)!=set(CUTOFFS):
                    raise AssertionError('Geographic source graph cutoff grid missing')
                for km in CUTOFFS:
                    components=comp_by_cut[km]
                    priorcomp=next(x for x in ref['spatial_filters'] if x['threshold_km']==km)
                    xs=components['component_support']
                    if components['n_source_centroid_components_with_edges']!=len(xs):
                        raise AssertionError('Source component counts wrong')
                    if [x['n_component_original_dyads'] for x in xs]!=priorcomp['component_dyad_counts'] or \
                        [x['n_component_original_animals'] for x in xs]!=priorcomp['component_animal_counts']:
                        raise AssertionError('Original-source location-derived component composition differs')
                    for x in xs:
                        _component_check(x)
                        if x['original_source_component_L1_by_radius_direction']['status']=='DESCRIPTIVE_SOURCE_GPS_EDGE_SET_ONLY':
                            output['n_source_component_estimates']+=1
                output['groups'].append({
                    'source':source,'year':year,'time_gap_seconds':tol,
                    'n_source_dyads':row['n_original_matched_source_dyads'],
                    'anonymous_spatial_components':[
                         {'cutoff_km':x['centroid_pair_distance_cutoff_km'],
                          'components':x['component_support']}
                         for x in row['components_by_annual_center_threshold']],
                    'seasonal_GPS_center_distance_by_ANNUAL_center_band':
                         row['annual_center_bands'],
                    'explicit_population_membership_verified':False})
    if (output['n_source_year_time_tolerance_groups']!=12 or
        output['n_valid_source_year_time_tolerance_groups']!=8 or
        output['n_STOP_groups']!=4 or
        output['n_source_season_centroid_distance_groups']!=32):
        raise AssertionError('Declared source-year/gap original GPS seasonal group scope incomplete')
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,default=ROOT)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=audit(args.input_dir)
    data=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:args.output.write_text(data)
    else:print(data)
    print(json.dumps({'status':'PASS_SOURCE_GPS_SEASONAL_COMPONENTS',
       'n_source_archives':result['n_original_GPS_source_archives'],
       'n_eligible_groups':result['n_valid_source_year_time_tolerance_groups'],
       'n_stops':result['n_STOP_groups'],
       'n_component_estimates':result['n_source_component_estimates'],
       'n_season_distances':result['n_source_season_centroid_distance_groups']}))


if __name__=='__main__':
    main()
