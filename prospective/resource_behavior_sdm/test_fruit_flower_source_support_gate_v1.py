"""Synthetic-only tests; no original bat tracking, cactus or bloom rows."""
import unittest
from fruit_flower_source_support_gate_v1 import audit_support


def setup():
    gps = [
        {"bat": "batA", "night": "2020-05-01", "field": "north"},
        {"bat": "batA", "night": "2020-05-02", "field": "north"},
        {"bat": "batB", "night": "2020-05-01", "field": "south"},
        {"bat": "batB", "night": "2020-05-01", "field": "south"},
        {"bat": "batC", "night": "2020-05-01", "field": "unsurveyed"},
    ]
    cacti = [
        {"cactus": "n1", "field": "north"},
        {"cactus": "n2", "field": "north"},
        {"cactus": "s1", "field": "south"},
    ]
    fields = [
        {"field": f, "surveyed_area_m2": 100, "independent_field_polygon": True}
        for f in ("north", "south")
    ]
    flowers = [
        {"cactus": c, "night": "2020-05-01", "open_flowers": q,
         "survey_effort": 1, "direct_observation": True, "simulated": False}
        for c, q in (("n1", 0), ("n2", 3), ("s1", 1))
    ]
    return gps, cacti, fields, flowers


class SupportAudit(unittest.TestCase):
    def test_stage_a_and_strict_b_distinguish_support(self):
        r = audit_support(*setup())
        self.assertEqual(r["stage_a"]["n_eligible_gps_records"], 4)
        self.assertEqual(r["stage_b_strict_full_field_night_census"]["n_eligible_gps_records"], 3)
        self.assertEqual(r["stage_b_strict_full_field_night_census"]["n_eligible_bats"], 2)
        self.assertEqual(r["stage_b_strict_full_field_night_census"]["n_missing_mapped_cactus_night_counts_on_gps_support"], 2)
        self.assertIsNone(r["measured_resource_height_field_gain"])

    def test_static_layout_only_never_becomes_nectar(self):
        gps, cactus, fields, _ = setup()
        r = audit_support(gps, cactus, fields, [])
        self.assertTrue(r["stage_a"]["potential_only"])
        self.assertFalse(r["stage_b_strict_full_field_night_census"]["potential_only"])

    def test_partial_survey_not_imputed_as_zero(self):
        gps, cactus, fields, bloom = setup()
        bloom.pop(1)
        r = audit_support(gps, cactus, fields, bloom)
        self.assertEqual(r["stage_b_strict_full_field_night_census"]["n_eligible_gps_records"], 2)
        self.assertEqual(r["stage_b_strict_full_field_night_census"]["n_missing_mapped_cactus_night_counts_on_gps_support"], 3)

    def test_census_night_must_exactly_match(self):
        gps, cactus, fields, bloom = setup()
        bloom[0]["night"] = "2020-05-02"
        r = audit_support(gps, cactus, fields, bloom)
        self.assertEqual(r["stage_b_strict_full_field_night_census"]["n_eligible_gps_records"], 2)

    def test_height_coupled_or_visit_labels_stop(self):
        for key in ("height", "altitude", "recorded_agl_m", "visit", "core_cactus"):
            args = setup()
            args[0][0][key] = 4.0
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "LEAKAGE"):
                audit_support(*args)

    def test_simulated_or_missing_census_not_direct(self):
        for key, val in (("simulated", True), ("direct_observation", False),
                         ("open_flowers", None), ("open_flowers", -1), ("survey_effort", 0)):
            args = setup()
            args[3][0][key] = val
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "STOP_"):
                audit_support(*args)

    def test_duplicate_cactus_and_census_stop(self):
        args = setup()
        args[1].append(dict(args[1][0]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_CACTUS"):
            audit_support(*args)
        args = setup()
        args[3].append(dict(args[3][0]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_CACTUS_NIGHT"):
            audit_support(*args)

    def test_no_independent_coverage_no_stage_a(self):
        args = setup()
        args[2][0]["independent_field_polygon"] = False
        with self.assertRaisesRegex(ValueError, "INDEPENDENTLY_DECLARED"):
            audit_support(*args)

    def test_source_rows_never_disclosed(self):
        r = str(audit_support(*setup()))
        for secret in ("batA", "batB", "batC", "n1", "north", "south"):
            self.assertNotIn(secret, r)

    def test_unknown_cactus_and_wrong_night_rejected(self):
        args = setup()
        args[3][0]["cactus"] = "extra"
        with self.assertRaisesRegex(ValueError, "FLOWER_CACTUS"):
            audit_support(*args)
        args = setup()
        args[0][0]["night"] = "2020/05/01"
        with self.assertRaisesRegex(ValueError, "ISO_DATE"):
            audit_support(*args)


if __name__ == "__main__":
    unittest.main()
