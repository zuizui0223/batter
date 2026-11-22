"""Read the pinned Cistrone supplements privately with Python's stdlib.

``load_archive(path)`` reads the outer ZIP and both XLSX packages in memory.
It never extracts or rewrites them. Its ``plots`` result contains private
plot-level data and must not be printed, committed, or included in a public
receipt. Only ``source_audit`` is a redacted aggregate suitable for reporting.

``validate_records`` exposes the same structural checks to synthetic tests.
``strict_source=False`` allows a synthetic package through the loader; it does
not assert that the package is the pinned study source. No calendar, recording
duration, trapping duration, or exact recorder height is inferred from labels,
tree heights, or trap heights. Formula caches are checked against the explicitly
enumerated species counts; this is not a general Excel calculation engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO
import math
from pathlib import Path
import posixpath
import re
from typing import Any, Mapping, Sequence
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


ADAPTER_VERSION = "cistrone_supplement_adapter_v1"
SOURCE_ARCHIVE_SHA256 = "3eed7ceeb9c1201a3e8594c6d28115d268a7c64e1c1acdccfb6e5d50da872653"
SOURCE_WORKBOOK_SHA256 = {
    "mmc1": "7220410f012954b82ae12d33a06d0a6ff70abb66aaa7e17a5aaaf874242f9259",
    "mmc2": "adcfc18635b5f7d804dad496f3f5108f642a86ba4aaec6d90a932c724148531d",
}
SOURCE_WORKBOOK_NAMES = {
    key: f"1-s2.0-S0378112726008807-{key}.xlsx" for key in SOURCE_WORKBOOK_SHA256
}
# Source precision permits a 0.01 percentage-point complement discrepancy.
# This tolerance validates the input and never adjusts either measurement.
CANOPY_COMPLEMENT_TOLERANCE_PP = 0.010000001

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
LEPIDOPTERA_TAXA = (
    "Agrotis ipsilon", "Alcis bastelbergi", "Amata phegea",
    "Arctornis l-nigrum", "Biston betularia", "Lymantria monacha",
    "Crambus pascuella", "Tuta absoluta", "Eilema caniola", "Orgyia antiqua",
    "Catocala ilia", "Pscoparia basistrigalis", "Eudonia lacustrata",
    "Tineola bisselliella",
)
DIPTERA_TAXA = (
    "Scathophaga stercoraria", "Brevicornu foliatum",
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
STAND_COLUMNS = ("Mean_basal_area_m2_ha", "Mean_DBH_cm", "Mean_tree_height_m")
STRATA = ("ground", "canopy")
NIGHTS = (1, 2)
_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
_CELL_REFERENCE = re.compile(r"([A-Z]+)([1-9][0-9]*)\Z")


class ValidationError(ValueError):
    """Source structure or values violate the stated adapter contract."""


@dataclass(frozen=True)
class Cell:
    """Cached cell value and optional formula; a blank is None, never zero."""

    value: Any
    formula: str | None = None


def _tag(local: str) -> str:
    return "{" + _MAIN + "}" + local


def _unique_zip_names(archive: ZipFile) -> None:
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValidationError("duplicate ZIP member name")


def _xml(archive: ZipFile, member: str) -> ET.Element:
    try:
        return ET.fromstring(archive.read(member))
    except (KeyError, ET.ParseError) as error:
        raise ValidationError("missing or malformed required XLSX XML part") from error


def _target(relationship: ET.Element) -> str:
    target = relationship.get("Target", "")
    if relationship.get("TargetMode") == "External" or ":" in target or "\\" in target:
        raise ValidationError("external or invalid XLSX relationship")
    result = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                 else posixpath.join("xl", target))
    if not target or result.startswith("../") or result == "..":
        raise ValidationError("invalid XLSX relationship target")
    return result


def _rich_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    parts = []
    for child in element:
        if child.tag == _tag("t"):
            parts.append(child.text or "")
        elif child.tag == _tag("r"):
            parts.extend(node.text or "" for node in child.findall(_tag("t")))
    return "".join(parts)


def _numeric_xml(text: str) -> int | Decimal:
    try:
        value = Decimal(text)
    except InvalidOperation as error:
        raise ValidationError("invalid numeric XLSX cell") from error
    if not value.is_finite():
        raise ValidationError("nonfinite numeric XLSX cell")
    if value == value.to_integral_value():
        return int(value)
    # Keep the exact decimal until the field's semantics are known. A float
    # conversion here could turn a fractional count into an integer or zero.
    return value


def _read_cell(element: ET.Element, shared: list[str]) -> Cell:
    formula_element = element.find(_tag("f"))
    formula = None if formula_element is None else (formula_element.text or "")
    value_element = element.find(_tag("v"))
    text = None if value_element is None else value_element.text
    kind = element.get("t", "n")
    if formula is not None and (text is None or text == ""):
        raise ValidationError("formula cell has no cached value")
    if kind == "inlineStr":
        value = _rich_text(element.find(_tag("is")))
    elif text is None or text == "":
        value = None
    elif kind == "s":
        if not text.isdecimal() or int(text) >= len(shared):
            raise ValidationError("invalid shared-string index")
        value = shared[int(text)]
    elif kind in ("str", "d"):
        value = text
    elif kind == "b":
        if text not in ("0", "1"):
            raise ValidationError("invalid Boolean XLSX cell")
        value = text == "1"
    elif kind == "e":
        raise ValidationError("spreadsheet error cell")
    elif kind == "n":
        value = _numeric_xml(text)
    else:
        raise ValidationError("unsupported XLSX cell type")
    return Cell(value, formula)


def parse_xlsx_bytes(data: bytes) -> dict[str, dict[int, dict[str, Cell]]]:
    """Read named worksheets using workbook relationships, without extraction.

    Returned rows are keyed by their Excel row numbers and column letters.
    Strings remain strings, Booleans remain Booleans, numeric cells become
    finite ints/Decimals, and missing cells are not synthesized.
    """
    try:
        with ZipFile(BytesIO(data)) as archive:
            _unique_zip_names(archive)
            workbook = _xml(archive, "xl/workbook.xml")
            rels_root = _xml(archive, "xl/_rels/workbook.xml.rels")
            relationships = {}
            for relationship in rels_root.findall("{" + _PKG + "}Relationship"):
                identifier = relationship.get("Id")
                if not identifier or identifier in relationships:
                    raise ValidationError("duplicate or missing XLSX relationship ID")
                relationships[identifier] = relationship
            shared = []
            string_parts = [r for r in relationships.values()
                            if r.get("Type", "").endswith("/sharedStrings")]
            if len(string_parts) > 1:
                raise ValidationError("multiple XLSX shared-string parts")
            if string_parts:
                shared = [_rich_text(item) for item in _xml(
                    archive, _target(string_parts[0])).findall(_tag("si"))]
            result = {}
            for sheet in workbook.findall(_tag("sheets") + "/" + _tag("sheet")):
                name, rid = sheet.get("name"), sheet.get("{" + _REL + "}id")
                if not name or name in result or rid not in relationships:
                    raise ValidationError("duplicate or invalid XLSX sheet metadata")
                relation = relationships[rid]
                if not relation.get("Type", "").endswith("/worksheet"):
                    raise ValidationError("sheet relationship is not a worksheet")
                root = _xml(archive, _target(relation))
                rows = {}
                for row in root.findall(_tag("sheetData") + "/" + _tag("row")):
                    row_text = row.get("r", "")
                    if not row_text.isdecimal() or int(row_text) < 1:
                        raise ValidationError("invalid XLSX row number")
                    number = int(row_text)
                    if number in rows:
                        raise ValidationError("duplicate XLSX row number")
                    cells = {}
                    for element in row.findall(_tag("c")):
                        match = _CELL_REFERENCE.fullmatch(element.get("r", ""))
                        if match is None or int(match.group(2)) != number:
                            raise ValidationError("invalid or mismatched XLSX cell address")
                        column = match.group(1)
                        if column in cells:
                            raise ValidationError("duplicate XLSX cell address")
                        cells[column] = _read_cell(element, shared)
                    rows[number] = cells
                result[name] = rows
            return result
    except BadZipFile as error:
        raise ValidationError("invalid XLSX ZIP package") from error


def _count(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValidationError(f"{field} must be a nonnegative integer count")
    if isinstance(value, Decimal) and (
            not value.is_finite() or value != value.to_integral_value()):
        raise ValidationError(f"{field} must be a finite integer count")
    if isinstance(value, float) and (not math.isfinite(value) or not value.is_integer()):
        raise ValidationError(f"{field} must be a finite integer count")
    if value < 0:
        raise ValidationError(f"{field} must be a nonnegative integer count")
    return int(value)


def _number(value: Any, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValidationError(f"{field} must be a finite numeric value")
    try:
        number = float(value)
    except OverflowError as error:
        raise ValidationError(f"{field} is outside finite numeric range") from error
    if not math.isfinite(number) or (positive and number <= 0):
        raise ValidationError(f"{field} must be finite" + (" and positive" if positive else ""))
    return number


def _key(row: Mapping[str, Any]) -> tuple[str, str]:
    plot = row["Plot"]
    if not isinstance(plot, str) or not plot or plot.strip() != plot:
        raise ValidationError("Plot must be a nonempty exact string identifier")
    stratum = row["Stratum"]
    if stratum not in STRATA:
        raise ValidationError("Stratum must be exactly ground or canopy")
    return plot, stratum


def _schema(row: Mapping[str, Any], columns: tuple[str, ...], domain: str) -> None:
    if not isinstance(row, Mapping) or set(row) != set(columns):
        raise ValidationError(f"{domain} column schema is incomplete or unexpected")


def _range(values: Sequence[float]) -> list[float]:
    return [min(values), max(values)]


def validate_records(insect_rows: Sequence[Mapping[str, Any]],
                     bat_rows: Sequence[Mapping[str, Any]], *,
                     expected_plot_count: int | None = None) -> dict[str, Any]:
    """Validate exact source-column records and build private paired inputs.

    There is one insect record per plot and stratum and one bat record per
    plot, stratum and night (1 or 2). Each input must contain its full schema.
    Missing counts, false-valued Booleans, duplicate keys and incomplete joins
    are errors. An observed zero remains zero, including all-zero bat plots.
    ``baseline`` is openness canopy-minus-ground, mean of two station nightly
    minima, stand basal area, stand DBH and stand mean tree height, in that order.
    """
    if not insect_rows or not bat_rows:
        raise ValidationError("insect and bat records must both be nonempty")
    if expected_plot_count is not None and (
            isinstance(expected_plot_count, bool) or not isinstance(expected_plot_count, int)
            or expected_plot_count <= 0):
        raise ValidationError("expected_plot_count must be a positive integer")
    insects, bats = {}, {}
    complement_errors = []
    for original in insect_rows:
        _schema(original, INSECT_COLUMNS, "insect")
        key = _key(original)
        if key in insects:
            raise ValidationError("duplicate insect plot-stratum key")
        row = dict(original)
        for field in (*INSECT_TAXA, "Total_individuals", "n_traps"):
            row[field] = _count(row[field], field)
        if sum(row[taxon] for taxon in INSECT_TAXA) != row["Total_individuals"]:
            raise ValidationError("insect Total_individuals does not equal all 23 taxa")
        if row["n_traps"] != 1:
            raise ValidationError("n_traps must equal one in every insect sample")
        for field in ("Clear_canopy_%", "Canopy_cover_%"):
            row[field] = _number(row[field], field)
            if not 0 <= row[field] <= 100:
                raise ValidationError(f"{field} must be in [0, 100]")
        error = abs(row["Clear_canopy_%"] + row["Canopy_cover_%"] - 100.0)
        if error > CANOPY_COMPLEMENT_TOLERANCE_PP:
            raise ValidationError("canopy cover and openness do not sum to 100 within source precision")
        complement_errors.append(error)
        row["Height_m"] = _number(row["Height_m"], "insect Height_m", positive=True)
        insects[key] = row
    for original in bat_rows:
        _schema(original, BAT_COLUMNS, "bat")
        pair = _key(original)
        row = dict(original)
        row["Night"] = _count(row["Night"], "Night")
        if row["Night"] not in NIGHTS:
            raise ValidationError("Night must be one or two")
        key = (*pair, row["Night"])
        if key in bats:
            raise ValidationError("duplicate bat plot-stratum-night key")
        for field in (*BAT_SPECIES, "Total_bat_passes"):
            row[field] = _count(row[field], field)
        if sum(row[species] for species in BAT_SPECIES) != row["Total_bat_passes"]:
            raise ValidationError("bat Total_bat_passes cache does not equal all 17 species groups")
        for field in ("Temp_min", *STAND_COLUMNS):
            row[field] = _number(row[field], field)
        bats[key] = row
    plot_ids = {key[0] for key in insects}
    if expected_plot_count is not None and len(plot_ids) != expected_plot_count:
        raise ValidationError("unexpected number of plots")
    if {key[0] for key in bats} != plot_ids:
        raise ValidationError("exact insect-bat plot join failed")
    expected_insects = {(plot, stratum) for plot in plot_ids for stratum in STRATA}
    expected_bats = {(*pair, night) for pair in expected_insects for night in NIGHTS}
    if set(insects) != expected_insects or set(bats) != expected_bats:
        raise ValidationError("unbalanced or missing plot-stratum-night join")
    plots = []
    for plot in sorted(plot_ids):
        four = [bats[plot, stratum, night] for stratum in STRATA for night in NIGHTS]
        for field in STAND_COLUMNS:
            if len({row[field] for row in four}) != 1:
                raise ValidationError(f"stand metadata {field} is not constant within plot")
        for night in NIGHTS:
            if bats[plot, "ground", night]["Temp_min"] != bats[plot, "canopy", night]["Temp_min"]:
                raise ValidationError("station temperature differs within plot-night")
        plots.append({
            "plot_id": plot,
            "passes": [sum(bats[plot, stratum, night]["Total_bat_passes"]
                           for night in NIGHTS) for stratum in STRATA],
            "baseline": [
                insects[plot, "canopy"]["Clear_canopy_%"] - insects[plot, "ground"]["Clear_canopy_%"],
                sum(bats[plot, "ground", night]["Temp_min"] for night in NIGHTS) / 2.0,
                *[four[0][field] for field in STAND_COLUMNS],
            ],
            "resources": {
                label: [sum(insects[plot, stratum][taxon] for taxon in taxa)
                        for stratum in STRATA]
                for label, taxa in (("total", INSECT_TAXA),
                                    ("lepidoptera", LEPIDOPTERA_TAXA),
                                    ("diptera", DIPTERA_TAXA))
            },
        })
    audit = {
        "adapter_version": ADAPTER_VERSION,
        "insect_rows": len(insects), "bat_rows": len(bats),
        "insect_taxa": len(INSECT_TAXA), "bat_species_groups": len(BAT_SPECIES),
        "plot_pairs": len(plots), "matched_plot_stratum_pairs": len(insects),
        "nights_per_plot": 2,
        "resource_taxon_counts": {"total": 23, "lepidoptera": 14, "diptera": 4, "other": 5},
        "totals": {
            "insect_individuals": sum(row["Total_individuals"] for row in insects.values()),
            "bat_passes": sum(row["Total_bat_passes"] for row in bats.values()),
            "insect_by_stratum": {s: sum(row["Total_individuals"] for key, row in insects.items()
                                         if key[1] == s) for s in STRATA},
            "bat_passes_by_stratum": {s: sum(row["Total_bat_passes"] for key, row in bats.items()
                                           if key[1] == s) for s in STRATA},
            "lepidoptera_individuals": sum(sum(p["resources"]["lepidoptera"]) for p in plots),
            "diptera_individuals": sum(sum(p["resources"]["diptera"]) for p in plots),
        },
        "zero_pass_plots": sum(sum(plot["passes"]) == 0 for plot in plots),
        "zero_pass_plot_stratum_pairs": sum(total == 0 for p in plots for total in p["passes"]),
        "zero_pass_recorder_nights": sum(r["Total_bat_passes"] == 0 for r in bats.values()),
        "zero_insect_samples": sum(r["Total_individuals"] == 0 for r in insects.values()),
        "height_ranges_m": {
            "insect_trap": {s: _range([row["Height_m"] for key, row in insects.items()
                                       if key[1] == s]) for s in STRATA},
            "stand_tree_height": _range([p["baseline"][-1] for p in plots]),
            "recorder": None,
        },
        "canopy_complement_tolerance_pp": CANOPY_COMPLEMENT_TOLERANCE_PP,
        "canopy_complement_max_error_pp": max(complement_errors),
        "strict_coarse_join": True,
        "time_join": False,
        "effort_standardized": False,
        "exact_recorder_height_join": False,
        "calendar_dates_available": False,
        "recording_hours_available": False,
        "insect_trapping_duration_available": False,
        "strict_source_hashes": False,
        "formula_cache_check": False,
        "formula_cache_count": 0,
        "checksums": {},
    }
    return {"source_audit": audit, "plots": plots}


def _column_number(letters: str) -> int:
    number = 0
    for letter in letters:
        number = 26 * number + ord(letter) - ord("A") + 1
    return number


def _records(sheets: dict[str, dict[int, dict[str, Cell]]], columns: tuple[str, ...],
             first_data_row: int, *, require_total_formula: bool = False
             ) -> tuple[list[dict[str, Any]], int]:
    if set(sheets) != {"Data", "Legend"}:
        raise ValidationError("each workbook must contain exactly Data and Legend sheets")
    data = sheets["Data"]
    header = {column: cell.value for column, cell in data.get(1, {}).items()
              if cell.value is not None}
    ordered = sorted(header, key=_column_number)
    if tuple(header[column] for column in ordered) != columns:
        raise ValidationError("XLSX Data header column schema differs from the supplement")
    if first_data_row == 3 and 2 not in data:
        raise ValidationError("missing S1 annotation row")
    rows, count = [], 0
    occupied_rows = [number for number, cells in data.items() if number >= first_data_row
                     and any(cell.value is not None or cell.formula is not None for cell in cells.values())]
    if not occupied_rows or sorted(occupied_rows) != list(range(first_data_row, max(occupied_rows) + 1)):
        raise ValidationError("missing or noncontiguous XLSX data row")
    for number in sorted(occupied_rows):
        cells = data[number]
        if any(column not in header and (cell.value is not None or cell.formula is not None)
               for column, cell in cells.items()):
            raise ValidationError("unexpected XLSX data column")
        record = {header[column]: cells.get(column, Cell(None)).value for column in ordered}
        if require_total_formula:
            total_column = ordered[columns.index("Total_bat_passes")]
            if cells.get(total_column, Cell(None)).formula is None:
                raise ValidationError("bat total must have a formula and cached value")
            count += 1
        rows.append(record)
    return rows, count


def load_archive(path: str | Path, *, strict_source: bool = True) -> dict[str, Any]:
    """Return redacted audit and private normalized plot records from a ZIP.

    Strict mode (default) requires the pinned outer archive and both workbook
    hashes, 20 plots, 40 insect data rows, 80 bat data rows and 80 formula caches.
    Synthetic mode retains every value/structure check but allows other source
    hashes and balanced plot counts. Neither mode writes files.
    """
    archive_bytes = Path(path).read_bytes()
    archive_hash = sha256(archive_bytes).hexdigest()
    if strict_source and archive_hash != SOURCE_ARCHIVE_SHA256:
        raise ValidationError("outer archive SHA256 does not match the pinned source")
    workbook_bytes, workbook_hashes = {}, {}
    try:
        with ZipFile(BytesIO(archive_bytes)) as archive:
            _unique_zip_names(archive)
            for key in SOURCE_WORKBOOK_NAMES:
                candidates = [name for name in archive.namelist()
                              if posixpath.basename(name) == key + ".xlsx"
                              or posixpath.basename(name).endswith("-" + key + ".xlsx")]
                if len(candidates) != 1:
                    raise ValidationError("archive must contain exactly one of each supplement workbook")
                name = candidates[0]
                if strict_source and name != SOURCE_WORKBOOK_NAMES[key]:
                    raise ValidationError("source workbook member name differs from pinned source")
                workbook_bytes[key] = archive.read(name)
                workbook_hashes[key] = sha256(workbook_bytes[key]).hexdigest()
                if strict_source and workbook_hashes[key] != SOURCE_WORKBOOK_SHA256[key]:
                    raise ValidationError("workbook SHA256 does not match the pinned source")
    except BadZipFile as error:
        raise ValidationError("invalid supplement ZIP archive") from error
    insects, _ = _records(parse_xlsx_bytes(workbook_bytes["mmc1"]), INSECT_COLUMNS, 3)
    bats, formula_count = _records(parse_xlsx_bytes(workbook_bytes["mmc2"]), BAT_COLUMNS, 2,
                                   require_total_formula=True)
    result = validate_records(insects, bats, expected_plot_count=20 if strict_source else None)
    if strict_source and (len(insects), len(bats), formula_count) != (40, 80, 80):
        raise ValidationError("pinned source row or formula-cache counts differ")
    result["source_audit"].update({
        "strict_source_hashes": bool(strict_source),
        "formula_cache_check": True,
        "formula_cache_count": formula_count,
        "s1_annotation_rows_skipped": 1,
        "checksums": {"archive_sha256": archive_hash,
                      "workbook_sha256": workbook_hashes},
    })
    return result
