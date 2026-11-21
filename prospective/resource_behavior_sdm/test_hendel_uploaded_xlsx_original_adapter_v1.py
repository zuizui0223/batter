"""Synthetic-only regression gates for the user-upload Hendel original adapter."""
import tempfile
import unittest
from pathlib import Path
from hendel_uploaded_xlsx_original_adapter_v1 import (
    SOURCE_HEADERS, SOURCE_TO_ENGINE, build_receipt, normalize_original_matrix
)

def synthetic_original_matrix():
    values = [list(SOURCE_HEADERS)]
    for i in range(65):
        d = {k: float(1 + (i % 7)) for k in SOURCE_HEADERS[1:]}
        d.update({
            "DOY": 140 + i % 85, "DOY_carabidae": 112 + i % 30,
            "elevation": 516 + i * 9, "temp_min": 7 + i % 8,
            "ForMI": (i % 6) / 3, "Opn_mean": 10 + i % 50,
            "ndsm_sd": 4 + i % 7, "mothcount_total": 20 + i % 40,
            "moth_richness": 4 + i % 20, "carabidae": 5 + i % 18,
            "carabidae_SR": 2 + i % 7, "SRE": i % 9,
            "MRE": i % 4, "LRE": i % 3, "Ppip": 5 + i % 45,
        })
        d["plotID"] = "FICTIONAL_" + str(i)
        values.append([d[c] for c in SOURCE_HEADERS])
    return values

class HendelUploadedOriginalAdapterTests(unittest.TestCase):
    def test_header_aliases_and_65_distinct_sites(self):
        data = normalize_original_matrix(synthetic_original_matrix())
        self.assertEqual(len(data),65)
        self.assertEqual(data[0]["mothcount"],20)
        self.assertEqual(data[0]["carabidae_S"],2)
        self.assertNotIn("mothcount_total",data[0])
        self.assertNotIn("carabidae_SR",data[0])
        self.assertEqual(SOURCE_TO_ENGINE["carabidae_SR"],"carabidae_S")

    def test_unexplained_64_vs_65_cannot_silently_drop_a_plot(self):
        rows = synthetic_original_matrix()
        with self.assertRaisesRegex(ValueError,"SCHEMA_UNEXPECTED"):
            normalize_original_matrix(rows[:-1])

    def test_bad_header_or_missing_prey_cannot_pass(self):
        rows = synthetic_original_matrix()
        rows[0][15] = "mothcount"  # not the original author header
        with self.assertRaisesRegex(ValueError,"SCHEMA_UNEXPECTED"):
            normalize_original_matrix(rows)
        rows = synthetic_original_matrix()
        rows[5][15] = None
        with self.assertRaisesRegex(ValueError,"PREDICTOR_MAP_MISSING"):
            normalize_original_matrix(rows)

    def test_duplicate_site_cannot_pass(self):
        rows = synthetic_original_matrix()
        rows[2][0] = rows[1][0]
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            normalize_original_matrix(rows)

    def test_unpinned_binary_rejected_before_artifact_tool_import(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/"fake.xlsx"
            path.write_bytes(b"not-the-user-provided-workbook")
            with self.assertRaisesRegex(ValueError,"SHA256_MISMATCH"):
                build_receipt(path)

if __name__ == "__main__":
    unittest.main()
