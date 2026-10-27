#!/usr/bin/env python3
"""Validate seasonal positive-overlap edge structure from pinned V2 ZIP.

POST-INSPECTION descriptive analysis; aggregate only. Positive geographic
overlap is not an observed contact, association, or shared resource.
"""
import hashlib
import json
import math
from pathlib import Path
import zipfile

PINNED_BLOB = '0da5fe5f429e08194525c59b70d0840735d958ac'
SOURCES = ('turkey', 'black_bear', 'moose_snowy_range', 'white_tailed_deer')
SCALES = (1.0, 2.0, 5.0, 10.0)
ORIGINS = ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5))


def close(x, y):
    return math.isclose(x, y, abs_tol=2e-10, rel_tol=1e-10)


def signed(v):
    return 1 if v > 1e-12 else -1 if v < -1e-12 else 0


def edge_statistics(r):
    """Reconcile dyad counts, fixed means and Shapley-style components."""
    if r['status'] != 'DESCRIPTIVE_MATCHED_DYADS':
        assert r['n_pairs'] == 0
        return None
    n = r['n_pairs']
    assert isinstance(n, int) and n > 0
    state = r['dyad_states']
    both, only1, only2, neither = (state[k] for k in ('both', 'season1_only', 'season2_only', 'neither'))
    assert all(isinstance(v, int) and v >= 0 for v in (both, only1, only2, neither))
    assert both + only1 + only2 + neither == n
    a, b = both + only1, both + only2
    s1, s2 = r['season1'], r['season2']
    assert a == s1['positive_pairs'] and b == s2['positive_pairs']
    p, q = a/n, b/n
    assert close(p, s1['positive_fraction']) and close(q, s2['positive_fraction'])
    v1, v2 = s1['mean_X'], s2['mean_X']
    assert 0 <= v1 <= 1 and 0 <= v2 <= 1
    assert close(v1-v2, r['difference_season1_minus_season2'])
    m1, m2 = s1['positive_strength'], s2['positive_strength']
    assert (m1 is None) == (a == 0) and (m2 is None) == (b == 0)
    assert close(v1, p * m1 if a else 0) and close(v2, q * m2 if b else 0)
    if a and b:
        incidence=(p-q)*(m1+m2)/2
        strength=(m1-m2)*(p+q)/2
        assert close(incidence, r['incidence_component'])
        assert close(strength, r['positive_strength_component'])
        assert close(incidence+strength, v1-v2)
    else:
        incidence=strength=None
        assert r['incidence_component'] is None and r['positive_strength_component'] is None
    union=both+only1+only2
    jaccard=both/union if union else None
    denom=a*(n-a)*b*(n-b)
    phi=(both*neither-only1*only2)/math.sqrt(denom) if denom else None
    return {'n_pairs':n,'both':both,'only_first':only1,'only_second':only2,'neither':neither,
            'first_positive':a,'second_positive':b,'mean_first':v1,'mean_second':v2,
            'delta':v1-v2,'incidence':incidence,'strength':strength,
            'jaccard':jaccard,'turnover':1-jaccard if jaccard is not None else None,
            'first_retained_in_second':both/a if a else None,
            'second_already_in_first':both/b if b else None,
            'phi':phi,
            'density_expected_both':a*b/n,
            'density_relative_retention':both/(a*b/n) if a*b else None}


def verify_zip(path):
    content=Path(path).read_bytes()
    actual=hashlib.sha1(f'blob {len(content)}\0'.encode()+content).hexdigest()
    assert actual == PINNED_BLOB, 'Pinned source-derived aggregate archive changed'
    with zipfile.ZipFile(path) as z:
        summary=json.loads(z.read('CROSS_SOURCE_NEARBY_DYAD_V2_SUMMARY_2026_10_20.json'))
        baseline={(r['source'],r['year'],r['window'],r['mode']):r for r in summary['reference_rows']}
        assert len(baseline)==80
        results=[]
        for source in SOURCES:
            obj=json.loads(z.read(source+'.json'))['source']
            assert obj['status']=='COMPLETE_EXPLORATORY_GEOGRAPHIC_X'
            groups={}
            for r in obj['comparisons']:
                groups.setdefault((r['year'],r['window'],r['risk_set_mode']),[]).append(r)
            assert len(groups)==20 and sum(map(len,groups.values()))==320
            for (year,window,mode),scenarios in sorted(groups.items()):
                assert len(scenarios)==16
                assert {(r['grid_km'],r['origin_x_fraction'],r['origin_y_fraction']) for r in scenarios}=={
                    (w,*o) for w in SCALES for o in ORIGINS}
                assert len({r['n_pairs'] for r in scenarios})==1
                assert len({r['n_matched_animals'] for r in scenarios})==1
                measured=[(r,edge_statistics(r)) for r in scenarios]
                original=baseline[(source,year,window,mode)]
                selected=[s for r,s in measured if r['grid_km']==5 and r['origin_x_fraction']==r['origin_y_fraction']==0]
                assert len(selected)==1
                ref=selected[0]
                assert (ref is not None)==(original['status']=='DESCRIPTIVE_MATCHED_DYADS')
                assert scenarios[0]['n_pairs']==original['n_pairs']
                if ref:
                    assert ref['both']==original['states']['both']
                    assert ref['only_first']==original['states']['season1_only']
                    assert ref['only_second']==original['states']['season2_only']
                    assert ref['neither']==original['states']['neither']
                    assert close(ref['delta'],original['delta'])
                signs={}
                for name in ('delta','incidence','strength'):
                    vals=[v[name] for _,v in measured if v is not None and v[name] is not None]
                    signs[name]={str(k):sum(signed(x)==k for x in vals) for k in (-1,0,1)}
                    signs[name]['undefined']=16-len(vals)
                assert signs['delta']['1']==original['sensitivity_positive']
                assert signs['delta']['-1']==original['sensitivity_negative']
                assert signs['delta']['0']==original['sensitivity_zero']
                results.append({'source':source,'year':year,'window':window,'mode':mode,
                    'reference':ref,'signs16':signs,
                    'jaccard_range':{
                       'min': min((v['jaccard'] for _,v in measured if v is not None and v['jaccard'] is not None), default=None),
                       'max': max((v['jaccard'] for _,v in measured if v is not None and v['jaccard'] is not None), default=None)}})
        other=json.loads(z.read('moose.json'))['source']
        assert other['status']=='STOP_NO_VALID_SOURCE_TIMESTAMPS_OR_COORDINATES'
        assert 'comparisons' not in other
    assert len(results)==80
    return {'source_git_blob':PINNED_BLOB,'source_zip_sha256':hashlib.sha256(content).hexdigest(),
            'n_groups':len(results),'n_settings':1280,'n_stopped_sources':1,
            'focus':[r for r in results if r['window']=='winter_summer' and r['mode']=='near_centroid_25km' and r['reference'] is not None and r['reference']['n_pairs']>=20],
            'warning':'Post-inspection source-aggregate descriptives; not calibrated inference, habitat resources or encounters'}


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--json-out',type=Path)
    args=ap.parse_args()
    archive=Path(__file__).resolve().with_name('CROSS_SOURCE_NEARBY_DYAD_V2_FULL_AGGREGATES_2026_10_20.zip')
    result=verify_zip(archive)
    data=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n'
    if args.json_out:
        args.json_out.write_text(data,encoding='utf-8')
    else:
        print(data,end='')


if __name__=='__main__':
    main()
