import csv
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from myotis_source_gate_v1 import audit_archive, analyse_canonical, SourceGateError


FIELDS = ['bat_id', 'session_date', 'trial_id', 'distance_m', 'speed_m_s', 'buzz_ii_valid', 'buzz_ii_ms']
REGIMES = [(0.08, 0.5), (0.08, 1), (0.08, 1.3), (0.24, 0.5), (0.24, 1), (0.24, 1.5)]


def make_rows(personal=True, invalid=False):
    rows = []
    for i in range(1, 5):
        for day in range(1, 5):
            date = f'2025-01-{day:02d}'
            for regime, (distance, speed) in enumerate(REGIMES):
                for rep in range(2):
                    difficult = regime >= 4
                    # 5×10^... positive milliseconds; differences in log1p known exactly
                    baseline = 3.0 + i * 0.1 + day * 0.02
                    response = (-0.1 + i*0.18) if personal else 0.25
                    log_duration = baseline + (response if difficult else 0.0)
                    ms = (2.718281828459045 ** log_duration) - 1
                    rows.append(dict(bat_id=f'bat{i}', session_date=date,
                                     trial_id=f'{i}-{day}-{regime}-{rep}',
                                     distance_m=distance, speed_m_s=speed,
                                     buzz_ii_valid='1', buzz_ii_ms=str(ms)))
    if invalid:
        rows[0]['buzz_ii_valid'] = '0'
        rows[0]['buzz_ii_ms'] = ''
    return rows


class SourceGateTests(unittest.TestCase):
    def write_csv(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        file = Path(tmp.name)/'normalized.csv'
        with file.open('w', newline='', encoding='utf-8') as w:
            writer = csv.DictWriter(w, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        return file

    def test_heldout_personal_response_predicts_when_stable(self):
        result = analyse_canonical(self.write_csv(make_rows(personal=True)))
        self.assertEqual(result['n_bats'], 4)
        self.assertEqual(result['n_train_bat_days'], 8)
        self.assertEqual(result['n_test_bat_days'], 8)
        self.assertEqual(result['status'], 'EXPLORATORY_POST_PUBLICATION')
        self.assertLess(result['equal_bat_mse_personal'], result['equal_bat_mse_group'])
        self.assertTrue(all('train_beta' in x for x in result['by_bat']))
        self.assertNotIn('p_value', result)

    def test_test_data_must_not_change_training_coefficients(self):
        rows = make_rows()
        before = analyse_canonical(self.write_csv(rows))
        for r in rows:
            if r['session_date'] >= '2025-01-03' and r['buzz_ii_valid'] == '1':
                r['buzz_ii_ms'] = str(float(r['buzz_ii_ms']) * 1.15)
        after = analyse_canonical(self.write_csv(rows))
        self.assertEqual(before['train_group_beta'], after['train_group_beta'])
        self.assertEqual([x['train_beta'] for x in before['by_bat']], [x['train_beta'] for x in after['by_bat']])

    def test_missing_buzz_not_zero_filled(self):
        out = analyse_canonical(self.write_csv(make_rows(invalid=True)))
        self.assertEqual(out['n_invalid_buzz'], 1)
        self.assertEqual(out['n_valid_buzz'], len(make_rows())-1)

    def test_missing_bat_challenge_day_fails_closed(self):
        rows=[r for r in make_rows() if not (r['bat_id']=='bat1' and r['session_date']=='2025-01-04' and r['distance_m']==0.24)]
        with self.assertRaises(SourceGateError):
            analyse_canonical(self.write_csv(rows))

    def test_only_three_dates_per_bat_fails_closed(self):
        rows=[r for r in make_rows() if not (r['bat_id']=='bat1' and r['session_date']=='2025-01-04')]
        with self.assertRaises(SourceGateError):
            analyse_canonical(self.write_csv(rows))

    def test_duplicate_trial_fails_closed(self):
        rows=make_rows()
        rows.append(rows[0].copy())
        with self.assertRaises(SourceGateError):
            analyse_canonical(self.write_csv(rows))

    def test_archive_inventory_shows_headers_but_no_outcome_values(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        zpath=Path(tmp.name)/'dataset.zip'
        with zipfile.ZipFile(zpath,'w') as z:
            z.writestr('data/observations.csv','bat_id,session_date,buzz_ii_ms\nbat1,2025-01-01,99.0\n')
            z.writestr('code/analysis.R','print("ok")')
            z.writestr('nested/variables.mat', b'MATLAB 5.0 MAT-file fake contents')
        out=audit_archive(zpath)
        self.assertEqual(out['archive_type'], 'zip')
        row=next(f for f in out['files'] if f['path']=='data/observations.csv')
        self.assertIn('buzz_ii_ms', row['columns'])
        self.assertNotIn('99.0',json.dumps(out))
        self.assertEqual(out['raw_data_schema_status'], 'HOLD_NOT_MAPPED')

    def test_archive_rejects_unsafe_filename(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        zpath=Path(tmp.name)/'bad.zip'
        with zipfile.ZipFile(zpath,'w') as z:z.writestr('../escape.csv','x\ny\n')
        with self.assertRaises(SourceGateError):audit_archive(zpath)

    def test_common_response_does_not_invent_individual_predictive_gain(self):
        out = analyse_canonical(self.write_csv(make_rows(personal=False)))
        self.assertAlmostEqual(out["equal_bat_mse_personal"], out["equal_bat_mse_group"], places=12)

    def test_cannot_replace_missing_buzz_with_zero(self):
        rows = make_rows(invalid=True)
        rows[0]["buzz_ii_ms"] = "0"
        with self.assertRaises(SourceGateError):
            analyse_canonical(self.write_csv(rows))

    def test_stimulus_units_must_match_original_physical_regimes(self):
        rows = make_rows()
        rows[0]["speed_m_s"] = 500  # millimetres/s erroneously supplied as m/s
        with self.assertRaises(SourceGateError):
            analyse_canonical(self.write_csv(rows))

    def test_physical_bat_count_cannot_be_inflated_by_trials(self):
        rows = [r for r in make_rows() if r["bat_id"] != "bat4"]
        with self.assertRaises(SourceGateError):
            analyse_canonical(self.write_csv(rows))


if __name__ == '__main__':
    unittest.main()
