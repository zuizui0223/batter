#!/usr/bin/env python3
"""Original-source coarse co-timed geographic occupancy: X, T6/T3 and exact label null.

Exploratory 20 October 2026 post-inspection design, NOT a biological encounter
test. All source animal IDs, coordinates and exact dates stay in temporary RAM.
Writes only source-year/season aggregate summaries. Original GPS/reference files
are verified against publisher MD5 AND previously pinned SHA256/source QC.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import random
import statistics
import tempfile
import zipfile

import cross_source_seasonal_x_v2 as old

ARCHIVE = 'CROSS_SOURCE_NEARBY_DYAD_V2_FULL_AGGREGATES_2026_10_20.zip'
ARCHIVE_SHA256 = '857e4157606ca1a4bf87d2f7e76fa379ab7bbf77c2bfc491ffec8196f543ee48'
SOURCES = ('turkey', 'black_bear', 'white_tailed_deer')
YEARS = (2019, 2020)
WINTER, SUMMER = (1, 2, 12), (6, 7, 8)
HOUR_WIDTHS = (6, 3)
GRIDS = ((5., 0., 0.), (1., 0., 0.), (10., 0., 0.), (5., .5, .5))
SEEDS = tuple(range(12))
MIN_DATES = 7
MONTHS_PER_SEASON = 2
MIN_SHARED_BINS = 2
MAX_CENTROID_KM = 25.


@dataclass(frozen=True, slots=True, repr=False)
class TimedFix:
    animal: str
    year: int
    month: int
    day: int
    lat: float
    lon: float
    hour: int


def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()


def _seed(*parts):
    b='\x1f'.join(str(x) for x in parts).encode()
    return int.from_bytes(hashlib.sha256(b).digest()[:16], 'big')


def _choice(items,count,*parts):
    if count > len(items):
        raise AssertionError('Insufficient original observation support')
    return tuple(sorted(random.Random(_seed(*parts)).sample(sorted(items),count)))


def decode_source_time(gps_files,reference_file,taxon,untimed):
    """Independent timestamp QC; must reproduce exact old accepted position multiset."""
    refs={(r.get('animal-id','').strip(),r.get('tag-id','').strip())
          for r in old._csv_rows(*reference_file)}
    if not refs:
        raise AssertionError('No original reference animal/tag joins')
    mapped={}
    for path,filename in gps_files:
        for r in old._csv_rows(path,filename):
            if (r.get('sensor-type') or '').strip().lower()!='gps':
                continue
            if (r.get('visible') or '').strip().lower() not in ('true','1'):
                continue
            if (r.get('individual-taxon-canonical-name') or '').strip()!=taxon:
                continue
            animal=(r.get('individual-local-identifier') or '').strip()
            tag=(r.get('tag-local-identifier') or '').strip()
            if (animal,tag) not in refs:
                continue
            if any((r.get(col) or '').strip().lower() in ('1','true')
                   for col in ('manually-marked-outlier','algorithm-marked-outlier',
                               'automatically-marked-outlier')):
                continue
            try:
                t=datetime.fromisoformat(r['timestamp'].strip().replace('Z','+00:00'))
                lat,lon=float(r['location-lat']),float(r['location-long'])
                if not math.isfinite(lat) or not math.isfinite(lon) or not (-90<=lat<=90 and -180<=lon<=180):
                    continue
            except (ValueError,KeyError,TypeError):
                continue
            if t.year not in YEARS:
                continue
            fix=TimedFix(animal,t.year,t.month,t.toordinal(),lat,lon,t.hour)
            key=(animal,t)
            if key in mapped and mapped[key]!=fix:
                mapped[key]=None
            elif key not in mapped:
                mapped[key]=fix
    timed=[v for v in mapped.values() if v is not None]
    source_signature=Counter((x.animal,x.year,x.month,x.day,x.lat,x.lon) for x in untimed)
    clock_signature=Counter((x.animal,x.year,x.month,x.day,x.lat,x.lon) for x in timed)
    if source_signature != clock_signature or len(timed)!=len(untimed):
        raise AssertionError('Source timestamp/QC join differs from original GPS position stream')
    return timed


def _archive_source(source):
    path=Path(__file__).resolve().with_name(ARCHIVE)
    if sha256_file(path)!=ARCHIVE_SHA256:
        raise AssertionError('Pinned full-source aggregate ZIP SHA256 differs')
    with zipfile.ZipFile(path) as z:
        payload=json.loads(z.read(source+'.json'))
    if payload['source']['status']!='COMPLETE_EXPLORATORY_GEOGRAPHIC_X':
        raise AssertionError('Original source not eligible in pinned archive')
    return payload


def get_original(source,folder):
    pinned=_archive_source(source)
    uuid,doi,taxon=old.SOURCES[source]
    _, entries=old._manifest(uuid)
    gps=[e for e in entries if e['role']=='gps']
    refs=[e for e in entries if e['role']=='reference']
    if not gps or len(refs)!=1 or sum(e['size'] for e in gps)>old.MAX_ARCHIVE_BYTES:
        raise AssertionError('Original source GPS/reference incomplete or exceeds bounded budget')
    paths={}
    recorded=pinned['source']['file_receipts']
    for entry in gps+refs:
        path,receipt=old._download(entry,folder)
        matches=[x for x in recorded if x['role']==entry['role'] and
                 x['sha256']==receipt['sha256'] and
                 x['source_md5']==receipt['source_md5'] and
                 x['bytes']==receipt['bytes']]
        if len(matches)!=1 or not receipt['md5_verified']:
            raise AssertionError('Original publisher MD5/pinned SHA256 mismatch')
        paths[entry['uuid']]=(path,entry['filename'])
    gf=[paths[e['uuid']] for e in gps]
    rf=paths[refs[0]['uuid']]
    untimed,qc,labels=old.read_originals(gf,rf,taxon)
    if qc!=pinned['source']['event_audit']:
        raise AssertionError('Replayed source QC diverges from original source archive')
    if labels:
        raise AssertionError('Previously unavailable reference group metadata changed')
    timed=decode_source_time(gf,rf,taxon,untimed)
    return timed,untimed,pinned


def _events_by_bin(timed,width):
    by=defaultdict(list)
    for r in timed:
        by[(r.year,r.month,r.animal,r.day,r.hour//width)].append((r.lat,r.lon))
    return {key:tuple(sorted(coords)) for key,coords in by.items()}


def _base_pair_set(untimed,year,centers):
    """Independent geometry+date support, must agree with the V2 frozen risk set."""
    dates=defaultdict(set)
    animals=set()
    for f in untimed:
        if f.year==year:
            dates[(f.animal,f.month)].add(f.day)
            animals.add(f.animal)
    pairs=set()
    for a,b in combinations(sorted(animals),2):
        if a not in centers[year] or b not in centers[year]:
            continue
        if old.centroid_distance_km(centers[year][a],centers[year][b])>MAX_CENTROID_KM:
            continue
        def has(month):
            return len(dates[(a,month)] & dates[(b,month)])>=MIN_DATES
        if sum(has(m) for m in WINTER)>=MONTHS_PER_SEASON and sum(has(m) for m in SUMMER)>=MONTHS_PER_SEASON:
            pairs.add((a,b))
    return pairs


def time_supported_pairs(original_pairs,timed,width,year):
    """A qualifying date has >=2 actual common source-clock bins, not imputed."""
    by=_events_by_bin(timed,width)
    days=defaultdict(lambda:defaultdict(set))
    # [animal,month,day] -> set of observed time bins
    for (y,month,animal,day,binid) in by:
        if y==year and month in WINTER+SUMMER:
            days[(animal,month)][day].add(binid)
    supported={}
    for a,b in sorted(original_pairs):
        monthly={}
        for month in WINTER+SUMMER:
            shared=set(days[(a,month)]) & set(days[(b,month)])
            available={}
            for day in shared:
                common=days[(a,month)][day] & days[(b,month)][day]
                if len(common)>=MIN_SHARED_BINS:
                    available[day]=tuple(sorted(common))
            if len(available)>=MIN_DATES:
                monthly[month]=available
        if (sum(m in monthly for m in WINTER)>=MONTHS_PER_SEASON and
                sum(m in monthly for m in SUMMER)>=MONTHS_PER_SEASON):
            supported[(a,b)]=monthly
    return by,supported


def _cell(lat,lon,grid,coslat):
    km,ox,oy=grid
    return (math.floor(lon*111.32*coslat/km+ox),
            math.floor(lat*111.32/km+oy))


def day_statistics(first,second):
    """One independently sampled original fix per animal/common clock bin."""
    m=len(first)
    if m!=len(second) or m<MIN_SHARED_BINS:
        raise AssertionError('Must have two or more pair-shared clock bins')
    a,b=Counter(first),Counter(second)
    overlap=sum(min(count,b.get(cell,0)) for cell,count in a.items())/m
    coincident=sum(x==y for x,y in zip(first,second))/m
    expectation=sum(count*b.get(cell,0) for cell,count in a.items())/(m*m)
    if not (0<=coincident<=overlap+1e-12 and 0<=expectation<=overlap+1e-12 and overlap<=1+1e-12):
        raise AssertionError('Co-time cell matching exceeds all-time within-day intersection')
    return overlap,coincident,expectation,coincident-expectation


def _mean(values):
    return statistics.fmean(values)


def evaluate_seed(by,supported,source,year,width,seed,lat_cos):
    """One complete sample selection, shared across all declared spatial grids."""
    if not supported:
        return []
    cache={}
    storage={g:{'winter':defaultdict(list),'summer':defaultdict(list)} for g in GRIDS}
    binsizes=[]
    n_days=0
    for (a,b),months in supported.items():
        pair=(a,b)
        for label,season_months in (('winter',WINTER),('summer',SUMMER)):
            chosen=_choice([m for m in season_months if m in months],MONTHS_PER_SEASON,
                           'MONTH',source,year,width,seed,label,a,b)
            local={g:[] for g in GRIDS}
            for month in chosen:
                dates=_choice(list(months[month]),MIN_DATES,
                              'DATE',source,year,width,seed,label,a,b,month)
                per_grid={g:[] for g in GRIDS}
                for day in dates:
                    bins=months[month][day]
                    binsizes.append(len(bins))
                    n_days+=1
                    left,right=[],[]
                    for animal,dest in ((a,left),(b,right)):
                        for clock in bins:
                            key=(year,month,animal,day,clock,width,seed)
                            if key not in cache:
                                opts=by[(year,month,animal,day,clock)]
                                cache[key]=_choice(opts,1,'FIX',source,year,width,seed,animal,month,day,clock)[0]
                            dest.append(cache[key])
                    for grid in GRIDS:
                        pos_a=[_cell(lat,lon,grid,lat_cos) for lat,lon in left]
                        pos_b=[_cell(lat,lon,grid,lat_cos) for lat,lon in right]
                        per_grid[grid].append(day_statistics(pos_a,pos_b))
                for grid in GRIDS:
                    local[grid].append(tuple(_mean(s[i] for s in per_grid[grid]) for i in range(4)))
            for grid in GRIDS:
                season_average=tuple(_mean(s[i] for s in local[grid]) for i in range(4))
                for i,name in enumerate(('X','T','N','D')):
                    storage[grid][label][name].append(season_average[i])
    output=[]
    n=len(supported)
    assert n_days==n*MONTHS_PER_SEASON*MIN_DATES*2
    for grid in GRIDS:
        s=storage[grid]
        winter={k:_mean(values) for k,values in s['winter'].items()}
        summer={k:_mean(values) for k,values in s['summer'].items()}
        if any(not (0<=z['T']<=z['X']+1e-10 and 0<=z['N']<=z['X']+1e-10 and
                    abs(z['D']-(z['T']-z['N']))<1e-10) for z in (winter,summer)):
            raise AssertionError('Season component bounds or identity violated')
        out={'source_year':year,'clock_bin_hours':width,'seed':seed,
             'grid_km':grid[0],'origin_x_fraction':grid[1],'origin_y_fraction':grid[2],
             'n_supported_dyads':n,'n_pair_dates':n_days,
             'mean_shared_clock_bins_per_pair_date':_mean(binsizes),
             'winter':winter,'summer':summer,
             'winter_minus_summer':{k:winter[k]-summer[k] for k in ('X','T','N','D')},
             'winter_positive_D_dyad_fraction':sum(x>1e-12 for x in s['winter']['D'])/n,
             'summer_positive_D_dyad_fraction':sum(x>1e-12 for x in s['summer']['D'])/n}
        output.append(out)
    return output


def analyze(timed,untimed,pinned,source):
    centers=old.annual_day_balanced_centroids(untimed)
    lat_cos=math.cos(math.radians(math.fsum(x.lat for x in untimed)/len(untimed)))
    source_rows=pinned['source']['comparisons']
    output={'schema_version':1,'as_of':'2026-10-20',
            'status':'POST_INSPECTION_COARSE_CLOCK_BIN_COUSE_EXPLORATORY',
            'source':source,'source_doi':old.SOURCES[source][1],
            'original_source_full_MD5_SHA256_verified':True,
            'original_position_and_timestamp_multisets_exact':True,
            'reference_population_label_verified':False,
            'source_clock_offset_UTC_verified':False,
            'n_valid_original_GPS_fixes':len(untimed),
            'hour_bin_widths':list(HOUR_WIDTHS),'grids':[list(x) for x in GRIDS],
            'n_seeds':len(SEEDS),'results':[],
            'limitations':['T means same geographic grid cell in same source-clock 6h/3h bin on a date, NOT true synchronous animal encounter',
                           'Within-day shuffled clock-bin reference is a descriptive expectation, not an exchangeable biological null or p-value',
                           'Tracks from multiple years and pairwise dyads are dependent',
                           'Annual centroid proximity cannot prove local social/ecological population identity',
                           'Post-inspection exploratory comparison; original-source GPS detection process/clock offset unresolved']}
    for year in YEARS:
        original=_base_pair_set(untimed,year,centers)
        expected=[r['n_pairs'] for r in source_rows
                  if r['year']==year and r['window']=='winter_summer' and
                     r['risk_set_mode']=='near_centroid_25km' and
                     r['grid_km']==5 and r['origin_x_fraction']==r['origin_y_fraction']==0]
        if len(expected)!=1 or len(original)!=expected[0]:
            raise AssertionError('Source risk-set precondition disagrees with frozen V2')
        for width in HOUR_WIDTHS:
            by,eligible=time_supported_pairs(original,timed,width,year)
            row={'year':year,'clock_bin_hours':width,
                 'n_original_geographic_support_dyads':len(original),
                 'n_joint_clock_support_dyads':len(eligible),
                 'fraction_geographic_dyads_with_clock_support':len(eligible)/len(original) if original else None,
                 'status':'DESCRIPTIVE_COMMON_CLOCK_CONDITIONAL' if len(eligible)>=2 else 'NOT_ESTIMABLE_FEWER_THAN_TWO_CLOCK_SUPPORTED_DYADS',
                 'grid_seed_aggregates':[]}
            if len(eligible)>=2:
                for seed in SEEDS:
                    row['grid_seed_aggregates'].extend(
                        evaluate_seed(by,eligible,source,year,width,seed,lat_cos))
                if len(row['grid_seed_aggregates'])!=len(SEEDS)*len(GRIDS):
                    raise AssertionError('Incomplete declared clock/grid/seed tests')
            output['results'].append(row)
            print(json.dumps({'source':source,'year':year,'clockbin_h':width,
                               'original_dyads':len(original),'joint_clock_dyads':len(eligible),
                               'scenarios':len(row['grid_seed_aggregates']),
                               'status':row['status']}),flush=True)
    return output


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',choices=SOURCES,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    archive=_archive_source(args.source)
    with tempfile.TemporaryDirectory(prefix='movebank_timed_original_') as folder:
        timed,untimed,pinned=get_original(args.source,Path(folder))
        result=analyze(timed,untimed,pinned,args.source)
    out=args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'source':args.source,'status':result['status'],
                      'n_original_fixes':result['n_valid_original_GPS_fixes'],
                      'n_valid_clock_years':sum(r['status'].startswith('DESCRIPTIVE_') for r in result['results']),
                      'aggregate_sha256':sha256_file(out)},sort_keys=True))


if __name__=='__main__':
    main()
