import math
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deer_seasonal_rx_v1 import (
    WeightedDistribution, balanced_profile, peer_distribution,
    analyze_month_r, select_constant_cohort, seasonal_pair_contrast,
)


def synthetic_steps(reverse=False, identical=False):
    rows = []
    for a in range(2):
        for day in range(1, 31):
            speed = 0.1 if identical else float(a)
            if reverse and day > 15:
                speed = 1 - speed
            for hour in (0, 2, 4):
                dt = datetime(2018, 4, day, hour)
                rows.append(SimpleNamespace(animal=str(a), day=dt.toordinal(),
                    year=2018, month=4, dt=dt, hour_bin=0,
                    lon=0.001, lat=0.001, speed_kmh=speed))
    return rows


class TestWeightedScores(unittest.TestCase):
    def test_exact_weighted_crps(self):
        f = WeightedDistribution([(0, .2), (1, .3), (4, .5)])
        self.assertAlmostEqual(f.crps(2), .79)

    def test_mixture_uses_dispersion_cross_term(self):
        f = WeightedDistribution.mixture([
            (WeightedDistribution([(0, 1)]), .7),
            (WeightedDistribution([(2, 1)]), .3)])
        self.assertAlmostEqual(f.crps(0), .18)
        self.assertAlmostEqual(f.crps(1), .58)
        self.assertAlmostEqual(f.crps(2), .98)

    def test_unequal_sampling_has_equal_day_mass(self):
        f = balanced_profile([(1, 0), (1, 0), (1, 0), (2, 2)])
        self.assertAlmostEqual(f.mean, 1)
        self.assertAlmostEqual(f.crps(1), .5)

    def test_peer_pool_excludes_self_and_equal_weights_donors(self):
        profiles = {
            'target': WeightedDistribution([(100, 1)]),
            'a': WeightedDistribution([(0, 1)]),
            'b': WeightedDistribution([(4, 1), (4, 1), (4, 1)])}
        p = peer_distribution(profiles, 'target')
        self.assertAlmostEqual(p.mean, 2)
        self.assertAlmostEqual(p.crps(2), 1)

    def test_invalid_weights_fail(self):
        for pairs in ([], [(1, -1)], [(1, 0)], [(math.nan, 1)]):
            with self.assertRaises(ValueError):
                WeightedDistribution(pairs)


class TestCrossFit(unittest.TestCase):
    def test_identical_profiles_no_gain(self):
        report, internal = analyze_month_r(synthetic_steps(identical=True), 2018, 4, 1)
        self.assertEqual(report['n_evaluated_animals'], 2)
        self.assertAlmostEqual(report['R_gain'], 0)
        self.assertTrue(report['calendar_separation_verified'])
        self.assertEqual(report['heldout_steps'], 180)
        self.assertEqual(len(internal['animals']), 2)

    def test_persistent_identity_improves_score(self):
        report, _ = analyze_month_r(synthetic_steps(), 2018, 4, 1)
        self.assertGreater(report['R_gain'], 0)
        self.assertLess(report['personal_CRPS'], report['peer_CRPS'])

    def test_reversed_profiles_are_worse(self):
        report, _ = analyze_month_r(synthetic_steps(reverse=True), 2018, 4, 1)
        self.assertLess(report['R_gain'], 0)

    def test_one_fold_absent_is_not_final_cohort(self):
        rows = [r for r in synthetic_steps() if not (r.animal == '1' and r.dt.day > 15)]
        report, internal = analyze_month_r(rows, 2018, 4, 1)
        self.assertEqual(report['n_evaluated_animals'], 0)
        self.assertIsNone(report['R_gain'])
        self.assertEqual(internal['animals'], set())


class TestStableContrasts(unittest.TestCase):
    def test_constant_cohort_requires_every_month(self):
        events = []
        for month in range(1, 13):
            for animal in ('all', 'partial'):
                if animal == 'partial' and month == 8:
                    continue
                for day in range(1, 11):
                    for hour in range(8):
                        dt = datetime(2018, month, day, hour)
                        events.append(SimpleNamespace(animal=animal, year=2018,
                            month=month, day=dt.toordinal()))
        self.assertEqual(select_constant_cohort(events, 2018), {'all'})

    def test_seasonal_contrast_pairs_before_averaging(self):
        pair = ('a', 'b')
        other = ('b', 'c')
        months = {1:{pair:.8, other:.3}, 2:{pair:.6}, 6:{pair:.2}, 7:{pair:.4}}
        r = seasonal_pair_contrast(months)
        self.assertEqual(r['n_pairs'], 1)
        self.assertAlmostEqual(r['winter_minus_summer_mean'], .4)
        self.assertAlmostEqual(r['winter_mean'], .7)
        self.assertAlmostEqual(r['summer_mean'], .3)

    def test_missing_season_is_not_zero(self):
        r = seasonal_pair_contrast({1:{('a','b'):.7}, 2:{('a','b'):.7}})
        self.assertEqual(r['n_pairs'], 0)
        self.assertIsNone(r['winter_minus_summer_mean'])


if __name__ == '__main__':
    unittest.main()
