"""Source-free unit tests for the original Ducke import contract."""
import unittest
from ducke_original_adapter_v1 import canon_site,parse_source_date,FOOD12

class AdapterContractTests(unittest.TestCase):
    def test_aliases_are_exact_and_reversible(self):
        self.assertEqual(canon_site("L3_0500"),canon_site("LO3_0500"))
        self.assertEqual(canon_site("PO1"),canon_site("PO_01"))
        self.assertEqual(canon_site("PO19"),"PO_19")
        with self.assertRaisesRegex(ValueError,"UNRECOGNIZED"):
            canon_site("invented")
    def test_dates_must_not_be_guessed_or_shifted(self):
        self.assertEqual(parse_source_date("01_13_2015").year,2015)
        with self.assertRaisesRegex(ValueError,"MALFORMED"):
            parse_source_date("2014-13-01")
    def test_published_potential_food_subset_fixed(self):
        self.assertEqual(len(FOOD12),12)
        self.assertIn("Piper",FOOD12)
        self.assertIn("Peperomia",FOOD12)
        self.assertNotIn("Not_identified",FOOD12)

if __name__=="__main__":
    unittest.main()
