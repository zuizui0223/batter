"""Source-free known-truth tests of publisher hash and small file scope."""
import hashlib
import io
import unittest
import zipfile

from independent_resource_vertical_smallfile_gate_v1 import (
    PASS,check_one,inspect_zip,inspect_xlsx,verify_digest
)
from independent_resource_vertical_dryad_gate_v1 import PASS as META_PASS


def fixture_zip():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("bat1.csv","ID,timestamp,lat,long,height.above.msl\nb,0,1,2,3\n")
        z.writestr("bat2.csv","ID,timestamp,lat,long,height.above.msl\nb,0,1,2,3\n")
    return b.getvalue()


def fixture_xlsx():
    ns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("xl/workbook.xml",f'<workbook xmlns="{ns}"><sheets><sheet name="Bats" sheetId="1"/><sheet name="Fruits" sheetId="2"/></sheets></workbook>')
    return b.getvalue()


class SmallOriginalFileTests(unittest.TestCase):
    def test_original_zip_headers_only_no_rows(self):
        data=fixture_zip()
        x=inspect_zip(data,"chrotopterus_2026")
        self.assertEqual(x["csv_header_files_inspected"],2)
        self.assertIn("height.above.msl",x["csv_first_line_column_names_union"])
        self.assertFalse(x["original_gps_rows_parsed"])
        src={"dataset":"chrotopterus_2026","status":META_PASS,"source_files":[
            {"source_file_name":"Raw_movement_data.zip","size_bytes":len(data),
             "original_file_id":123,"digest_type":"md5","digest":hashlib.md5(data).hexdigest()}]}
        o=check_one(src,lambda fid,n,cap:data)
        self.assertEqual(o["status"],PASS)
        self.assertIsNone(o["new_ecological_height_resource_gain"])

    def test_xlsx_is_only_workbook_metadata(self):
        data=fixture_xlsx()
        x=inspect_xlsx(data)
        self.assertEqual(x["workbook_worksheet_count"],2)
        self.assertTrue(x["original_bat_capture_or_fruit_values_parsed"] is False)
        src={"dataset":"ducke_bats_2018","status":META_PASS,"source_files":[
            {"source_file_name":"Bats_Ducke_data_metadata.xlsx","size_bytes":len(data),
             "original_file_id":124,"digest_type":"sha256","digest":hashlib.sha256(data).hexdigest()}]}
        self.assertEqual(check_one(src,lambda fid,n,cap:data)["status"],PASS)

    def test_mismatched_publisher_digest_rejected(self):
        raw=b"test"
        with self.assertRaisesRegex(RuntimeError,"DIGEST_MISMATCH"):
            verify_digest(raw,{"digest_type":"md5","digest":"0"*32})
        with self.assertRaisesRegex(RuntimeError,"DIGEST_UNSUPPORTED"):
            verify_digest(raw,{"digest_type":"sha1","digest":"0"*40})

    def test_unverified_metadata_stops(self):
        with self.assertRaisesRegex(RuntimeError,"METADATA_NOT_QUALIFIED"):
            check_one({"dataset":"ducke_bats_2018","status":"STOP"},lambda i,n,c:b"")

if __name__=="__main__":
    unittest.main()
