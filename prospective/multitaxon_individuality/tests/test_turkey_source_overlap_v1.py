import hashlib
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_maine_source_overlap_v1 as m

class OverlapAuditTests(unittest.TestCase):
    def run_audit(self, candidate_row):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d)/'a.csv', Path(d)/'b.csv'
            a.write_text('individual-local-identifier,timestamp,location-lat,location-long\nold,2020-02-01 12:00:00,30,-80\n', encoding='utf8')
            b.write_text('BirdID,timestamp,location_lat,location_long\n'+candidate_row+'\n', encoding='utf8')
            with patch.object(m, 'DISCOVERY_SHA', hashlib.sha256(a.read_bytes()).hexdigest()), patch.object(m, 'MAINE_SHA', hashlib.sha256(b.read_bytes()).hexdigest()):
                return m.audit(a,b)

    def test_recoded_id_and_timezone_do_not_hide_duplicate(self):
        r = self.run_audit('new,2020-02-01T07:00:00-05:00,30,-80')
        self.assertEqual(r['literal_id_label_intersection_count'], 0)
        self.assertEqual(r['candidate_rows_matching_timestamp_and_position'], 1)

    def test_rounding_sensitivity_is_separate_from_exact_match(self):
        r = self.run_audit('new,2020-02-01T12:00:00Z,30.000001,-80.000001')
        self.assertEqual(r['candidate_rows_matching_timestamp_and_position'], 0)
        self.assertEqual(r['candidate_rows_matching_timestamp_and_position_rounded_5dp'], 1)

    def test_spatial_bound_and_no_outcome(self):
        r = self.run_audit('new,2020-02-01T12:00:00Z,45,-70')
        self.assertAlmostEqual(r['minimum_spatial_separation_lower_bound_km'], 6371*math.radians(15))
        self.assertFalse(r['hypothesis_effect_computed'])

if __name__ == '__main__':
    unittest.main()
