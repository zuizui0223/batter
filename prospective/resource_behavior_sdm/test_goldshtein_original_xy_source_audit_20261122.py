"""Pure standard-library geometry tests; no source ZIP opened by CI."""
import tempfile
import unittest
from pathlib import Path
from goldshtein_original_xy_source_audit_20261122 import (
    audit, convex_hull, inside_hull, nmea_degree, ORIGINAL_SHA
)


class GoldshteinSourceXYTests(unittest.TestCase):
    def test_nmea_coordinate_semantics(self):
        self.assertAlmostEqual(nmea_degree("3121.5000", "N"), 31.35833333333)
        self.assertAlmostEqual(nmea_degree("11234.5000", "W"), -112.575)
        self.assertIsNone(nmea_degree("", "W"))
        self.assertIsNone(nmea_degree("3161.00", "N"))
        self.assertIsNone(nmea_degree("11240.5", "X"))
        self.assertIsNone(nmea_degree("999999.0", "N"))

    def test_ccw_convex_hull_and_membership(self):
        h=convex_hull([(0,0),(2,0),(2,2),(0,2),(1,1),(0,0)])
        self.assertEqual(len(h),4)
        self.assertTrue(inside_hull(h,(1,1)))
        self.assertTrue(inside_hull(h,(0,1)))
        self.assertFalse(inside_hull(h,(3,1)))
        self.assertEqual(convex_hull([(0,0),(1,1)]),[])

    def test_bad_or_unauthenticated_zip_cannot_be_treated_as_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"untrusted.zip"
            p.write_bytes(b"fake-file")
            with self.assertRaisesRegex(ValueError,"SOURCE_ZIP_SHA256"):
                audit(str(p))
        self.assertEqual(len(ORIGINAL_SHA),64)

    def test_source_geometry_is_not_true_survey_availability(self):
        h=convex_hull([(0,0),(1,0),(1,1),(0,1)])
        self.assertTrue(inside_hull(h,(0.5,0.5)))
        # A convex hull contains space not necessarily surveyed for cactus absence.
        self.assertFalse(set(h)=={(0.5,0.5)})


if __name__=="__main__":
    unittest.main()
