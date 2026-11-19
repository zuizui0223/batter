"""No-network source + claim boundary test for two archived bat studies.

The original raw spreadsheets are NOT present in GitHub; their SHA/MD5 were
verified in a source-reading CI. Here we only check stored derived contrasts.
"""
import json
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
FILE=HERE/"H1_TWO_DISTRESS_ORIGINAL_RECEIPT_V1.json"

class TestDistressContextAggregate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=json.loads(FILE.read_text(encoding="utf-8"))

    def test_both_origins_verified_no_raw_data_in_git(self):
        r=self.r
        self.assertEqual(r["status"],"TWO_ORIGINAL_SOURCES_AUTHENTICATED_REANALYSIS_COMPLETE")
        self.assertTrue(r["based_on_published_prior_art"])
        self.assertFalse(r["raw_original_sources_committed"])
        self.assertEqual(r["source_2016"]["original_xlsx_sha256"],
            "28402ac6c969f7a6c13acf5f90192afbfa4b6c5158e1bbc8f657b55f255b05ef")
        self.assertEqual(r["source_2015"]["original_csv_md5"],
            "991be124c47f48a955fa5a0a40dd864c")

    def test_2016_design_and_arithmetic(self):
        x=self.r["source_2016"]
        self.assertEqual((x["original_data_rows"],x["original_session_labels"],x["published_physical_colonies"]),(114,19,11))
        m=x["means_by_location"]
        s="S. bilineata"; t="M. molossus"
        delta=(m["within"][s]-m["within"][t])-(m["foraging"][s]-m["foraging"][t])
        self.assertAlmostEqual(delta,x["withinsession_conspecific_minus_heterospecific_by_location_within_minus_foraging"]["mean"])
        near=(m["close"][s]-m["close"][t])-(m["foraging"][s]-m["foraging"][t])
        self.assertAlmostEqual(near,x["nearroost_minus_foraging_call_specificity"]["mean"])
        self.assertEqual(x["withinsession_conspecific_minus_heterospecific_by_location_within_minus_foraging"]["positive_sessions"],14)
        self.assertTrue(x["missing_physical_colony_to_session_crosswalk"])

    def test_unknown_eight_pairs_three_singles_bounds_have_robust_sign(self):
        x=self.r["source_2016"]
        for key in ["withinsession_conspecific_minus_heterospecific_by_location_within_minus_foraging",
                    "nearroost_minus_foraging_call_specificity",
                    "conspecific_only_roost_minus_foraging"]:
            d=x[key];lo,hi=d["physical_colony_equal_mean_partial_identification_bounds"]
            self.assertLess(lo,d["mean"])
            self.assertGreater(hi,d["mean"])
            self.assertGreater(lo,0)
            self.assertGreater(hi,0)
        # Known-truth algebra for 8 paired colony observations + 3 singletons:
        source=[float(i) for i in range(-9,10)] # n=19
        lo=(sum(source)+sum(sorted(source)[:3]))/22
        hi=(sum(source)+sum(sorted(source)[-3:]))/22
        for singles in ([0,1,2],[3,7,18],[16,17,18]):
            rest=[j for j in range(19) if j not in singles]
            colony_means=[source[j] for j in singles]+[
                (source[rest[i]]+source[rest[i+1]])/2 for i in range(0,16,2)]
            v=sum(colony_means)/11
            self.assertLessEqual(lo-1e-12,v)
            self.assertGreaterEqual(hi+1e-12,v)

    def test_2015_two_recipient_hierarchy_and_no_meta(self):
        x=self.r["source_2015"]
        self.assertEqual((x["original_trials"],x["distress_trials"],x["noise_trials"]),(308,155,153))
        self.assertEqual((x["session_labels"],x["published_field_sites"]),(12,8))
        self.assertTrue(x["unmapped_site_ids"])
        self.assertAlmostEqual(x["recipients"]["M. molossus"]["session_mean_distress_minus_noise"],0.549361270985985)
        self.assertAlmostEqual(x["recipients"]["S. bilineata"]["session_mean_distress_minus_noise"],0.25371248644990063)
        self.assertEqual(x["recipients"]["M. molossus"]["positive_sessions"],9)
        self.assertEqual(x["recipients"]["S. bilineata"]["positive_sessions"],6)
        self.assertEqual(x["recipients"]["M. molossus"]["original_authors_nonzero_filter_retained"],116)
        self.assertEqual(x["recipients"]["S. bilineata"]["original_authors_nonzero_filter_retained"],59)
        self.assertIn("STOP",self.r["generalization"])
        self.assertFalse(self.r["h1_2019_buzz_density_exact_replication"])

if __name__=="__main__":
    unittest.main()
