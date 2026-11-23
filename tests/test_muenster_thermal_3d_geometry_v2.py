"""Source-free tests for real XYZ coordinate grammar; no actual bat data."""
from io import BytesIO
from zipfile import ZipFile
import unittest
from scripts.audit_muenster_thermal_3d_geometry_v2 import (
    read_3d_numeric_rows,BASENAME,audit_archive,
)


class MünsterSourceGeometryTests(unittest.TestCase):
    def test_headerless_3D_xyz_is_numeric_and_preserves_source_axes(self):
        result=read_3d_numeric_rows(b"1.5,2.5,3.5\n-1.5,0.0,1.5\n")
        self.assertEqual(result["finite_three_coordinate_rows"],2)
        self.assertEqual(result["original_local_axes_min_source_units"],[-1.5,0.,1.5])
        self.assertFalse(result["named_XYZ_header"])
        self.assertTrue(result["axes_are_Not_yet_verified_AGL_or_world_EPSG"])

    def test_bad_original_four_column_schema_stops(self):
        with self.assertRaisesRegex(ValueError,"3 columns"):
            read_3d_numeric_rows(b"1,2,3,4\n5,6,7,8\n")

    def test_missing_xyz_not_false_zero_bat_position(self):
        result=read_3d_numeric_rows(b"1,2,3\nNaN,NaN,NaN\n2,3,4\n")
        self.assertEqual(result["row_count"],3)
        self.assertEqual(result["finite_three_coordinate_rows"],2)
        self.assertEqual(result["nonfinite_rows_not_interpolated"],1)

    def test_uninterrupted_variant_does_not_get_new_flight_ID(self):
        source=[
            "DLTdv5_night18_bat1_uninterrupted_xyzpts.csv",
            "DLTdv5_night18_bat1_xyzpts.csv",
        ]
        values=[BASENAME.fullmatch(s).groupdict() for s in source]
        self.assertEqual(len({(x["night"],x["id"]) for x in values}),1)
        self.assertEqual([bool(x["variant"]) for x in values],[True,False])

    def test_source_lamp_is_a_landmark_not_a_second_bat(self):
        data=[
            "DLTdv5_night18_lamp_xyzpts.csv",
            "DLTdv5_night19_bat3_xyzpts.csv",
        ]
        parsed=[BASENAME.fullmatch(x).groupdict() for x in data]
        self.assertEqual(parsed[0]["id"],"lamp")
        self.assertEqual(parsed[1]["id"],"bat3")

    def test_unmarked_source_labels_are_not_reinterpreted_as_geo(self):
        with self.assertRaisesRegex(ValueError,"nonnumeric"):
            read_3d_numeric_rows(b"EPSG,lat,lon\n1,2,3\n")

if __name__=="__main__":
    unittest.main()
