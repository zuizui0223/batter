"""Synthetic structural-key-only and original blob STOP controls."""
import unittest
from dryad_rous_author_source_keys import ALLOW,KEYS,key_rows_only,key_stats

class AuthorKeyGateTest(unittest.TestCase):
    def test_source_allowlist(self):
        self.assertEqual(len(ALLOW),4)
        self.assertEqual(ALLOW["Field_Manipulation_Table.csv"][0],291)
        self.assertEqual(ALLOW["visits_to_f.sycamorus.csv"][0],197784)

    def test_outcome_columns_not_selected(self):
        all_keys={k for subset in KEYS.values() for k in subset}
        for outcome in ("Visited","n_visited_North_Tree","n_visited_either_tree",
                        "time_of_visit","duration","n_total"):
            self.assertNotIn(outcome,all_keys)
        h,rows=key_rows_only("Field_Manipulation_Table.csv",
                             b"date_manipulation,Cave_roost,n_visited_either_tree\n2020-01,A,999\n")
        self.assertEqual(rows,[("2020-01","A")])
        self.assertIn("n_visited_either_tree",h)

    def test_missing_or_wrong_width_stops(self):
        with self.assertRaisesRegex(RuntimeError,"JOIN_KEY_MISSING"):
            key_rows_only("Tags_manipulated_and_visiting.csv",b"tags,Visited\nB,yes\n")
        with self.assertRaisesRegex(RuntimeError,"ROW_WIDTH_STOP"):
            key_rows_only("Field_Manipulation_Table.csv",
                          b"date_manipulation,Cave_roost\n2020,A,unused\n")

    def test_unpinned_bytes_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError,"AUTHOR_GIT_BLOB_SHA_MISMATCH"):
            key_stats(lambda name,n:b"x"*n)

if __name__=="__main__":
    unittest.main()
