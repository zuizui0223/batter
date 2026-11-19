"""Known-truth source-hierarchy tests for 2018 vampire maze reanalysis.

Synthetic ONLY. Real original Figshare source SHA verified and reanalyzed in
its separate workflow; no raw identifiers or rows are stored in the repo.
"""
import unittest
from unittest.mock import patch
import h1_vampire2018_original_reanalysis_v1 as mod

class TestOriginalPhaseHierarchy(unittest.TestCase):
    def synthetic_original(self):
        rows=[]
        for i in range(12):
            # 104 original demonstrator training attempts split across 12 bats
            reps=9 if i<8 else 8
            for attempt in range(reps):
                rows.append({"experiment":"train","trial ":str(100+len(rows)),
                    "bat":f"d{i}","demonstrator":"T","phase":"train",
                    "attempt":str(attempt+1),"latency":"","latency2":"",
                    "exit.in.15":"F","naive":"F"})
        self.assertEqual(len(rows),104)
        for i in range(24):
            for stage in ("1pre","2test","3post"):
                win=(stage=="2test" and i<5) or (stage=="3post" and (i<4 or i==5))
                exp_naive="F" if stage=="2test" and i==23 else "T"
                rows.append({"experiment":"test","trial ":str(
                    (i//3) if stage!="2test" else 1000+i//2),
                    "bat":f"n{i}","demonstrator":"F","phase":stage,
                    "attempt":"1","latency":"","latency2":"",
                    "exit.in.15":"T" if win else "F",
                    "naive":exp_naive})
        for i in range(12):
            rows.append({"experiment":"test","trial ":str(1000+i),
                "bat":f"d{i}","demonstrator":"T","phase":"2test",
                "attempt":"1","latency":"","latency2":"",
                "exit.in.15":"T","naive":"F"})
        self.assertEqual(len(rows),188)
        return rows

    def test_24_naive_roles_but_23_exposure_naive_eligible(self):
        with patch.object(mod,"read_original",return_value=(self.synthetic_original(),b"")):
            a=mod.aggregate()
        self.assertEqual(a["original_n_rows"],188)
        self.assertEqual(a["naive_bat_count"],24)
        self.assertEqual(a["n_training_demonstrator_bats"],12)
        self.assertEqual(a["phase_naive_records"]["2test"]["raw_naive_rows"],24)
        self.assertEqual(a["during_original_status_F_n"],1)
        self.assertEqual(a["during_exit_valid_naive_n"],23)
        self.assertEqual(a["during_exit_positive_naive_n"],5)
        self.assertEqual(a["after_demonstrator_retention_positive_n"],4)
        self.assertEqual(a["after_demonstrator_retention_fraction"],0.8)
        self.assertTrue(a["published_pre_0_24_consistent"])
        self.assertTrue(a["published_during_5_23_consistent"])
        self.assertTrue(a["published_four_of_five_retained_consistent"])
        self.assertEqual(a["individual_pre_post_transition_table"]["F->T"],5)
        self.assertEqual(a["individual_pre_post_transition_table"]["F->F"],19)
        self.assertFalse(a["claim_boundary"]["individual_trial_rows_committed"])

    def test_original_experienced_bat_not_falsely_naive_even_if_exits(self):
        rows=self.synthetic_original()
        for r in rows:
            if r["bat"]=="n23" and r["phase"]=="2test":
                r["exit.in.15"]="T"
        with patch.object(mod,"read_original",return_value=(rows,b"")):
            a=mod.aggregate()
        self.assertEqual(a["during_status_F_exit_true_n"],1)
        self.assertEqual(a["during_exit_positive_naive_n"],5)
        self.assertEqual(a["during_exit_valid_naive_n"],23)

    def test_fail_when_unique_naive_subject_row_missing(self):
        rows=self.synthetic_original()
        rows=[r for r in rows if not (r["bat"]=="n23" and r["phase"]=="3post")]
        with patch.object(mod,"read_original",return_value=(rows,b"")):
            with self.assertRaisesRegex(ValueError,"Naive phase counts changed"):
                mod.aggregate()

if __name__=="__main__":
    unittest.main()
