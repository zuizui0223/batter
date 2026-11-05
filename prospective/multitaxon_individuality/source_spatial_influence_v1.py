#!/usr/bin/env python3
"""Source-verified spatial structure, repeated animals and leave-one-animal influence.

Exploratory post-outcome robustness on wild turkey, white-tailed deer and
black bear original published Movebank GPS. All original source files
are fetched complete and verified by the publisher MD5 and pinned SHA256,
source animal-tag joins and independently reconstituted time/position
multiset. Previously stored A/B reversal source aggregates must exactly
reconstruct from original per-dyad sampled GPS times/locations.

Original animal IDs, exact GPS dates/times, coordinates, dyad identities,
and cluster centroids remain **private within the ephemeral runner RAM**.
Only anonymous source-year count/distribution summaries are serialized.

A geographic component of annual GPS-use centers is NOT a verified local
biological population, and a matched GPS near-position is NOT a social
association, direct encounter, dietary overlap or causal ecological mechanism.
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
import day_shift_anchor_reverse_v1 as reversal

SOURCES = ('turkey', 'black_bear', 'white_tailed_deer')
YEARS = (2019, 2020)
TIME_TOLS = (900, 1800)
SPATIAL_THRESHOLDS_KM = (5.0, 10.0, 25.0)
RADII_KM = (0.5, 1.0, 2.0)
SEEDS = tuple(range(12))
DIRECTIONS = ('original_A_to_B', 'reversed_B_to_A')
MIN_DYADS = 8
MIN_ANIMALS = 3
SOURCE_DUAL_SHA256 = {
    'turkey': 'a5f61ffd8d34b2ac267fdf3f7d49eea508adafc690a306c9c8adbb2a1f985b5e',
    'black_bear': 'd7fae22468baf408265d1fe39da31c3688ae1c9ff06c7947ce3a568b4e4a5a37',
    'white_tailed_deer': 'd7066327a4329cae149ae85b3f57013e72fc81a6b6e65b8a47af4d0c932fe7d6',
}


def _near(a, b):
    return math.isclose(a, b, rel_tol=1e-10, abs_tol=3e-11)


def signs(seq):
    counts=Counter(1 if x > 1e-12 else -1 if x < -1e-12 else 0 for x in seq)
    return {'positive': counts[1], 'negative': counts[-1], 'near_zero': counts[0]}


def mean(seq):
    return statistics.fmean(seq)


def median(seq):
    return statistics.median(seq) if seq else None


def _animals(edges):
    return {a for p in edges for a in p}


def _component_counts(edges):
    """Anonymous complete component sizes only; no site or animal locator."""
    adj=defaultdict(set)
    for a,b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen=set()
    groups=[]
    for start in sorted(adj):
        if start in seen:continue
        queue=[start]; seen.add(start); members={start}
        while queue:
            q=queue.pop()
            for w in adj[q]-seen:
                seen.add(w);members.add(w);queue.append(w)
        n_edges=sum(a in members and b in members for a,b in edges)
        groups.append((len(members),n_edges))
    groups.sort(reverse=True)
    return {'n_connected_components':len(groups),
            'component_animal_counts':[x[0] for x in groups],
            'component_dyad_counts':[x[1] for x in groups],
            'n_components_meeting_3_animals_and_8_dyads':
                sum(a>=MIN_ANIMALS and b>=MIN_DYADS for a,b in groups),
            'n_component_pairs_sum':sum(x[1] for x in groups)}


def _summary_for_edges(per_pair, edges, radii=RADII_KM):
    pairs=sorted(edges)
    n=len(pairs)
    n_animals=len(_animals(pairs))
    if n<MIN_DYADS or n_animals<MIN_ANIMALS:
        return {'status':'NOT_ESTIMABLE_INSUFFICIENT_WITHIN_SOURCE_PAIR_SUPPORT',
                'n_pairs':n,'n_animals':n_animals,'radii':[]}
    table=[]
    for radius in radii:
        for di in DIRECTIONS:
            samples=[]
            for seed in SEEDS:
                vals=[per_pair[(di,p,seed,radius)] for p in pairs]
                samples.append(mean(vals))
            table.append({
                'radius_km':radius,'orientation':di,
                'winter_minus_summer_L_mean':mean(samples),
                'winter_minus_summer_L_seed_min':min(samples),
                'winter_minus_summer_L_seed_max':max(samples),
                'n_seed_draws':len(samples),
                'seed_signs':signs(samples),
            })
    return {'status':'DESCRIPTIVE_SOURCE_GPS_EDGE_SET_ONLY',
            'n_pairs':n,'n_animals':n_animals,'radii':table}


def _source_site_and_device_field_audit(source,cache,year_events,byday):
    """Column presence/coverage only; never leak original group/site/animal values."""
    uuid,_,_=geo.SOURCES[source]
    _,entries=geo._manifest(uuid)
    ref=[x for x in entries if x['role']=='reference']
    gps=[x for x in entries if x['role']=='gps']
    if len(ref)!=1 or not gps:raise AssertionError('Original source reference missing')
    refpath,_=geo._download(ref[0],cache)
    reference=list(geo._csv_rows(refpath,ref[0]['filename']))
    if not reference:raise AssertionError('No animal tag reference rows')
    columns=set(reference[0])
    gpspath,_=geo._download(gps[0],cache)
    event_columns=set(next(geo._csv_rows(gpspath,gps[0]['filename'])))
    # Explicit social/spatial/site labels are absent from these source
    # reference tables in the earlier source V2 replay.  Do not assume
    # that an animal-ID prefix is a biological population label.
    label_headers=sorted(c for c in columns if
        any(x in c.lower() for x in ('study-site','animal-group','population',
            'capture-site','capture-location-name','source-study-site')))
    accuracy_headers=sorted(c for c in columns|event_columns if
        any(x in c.lower() for x in ('gps-hdop','gps-vdop','gps-pdop',
            'location-error','location-accuracy','horizontal-accuracy',
            'gps-accuracy','satellite-count','fix-quality','gps-fix-type')))
    schedule_headers=sorted(c for c in columns if
        any(x in c.lower() for x in ('duty-cycle','duty cycle',
                                     'sampling-interval','fix-interval',
                                     'sampling-schedule','schedule')))
    local_site_count=set()
    for row in reference:
        animal=(row.get('animal-id') or '').strip()
        if animal and any((row.get(field) or '').strip() for field in label_headers):
            local_site_count.add(animal)
    nfix=[len(seq) for (year,month,animal,day),seq in byday.items() if year in YEARS]
    intervals=[]
    # Day-internal actual clock intervals; day ordering never crosses
    # midnight and UTC/GPS absolute clock basis is not claimed known.
    for seq in byday.values():
        if len(seq)<2:continue
        intervals.extend(b[0]-a[0] for a,b in zip(seq,seq[1:]) if b[0]>a[0])
    return {
        'reference_table_n_rows':len(reference),
        'reference_columns_present_but_no_values_shared':len(columns),
        'original_GPS_columns_present_but_no_values_shared':len(event_columns),
        'explicit_site_or_group_metadata_fields':label_headers,
        'animals_with_nonempty_explicit_site_field':len(local_site_count),
        'tag_schedule_fields':schedule_headers,
        'location_accuracy_or_GPS_quality_fields':accuracy_headers,
        'n_source_animal_calendar_dates':len(nfix),
        'median_observed_fixes_per_animal_day':median(nfix),
        'median_observed_within_day_interfix_seconds':median(intervals),
        'source_clock_basis_verified':False,
        'local_population_membership_verified':False,
        'tag_specific_GPS_location_error_calibrated':False,
        'note':'Nonempty generic site labels alone would not prove local population membership; no animal IDs or locations released.'}


def _source_dual_archive(source):
    path=Path(__file__).resolve().with_name(
        'DAY_SHIFT_DUAL_ANCHOR_'+source.upper()+'_2026_10_21.json')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_DUAL_SHA256[source]:
        raise AssertionError('Pinned dual-anchor whole-source result SHA256 changed')
    return json.loads(raw)


def _per_pair_and_replay(forward,backward,source,year,tol,archived):
    """Exact replay of prior source means from single-dyad source-GPS draws."""
    pairs=sorted(forward)
    by={}
    for seed in SEEDS:
        for pair in pairs:
            for di,orient,days in (
                    (DIRECTIONS[0],pair,forward[pair]),
                    (DIRECTIONS[1],(pair[1],pair[0]),backward[(pair[1],pair[0])])):
                rows=day._one_seed({orient:days},source,year,tol,seed)
                if len(rows)!=len(RADII_KM):
                    raise AssertionError('Single-dyad source source-GPS radius count changed')
                for item in rows:
                    r=float(item['radius_km'])
                    by[(di,pair,seed,r)]=item
    original={(x['direction'],x['seed'],float(x['radius_km'])):x
              for x in archived}
    if (len(original)!=len(SEEDS)*len(RADII_KM)*2 or
        set(original)!={(di,seed,r) for di in DIRECTIONS
                         for seed in SEEDS for r in RADII_KM}):
        raise AssertionError('Previously pinned original source results incomplete')
    for di in DIRECTIONS:
        for seed in SEEDS:
            for radius in RADII_KM:
                prior=original[(di,seed,radius)]
                if prior['n_dyads']!=len(pairs):
                    raise AssertionError('Original-source pair denominator changed')
                selected=[by[(di,p,seed,radius)] for p in pairs]
                for season in ('winter','summer'):
                    for metric in ('same','previous_day','next_day',
                                   'adjacent_day_reference','same_minus_adjacent'):
                        got=mean(x[season][metric] for x in selected)
                        if not _near(got,prior[season][metric]):
                            raise AssertionError('Original-source per-pair replay changed '+di)
                    for metric in ('same','previous_day','next_day'):
                        got=mean(x['mean_abs_source_clock_gap_seconds'][season][metric]
                                 for x in selected)
                        if not _near(got,prior['mean_abs_source_clock_gap_seconds'][season][metric]):
                            raise AssertionError('Original-time gap replay changed')
                got=mean(x['winter_minus_summer']['same_minus_adjacent'] for x in selected)
                if not _near(got,prior['winter_minus_summer']['same_minus_adjacent']):
                    raise AssertionError('Source seasonal L1 replay changed')
    return {(di,p,seed,r):data['winter_minus_summer']['same_minus_adjacent']
            for (di,p,seed,r),data in by.items()}


def _loo(per_pair,pairs):
    """Aggregate min/median/max influence. Individual removals stay private."""
    pairs=set(pairs)
    animals=sorted(_animals(pairs))
    out=[]
    for radius in RADII_KM:
        for direction in DIRECTIONS:
            metrics=[]
            for animal in animals:
                trimmed={p for p in pairs if animal not in p}
                if len(trimmed)<MIN_DYADS or len(_animals(trimmed))<MIN_ANIMALS:
                    continue
                seeds=[mean(per_pair[(direction,p,seed,radius)] for p in trimmed)
                       for seed in SEEDS]
                metrics.append({'average':mean(seeds),'signed':signs(seeds)})
            out.append({
                'radius_km':radius,
                'orientation':direction,
                'n_animal_deletions_attempted':len(animals),
                'n_estimable_animal_deletions':len(metrics),
                'n_unestimable_deletions':len(animals)-len(metrics),
                'source_animal_loo_delta_mean_range':
                    [min(m['average'] for m in metrics),max(m['average'] for m in metrics)]
                    if metrics else None,
                'source_animal_loo_delta_mean_median':
                    median([m['average'] for m in metrics]),
                'n_omissions_with_positive_mean':sum(m['average']>0 for m in metrics),
                'n_omissions_with_at_least_10_of_12_positive_source_draws':
                    sum(m['signed']['positive']>=10 for m in metrics),
                'smallest_positive_seed_count_among_omissions':
                    min(m['signed']['positive'] for m in metrics) if metrics else None,
                'all_valid_omissions_positive_10_of_12':
                    len(metrics)>0 and all(m['signed']['positive']>=10 for m in metrics),
            })
    return out


def analyze_source(source,cache):
    timed,original_events,pinned=clock.get_original(source,cache)
    byday=near._native_positions(source,cache,original_events)
    dual=_source_dual_archive(source)
    if dual['source']!=source:
        raise AssertionError('The source archive names do not agree')
    archived_years={x['year']:x for x in dual['source_year_results']}
    centers=geo.annual_day_balanced_centroids(original_events)
    result={
        'schema_version':1,'as_of':'2026-10-22',
        'status':'POST_INSPECTION_SPATIAL_CLUSTER_SUBJECT_INFLUENCE_AUDIT',
        'source':source,'source_doi':geo.SOURCES[source][1],
        'full_original_GPS_and_reference_MD5_SHA256_verified':True,
        'full_source_GPS_position_and_timestamp_multiset_replayed':True,
        'original_dual_anchor_aggregate_SHA256_exactly_verified':True,
        'source_original_fixes':len(original_events),
        'source_reference_audit':_source_site_and_device_field_audit(
            source,cache,original_events,byday),
        'distance_filter_thresholds_km':list(SPATIAL_THRESHOLDS_KM),
        'location_radii_km':list(RADII_KM),
        'time_tolerances_seconds':list(TIME_TOLS),
        'n_seeds':len(SEEDS),
        'original_year_results':[],
        'same_animal_and_pair_reuse_by_time_tolerance':[],
        'limits':['Spatial components are GPS-usage-centroid graph components, not biological populations',
                  'The 2019 and 2020 years can reuse original animals and pairs; report counts rather than claiming independent replication',
                  'LOO is sensitivity to removing one animal and its incident dyads, not an iid sampling or jackknife confidence interval',
                  'A same-day within-15/30min GPS distance pair is not an animal encounter, social contact or resource overlap',
                  'Missing 25km/10km/5km or tag metadata sources are NOT_ESTIMABLE/NOT_VERIFIED, not null effects',
                  'Post-inspection exploratory source-specific analysis, not a causal ecological law or significance test'],
    }
    all_year_sets={tol:{} for tol in TIME_TOLS}
    for year in YEARS:
        original_pairs=clock._base_pair_set(original_events,year,centers)
        expected_year=day.EXPECTED_V2_COUNTS[source][year]
        if len(original_pairs)!=expected_year[0]:
            raise AssertionError('Original 25-km source-year opportunity differs')
        old_year=archived_years[year]
        original_by_tol={x['max_abs_original_GPS_time_gap_seconds']:x
                         for x in old_year['time_tolerance_results']}
        row={'year':year,'n_original_geographic_dyads':len(original_pairs),
             'time_tolerance_rows':[]}
        for index,tol in enumerate(TIME_TOLS):
            same=near._derive_opportunity(byday,original_pairs,year,tol)
            if len(same)!=expected_year[index+1]:
                raise AssertionError('Original source time opportunity changed')
            forward=day.eligible_day_shift(byday,set(same),year,tol)
            reverse=day.eligible_day_shift(byday,{(b,a) for a,b in same},year,tol)
            valid=set(forward) & {(b,a) for a,b in reverse}
            prior=original_by_tol[tol]
            if len(valid)!=prior['n_both_orientation_supported_dyads']:
                raise AssertionError('Pinned dual-anchor matched dyad risk set changed')
            all_year_sets[tol][year]=valid
            animals=_animals(valid)
            entry={
                'tolerance_seconds':tol,
                'n_same_day_source_dyads':len(same),
                'n_both_direction_day_shift_dyads':len(valid),
                'n_source_animals_in_matched_pair_set':len(animals),
                'status':'SOURCE_PAIR_SET_GEOGRAPHIC_INFLUENCE_EXPLORATORY'
                         if prior['status'].startswith('DESCRIPTIVE_')
                         else 'STOP_PREVIOUS_SOURCE_TIME_OPPORTUNITY',
                'spatial_filters':[],
                'leave_one_animal_out':[],
                'original_result_reconstructed':False,
            }
            if entry['status'].startswith('STOP'):
                if prior['orientation_seed_radius_aggregates']:
                    raise AssertionError('Original source STOP was not empty')
                row['time_tolerance_rows'].append(entry)
                continue
            f={p:forward[p] for p in sorted(valid)}
            b={(p[1],p[0]):reverse[(p[1],p[0])] for p in sorted(valid)}
            per_pair=_per_pair_and_replay(f,b,source,year,tol,
                                        prior['orientation_seed_radius_aggregates'])
            entry['original_result_reconstructed']=True
            dist={pair:geo.centroid_distance_km(
                 centers[year][pair[0]],centers[year][pair[1]]) for pair in valid}
            for threshold in SPATIAL_THRESHOLDS_KM:
                subset={pair for pair in valid if dist[pair]<=threshold+1e-10}
                comp=_component_counts(subset)
                summary=_summary_for_edges(per_pair,subset)
                entry['spatial_filters'].append({
                    'threshold_km':threshold,
                    **comp,
                    **summary,
                })
            entry['leave_one_animal_out']=_loo(per_pair,valid)
            row['time_tolerance_rows'].append(entry)
            print(json.dumps({
                'source':source,'year':year,'time_tolerance_seconds':tol,
                'n_old_source_pairs':len(original_pairs),
                'n_valid_pairs':len(valid),
                'n_animals':len(animals),
                'n_5km_pairs':entry['spatial_filters'][0]['n_pairs'],
                'n_10km_pairs':entry['spatial_filters'][1]['n_pairs'],
                'n_25km_pairs':entry['spatial_filters'][2]['n_pairs'],
                'n_components_5km':entry['spatial_filters'][0]['n_connected_components'],
                'pinned_all_aggregate_scores_exact_replayed':True},sort_keys=True),flush=True)
        result['original_year_results'].append(row)
    for tol in TIME_TOLS:
        y1=all_year_sets[tol][2019]
        y2=all_year_sets[tol][2020]
        result['same_animal_and_pair_reuse_by_time_tolerance'].append({
            'tolerance_seconds':tol,
            'n_2019_matched_animals':len(_animals(y1)),
            'n_2020_matched_animals':len(_animals(y2)),
            'n_both_years_matched_animals':len(_animals(y1)&_animals(y2)),
            'n_2019_matched_pairs':len(y1),
            'n_2020_matched_pairs':len(y2),
            'n_both_years_matched_pair_identities':len(y1&y2),
            'independent_source_populations_established':False,
        })
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',choices=SOURCES,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='original_source_spatial_influence_') as temporary:
        data=analyze_source(args.source,Path(temporary))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps({
        'source':args.source,'status':data['status'],
        'original_source_fix_count':data['source_original_fixes'],
        'n_source_years':len(data['original_year_results']),
        'n_source_years_with_overlap_for_900s':
            next(x['n_both_years_matched_animals'] for x in
                 data['same_animal_and_pair_reuse_by_time_tolerance']
                 if x['tolerance_seconds']==900),
        'output_aggregate_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
    },sort_keys=True))


if __name__=='__main__':
    main()
