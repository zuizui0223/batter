"""Source-free known-truth challenge tests for candidate fruit specificity."""
import unittest
from ducke_resource_specificity_v2 import MODELS, _evaluate


def fake():
    rows=[]
    for i in range(49):
        food=(i*7)%12; other=(i*3)%10
        n=round(20*(.2+.05*food))
        rows.append({
            "plot":"sim_"+str(i),"block":"group_"+str(i//7),"captures":20,
            "frug":n,"glean":20-n,"nectar":0,
            "elevation_m":60+i%11,"design_added_riparian_plot":i>=28,
            "n_matched_nights":1+i%3,
            "fruit_batfood_12":food,"fruit_other":other,
            "fruit_all":food+other,
        })
    return rows


class ResourceSpecificityTests(unittest.TestCase):
    def test_exact_predefined_comparisons_and_no_original_rows(self):
        self.assertEqual(set(MODELS),{
            "baseline","food12","other10","food12_and_other10","all22_sum"})
        r=_evaluate(fake(),"frug")
        self.assertEqual(r["n_outer_groups"],7)
        self.assertEqual(r["n_source_plots"],49)
        self.assertTrue(r["group_equal_mean"]["food_minus_baseline"]>0)
        self.assertFalse(r["source_ids_or_positions_stored"])
        self.assertNotIn("plot",r["fold_ordinal_only"][0])
    def test_same_data_splits_for_each_nested_comparison(self):
        r=_evaluate(fake(),"frug")
        for x in r["fold_ordinal_only"]:
            v=x["contrasts"]
            self.assertAlmostEqual(
                v["both_minus_baseline"]-v["food_minus_baseline"],
                v["other_given_food"],places=12)
            self.assertAlmostEqual(
                v["both_minus_baseline"]-v["other_minus_baseline"],
                v["food_given_other"],places=12)
    def test_no_missing_or_duplicate_plot_rescue(self):
        r=fake();r[0]["plot"]=r[1]["plot"]
        with self.assertRaisesRegex(ValueError,"DUPLICATED"):
            _evaluate(r,"frug")
        r=fake();del r[0]["fruit_other"]
        with self.assertRaises(ValueError):
            _evaluate(r,"frug")

if __name__=="__main__":
    unittest.main()
