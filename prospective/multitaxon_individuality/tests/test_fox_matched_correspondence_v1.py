"""Behavioral invariants for conditional whole-profile correspondence references."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def module():
    spec = importlib.util.spec_from_file_location("fox_matched_correspondence_v1", ROOT / "fox_matched_correspondence_v1.py")
    if spec is None or spec.loader is None or not (ROOT / "fox_matched_correspondence_v1.py").exists():
        raise AssertionError("The correspondence implementation is not present")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class MappingReferenceTests(unittest.TestCase):
    def test_missing_donor_support_cannot_create_identity_evidence(self):
        m = module()
        out = m.mapping_reference([[2.0, None], [None, 3.0]], [[True, False], [False, True]])
        self.assertEqual(out["n_admissible_maps"], 1)
        self.assertEqual(out["n_movable_animals"], 0)
        self.assertIsNone(out["tail_fraction"])
        self.assertEqual(out["status"], "NOT_CALIBRATABLE_IDENTITY_ONLY")

    def test_known_correspondence_has_all_twenty_four_maps(self):
        m = module()
        scores = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
        out = m.mapping_reference(scores, [[True] * 4 for _ in range(4)])
        self.assertEqual(out["n_admissible_maps"], 24)
        self.assertAlmostEqual(out["observed_gain"], 1.0)
        self.assertAlmostEqual(out["reference_mean_gain"], .25)
        self.assertAlmostEqual(out["excess_over_reference"], .75)
        self.assertAlmostEqual(out["tail_fraction"], 1 / 24)
        self.assertEqual(out["n_movable_animals"], 4)

    def test_identical_profiles_do_not_create_gain(self):
        m = module()
        out = m.mapping_reference([[.2] * 4 for _ in range(4)], [[True] * 4 for _ in range(4)])
        self.assertAlmostEqual(out["excess_over_reference"], 0)
        self.assertEqual(out["tail_fraction"], 1)

    def test_reversed_correspondence_is_not_positive_identity(self):
        m = module()
        out = m.mapping_reference([[0, 1], [1, 0]], [[True] * 2 for _ in range(2)])
        self.assertLess(out["excess_over_reference"], 0)
        self.assertEqual(out["tail_fraction"], 1)
        self.assertEqual(out["status"], "DESCRIPTIVE_LOW_MAPPING_RESOLUTION")

    def test_allowed_edge_outside_perfect_matching_does_not_mark_movable(self):
        m = module()
        out = m.mapping_reference([[0, 5], [None, 0]], [[True, True], [False, True]])
        self.assertEqual(out["n_movable_animals"], 0)

    def test_calendar_split_does_not_depend_on_animal_start_date(self):
        m = module()
        a = [{"animal": "a", "day": f"2020-05-{d:02}", "month": "2020-05"} for d in (1, 15, 16, 31)]
        b = [{"animal": "b", "day": f"2020-05-{d:02}", "month": "2020-05"} for d in (14, 15, 16, 29)]
        train, test = m.calendar_split(a + b, "2020-05")
        self.assertEqual({x["day"] for x in train} & {x["day"] for x in test}, set())
        self.assertTrue(all(x["day"] <= "2020-05-15" for x in train))
        self.assertTrue(all(x["day"] >= "2020-05-16" for x in test))

    def test_day_weighting_is_not_fix_weighting(self):
        m = module()
        self.assertAlmostEqual(m.day_mean([("day1", 1.0)] + [("day2", 0.0)] * 9), .5)

    def test_activity_threshold_requires_both_axes(self):
        m = module()
        self.assertEqual(m.outcome({"activity_x": 2, "activity_y": 2}, "activity"), 1)
        self.assertEqual(m.outcome({"activity_x": 10, "activity_y": 1}, "activity"), 0)
        self.assertIsNone(m.outcome({"activity_x": None, "activity_y": 5}, "activity"))

    def test_matched_geography_distinguishes_absent_opportunity_from_zero(self):
        m = module()
        rows = [{"animal": animal, "day": f"2020-05-{d:02}", "month": "2020-05",
                 "lat": .001, "lon": .001}
                for animal in ("a", "b") for d in (16, 17, 18)]
        same = m.matched_x(rows, ["a", "b"], "2020-05", 1)
        self.assertEqual(same["n_supported_dependent_dyads"], 1)
        self.assertAlmostEqual(same["scales"][1]["mean_overlap"], 1)
        disjoint = [dict(r, lon=1.0) if r["animal"] == "b" else r for r in rows]
        different = m.matched_x(disjoint, ["a", "b"], "2020-05", 1)
        self.assertEqual(different["scales"][1]["mean_overlap"], 0)
        sparse = [r for r in rows if not (r["animal"] == "b" and r["day"].endswith("18"))]
        missing = m.matched_x(sparse, ["a", "b"], "2020-05", 1)
        self.assertEqual(missing["n_dyads_missing_shared_date_support"], 1)
        self.assertIsNone(missing["scales"][1]["mean_overlap"])

    def test_geographic_occupancy_weights_days_not_number_of_fixes(self):
        m = module()
        a = [{"day": "d1", "lat": .001, "lon": .001}] * 99
        a += [{"day": "d2", "lat": .001, "lon": 1.0}]
        hist = m.occupancy(a, 1.0, 1)
        self.assertAlmostEqual(hist[(0, 0)], .5)
        self.assertAlmostEqual(sum(hist.values()), 1)


if __name__ == "__main__":
    unittest.main()
