#!/usr/bin/env python3
"""Source-verified seasonal geographic-overlap incidence and dyad transitions.

Observational, exploratory only. Fetches full original Movebank GPS and reference
files, checks source MD5, retains only aggregate summaries. Original IDs, exact
dates, coordinates and cells must never appear in outputs or workflow logs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from datetime import datetime
import gzip
import hashlib
import io
from itertools import combinations
import json
import math
from pathlib import Path
import tempfile
import time
from urllib.request import Request, urlopen
import zipfile

from deer_geography_v1 import compute_geography_overlap, DEFAULT_SCALES_KM, DEFAULT_ORIGINS

API = 'https://datarepository.movebank.org/server/api/core/'
SOURCES = {
    'black_bear': ('89b8132d-fc88-498f-9040-39643b387dd4', '10.5441/001/1.706', 'Ursus americanus'),
    'turkey': ('dd064947-25b7-46a2-8976-adfc488750bc', '10.5441/001/1.671', 'Meleagris gallopavo'),
    'moose': ('26a9d940-906d-490b-a87d-02be51e5e21f', '10.5441/001/1.714', 'Alces alces'),
    'moose_snowy_range': ('6857a715-9703-40fe-b306-43464f65a35c', '10.5441/001/1.700', 'Alces alces'),
    'white_tailed_deer': ('e6102c38-8e96-4e36-9ff8-f40a0c03fe5f', '10.5441/001/1.718', 'Odocoileus virginianus'),
}
YEARS = (2019, 2020)
WINDOWS = {'winter_summer': ((12, 1, 2), (6, 7, 8)), 'early_late': ((1, 2), (3, 4))}
MAX_ARCHIVE_BYTES = 170 * 1024 * 1024
MAX_UNCOMPRESSED_CSV = 1200 * 1024 * 1024
MAX_EVENTS = 2_600_000


@dataclass(frozen=True, slots=True, repr=False)
class Fix:
    animal: str
    year: int
    month: int
    day: int
    lat: float
    lon: float


def _get(url):
    with urlopen(Request(url, headers={'User-Agent': 'source-verified-ecology/1.0'}), timeout=120) as r:
        return r.read()


def _json(url):
    return json.loads(_get(url).decode('utf-8'))


def _manifest(uuid):
    # Strict one-page checks: never quietly work on an incomplete source.
    item = _json(API + 'items/' + uuid)
    bundles = _json(API + 'items/' + uuid + '/bundles?size=100')
    if bundles.get('page', {}).get('totalPages') != 1:
        raise ValueError('Source bundle pagination unsupported')
    originals = [x for x in bundles['_embedded']['bundles'] if x['name'] == 'ORIGINAL']
    if len(originals) != 1:
        raise ValueError('Source ORIGINAL bundle missing or ambiguous')
    entries = _json(originals[0]['_links']['bitstreams']['href'] + '?size=100')
    if entries.get('page', {}).get('totalPages') != 1:
        raise ValueError('Source bitstream pagination unsupported')
    chosen = []
    for x in entries['_embedded']['bitstreams']:
        name = x['name'].lower()
        if x['checkSum']['checkSumAlgorithm'].upper() != 'MD5':
            raise ValueError('Source does not provide an original MD5')
        if 'reference-data' in name:
            role = 'reference'
        elif name.endswith(('.csv', '.csv.zip', '.csv.gz', '.zip')) and not any(
                token in name for token in ('-acc', 'acceleration', '-mag', 'orientation', 'reference')):
            role = 'gps'
        else:
            continue
        chosen.append({'role': role, 'filename': x['name'], 'uuid': x['uuid'],
                       'size': int(x['sizeBytes']), 'md5': x['checkSum']['value'].lower(),
                       'url': x['_links']['content']['href']})
    return item, chosen


def _download(entry, folder):
    """Never trust partial caches; retry complete, size-pinned original downloads."""
    path = folder / (entry['uuid'] + '.original')
    if not path.exists() or path.stat().st_size != entry['size']:
        last_error = None
        for attempt in range(3):
            temp = path.with_suffix('.part')
            size = 0
            try:
                with urlopen(Request(entry['url'], headers={'User-Agent': 'source-verified-ecology/1.0'}), timeout=120) as r, temp.open('wb') as f:
                    for chunk in iter(lambda: r.read(1024 * 1024), b''):
                        size += len(chunk)
                        if size > entry['size']:
                            raise ValueError('Original content longer than source manifest')
                        f.write(chunk)
                if size != entry['size']:
                    raise ValueError('Incomplete original file')
                temp.replace(path)
                break
            except Exception as exc:
                last_error = exc
                temp.unlink(missing_ok=True)
                if attempt < 2:
                    time.sleep(2 ** attempt)
        else:
            raise RuntimeError('All bounded full-original download attempts failed') from last_error
    md5 = hashlib.md5(usedforsecurity=False)
    sha = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            md5.update(part)
            sha.update(part)
    if path.stat().st_size != entry['size'] or md5.hexdigest() != entry['md5']:
        path.unlink(missing_ok=True)
        raise ValueError('Original source MD5 or size mismatch')
    return path, {'role': entry['role'], 'bytes': entry['size'], 'md5_verified': True,
                  'source_md5': entry['md5'], 'sha256': sha.hexdigest()}


def _csv_rows(path, filename):
    lower = filename.lower()
    if lower.endswith('.zip'):
        with zipfile.ZipFile(path) as z:
            csv_members = [x for x in z.infolist() if not x.is_dir()
                           and x.filename.lower().endswith('.csv')
                           and not x.filename.startswith('__MACOSX/')
                           and not Path(x.filename).name.startswith('._')]
            if len(csv_members) != 1 or csv_members[0].file_size > MAX_UNCOMPRESSED_CSV:
                raise ValueError('ZIP does not contain exactly one bounded GPS/reference CSV')
            with z.open(csv_members[0]) as b, io.TextIOWrapper(b, encoding='utf-8-sig', newline='') as f:
                yield from csv.DictReader(f)
    elif lower.endswith('.gz'):
        with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as f:
            yield from csv.DictReader(f)
    elif lower.endswith('.csv'):
        with path.open('r', encoding='utf-8-sig', newline='') as f:
            yield from csv.DictReader(f)
    else:
        raise ValueError('Unknown original data file extension')


def read_originals(gps_paths, reference_path, taxon):
    # Returns biological identities privately for the in-memory pair risk sets.
    tags, labels, ref_count = defaultdict(set), defaultdict(set), 0
    for r in _csv_rows(*reference_path):
        ref_count += 1
        animal, tag = (r.get('animal-id') or '').strip(), (r.get('tag-id') or '').strip()
        if animal and tag:
            tags[animal].add(tag)
            site = (r.get('study-site') or r.get('animal-group-id') or '').strip()
            if site:
                labels[animal].add(site)
    if not tags:
        raise ValueError('Original source reference lacks animal-tag pairs')
    by_key = {}
    qc = Counter()
    for path, filename in gps_paths:
        for r in _csv_rows(path, filename):
            qc['source_rows'] += 1
            animal = (r.get('individual-local-identifier') or '').strip()
            tag = (r.get('tag-local-identifier') or '').strip()
            if (r.get('sensor-type') or '').strip().lower() != 'gps':
                qc['non_gps'] += 1
                continue
            if (r.get('visible') or '').strip().lower() not in ('true', '1'):
                qc['not_visible'] += 1
                continue
            if (r.get('individual-taxon-canonical-name') or '').strip() != taxon:
                qc['other_taxon'] += 1
                continue
            if tag not in tags.get(animal, set()):
                qc['missing_reference_pair'] += 1
                continue
            if any((r.get(col) or '').strip().lower() in ('1', 'true') for col in (
                'manually-marked-outlier', 'algorithm-marked-outlier', 'automatically-marked-outlier')):
                qc['source_outlier'] += 1
                continue
            try:
                t = datetime.fromisoformat(r['timestamp'].strip().replace('Z', '+00:00'))
                # Keep source-clock day. Do not assert an undocumented UTC offset.
            except (ValueError, TypeError, KeyError):
                qc['invalid_timestamp'] += 1
                continue
            try:
                lat, lon = float(r['location-lat']), float(r['location-long'])
                if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                    raise ValueError('Invalid coordinates')
            except (ValueError, TypeError, KeyError):
                qc['invalid_position'] += 1
                continue
            if t.year not in YEARS:
                qc['outside_fixed_years'] += 1
                continue
            key = (animal, t)
            fix = Fix(animal, t.year, t.month, t.toordinal(), lat, lon)
            if key in by_key:
                if by_key[key] == fix:
                    qc['identical_duplicate'] += 1
                else:
                    qc['conflicting_timestamp'] += 1
                    by_key[key] = None
            else:
                by_key[key] = fix
            if len(by_key) > MAX_EVENTS:
                raise ValueError('Source exceeds complete-event memory safety bound')
    events = [x for x in by_key.values() if x is not None]
    qc['retained_fixes'] = len(events)
    label_by_animal = {animal: next(iter(values)) for animal, values in labels.items() if len(values) == 1}
    qc['reference_rows'] = ref_count
    qc['reference_animals'] = len(tags)
    qc['animals_with_one_reference_label'] = len(label_by_animal)
    qc['animals_with_ambiguous_reference_labels'] = sum(len(x) > 1 for x in labels.values())
    qc['distinct_reference_labels'] = len({v for vs in labels.values() for v in vs})
    qc['retained_animals'] = len({x.animal for x in events})
    qc['retained_fixes_by_year'] = dict(sorted(Counter(str(x.year) for x in events).items()))
    qc['animals_observed_by_year'] = {str(year): len({x.animal for x in events if x.year == year}) for year in YEARS}
    qc['months_with_fixes_by_year'] = {str(year): sum(any(x.year == year and x.month == m for x in events) for m in range(1, 13)) for year in YEARS}
    return events, dict(qc), label_by_animal


def describe(winter, summer):
    """Exact symmetric decomposition on the SAME supported dyads, with explicit zeros."""
    if set(winter) != set(summer):
        raise ValueError('Cross-season pair risk sets differ')
    if not winter:
        return {'status': 'NOT_ESTIMABLE_NO_MATCHED_DYADS', 'n_pairs': 0}
    for v in list(winter.values()) + list(summer.values()):
        if isinstance(v, bool) or v is None or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 1:
            raise ValueError('Missing overlap must not be encoded as zero')
    n = len(winter)
    nw, ns = sum(x > 0 for x in winter.values()), sum(x > 0 for x in summer.values())
    mw, ms = math.fsum(winter.values()) / n, math.fsum(summer.values()) / n
    pw, ps = nw/n, ns/n
    sw = math.fsum(x for x in winter.values() if x > 0) / nw if nw else None
    ss = math.fsum(x for x in summer.values() if x > 0) / ns if ns else None
    c = Counter((winter[k] > 0, summer[k] > 0) for k in winter)
    result = {'status': 'DESCRIPTIVE_MATCHED_DYADS', 'n_pairs': n,
              'season1': {'positive_pairs': nw, 'positive_fraction': pw, 'positive_strength': sw, 'mean_X': mw},
              'season2': {'positive_pairs': ns, 'positive_fraction': ps, 'positive_strength': ss, 'mean_X': ms},
              'difference_season1_minus_season2': mw-ms,
              'dyad_states': {'neither': c[(False, False)], 'season1_only': c[(True, False)],
                              'season2_only': c[(False, True)], 'both': c[(True, True)]},
              'paired_difference_signs': {'first_greater': sum(winter[k] > summer[k] for k in winter),
                                          'second_greater': sum(winter[k] < summer[k] for k in winter),
                                          'equal': sum(winter[k] == summer[k] for k in winter)}}
    if nw and ns:
        incidence = (pw-ps)*(sw+ss)/2
        strength = (sw-ss)*(pw+ps)/2
        residual = mw-ms-incidence-strength
        if abs(residual) > 1e-10:
            raise AssertionError('Exact two-component decomposition did not reconcile')
        result.update({'incidence_component': incidence, 'positive_strength_component': strength,
                       'decomposition_residual': residual})
    else:
        result.update({'incidence_component': None, 'positive_strength_component': None,
                       'decomposition_residual': None,
                       'undefined_reason': 'Positive overlap strength is undefined in an all-zero season'})
    return result


def _window_score(monthly_pairs, months):
    scores = defaultdict(list)
    for month in months:
        for pair, value in monthly_pairs.get(month, {}).items():
            scores[pair].append(value)
    return {pair: math.fsum(v)/len(v) for pair, v in scores.items() if len(v) >= 2}


EARTH_RADIUS_KM = 6371.0
NEAR_CENTROID_KM = (25., 50., 100.)


def annual_day_balanced_centroids(events):
    """Internal 3D-unit-vector mean of daily position centers, never serialized.

    Each observed date has equal mass regardless of fix frequency. 3D vectors
    correctly handle longitude wraparound. An annual center is NOT a biological
    population label or measured interaction opportunity.
    """
    by_day = defaultdict(lambda: [0., 0., 0., 0])
    for fix in events:
        latitude, longitude = math.radians(fix.lat), math.radians(fix.lon)
        c = math.cos(latitude)
        xyz = (c * math.cos(longitude), c * math.sin(longitude), math.sin(latitude))
        state = by_day[(fix.year, fix.animal, fix.day)]
        for i in range(3):
            state[i] += xyz[i]
        state[3] += 1
    by_year_animal = defaultdict(lambda: [0., 0., 0., 0])
    for (year,animal,_), state in by_day.items():
        norm = math.sqrt(sum(state[i]**2 for i in range(3)))
        if norm <= 1e-12:
            continue
        year_state = by_year_animal[(year,animal)]
        for i in range(3):
            year_state[i] += state[i] / norm
        year_state[3] += 1
    output = defaultdict(dict)
    for (year,animal),state in by_year_animal.items():
        norm = math.sqrt(sum(state[i]**2 for i in range(3)))
        if norm > 1e-12:
            output[year][animal] = tuple(state[i] / norm for i in range(3))
    return output


def centroid_distance_km(a, b):
    """Great-circle distance between source-year internal unit-vector centers."""
    dot = max(-1., min(1., math.fsum(a[i]*b[i] for i in range(3))))
    return EARTH_RADIUS_KM * math.acos(dot)


def compare_events(events, label_by_animal):
    by_year_month = defaultdict(list)
    for x in events:
        by_year_month[(x.year, x.month)].append(x)
    lat_cos = math.cos(math.radians(math.fsum(x.lat for x in events) / len(events))) if events else 1.0
    centers = annual_day_balanced_centroids(events)
    keys = [(float(k), float(x), float(y)) for k in DEFAULT_SCALES_KM for x, y in DEFAULT_ORIGINS]
    output = []
    for year in YEARS:
        monthly = {}
        for m in range(1, 13):
            seq = by_year_month.get((year, m), [])
            animals = {r.animal for r in seq}
            if len(animals) >= 2:
                _, pairs = compute_geography_overlap(seq, animals, lat_cos=lat_cos,
                                                     min_shared_days=7)
            else:
                pairs = {k: {} for k in keys}
            monthly[m] = pairs
        for grid_km, ox, oy in keys:
            for window_name, (first, second) in WINDOWS.items():
                first_pairs = _window_score({m:monthly[m][(grid_km,ox,oy)] for m in first}, first)
                second_pairs = _window_score({m:monthly[m][(grid_km,ox,oy)] for m in second}, second)
                risk_set = set(first_pairs) & set(second_pairs)
                pair_distances = {pair: centroid_distance_km(centers[year][pair[0]],
                                                            centers[year][pair[1]])
                                  for pair in risk_set if pair[0] in centers[year]
                                  and pair[1] in centers[year]}
                for mode in ('source_wide','near_centroid_25km','near_centroid_50km',
                             'near_centroid_100km','same_reference_label'):
                    if mode == 'source_wide':
                        selected = risk_set
                    elif mode == 'same_reference_label':
                        selected = {p for p in risk_set if p[0] in label_by_animal
                                    and p[1] in label_by_animal
                                    and label_by_animal[p[0]] == label_by_animal[p[1]]}
                    else:
                        threshold=float(mode.removeprefix('near_centroid_').removesuffix('km'))
                        selected = {p for p, distance in pair_distances.items()
                                    if distance <= threshold}
                    result = describe({p:first_pairs[p] for p in selected},
                                      {p:second_pairs[p] for p in selected})
                    output.append({'year': year, 'window': window_name,
                                   'grid_km':grid_km, 'origin_x_fraction':ox, 'origin_y_fraction':oy,
                                   'risk_set_mode':mode,
                                   'n_season1_supported_pairs':len(first_pairs),
                                   'n_season2_supported_pairs':len(second_pairs),
                                   'n_matched_animals':len({a for pair in selected for a in pair}),
                                   **result})
    return output


def process_source(label, cache):
    uuid, doi, taxon = SOURCES[label]
    out = {'label':label, 'doi':doi, 'taxon':taxon, 'status':'PENDING',
           'clock_verified_utc':False, 'population_independence_verified':False}
    stage = 'MANIFEST'
    try:
        item, entries = _manifest(uuid)
        gps = [x for x in entries if x['role'] == 'gps']
        refs = [x for x in entries if x['role'] == 'reference']
        out['source_title'] = item['name']
        out['gps_archived_bytes'] = sum(x['size'] for x in gps)
        if len(refs) != 1 or not gps:
            out['status'] = 'STOP_MISSING_FULL_ORIGINAL_GPS_OR_REFERENCE'
            return out
        if out['gps_archived_bytes'] > MAX_ARCHIVE_BYTES:
            out['status'] = 'STOP_SOURCE_TOO_LARGE_FOR_BOUNDED_ACQUISITION'
            return out
        if sum(x['size'] for x in refs) > 10 * 1024 * 1024:
            out['status'] = 'STOP_REFERENCE_TOO_LARGE_FOR_BOUNDED_ACQUISITION'
            return out
        stage = 'DOWNLOAD_AND_MD5'
        paths, receipts = {}, []
        for e in gps + refs:
            path, receipt = _download(e, cache)
            paths[e['uuid']] = (path, e['filename'])
            receipts.append(receipt)
        out['file_receipts'] = receipts
        stage = 'JOIN_AND_GPS_QUALITY'
        events, audit, labels = read_originals([paths[e['uuid']] for e in gps], paths[refs[0]['uuid']], taxon)
        out['event_audit'] = audit
        if not events:
            out['status'] = ('STOP_NO_VALID_SOURCE_TIMESTAMPS_OR_COORDINATES'
                             if audit.get('invalid_timestamp',0) or audit.get('invalid_position',0)
                             else 'STOP_NO_TARGET_FIXES_IN_DECLARED_YEARS')
            return out
        stage = 'MATCHED_DYAD_ANALYSIS'
        out['comparisons'] = compare_events(events, labels)
        out['estimable_rows'] = sum(r['status']=='DESCRIPTIVE_MATCHED_DYADS' for r in out['comparisons'])
        out['status'] = ('COMPLETE_EXPLORATORY_GEOGRAPHIC_X' if out['estimable_rows']
                         else 'NOT_ESTIMABLE_MATCHED_SEASONAL_DYADS')
    except Exception as exc:
        # Never write exceptions that might contain identifiers or coordinates.
        out['status'] = 'STOP_SOURCE_OR_ANALYSIS_ERROR'
        out['error_class'] = type(exc).__name__
        out['error_stage'] = stage
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=sorted(SOURCES), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cache', type=Path)
    args = parser.parse_args()
    folder = args.cache or Path(tempfile.mkdtemp(prefix='mb_source_x_'))
    folder.mkdir(parents=True, exist_ok=True)
    source = process_source(args.only, folder)
    result = {'schema_version':2, 'as_of':'2026-10-20',
              'status':'EXPLORATORY_NOT_CROSS_TAXON_INFERENCE',
              'analysis_method':'two seasons, same pair risk set, date-balanced 2D occupancy',
              'timing':'Post-prior-session exploratory reconstruction, NOT independent preregistration',
              'grid_widths_km':list(DEFAULT_SCALES_KM),
              'grid_origins':[list(x) for x in DEFAULT_ORIGINS],
              'month_windows':{k:[list(a),list(b)] for k,(a,b) in WINDOWS.items()},
              'near_centroid_thresholds_km':list(NEAR_CENTROID_KM),
              'centroid_method':'unit-sphere annual center, equal observed dates; opportunity proxy only',
              'source':source,
              'restrictions':['Only aggregate output; never commit full source animal tracks',
                              'Not simultaneous encounters, dietary sharing or causal partitioning',
                              'Seasonal windows are calendar labels, not known migration state',
                              'Within-reference-label is a proxy and does not establish actual social population',
                              'Annual-centroid proximity is a post-session geometric sensitivity, not evidence of encounters']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'source':args.only,'status':source['status'],
                      'original_MD5s_checked':len(source.get('file_receipts',[])),
                      'retained_fixes':source.get('event_audit',{}).get('retained_fixes'),
                      'estimable_scenarios':source.get('estimable_rows',0)},sort_keys=True))
    # Source errors get a nonzero job status while still uploading safe receipt.
    if source['status']=='STOP_SOURCE_OR_ANALYSIS_ERROR':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
