"""No real PLOS biological outcomes used in these source-gate tests."""
import io
import zipfile
import unittest

from plos2016_3d_xlsx_source_gate import (
    FILE_DOI, PASS, structure_audit, validate_redirect
)


def fixture():
    workbook=(
        b'<?xml version="1.0"?><workbook xmlns="http://schemas.openxmlformats.org/'
        b'spreadsheetml/2006/main"><sheets><sheet name="test" sheetId="1"/></sheets></workbook>'
    )
    xml=(b'<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/'
         b'spreadsheetml/2006/main"><dimension ref="A1:C3"/><sheetData>'
         b'<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="n"><v>1</v></c></row>'
         b'<row r="2"><c r="A2" t="n"><v>999</v></c></row>'
         b'</sheetData></worksheet>')
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w") as f:
        f.writestr("xl/workbook.xml",workbook)
        f.writestr("[Content_Types].xml","present")
        f.writestr("xl/worksheets/sheet1.xml",xml)
    return out.getvalue()


class SourceGateTest(unittest.TestCase):
    def test_synthetic_structure_records_no_biology(self):
        v=structure_audit(fixture())
        self.assertEqual(v["status"],PASS)
        self.assertEqual(v["worksheet_count"],1)
        self.assertEqual(v["worksheet_schema_aggregate"][0]["declared_excel_dimension"],"A1:C3")
        self.assertFalse(v["original_coordinates_or_height_values_read"])
        self.assertIsNone(v["new_resource_conditional_3d_log_score"])
    def test_official_redirect_guard(self):
        validate_redirect("https://journals.plos.org/plosone/article/file?id="+FILE_DOI)
        validate_redirect("https://corpus-prod.abc.r2.cloudflarestorage.com/"
                          "10.1371/journal.pone.0163492/1/pone.0163492.s001.xlsx")
        for url in ("http://journals.plos.org/plosone/article/file?id="+FILE_DOI,
                    "https://evil.example/10.1371/journal.pone.0163492/1/pone.0163492.s001.xlsx",
                    "https://corpus-prod.abc.r2.cloudflarestorage.com/other.xlsx"):
            with self.assertRaises(ValueError):
                validate_redirect(url)
    def test_unexpected_bytes_fail(self):
        with self.assertRaises(ValueError):
            structure_audit(b"not a spreadsheet")
        with self.assertRaises(ValueError):
            structure_audit(b"PK\x03\x04"+b"X"*1024*1024)

if __name__=="__main__":
    unittest.main()
