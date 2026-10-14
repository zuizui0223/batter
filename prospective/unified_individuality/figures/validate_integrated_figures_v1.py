#!/usr/bin/env python3
"""Static, dependency-free QA of unified paper's source-backed SVG figures.

Run after generate_integrated_figures_v1.cjs.
This validator checks figure source semantics, unambiguous counts, basic SVG
structure and visualization labels. It is not a raw-data replication or
pixel-level figure review.
"""
from __future__ import annotations

from pathlib import Path
import json
import math
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "FROZEN_FIGURE_DATA_V1.json").read_text(encoding="utf-8"))
IMAGES = [
    "FIGURE_1_INFERENTIAL_LAYERS_V1.svg",
    "FIGURE_2_HISTORY_AND_DEVELOPMENT_V1.svg",
    "FIGURE_3_ACUTE_CORRESPONDENCE_V1.svg",
    "FIGURE_4_PORTABILITY_AND_BRIDGE_V1.svg",
    "FIGURE_5_CENTERED_VERTICAL_IDENTITY_V1.svg",
    "FIGURE_6_FIDELITY_VS_PARTITIONING_V1.svg",
]
SVG_NS = "{http://www.w3.org/2000/svg}"


def close(actual: float, expected: float, name: str) -> None:
    assert math.isclose(actual, expected, abs_tol=1e-9), f"{name} drift: {actual} != {expected}"


def science_gate() -> None:
    assert DATA["meta"]["wild_branch"] == "release/jae-v0.4.0-rc2"
    assert DATA["meta"]["be_branch"] == "prospective/public-causal-synthesis-v1"
    assert len(DATA["meta"]["source_files"]) == 8
    cen = DATA["centered"]
    assert len(cen) == 6
    assert sum(bool(x["supported"]) for x in cen) == 5
    assert len([x for x in cen if x["panel"] == "tadarida" and not x["supported"]]) == 1
    close(next(x for x in cen if x["panel"] == "tadarida")["p_upper"], 0.5121, "focal p")
    close(next(x for x in cen if x["panel"] == "phyllostomus_2016")["calibrated_excess"], 0.573986824453972, "P2016 shape")

    terrain = DATA["terrain"]
    ids = ["hypsignathus", "phyllostomus_2022", "phyllostomus_2023", "phyllostomus_2016"]
    assert [x["panel"] for x in terrain] == ids
    assert len(terrain) == 4
    assert sum(bool(x["v_supported"]) for x in terrain) == 4
    assert sum(x["s_rel"] > 0 and x["s_p_two_sided"] <= 0.05 for x in terrain) == 0
    assert sum(bool(x["couse_supported"]) for x in terrain) == 1
    assert [x["couse_tolerance_s"] for x in terrain] == [60, 60, 600, 600]
    assert [x["couse_scope"] for x in terrain] == [
        "endpoint_excluded", "endpoint_excluded", "all_space", "endpoint_excluded"
    ], "Source co-use scopes were changed"
    assert [x["couse_n_dyads"] for x in terrain] == [22, 10, 8, 8]
    for x in terrain:
        assert x["s_q025"] <= x["s_q975"], "S interval inverted"
        assert x["couse_boot_q025_m"] <= x["couse_excess_m"] <= x["couse_boot_q975_m"], "co-use interval mismatch"
    assert terrain[0]["s_rel"] < terrain[0]["s_q025"], "Hypsignathus negative-tail S result lost"
    close(terrain[0]["s_p_two_sided"], 0.0362, "H S p2")
    close(terrain[2]["couse_excess_m"], 3.5737278739273783, "2023 co-use")
    close(terrain[2]["couse_p_upper"], 0.0231, "2023 phase p")
    assert DATA["lab"]["juvenile"]["sign_positive"] == 8
    assert DATA["lab"]["juvenile"]["sign_gate"] == 10
    assert sum(v > 0 for v in DATA["lab"]["juvenile"]["slopes_rounded"]) == 8
    assert len(DATA["lab"]["juvenile"]["slopes_rounded"]) == 14
    assert len(DATA["lab"]["acute"]) == 4
    assert [x["n"] for x in DATA["lab"]["acute"]] == [6, 3, 4, 4]
    assert len(DATA["lab"]["portability"]) == 3
    assert [x["status"] for x in DATA["lab"]["portability"]] == ["SUPPORTED", "SUPPORTED", "UNSUPPORTED"]
    assert DATA["lab"]["bridge"]["outcomes"] == ["PASS", "PASS", "FAIL", "STRUCTURAL STOP"]
    assert DATA["lab"]["bridge"]["criterion"] == 3


def svg_gate() -> None:
    for name in IMAGES:
        file = HERE / name
        assert file.is_file(), f"SVG missing: {name}"
        text = file.read_text(encoding="utf-8")
        assert text.startswith("<svg"), f"{name}: missing root"
        assert "</svg>" in text and "<script" not in text, f"{name}: unsafe/invalid"
        assert not any(v in text for v in ["NaN", "undefined", "javascript:", "<foreignObject", "<script"]), f"{name}: invalid value"
        root = ET.fromstring(text)
        assert root.tag == SVG_NS + "svg", f"{name}: invalid XML namespace"
        bounds = root.attrib["viewBox"].split()
        assert len(bounds) == 4
        width, height = float(bounds[2]), float(bounds[3])
        assert width >= 1000 and height >= 500
        labels = root.findall(".//" + SVG_NS + "text")
        assert len(labels) >= 20, f"{name}: missing labels"
        for item in labels:
            x, y = float(item.attrib["x"]), float(item.attrib["y"])
            assert 0 <= x <= width and 0 <= y <= height, f"{name}: label out of viewBox at {(x,y)}"
        print(f"XML + text anchors OK: {name}, text elements={len(labels)}")

    f5 = (HERE / IMAGES[4]).read_text(encoding="utf-8")
    for tok in ["E. helvum", "H. monstrosus", "P. hastatus 2022", "P. hastatus 2023", "P. hastatus 2016", "T. teniotis", "0.5121", "+0.574"]:
        assert tok in f5, f"centered-shape figure missing {tok}"
    f6 = (HERE / IMAGES[5]).read_text(encoding="utf-8")
    for tok in ["4 / 4 supported", "0 / 4 positive supported", "1 / 4 supported", "p2=0.036", "p+ = 0.0231", "+3.57 m", "2016 also uses 600s"]:
        assert tok in f6, f"field figure missing {tok}"


if __name__ == "__main__":
    science_gate()
    svg_gate()
    print("PASS — immutable-source summary semantics and SVG/XML structural gates")
