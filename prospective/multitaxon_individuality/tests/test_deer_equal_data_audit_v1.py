"""Regressions for same-record pooling, score weights, and frozen support."""
import calendar
from collections import Counter, defaultdict
from datetime import datetime
import math
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deer_seasonal_rx_v1 import WeightedDistribution, analyze_month_r, balanced_profile

try:
    import deer_equal_data_audit_v1 as audit
except ModuleNotFoundError as error:
    if error.name != 'deer_equal_data_audit_v1':
        raise
    audit = None


def step(animal, day, index, value):
    dt = datetime(2018, 4, day, index * 2)
    return SimpleNamespace(animal=animal, day=dt.toordinal(), year=2018,
        month=4, dt=dt, hour_bin=0, lon=.001, lat=.001,
        speed_kmh=math.expm1(value) / 20)


def constant_steps():
    return [step(str(animal), day, index, 2 * animal)
            for animal in range(2) for day in range(1, 31) for index in range(3)]


def brute_crps(points, observed):
    return (math.fsum(weight * abs(value - observed) for value, weight in points)
            - .5 * math.fsum(w * v * abs(x - y)
                            for x, w in points for y, v in points))


class TestEqualDataAudit(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(audit, 'The additive equal-data audit is not implemented')

    def test_extra_sample_counterexample_is_not_identity_weight_gain(self):
        profiles = {'focal': WeightedDistribution([(2, 1)]),
                    'other': WeightedDistribution([(0, 1)])}
        peer, pool, personal = audit.audit_models(profiles, 'focal', 15)
        scores = [sum(model.crps(y) for y in (0, 2)) / 2
                  for model in (peer, pool, personal)]
        self.assertAlmostEqual(scores[0], 1)
        self.assertAlmostEqual(scores[1], .5)
        self.assertAlmostEqual(scores[2], .625)
        self.assertAlmostEqual(scores[0] - scores[2], .375)
        self.assertAlmostEqual(scores[1] - scores[2], -.125)
        self.assertAlmostEqual(scores[0] - scores[1], .5)
        _, pool, personal = audit.audit_models(profiles, 'focal', 5)
        self.assertEqual(pool.points, personal.points)

    def test_pool_and_personal_use_equal_animal_and_day_weights(self):
        profiles = {'focal': balanced_profile([(1, 9), (1, 9), (2, 9)]),
                    'one': balanced_profile([(1, 0), (1, 0), (2, 2)]),
                    'two': WeightedDistribution([(4, 1)])}
        peer, pool, personal = audit.audit_models(profiles, 'focal', 3)
        self.assertEqual(dict(peer.points), {0: .25, 2: .25, 4: .5})
        expected_pool = {0: 1 / 6, 2: 1 / 6, 4: 1 / 3, 9: 1 / 3}
        for value, weight in pool.points:
            self.assertAlmostEqual(weight, expected_pool[value])
        expected_personal = {0: .15625, 2: .15625, 4: .3125, 9: .375}
        for value, weight in personal.points:
            self.assertAlmostEqual(weight, expected_personal[value])

    def test_persistent_profiles_reconcile_and_decompose_exactly(self):
        rows = constant_steps()
        primary, primary_internal = analyze_month_r(rows, 2018, 4, 1)
        result, internal = audit.analyze_month_audit(rows, 2018, 4, 1)
        check = audit.reconcile_primary(result, primary)
        self.assertLessEqual(check['max_absolute_score_difference'], 1e-11)
        self.assertEqual(internal['animals'], primary_internal['animals'])
        self.assertEqual(result['heldout_steps'], 180)
        self.assertEqual(result['heldout_animal_days'], 60)
        self.assertAlmostEqual(result['peer_CRPS'], 2)
        self.assertAlmostEqual(result['anonymous_pool_CRPS'], .5)
        self.assertAlmostEqual(result['personal_CRPS'], .125)
        self.assertAlmostEqual(result['original_peer_gain'], 1.875)
        self.assertAlmostEqual(result['identity_weight_gain'], .375)
        self.assertAlmostEqual(result['data_addition_gain'], 1.5)

    def test_unequal_days_and_samples_match_independent_double_sum(self):
        rows = []
        for animal in range(3):
            for day in range(1, 31):
                if day == animal + 1:
                    continue
                for index in range(2 if day % 5 == 0 else 3):
                    value = animal * .3 + (day % 4) * .2 + index * .1
                    rows.append(step(str(animal), day, index, value))
        result, _ = audit.analyze_month_audit(rows, 2018, 4, 1)
        daily = defaultdict(lambda: defaultdict(list))
        split = calendar.monthrange(2018, 4)[1] // 2
        for train_first in (True, False):
            train = [r for r in rows if (r.dt.day <= split) == train_first]
            test = [r for r in rows if (r.dt.day <= split) != train_first]
            profile, days = {}, {}
            for animal in ('0', '1', '2'):
                seq = [r for r in train if r.animal == animal]
                counts = Counter(r.day for r in seq)
                days[animal] = len(counts)
                profile[animal] = [(math.log1p(r.speed_kmh * 20),
                                    1 / len(counts) / counts[r.day]) for r in seq]
            pool = [(z, w / 3) for points in profile.values() for z, w in points]
            for row in test:
                peer = [(z, w / 2) for animal, points in profile.items()
                        if animal != row.animal for z, w in points]
                alpha = days[row.animal] / (days[row.animal] + 5)
                personal = ([(z, w * (1 - alpha)) for z, w in peer]
                            + [(z, w * alpha) for z, w in profile[row.animal]])
                y = math.log1p(row.speed_kmh * 20)
                daily[row.animal][row.day].append(
                    [brute_crps(points, y) for points in (peer, pool, personal)])
        for index, key in enumerate(('peer_CRPS', 'anonymous_pool_CRPS', 'personal_CRPS')):
            expected = math.fsum(
                math.fsum(math.fsum(s[index] for s in seq) / len(seq)
                          for seq in days.values()) / len(days)
                for days in daily.values()) / len(daily)
            self.assertAlmostEqual(result[key], expected, places=12)

    def test_training_donor_need_not_belong_to_final_test_cohort(self):
        rows = constant_steps()
        # This donor has 90 first-half steps and no heldout second-half support.
        # Its records still belong to the first-fold anonymous training pool.
        for day in range(1, 16):
            rows.extend(step('training_only', day, index % 3, 4) for index in range(6))
        primary, _ = analyze_month_r(rows, 2018, 4, 1)
        result, internal = audit.analyze_month_audit(rows, 2018, 4, 1)
        audit.reconcile_primary(result, primary)
        self.assertEqual(internal['animals'], {'0', '1'})
        first_fold = sum(brute_crps([(0, 1/3), (2, 1/3), (4, 1/3)], y)
                         for y in (0, 2)) / 2
        second_fold = .5
        self.assertAlmostEqual(result['anonymous_pool_CRPS'],
                               (first_fold + second_fold) / 2)

    def test_missing_second_fold_keeps_primary_nonestimable(self):
        rows = [r for r in constant_steps() if not (r.animal == '1' and r.dt.day > 15)]
        primary, _ = analyze_month_r(rows, 2018, 4, 1)
        result, internal = audit.analyze_month_audit(rows, 2018, 4, 1)
        audit.reconcile_primary(result, primary)
        self.assertEqual(internal['animals'], set())
        self.assertIsNone(result['identity_weight_gain'])
        self.assertEqual(result['heldout_steps'], 0)

    def test_reconciliation_rejects_changed_primary_scores_or_mask_counts(self):
        rows = constant_steps()
        primary, _ = analyze_month_r(rows, 2018, 4, 1)
        result, _ = audit.analyze_month_audit(rows, 2018, 4, 1)
        for key, delta in [('peer_CRPS', .001), ('heldout_steps', 1),
                           ('n_evaluated_animals', 1)]:
            changed = dict(primary)
            changed[key] += delta
            with self.assertRaises(AssertionError):
                audit.reconcile_primary(result, changed)

    def test_source_audit_reconciliation_respects_json_year_keys_and_counts(self):
        self.assertTrue(callable(getattr(audit, 'reconcile_source_audits', None)))
        primary = {'event_audit': {'retained_rows_by_year': {'2018': 10}},
                   'step_audit': {'retained_steps_by_year': {'2018': 8}}}
        events = {'retained_rows_by_year': {2018: 10}}
        steps = {'retained_steps_by_year': {2018: 8}}
        audit.reconcile_source_audits(events, steps, primary)
        with self.assertRaises(AssertionError):
            audit.reconcile_source_audits(events, {'retained_steps_by_year': {2018: 9}}, primary)

    def test_seasonal_gains_pair_same_animals_and_require_two_months(self):
        months = {1: {'a': .8, 'b': 7}, 2: {'a': .6},
                  6: {'a': .2, 'b': 8}, 7: {'a': .4}}
        components = {'original_peer_gain': months,
                      'identity_weight_gain': {m: {a: v / 4 for a, v in d.items()}
                                               for m, d in months.items()},
                      'data_addition_gain': {m: {a: 3 * v / 4 for a, v in d.items()}
                                              for m, d in months.items()}}
        result = audit.seasonal_audit(components)
        self.assertEqual(result['identity_weight_gain']['n_matched_animals'], 1)
        self.assertAlmostEqual(result['original_peer_gain']['winter_minus_summer_gain'], .4)
        self.assertAlmostEqual(result['identity_weight_gain']['winter_minus_summer_gain'], .1)
        self.assertAlmostEqual(result['data_addition_gain']['winter_minus_summer_gain'], .3)
        self.assertLessEqual(result['max_absolute_decomposition_error'], 1e-11)


if __name__ == '__main__':
    unittest.main()
