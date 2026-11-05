"""Offline reconciliation of the frozen aggregate-only follow-up."""
import hashlib,json,math,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def validate(root=ROOT):
    d=json.loads((root/'TURKEY_CORE_EFFORT_RESULT_2026_11_05.json').read_text(encoding='utf-8'))
    contract=(root/'TURKEY_CORE_EFFORT_DESIGN_2026_11_05.md').read_bytes().replace(b'\r\n',b'\n')
    assert hashlib.sha256(contract).hexdigest()==d['contract_sha256']
    assert d['source_commit']=='45017e0f7f35fd79468db07f16ee162816efc0d6'
    assert d['original_accepted_gps_fixes']==435214
    assert len(d['groups'])==5
    checked=0
    for group in d['groups'].values():
        rows=group['balanced_draws']
        assert [r['sample'] for r in rows]==list(range(24))
        assert min(group['common_day_counts'].values())>=7
        for label,summary in group['balanced_summary'].items():
            for key,values in [
                ('whole_group',[r['contrasts'][label]['delta_km'] for r in rows]),
                ('worst_animal_deletion',[r['contrasts'][label]['leave_one_animal']['minimum'] for r in rows])]:
                s=summary[key]
                assert s['n']==24 and s['positive']==sum(v>0 for v in values)
                for field,value in [('minimum',min(values)),('maximum',max(values)),('mean',statistics.fmean(values))]:
                    assert math.isclose(s[field],value,abs_tol=1e-12)
                checked+=1
    for r in d['full_month_exact_mean_decomposition']:
        assert math.isclose(r['total_delta_km'],r['isolate_core_term_km']+r['core_core_term_km'],abs_tol=1e-10)
        assert math.isclose(r['isolate_pair_share_of_total'],r['isolate_core_term_km']/r['total_delta_km'],abs_tol=1e-12)
    assert d['groups']['2020_core']['balanced_summary']['apr_minus_feb']['worst_animal_deletion']['positive']==24
    assert d['groups']['2019_component_1_original_edges']['full_days']['contrasts']['apr_minus_feb']['leave_one_animal']['minimum']<0
    assert max(x['absolute_difference'] for x in d['baseline_numeric_differences'])<1e-4
    assert d['independent_atan2_max_pair_distance_difference_km']<1e-4
    return {'status':'AGGREGATE_RECONCILED_NOT_INDEPENDENT_REPLICATION','group_draws':120,'checked_summaries':checked}

if __name__=='__main__':print(json.dumps(validate()))
