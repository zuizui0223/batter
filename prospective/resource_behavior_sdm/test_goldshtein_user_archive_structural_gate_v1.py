"""Source-free checks for structural file-intake and height-label circularity."""
import io
import unittest
import zipfile

from goldshtein_user_archive_structural_gate_v1 import (
    audit_archive_bytes,candidate_semantics
)

def zip_bytes(items):
    mem=io.BytesIO()
    with zipfile.ZipFile(mem,"w") as z:
        for name,data in items:
            z.writestr(name,data)
    return mem.getvalue()

class GoldshteinUserOriginalStructuralGateTests(unittest.TestCase):
    def test_observation_rows_are_never_printed_or_read(self):
        src=zip_bytes([
            ("private/tracks.csv",b"bat_id,timestamp,longitude,latitude,altitude\nSECRET_BAT_003,2016-05-01T19:00:00,-112,31,20\n"),
            ("private/flower_map.csv",b"longitude,latitude,flower_count,survey_date\n-112,31,500,2016-05-01\n"),
            ("private/model.m",b"fprintf('this must never execute');")
        ])
        rec=audit_archive_bytes(src)
        self.assertTrue(rec["csv_header_hints_possible_gps"])
        self.assertTrue(rec["csv_header_hints_possible_flower_resource"])
        self.assertFalse(rec["night_by_bat_resource_join_verified"])
        self.assertFalse(rec["height_agl_semantics_verified_from_original"])
        self.assertFalse(rec["original_publisher_digest_verified"])
        self.assertIsNone(rec["source_original_3d_resource_gain"])
        self.assertNotIn("SECRET_BAT",str(rec))
        self.assertNotIn("-112",str(rec))
        self.assertNotIn("private",str(rec))
        self.assertIn("height-derived visit labels",rec["next_gate"])

    def test_only_same_2d_source_does_not_pass_vertical(self):
        x=candidate_semantics(["bat_id","timestamp","longitude","latitude","straightness"])
        self.assertFalse(x["possible_tracking_columns"])
        y=candidate_semantics(["cactus_latitude","cactus_longitude","flower_est"])
        self.assertTrue(y["possible_flower_columns"])
        self.assertTrue(y["not_sufficient_for_resource_height_join"])

    def test_height_derived_visit_label_is_not_a_valid_predictor(self):
        rec=audit_archive_bytes(zip_bytes([("visits.csv",b"visit,altitude,latitude,longitude\ntrue,4,31,-112\n")]))
        self.assertIn("altitude",rec["response_leakage_stop"].lower())
        self.assertFalse(rec["independent_xy_only_state_assignment_verified"])

    def test_zip_slip_and_duplicate_prevent_reading(self):
        for name in ("../secret.csv","/secret.csv","folder\\secret.csv"):
            with self.subTest(name=name):
                bad=zip_bytes([(name,b"a,b\n1,2\n")])
                with self.assertRaisesRegex(ValueError,"UNSAFE_OR_DUPLICATE"):
                    audit_archive_bytes(bad)
        with self.assertRaisesRegex(ValueError,"UNSAFE_OR_DUPLICATE"):
            audit_archive_bytes(zip_bytes([("x.csv",b"a,b\n"),("x.csv",b"a,b\n")]))

    def test_matlab_and_unknown_is_not_auto_joined(self):
        rec=audit_archive_bytes(zip_bytes([
            ("source/tracking.mat", b"MATLAB 5.0 MAT-file, Platform: PCWIN64"),
            ("source/flower_source.rds", b"anything")
        ]))
        self.assertFalse(rec["csv_header_hints_possible_gps"])
        self.assertFalse(rec["csv_header_hints_possible_flower_resource"])
        self.assertEqual(rec["anonymous_files"][0]["format_note"],"MATLAB_V5_HEADER_ONLY")
        self.assertFalse(rec["night_by_bat_resource_join_verified"])

if __name__=="__main__":
    unittest.main()
