"""Source-free regression tests for original DLTdv5 multiple XYZ target schema."""
from io import BytesIO
from zipfile import ZipFile
import unittest
from scripts.audit_muenster_thermal_3d_geometry_v2_3 import (
    parse_real_source_point_streams,run_real_source_QC,
)


def original_like_zip():
    data=BytesIO()
    with ZipFile(data,"w") as archive:
        def add(n,txt):
            archive.writestr(f"3DTracks/coordinates_tracks/DLTdv5_night{n}_xyzpts.csv",txt)
        a=b"pt1_X,pt1_Y,pt1_Z\n1,2,3\nNaN,NaN,NaN\n"
        dual=b"pt1_X,pt1_Y,pt1_Z,pt2_X,pt2_Y,pt2_Z\n1,2,3,NaN,NaN,NaN\n4,5,6,7,8,9\n"
        for i in range(1,9):
            add(f"18_bat{i}",dual if i==8 else a)
        for i in (1,4,8):
            add(f"18_bat{i}_uninterrupted",dual if i==8 else a)
        add("18_lamp",a)
        for i in range(1,4):
            add(f"19_bat{i}",a)
        add("19_lamp",a)
        archive.writestr("3DTracks/plots/a.png",b"PNG")
        archive.writestr("3DTracks/plots/b.png",b"PNG")
    return data.getvalue()


class SourceAuthorDLTdv5Tests(unittest.TestCase):
    def test_first_row_original_labels_and_nan_missing(self):
        r=parse_real_source_point_streams(
            b"pt1_X,pt1_Y,pt1_Z\nNaN,NaN,NaN\n-2,2,3\n")
        self.assertEqual(r["source_original_column_headers"],["pt1_X","pt1_Y","pt1_Z"])
        self.assertEqual(r["source_numeric_point_streams"]["pt1"]["full_valid_xyz"],1)
        self.assertEqual(r["source_numeric_point_streams"]["pt1"]["all_missing_xyz"],1)
        self.assertTrue(r["source_numeric_point_streams"]["pt1"]["zero_substitution_or_missing_track_interpolation_used"]==False)

    def test_dual_target_pt1_pt2_parsed_separately_not_two_source_files(self):
        r=parse_real_source_point_streams(
            b"pt1_X,pt1_Y,pt1_Z,pt2_X,pt2_Y,pt2_Z\n"
            b"1,2,3,NaN,NaN,NaN\n"
            b"4,5,6,7,8,9\n")
        self.assertTrue(r["source_has_second_pt2_stream"])
        self.assertEqual(r["source_numeric_point_streams"]["pt1"]["full_valid_xyz"],2)
        self.assertEqual(r["source_numeric_point_streams"]["pt2"]["full_valid_xyz"],1)

    def test_incomplete_coordinate_triples_are_not_valid_points(self):
        r=parse_real_source_point_streams(
            b"pt1_X,pt1_Y,pt1_Z\n"
            b"1,2,NaN\n"
            b"4,5,6\n")
        self.assertEqual(r["source_numeric_point_streams"]["pt1"]["partially_missing_xyz"],1)
        self.assertEqual(r["source_numeric_point_streams"]["pt1"]["full_valid_xyz"],1)

    def test_original_symbolic_xyz_grid_does_not_fabricate_lidar_alignment(self):
        r=run_real_source_QC(original_like_zip(),b"README camera local xyz only")
        self.assertEqual(r["canonical_source_bat_filename_IDs_by_night"],{"18":8,"19":3})
        self.assertEqual(r["observed_numerically_valid_target_streams_by_night"],{"18":9,"19":3})
        self.assertEqual(r["source_pt2_additional_streams_nonzero"],1)
        self.assertEqual(r["canonical_source_target_streams_with_ge1_valid_xyz"],12)
        self.assertFalse(r["original_geographic_XYZ_or_EPSG_control_ties_verified"])
        self.assertFalse(r["field_clutter_niche_or_3D_SDM_fitted"])

    def test_unexpected_x_y_z_names_not_silently_assumed_same_source_format(self):
        with self.assertRaisesRegex(ValueError,"header"):
            parse_real_source_point_streams(b"X,Y,Z\n1,2,3\n")

    def test_wrong_four_columns_and_nonnumeric_row_hard_stops(self):
        with self.assertRaisesRegex(ValueError,"header"):
            parse_real_source_point_streams(
                b"pt1_X,pt1_Y,pt1_Z,pt4_X\n1,2,3,4\n")
        with self.assertRaisesRegex(ValueError,"nonnumeric"):
            parse_real_source_point_streams(
                b"pt1_X,pt1_Y,pt1_Z\n1,foo,3\n")

if __name__=="__main__":
    unittest.main()
