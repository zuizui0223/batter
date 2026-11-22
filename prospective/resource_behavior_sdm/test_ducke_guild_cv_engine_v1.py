"""Known-truth software tests only; no original Ducke bat or plant rows."""
import unittest
from ducke_guild_cv_engine_v1 import grouped_cv,predict

def world():
    result=[]
    for j in range(49):
        n=(j*7)%12
        a=round(20*(.13+.068*n))
        result.append({"plot":"toy_"+str(j),"block":"block_"+str(j//7),
                       "captures":20,"frug":a,"design_added_riparian_plot":j>29,
                       "elevation_m":70+(j%5)*8,"n_matched_nights":1+j%3,
                       "fruit_batfood_12":n,"fruit_all":n+3,"fruit_other":3,
                       "insect_mass_g":2+(j%7)*.6})
    return result

class DuckeOriginalSourceFreeTest(unittest.TestCase):
    def test_heldout_food_can_be_predictive_without_raw_source(self):
        v=grouped_cv(world())
        self.assertEqual(v["n_folds"],7)
        self.assertGreater(v["equal_fold_gains"]["food_12"],0.)
        self.assertFalse(v["raw_source_rows_or_coordinates_included"])
        self.assertIsNone(v["empirical_5D_resource_height_gain"])
    def test_leave_plot_is_not_independent_external_region(self):
        v=grouped_cv(world(),heldout="plot")
        self.assertEqual(v["n_folds"],49)
        self.assertEqual(v["folds_without_identifiers"],[])
    def test_missing_food_is_not_imputed_zero(self):
        x=world()
        del x[0]["fruit_batfood_12"]
        with self.assertRaisesRegex(ValueError,"MISSING_SOURCE_PREDICTOR"):
            grouped_cv(x)
    def test_duplicate_sample_unit_and_bad_response_stop(self):
        x=world()
        x[0]["plot"]=x[1]["plot"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PLOT"):
            grouped_cv(x)
        x=world()
        x[0]["frug"]=21
        with self.assertRaisesRegex(ValueError,"UNKNOWN_GUILD_DENOMINATOR"):
            grouped_cv(x)

if __name__=="__main__":
    unittest.main()
