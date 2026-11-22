"""Only synthetic/source-free legacy Excel BIFF8 parser tests."""
import struct
import unittest
from goldshtein_legacy_biff_source_gate_v1 import (
    rk_number, read_pinned_source_tables, ZIP_SHA, XLS_SHA)


class LegacySourceStructureTests(unittest.TestCase):
    def test_four_rk_numeric_variants(self):
        # Bits 1=int and 0=divide by 100.
        self.assertEqual(rk_number((25 << 2) | 2), 25)
        self.assertEqual(rk_number((25 << 2) | 3), 0.25)
        self.assertEqual(rk_number(((1 << 32) - 12) | 2), -3)
        bits = struct.unpack("<Q", struct.pack("<d", 3.5))[0]
        self.assertAlmostEqual(rk_number((bits >> 32) & ~3), 3.5)

    def test_wrong_byte_digest_always_fails_closed(self):
        for data in (b"", b"fake xls", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            with self.subTest(length=len(data)), self.assertRaisesRegex(
                    ValueError, "STOP_LEGACY_XLS_SHA_MISMATCH"):
                read_pinned_source_tables(data)

    def test_publisher_equivalence_not_guaranteed_by_uploaded_sha(self):
        self.assertEqual(len(ZIP_SHA), 64)
        self.assertEqual(len(XLS_SHA), 64)
        self.assertNotEqual(ZIP_SHA, XLS_SHA)


if __name__ == "__main__":
    unittest.main()
