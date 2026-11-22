from collections import Counter, defaultdict
import unittest
from prospective.lunar_3d.lunar_source_admission_v3 import build_reference, match_counts

class AdmissionTests(unittest.TestCase):
    def test_reference_safety_gate(self):
        refs = [
            {"animal_id":"a","study_site":"S1","manipulation_type":"none","tag_id":"t1"},
            {"animal_id":"a","study_site":"S1","manipulation_type":"","tag_id":"t2"},
            {"animal_id":"b","study_site":"S2","manipulation_type":"feeding"},
            {"animal_id":"c","study_site":"S1","manipulation_type":""},
            {"animal_id":"c","study_site":"S2","manipulation_type":""},
        ]
        r=build_reference(refs)
        self.assertTrue(r["a"]["ok"])
        self.assertTrue(r["a"]["mixed_reference_tags"])
        self.assertFalse(r["b"]["ok"])
        self.assertFalse(r["c"]["ok"])
    def test_proper_night_holdout_and_exposure_breadth(self):
        g=defaultdict(lambda: {"bright":Counter(),"dark":Counter()})
        key=("i","site","2026",1,2,3)
        g[key]["bright"].update({"2026-11-10":10,"2026-11-11":10})
        g[key]["dark"].update({"2026-11-20":10,"2026-11-21":10})
        self.assertEqual(len(match_counts(g)),1)
        g[key]["bright"]=Counter({"2026-11-10":19,"2026-11-11":1})
        self.assertEqual(len(match_counts(g)),0)
    def test_year_must_match(self):
        g=defaultdict(lambda: {"bright":Counter(),"dark":Counter()})
        a=("i","site","2025",1,2,3)
        b=("i","site","2026",1,2,3)
        g[a]["bright"].update({"2025-12-30":10,"2025-12-31":10})
        g[b]["dark"].update({"2026-01-01":10,"2026-01-02":10})
        self.assertEqual(len(match_counts(g)),0)

if __name__=="__main__":
    unittest.main()
