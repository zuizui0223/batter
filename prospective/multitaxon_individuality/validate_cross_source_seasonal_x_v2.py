#!/usr/bin/env python3
"""Independently check aggregate seasonal X results (not the private source)."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

YEARS=(2019,2020)
WINDOWS=('winter_summer','early_late')
SCALES=(1.,2.,5.,10.)
ORIGINS=((0.,0.),(.5,0.),(0.,.5),(.5,.5))
MODES=('source_wide','near_centroid_25km','near_centroid_50km','near_centroid_100km','same_reference_label')
TOL=1e-9


def near(a,b):
    return math.isclose(a,b,rel_tol=TOL,abs_tol=TOL)


def validate_rows(rows):
    expected={(year,window,scale,*origin,mode) for year in YEARS
              for window in WINDOWS for scale in SCALES for origin in ORIGINS
              for mode in MODES}
    observed={}
    for row in rows:
        key=(row['year'],row['window'],float(row['grid_km']),
             float(row['origin_x_fraction']),float(row['origin_y_fraction']),row['risk_set_mode'])
        if key in observed:
            raise AssertionError('Duplicate scenario')
        observed[key]=row
        n=row['n_pairs']
        if not isinstance(n,int) or n<0:
            raise AssertionError('Invalid dyad count')
        if row['n_matched_animals']>0 and n==0:
            raise AssertionError('Animals reported without a matched pair')
        if n==0:
            if row['status']!='NOT_ESTIMABLE_NO_MATCHED_DYADS':
                raise AssertionError('Missing risk-set must not be zero overlap')
            continue
        if row['status']!='DESCRIPTIVE_MATCHED_DYADS':
            raise AssertionError('Nonempty matched risk-set must be descriptive')
        if row['n_matched_animals']<2 or row['n_matched_animals']>2*n:
            raise AssertionError('Impossible matched animals')
        states=row['dyad_states']
        if sum(states.values())!=n or any((not isinstance(x,int) or x<0) for x in states.values()):
            raise AssertionError('Four dyad states fail to partition n')
        signs=row['paired_difference_signs']
        if sum(signs.values())!=n:
            raise AssertionError('Paired sign counts fail to partition n')
        for season,name,positive in ((row['season1'],'season1','season1_only'),
                                     (row['season2'],'season2','season2_only')):
            expected_positive=states[positive]+states['both']
            if season['positive_pairs']!=expected_positive:
                raise AssertionError('Season incidence differs from dyad transition counts')
            p=expected_positive/n
            if not near(season['positive_fraction'],p):
                raise AssertionError('Season incidence denominator inconsistent')
            if not 0<=season['mean_X']<=1:
                raise AssertionError('Overlap mean outside [0,1]')
            if positive_count:=expected_positive:
                strength=season['positive_strength']
                if strength is None or not 0<strength<=1:
                    raise AssertionError('Observed positives require valid positive strength')
                if not near(season['mean_X'],p*strength):
                    raise AssertionError('Mean overlap fails p*E[X|X>0] identity')
            elif season['positive_strength'] is not None or not near(season['mean_X'],0):
                raise AssertionError('All-zero season cannot have defined strength')
        d=row['season1']['mean_X']-row['season2']['mean_X']
        if not near(row['difference_season1_minus_season2'],d):
            raise AssertionError('Reported seasonal difference is inconsistent')
        if row['season1']['positive_pairs'] and row['season2']['positive_pairs']:
            if any(row[k] is None for k in ('incidence_component','positive_strength_component','decomposition_residual')):
                raise AssertionError('Missing estimable decomposition component')
            if not near(d,row['incidence_component']+row['positive_strength_component']):
                raise AssertionError('Exact two-component decomposition failed')
            if not near(row['decomposition_residual'],0):
                raise AssertionError('Decomposition residual nonzero')
        elif any(row[k] is not None for k in ('incidence_component','positive_strength_component','decomposition_residual')):
            raise AssertionError('Undefined conditional mean must not be imputed')
    if set(observed)!=expected:
        raise AssertionError('Full fixed 320-scenario grid is incomplete')
    for year in YEARS:
        for window in WINDOWS:
            for scale in SCALES:
                for origin in ORIGINS:
                    base=(year,window,scale,*origin)
                    wide=observed[(*base,'source_wide')]
                    stratum=observed[(*base,'same_reference_label')]
                    if stratum['n_pairs']>wide['n_pairs']:
                        raise AssertionError('Restricted group exceeds source-wide risk set')
                    near_counts=[observed[(*base,f'near_centroid_{k}km')]['n_pairs'] for k in (25,50,100)]
                    if not (near_counts[0]<=near_counts[1]<=near_counts[2]<=wide['n_pairs']):
                        raise AssertionError('Centroid-distance nested risk sets are inconsistent')
    return {'scenarios_verified':len(observed),'matched_scenarios':sum(r['n_pairs']>0 for r in rows)}


def validate_document(payload):
    if payload['schema_version']!=2 or payload['status']!='EXPLORATORY_NOT_CROSS_TAXON_INFERENCE':
        raise AssertionError('Unsupported public evidence stage')
    source=payload['source']
    if source['status']=='COMPLETE_EXPLORATORY_GEOGRAPHIC_X':
        if not source.get('file_receipts') or not all(x['md5_verified'] for x in source['file_receipts']):
            raise AssertionError('Original source MD5 receipts missing')
        detail=validate_rows(source['comparisons'])
        if detail['matched_scenarios']!=source['estimable_rows']:
            raise AssertionError('Matched scenario count mismatch')
    elif source['status']=='NOT_ESTIMABLE_MATCHED_SEASONAL_DYADS':
        if not source.get('file_receipts') or not all(x['md5_verified'] for x in source['file_receipts']):
            raise AssertionError('Missing source checksum receipts')
        detail=validate_rows(source['comparisons'])
        if detail['matched_scenarios']!=0 or source['estimable_rows']!=0:
            raise AssertionError('Invalid not-estimable classification')
    elif source['status'].startswith('STOP_'):
        if source.get('comparisons'):
            raise AssertionError('A STOP source cannot report ecological comparisons')
        detail={'scenarios_verified':0,'matched_scenarios':0}
    else:
        raise AssertionError('Unrecognized source status')
    # Conservative field-name screening, without treating source title as private.
    text=json.dumps(payload,allow_nan=False)
    for name in ('individual-local-identifier','tag-local-identifier','location-lat',
                 'location-long','grid_cell_id','animal_id','pair_id'):
        if '\"'+name+'\"' in text:
            raise AssertionError('Prohibited raw-source field in aggregate output')
    return {'source':source['label'],'source_status':source['status'],**detail}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(validate_document(json.loads(args.input.read_text()))))

if __name__=='__main__':
    main()
