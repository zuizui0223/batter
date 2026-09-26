from __future__ import annotations

import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MS=ROOT/"manuscript/MOVEMENT_ECOLOGY_MANUSCRIPT_V1.md"

def section(text, start, end):
    return text.split(start,1)[1].split(end,1)[0]

def test_required_research_sections_present():
    t=MS.read_text()
    required=[
      "## Abstract","### Background","### Methods","### Results","### Conclusions",
      "## Background","## Methods","## Results","## Discussion","## Conclusions",
      "## List of abbreviations","## Declarations",
      "### Ethics approval and consent to participate",
      "### Consent for publication","### Availability of data and materials",
      "### Competing interests","### Funding","### Authors' contributions","### Acknowledgements"
    ]
    for x in required:
        assert x in t

def test_structured_abstract_under_350_words():
    t=MS.read_text()
    a=section(t,"## Abstract","**Keywords:**")
    words=re.findall(r"\b[\w*.-]+\b",a)
    assert len(words)<=350, len(words)

def test_key_claims_and_boundaries():
    t=MS.read_text()
    assert "P=0.0001736" in t
    assert "0.1605" in t
    assert "only four of eight" in t.lower()
    assert "height above mean sea level" in t
    assert "do not interpret this variable as height above ground" in t
    assert "not independent replication" in t.lower()

def test_no_strong_spatial_strategy_overclaim():
    t=MS.read_text().lower()
    forbidden=[
      "eight distinct vertical strategies",
      "each bat has its own vertical strategy",
      "individual-by-location vertical interaction was supported",
      "height above ground was used as the vertical axis"
    ]
    for x in forbidden:
        assert x not in t

def test_exact_individual_replication_logic():
    t=MS.read_text()
    assert "8! = 40,320" in t
    assert "events are independent replicates" not in t.lower()
