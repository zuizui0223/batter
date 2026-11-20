"""Synthetic only. No Hendel source animal or prey data in test suite."""
import unittest
from hendel_heldout_prey_activity_v1 import (
    BASE,TARGETS,MODELS,CONTRASTS,validate_original_source_rows,
    evaluate_heldout_sites,
)


def synthetic():
    rows=[]
    for i in range(64):
        moth=float((i*13)%41)
        beetle=float((i*17)%23)
        forest=float((i*3)%20)/19
        rows.append({
            "plotID":"fictional_"+str(i),
            "elevation":500+11*(i%9),"DOY":130+(i*7)%80,
            "temp_min":4.+i%7,"Opn_mean":forest,
            "ndsm_sd":2.+i%13,"ForMI":float(i%5)/5,
            "mothcount":moth,"moth_richness":float((i*11)%19),
            "carabidae":beetle,"carabidae_S":float((i*5)%12),
            "SRE":1.0+10*moth,"MRE":1.+i%13,
            "Ppip":2.+i%11,"LRE":1.+7*beetle
        })
    return rows


class ForestResourceTransferTests(unittest.TestCase):
    def test_64_sites_and_two_independent_resource_channels(self):
        result=evaluate_heldout_sites(synthetic())
        self.assertEqual(result["n_source_sites"],64)
        self.assertEqual(len(result["source_guild_channels"]),4)
        self.assertGreater(result["per_guild_equal_site_gain"]["SRE"]["moth_abundance_given_forest"],0)
        self.assertGreater(result["per_guild_equal_site_gain"]["LRE"]["beetle_abundance_given_forest"],0)
        self.assertFalse(result["Ducke_2018_original_4guild_log_score_directly_comparable"])
        self.assertFalse(result["geographically_independent_test"])
        self.assertIsNone(result["resource_conditioned_individual_3D_height_gain"])
    def test_target_is_not_a_mistnet_count_or_normalized_guild_share(self):
        r=evaluate_heldout_sites(synthetic())
        self.assertFalse(r["acoustic_guilds_are_mutually_exclusive"])
        self.assertTrue(r["guild_activity_is_not_population_abundance"])
        self.assertIn("moth_richness_given_abundance",CONTRASTS)
    def test_original_grain_or_missing_prey_causes_stop(self):
        x=synthetic()
        x[0]["plotID"]=x[1]["plotID"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OR_REUSED"):
            validate_original_source_rows(x)
        x=synthetic()
        del x[0]["mothcount"]
        with self.assertRaisesRegex(ValueError,"FIELD_MISSING"):
            validate_original_source_rows(x)
    def test_negative_activity_and_small_sites_stop(self):
        x=synthetic()
        x[3]["SRE"]=-1
        with self.assertRaisesRegex(ValueError,"NEGATIVE_PREY_OR_ACTIVITY"):
            validate_original_source_rows(x)
        with self.assertRaisesRegex(ValueError,"N_SOURCE_TOO_SMALL"):
            evaluate_heldout_sites(synthetic()[:12])


if __name__=="__main__":
    unittest.main()
