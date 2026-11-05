#!/usr/bin/env python3
"""Exact annual-centroid dyad-band accounting from pinned Movebank source aggregates.

Derives signed contributions to the source-wide winter-vs-summer L1:
same-day GPS near-position minus adjacent-day original trajectory mean.
Read ONLY source/year aggregate JSON: no GPS tracks, animal IDs or dyad
rows. The far 2020 5 dyads share one animal but are NOT 5 independent
events. All contrasts are post-inspection descriptive arithmetic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

BASE=Path(__file__).resolve().parent
INFLUENCE_NAME='SOURCE_SPATIAL_INFLUENCE_SUMMARY_2026_10_22.json'
INFLUENCE_GIT_BLOB='12b1551acbf6cdfe2467449d221294e786b60292'
MOVER_NAME='TURKEY_SINGLE_MOVER_ORIGINAL_GPS_2026_10_22.json'
MOVER_SHA='7b84c27d0b05449e0a53dc465964c7fd0c8c3aed81478556387cb706598f4225'
YEARS=(2019,2020)
CLOCK_GAPS=(900,1800)
RADIUS_KM=(.5,1.,2.)
DIRECTIONS=('original_A_to_B','reversed_B_to_A')
EXPECTED={2019:{5:73,10:78,25:112},2020:{5:14,10:16,25:21}}
EPS=2e-10


def close(a,b):
    return math.isclose(a,b,rel_tol=1e-10,abs_tol=EPS)


def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def _verified_json(path,digest,kind):
    raw=Path(path).read_bytes()
    actual=blob_sha(raw) if kind=='gitblob' else hashlib.sha256(raw).hexdigest()
    if actual!=digest:
        raise AssertionError('Original source-derived aggregate '+kind+' checksum changed')
    return json.loads(raw)


def band_decompose(rows, expected_counts):
    """Independent algebraic decomposition of EXACT three nested subset means."""
    if set(rows)!={5,10,25}:
        raise AssertionError('Only exact three frozen annual usage-center cutoffs may be included')
    for threshold, (n,mean) in rows.items():
        if (n!=expected_counts[threshold] or
                isinstance(mean,bool) or
                not isinstance(mean,(float,int)) or
                not math.isfinite(mean) or not -1<=mean<=1):
            raise AssertionError('Non-frozen original dyad denominator or mean')
    n5,n10,n25=(rows[t][0] for t in (5,10,25))
    m5,m10,m25=(rows[t][1] for t in (5,10,25))
    if not 0<n5<n10<n25:
        raise AssertionError('Source annual-centroid sets are not properly nested')
    sums=[n5*m5, n10*m10-n5*m5, n25*m25-n10*m10]
    counts=[n5,n10-n5,n25-n10]
    means=[total/count for total,count in zip(sums,counts)]
    if sum(counts)!=n25 or not close(math.fsum(sums),n25*m25):
        raise AssertionError('Annulus source signed means fail whole-source reconstruction')
    if not close(sum(count*mean for count,mean in zip(counts,means))/n25,m25):
        raise AssertionError('Source three-annulus weighted mean identity failed')
    if any(abs(v)>1+EPS for v in means):
        raise AssertionError('Implied annulus mean outside physically possible source L1 [-1,1]')
    source_total=n25*m25
    frac=sums[2]/source_total if abs(source_total)>1e-12 else None
    return {
        'whole_source':{'n_original_dyads':n25,'winter_minus_summer_L_mean':m25,
                        'signed_sum_over_dyads':source_total},
        'annuli':[
          {'annual_centroid_separation_band':name,
           'n_original_dyads':count,'winter_minus_summer_L_mean':avg,
           'signed_sum_over_dyads':total,
           'below_minimum_eight_pair_standalone_biological_gate':count<8}
          for name,count,avg,total in zip(('<=5 km','(5,10] km','(10,25] km'),
                                           counts,means,sums)],
        'far10to25_fraction_of_signed_whole_source_sum':frac,
        'note':'The share is an arithmetic ratio, may exceed 1 or be negative if source contributions offset. Not causal fraction explained or independent pair effects',
    }


def derive(folder=BASE):
    root=Path(folder)
    inf=_verified_json(root/INFLUENCE_NAME,INFLUENCE_GIT_BLOB,'gitblob')
    mover=_verified_json(root/MOVER_NAME,MOVER_SHA,'sha256')
    if (inf['status']!='POST_INSPECTION_SOURCE_GPS_YEAR_REUSE_AND_SPATIAL_INFLUENCE_VALIDATED'
            or inf['n_original_source_studies']!=3
            or inf['n_replayed_original_source_seed_radius_scores']!=576
            or mover['status']!='POST_INSPECTION_SINGLE_ORIGINAL_TURKEY_SEASONAL_MOVER_GEOGRAPHY'
            or mover['original_2019_2020_complete_GPS_fix_count']!=435214
            or not mover['complete_original_source_MD5_SHA256_reference_verified']
            or not mover['independent_original_time_position_multiset_verified']
            or mover['source']!='turkey' or mover['doi']!='10.5441/001/1.671'):
        raise AssertionError('Expected original Movebank source and verified analysis status absent')
    new=next(x for x in mover['groups'] if x['year']==2020)
    topology=new['original_source_graph_topology']
    if (topology['n_annual10_to25km_dyads']!=5
        or topology['n_outer10_dyads_incident_to_isolated_animal']!=5
        or topology['n_all_25km_dyads']!=21
        or topology['n_isolated_core_dyads_all_25km']!=6):
        raise AssertionError('All five 2020 annual >10km source pairs no longer share the one original bird')
    if mover['n_reused_original_animal_IDs_between_years']!=0:
        raise AssertionError('2020 turkey original subjects reused in 2019')
    samples=[x for x in inf['summaries'] if x['source']=='turkey']
    eligible={(x['year'],x['tolerance_seconds'],float(x['centroid_pair_distance_max_km'])):x for x in samples}
    if len(samples)!=12 or set(eligible)!={(year,gap,float(d))
            for year in YEARS for gap in CLOCK_GAPS for d in (5,10,25)}:
        raise AssertionError('Missing or unexpected turkey source/year/GPS time/cutoff results')
    output={
        'schema_version':1,'as_of':'2026-10-23',
        'status':'POST_INSPECTION_SOURCE_WEIGHTED_PAIR_DUPLICATION_ACCOUNTING',
        'original_DOI':'10.5441/001/1.671',
        'original_GPS_fixes_2019_2020':435214,
        'source_sha256_original_single_mover':MOVER_SHA,
        'source_git_blob_original_spatial_influence':INFLUENCE_GIT_BLOB,
        'n_year_gap_orientation_radius_comparisons':0,
        'results':[],
        'year2020_one_animal_in_all_five_far10_to25km_dyads':True,
        'year2020_one_animal_janfeb_to_summer_source_center_shift_km':
            new['unique_annual5_isolated_individual_janfeb_to_summer_center_shift_km'],
        'source_calendar_scope':'Jan/Feb/Dec of source year versus Jun/Jul/Aug, not contiguous winter; no verified December 2020 support',
        'nonclaims':[
            'Distinct original dyads sharing one animal are not independent biological interaction replications',
            'Signed sum fraction can exceed 100 percent and is not a causal effect share',
            'The >10km five-dyad annulus is below the declared minimum eight independent-pair descriptive gate',
            'Original published study may mix demographic populations; source tag GPS fix error/clock unknown',
            'Seasonal center movement is source geography not an observed encounter, flock membership, food-resource use or migration mechanism',
        ]}
    for year in YEARS:
        for gap in CLOCK_GAPS:
            for direction in DIRECTIONS:
                for radius in RADIUS_KM:
                    row_by_radius={}
                    for threshold in (5,10,25):
                        x=eligible[(year,gap,float(threshold))]
                        if x['n_dyads']!=EXPECTED[year][threshold]:
                            raise AssertionError('Original year/site cutoff denominator changed')
                        hits=[v for v in x['radii'] if
                              v['orientation']==direction and v['radius_km']==radius]
                        if len(hits)!=1:
                            raise AssertionError('Duplicate/missing original A/B × radius source result')
                        value=hits[0]['mean_winter_minus_summer_L']
                        row_by_radius[threshold]=(x['n_dyads'],value)
                    components=band_decompose(row_by_radius,EXPECTED[year])
                    output['results'].append({
                        'source':'turkey','year':year,
                        'time_tolerance_seconds':gap,
                        'geodesic_GPS_near_radius_km':radius,
                        'animal_anchor_orientation':direction,
                        **components,
                    })
                    output['n_year_gap_orientation_radius_comparisons']+=1
    if len(output['results'])!=24:
        raise AssertionError('Expected full 2 years ×2 gaps ×2 anchors ×3 radii source decomposition')
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir',type=Path,default=BASE)
    p.add_argument('--output',type=Path)
    p.add_argument('--verify',type=Path)
    args=p.parse_args()
    d=derive(args.input_dir)
    text=json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+'\n'
    if args.verify:
        if json.loads(args.verify.read_text())!=d:
            raise AssertionError('Previously published weighted-dyad source table inconsistent')
    if args.output:args.output.write_text(text)
    else:print(text,end='')
    print('PASS source-wide original GPS annulus accounting: 24 configurations; 2020 all five far dyads share 1 bird')


if __name__=='__main__':
    main()
