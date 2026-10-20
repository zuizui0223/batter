#!/usr/bin/env python3
"""Verify pinned original-GPS observation-balance aggregate results only.

No source records, animal IDs, exact dates or coordinates are ever needed.
Refuse changed source SHA256, loss of supported dyads, missing-as-zero or
numeric inconsistencies. Sensitivity seeds are NOT biological replicates.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parent
PINNED={
'turkey':('40dc3c3efa5d08bc45a37fa08aa09822f53e73753225e581881cb892b6116c2c',435214,{2019:112,2020:21}),
'black_bear':('8c192c5f762c0d5d1e0b72e866cd4befdf96720bd87aad81684bb728a27277ad',148394,{2019:1,2020:104}),
'white_tailed_deer':('926c3f512e743fd2e0a51010df313652460f8ff8216b6633b5f6ff8dbb75b7d5',371080,{2019:55,2020:205}),
}
ARCHIVE_SHA256='857e4157606ca1a4bf87d2f7e76fa379ab7bbf77c2bfc491ffec8196f543ee48'
GRIDS={(1.,0.,0.),(5.,0.,0.),(5.,.5,.5),(10.,0.,0.)}
CHECK_FIELDS=('winter_mean_X','summer_mean_X','delta_mean_X',
              'winter_edge_fraction','summer_edge_fraction',
              'delta_incidence','delta_conditional_strength',
              'jaccard_positive_edges')


def close(a,b,tolerance=2e-10):
    return math.isclose(a,b,rel_tol=1e-10,abs_tol=tolerance)


def verify_seed(row,n):
    if row['n_pairs'] != n or n<1:
        raise AssertionError('Seed pair count changed')
    for name in ('winter_mean_X','summer_mean_X',
                 'winter_edge_fraction','summer_edge_fraction'):
        if row[name] is None or not 0 <= row[name] <= 1:
            raise AssertionError('Outside bounded geographic estimand')
    if not close(row['winter_mean_X']-row['summer_mean_X'],row['delta_mean_X']):
        raise AssertionError('Mean X difference mismatch')
    counts=(row['both_edges'],row['winter_only_edges'],
            row['summer_only_edges'],row['neither_edges'])
    if sum(counts)!=n or any(isinstance(x,bool) or not isinstance(x,int) or x<0 for x in counts):
        raise AssertionError('Dyad edge states do not partition the fixed risk set')
    b,w,s,z=counts
    assert row['winter_positive_pairs']==b+w
    assert row['summer_positive_pairs']==b+s
    if not close(row['winter_edge_fraction'],(b+w)/n) or not close(row['summer_edge_fraction'],(b+s)/n):
        raise AssertionError('Edge density inconsistent with counts')
    expected=b/(b+w+s) if b+w+s else None
    if expected is None:
        if row['jaccard_positive_edges'] is not None:
            raise AssertionError('Undefined Jaccard reported as a number')
    elif row['jaccard_positive_edges'] is None or not close(expected,row['jaccard_positive_edges']):
        raise AssertionError('Jaccard edge persistence mismatch')
    delta_p=row['delta_incidence']
    delta_strength=row['delta_conditional_strength']
    if delta_p is None or delta_strength is None:
        if (b+w>0 and b+s>0) or delta_p is not delta_strength:
            raise AssertionError('Missing strength component is not permitted')
    elif not close(delta_p+delta_strength,row['delta_mean_X']):
        raise AssertionError('Additive mean decomposition failed')


def verify_group(group,expected_n):
    if group['n_original_eligible_pairs']!=expected_n:
        raise AssertionError('Source cohort no longer matches reference dyad mask')
    if expected_n<2:
        if group['status']!='NOT_ESTIMABLE_FEWER_THAN_TWO_SOURCE_DYADS':
            raise AssertionError('Small n promoted to estimable')
        return {'status':group['status'],'original_pairs':expected_n}
    if group['status']!='EXPLORATORY_EFFORT_SENSITIVITY':
        raise AssertionError('Expected eligible balanced cohort')
    ks={row['k_fixes_per_animal_day']:row for row in group['by_fix_count']}
    if set(ks)!={1,2} or ks[1]['n_pairs']!=expected_n:
        raise AssertionError('1-fix risk set differs from baseline')
    if ks[2]['n_pairs']>expected_n or group['n_k2_supported_pairs']!=ks[2]['n_pairs']:
        raise AssertionError('2-fix risk set is not nested')
    if not close(ks[2]['n_pairs']/expected_n,group['k2_retention_fraction']):
        raise AssertionError('k2 attrition summary mismatch')
    info={'status':group['status'],'original_pairs':expected_n,'k2_pairs':ks[2]['n_pairs'],'grids':{}}
    for k, row in ks.items():
        grids={}
        for g in row['grids']:
            grid=(float(g['grid_km']),float(g['origin_x_fraction']),float(g['origin_y_fraction']))
            if grid in grids:
                raise AssertionError('Duplicated grid')
            grids[grid]=g
        if set(grids)!=GRIDS:
            raise AssertionError('Missing declared grid or origin')
        for grid,g in grids.items():
            if not row['n_pairs']:
                if g['seed_aggregate_results'] or g['summary'] is not None:
                    raise AssertionError('Missing dyads imputed')
                continue
            draws=g['seed_aggregate_results']
            if len(draws)!=24 or g['status']!='DESCRIPTIVE_EFFORT_STANDARDIZED':
                raise AssertionError('Incomplete seed experiment')
            for seed in draws:
                verify_seed(seed,row['n_pairs'])
            report=g['summary']
            for name in CHECK_FIELDS:
                values=[v[name] for v in draws if v[name] is not None]
                summary=report[name]
                if summary['n_defined'] != len(values):
                    raise AssertionError('Invalid defined-count denominator')
                if values:
                    if not close(statistics.fmean(values),summary['mean']) or not close(min(values),summary['min']) or not close(max(values),summary['max']):
                        raise AssertionError('Saved seed mean/range differs from source samples')
                    if not close(statistics.median(values),summary['median']):
                        raise AssertionError('Saved seed median differs from source samples')
                elif any(summary.get(x) is not None for x in ('mean','min','max','median')):
                    raise AssertionError('Undefined statistic saved as a number')
                if name.startswith('delta_'):
                    sign=Counter(1 if v>1e-12 else -1 if v< -1e-12 else 0 for v in values)
                    if [summary[f] for f in ('positive_seeds','negative_seeds','near_zero_seeds')] != [sign[1],sign[-1],sign[0]]:
                        raise AssertionError('Seed sign-count mismatch')
            if grid==(5.,0.,0.):
                info['grids'][str(k)]={'delta_mean_X':report['delta_mean_X']['mean'],
                        'delta_incidence':report['delta_incidence']['mean'],
                        'delta_strength':report['delta_conditional_strength']['mean'],
                        'signs_incidence':(report['delta_incidence']['positive_seeds'],
                                           report['delta_incidence']['negative_seeds'],
                                           report['delta_incidence']['near_zero_seeds']),
                        'signs_strength':(report['delta_conditional_strength']['positive_seeds'],
                                          report['delta_conditional_strength']['negative_seeds'],
                                          report['delta_conditional_strength']['near_zero_seeds'])}
    return info


def validate(path=ROOT):
    output={'n_original_sources':0,'n_source_years':0,'n_full_seed_grid_draws':0,
            'all_source_receipts_pinned':True,'results':[]}
    for source,(expected_hash,fixes,years) in PINNED.items():
        file=Path(path)/('SEASONAL_EDGE_EFFORT_BALANCED_'+source.upper()+'_2026_10_20.json')
        raw=file.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected_hash:
            raise AssertionError('Aggregated source receipt changed')
        data=json.loads(raw)
        if data['source']!=source or data['n_source_fixes']!=fixes or data['n_seeds']!=24:
            raise AssertionError('Source size or seeds differ')
        if data['baseline_aggregate_zip_sha256']!=ARCHIVE_SHA256 or not data['source_original_event_qc_verified']:
            raise AssertionError('Original checksum-pinned audit absent')
        if data['centroid_group_labels_verified'] is not False:
            raise AssertionError('Population metadata claim expanded')
        rows={g['year']:g for g in data['groups']}
        if set(rows)!=set(years):
            raise AssertionError('Source years or source cohorts changed')
        for year,expected_n in years.items():
            info=verify_group(rows[year],expected_n)
            output['results'].append({'source':source,'year':year,**info})
            output['n_source_years']+=1
            if expected_n>=2:
                for k in rows[year]['by_fix_count']:
                    output['n_full_seed_grid_draws']+=len(k['grids'])*len(k['grids'][0]['seed_aggregate_results'])
        output['n_original_sources']+=1
    return output


def main():
    out=validate()
    print(json.dumps(out,sort_keys=True,allow_nan=False))


if __name__=='__main__':
    main()
