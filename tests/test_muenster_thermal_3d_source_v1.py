from io import BytesIO
from zipfile import ZipFile
import unittest

from scripts.audit_muenster_thermal_3d_source_v1 import (
    safe_member_metadata,readme_design_lines,source_url,
)


def archive(items):
    out=BytesIO()
    with ZipFile(out,"w") as z:
        for name,data in items.items():
            z.writestr(name,data)
    return out.getvalue()


class PublishedThermal3DSourceGateTests(unittest.TestCase):
    def test_source_Zenodo_is_version_pinned(self):
        self.assertEqual(
            source_url("3DTracks.zip"),
            "https://zenodo.org/records/7797077/files/3DTracks.zip?download=1"
        )

    def test_only_header_coordinates_not_original_numeric_positions_are_read(self):
        sample=archive({
            "tracks/test_track_001.csv":
                b"x,y,z,frame\n25.4,93.6,4.4,1\n64.2,83.4,9.1,2\n",
        })
        result=safe_member_metadata(sample)
        self.assertEqual(result["source_zip_member_count"],1)
        record=result["source_members"][0]
        self.assertEqual(record["textual_column_headers_only"],["x","y","z","frame"])
        self.assertFalse(result["original_numeric_flight_locations_opened"])
        self.assertNotIn("25.4",str(result))
        self.assertNotIn("93.6",str(result))

    def test_no_numeric_first_row_confused_with_header(self):
        sample=archive({"tracks/flight_raw.txt":
            b"12.4,23.8,4.2,1\n3.3,4.5,6.6,2\n"})
        result=safe_member_metadata(sample)
        self.assertNotIn(
            "textual_column_headers_only",result["source_members"][0])

    def test_member_path_cannot_escape_original_zip(self):
        sample=archive({"../untrusted.csv":b"x,y,z\n1,2,3\n"})
        with self.assertRaisesRegex(ValueError,"unsafe"):
            safe_member_metadata(sample)

    def test_original_readme_design_language_not_biological_predictions(self):
        selected=readme_design_lines(
            b"Title\nLocal xyz positions relative to stereo camera\n"
            b"Forest lamppost site calibration required\n")
        self.assertEqual(len(selected),2)
        self.assertIn("xyz",selected[0])

    def test_source_zip_requires_content_and_expected_format(self):
        with self.assertRaisesRegex(ValueError,"ZIP"):
            safe_member_metadata(b"not a zip file")


if __name__=="__main__":
    unittest.main()
