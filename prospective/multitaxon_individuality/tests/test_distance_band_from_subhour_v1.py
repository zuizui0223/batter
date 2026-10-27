"""Synthetic and original-source-aggregate contracts for disjoint GPS distance bands.

Only archived source/year aggregate input; NEVER raw GPS tracking records.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import distance_band_from_subhour_v1 as b


def synthetic_cumulatives(seed=3, n=2):
    distributions = {
        "winter": {0.5: (0.20, 0.10), 1.0: (0.35, 0.30), 2.0: (0.50, 0.60)},
        "summer": {0.5: (0.10, 0.15), 1.0: (0.30, 0.25), 2.0: (0.55, 0.50)},
    }
    idx = {}
    for radius in b.RADII:
        winter = distributions["winter"][radius]
        summer = distributions["summer"][radius]
        row = {
            "seed": seed, "radius_km": radius, "n_matched_dyads": n,
            "n_selected_dyad_dates": n*28,
            "n_selected_direct_fix_pairs": n*84,
            "winter_mean_abs_recording_gap_seconds": 3.5,
            "summer_mean_abs_recording_gap_seconds": 4.0,
        }
        for season, (o, null) in (("winter", winter), ("summer", summer)):
            row[season] = {"O": o, "N": null, "D": o-null}
        row["winter_minus_summer"] = {
            key: row["winter"][key]-row["summer"][key]
            for key in ("O", "N", "D")
        }
        idx[(seed, radius)] = row
    return idx


class TestDistanceBandArithmetic(unittest.TestCase):
    def test_disjoint_bands_equal_exact_manual_probability_partition(self):
        results = b._observed_seed_bands(synthetic_cumulatives(), 3, 2)
        self.assertEqual([row["band"] for row in results],
                         [name for name, _, _ in b.BANDS])
        w_d = [row["winter"]["D"] for row in results]
        s_d = [row["summer"]["D"] for row in results]
        for got, want in zip(w_d, (.10, -.05, -.15, .10)):
            self.assertAlmostEqual(got, want)
        for got, want in zip(s_d, (-.05, .10, 0, -.05)):
            self.assertAlmostEqual(got, want)
        self.assertAlmostEqual(math.fsum(row["winter"]["O"] for row in results), 1)
        self.assertAlmostEqual(math.fsum(row["summer"]["N"] for row in results), 1)
        self.assertAlmostEqual(math.fsum(row["winter_minus_summer_D"] for row in results), 0)

    def test_zero_sum_does_not_force_a_specific_negative_band(self):
        results = b._observed_seed_bands(synthetic_cumulatives(), 3, 2)
        self.assertGreater(results[0]["winter"]["D"], 0)
        self.assertLess(results[1]["winter"]["D"], 0)
        self.assertLess(results[2]["winter"]["D"], 0)
        self.assertGreater(results[3]["winter"]["D"], 0)

    def test_distance_radius_must_preserve_source_time_and_pair_mask(self):
        for changed in (
            ("n_matched_dyads", 3),
            ("n_selected_dyad_dates", 13),
            ("n_selected_direct_fix_pairs", 11),
            ("winter_mean_abs_recording_gap_seconds", 5.0),
        ):
            with self.subTest(changed=changed):
                x = synthetic_cumulatives()
                x[(3, 2.)][changed[0]] = changed[1]
                with self.assertRaises(AssertionError):
                    b._observed_seed_bands(x, 3, 2)

    def test_rejects_nonmonotone_radius_and_source_O_minus_N_drift(self):
        x = synthetic_cumulatives()
        x[(3,1.)]["winter"]["O"] = .01
        with self.assertRaises(AssertionError):
            b._observed_seed_bands(x, 3, 2)
        x = synthetic_cumulatives()
        x[(3,.5)]["winter"]["D"] += .01
        with self.assertRaises(AssertionError):
            b._observed_seed_bands(x, 3, 2)

    def test_summary_counts_and_null_semantics(self):
        row = b._observed_seed_bands(synthetic_cumulatives(), 3, 2)
        all_seeds = [{**item, "seed": seed} for seed in b.SEEDS for item in row]
        summary = b._summary(all_seeds, b.BANDS[0][0])
        self.assertEqual(summary["n_seeds"], 12)
        self.assertEqual(summary["delta_D_seed_signs"], {"positive":12,"negative":0,"near_zero":0})
        self.assertAlmostEqual(summary["winter_minus_summer_D"], .15)
        with self.assertRaises(AssertionError):
            b._summary(all_seeds[:-4], b.BANDS[0][0])

    def test_signed_classification_handles_zero_and_negative(self):
        self.assertEqual(b.signed([0, -1, 1e-15, 2]),
                         {"positive":1, "negative":1, "near_zero":2})

    def test_archived_original_source_sha_recomputed_and_complete(self):
        data = b.derive()
        self.assertEqual(data["n_valid_source_year_tolerance_groups"], 10)
        self.assertEqual(data["n_stopped_source_year_tolerance_groups"], 2)
        self.assertEqual(data["n_seed_band_records"], 480)
        self.assertEqual(data["n_summary_band_records"], 40)
        self.assertEqual(len(data["source_years"]), 12)
        for cohort in data["source_years"]:
            if cohort["status"].startswith("DESCRIPTIVE_"):
                self.assertEqual(len(cohort["seed_band_records"]), 48)
                self.assertEqual(len(cohort["band_summary"]), 4)
            else:
                self.assertFalse(cohort["seed_band_records"])
                self.assertFalse(cohort["band_summary"])

    def test_fine_radius_whitetail_pattern_and_controls_from_actual_archived_aggregates(self):
        data = b.derive()
        for year in (2019, 2020):
            for gap in (900, 1800):
                cohort = next(
                    row for row in data["source_years"]
                    if (row["source"], row["year"], row["max_abs_timestamp_gap_seconds"])
                       == ("white_tailed_deer", year, gap)
                )
                near, intermediate = cohort["band_summary"][0], cohort["band_summary"][2]
                # This is descriptive inspection of the same two source-year
                # panels already studied, NOT an inferential test.
                self.assertLess(near["winter"]["O"], near["summer"]["O"])
                self.assertGreater(near["winter"]["D"], 0)
                self.assertLess(intermediate["winter"]["D"], 0)
                self.assertEqual(near["delta_D_seed_signs"]["positive"], 12)
                # Source check: deer 2019 at 30 minutes has 11 negative
                # sampling contrasts and one positive. Do not overstate
                # the 15-minute 12/12 reference as a universal result.
                expected_negative = 11 if (year, gap) == (2019, 1800) else 12
                self.assertEqual(intermediate["delta_D_seed_signs"]["negative"],
                                 expected_negative)

    def test_same_observed_mean_and_different_temporal_null_differ_by_band(self):
        # Equal observed winter/summer locations do not entail equal
        # conditional time-pairing surpluses.
        x=synthetic_cumulatives()
        winter = x[(3,.5)]["winter"]
        summer = x[(3,.5)]["summer"]
        self.assertNotEqual(winter["O"]-winter["N"], summer["O"]-summer["N"])

    def test_recursive_result_validation_detects_changed_aggregate_value(self):
        x = b.derive()
        b._recursive_check(x, x)
        corrupted = deepcopy(x)
        corrupted["source_years"][0]["band_summary"][0]["winter"]["D"] += .001
        with self.assertRaises(AssertionError):
            b._recursive_check(corrupted, x)


if __name__ == "__main__":
    unittest.main()
