import csv
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from myotis_source_gate_v1 import audit_archive, analyse_canonical, SourceGateError
import myotis_source_gate_v1 as model


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
        rows = make_rows()
        extra_valid = rows[0].copy()
        extra_valid['trial_id'] += '-third-replicate'
        rows.append(extra_valid)
        rows[0]['buzz_ii_valid'] = '0'
        rows[0]['buzz_ii_ms'] = ''
        out = analyse_canonical(self.write_csv(rows))
        self.assertEqual(out['n_invalid_buzz'], 1)
        self.assertEqual(out['n_valid_buzz'], len(rows)-1)

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

    def test_missing_all_valid_buzz_for_one_treatment_fails_closed(self):
        rows = make_rows()
        for r in rows:
            if r['bat_id'] == 'bat1' and r['session_date'] == '2025-01-01' and r['distance_m'] == 0.08 and r['speed_m_s'] == 0.5:
                r['buzz_ii_valid'] = '0'
                r['buzz_ii_ms'] = ''
        # Treatment exposure is recorded, but usable buzzes are absent.
        with self.assertRaises(SourceGateError):
            analyse_canonical(self.write_csv(rows))

    def test_unequal_trial_count_does_not_reweight_physical_treatments(self):
        rows = make_rows()
        for r in rows:
            if r['distance_m'] == 0.08 and r['speed_m_s'] == 0.5:
                r['buzz_ii_ms'] = str(float(r['buzz_ii_ms']) * 3.0)
        baseline = analyse_canonical(self.write_csv(rows))
        more = [r.copy() for r in rows]
        for r in rows:
            if r['distance_m'] == 0.08 and r['speed_m_s'] == 0.5:
                for j in range(9):
                    duplicate_measure = r.copy()
                    duplicate_measure['trial_id'] += f'-extra-{j}'
                    more.append(duplicate_measure)
        changed = analyse_canonical(self.write_csv(more))
        # Replicating observations of one published treatment must not alter
        # its fixed equal-treatment contribution to the challenge contrast.
        self.assertAlmostEqual(baseline['train_group_beta'], changed['train_group_beta'], places=12)
        for old, new in zip(baseline['by_bat'], changed['by_bat']):
            self.assertAlmostEqual(old['train_beta'], new['train_beta'], places=12)



    def test_factorial_four_cells_exactly_recover_separate_response_axes(self):
        # Exact orthogonal 2x2 with physical distance x speed stimuli.
        # A=(.08,.5), B=(.08,1), C=(.24,.5), D=(.24,1).
        function = getattr(model, 'factorial_2x2_coefficients', None)
        self.assertIsNotNone(function, "No factorial sensory-response decomposition")
        four = {(0.08, 0.5): 2.4, (0.08, 1.0): 2.0,
                (0.24, 0.5): 1.0, (0.24, 1.0): 2.6}
        out = function(four)
        self.assertAlmostEqual(out['mean'], 2.0)
        self.assertAlmostEqual(out['speed'], 0.3)
        self.assertAlmostEqual(out['distance'], -0.2)
        self.assertAlmostEqual(out['speed_x_distance'], 0.5)

    def test_factorial_secondary_is_fixed_and_held_out_on_days_3_and_4(self):
        out = analyse_canonical(self.write_csv(make_rows(personal=True)))
        self.assertIn('factorial_2x2_secondary', out)
        secondary = out['factorial_2x2_secondary']
        self.assertEqual(secondary['n_test_bat_days'], 8)
        self.assertEqual(secondary['dimensions'], ['speed', 'distance', 'speed_x_distance'])
        self.assertLess(secondary['equal_bat_mse_personal'], secondary['equal_bat_mse_group'])
        self.assertEqual({r['date'] for r in secondary['held_out']}, {'2025-01-03','2025-01-04'})

    def test_factorial_secondary_never_learns_from_future_test_values(self):
        original = make_rows()
        before = analyse_canonical(self.write_csv(original))
        for r in original:
            if r['session_date'] >= '2025-01-03':
                r['buzz_ii_ms'] = str(float(r['buzz_ii_ms']) * (2.0 if r['speed_m_s'] == 1.0 else 0.7))
        after = analyse_canonical(self.write_csv(original))
        b=before['factorial_2x2_secondary'];a=after['factorial_2x2_secondary']
        self.assertEqual(b['train_group_coefficients'], a['train_group_coefficients'])
        self.assertEqual([q['train_coefficients'] for q in b['by_bat']],
                         [q['train_coefficients'] for q in a['by_bat']])

    def test_factorial_shared_only_synthetic_does_not_fake_personal_advantage(self):
        out = analyse_canonical(self.write_csv(make_rows(personal=False)))
        s=out['factorial_2x2_secondary']
        self.assertAlmostEqual(s['equal_bat_mse_personal'], s['equal_bat_mse_group'], places=12)



    def test_nominal_equal_motion_time_pair_exists_but_is_not_measured(self):
        # Values are NOMINAL distance/speed, not camera-confirmed time.
        pair = getattr(model, "NOMINAL_DURATION_MATCH_PAIR", None)
        self.assertIsNotNone(pair, "Missing physically identified nominal duration pair")
        a, b = pair
        self.assertEqual(a, (0.08, 0.5))
        self.assertEqual(b, (0.24, 1.5))
        self.assertAlmostEqual(a[0]/a[1], b[0]/b[1], places=12)
        self.assertAlmostEqual(a[0]/a[1], 0.160, places=12)

    def test_nominal_duration_pair_diagnostic_is_exploratory_only(self):
        obj = analyse_canonical(self.write_csv(make_rows(personal=True)))
        self.assertIn("nominal_duration_pair_diagnostic", obj)
        diag = obj["nominal_duration_pair_diagnostic"]
        self.assertEqual(diag["n_bats"], 4)
        self.assertEqual(diag["n_test_bat_days"], 8)
        self.assertFalse(diag["actual_duration_verified"])
        self.assertEqual(diag["nominal_travel_seconds"], [0.16, 0.16])
        self.assertEqual(diag["scope"], "SECONDARY_DIAGNOSTIC_NOMINAL_DURATION_NOT_CAUSAL")
        self.assertLess(diag["equal_bat_mse_personal"], diag["equal_bat_mse_group"])
        self.assertNotIn("p_value", diag)
        self.assertEqual({v["date"] for v in diag["held_out"]},
                         {"2025-01-03", "2025-01-04"})

    def test_nominal_pair_diagnostic_training_frozen_to_days_one_two(self):
        rows = make_rows(personal=True)
        original = analyse_canonical(self.write_csv(rows))["nominal_duration_pair_diagnostic"]
        for row in rows:
            if row["session_date"] >= "2025-01-03":
                row["buzz_ii_ms"] = str(float(row["buzz_ii_ms"])*1.7)
        changed = analyse_canonical(self.write_csv(rows))["nominal_duration_pair_diagnostic"]
        self.assertEqual(original["group_mean_train_contrast"],
                         changed["group_mean_train_contrast"])
        self.assertEqual([r["training_contrast"] for r in original["by_bat"]],
                         [r["training_contrast"] for r in changed["by_bat"])


if __name__ == '__main__':
    unittest.main()
