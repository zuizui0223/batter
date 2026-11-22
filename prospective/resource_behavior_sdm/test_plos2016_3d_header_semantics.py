"""Synthetic header data only. No biological source values."""
import io
import json
import unittest
import zipfile

from plos2016_3d_header_semantics import PASS, inspect_publisher_header

def fake():
    ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    names=['BAT','TRIAL','TREATMENT','X','Y','Z','TIME']
    header=''.join(f'<c r="{chr(65+i)}1" t="s"><v>{i}</v></c>' for i in range(7))
    sh=f'<worksheet xmlns="{ns}"><dimension ref="A1:G31"/><sheetData><row r="1">{header}</row><row r="2"><c r="A2"><v>123</v></c></row></sheetData></worksheet>'
    wb=f'<workbook xmlns="{ns}"><sheets><sheet name="a" sheetId="1"/></sheets></workbook>'
    strings=f'<sst xmlns="{ns}">'+''.join(f'<si><t>{x}</t></si>' for x in names)+'</sst>'
    f=io.BytesIO()
    with zipfile.ZipFile(f,"w") as z:
        z.writestr("xl/workbook.xml",wb)
        z.writestr("xl/worksheets/sheet1.xml",sh)
        z.writestr("xl/sharedStrings.xml",strings)
        z.writestr("[Content_Types].xml","metadata")
    return f.getvalue()

class HeaderSemanticTests(unittest.TestCase):
    def test_header_only_and_hash(self):
        r=inspect_publisher_header(fake())
        self.assertEqual(r["status"],PASS)
        self.assertEqual(r["verified_original_first_row_column_names"],
                         ['BAT','TRIAL','TREATMENT','X','Y','Z','TIME'])
        self.assertFalse(r["height_or_trajectory_values_opened"])
        self.assertIsNone(r["new_predictive_3d_effect"])
        self.assertEqual(len(r["source_sha256"]),64)
    def test_corrupt_source_stop(self):
        with self.assertRaises(ValueError):
            inspect_publisher_header(b"not xlsx")

if __name__=="__main__":
    unittest.main()
