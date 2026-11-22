import unittest
from datetime import datetime
from prospective.lunar_3d.lunar_height_score_v4 import (
    cat, score_height_records, keep_admitted_fixes,
    quality_ok, requalify_quality_rows, MAX_ABS_HEIGHT, add_numeric_height
)

class HeightScoreV4Tests(unittest.TestCase):
    @staticmethod
    def synthetic(n_animals=5):
        rows=[]
        dates=[("2026-11-10","bright",120.0),("2026-11-11","bright",120.0),
               ("2026-11-20","dark",-120.0),("2026-11-21","dark",-120.0)]
        for i in range(n_animals):
            key=(f"bat{i}","site","2026",10,20,5)
            for d,exp,z in dates:
                for f in range(12):
                    rows.append({"key":key,"animal":key[0],"night":d,"exposure":exp,
                                 "z":z+(f%3)-1,
                                 "height_raw_string":str(z),
                                 "hdop":"2","vdop":"3","dop":"2"})
        return rows
    def test_bin_boundaries(self):
        self.assertEqual(cat(-100),0)
        self.assertEqual(cat(-25),1)
        self.assertEqual(cat(25),2)
        self.assertEqual(cat(100),3)
        self.assertEqual(cat(101),4)
    def test_positive_synthetic_out_of_night(self):
        r=score_height_records(self.synthetic())
        self.assertEqual(r["scored_animals"],5)
        self.assertEqual(r["number_of_heldout_night_stratum_exposure_folds"],20)
        self.assertGreater(r["equal_animal_delta_nats_per_fix"],0.1)
        self.assertGreater(r["animal_bootstrap_95pct"][0],0)
    def test_no_imagined_animal_replicates(self):
        r=score_height_records(self.synthetic(n_animals=4))
        self.assertEqual(r["status"],"insufficient_scored_animals")
    def test_quality_thresholds(self):
        r={"hdop":"5","vdop":"8","dop":"8"}
        self.assertEqual(quality_ok(r,"10.5441/001/1.321"),(True,True))
        self.assertEqual(quality_ok(r,"10.5441/001/1.278"),(True,True))
        self.assertEqual(quality_ok({"hdop":"6","vdop":"1"},"10.5441/001/1.321"),(True,False))
        self.assertEqual(quality_ok({"dop":""},"10.5441/001/1.278"),(False,False))
    def test_numeric_quality_is_not_imputed(self):
        r=[{"height_raw_string":"NaN"}, {"height_raw_string":"123"}, {"height_raw_string":"20000"}]
        good,why=add_numeric_height(r)
        self.assertEqual(len(good),1)
        self.assertEqual(why["missing_or_nonfinite_numeric_height"],1)
        self.assertEqual(why["implausible_abs_gt_10000m"],1)

if __name__=="__main__":
    unittest.main()
