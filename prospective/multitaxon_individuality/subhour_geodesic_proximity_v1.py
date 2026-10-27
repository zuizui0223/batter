#!/usr/bin/env python3
"""Checksum-pinned original-source GPS co-observed geodesic nearness versus pairing null.

POST-INSPECTION exploratory source-only measurement. One-to-one native GPS
timestamp matching <=15/30min, exactly 3 fix pairs/date, same 7 dates in 2
months per winter/summer, 12 deterministic samples and 0.5/1/2-km radii.
A GPS nearby-position indicator is NOT proof of direct physical animal
encounter, social association, dietary overlap, or common population.
Raw original animal IDs, dates, timestamps and positions never serialized.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import random
import statistics
import tempfile

import cross_source_seasonal_x_v2 as original
import same_clock_bin_couse_v1 as clock
import subhour_timestamp_opportunity_v1 as support

SOURCES=clock.SOURCES
YEARS=(2019,2020)
WINTER,SUMMER=(1,2,12),(6,7,8)
TIME_GAPS=(900,1800)
RADII_KM=(1.,.5,2.)
SEEDS=tuple(range(12))
N_MONTHS=2
N_DATES=7
N_PAIRS_PER_DAY=3
EXPECTED_PAIRS={
    'turkey':{2019:(112,112,112),2020:(21,21,21)},
    'black_bear':{2019:(1,0,0),2020:(104,38,47)},
    'white_tailed_deer':{2019:(55,55,55),2020:(205,205,205)},
}
EARTH_RADIUS_KM=6371.0


def _native_positions(source,folder,untimed):
    """Independent native-time source original scanner; exact QCd position equality."""
    uuid,_,taxon=original.SOURCES[source]
    _,entries=original._manifest(uuid)
    gps=[entry for entry in entries if entry['role']=='gps']
    refs=[entry for entry in entries if entry['role']=='reference']
    if not gps or len(refs)!=1:
        raise AssertionError('Source archive incomplete')
    paths={}
    for entry in gps+refs:
        file,_=original._download(entry,folder)
        paths[entry['uuid']]=(file,entry['filename'])
    allowed={(row.get('animal-id','').strip(),row.get('tag-id','').strip())
             for row in original._csv_rows(*paths[refs[0]['uuid']])}
    mapped={}
    for entry in gps:
        for row in original._csv_rows(*paths[entry['uuid']]):
            if (row.get('sensor-type') or '').strip().lower()!='gps':
                continue
            if (row.get('visible') or '').strip().lower() not in ('true','1'):
                continue
            if (row.get('individual-taxon-canonical-name') or '').strip()!=taxon:
                continue
            animal=(row.get('individual-local-identifier') or '').strip()
            tag=(row.get('tag-local-identifier') or '').strip()
            if (animal,tag) not in allowed:
                continue
            if any((row.get(field) or '').strip().lower() in ('true','1') for field in
                   ('manually-marked-outlier','algorithm-marked-outlier',
                    'automatically-marked-outlier')):
                continue
            try:
                t=datetime.fromisoformat(row['timestamp'].strip().replace('Z','+00:00'))
                lat,lon=float(row['location-lat']),float(row['location-long'])
                if not (math.isfinite(lat) and math.isfinite(lon) and
                        -90<=lat<=90 and -180<=lon<=180):
                    continue
            except (KeyError,ValueError,TypeError):
                continue
            if t.year not in YEARS:
                continue
            record=(animal,t.year,t.month,t.toordinal(),lat,lon)
            key=(animal,t)
            if key in mapped:
                if mapped[key]!=record:
                    mapped[key]=None
            else:
                mapped[key]=record
    clean={key:record for key,record in mapped.items() if record is not None}
    expected=Counter((r.animal,r.year,r.month,r.day,r.lat,r.lon) for r in untimed)
    if Counter(clean.values())!=expected or len(clean)!=len(untimed):
        raise AssertionError('Sub-hour timestamp-to-position original-source QC reconciliation failure')
    by_day=defaultdict(list)
    for (animal,t),record in clean.items():
        second=t.hour*3600+t.minute*60+t.second+t.microsecond/1e6
        by_day[(t.year,t.month,animal,t.toordinal())].append((second,record[4],record[5]))
    return {key:tuple(sorted(value)) for key,value in by_day.items()}


def one_to_one_time_pairs(left,right,tolerance_seconds):
    """Return actual matched original positions; no reuse of source fixes."""
    i=j=0
    paired=[]
    while i<len(left) and j<len(right):
        d=left[i][0]-right[j][0]
        if abs(d)<=tolerance_seconds+1e-9:
            paired.append((left[i],right[j]))
            i+=1;j+=1
        elif d<0:
            i+=1
        else:
            j+=1
    return tuple(paired)


def _derive_opportunity(byday,base_pairs,year,tolerance):
    """Eligibility from original time records only; no spatial nearness score."""
    months_index=defaultdict(dict)
    for (y,m,a,day),seq in byday.items():
        if y==year and m in WINTER+SUMMER:
            months_index[(a,m)][day]=seq
    qualified={}
    for pair in sorted(base_pairs):
        a,b=pair
        monthly={}
        for month in WINTER+SUMMER:
            first=months_index.get((a,month),{})
            second=months_index.get((b,month),{})
            days={}
            for date in first.keys() & second.keys():
                if len(first[date])<N_PAIRS_PER_DAY or len(second[date])<N_PAIRS_PER_DAY:
                    continue
                pairs=one_to_one_time_pairs(first[date],second[date],tolerance)
                if len(pairs)>=N_PAIRS_PER_DAY:
                    days[date]=pairs
            if len(days)>=N_DATES:
                monthly[month]=days
        if (sum(m in monthly for m in WINTER)>=N_MONTHS and
                sum(m in monthly for m in SUMMER)>=N_MONTHS):
            qualified[pair]=monthly
    return qualified


def _seed(*values):
    return int.from_bytes(hashlib.sha256('\x1f'.join(map(str,values)).encode()).digest()[:16],'big')


def _select(seq,n,*keys):
    if len(seq)<n:
        raise AssertionError('Missing frozen temporal observation support')
    return tuple(sorted(random.Random(_seed(*keys)).sample(sorted(seq),n)))


def haversine_km(a,b):
    """Input positional records are (source_day_second, latitude, longitude)."""
    lat1,lat2=math.radians(a[1]),math.radians(b[1])
    dlat=lat2-lat1
    dlon=math.radians(b[2]-a[2])
    z=math.sin(dlat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*EARTH_RADIUS_KM*math.asin(min(1.,math.sqrt(max(0.,z))))


def daily_nearby_statistics(matched_three):
    """Observed 3 paired distances and exact 3x3 assignment reference, per radius."""
    if len(matched_three)!=N_PAIRS_PER_DAY:
        raise AssertionError('Exactly 3 time-aligned GPS pairs per selected date required')
    a=[row[0] for row in matched_three]
    b=[row[1] for row in matched_three]
    gaps=[abs(x[0]-y[0]) for x,y in matched_three]
    distances=[[haversine_km(x,y) for y in b] for x in a]
    result={}
    for radius in RADII_KM:
        observed=sum(distances[i][i]<=radius for i in range(3))/3
        reference=sum(distances[i][j]<=radius for i in range(3) for j in range(3))/9
        result[radius]={'O':observed,'N':reference,'D':observed-reference}
    return result,statistics.fmean(gaps)


def _mean(values):
    return statistics.fmean(values)


def _one_seed(qualified,source,year,tolerance,seed):
    values={rad:{'winter':defaultdict(list),'summer':defaultdict(list)}
            for rad in RADII_KM}
    gap_values={'winter':[], 'summer':[]}
    for pair,monthly in sorted(qualified.items()):
        for season,months in (('winter',WINTER),('summer',SUMMER)):
            selected_months=_select([m for m in months if m in monthly],N_MONTHS,
                                    'MONTH',source,year,tolerance,seed,pair,season)
            per_radius={rad:[] for rad in RADII_KM}
            per_month_gaps=[]
            for month in selected_months:
                dates=_select(list(monthly[month]),N_DATES,
                              'DAY',source,year,tolerance,seed,pair,season,month)
                per_date={rad:[] for rad in RADII_KM}
                daily_gaps=[]
                for date in dates:
                    matchset=monthly[month][date]
                    selected=_select(matchset,N_PAIRS_PER_DAY,
                                     'FIX',source,year,tolerance,seed,pair,season,month,date)
                    daily,gap=daily_nearby_statistics(selected)
                    if any(abs(selected_fix[0][0]-selected_fix[1][0])>tolerance+1e-9
                           for selected_fix in selected):
                        raise AssertionError('Pair matches exceed frozen source timestamp tolerance')
                    daily_gaps.append(gap)
                    for radius in RADII_KM:
                        per_date[radius].append(daily[radius])
                per_month_gaps.append(_mean(daily_gaps))
                for radius in RADII_KM:
                    per_radius[radius].append({k:_mean(d[k] for d in per_date[radius])
                                                for k in ('O','N','D')})
            gap_values[season].append(_mean(per_month_gaps))
            for radius in RADII_KM:
                for k in ('O','N','D'):
                    values[radius][season][k].append(
                        _mean(m[k] for m in per_radius[radius]))
    out=[]
    ndyads=len(qualified)
    for radius in RADII_KM:
        v=values[radius]
        winter={k:_mean(v['winter'][k]) for k in ('O','N','D')}
        summer={k:_mean(v['summer'][k]) for k in ('O','N','D')}
        for val in (winter,summer):
            if not (0<=val['O']<=1 and 0<=val['N']<=1 and
                    abs(val['O']-val['N']-val['D'])<1e-12):
                raise AssertionError('Observed minus exact matching reference did not reconcile')
        out.append({
            'source_year':year,'timestamp_tolerance_seconds':tolerance,
            'radius_km':radius,'seed':seed,
            'n_matched_dyads':ndyads,
            'n_selected_dyad_dates':ndyads*N_MONTHS*N_DATES*2,
            'n_selected_direct_fix_pairs':ndyads*N_MONTHS*N_DATES*2*N_PAIRS_PER_DAY,
            'winter':winter,'summer':summer,
            'winter_minus_summer':{k:winter[k]-summer[k] for k in ('O','N','D')},
            'winter_mean_abs_recording_gap_seconds':_mean(gap_values['winter']),
            'summer_mean_abs_recording_gap_seconds':_mean(gap_values['summer']),
            'winter_positive_D_dyad_fraction':sum(x>1e-12 for x in v['winter']['D'])/ndyads,
            'summer_positive_D_dyad_fraction':sum(x>1e-12 for x in v['summer']['D'])/ndyads})
    return out


def analyze(source,byday,untimed,pinned):
    centers=original.annual_day_balanced_centroids(untimed)
    output={'schema_version':1,'as_of':'2026-10-20','source':source,
            'source_doi':original.SOURCES[source][1],
            'status':'POST_INSPECTION_SOURCE_GPS_TIME_MATCHED_GEODESIC_NEARBY_ONLY',
            'complete_original_MD5_SHA256_replay_verified':True,
            'independent_original_native_timestamp_to_position_QC_verified':True,
            'native_clock_absolute_UTC_offset_verified':False,
            'source_specific_population_membership_verified':False,
            'GPS_location_error_quantified':False,
            'n_original_fixes':len(untimed),
            'timestamp_tolerances_seconds':list(TIME_GAPS),
            'geodesic_radii_km':list(RADII_KM),
            'n_seeds':len(SEEDS),'year_results':[],
            'limitations':['Subhour positional nearness is observational GPS proxy, NOT verified animal encounter or social relationship',
                           'Original source native clock basis, fix error and local ecological populations unresolved',
                           'A fixed-date matching-permutation expectation is descriptive and breaks real movement autocorrelation',
                           'Years, dyads and sampling seeds are dependent; no biological p-values or independent source populations',
                           'Black bear 2019 source has too few time-qualified dyads and is STOP, not zero encounter']}
    for year in YEARS:
        fixed=clock._base_pair_set(untimed,year,centers)
        want=EXPECTED_PAIRS[source][year]
        if len(fixed)!=want[0]:
            raise AssertionError('Original source-year geographic risk set changed')
        yearly={'year':year,'n_original_source_geographic_dyads':len(fixed),
                'time_tolerance_results':[]}
        for tol,expected in zip(TIME_GAPS,want[1:]):
            selected=_derive_opportunity(byday,fixed,year,tol)
            if len(selected)!=expected:
                raise AssertionError('Actual subhour matched-fix risk set differs from pre-outcome source-timestamp screen')
            n_animals=len({animal for pair in selected for animal in pair})
            status=('DESCRIPTIVE_NEAR_SYNCHRONOUS_GPS_NEARBY_PROXY'
                    if len(selected)>=8 and n_animals>=3
                    else 'STOP_SMALL_TIMESTAMP_MATCHED_OPPORTUNITY')
            r={'max_abs_timestamp_gap_seconds':tol,'status':status,
               'n_clock_matched_dyads':len(selected),'n_animal_ids_aggregated':n_animals,
               'grid_free_geodesic_seed_results':[]}
            if status.startswith('DESCRIPTIVE_'):
                for seed in SEEDS:
                    r['grid_free_geodesic_seed_results'].extend(
                        _one_seed(selected,source,year,tol,seed))
                if len(r['grid_free_geodesic_seed_results'])!=len(RADII_KM)*len(SEEDS):
                    raise AssertionError('Missing declared continuous-distance sensitivity scenarios')
            yearly['time_tolerance_results'].append(r)
            print(json.dumps({'source':source,'year':year,'max_gap_seconds':tol,
                              'reference_dyads':want[0],'time_supported_dyads':len(selected),
                              'geodesic_scenarios':len(r['grid_free_geodesic_seed_results']),
                              'status':status},sort_keys=True),flush=True)
        output['year_results'].append(yearly)
    return output


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',choices=SOURCES,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='movebank_geodesic_original_') as temporary:
        folder=Path(temporary)
        clock_fix,untimed,pinned=clock.get_original(args.source,folder)
        byday=_native_positions(args.source,folder,untimed)
        out=analyze(args.source,byday,untimed,pinned)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'source':args.source,'fixes':out['n_original_fixes'],
                      'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'status':'VALID_SOURCE_AGGREGATES_ONLY'},sort_keys=True))


if __name__=='__main__':
    main()
