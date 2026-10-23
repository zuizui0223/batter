#!/usr/bin/env python3
"""Bounded source-date-only rescue for the malformed Bighorn Mountain moose archive.

Exact original Movebank GPS and reference bytes must match publisher MD5.
The source writes an invalid literal 'S' as the final seconds character in
all of its GPS timestamp strings. This code parses calendar DATE only, does NOT
impute seconds or assert an absolute UTC offset, and uses the complete original
character string for duplicate animal/timestamp checks. Only pair-date-balanced
2D geographic occupancy X is estimated, never velocity, encounters T or behavior R.

This is a post-format-diagnostic exploratory analysis, not preregistration or a
biological source-population check. Aggregate-only JSON is written.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile

from cross_source_seasonal_overlap_v1 import (
    _original_manifest, _stream_file, _digest, _read_csv,
    MAX_GPS_ARCHIVE_BYTES, compute_source_comparisons,
)

SOURCE_UID='26a9d940-906d-490b-a87d-02be51e5e21f'
SOURCE_DOI='10.5441/001/1.714'
SOURCE_TAXON='Alces alces'
# The literal suffix is deliberately not treated as a recoverable second.
MALFORMED_SOURCE_CLOCK=re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\dS$')


def date_only(raw):
    """Return (calendar year, month, ordinal day); do not invent HH:MM:SS."""
    if not MALFORMED_SOURCE_CLOCK.fullmatch(raw.strip()):
        raise ValueError('Source timestamp does not match the observed S-tail format')
    day=datetime.strptime(raw[:10], '%Y-%m-%d')
    return day.year,day.month,day.toordinal()


def source_rows(gps_paths, reference_path):
    refs=defaultdict(set)
    ref_rows=0
    for row in _read_csv(*reference_path):
        ref_rows+=1
        animal=(row.get('animal-id') or '').strip()
        tag=(row.get('tag-id') or '').strip()
        if animal and tag:
            refs[animal].add(tag)
    if not refs:
        raise ValueError('Original reference contains no valid animal/tag pairs')
    counts=Counter({k:0 for k in ('original_rows','non_gps_removed','not_visible_removed',
        'wrong_taxon_removed','reference_mismatch_removed','source_outlier_removed',
        'malformed_date_or_position_removed','out_of_fixed_years_removed',
        'exact_duplicate_removed','conflicting_timestamp_rows')})
    by_timestamp={}
    for path,filename in gps_paths:
        for row in _read_csv(path, filename):
            counts['original_rows']+=1
            sensor=(row.get('sensor-type') or '').strip().lower()
            if sensor!='gps':
                counts['non_gps_removed']+=1
                continue
            if (row.get('visible') or '').strip().lower() not in ('true','1'):
                counts['not_visible_removed']+=1
                continue
            if (row.get('individual-taxon-canonical-name') or '').strip()!=SOURCE_TAXON:
                counts['wrong_taxon_removed']+=1
                continue
            animal=(row.get('individual-local-identifier') or '').strip()
            tag=(row.get('tag-local-identifier') or '').strip()
            if tag not in refs.get(animal,set()):
                counts['reference_mismatch_removed']+=1
                continue
            if any((row.get(key) or '').strip().lower() in ('true','1') for key in
                   ('manually-marked-outlier','algorithm-marked-outlier','automatically-marked-outlier')):
                counts['source_outlier_removed']+=1
                continue
            raw=(row.get('timestamp') or '').strip()
            try:
                year,month,day=date_only(raw)
                lat,lon=float(row['location-lat']),float(row['location-long'])
                if not (math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
                    raise ValueError('Invalid source position')
            except (KeyError,TypeError,ValueError):
                counts['malformed_date_or_position_removed']+=1
                continue
            if year not in (2019,2020):
                counts['out_of_fixed_years_removed']+=1
                continue
            # The exact raw timestamp (NOT an imputed seconds value) protects
            # against collapsing valid same-day or same-minute GPS fixes.
            key=(animal,raw)
            event=(animal,year,month,day,lon,lat,tag)
            if key in by_timestamp:
                if by_timestamp[key]==event:
                    counts['exact_duplicate_removed']+=1
                else:
                    counts['conflicting_timestamp_rows']+=1
                    by_timestamp[key]=None
            else:
                by_timestamp[key]=event
    events=[value for value in by_timestamp.values() if value is not None]
    events.sort(key=lambda x:(x[1],x[2],x[0],x[3]))
    counts['retained_events']=len(events)
    counts['retained_animals']=len({x[0] for x in events})
    counts['reference_rows']=ref_rows
    counts['reference_animals']=len(refs)
    counts['source_timestamp_format']='YYYY-MM-DD HH:MM:dS (d is one numeral; literal S remains unresolved)'
    counts['calendar_day_verified_by_strptime']=True
    counts['seconds_imputed']=False
    counts['full_timestamp_or_utc_verified']=False
    counts['rows_by_year']=dict(sorted(Counter(x[1] for x in events).items()))
    return events,dict(counts)


def run(cache:Path, out:Path):
    cache.mkdir(parents=True,exist_ok=True)
    source={'doi':SOURCE_DOI,'taxon':SOURCE_TAXON,
            'status':'PENDING','original_file_md5_verified':False,
            'native_seconds_known':False,'utc_verified':False,
            'study_population_harmonized':False}
    try:
        item,entries=_original_manifest(SOURCE_UID)
        gps=[e for e in entries if e['role']=='gps']
        ref=[e for e in entries if e['role']=='reference']
        source['source_title']=item['name']
        if len(ref)!=1 or not gps or sum(e['bytes'] for e in gps)>MAX_GPS_ARCHIVE_BYTES:
            source['status']='STOP_INCOMPLETE_OR_OVERSIZE_ORIGINALS'
        else:
            paths={}
            receipts=[]
            for e in gps+ref:
                path=cache/(e['uuid']+'.bin')
                if not path.exists() or path.stat().st_size!=e['bytes']:
                    _stream_file(e['content_url'],path,e['bytes'])
                if _digest(path,'md5')!=e['md5'] or path.stat().st_size!=e['bytes']:
                    raise ValueError('Original source checksum mismatch')
                paths[e['uuid']]=(path,e['filename'])
                receipts.append({'role':e['role'],'bytes':e['bytes'],
                                 'publisher_md5_verified':True,
                                 'sha256':_digest(path,'sha256')})
            source['original_file_receipts']=receipts
            source['original_file_md5_verified']=True
            events,audit=source_rows([paths[e['uuid']] for e in gps],paths[ref[0]['uuid']])
            source['date_only_source_audit']=audit
            # If a single accepted GPS row fails date/position parsing, report
            # the STOP instead of silently selecting favourable observations.
            if (audit['malformed_date_or_position_removed'] or
                    audit['reference_mismatch_removed'] or
                    audit['conflicting_timestamp_rows'] or
                    audit['retained_events']!=52648):
                source['status']='STOP_SOURCE_QC_OR_EXPECTED_COVERAGE_MISMATCH'
            else:
                source['comparisons']=compute_source_comparisons(events)
                source['status']='EXPLORATORY_DATE_ONLY_GEOGRAPHIC_X'
                source['n_estimable']=sum(x['status']=='OBSERVED_MATCHED_DYADS' for x in source['comparisons'])
    except Exception as exc:
        # Do not expose exception text: it could contain original identity data.
        source['status']='STOP_SOURCE_OR_ANALYSIS_ERROR'
        source['error_class']=type(exc).__name__
    result={'schema_version':1,'as_of':'2026-10-20',
            'design_status':'STRICT_POST_DIAGNOSTIC_DATE_ONLY_RESCUE_BEFORE_VIEWING_X_OUTCOMES',
            'source':source,'inference_limitations':[
                'Original trailing S cannot be converted to known seconds; only calendar dates are used',
                'Source date clock is not verified UTC or corrected to local midnight',
                'Source-wide dyads need independent local-population opportunity validation',
                'Source comparisons are 2D geographic overlap, not encounters, diet or behavioral individuality',
                'No biological p-values or repeated independent study effects']}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'doi':SOURCE_DOI,'status':source['status'],
                      'md5_verified':source.get('original_file_md5_verified'),
                      'n_events':source.get('date_only_source_audit',{}).get('retained_events'),
                      'n_estimable_scenarios':source.get('n_estimable',0)},sort_keys=True))
    for row in source.get('comparisons',[]):
        if row['grid_km']==5 and row['origin_x_fraction']==row['origin_y_fraction']==0:
            print(json.dumps({'year':row['year'],'window':row['window'],
                              'status':row['status'],'n_pairs':row['n_pairs'],
                              'n_animals':row['n_matched_animals'],
                              'mean_difference':row.get('winter_minus_summer_X'),
                              'pair_states':row.get('pair_state_counts')},sort_keys=True))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,default=Path(tempfile.gettempdir())/'bighorn_date_only_originals_v1')
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    result=run(args.cache,args.out)
    if result['source']['status']=='STOP_SOURCE_OR_ANALYSIS_ERROR':
        raise SystemExit(2)


if __name__=='__main__':
    main()