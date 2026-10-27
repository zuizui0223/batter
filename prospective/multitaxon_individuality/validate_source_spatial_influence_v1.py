#!/usr/bin/env python3
"""Pinned original-GPS spatial influence source aggregator and integrity validator.

This is a SECONDARY transformation of fully reexecuted, whole-source MD5/SHA256
validated original public Movebank GPS outputs. No individual GPS locations,
IDs, dyad identities or per-animal results are accessed or serialized here.
Year reuse is tracked via private original-ID comparisons from the original
runner, and never reports names or sites.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean

ROOT=Path(__file__).resolve().parent
PINS={
 'turkey':('8182bf56b2d8e25d3f5ead3ffc89cd74d5d57c78bc171c954438a585ee8f63e2',
           435214,'10.5441/001/1.671',{2019:(112,19),2020:(21,7)},0,0),
 'black_bear':('2252cc771c8f8337d452cadc5c2abd5bd9d7ca5a2350e6893f9a98f547540bac',
             148394,'10.5441/001/1.706',{2019:(0,0),2020:(5,4)},0,0),
 'white_tailed_deer':('19e035aa578ff4954a425201c9eb8074b89ed0a8753f71a1610a6db272d671b9',
                     371080,'10.5441/001/1.718',{2019:(55,11),2020:(205,21)},11,55),
}
THRESHOLDS=(5.0,10.0,25.0)
RADIUS=(0.5,1.0,2.0)
TOLS=(900,1800)
DIRECTIONS=('original_A_to_B','reversed_B_to_A')
EPS=1e-10


def close(a,b):
    return math.isclose(a,b,abs_tol=EPS,rel_tol=1e-10)


def _pinned_source(root,source):
    path=Path(root)/('SOURCE_SPATIAL_INFLUENCE_'+source.upper()+'_2026_10_22.json')
    stage=Path(root)/(source+'_spatial_influence_20261022.json')
    found=[p for p in (path,stage) if p.exists()]
    if len(found)==0:raise AssertionError('Missing exact original-GPS source results')
    if len(found)>1 and found[0].read_bytes()!=found[1].read_bytes():
        raise AssertionError('Published and staging source results differ')
    raw=found[0].read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PINS[source][0]:
        raise AssertionError('Whole-source original-GPS output SHA256 does not match approved result')
    return json.loads(raw)


def _check_radii(summary,number):
    if summary['n_pairs']!=number or summary['n_animals']<3:
        raise AssertionError('Geographic subcohort denominator mismatch')
    if summary['status']!='DESCRIPTIVE_SOURCE_GPS_EDGE_SET_ONLY':
        raise AssertionError('Source geometry missed eligible comparison')
    rows=summary['radii']
    keys={(r['radius_km'],r['orientation']) for r in rows}
    if len(rows)!=6 or keys!={(r,d) for r in RADIUS for d in DIRECTIONS}:
        raise AssertionError('Source radius and orientation scan incomplete')
    for r in rows:
        mean=r['winter_minus_summer_L_mean']
        if not (-1<=mean<=1) or not (
            -1<=r['winter_minus_summer_L_seed_min']<=mean<=
            r['winter_minus_summer_L_seed_max']<=1):
            raise AssertionError('Source proximity contrast is out of range')
        signs=r['seed_signs']
        if sum(signs.values())!=12 or r['n_seed_draws']!=12:
            raise AssertionError('Seed signs do not cover exactly twelve source subsamples')
    return {(r['radius_km'],r['orientation']):r for r in rows}


def _check_loo(data,n_animals):
    if len(data)!=6 or {(x['radius_km'],x['orientation']) for x in data}!={(r,d)
        for r in RADIUS for d in DIRECTIONS}:
        raise AssertionError('Missing leave-one-individual source effects')
    for entry in data:
        if entry['n_animal_deletions_attempted']!=n_animals:
            raise AssertionError('Source deletion count no longer matches its original animals')
        support=entry['n_estimable_animal_deletions']
        missing=entry['n_unestimable_deletions']
        if support+missing!=n_animals:
            raise AssertionError('Dropped individual coded as null effect')
        if not (0<=entry['n_omissions_with_positive_mean']<=support and
                0<=entry['n_omissions_with_at_least_10_of_12_positive_source_draws']<=support):
            raise AssertionError('Source deletion signs exceed counts')
        if support:
            lo,hi=entry['source_animal_loo_delta_mean_range']
            med=entry['source_animal_loo_delta_mean_median']
            if not (-1<=lo<=med<=hi<=1):
                raise AssertionError('Source deletion mean range/median invalid')
            if not 0<=entry['smallest_positive_seed_count_among_omissions']<=12:
                raise AssertionError('Source min signed drawing count outside 0..12')
            if entry['all_valid_omissions_positive_10_of_12'] != (
                    entry['n_omissions_with_at_least_10_of_12_positive_source_draws']==support):
                raise AssertionError('LOO stability gate inconsistent with sampled data')
    return {(x['radius_km'],x['orientation']):x for x in data}


def _annulus(a,b,lo,hi,radius,direction):
    r0=a[(radius,direction)]['winter_minus_summer_L_mean']
    r1=b[(radius,direction)]['winter_minus_summer_L_mean']
    n0,n1=lo,hi
    if n0>n1:raise AssertionError('Spatial dyad set is not nested')
    if n0==n1:return None
    d=(n1*r1-n0*r0)/(n1-n0)
    if not -1.0000001<=d<=1.0000001:
        raise AssertionError('Derived geographic annulus mean out of range')
    return d


def validate(root=ROOT):
    report={
        'schema_version':1,'as_of':'2026-10-22',
        'status':'POST_INSPECTION_SOURCE_GPS_YEAR_REUSE_AND_SPATIAL_INFLUENCE_VALIDATED',
        'fixed_design':'SOURCE_SPATIAL_INFLUENCE_DESIGN_2026_10_22.md',
        'source_pinned_SHA256':{name:src[0] for name,src in PINS.items()},
        'n_original_source_studies':3,
        'n_source_year_tolerance_rows':0,
        'n_valid_original_dyad_groups':0,
        'n_stopped_source_year_tolerance_rows':0,
        'n_replayed_original_source_seed_radius_scores':0,
        'source_reference_metadata_audits':[],
        'year_reuse_audits':[],
        'summaries':[],
        'stop_groups':[],
        'limits':[
           'Annual-centroid spatial clusters do not certify local ecological or social populations',
           'No original animal IDs, GPS source coordinates or precise time/location records are published',
           'Yearly source cohorts can contain the same original animals; year overlap audited rather than assumed independent',
           'Component/geography cutoff and single-animal omission are exploratory sensitivity conditions, not calibrated null tests',
           'The only causal control is none: adjacent-day records can differ in weather, habitats and day-to-day animal mobility',
           'Near-time GPS distance <=500m/1km is not verified physical encounter, synchronized behavior or trophic niche separation',
           'Individual GPS accuracy, clock time basis, source tag duty cycles and verified populations remain unmeasured'],
    }
    for source,(digest,nfix,doi,years,expected_reuse,expected_dyad_reuse) in PINS.items():
        doc=_pinned_source(root,source)
        if (doc['source']!=source or doc['source_doi']!=doi or
             doc['source_original_fixes']!=nfix or
             doc['status']!='POST_INSPECTION_SPATIAL_CLUSTER_SUBJECT_INFLUENCE_AUDIT' or
             not doc['full_original_GPS_and_reference_MD5_SHA256_verified'] or
             not doc['full_source_GPS_position_and_timestamp_multiset_replayed'] or
             not doc['original_dual_anchor_aggregate_SHA256_exactly_verified'] or
             doc['distance_filter_thresholds_km']!=list(THRESHOLDS) or
             doc['location_radii_km']!=list(RADIUS) or
             doc['time_tolerances_seconds']!=list(TOLS) or
             doc['n_seeds']!=12):
            raise AssertionError('Original source identity, receipt or frozen analysis changed')
        meta=doc['source_reference_audit']
        if (meta['local_population_membership_verified'] or
            meta['source_clock_basis_verified'] or
            meta['tag_specific_GPS_location_error_calibrated']):
            raise AssertionError('Unverified original GPS site/time/error inference')
        if meta['animals_with_nonempty_explicit_site_field']!=0:
            raise AssertionError('Source site fields now present; new population stratification required')
        if meta['median_observed_within_day_interfix_seconds']!=3600:
            raise AssertionError('Original source sampling cadence changed')
        report['source_reference_metadata_audits'].append({'source':source,**meta})
        reuse={r['tolerance_seconds']:r for r in doc['same_animal_and_pair_reuse_by_time_tolerance']}
        if set(reuse)!=set(TOLS):
            raise AssertionError('Missing source year-reuse tolerances')
        for tol in TOLS:
            x=reuse[tol]
            if ((x['n_2019_matched_animals'],x['n_2020_matched_animals'],
                x['n_2019_matched_pairs'],x['n_2020_matched_pairs'])!=(
                years[2019][1],years[2020][1],years[2019][0],years[2020][0])):
                # Black bear 30 min includes 6 rather than 5 pairs;
                # the source-specific baseline is checked separately.
                if not (source=='black_bear' and tol==1800 and
                        x['n_2020_matched_pairs']==6 and
                        x['n_2020_matched_animals']==4 and
                        x['n_2019_matched_pairs']==0):
                    raise AssertionError('Original source animal/year pair risk sets changed')
            if x['n_both_years_matched_animals']!=expected_reuse or \
               x['n_both_years_matched_pair_identities']!=expected_dyad_reuse:
                raise AssertionError('Repeated original individual/year study support changed')
            if x['independent_source_populations_established']:
                raise AssertionError('Site independence asserted without biological evidence')
            report['year_reuse_audits'].append({'source':source,**x})
        indexed={r['year']:r for r in doc['original_year_results']}
        if set(indexed)!={2019,2020}:
            raise AssertionError('Missing source year cohort')
        for year in (2019,2020):
            yearblock=indexed[year]
            rows={x['tolerance_seconds']:x for x in yearblock['time_tolerance_rows']}
            if set(rows)!=set(TOLS):
                raise AssertionError('Missing source 15/30 minute cohort')
            for tol in TOLS:
                group=rows[tol]
                report['n_source_year_tolerance_rows']+=1
                matched=group['n_both_direction_day_shift_dyads']
                if source=='black_bear':
                    expected=0 if year==2019 else 5 if tol==900 else 6
                else:
                    expected=years[year][0]
                if matched!=expected:
                    raise AssertionError('Pinned dual-anchor original source pair count changed')
                if matched<8:
                    if group['status']!='STOP_PREVIOUS_SOURCE_TIME_OPPORTUNITY' or (
                            group['spatial_filters'] or group['leave_one_animal_out']):
                        raise AssertionError('Insufficient source original GPS not STOP')
                    report['stop_groups'].append({'source':source,'year':year,
                      'tol_seconds':tol,'supported_dyads':matched,'status':group['status']})
                    report['n_stopped_source_year_tolerance_rows']+=1
                    continue
                if group['status']!='SOURCE_PAIR_SET_GEOGRAPHIC_INFLUENCE_EXPLORATORY' or \
                    not group['original_result_reconstructed']:
                    raise AssertionError('Original per-dyad source GPS replay not guaranteed')
                if group['n_source_animals_in_matched_pair_set'] != years[year][1]:
                    raise AssertionError('Original source-year distinct animal count changed')
                filters={x['threshold_km']:x for x in group['spatial_filters']}
                if set(filters)!=set(THRESHOLDS):
                    raise AssertionError('Spatial sensitivity thresholds missing')
                if [filters[k]['n_pairs'] for k in THRESHOLDS] != sorted(
                        [filters[k]['n_pairs'] for k in THRESHOLDS]):
                    raise AssertionError('Original GPS centroid masks are not nested')
                if filters[25.0]['n_pairs']!=matched:
                    raise AssertionError('Original 25km source pair mask not complete')
                checked={}
                for cutoff in THRESHOLDS:
                    g=filters[cutoff]
                    if g['n_component_pairs_sum']!=g['n_pairs'] or (
                       sum(g['component_dyad_counts'])!=g['n_pairs']):
                        raise AssertionError('Geographic connected components miss pair edges')
                    if len(g['component_animal_counts'])!=g['n_connected_components'] or \
                       sum(g['component_animal_counts'])!=g['n_animals']:
                        raise AssertionError('Geographic connected components miss animal nodes')
                    if g['n_pairs'] >= 8 and g['n_animals']>=3:
                        checked[cutoff]=_check_radii(g,g['n_pairs'])
                    elif g['status']!='NOT_ESTIMABLE_INSUFFICIENT_WITHIN_SOURCE_PAIR_SUPPORT':
                        raise AssertionError('Geographic source subset support should STOP')
                low=checked.get(5.0)
                mid=checked.get(10.0)
                wide=checked[25.0]
                deletions=_check_loo(group['leave_one_animal_out'],years[year][1])
                report['n_valid_original_dyad_groups']+=1
                report['n_replayed_original_source_seed_radius_scores']+=72
                for cutoff in THRESHOLDS:
                    g=filters[cutoff]
                    audit={'source':source,'year':year,'tolerance_seconds':tol,
                          'centroid_pair_distance_max_km':cutoff,
                          'n_dyads':g['n_pairs'],'n_animals':g['n_animals'],
                          'component_animal_counts':g['component_animal_counts'],
                          'component_dyad_counts':g['component_dyad_counts'],
                          'n_distinct_source_geographic_components':g['n_connected_components'],
                          'n_large_source_geographic_components':
                             g['n_components_meeting_3_animals_and_8_dyads'],
                          'status':g['status'],
                          'radii':[]}
                    if cutoff in checked:
                        for radius in RADIUS:
                            for direction in DIRECTIONS:
                                s=checked[cutoff][(radius,direction)]
                                loo=deletions[(radius,direction)]
                                rec={'radius_km':radius,'orientation':direction,
                                     'mean_winter_minus_summer_L':s['winter_minus_summer_L_mean'],
                                     'n_positive_source_subsampling_seeds':s['seed_signs']['positive'],
                                     'n_negative_source_subsampling_seeds':s['seed_signs']['negative'],
                                     'n_animal_omissions_with_positive_10_of_12':
                                          loo['n_omissions_with_at_least_10_of_12_positive_source_draws']
                                          if cutoff==25.0 else None,
                                     'n_eligible_animal_deletions':loo['n_estimable_animal_deletions']
                                          if cutoff==25.0 else None,
                                     'animal_deletion_mean_min_max':
                                          loo['source_animal_loo_delta_mean_range'] if cutoff==25.0 else None,
                                     'conditional_annulus_means_exploratory':None}
                                if cutoff==25.0 and low is not None and mid is not None:
                                    a=filters[5.0]['n_pairs']
                                    b=filters[10.0]['n_pairs']
                                    c=filters[25.0]['n_pairs']
                                    m5=low[(radius,direction)]['winter_minus_summer_L_mean']
                                    m10=mid[(radius,direction)]['winter_minus_summer_L_mean']
                                    m25=wide[(radius,direction)]['winter_minus_summer_L_mean']
                                    rec['conditional_annulus_means_exploratory']={
                                        '0_5km_mean':m5,'n_0_5km_pairs':a,
                                        '5_10km_mean':(b*m10-a*m5)/(b-a) if b>a else None,
                                        'n_5_10km_pairs':b-a,
                                        '10_25km_mean':(c*m25-b*m10)/(c-b) if c>b else None,
                                        'n_10_25km_pairs':c-b,
                                        'note':'Algebraic pair-weighted means only. Annulus 12-seed sign frequencies cannot be inferred from group summaries.',
                                    }
                                    parts=[(a,m5),(b-a,rec['conditional_annulus_means_exploratory']['5_10km_mean']),
                                           (c-b,rec['conditional_annulus_means_exploratory']['10_25km_mean'])]
                                    if not close(sum(n*m for n,m in parts if m is not None)/c,m25):
                                        raise AssertionError('Disjoint annual-centroid annulus mean does not reconcile with 25km source mean')
                                audit['radii'].append(rec)
                    report['summaries'].append(audit)
    if report['n_source_year_tolerance_rows']!=12 or (
         report['n_valid_original_dyad_groups']!=8 or
         report['n_stopped_source_year_tolerance_rows']!=4 or
         report['n_replayed_original_source_seed_radius_scores']!=576):
        raise AssertionError('Original GPS geographic influence fixed source frame incomplete')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir',type=Path,default=ROOT)
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    result=validate(args.input_dir)
    content=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:args.output.write_text(content)
    else:print(content)
    print(json.dumps({'status':'PASS_ORIGINAL_SOURCE_SPATIAL_COHORT_INFLUENCE',
         'source_documents':result['n_original_source_studies'],
         'years_and_tolerances':result['n_source_year_tolerance_rows'],
         'valid':result['n_valid_original_dyad_groups'],
         'stops':result['n_stopped_source_year_tolerance_rows'],
         'replayed_source_seed_radius_scores':
             result['n_replayed_original_source_seed_radius_scores']}))


if __name__=='__main__':
    main()
