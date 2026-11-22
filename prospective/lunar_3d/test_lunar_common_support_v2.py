from collections import Counter
import unittest

from prospective.lunar_3d.lunar_common_support_v2 import summarize

class CommonSupportTests(unittest.TestCase):
    def make_counts(self, n=5, far=False):
        bright = Counter({"2026-11-10": 10, "2026-11-11": 10})
        if far:
            dark = Counter({"2022-01-10": 10, "2022-01-11": 10})
        else:
            dark = Counter({"2026-11-20": 10, "2026-11-21": 10})
        return {(f"bat-{i}", 111, 222, 10): {"bright": bright, "dark": dark} for i in range(n)}
    def test_repeated_within_month_matched(self):
        r = summarize(self.make_counts(5))
        self.assertEqual(r["matched_individuals"], 5)
        self.assertTrue(r["matched_support_pass"])
        self.assertEqual(r["matched_strata"], 5)
    def test_reject_cross_year_false_match(self):
        r = summarize(self.make_counts(5, far=True))
        self.assertEqual(r["matched_individuals"], 0)
        self.assertFalse(r["matched_support_pass"])
    def test_no_five_individuals(self):
        self.assertFalse(summarize(self.make_counts(4))["matched_support_pass"])

if __name__ == "__main__":
    unittest.main()
