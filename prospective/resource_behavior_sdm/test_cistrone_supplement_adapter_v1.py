"""Synthetic-only checks for the private Cistrone supplement adapter.

All identifiers and measurements below are invented. No source workbook or
source data row is needed to run this suite.
"""

from copy import deepcopy
from decimal import Decimal
import importlib
import importlib.util
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


INSECT_TAXA = (
    "Agrotis ipsilon", "Alcis bastelbergi", "Amata phegea",
    "Arctornis l-nigrum", "Biston betularia", "Lymantria monacha",
    "Crambus pascuella", "Tuta absoluta", "Eilema caniola", "Orgyia antiqua",
    "Catocala ilia", "Pscoparia basistrigalis", "Eudonia lacustrata",
    "Camponotus vagus", "Temnothorax nylanderi", "Meteorus pendulus",
    "Sinodendron cylindricum", "Tineola bisselliella",
    "Scathophaga stercoraria", "Brevicornu foliatum", "Allogamus ausoniae",
    "Pseudolynchia canariensis", "Cylindromyia rufipes",
)
BAT_SPECIES = (
    "Barbastella barbastellus", "Eptesicus serotinus", "Hypsugo savii",
    "Myotis cf bechsteinii", "Myotis myotis/blythii", "Myotis cf mystacinus",
    "Myotis crypticus", "Nyctalus leisleri", "Nyctalus noctula",
    "Pipistrellus kuhlii/nathusii", "Pipistrellus pipistrellus",
    "Pipistrellus pygmaeus", "Plecotus cf auritus", "Plecotus cf austriacus",
    "Rhinolophus hipposideros", "Tadarida teniotis", "Myotis sp (unidentified)",
)
INSECT_COLUMNS = (
    "Plot", "Stratum", "Clear_canopy_%", "Canopy_cover_%", "Height_m", "n_traps",
    *INSECT_TAXA, "Total_individuals",
)
BAT_COLUMNS = (
    "Plot", "Stratum", "Night", *BAT_SPECIES, "Total_bat_passes", "Temp_min",
    "Mean_basal_area_m2_ha", "Mean_DBH_cm", "Mean_tree_height_m",
)
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def synthetic_records():
    """Two balanced invented plots; one has zero bat passes on all nights."""
    insects, bats = [], []
    for plot, active in (("synthetic-active", True), ("synthetic-zero", False)):
        for stratum, multiplier in (("ground", 1), ("canopy", 2)):
            counts = [multiplier * i if active else 0 for i in range(1, 24)]
            clear = 20.0 if stratum == "ground" else 35.0
            insects.append({
                "Plot": plot, "Stratum": stratum, "Clear_canopy_%": clear,
                "Canopy_cover_%": 100.0 - clear,
                "Height_m": 1.2 if stratum == "ground" else 9.4, "n_traps": 1,
                **dict(zip(INSECT_TAXA, counts)), "Total_individuals": sum(counts),
            })
            for night in (1, 2):
                pair = {
                    ("ground", 1): (3, 5), ("ground", 2): (2, 4),
                    ("canopy", 1): (7, 1), ("canopy", 2): (6, 8),
                }[stratum, night] if active else (0, 0)
                species = [*pair, *([0] * 15)]
                bats.append({
                    "Plot": plot, "Stratum": stratum, "Night": night,
                    **dict(zip(BAT_SPECIES, species)),
                    "Total_bat_passes": sum(species),
                    "Temp_min": 12.5 if night == 1 else 15.5,
                    "Mean_basal_area_m2_ha": 33.0,
                    "Mean_DBH_cm": 28.0,
                    "Mean_tree_height_m": 21.0 if active else 24.0,
                })
    return insects, bats


def column_letters(index):
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def synthetic_xlsx(columns, records, *, annotated=False, formula_total=False,
                   missing_cache=False, stale_cache=False, shared=True,
                   missing_cell=None, duplicate_cell=False, formula_missing=False):
    """Small actual OOXML package, including relationships and both sheets.

    The fixture exercises mixed shared/inline rich strings, reordered physical
    XML cells, cached formula values, and explicit empty/missing cells.
    """
    q = lambda name: "{" + MAIN_NS + "}" + name
    strings, indexes = [], {}
    data = ET.Element(q("worksheet"))
    sheet_data = ET.SubElement(data, q("sheetData"))

    def add_row(number, values, with_total=False):
        row = ET.SubElement(sheet_data, q("row"), r=str(number))
        for index, value in reversed(list(enumerate(values, 1))):
            address = column_letters(index) + str(number)
            if missing_cell == address:
                continue
            cell = ET.SubElement(row, q("c"), r=address)
            is_total = with_total and columns[index - 1] == "Total_bat_passes"
            if is_total and not formula_missing:
                ET.SubElement(cell, q("f")).text = f"SUM(D{number}:T{number})"
                if missing_cache:
                    continue
                if stale_cache:
                    value += 1
            if value is None:
                continue
            if isinstance(value, bool):
                cell.set("t", "b")
                ET.SubElement(cell, q("v")).text = "1" if value else "0"
            elif isinstance(value, str):
                if shared and index % 2:
                    cell.set("t", "s")
                    if value not in indexes:
                        indexes[value] = len(strings)
                        strings.append(value)
                    ET.SubElement(cell, q("v")).text = str(indexes[value])
                else:
                    cell.set("t", "inlineStr")
                    inline = ET.SubElement(cell, q("is"))
                    split = max(1, len(value) // 2)
                    for fragment in (value[:split], value[split:]):
                        run = ET.SubElement(inline, q("r"))
                        ET.SubElement(run, q("t")).text = fragment
            else:
                ET.SubElement(cell, q("v")).text = str(value)
            if duplicate_cell and address == "A1":
                row.append(deepcopy(cell))

    add_row(1, columns)
    if annotated:
        add_row(2, ["Synthetic annotation", *([None] * (len(columns) - 1))])
    start = 3 if annotated else 2
    for number, record in enumerate(records, start):
        add_row(number, [record.get(name) for name in columns], with_total=formula_total)
    legend = ET.Element(q("worksheet"))
    ET.SubElement(legend, q("sheetData"))
    workbook = ET.Element(q("workbook"))
    sheets = ET.SubElement(workbook, q("sheets"))
    # Data is deliberately sheet 7, not sheet1.xml.
    for name, sid, rid in (("Data", "7", "dataRel"), ("Legend", "9", "legendRel")):
        ET.SubElement(sheets, q("sheet"), name=name, sheetId=sid,
                      attrib={"{" + REL_NS + "}id": rid})
    relationships = ET.Element("{" + PKG_NS + "}Relationships")
    for rid, target in (("dataRel", "worksheets/data7.xml"),
                        ("legendRel", "/xl/worksheets/legend9.xml")):
        ET.SubElement(relationships, "{" + PKG_NS + "}Relationship", Id=rid,
                      Type=REL_NS + "/worksheet", Target=target)
    if shared:
        ET.SubElement(relationships, "{" + PKG_NS + "}Relationship", Id="stringsRel",
                      Type=REL_NS + "/sharedStrings", Target="sharedStrings.xml")
    sst = ET.Element(q("sst"))
    for text in strings:
        si = ET.SubElement(sst, q("si"))
        ET.SubElement(si, q("t")).text = text
    result = BytesIO()
    with ZipFile(result, "w", ZIP_DEFLATED) as archive:
        for name, element in (("xl/workbook.xml", workbook),
                              ("xl/_rels/workbook.xml.rels", relationships),
                              ("xl/worksheets/data7.xml", data),
                              ("xl/worksheets/legend9.xml", legend)):
            archive.writestr(name, ET.tostring(element, encoding="utf-8"))
        if shared:
            archive.writestr("xl/sharedStrings.xml", ET.tostring(sst, encoding="utf-8"))
    return result.getvalue()


def synthetic_archive(insects=None, bats=None, **bat_options):
    if insects is None or bats is None:
        insects, bats = synthetic_records()
    result = BytesIO()
    with ZipFile(result, "w", ZIP_DEFLATED) as archive:
        archive.writestr("synthetic-mmc1.xlsx", synthetic_xlsx(
            INSECT_COLUMNS, insects, annotated=True))
        archive.writestr("synthetic-mmc2.xlsx", synthetic_xlsx(
            BAT_COLUMNS, bats, formula_total=True, **bat_options))
    return result.getvalue()


class AdapterTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.find_spec("cistrone_supplement_adapter_v1")
        self.assertIsNotNone(spec, "The requested adapter has not been implemented")
        self.adapter = importlib.import_module("cistrone_supplement_adapter_v1")
        self.insects, self.bats = synthetic_records()

    def validated(self):
        return self.adapter.validate_records(self.insects, self.bats)

    def load_synthetic(self, payload, **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.zip"
            path.write_bytes(payload)
            before = path.read_bytes()
            result = self.adapter.load_archive(path, **kwargs)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["synthetic.zip"])
            return result

    def test_exact_stratum_join_and_hand_checked_features(self):
        # Break caught: grouping by row order or reversing ground/canopy.
        self.insects.reverse()
        self.bats.reverse()
        result = self.validated()
        self.assertEqual(result["plots"][0], {
            "plot_id": "synthetic-active", "passes": [14, 22],
            "baseline": [15.0, 14.0, 33.0, 28.0, 21.0],
            "resources": {"total": [276, 552], "lepidoptera": [109, 218],
                          "diptera": [84, 168]},
        })
        self.assertTrue(result["source_audit"]["strict_coarse_join"])

    def test_all_zero_pass_plot_is_retained_and_audited(self):
        result = self.validated()
        self.assertEqual(len(result["plots"]), 2)
        self.assertEqual(result["plots"][1]["passes"], [0, 0])
        self.assertEqual(result["source_audit"]["zero_pass_plots"], 1)
        self.assertEqual(result["source_audit"]["zero_insect_samples"], 2)

    def test_duplicate_insect_key_is_rejected(self):
        self.insects.append(deepcopy(self.insects[0]))
        with self.assertRaisesRegex(ValueError, "duplicate.*insect|insect.*duplicate"):
            self.validated()

    def test_duplicate_bat_key_is_rejected(self):
        self.bats.append(deepcopy(self.bats[0]))
        with self.assertRaisesRegex(ValueError, "duplicate.*bat|bat.*duplicate"):
            self.validated()

    def test_missing_stratum_and_missing_night_are_rejected(self):
        for domain in ("insects", "bats"):
            with self.subTest(domain=domain):
                self.insects, self.bats = synthetic_records()
                getattr(self, domain).pop()
                with self.assertRaises(ValueError):
                    self.validated()

    def test_disjoint_plot_keys_are_not_silently_inner_joined(self):
        for row in self.bats:
            if row["Plot"] == "synthetic-zero":
                row["Plot"] = "synthetic-unmatched"
        with self.assertRaisesRegex(ValueError, "join|plot"):
            self.validated()

    def test_plot_identifiers_are_not_coerced_or_case_folded(self):
        for value in (None, 7, " synthetic-active", ""):
            with self.subTest(value=value):
                self.insects, self.bats = synthetic_records()
                self.insects[0]["Plot"] = value
                with self.assertRaises(ValueError):
                    self.validated()
        self.insects, self.bats = synthetic_records()
        self.bats[0]["Plot"] = "SYNTHETIC-ACTIVE"
        with self.assertRaises(ValueError):
            self.validated()

    def test_nonnegative_integral_counts_are_required_in_both_tables(self):
        for domain, field in (("insects", INSECT_TAXA[0]), ("bats", BAT_SPECIES[0])):
            for value in (-1, 0.25, None, "0", True, False, float("nan"), float("inf")):
                with self.subTest(domain=domain, value=value):
                    self.insects, self.bats = synthetic_records()
                    getattr(self, domain)[0][field] = value
                    with self.assertRaises(ValueError):
                        self.validated()

    def test_totals_reconcile_with_all_taxa_and_species(self):
        for domain, field in (("insects", "Total_individuals"),
                              ("bats", "Total_bat_passes")):
            with self.subTest(domain=domain):
                self.insects, self.bats = synthetic_records()
                getattr(self, domain)[0][field] += 1
                with self.assertRaisesRegex(ValueError, "total|Total"):
                    self.validated()

    def test_missing_count_column_is_not_imputed_zero(self):
        del self.insects[0][INSECT_TAXA[-1]]
        with self.assertRaisesRegex(ValueError, "column|schema|missing"):
            self.validated()

    def test_nights_are_exactly_one_and_two_without_boolean_coercion(self):
        for value in (0, 3, True, "1", None, 1.25):
            with self.subTest(value=value):
                self.insects, self.bats = synthetic_records()
                self.bats[0]["Night"] = value
                with self.assertRaises(ValueError):
                    self.validated()

    def test_canopy_complements_and_single_trap_are_validated(self):
        for field, value in (("Canopy_cover_%", 70), ("Clear_canopy_%", -1),
                             ("n_traps", 2), ("n_traps", True)):
            with self.subTest(field=field, value=value):
                self.insects, self.bats = synthetic_records()
                self.insects[0][field] = value
                with self.assertRaises(ValueError):
                    self.validated()

    def test_canopy_complement_tolerance_is_absolute(self):
        self.insects[0]["Canopy_cover_%"] += 0.01
        self.validated()
        self.insects[0]["Canopy_cover_%"] += 0.001
        with self.assertRaises(ValueError):
            self.validated()

    def test_plot_metadata_cannot_vary_across_strata_or_nights(self):
        for field in ("Mean_basal_area_m2_ha", "Mean_DBH_cm", "Mean_tree_height_m"):
            with self.subTest(field=field):
                self.insects, self.bats = synthetic_records()
                self.bats[3][field] += 1
                with self.assertRaisesRegex(ValueError, "constant|within|metadata"):
                    self.validated()

    def test_station_temperature_is_shared_only_within_plot_night(self):
        self.bats[2]["Temp_min"] = 99
        with self.assertRaisesRegex(ValueError, "temperature|Temp_min"):
            self.validated()

    def test_missing_and_nonfinite_baseline_values_are_rejected(self):
        for field in ("Temp_min", "Mean_basal_area_m2_ha", "Mean_DBH_cm", "Mean_tree_height_m"):
            for value in (None, float("nan"), True):
                with self.subTest(field=field, value=value):
                    self.insects, self.bats = synthetic_records()
                    self.bats[0][field] = value
                    with self.assertRaises(ValueError):
                        self.validated()

    def test_trap_height_never_substitutes_for_stand_or_recorder_height(self):
        self.insects[0]["Height_m"] = 2.7
        self.insects[1]["Height_m"] = 15.4
        result = self.validated()
        self.assertEqual(result["plots"][0]["baseline"][-1], 21.0)
        audit = result["source_audit"]
        self.assertEqual(audit["height_ranges_m"]["insect_trap"]["canopy"], [9.4, 15.4])
        self.assertIsNone(audit["height_ranges_m"]["recorder"])
        self.assertFalse(audit["exact_recorder_height_join"])
        self.assertFalse(audit["time_join"])
        self.assertFalse(audit["effort_standardized"])

    def test_unavailable_recorder_height_is_not_accepted_as_a_known_column(self):
        self.bats[0]["Recorder_height_m"] = 21.0
        with self.assertRaisesRegex(ValueError, "column|schema"):
            self.validated()

    def test_positive_heights_are_required(self):
        for value in (0, -1, None, float("inf"), True):
            with self.subTest(value=value):
                self.insects, self.bats = synthetic_records()
                self.insects[0]["Height_m"] = value
                with self.assertRaises(ValueError):
                    self.validated()

    def test_expected_plot_count_cannot_be_satisfied_by_partial_input(self):
        with self.assertRaises(ValueError):
            self.adapter.validate_records(self.insects, self.bats, expected_plot_count=20)

    def test_zip_xml_loader_handles_relationships_shared_and_inline_strings(self):
        result = self.load_synthetic(synthetic_archive(), strict_source=False)
        self.assertEqual(result["plots"][0]["passes"], [14, 22])
        self.assertEqual(result["plots"][0]["resources"]["lepidoptera"], [109, 218])
        audit = result["source_audit"]
        self.assertEqual(audit["bat_rows"], 8)
        self.assertEqual(audit["insect_rows"], 4)
        self.assertEqual(audit["formula_cache_count"], 8)
        self.assertTrue(audit["formula_cache_check"])
        self.assertFalse(audit["strict_source_hashes"])
        self.assertEqual(len(audit["checksums"]["archive_sha256"]), 64)
        self.assertNotIn("synthetic-active", str(audit))

    def test_unpinned_archive_is_rejected_by_default(self):
        with self.assertRaisesRegex(ValueError, "SHA|checksum|hash"):
            self.load_synthetic(synthetic_archive())

    def test_absent_or_stale_formula_cache_is_rejected(self):
        for option in ("missing_cache", "stale_cache", "formula_missing"):
            with self.subTest(option=option):
                with self.assertRaises(ValueError):
                    self.load_synthetic(synthetic_archive(**{option: True}), strict_source=False)

    def test_boolean_count_in_actual_xml_is_rejected(self):
        self.insects[0][INSECT_TAXA[0]] = True
        with self.assertRaises(ValueError):
            self.load_synthetic(synthetic_archive(self.insects, self.bats), strict_source=False)

    def test_nonintegral_xml_count_cannot_round_to_integer_or_zero(self):
        # Break caught: converting XML decimals to float before count checks.
        for field, value in ((INSECT_TAXA[0], Decimal("1.0000000000000000001")),
                             (INSECT_TAXA[-1], Decimal("1e-1000"))):
            with self.subTest(field=field):
                self.insects, self.bats = synthetic_records()
                if field == INSECT_TAXA[-1]:
                    self.insects[0][field] = 0
                    self.insects[0]["Total_individuals"] = 253
                self.insects[0][field] = value
                with self.assertRaises(ValueError):
                    self.load_synthetic(synthetic_archive(self.insects, self.bats), strict_source=False)

    def test_missing_xml_count_cell_is_not_zero(self):
        with self.assertRaises(ValueError):
            self.load_synthetic(synthetic_archive(missing_cell="D2"), strict_source=False)

    def test_duplicate_xml_cell_addresses_are_rejected(self):
        payload = synthetic_xlsx(BAT_COLUMNS, self.bats, duplicate_cell=True)
        with self.assertRaisesRegex(ValueError, "duplicate.*cell|cell.*duplicate"):
            self.adapter.parse_xlsx_bytes(payload)

    def test_inline_only_xlsx_can_be_parsed(self):
        payload = synthetic_xlsx(BAT_COLUMNS, self.bats, formula_total=True, shared=False)
        parsed = self.adapter.parse_xlsx_bytes(payload)
        self.assertEqual(parsed["Data"][1]["A"].value, "Plot")
        self.assertEqual(parsed["Data"][2]["A"].value, "synthetic-active")
        self.assertEqual(parsed["Data"][2]["U"].value, 8)
        self.assertIsNotNone(parsed["Data"][2]["U"].formula)


if __name__ == "__main__":
    unittest.main()
