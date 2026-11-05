"""Synthetic behavioral contracts for pair-date-balanced geographic overlap."""
from __future__ import annotations

import importlib
import json
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deer_source_pipeline_v1 import Event

try:
    geography = importlib.import_module("deer_geography_v1")
except ModuleNotFoundError:
    geography = None


def event(animal, day, x_km, y_km=0.1, *, lat_cos=1.0):
    """Make a synthetic point away from grid boundaries; no source records."""
    return Event(animal=animal, tag="synthetic-tag", group="synthetic-group",
                 sex="f", life_stage="adult", deployment=0,
                 dt=datetime(2018, 1, 1) + timedelta(days=day),
                 lat=y_km / 111.32, lon=x_km / (111.32 * lat_cos))


def repeated(animal, days, x_km, fixes=1, y_km=0.1):
    return [event(animal, day, x_km, y_km) for day in days for _ in range(fixes)]


class DeerGeographyTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(geography, "deer geography implementation is missing")

    def compute(self, events, animals=("synthetic-a", "synthetic-b"), **kwargs):
        kwargs.setdefault("lat_cos", 1.0)
        return geography.compute_geography_overlap(events, animals, **kwargs)

    def first_overlap(self, report):
        return report["grids"][0]["overlap"]

    def test_identical_distributions_have_unit_overlap_at_all_default_grids(self):
        rows = repeated("synthetic-a", range(7), 0.1) + repeated("synthetic-b", range(7), 0.1)
        report, pairs = self.compute(rows)
        self.assertEqual(len(report["grids"]), 16)
        self.assertEqual((report["n_animals"], report["n_pairs_possible"], report["n_pairs_valid"]), (2, 1, 1))
        for grid in report["grids"]:
            self.assertEqual(grid["overlap"], {"mean": 1.0, "median": 1.0, "q25": 1.0,
                                               "q75": 1.0, "zero_fraction": 0.0})
        self.assertEqual(len(pairs), 16)
        self.assertEqual(pairs[(1.0, 0.0, 0.0)][("synthetic-a", "synthetic-b")], 1.0)

    def test_disjoint_distributions_have_zero_overlap(self):
        rows = repeated("synthetic-a", range(7), 0.1) + repeated("synthetic-b", range(7), 100.1)
        report, _ = self.compute(rows)
        for grid in report["grids"]:
            self.assertEqual(grid["overlap"]["mean"], 0.0)
            self.assertEqual(grid["overlap"]["zero_fraction"], 1.0)

    def test_known_partial_overlap_uses_probability_mass_intersection(self):
        rows = (repeated("synthetic-a", range(7), 0.1, 3) + repeated("synthetic-a", range(7), 2.1)
                + repeated("synthetic-b", range(7), 0.1) + repeated("synthetic-b", range(7), 2.1, 3))
        report, _ = self.compute(rows, scales_km=(1,), origins=((0, 0),))
        self.assertAlmostEqual(self.first_overlap(report)["mean"], 0.5)

    def test_daily_balance_prevents_fix_rich_date_dominating(self):
        rows = (repeated("synthetic-a", [0], 0.1, 100) + repeated("synthetic-a", [1], 2.1)
                + repeated("synthetic-b", [0, 1], 0.1, 3))
        report, _ = self.compute(rows, min_shared_days=2, scales_km=(1,), origins=((0, 0),))
        self.assertAlmostEqual(self.first_overlap(report)["mean"], 0.5)

    def test_pair_summary_weights_pairs_equally_and_uses_linear_quantiles(self):
        rows = (repeated("synthetic-a", range(7), 0.1)
                + repeated("synthetic-b", range(7), 0.1) + repeated("synthetic-b", range(7), 2.1)
                + repeated("synthetic-c", range(7), 2.1))
        report, _ = self.compute(rows, ("synthetic-a", "synthetic-b", "synthetic-c"),
                                 scales_km=(1,), origins=((0, 0),))
        overlap = self.first_overlap(report)
        self.assertAlmostEqual(overlap["mean"], 1 / 3)
        self.assertEqual((overlap["median"], overlap["q25"], overlap["q75"]), (0.5, 0.25, 0.5))
        self.assertAlmostEqual(overlap["zero_fraction"], 1 / 3)

    def test_both_occupancies_use_identical_pair_shared_dates(self):
        rows = (repeated("synthetic-a", range(7), 0.1) + repeated("synthetic-a", [7], 100.1, 100)
                + repeated("synthetic-b", range(7), 0.1))
        report, _ = self.compute(rows)
        self.assertEqual(self.first_overlap(report)["mean"], 1.0)
        self.assertEqual(report["shared_days_valid_pairs"]["median"], 7.0)

    def test_pair_specific_date_intersection_and_support_distribution(self):
        rows = (repeated("synthetic-a", range(13), 0.1) + repeated("synthetic-b", range(7), 0.1)
                + repeated("synthetic-c", range(7, 13), 0.1))
        report, pairs = self.compute(rows, ("synthetic-a", "synthetic-b", "synthetic-c"))
        self.assertEqual((report["n_pairs_possible"], report["n_pairs_valid"]), (3, 1))
        self.assertEqual(report["shared_days_all_pairs"]["min"], 0)
        self.assertEqual(report["shared_days_all_pairs"]["median"], 6.0)
        self.assertEqual(report["shared_days_all_pairs"]["max"], 7)
        self.assertEqual(set(pairs[(1.0, 0.0, 0.0)]), {("synthetic-a", "synthetic-b")})

    def test_insufficient_date_intersection_is_missing_not_zero_overlap(self):
        rows = repeated("synthetic-a", range(7), 0.1) + repeated("synthetic-b", range(1, 8), 0.1)
        report, pairs = self.compute(rows)
        self.assertEqual(report["n_pairs_valid"], 0)
        self.assertIsNone(self.first_overlap(report)["mean"])
        self.assertIsNone(self.first_overlap(report)["zero_fraction"])
        self.assertEqual(pairs[(1.0, 0.0, 0.0)], {})

    def test_zero_selected_and_absent_selected_animals_remain_auditable(self):
        empty, _ = self.compute([], ())
        self.assertEqual((empty["n_animals"], empty["n_pairs_possible"]), (0, 0))
        self.assertIsNone(empty["shared_days_all_pairs"]["median"])
        report, _ = self.compute(repeated("synthetic-a", range(7), 0.1))
        self.assertEqual((report["n_animals"], report["n_animals_observed"], report["n_pairs_possible"]), (2, 1, 1))
        self.assertEqual(report["shared_days_all_pairs"]["min"], 0)

    def test_grid_origin_shift_matches_translating_synthetic_points(self):
        rows = repeated("synthetic-a", range(7), 0.1) + repeated("synthetic-b", range(7), 0.9)
        report, pairs = self.compute(rows, scales_km=(1,), origins=((0, 0), (0.5, 0)))
        self.assertEqual(report["grids"][0]["overlap"]["mean"], 1.0)
        self.assertEqual(report["grids"][1]["overlap"]["mean"], 0.0)
        translated = repeated("synthetic-a", range(7), 0.6) + repeated("synthetic-b", range(7), 1.4)
        translated_report, _ = self.compute(translated, scales_km=(1,), origins=((0, 0),))
        self.assertEqual(translated_report["grids"][0]["overlap"], report["grids"][1]["overlap"])
        self.assertEqual(pairs[(1.0, 0.5, 0.0)][("synthetic-a", "synthetic-b")], 0.0)

    def test_negative_grid_coordinates_use_floor_and_fixed_latitude_cosine(self):
        rows = [event(animal, day, x, lat_cos=0.5)
                for animal, x in (("synthetic-a", -0.1), ("synthetic-b", 0.1)) for day in range(7)]
        report, _ = self.compute(rows, lat_cos=0.5, scales_km=(1,), origins=((0, 0),))
        self.assertEqual(self.first_overlap(report)["mean"], 0.0)
        rows = [event(animal, day, x, lat_cos=0.5)
                for animal, x in (("synthetic-a", 0.1), ("synthetic-b", 0.6)) for day in range(7)]
        report, _ = self.compute(rows, lat_cos=0.5, scales_km=(1,), origins=((0, 0),))
        self.assertEqual(self.first_overlap(report)["mean"], 1.0)

    def test_aggregate_is_json_safe_and_keeps_identities_internal(self):
        rows = repeated("synthetic-a", range(7), 0.1) + repeated("synthetic-b", range(7), 0.1)
        report, pairs = self.compute(iter(reversed(rows)), ("synthetic-b", "synthetic-a", "synthetic-a"))
        serialized = json.dumps(report, allow_nan=False)
        self.assertNotIn("synthetic-a", serialized)
        self.assertNotIn("synthetic-b", serialized)
        self.assertEqual(report["n_animals"], 2)
        self.assertIn(("synthetic-a", "synthetic-b"), pairs[(1.0, 0.0, 0.0)])

    def test_multiple_months_are_rejected_without_disclosing_records(self):
        rows = [event("synthetic-a", 0, 0.1), event("synthetic-a", 31, 0.1)]
        with self.assertRaisesRegex(ValueError, "one calendar month") as caught:
            self.compute(rows)
        self.assertNotIn("synthetic-a", str(caught.exception))

    def test_invalid_grid_or_support_parameters_are_rejected(self):
        for kwargs in ({"lat_cos": 0.0}, {"lat_cos": float("nan")},
                       {"scales_km": (0,)}, {"origins": ((1, 0),)}, {"min_shared_days": 0}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    self.compute([], **kwargs)


if __name__ == "__main__":
    unittest.main()
