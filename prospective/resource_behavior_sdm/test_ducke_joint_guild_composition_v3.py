"""Only synthetic known-truth tests of the source-open multinomial engine."""
import unittest
from ducke_joint_guild_composition_v3 import GUILDS, fit_predict, grouped_cv, run

def fixture():
    result=[]
    for i in range(49):
        food=(i*7)%12
        n=20
        frug=max(0,min(16,round(4+food*1.05)))
        glean=max(1,14-frug)
        nectar=3
        aerial=n-frug-glean-nectar
        if aerial<1:
            aerial=1
            glean=n-frug-nectar-aerial
        result.append({
          "plot":"toy_"+str(i),"block":"PO" if i>=42 else "L"+str(3+i//7),
          "captures":n,"frug":frug,"glean":glean,"nectar":nectar,
          "aerial":aerial,"sanguivore":0,
          "elevation_m":60+i%12,"design_added_riparian_plot":i>=42,
          "n_matched_nights":1+i%3,
          "fruit_all":food+3,"fruit_batfood_12":food,"fruit_other":3
        })
    return result

class JointFourGuildTests(unittest.TestCase):
    def test_probability_simplex(self):
        x=fixture()
        v=fit_predict(x[:42],x[42:],("elevation_m","n_matched_nights"))
        self.assertEqual(len(v),7)
        self.assertTrue(all(abs(sum(p)-1.)<1e-12 for p in v))
        self.assertTrue(all(all(0.<=w<=1. for w in p) for p in v))
    def test_known_truth_batfood_predictive(self):
        d=fixture()
        # Override block identifiers to pass 7 group gate with 7 sites/group.
        for i,x in enumerate(d):
            x["block"]="block_"+str(i//7)
        a=grouped_cv(d)
        self.assertEqual(a["n_heldout_source_blocks"],7)
        self.assertGreater(a["equal_source_block_log_score_gain"]["candidate12_minus_baseline"],0)
        self.assertEqual(a["observed_4guild_captures"],980)
        self.assertEqual(a["excluded_sanguivore_captures"],0)
        self.assertIsNone(a["resource_conditioned_3D_animal_height_gain"])
    def test_no_invented_fifth_guild(self):
        x=fixture()
        x[0]["sanguivore"]=1
        with self.assertRaisesRegex(ValueError,"GUILD_SUM_OR_CAPTURE"):
            fit_predict(x[:42],x[42:],("elevation_m",))
    def test_bad_original_source_not_promoted(self):
        with self.assertRaisesRegex(ValueError,"ELIGIBILITY"):
            run(fixture())
    def test_missing_guild_class_stop(self):
        x=fixture()
        del x[0]["frug"]
        with self.assertRaises(ValueError):
            grouped_cv(x)

if __name__=="__main__":
    unittest.main()
