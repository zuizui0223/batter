#!/usr/bin/env python3
"""Independent source-receipt, opportunity and geodesic proximity aggregate audit.

Only aggregate JSON. This verifier never opens individual GPS source tracks.
Checks exact original-GPS aggregate SHA256 receipts, common source-year
denominators, time-matched fix opportunity, all 360 source-year/tolerance/
radius/seed response rows, monotone observed/reference proximity in radius,
and daily/per-year exact O-N=D algebra. No biological p-value is implied.
"""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

RECEIPTS={
'turkey':{'fixes':435214,'doi':'10.5441/001/1.671','original':{2019:112,2020:21},
  'opportunity_hash':'eee1fadcffdbcbca0a15f6698244abd5088a3d6626816c025ae8681448951b62',
  'geodesic_hash':'13008932046ad79cdde16e3cbd8b7aacb253668953ac2de34580abc71c99d938',
  'time_pairs':{2019:(112,112),2020:(21,21)}},
'black_bear':{'fixes':148394,'doi':'10.5441/001/1.706','original':{2019:1,2020:104},
  'opportunity_hash':'abeb50d7cfcb6e08509e668156ce0862498428040da9439d21d4dd0c065a1b32',
  'geodesic_hash':'867c9941b472a0781708e71c084ff595cd62f3c78c9d2d404ee48d4d63dd7bc7',
  'time_pairs':{2019:(0,0),2020:(38,47)}},
'white_tailed_deer':{'fixes':371080,'doi':'10.5441/001/1.718','original':{2019:55,2020:205},
  'opportunity_hash':'e64d753c0b632ba5d053555b3588e8276bd0821f6535da1d265a16f3768641a0',
  'geodesic_hash':'919d0786370d0b298d904d13510571e7dfb67c0ffdd6bc32b54bdaddc847bae6',
  'time_pairs':{2019:(55,55),2020:(205,205)}},
}
TIME_TOLS=(900,1800)
RADII=(1.0,.5,2.0)
SEEDS=range(12)
EPS=1e-10


def near(a,b):
    return math.isclose(a,b,abs_tol=EPS,rel_tol=1e-10)


def signed(values):
    c=Counter(1 if value>1e-12 else -1 if value< -1e-12 else 0 for value in values)
    return {'positive':c[1],'negative':c[-1],'near_zero':c[0]}


def _find_file(directory,source,kind):
    dir=Path(directory)
    paths=[dir/(source+('_subhour_opportunity.json' if kind=='opportunity' else '_subhour_geodesic.json')),
           dir/(('SUBHOUR_TIMESTAMP_OPPORTUNITY_' if kind=='opportunity' else 'SUBHOUR_GEODESIC_')+
                source.upper()+'_2026_10_20.json')]
    matches=[x for x in paths if x.exists()]
    if not matches:
        raise AssertionError('Missing source aggregate JSON in staging or published directory')
    if len(matches)==2 and matches[0].read_bytes()!=matches[1].read_bytes():
        raise AssertionError('Temporary source and published aggregate files differ')
    return matches[-1]


def _verified_load(source,kind,folder):
    path=_find_file(folder,source,kind)
    data=path.read_bytes()
    expected=RECEIPTS[source][kind+'_hash']
    if hashlib.sha256(data).hexdigest()!=expected:
        raise AssertionError('Original-GPS aggregate SHA256 receipt changed')
    return json.loads(data)


def _verify_opportunity(source,obj):
    expected=RECEIPTS[source]
    if obj['source']!=source or obj['source_doi']!=expected['doi'] or obj['n_original_source_fixes']!=expected['fixes']:
        raise AssertionError('Original-source provenance differs')
    if obj['fix_pair_thresholds_seconds']!=[900,1800] or obj['min_fix_pairs_per_qualifying_date']!=3 or obj['min_dates_per_qualifying_month']!=7 or obj['min_months_per_season']!=2:
        raise AssertionError('Frozen sub-hour observation gate has been changed')
    if not (obj['complete_original_source_MD5_SHA256_and_QC_verified'] and
            obj['independent_source_timestamp_to_original_position_multiset_verified']):
        raise AssertionError('Source full MD5/SHA256 or event multiset not confirmed')
    if obj['original_population_membership_verified'] or obj['source_clock_absolute_UTC_offset_verified']:
        raise AssertionError('Unvalidated biological population or clock inferred')
    rows={row['year']:row for row in obj['year_results']}
    if set(rows)!={2019,2020}:
        raise AssertionError('Source years missing')
    for year,row in rows.items():
        if row['n_original_geographic_dyads']!=expected['original'][year]:
            raise AssertionError('Original fixed geography risk set changed')
        if {v['max_fix_time_gap_seconds'] for v in row['subhour_tolerance_results']}!=set(TIME_TOLS):
            raise AssertionError('Sub-hour time thresholds missing')
        for tol,r in zip(TIME_TOLS,row['subhour_tolerance_results']):
            n=expected['time_pairs'][year][TIME_TOLS.index(tol)]
            if r['max_fix_time_gap_seconds']!=tol or r['n_eligible_dyads']!=n:
                raise AssertionError('Original source timestamp opportunity support changed')
            if not near(r['fraction_original_dyads_eligible'],
                        n/expected['original'][year]):
                raise AssertionError('Timestamp support fraction inconsistent')
            status=('TIME_OPPORTUNITY_SUFFICIENT_FOR_SEPARATE_SOURCE_ACCURACY_AND_POPULATION_AUDIT'
                    if n>=8 else 'STOP_SMALL_OPPORTUNITY_NOT_ZERO_ENCOUNTER')
            if r['status']!=status:
                raise AssertionError('Source readiness/STOP status inconsistent')
    return rows


def _verify_geodesic(source,obj,opportunity):
    expected=RECEIPTS[source]
    if obj['source']!=source or obj['source_doi']!=expected['doi'] or obj['n_original_fixes']!=expected['fixes']:
        raise AssertionError('Geodesic archive source metadata differs')
    if obj['timestamp_tolerances_seconds']!=[900,1800] or obj['geodesic_radii_km']!=[1.,.5,2.] or obj['n_seeds']!=12:
        raise AssertionError('Geodesic time/distance sampling constants changed')
    if not obj['complete_original_MD5_SHA256_replay_verified'] or not obj['independent_original_native_timestamp_to_position_QC_verified']:
        raise AssertionError('Original source receipt/time-position multiset not verified')
    if obj['native_clock_absolute_UTC_offset_verified'] or obj['source_specific_population_membership_verified'] or obj['GPS_location_error_quantified']:
        raise AssertionError('Unverified encounter/population/position-error inference')
    rows={x['year']:x for x in obj['year_results']}
    if set(rows)!={2019,2020}:
        raise AssertionError('Original source-year groups missing')
    out=[]
    scenario_count=0
    for year,row in sorted(rows.items()):
        old_n=expected['original'][year]
        if row['n_original_source_geographic_dyads']!=old_n:
            raise AssertionError('Source pair baseline changed')
        timegroups={r['max_abs_timestamp_gap_seconds']:r for r in row['time_tolerance_results']}
        if set(timegroups)!=set(TIME_TOLS):
            raise AssertionError('Incomplete near-time source settings')
        for tol,r in sorted(timegroups.items()):
            n=expected['time_pairs'][year][TIME_TOLS.index(tol)]
            if r['n_clock_matched_dyads']!=n or n!=next(x for x in opportunity[year]['subhour_tolerance_results'] if x['max_fix_time_gap_seconds']==tol)['n_eligible_dyads']:
                raise AssertionError('Unexpected actual original timestamp/gps paired eligibility')
            expected_status='DESCRIPTIVE_NEAR_SYNCHRONOUS_GPS_NEARBY_PROXY' if n>=8 else 'STOP_SMALL_TIMESTAMP_MATCHED_OPPORTUNITY'
            if r['status']!=expected_status:
                raise AssertionError('Geodesic source STOP status wrong')
            if n<8:
                if r['grid_free_geodesic_seed_results']:
                    raise AssertionError('Unsupported source-year encoded as nearness zero')
                out.append({'source':source,'year':year,'tolerance_seconds':tol,'status':expected_status,
                            'n_original_dyads':old_n,'n_time_supported_dyads':n})
                continue
            values=r['grid_free_geodesic_seed_results']
            if len(values)!=36:
                raise AssertionError('Missing 12-seed by 3-radius original-source rows')
            indexed={(x['radius_km'],x['seed']):x for x in values}
            if set(indexed)!={(radius,seed) for radius in RADII for seed in SEEDS}:
                raise AssertionError('Missing/duplicated radius-by-seed scenario')
            scenario_count+=36
            for seed in SEEDS:
                shared_gaps=None
                lastO=lastN=-1.
                for radius in sorted(RADII):
                    v=indexed[(radius,seed)]
                    required={'source_year','timestamp_tolerance_seconds','radius_km','seed',
                              'n_matched_dyads','n_selected_dyad_dates','n_selected_direct_fix_pairs',
                              'winter','summer','winter_minus_summer',
                              'winter_mean_abs_recording_gap_seconds','summer_mean_abs_recording_gap_seconds',
                              'winter_positive_D_dyad_fraction','summer_positive_D_dyad_fraction'}
                    if set(v)!=required:
                        raise AssertionError('Unexpected source output fields: possible animal data')
                    if v['source_year']!=year or v['timestamp_tolerance_seconds']!=tol or v['n_matched_dyads']!=n:
                        raise AssertionError('Inconsistent source cohort across radii')
                    if v['n_selected_dyad_dates']!=n*28 or v['n_selected_direct_fix_pairs']!=n*84:
                        raise AssertionError('A dyad/date/fix included under wrong source support')
                    gaps=(v['winter_mean_abs_recording_gap_seconds'],v['summer_mean_abs_recording_gap_seconds'])
                    if any(not 0<=g<=tol+EPS for g in gaps):
                        raise AssertionError('Matched source time gap exceeds specified cutoff')
                    if shared_gaps is not None and gaps!=shared_gaps:
                        raise AssertionError('Changing radius changed source matched GPS timestamps')
                    shared_gaps=gaps
                    for name in ('winter','summer'):
                        m=v[name]
                        if set(m)!={'O','N','D'}:
                            raise AssertionError('Unexpected geodesic component')
                        if not all(isinstance(m[key],(int,float)) and math.isfinite(m[key]) for key in ('O','N','D')):
                            raise AssertionError('Invalid source proximity score')
                        if not (0<=m['O']<=1 and 0<=m['N']<=1 and near(m['D'],m['O']-m['N'])):
                            raise AssertionError('Source O−N=D and bounds violated')
                    if set(v['winter_minus_summer'])!={'O','N','D'}:
                        raise AssertionError('Unexpected contrast fields')
                    for k in ('O','N','D'):
                        if not near(v['winter_minus_summer'][k],v['winter'][k]-v['summer'][k]):
                            raise AssertionError('Season contrast does not reconcile')
                    if any(not 0<=v[k]<=1 for k in ('winter_positive_D_dyad_fraction','summer_positive_D_dyad_fraction')):
                        raise AssertionError('Invalid within-cohort positive-D fraction')
                    # Geodesic-nearness probabilities must rise with radius.
                    # Their residual differences need not be monotone.
                    if v['winter']['O']+EPS<lastO or v['winter']['N']+EPS<lastN:
                        raise AssertionError('Position sample changed when distance radius changed')
                    lastO,lastN=v['winter']['O'],v['winter']['N']
            for radius in RADII:
                x=[indexed[(radius,seed)] for seed in SEEDS]
                def av(season,key): return statistics.fmean(row[season][key] for row in x)
                out.append({'source':source,'year':year,'status':expected_status,
                  'n_original_dyads':old_n,'n_time_supported_dyads':n,
                  'tolerance_seconds':tol,'radius_km':radius,'n_seeds':12,
                  'winter':{k:av('winter',k) for k in ('O','N','D')},
                  'summer':{k:av('summer',k) for k in ('O','N','D')},
                  'winter_minus_summer':{k:av('winter_minus_summer',k) for k in ('O','N','D')},
                  'D_delta_signs':signed([row['winter_minus_summer']['D'] for row in x]),
                  'mean_abs_source_fix_gap_seconds':{
                      season:statistics.fmean(row[season+'_mean_abs_recording_gap_seconds'] for row in x)
                      for season in ('winter','summer')}})
    return out,scenario_count


def validate(opportunity_dir,geodesic_dir):
    rows=[];scenarios=0
    for source in RECEIPTS:
        o=_verified_load(source,'opportunity',opportunity_dir)
        g=_verified_load(source,'geodesic',geodesic_dir)
        by_year=_verify_opportunity(source,o)
        v,n=_verify_geodesic(source,g,by_year)
        rows+=v;scenarios+=n
    if scenarios!=360 or len(rows)!=32:
        raise AssertionError('Missing full 5 source-year × 2 tolerances × 3 radii × 12-seed results plus STOPs')
    return {'schema_version':1,'as_of':'2026-10-20',
            'scope':'Post-inspection source-native GPS positions within <=15/30min and 0.5/1/2km geodesic radii; no verified animal encounters/social/resource use',
            'n_source_studies':3,'n_geodesic_scenarios':scenarios,
            'n_source_year_tolerance_stop_rows':2,
            'n_summary_rows':len(rows),
            'original_source_receipts_sha256':{s:{'opportunity':r['opportunity_hash'],'geodesic':r['geodesic_hash']}
                                               for s,r in RECEIPTS.items()},
            'geodesic_source_run':'https://github.com/zuizui0223/batter/actions/runs/39418452060',
            'timestamp_source_run':'https://github.com/zuizui0223/batter/actions/runs/39417475863',
            'records':rows,
            'limits':['Each dyad same source/year; no biology-based population verification',
                      'Greedy maximal source-time matching controls observation support, not location accuracy',
                      'One-to-one <=15/30 min GPS proxy is not a physical interaction',
                      'Within-day spatial rematching reference does not preserve biological autocorrelation',
                      'Multiple source-years, dyads and seeds dependent; no p-values or population confidence intervals']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--opportunity-dir',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--geodesic-dir',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    result=validate(args.opportunity_dir,args.geodesic_dir)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.output:args.output.write_text(payload)
    else:print(payload)
    print('PASS exact pinned source receipts and all 360 aggregate geodesic sensitivity configurations')


if __name__=='__main__':
    main()
