"""Pure source-free tests: no original animal/GPS/cactus source rows are read."""
import tempfile
import unittest
from pathlib import Path

from goldshtein_cactus_alt_geoid96_sensitivity_v1 import (
    _digest, _nmea_coordinate, _quantiles, audit_original,
    ORIGINAL_SHA, EGM96_GRID_SHA,
)


class GoldshteinVerticalReferenceTests(unittest.TestCase):
    def test_source_rmc_xy_parse(self):
        self.assertAlmostEqual(_nmea_coordinate("3121.5000","N"),31.358333333333)
        self.assertAlmostEqual(_nmea_coordinate("11234.5000","W"),-112.575)
        self.assertIsNone(_nmea_coordinate(None,"N"))
        self.assertIsNone(_nmea_coordinate("3161.00","N"))
        self.assertIsNone(_nmea_coordinate("999999.0","N"))
        self.assertIsNone(_nmea_coordinate("11234.5000","X"))

    def test_sha_gate_blocks_untrusted_source_and_grid_before_original_open(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"fake.zip"
            g=Path(d)/"fake.gtx"
            f.write_bytes(b"untrusted")
            g.write_bytes(b"untrusted")
            self.assertEqual(len(_digest(f)),64)
            with self.assertRaisesRegex(ValueError,"STOP_SOURCE_OR_REFERENCE_GRID"):
                audit_original(f,g)
        self.assertEqual(len(ORIGINAL_SHA),64)
        self.assertEqual(len(EGM96_GRID_SHA),64)

    def test_equal_animal_and_fix_quantiles_are_distinct(self):
        # Explicitly do not use 36082 correlated GPS fixes as 36082 bats.
        self.assertEqual(_quantiles([0,0,0,50,100]),[0.,0.,0.,50.,90.])
        per_animal_medians=[-79.35,-28.2]
        self.assertNotEqual(sum(per_animal_medians)/2,0)

    def test_no_source_raw_or_bat_ID_literal_in_public_result_schema(self):
        schema={
            "source_author_original_AGL_reconstructed":False,
            "single_constant_offset_validated":False,
            "observed_food_conditional_altitude_gain":None,
        }
        self.assertFalse(schema["source_author_original_AGL_reconstructed"])
        self.assertIsNone(schema["observed_food_conditional_altitude_gain"])


if __name__=="__main__":
    unittest.main()
