#!/usr/bin/env python3
"""Same-day versus adjacent-day original-GPS trajectory proximity diagnostic.

Full original public Movebank source GPS/reference verified against publisher
MD5 and prior SHA256. The original-source date/time/coordinate/animal
multiset is independently reconstructed; no raw tracks, locations, exact
timestamps or animal/dyad identifiers are emitted.

POST-INSPECTION comparison, NOT a biological no-interaction null:
on the same source-clock time-of-day, pair focal animal A's original
GPS positions with B's original positions on the same, previous and next
calendar days, with exactly the SAME focal A fix serving all treatments.
Adjacent-day B sequences retain their time order and original locations.
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
import subhour_geodesic_proximity_v1 as geodesic
import subhour_timestamp_opportunity_v1 as screening

SOURCES = ('turkey', 'black_bear', 'white_tailed_deer')
YEARS = (2019, 2020)
WINTER, SUMMER = (1, 2, 12), (6, 7, 8)
TOLERANCES = (900, 1800)
RADII_KM = (0.5, 1., 2.)
SEEDS = tuple(range(12))
MIN_MATCHED_FIXES_PER_DAY = 3
MIN_COMMON_DATES_PER_MONTH = 7
MONTHS_PER_SEASON = 2
MIN_SUPPORTED_DYADS = 8
MIN_SUPPORTED_ANIMALS = 3
EXPECTED_V2_COUNTS = {
    'turkey': {2019: (112, 112, 112), 2020: (21, 21, 21)},
    'black_bear': {2019: (1, 0, 0), 2020: (104, 38, 47)},
    'white_tailed_deer': {2019: (55, 55, 55), 2020: (205, 205, 205)},
}


def _time_matches_by_A(a, b, tol):
    """Optimal one-to-one time pairing, mapping each retained focal A fix once."""
    raw = geodesic.one_to_one_time_pairs(a, b, tol)
    answer = {afix: bfix for afix, bfix in raw}
    if len(answer) != len(raw):
        raise AssertionError('An original A timestamp was reused in one time alignment')
    return answer


def eligible_day_shift(byday, original_pairs, year, tolerance):
    """Eligibility before spatial scoring; all three B date choices share A anchors.

    Private result uses original dyad identifiers and GPS coordinates in RAM
    only. Never JSON-serialize this return value.
    """
    index = defaultdict(dict)
    for (y, m, animal, day), values in byday.items():
        if y == year and m in WINTER + SUMMER:
            index[(animal, m)][day] = values
    pairs = {}
    for a, b in sorted(original_pairs):
        monthly = {}
        for m in WINTER + SUMMER:
            a_days = index.get((a, m), {})
            b_days = index.get((b, m), {})
            supported = {}
            for day in sorted(a_days.keys() & b_days.keys()):
                prev_b, next_b = b_days.get(day - 1), b_days.get(day + 1)
                if prev_b is None or next_b is None:
                    continue
                if any(len(z) < MIN_MATCHED_FIXES_PER_DAY
                       for z in (a_days[day], b_days[day], prev_b, next_b)):
                    continue
                by_treatment = (
                    _time_matches_by_A(a_days[day], b_days[day], tolerance),
                    _time_matches_by_A(a_days[day], prev_b, tolerance),
                    _time_matches_by_A(a_days[day], next_b, tolerance),
                )
                anchors = sorted(set(by_treatment[0]) & set(by_treatment[1])
                                 & set(by_treatment[2]))
                if len(anchors) < MIN_MATCHED_FIXES_PER_DAY:
                    continue
                supported[day] = tuple((x, by_treatment[0][x],
                                        by_treatment[1][x],
                                        by_treatment[2][x]) for x in anchors)
            if len(supported) >= MIN_COMMON_DATES_PER_MONTH:
                monthly[m] = supported
        if (sum(m in monthly for m in WINTER) >= MONTHS_PER_SEASON
                and sum(m in monthly for m in SUMMER) >= MONTHS_PER_SEASON):
            pairs[(a, b)] = monthly
    return pairs


def _draw(values, n, *key):
    """Same deterministic, source- and dyad-qualified sampling conventions."""
    return geodesic._select(values, n, 'ADJACENT_DAY', *key)


def _daily_proximity(selected):
    """Compute all three radii from exact same three A-time anchored fixes."""
    if len(selected) != MIN_MATCHED_FIXES_PER_DAY:
        raise AssertionError('Expected precisely three fully matched A anchors')
    out = {r: {'same': 0, 'previous_day': 0, 'next_day': 0} for r in RADII_KM}
    gaps = {'same': [], 'previous_day': [], 'next_day': []}
    for a, b0, bprev, bnext in selected:
        for name, b in (('same', b0), ('previous_day', bprev), ('next_day', bnext)):
            gap = abs(a[0] - b[0])
            gaps[name].append(gap)
            dist = geodesic.haversine_km(a, b)
            for radius in RADII_KM:
                out[radius][name] += int(dist <= radius)
    for radius in RADII_KM:
        for name in out[radius]:
            out[radius][name] /= MIN_MATCHED_FIXES_PER_DAY
    return out, {k: statistics.fmean(v) for k, v in gaps.items()}


def _one_seed(supported, source, year, tol, seed):
    """Equal dyads, months, dates and FIXES across treatments and distance radii."""
    values = {
        r: {'winter': defaultdict(list), 'summer': defaultdict(list)}
        for r in RADII_KM}
    gaps = {'winter': defaultdict(list), 'summer': defaultdict(list)}
    n_pairs = len(supported)
    for pair, months in sorted(supported.items()):
        for season, season_months in (('winter', WINTER), ('summer', SUMMER)):
            selected_months = _draw([m for m in season_months if m in months],
                                    MONTHS_PER_SEASON,
                                    'MONTH', source, year, tol, seed, pair, season)
            monthly_results = {r: defaultdict(list) for r in RADII_KM}
            monthly_gaps = defaultdict(list)
            for month in selected_months:
                day_indexes = _draw(list(months[month]), MIN_COMMON_DATES_PER_MONTH,
                                    'DAY', source, year, tol, seed, pair, season, month)
                per_day = {r: defaultdict(list) for r in RADII_KM}
                per_day_gaps = defaultdict(list)
                for day in day_indexes:
                    fixes = _draw(months[month][day], MIN_MATCHED_FIXES_PER_DAY,
                                  'FIX', source, year, tol, seed, pair,
                                  season, month, day)
                    observed, gap_record = _daily_proximity(fixes)
                    if any(z > tol + 1e-9 for z in gap_record.values()):
                        raise AssertionError('Frozen source-recording tolerance was exceeded')
                    for r in RADII_KM:
                        for name, fraction in observed[r].items():
                            per_day[r][name].append(fraction)
                    for name, seconds in gap_record.items():
                        per_day_gaps[name].append(seconds)
                for r in RADII_KM:
                    for name in ('same', 'previous_day', 'next_day'):
                        monthly_results[r][name].append(
                            statistics.fmean(per_day[r][name]))
                for name in ('same', 'previous_day', 'next_day'):
                    monthly_gaps[name].append(statistics.fmean(per_day_gaps[name]))
            for r in RADII_KM:
                for name in ('same', 'previous_day', 'next_day'):
                    values[r][season][name].append(statistics.fmean(monthly_results[r][name]))
            for name in ('same', 'previous_day', 'next_day'):
                gaps[season][name].append(statistics.fmean(monthly_gaps[name]))
    output = []
    for radius in RADII_KM:
        months = values[radius]
        seasons = {}
        for season in ('winter', 'summer'):
            source_positions = {name: statistics.fmean(months[season][name])
                                for name in ('same', 'previous_day', 'next_day')}
            source_positions['adjacent_day_reference'] = (
                source_positions['previous_day'] + source_positions['next_day']) / 2
            source_positions['same_minus_adjacent'] = (
                source_positions['same'] - source_positions['adjacent_day_reference'])
            seasons[season] = source_positions
        result = {
            'source_year': year,
            'tolerance_seconds': tol,
            'radius_km': radius,
            'seed': seed,
            'n_dyads': n_pairs,
            'n_sampled_pair_dates': n_pairs * 28,
            'n_sampled_fix_triples': n_pairs * 84,
            'winter': seasons['winter'],
            'summer': seasons['summer'],
            'winter_minus_summer': {
                name: seasons['winter'][name] - seasons['summer'][name]
                for name in seasons['winter']},
            'mean_abs_source_clock_gap_seconds': {
                season: {name: statistics.fmean(gaps[season][name])
                         for name in ('same', 'previous_day', 'next_day')}
                for season in ('winter', 'summer')},
        }
        for season in ('winter', 'summer'):
            sc = seasons[season]
            if not all(0 <= sc[name] <= 1 for name in
                       ('same', 'previous_day', 'next_day', 'adjacent_day_reference')):
                raise AssertionError('Source geographic nearness outside [0,1]')
            if not math.isclose(sc['same'] - sc['adjacent_day_reference'],
                                sc['same_minus_adjacent'], abs_tol=1e-12):
                raise AssertionError('Trajectory phase contrast failed to reconcile')
        output.append(result)
    return output


def analyze_source(source, untimed, pinned, byday):
    """Original source-year support and full 2×3×12 evaluation, no case selection."""
    centers = geo.annual_day_balanced_centroids(untimed)
    rows = {
        'schema_version': 1, 'as_of': '2026-10-21',
        'status': 'POST_INSPECTION_ADJACENT_SOURCE_DAY_ORIGINAL_GPS_CONTROL',
        'source': source, 'doi':geo.SOURCES[source][1],
        'complete_original_publisher_MD5_and_pinned_SHA256_verified': True,
        'full_original_time_position_QC_multiset_verified': True,
        'n_original_GPS_fixes': len(untimed),
        'source_clock_absolute_UTC_offset_verified': False,
        'biological_population_membership_verified': False,
        'GPS_location_error_quantified': False,
        'time_tolerances_seconds': list(TOLERANCES),
        'radii_km': list(RADII_KM), 'n_seeds':len(SEEDS),
        'lagged_B_source_days':[-1,0,1],
        'require_same_focal_A_GPS_fix_for_all_three_source_days':True,
        'year_results': [],
        'limits': [
            'Original GPS near-position at time gap <=15/30 min is NOT a verified animal encounter',
            'Adjacent source-day B trajectories preserve within-day ordering but not environmental history',
            'Unverified same-population/source-tag positional accuracy and GPS clock calibration',
            'Calendar winter months are noncontiguous in each source year',
            'Repeated years, dyads and random seeds are dependent; no biological p-values or mechanism proof'],
    }
    for year in YEARS:
        baseline = clock._base_pair_set(untimed, year, centers)
        expected = EXPECTED_V2_COUNTS[source][year]
        if len(baseline) != expected[0]:
            raise AssertionError('Old source-season 25km dyad denominator changed')
        per_year = {'year':year, 'n_old_geographic_pairs':len(baseline), 'time_tolerance_results':[]}
        selected_masks = []
        for tol, expected_n in zip(TOLERANCES, expected[1:]):
            same_day = geodesic._derive_opportunity(byday, baseline, year, tol)
            if len(same_day) != expected_n:
                raise AssertionError('Previous source time-matched pair mask changed')
            supported = eligible_day_shift(byday, set(same_day), year, tol)
            if not set(supported).issubset(set(same_day)):
                raise AssertionError('Adjacent-day risk set not nested in original matched-day support')
            selected_masks.append(set(supported))
            n = len(supported)
            n_animals = len({a for pair in supported for a in pair})
            status = ('DESCRIPTIVE_ADJACENT_DAY_ORIGINAL_GPS_CONTROL'
                      if n>=MIN_SUPPORTED_DYADS and n_animals>=MIN_SUPPORTED_ANIMALS
                      else 'STOP_INSUFFICIENT_DAY_SHIFT_TEMPORAL_OPPORTUNITY')
            row = {'max_gap_seconds':tol,
                   'status': status,
                   'n_original_same_day_supported_dyads': len(same_day),
                   'n_adjacent_day_supported_dyads':n,
                   'n_source_animals_with_supported_pairs':n_animals,
                   'fraction_matched_pairs_with_adjacent_day_support':
                       n / len(same_day) if same_day else None,
                   'sampled_geodesic_seed_results': []}
            if status.startswith('DESCRIPTIVE_'):
                for seed in SEEDS:
                    row['sampled_geodesic_seed_results'].extend(
                        _one_seed(supported, source, year, tol, seed))
                if len(row['sampled_geodesic_seed_results']) != len(SEEDS)*len(RADII_KM):
                    raise AssertionError('Source-year lagged-sample scenario count mismatch')
            per_year['time_tolerance_results'].append(row)
            print(json.dumps({
                'source':source,'year':year,'tol_seconds':tol,
                'n_original_day_match_pairs':len(same_day),
                'n_adjacent_day_pairs':n,'n_animals':n_animals,
                'scenarios':len(row['sampled_geodesic_seed_results']),'status':status
                },sort_keys=True),flush=True)
        if not selected_masks[0].issubset(selected_masks[1]):
            raise AssertionError('<=15min adjacent-day support is not subset of <=30min')
        rows['year_results'].append(per_year)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',choices=SOURCES,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='source_day_shift_') as temporary:
        path=Path(temporary)
        timed,untimed,pinned=clock.get_original(args.source,path)
        byday=geodesic._native_positions(args.source,path,untimed)
        outcome=analyze_source(args.source,untimed,pinned,byday)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(outcome,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'source':args.source,
                      'fix_count':outcome['n_original_GPS_fixes'],
                      'verified_aggregate_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'status':outcome['status']},sort_keys=True))


if __name__ == '__main__':
    main()
