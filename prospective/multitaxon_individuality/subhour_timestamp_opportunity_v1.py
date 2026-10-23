#!/usr/bin/env python3
"""Source-original short-lag GPS timestamp pairing FEASIBILITY, not encounters.

Reconstruct fully checksum-pinned original event GPS, verify exact accepted
position multi-set, and report only source/year counts of dyads with sufficient
<=15 or <=30 min source-clock fix matching on shared observed dates.
No geographic proximity, interaction, resource or biological effect is
estimated. Original animal IDs, positions and exact times never serialized.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import tempfile

import cross_source_seasonal_x_v2 as baseline
import same_clock_bin_couse_v1 as timed

SOURCES=timed.SOURCES
YEARS=timed.YEARS
WINTER=timed.WINTER
SUMMER=timed.SUMMER
WINDOW_MONTHS=WINTER+SUMMER
GAPS_IN_SECONDS=(900,1800)
MIN_MATCHED_FIX_PAIRS_PER_DATE=3
MIN_SHARED_DATES_PER_MONTH=7
MIN_MONTHS_PER_SEASON=2
MIN_READY_DYADS=8
MIN_READY_ANIMALS=3


def original_native_second_fix_times(source, folder, accepted):
    uuid,doi,taxon=baseline.SOURCES[source]
    _,entries=baseline._manifest(uuid)
    gps=[r for r in entries if r['role']=='gps']
    refs=[r for r in entries if r['role']=='reference']
    if len(refs)!=1 or not gps:
        raise AssertionError('Expected published full GPS and unique reference')
    all_files={}
    for entry in gps+refs:
        path,_=baseline._download(entry,folder)
        all_files[entry['uuid']]=(path,entry['filename'])
    ref_join={(r.get('animal-id','').strip(),r.get('tag-id','').strip())
              for r in baseline._csv_rows(*all_files[refs[0]['uuid']])}
    if not ref_join:
        raise AssertionError('Source lacks independently verified reference animal tags')
    by_key={}
    for entry in gps:
        for r in baseline._csv_rows(*all_files[entry['uuid']]):
            if (r.get('sensor-type') or '').strip().lower()!='gps':
                continue
            if (r.get('visible') or '').strip().lower() not in ('true','1'):
                continue
            if (r.get('individual-taxon-canonical-name') or '').strip()!=taxon:
                continue
            animal=(r.get('individual-local-identifier') or '').strip()
            tag=(r.get('tag-local-identifier') or '').strip()
            if (animal,tag) not in ref_join:
                continue
            if any((r.get(col) or '').strip().lower() in ('true','1')
                   for col in ('manually-marked-outlier','algorithm-marked-outlier',
                               'automatically-marked-outlier')):
                continue
            try:
                dt=datetime.fromisoformat(r['timestamp'].strip().replace('Z','+00:00'))
                lat=float(r['location-lat'])
                lon=float(r['location-long'])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
                import math
                if not (math.isfinite(lat) and math.isfinite(lon)):
                    continue
            except (ValueError,TypeError,KeyError):
                continue
            if dt.year not in YEARS:
                continue
            fix=(animal,dt.year,dt.month,dt.toordinal(),lat,lon)
            key=(animal,dt)
            if key in by_key:
                if by_key[key]!=fix:
                    by_key[key]=None
            else:
                by_key[key]=fix
    verified={key:value for key,value in by_key.items() if value is not None}
    accepted_positions=Counter((x.animal,x.year,x.month,x.day,x.lat,x.lon) for x in accepted)
    recovered_positions=Counter(verified.values())
    if recovered_positions!=accepted_positions or len(verified)!=len(accepted):
        raise AssertionError('Independent sub-hour source-time join differs from pinned original GPS fixes')
    by_day=defaultdict(list)
    for (animal,dt),value in verified.items():
        second=dt.hour*3600+dt.minute*60+dt.second+dt.microsecond/1e6
        by_day[(dt.year,dt.month,animal,dt.toordinal())].append(second)
    return {k:tuple(sorted(v)) for k,v in by_day.items()}


def paired_fix_count(a,b,maximum_gap_seconds):
    """Optimal one-to-one greedy pairing of two sorted timestamp sequences."""
    i=j=count=0
    while i<len(a) and j<len(b):
        d=a[i]-b[j]
        if abs(d)<=maximum_gap_seconds+1e-9:
            i+=1;j+=1;count+=1
        elif d < 0:
            i+=1
        else:
            j+=1
    return count


def _quantile(values,p):
    if not values:return None
    ordered=sorted(values)
    pos=(len(ordered)-1)*p
    lo=int(pos)
    hi=min(lo+1,len(ordered)-1)
    return ordered[lo]+(ordered[hi]-ordered[lo])*(pos-lo)


def time_opportunity(byday, original_pairs, year, tolerance):
    eligible={}
    all_positive_dates=0
    all_positive_fix_pairs=0
    by_animal_month=defaultdict(dict)
    for (y,m,animal,day),seq in byday.items():
        if y==year and m in WINDOW_MONTHS:
            by_animal_month[(animal,m)][day]=seq
    for pair in sorted(original_pairs):
        a,b=pair
        support={}
        for month in WINDOW_MONTHS:
            dates_a=by_animal_month.get((a,month),{})
            dates_b=by_animal_month.get((b,month),{})
            qualifying={}
            for day in dates_a.keys() & dates_b.keys():
                if len(dates_a[day])<MIN_MATCHED_FIX_PAIRS_PER_DATE or len(dates_b[day])<MIN_MATCHED_FIX_PAIRS_PER_DATE:
                    continue
                n=paired_fix_count(dates_a[day],dates_b[day],tolerance)
                if n>=MIN_MATCHED_FIX_PAIRS_PER_DATE:
                    qualifying[day]=n
            if len(qualifying)>=MIN_SHARED_DATES_PER_MONTH:
                support[month]=qualifying
        if sum(month in support for month in WINTER)>=MIN_MONTHS_PER_SEASON and \
           sum(month in support for month in SUMMER)>=MIN_MONTHS_PER_SEASON:
            eligible[pair]=support
            all_positive_dates+=sum(len(dates) for dates in support.values())
            all_positive_fix_pairs+=sum(sum(n for n in dates.values()) for dates in support.values())
    animals={a for pair in eligible for a in pair}
    by_dyad_dates=[sum(len(days) for days in months.values()) for months in eligible.values()]
    return {'n_eligible_dyads':len(eligible),'n_eligible_animals':len(animals),
            'n_dyad_dates_with_at_least_three_matched_fixes':all_positive_dates,
            'total_greedy_one_to_one_fix_matches_on_qualifying_dyad_dates':all_positive_fix_pairs,
            'qualifying_dates_per_eligible_dyad':{'min':min(by_dyad_dates) if by_dyad_dates else None,
                'median':_quantile(by_dyad_dates,.5),'max':max(by_dyad_dates) if by_dyad_dates else None},
            'status':('TIME_OPPORTUNITY_SUFFICIENT_FOR_SEPARATE_SOURCE_ACCURACY_AND_POPULATION_AUDIT'
                       if len(eligible)>=MIN_READY_DYADS and len(animals)>=MIN_READY_ANIMALS
                       else 'STOP_SMALL_OPPORTUNITY_NOT_ZERO_ENCOUNTER'),
            '_eligible_pairs_private':set(eligible)}


def analyze(untimed,pinned,byday,source):
    centers=baseline.annual_day_balanced_centroids(untimed)
    output={'schema_version':1,'as_of':'2026-10-20',
      'source':source,'source_doi':baseline.SOURCES[source][1],
      'status':'TIMESTAMP_MATCHING_OPPORTUNITY_PREFLIGHT_ONLY',
      'complete_original_source_MD5_SHA256_and_QC_verified':True,
      'independent_source_timestamp_to_original_position_multiset_verified':True,
      'n_original_source_fixes':len(untimed),
      'source_clock_absolute_UTC_offset_verified':False,
      'original_population_membership_verified':False,
      'fix_pair_thresholds_seconds':list(GAPS_IN_SECONDS),
      'min_fix_pairs_per_qualifying_date':MIN_MATCHED_FIX_PAIRS_PER_DATE,
      'min_dates_per_qualifying_month':MIN_SHARED_DATES_PER_MONTH,
      'min_months_per_season':MIN_MONTHS_PER_SEASON,
      'future_gate_min_dyads':MIN_READY_DYADS,
      'future_gate_min_animals':MIN_READY_ANIMALS,
      'method':'greedy maximal one-to-one pairing of recorded source-native GPS timestamps within same animal-pair date, without spatial location test',
      'year_results':[],
      'limitations':['Time matching opportunity does not measure spatial nearness or encounters',
                     'Source timestamp absolute UTC/GPS clock basis unresolved',
                     'No verified local biological population label among candidate dyads',
                     'Fix intervals/detection precision may differ by source, season and animal',
                     'Original publication pool and source-years reuse animals, not independent species-population replications'] }
    for year in YEARS:
        original=timed._base_pair_set(untimed,year,centers)
        expected=[r['n_pairs'] for r in pinned['source']['comparisons']
                  if r['year']==year and r['window']=='winter_summer'
                  and r['risk_set_mode']=='near_centroid_25km' and
                  r['grid_km']==5 and r['origin_x_fraction']==r['origin_y_fraction']==0]
        if len(expected)!=1 or len(original)!=expected[0]:
            raise AssertionError('Frozen source-year 25-km pair baseline changed')
        yearly={'year':year,'n_original_geographic_dyads':len(original),
                'subhour_tolerance_results':[]}
        private=[]
        for gap in GAPS_IN_SECONDS:
            data=time_opportunity(byday,original,year,gap)
            private.append(data.pop('_eligible_pairs_private'))
            data['max_fix_time_gap_seconds']=gap
            data['fraction_original_dyads_eligible']=data['n_eligible_dyads']/len(original) if original else None
            yearly['subhour_tolerance_results'].append(data)
        if not private[0].issubset(private[1]):
            raise AssertionError('15-minute dyad opportunity is not a subset of 30-minute opportunity')
        output['year_results'].append(yearly)
        print(json.dumps({'source':source,'year':year,'original_geographic_dyads':len(original),
                          'eligible15':len(private[0]),'eligible30':len(private[1]),
                          'status15':yearly['subhour_tolerance_results'][0]['status'],
                          'status30':yearly['subhour_tolerance_results'][1]['status']},sort_keys=True),flush=True)
    return output


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',choices=SOURCES,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='movebank_subhour_original_') as tmp:
        folder=Path(tmp)
        timedrows,untimed,pinned=timed.get_original(args.source,folder)
        byday=original_native_second_fix_times(args.source,folder,untimed)
        result=analyze(untimed,pinned,byday,args.source)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'source':args.source,'n_fixes':result['n_original_source_fixes'],
                      'result_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'status':'AGGREGATE_TIMESTAMP_OPPORTUNITY_ONLY'},sort_keys=True))


if __name__=='__main__':
    main()
