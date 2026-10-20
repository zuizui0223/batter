#!/usr/bin/env python3
"""Original-Movebank GPS observation-effort standardization for seasonal X.

Post-primary-inspection sensitivity only. Reuses the exact source decoder and
QC from cross_source_seasonal_x_v2. Downloads complete original CSVs into a
temporary runner cache, pins original publisher MD5 and prior SHA256, and
writes cohort-level aggregates only. Raw IDs, dates, coordinates and dyads
are never serialized. No inferential p-values or social-contact claims.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from itertools import combinations
from pathlib import Path
import random
import statistics
import tempfile
import zipfile

import cross_source_seasonal_x_v2 as baseline

ARCHIVE_NAME = 'CROSS_SOURCE_NEARBY_DYAD_V2_FULL_AGGREGATES_2026_10_20.zip'
ARCHIVE_SHA256 = '857e4157606ca1a4bf87d2f7e76fa379ab7bbf77c2bfc491ffec8196f543ee48'
SOURCES = ('turkey', 'black_bear', 'white_tailed_deer')
YEARS = (2019, 2020)
WINTER = (12, 1, 2)
SUMMER = (6, 7, 8)
SEEDS = tuple(range(24))
POINTS_PER_DAY = (1, 2)
SHARED_DATES_PER_MONTH = 7
MONTHS_PER_SEASON = 2
CENTROID_KM = 25
GRIDS = ((1., 0., 0.), (5., 0., 0.), (5., .5, .5), (10., 0., 0.))


def _sha256_path(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _seed(*parts):
    raw = '\x1f'.join(str(v) for v in parts).encode('utf-8')
    return int.from_bytes(hashlib.sha256(raw).digest()[:16], 'big')


def _draw(items, count, *salt):
    """Select without replacement; permutation of original source rows invariant."""
    if len(items) < count:
        raise ValueError('Cannot draw more fixes/dates/months than exist')
    rng = random.Random(_seed(*salt))
    return tuple(sorted(rng.sample(sorted(items), count)))


def _group(events):
    """(year, month, animal, native ordinal day) -> sorted original positions."""
    by = defaultdict(list)
    for r in events:
        by[(r.year, r.month, r.animal, r.day)].append((r.lat, r.lon))
    return {key: tuple(sorted(points)) for key, points in by.items()}


def _supported_pairs(events, by, year, k, centers):
    """Fix-independent dyad inclusion before any spatial overlap is scored."""
    dates = defaultdict(set)
    for (y, month, animal, day), points in by.items():
        if y == year and len(points) >= k:
            dates[(animal, month)].add(day)
    animals = sorted({animal for animal, month in dates})
    eligible = []
    details = {}
    for a, b in combinations(animals, 2):
        if a not in centers.get(year, {}) or b not in centers.get(year, {}):
            continue
        if baseline.centroid_distance_km(centers[year][a], centers[year][b]) > CENTROID_KM:
            continue
        monthly = {}
        for month in set(WINTER + SUMMER):
            common = dates[(a, month)] & dates[(b, month)]
            if len(common) >= SHARED_DATES_PER_MONTH:
                monthly[month] = tuple(sorted(common))
        if (sum(month in monthly for month in WINTER) >= MONTHS_PER_SEASON
                and sum(month in monthly for month in SUMMER) >= MONTHS_PER_SEASON):
            eligible.append((a, b))
            details[(a, b)] = monthly
    return eligible, details


def _selected_fix_positions(by, year, month, animal, day, count, seed, cache):
    key = (year, month, animal, day, count, seed)
    if key not in cache:
        points = by[(year, month, animal, day)]
        cache[key] = _draw(points, count, 'FIX', count, seed, year, month, animal, day)
    return cache[key]


def _cell(lat, lon, width_km, ox, oy, lat_cos):
    return (math.floor(lon * 111.32 * lat_cos / width_km + ox),
            math.floor(lat * 111.32 / width_km + oy))


def _selected_month_dates(monthly, months, count, seed, a, b, season):
    present = [month for month in months if month in monthly]
    return _draw(present, count, 'MONTH', seed, a, b, season)


def _pair_month_X(by, pair, year, month, shared_dates, k, seed, grid, lat_cos,
                  fix_cache):
    """Each partner has exactly k original fixes per same, selected date."""
    width, ox, oy = grid
    a, b = pair
    days = _draw(shared_dates, SHARED_DATES_PER_MONTH,
                 'DAY', k, seed, year, month, a, b)
    counts_a, counts_b = Counter(), Counter()
    for day in days:
        for lat, lon in _selected_fix_positions(by, year, month, a, day,
                                                 k, seed, fix_cache):
            counts_a[_cell(lat, lon, width, ox, oy, lat_cos)] += 1
        for lat, lon in _selected_fix_positions(by, year, month, b, day,
                                                 k, seed, fix_cache):
            counts_b[_cell(lat, lon, width, ox, oy, lat_cos)] += 1
    mass = k * SHARED_DATES_PER_MONTH
    numerator = sum(min(v, counts_b.get(cell, 0))
                    for cell, v in counts_a.items())
    return numerator / mass


def _pair_season_X(by, pair, year, monthly, months, k, seed, grid,
                   lat_cos, fix_cache, season):
    chosen = _selected_month_dates(monthly, months, MONTHS_PER_SEASON,
                                   seed, *pair, season)
    values = [_pair_month_X(by, pair, year, m, monthly[m], k, seed,
                            grid, lat_cos, fix_cache) for m in chosen]
    return sum(values) / len(values)


def _distribution(values):
    values = sorted(v for v in values if v is not None)
    if not values:
        return {'n_defined': 0, 'mean': None, 'median': None,
                'min': None, 'max': None}
    return {'n_defined': len(values), 'mean': statistics.fmean(values),
            'median': statistics.median(values),
            'min': values[0], 'max': values[-1]}


def _summarize_draws(draws):
    """Preserve each seed's aggregate, with no source animal identifiers."""
    fields = ('winter_mean_X', 'summer_mean_X', 'delta_mean_X',
              'winter_edge_fraction', 'summer_edge_fraction',
              'delta_incidence', 'delta_conditional_strength',
              'jaccard_positive_edges')
    out = {key: _distribution([row.get(key) for row in draws]) for key in fields}
    for key in ('delta_mean_X', 'delta_incidence',
                'delta_conditional_strength'):
        defined = [row[key] for row in draws if row.get(key) is not None]
        out[key]['positive_seeds'] = sum(v > 1e-12 for v in defined)
        out[key]['negative_seeds'] = sum(v < -1e-12 for v in defined)
        out[key]['near_zero_seeds'] = len(defined) - out[key]['positive_seeds'] - out[key]['negative_seeds']
    return out


def _compute_grid_seed(by, year, pairs, support, k, seed, grid, lat_cos):
    cache = {}
    winter, summer = {}, {}
    for pair in pairs:
        monthly = support[pair]
        winter[pair] = _pair_season_X(by, pair, year, monthly, WINTER, k,
                                      seed, grid, lat_cos, cache, 'WINTER')
        summer[pair] = _pair_season_X(by, pair, year, monthly, SUMMER, k,
                                      seed, grid, lat_cos, cache, 'SUMMER')
    stats = baseline.describe(winter, summer)
    if stats['status'] != 'DESCRIPTIVE_MATCHED_DYADS':
        return {'status': stats['status'], 'n_pairs': 0}
    w = stats['season1']
    s = stats['season2']
    states = stats['dyad_states']
    union = states['both'] + states['season1_only'] + states['season2_only']
    return {
        'status': 'DESCRIPTIVE_BALANCED_ORIGINAL_FIXES',
        'n_pairs': stats['n_pairs'],
        'winter_mean_X': w['mean_X'], 'summer_mean_X': s['mean_X'],
        'delta_mean_X': stats['difference_season1_minus_season2'],
        'winter_edge_fraction': w['positive_fraction'],
        'summer_edge_fraction': s['positive_fraction'],
        'delta_incidence': stats['incidence_component'],
        'delta_conditional_strength': stats['positive_strength_component'],
        'jaccard_positive_edges': states['both'] / union if union else None,
        'winter_positive_pairs': w['positive_pairs'],
        'summer_positive_pairs': s['positive_pairs'],
        'both_edges': states['both'],
        'winter_only_edges': states['season1_only'],
        'summer_only_edges': states['season2_only'],
        'neither_edges': states['neither'],
    }


def analyze_events(events, reference_summary, source, *, seeds=SEEDS, grids=GRIDS):
    if source not in SOURCES:
        raise ValueError('Source not declared in design')
    by = _group(events)
    if not events:
        raise ValueError('Empty source after original quality control')
    lat_cos = math.cos(math.radians(math.fsum(x.lat for x in events) / len(events)))
    centers = baseline.annual_day_balanced_centroids(events)
    fixed = {(r['year'], r['window'], r['risk_set_mode'], r['grid_km'],
              r['origin_x_fraction'], r['origin_y_fraction']): r
             for r in reference_summary['source']['comparisons']}
    groups = []
    for year in YEARS:
        base_pairs, base_dates = _supported_pairs(events, by, year, 1, centers)
        expected = fixed[(year, 'winter_summer', 'near_centroid_25km',
                          5.0, 0., 0.)]['n_pairs']
        if len(base_pairs) != expected:
            raise AssertionError('Reconstructed k=1 dyad mask differs from pinned source V2')
        if len(base_pairs) < 2:
            groups.append({'year': year, 'status': 'NOT_ESTIMABLE_FEWER_THAN_TWO_SOURCE_DYADS',
                           'n_original_eligible_pairs': len(base_pairs)})
            continue
        pairs2, dates2 = _supported_pairs(events, by, year, 2, centers)
        subset = set(base_pairs)
        if not set(pairs2).issubset(subset):
            raise AssertionError('k=2 support is not a subset of original pair mask')
        group = {'year': year, 'status': 'EXPLORATORY_EFFORT_SENSITIVITY',
                 'n_original_eligible_pairs': len(base_pairs),
                 'n_k2_supported_pairs': len(pairs2),
                 'k2_retention_fraction': len(pairs2)/len(base_pairs),
                 'by_fix_count': []}
        for k, pairs, support in ((1, base_pairs, base_dates), (2, pairs2, dates2)):
            item = {'k_fixes_per_animal_day': k,
                    'n_pairs': len(pairs), 'grids': []}
            for grid in grids:
                draws = [_compute_grid_seed(by, year, pairs, support, k, seed,
                                            grid, lat_cos) for seed in seeds]
                item['grids'].append({'grid_km': grid[0],
                    'origin_x_fraction': grid[1], 'origin_y_fraction': grid[2],
                    'summary': _summarize_draws(draws) if pairs else None,
                    'seed_aggregate_results': draws if pairs else [],
                    'status': 'DESCRIPTIVE_EFFORT_STANDARDIZED' if pairs else 'NOT_ESTIMABLE_NO_K_SUPPORT'})
            group['by_fix_count'].append(item)
        groups.append(group)
    day_counts = [len(seq) for seq in by.values()]
    return {
        'source': source, 'status': 'POST_INSPECTION_ORIGINAL_SOURCE_BALANCED_SENSITIVITY',
        'source_doi': baseline.SOURCES[source][1], 'n_source_fixes': len(events),
        'n_source_animals': len({x.animal for x in events}),
        'n_animal_calendar_dates': len(day_counts),
        'original_fix_per_animal_day': {'mean': statistics.fmean(day_counts),
                                       'median': statistics.median(day_counts),
                                       'min': min(day_counts), 'max': max(day_counts)},
        'centroid_group_labels_verified': False,
        'groups': groups,
    }


def source_from_publisher(source, cache):
    """Download archived original full files; verify both existing sha256 pins."""
    with zipfile.ZipFile(Path(__file__).resolve().with_name(ARCHIVE_NAME)) as archive:
        pinned = json.loads(archive.read(source + '.json'))
    recorded = pinned['source']
    if recorded['status'] != 'COMPLETE_EXPLORATORY_GEOGRAPHIC_X':
        raise ValueError('Pinned source was not valid')
    uuid, doi, taxon = baseline.SOURCES[source]
    _, entries = baseline._manifest(uuid)
    gps = [x for x in entries if x['role'] == 'gps']
    refs = [x for x in entries if x['role'] == 'reference']
    if not gps or len(refs) != 1:
        raise ValueError('Published item does not contain complete GPS and unique reference')
    if sum(x['size'] for x in gps) > baseline.MAX_ARCHIVE_BYTES:
        raise ValueError('GPS original acquisition would exceed budget')
    obtained = []
    for entry in gps + refs:
        path, receipt = baseline._download(entry, cache)
        candidates = [x for x in recorded['file_receipts'] if x['role'] == entry['role']
                      and x['sha256'] == receipt['sha256']
                      and x['bytes'] == receipt['bytes']
                      and x['source_md5'] == receipt['source_md5']]
        if len(candidates) != 1 or not receipt['md5_verified']:
            raise AssertionError('Complete original source differs from pinned receipt')
        obtained.append((entry, path))
    gps_files = [(path, entry['filename']) for entry, path in obtained if entry['role'] == 'gps']
    reference = next((path, entry['filename']) for entry, path in obtained if entry['role'] == 'reference')
    events, qc, labels = baseline.read_originals(gps_files, reference, taxon)
    if qc != recorded['event_audit']:
        raise AssertionError('Original event QC differs from pinned V2')
    # Original archive has zero usable group labels in the chosen sources.
    if labels:
        raise AssertionError('Source population label availability changed; stop for manual review')
    return events, qc, pinned


def run(source, output):
    archive_path = Path(__file__).resolve().with_name(ARCHIVE_NAME)
    if _sha256_path(archive_path) != ARCHIVE_SHA256:
        raise AssertionError('Pinned baseline ZIP SHA256 mismatch')
    with tempfile.TemporaryDirectory(prefix='movebank_balanced_orig_') as tmp:
        events, qc, pinned = source_from_publisher(source, Path(tmp))
        result = analyze_events(events, pinned, source)
        del events
    result['source_original_event_qc_verified'] = True
    result['source_files_sha256_pinned'] = [
        {'role': r['role'], 'sha256': r['sha256'], 'md5_verified': True}
        for r in pinned['source']['file_receipts']]
    result['baseline_aggregate_zip_sha256'] = ARCHIVE_SHA256
    result['design'] = 'SEASONAL_EDGE_OBSERVATION_BALANCE_DESIGN_2026_10_20.md'
    result['n_seeds'] = len(SEEDS)
    result['grids'] = [list(x) for x in GRIDS]
    result['limitations'] = [
        'Post-primary-inspection exploration; not an independent preregistration',
        'Equalized observed sample counts do not recover undetected animal use or fix accuracy',
        'Centroid <=25 km cannot establish shared population or direct interactions',
        'k2 may retain fewer animal pairs; no missing-as-zero imputation',
        'Seeds and grid settings are dependent sensitivity scenarios, not independent biological replicates',
        'No inference about food, resource exposure E, encounters T, movement individuality R, or causes',
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
    # The CI logs are strictly aggregate-only (no pair IDs, dates, coordinates).
    short = {'source': source,
             'n_retained_fixes': result['n_source_fixes'],
             'source_qc_verified': True, 'summary': []}
    for group in result['groups']:
        if group['status'] != 'EXPLORATORY_EFFORT_SENSITIVITY':
            short['summary'].append({'year': group['year'], 'status': group['status'],
                                     'pairs': group['n_original_eligible_pairs']})
            continue
        rows = []
        for krow in group['by_fix_count']:
            grid = next(x for x in krow['grids'] if x['grid_km']==5.0 and
                        x['origin_x_fraction']==0 and x['origin_y_fraction']==0)
            rows.append({'k':krow['k_fixes_per_animal_day'],
                         'n_pairs':krow['n_pairs'],
                         'reference_5km':grid['summary']})
        short['summary'].append({'year':group['year'], 'n_original_pairs':group['n_original_eligible_pairs'],
                                 'k2_retained_pairs':group['n_k2_supported_pairs'],
                                 'effort':rows})
    print('AGGREGATE_BALANCED_RESULT=' + json.dumps(short, sort_keys=True, allow_nan=False), flush=True)
    print('AGGREGATE_BALANCED_RESULT_SHA256=' + _sha256_path(output), flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, choices=SOURCES)
    parser.add_argument('--output', required=True, type=Path)
    args=parser.parse_args()
    run(args.source, args.output)


if __name__=='__main__':
    main()
