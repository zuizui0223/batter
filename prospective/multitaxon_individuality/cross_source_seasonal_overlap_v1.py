#!/usr/bin/env python3
"""Movebank cross-source seasonal spatial incidence/strength, original-file-only.

Exploratory fixed-window extension: three original Movebank packages chosen from
an existing metadata queue, not selected by observed overlap effects. Original
CSV/ZIP and references are checked against the published MD5 before analysis.
Nothing identifying an individual, date or coordinate is written or printed.
No p-values, randomization claims, resource-use or encounter claims.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import tempfile
import time
from urllib.request import urlopen, Request
import zipfile

API = 'https://datarepository.movebank.org/server/api/core/'
# UUIDs were in the pre-existing 437-package source-registry / selection queue.
SOURCES = [
    ('turkey', 'dd064947-25b7-46a2-8976-adfc488750bc', '10.5441/001/1.671', 'Meleagris gallopavo'),
    ('moose', '26a9d940-906d-490b-a87d-02be51e5e21f', '10.5441/001/1.714', 'Alces alces'),
    ('black_bear', '89b8132d-fc88-498f-9040-39643b387dd4', '10.5441/001/1.706', 'Ursus americanus'),
]
YEARS = (2019, 2020)
GRIDS_KM = (1, 2, 5, 10)
ORIGINS = ((0., 0.), (.5, 0.), (0., .5), (.5, .5))
WINDOWS = {
    'winter_summer': ((12, 1, 2), (6, 7, 8)),
    'early_late': ((1, 2), (3, 4)),
}
MAX_GPS_ARCHIVE_BYTES = 170 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 1200 * 1024 * 1024
MIN_SHARED_DATES_PER_MONTH = 7
MIN_MONTHS_PER_SEASON = 2
MAX_RETAINED_EVENTS_PER_SOURCE = 2_600_000


def _get(url, *, tries=3):
    last = None
    for attempt in range(tries):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'research-reproducibility/1.0'}), timeout=90) as res:
                return res.read()
        except Exception as exc:
            last = exc
            if attempt + 1 < tries:
                time.sleep(2 ** attempt)
    raise RuntimeError('Source endpoint failed after retries: ' + url.split('/')[-1]) from last


def _json(url):
    return json.loads(_get(url).decode('utf-8'))


def _digest(path, alg):
    h = hashlib.new(alg)
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def _stream_file(url, target, expected_size):
    last = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'research-reproducibility/1.0'}), timeout=120) as res, open(target, 'wb') as f:
                size = 0
                for chunk in iter(lambda: res.read(1024 * 1024), b''):
                    size += len(chunk)
                    if size > expected_size:
                        raise RuntimeError('Download size exceeded publisher manifest')
                    f.write(chunk)
            if size != expected_size:
                raise RuntimeError('Incomplete published original')
            return
        except Exception as exc:
            last = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError('Original download failed: ' + str(expected_size) + ' bytes') from last


def _original_manifest(uid):
    item = _json(API + 'items/' + uid)
    bundles = _json(API + 'items/' + uid + '/bundles?size=100')
    if bundles.get('page', {}).get('totalPages') != 1:
        raise ValueError('Unexpected ORIGINAL bundle pagination')
    originals = [b for b in bundles['_embedded']['bundles'] if b['name'] == 'ORIGINAL']
    if len(originals) != 1:
        raise ValueError('Missing or non-unique ORIGINAL bundle')
    listing = _json(originals[0]['_links']['bitstreams']['href'] + '?size=100')
    if listing.get('page', {}).get('totalPages') != 1:
        raise ValueError('Unexpected bitstream pagination')
    entries = []
    for row in listing['_embedded']['bitstreams']:
        name = row['name'].lower()
        if row['checkSum']['checkSumAlgorithm'].upper() != 'MD5':
            raise ValueError('Original publisher MD5 missing')
        role = 'reference' if 'reference-data' in name else ('readme' if name == 'readme.txt' else
               'other' if any(t in name for t in ('-acc-', '-acc.', '-mag.', '-orientation.', 'acceleration')) else
               'gps' if name.endswith(('.csv', '.csv.zip', '.csv.gz', '.zip')) else 'other')
        entries.append({'filename': row['name'], 'uuid': row['uuid'], 'role': role,
                        'bytes': row['sizeBytes'], 'md5': row['checkSum']['value'],
                        'content_url': row['_links']['content']['href']})
    return item, entries


def _read_csv(path, filename):
    low = filename.lower()
    if low.endswith('.zip'):
        with zipfile.ZipFile(path) as archive:
            members = [m for m in archive.infolist()
                if not m.is_dir() and not m.filename.startswith('__MACOSX/')
                and Path(m.filename).name.lower().endswith('.csv')
                and not Path(m.filename).name.startswith('._')]
            if len(members) != 1:
                raise ValueError('ZIP must contain exactly one real source CSV (no partial parse)')
            if members[0].file_size > MAX_UNCOMPRESSED_BYTES:
                raise ValueError('Uncompressed source exceeds declared safety bound')
            with archive.open(members[0]) as binary:
                with io.TextIOWrapper(binary, encoding='utf-8-sig', newline='') as stream:
                    yield from csv.DictReader(stream)
    elif low.endswith('.gz'):
        with gzip.open(path, mode='rt', encoding='utf-8-sig', newline='') as stream:
            yield from csv.DictReader(stream)
    elif low.endswith('.csv'):
        with open(path, encoding='utf-8-sig', newline='') as stream:
            yield from csv.DictReader(stream)
    else:
        raise ValueError('Unexpected original GPS file extension')


def _parse_time(raw):
    dt = datetime.fromisoformat(raw.strip().replace('Z', '+00:00'))
    return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt


def _source_year_records(gps_paths, reference_path, taxon):
    refs = defaultdict(set)
    sites = defaultdict(set)
    ref_sexes = Counter()
    ref_rows = 0
    for row in _read_csv(*reference_path):
        ref_rows += 1
        animal = row.get('animal-id', '').strip()
        tag = row.get('tag-id', '').strip()
        if animal and tag:
            refs[animal].add(tag)
            site = (row.get('study-site') or row.get('animal-group-id') or '').strip()
            if site:
                sites[animal].add(site)
        ref_sexes[row.get('animal-sex','').strip() or 'missing'] += 1
    if not refs:
        raise ValueError('Missing reference animal/tag identifiers')
    observation_counts = Counter()
    by_animal_timestamp = {}
    sensor_counts = Counter()
    all_taxa = Counter()
    for path, filename in gps_paths:
        for row in _read_csv(path, filename):
            observation_counts['original_rows'] += 1
            animal = (row.get('individual-local-identifier') or '').strip()
            tag = (row.get('tag-local-identifier') or '').strip()
            sensor = (row.get('sensor-type') or '').lower().strip()
            sensor_counts[sensor or 'missing'] += 1
            observed_taxon = (row.get('individual-taxon-canonical-name') or '').strip()
            all_taxa[observed_taxon or 'missing'] += 1
            if sensor != 'gps' or (row.get('visible') or '').lower().strip() not in ('true','1'):
                observation_counts['sensor_or_visibility_removed'] += 1
                continue
            if observed_taxon != taxon:
                observation_counts['non_target_taxon_removed'] += 1
                continue
            if not animal or tag not in refs.get(animal, set()):
                observation_counts['reference_pair_mismatch_removed'] += 1
                continue
            if any((row.get(flag) or '').lower().strip() in ('true', '1')
                   for flag in ('manually-marked-outlier','algorithm-marked-outlier','automatically-marked-outlier')):
                observation_counts['source_outlier_removed'] += 1
                continue
            try:
                dt = _parse_time(row['timestamp'])
                lat, lon = float(row['location-lat']), float(row['location-long'])
                if not all(map(math.isfinite, (lat, lon))) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
                    raise ValueError
            except (ValueError, KeyError, TypeError):
                observation_counts['invalid_position_or_clock_removed'] += 1
                continue
            if dt.year not in YEARS:
                observation_counts['outside_fixed_years_removed'] += 1
                continue
            key = (animal, dt)
            datum = (animal, dt.year, dt.month, dt.toordinal(), lon, lat, tag)
            if key in by_animal_timestamp:
                prev = by_animal_timestamp[key]
                if prev != datum:
                    by_animal_timestamp[key] = None
                    observation_counts['conflicting_time_removed'] += 1
                else:
                    observation_counts['identical_duplicate_removed'] += 1
            else:
                by_animal_timestamp[key] = datum
            if len(by_animal_timestamp) > MAX_RETAINED_EVENTS_PER_SOURCE:
                raise ValueError('Event safety bound reached: full source cannot be processed')
    events = [e for e in by_animal_timestamp.values() if e is not None]
    events.sort(key=lambda e: (e[1],e[2],e[0],e[3]))
    summary = {'original_rows': observation_counts['original_rows'], 'valid_fixed_year_events':len(events),
               'reference_rows':ref_rows,'reference_animals':len(refs),
               'animals_with_unambiguous_site_label':sum(len(v)==1 for v in sites.values()),
               'animals_with_multiple_site_labels':sum(len(v)>1 for v in sites.values()),
               'n_source_site_labels':len({v for values in sites.values() for v in values}),
               'reference_sexes':dict(ref_sexes),
               'sensor_row_counts':dict(sensor_counts),
               'taxon_row_counts':dict(all_taxa),
               'filter_counts':dict(observation_counts),
               'source_clock_verified_utc':False,
               'source_sites_not_harmonized':True}
    return events, summary


def calculate_incidence_strength(winter_scores, summer_scores):
    """Same fully supported dyad risk set in both seasons, no imputation.

    Returns a zero-safe mean and transition counts. Contributions are only
    identified when both seasons contain a strictly positive overlap.
    """
    if set(winter_scores) != set(summer_scores):
        raise ValueError('Both seasons must have identical dyad risk sets')
    if not winter_scores:
        return {'n_pairs':0, 'status':'NOT_ESTIMABLE_NO_MATCHED_PAIRS'}
    for v in list(winter_scores.values()) + list(summer_scores.values()):
        if v is None or not math.isfinite(v) or not 0 <= v <= 1:
            raise ValueError('Missing or invalid overlap values cannot be zero-imputed')
    N = len(winter_scores)
    w, s = list(winter_scores.values()), list(summer_scores.values())
    n_w, n_s = sum(v > 0 for v in w), sum(v > 0 for v in s)
    p_w,p_s = n_w / N,n_s / N
    mu_w = math.fsum(w)/N
    mu_s = math.fsum(s)/N
    strength_w = math.fsum(v for v in w if v > 0)/n_w if n_w else None
    strength_s = math.fsum(v for v in s if v > 0)/n_s if n_s else None
    counts = Counter(('1' if winter_scores[k] > 0 else '0') + ('1' if summer_scores[k] > 0 else '0') for k in winter_scores)
    out = {
        'status':'OBSERVED_MATCHED_DYADS', 'n_pairs':N,
        'winter':{'n_positive_pairs':n_w,'positive_fraction':p_w, 'conditional_strength':strength_w, 'mean_X':mu_w},
        'summer':{'n_positive_pairs':n_s,'positive_fraction':p_s, 'conditional_strength':strength_s, 'mean_X':mu_s},
        'winter_minus_summer_X':mu_w-mu_s,
        'pair_state_counts':{'both_zero':counts['00'],'winter_only':counts['10'],
              'summer_only':counts['01'],'both_positive':counts['11']},
        'fraction_pairs_winter_higher':sum(winter_scores[k] > summer_scores[k] for k in winter_scores)/N,
        'fraction_pairs_summer_higher':sum(winter_scores[k] < summer_scores[k] for k in winter_scores)/N,
    }
    if n_w and n_s:
        incidence = (p_w-p_s)*(strength_w+strength_s)/2
        intensity = (strength_w-strength_s)*(p_w+p_s)/2
        residual = (mu_w-mu_s)-incidence-intensity
        if abs(residual) > 1e-10:
            raise AssertionError('Decomposition failed exact verification')
        out.update({'incidence_component':incidence,'strength_component':intensity,
                    'decomposition_residual':residual})
    else:
        out.update({'incidence_component':None,'strength_component':None,
                    'decomposition_residual':None,
                    'unidentified_reason':'Conditional strength is undefined in a season with no positive pairs'})
    return out


def pair_date_geography(events, year, month, scale, origin, lat_cos=1.0):
    """All matched months use the exact source-calendar same-date intersection.

    Parse all records once, rebuild a day's 2D occupancy at each grid. A pair
    requires >=7 shared observed dates. Daily distribution is equal-weighted,
    then pair-shared days equal-weighted. Dataset has no actual encounter clock.
    """
    rows = [r for r in events if r[1] == year and r[2] == month]
    if not rows:
        return {}
    # Projection is source-fixed: seasonal shifts may not recenter the grid.
    xscale=111.32*lat_cos
    occupancy=defaultdict(lambda:defaultdict(Counter))
    for animal,_,_,day,lon,lat,_ in rows:
        cell=(math.floor((lon*xscale)/scale+origin[0]), math.floor((lat*111.32)/scale+origin[1]))
        occupancy[animal][day][cell]+=1
    daily={animal:{d:{cell:n/sum(c.values()) for cell,n in c.items()} for d,c in days.items()}
           for animal,days in occupancy.items()}
    pair_overlap={}
    for a,b in combinations(sorted(daily),2):
        days=sorted(set(daily[a]) & set(daily[b]))
        if len(days)<MIN_SHARED_DATES_PER_MONTH:
            continue
        pa,pb=defaultdict(float),defaultdict(float)
        for d in days:
            for c,v in daily[a][d].items():pa[c]+=v/len(days)
            for c,v in daily[b][d].items():pb[c]+=v/len(days)
        if len(pa)>len(pb):pa,pb=pb,pa
        pair_overlap[(a,b)]=max(0.,min(1.,math.fsum(min(v,pb.get(c,0.)) for c,v in pa.items())))
    return pair_overlap


def _combine_window(monthly, months):
    """Retain a pair when >=2 specified months supply pair-matched dates."""
    by_pair=defaultdict(list)
    for m in months:
        for pair,val in monthly.get(m,{}).items():
            by_pair[pair].append(val)
    return {pair:math.fsum(values)/len(values) for pair,values in by_pair.items()
            if len(values)>=MIN_MONTHS_PER_SEASON}


def compute_source_comparisons(events):
    results=[]
    lat_cos = math.cos(math.radians(math.fsum(r[5] for r in events)/len(events))) if events else 1.0
    for year in YEARS:
        for scale in GRIDS_KM:
            for origin in ORIGINS:
                per_month={m:pair_date_geography(events,year,m,scale,origin,lat_cos=lat_cos) for m in range(1,13)}
                for label,(winter_months,summer_months) in WINDOWS.items():
                    winter = _combine_window(per_month,winter_months)
                    summer = _combine_window(per_month,summer_months)
                    shared=set(winter)&set(summer)
                    outcome=calculate_incidence_strength({pair:winter[pair] for pair in shared},
                                                          {pair:summer[pair] for pair in shared})
                    results.append({'year':year,'window':label,'grid_km':scale,
                                    'origin_x_fraction':origin[0],'origin_y_fraction':origin[1],
                                    'n_season1_supported_pairs':len(winter),
                                    'n_season2_supported_pairs':len(summer),
                                    'n_matched_animals':len({a for pair in shared for a in pair}),
                                    **outcome})
    return results


def process_one(label,uid,doi,taxon,cache):
    record={'label':label,'doi':doi,'taxon':taxon,
            'status':'PENDING','source_clock_verified_utc':False,
            'source_population_independence_verified':False}
    try:
        item, entries=_original_manifest(uid)
        role_gps=[e for e in entries if e['role']=='gps']
        references=[e for e in entries if e['role']=='reference']
        record.update({'source_title':item['name'],
                       'rights':[v['value'] for v in item.get('metadata',{}).get('dc.rights',[])],
                       'original_gps_file_count':len(role_gps),
                       'original_gps_total_bytes':sum(e['bytes'] for e in role_gps),
                       'original_reference_file_count':len(references),
                       'original_manifest':[{k:e[k] for k in ('filename','bytes','md5','role')} for e in entries]})
        if len(references)!=1 or not role_gps:
            record['status']='STOP_MISSING_COMPLETE_GPS_OR_REFERENCE'
            return record
        if sum(e['bytes'] for e in role_gps)>MAX_GPS_ARCHIVE_BYTES:
            record['status']='STOP_COMPLETE_GPS_EXCEEDS_BOUNDED_BYTES'
            return record
        manifests=[]
        for entry in role_gps+references:
            file=cache / (entry['uuid']+'.bin')
            if not file.exists() or file.stat().st_size!=entry['bytes']:
                _stream_file(entry['content_url'],file,entry['bytes'])
            if file.stat().st_size!=entry['bytes'] or _digest(file,'md5')!=entry['md5']:
                raise RuntimeError('Publisher original-file MD5 mismatch')
            manifests.append({'role':entry['role'],'filename':entry['filename'],
                              'bytes':entry['bytes'],'md5_verified':True,
                              'sha256':_digest(file,'sha256')})
        record['validated_files']=manifests
        gp=list(zip((cache / (e['uuid']+'.bin') for e in role_gps), (e['filename'] for e in role_gps)))
        ref=(cache / (references[0]['uuid']+'.bin'), references[0]['filename'])
        events, audit = _source_year_records(gp, ref, taxon)
        record['event_audit']=audit
        record['comparisons']=compute_source_comparisons(events)
        record['status']='COMPLETE_EXPLORATORY_GEOGRAPHIC_X'
        record['number_estimated_comparisons']=sum(v['status']=='OBSERVED_MATCHED_DYADS' for v in record['comparisons'])
    except Exception as exc:
        # Not recording exceptions with source-animal fields and positions.
        record['status']='STOP_SOURCE_OR_ANALYSIS_ERROR'
        record['error_class']=type(exc).__name__
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,default=Path(tempfile.gettempdir())/'movebank_x_repeat_cache')
    p.add_argument('--out',type=Path,default=Path('CROSS_SOURCE_SEASONAL_X_2026_10_20.json'))
    p.add_argument('--only',choices=[s[0] for s in SOURCES],nargs='*')
    args=p.parse_args()
    args.cache.mkdir(parents=True,exist_ok=True)
    selected=[s for s in SOURCES if args.only is None or s[0] in args.only]
    summary={'schema_version':1,'analysis_date':'2026-10-20',
             'registration_status':'Post-existing exploratory selection. Script fixed before this run; NOT independent preregistration.',
             'source_registry_selection':'3 previously queued sources, not favorable-effect sampling',
             'years':YEARS,'windows':{k:{'season1':w,'season2':s} for k,(w,s) in WINDOWS.items()},
             'grids_km':GRIDS_KM,'origins':ORIGINS,
             'controls':{'month_pair_same_source_calendar_dates':MIN_SHARED_DATES_PER_MONTH,
                         'min_support_months_per_season':MIN_MONTHS_PER_SEASON,
                         'same_risk_dyads_both_seasons':True,
                         'monthly_occupancy_weighting':'equal pair-shared observed days then equal fixes per day',
                         'seasonal_occupancy_weighting':'equal supported months per dyad',
                         'sensitivity':'all 16 grids/origins, no optimized grid'},
             'limitations':['Only 2D position: E trophic/environmental resource and T synchronous encounter unavailable',
                            'Broad source package may contain distant populations or heterogenous cohorts; no shared-pool assertion',
                            'Months use native source dates; UTC/GPS ambiguity may remain',
                            'No sampling-rate or true-simultaneity adjustment; results are exploratory',
                            'Years or dyads cannot be counted as independent biological replications',
                            'The three source packages may derive from one 2026 paper: DOIs do not equal independent hypotheses'],
             'sources':[]}
    for source in selected:
        result=process_one(*source,args.cache)
        summary['sources'].append(result)
        comparable=[v for v in result.get('comparisons',[]) if v['status']=='OBSERVED_MATCHED_DYADS'
                    and v['grid_km']==5 and v['origin_x_fraction']==0 and v['origin_y_fraction']==0]
        print(json.dumps({'source':result['label'],'status':result['status'],
                          'original_rows':result.get('event_audit',{}).get('original_rows'),
                          'comparisons_5km_origin0':[{'year':v['year'],'window':v['window'],
                             'n_matched_animals':v['n_matched_animals'],'n_pairs':v['n_pairs'],
                             'delta_x':v['winter_minus_summer_X'],'n_pos_first':v['winter']['n_positive_pairs'],
                             'n_pos_second':v['summer']['n_positive_pairs']} for v in comparable]}),flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('RESULT_FILE',str(args.out),flush=True)

if __name__=='__main__':main()