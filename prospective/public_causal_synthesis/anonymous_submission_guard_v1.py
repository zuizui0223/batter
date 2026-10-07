#!/usr/bin/env python3
"""Submission-format and anonymization guard for Behavioral Ecology."""

from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
P = HERE / "COMPLETE_ANONYMOUS_TEXT_V1.md"
text = P.read_text(encoding="utf-8")

def words(s):
    return len(re.findall(r"\S+", s))

if not text.startswith("# Lay Summary\n"):
    raise SystemExit("STOP: Complete Anonymous Text must begin with Lay Summary")

title_match = re.search(r"^# (Individual organization remains detectable across acute perturbations in bats)$", text, re.M)
if not title_match:
    raise SystemExit("STOP: manuscript title missing or altered")

title = title_match.group(1)
if len(title) > 100:
    raise SystemExit(f"STOP: title is {len(title)} characters (>100)")

lay_match = re.search(r"^# Lay Summary\n\n([\s\S]*?)\n\n# Individual organization", text, re.M)
if not lay_match:
    raise SystemExit("STOP: lay summary block not found")
lay_n = words(lay_match.group(1))
if lay_n > 75:
    raise SystemExit(f"STOP: lay summary is {lay_n} words (>75)")

abs_match = re.search(r"^## Abstract\n\n([\s\S]*?)\n\n\*\*Keywords:", text, re.M)
if not abs_match:
    raise SystemExit("STOP: abstract block not found")
abs_n = words(abs_match.group(1))
if abs_n > 250:
    raise SystemExit(f"STOP: abstract is {abs_n} words (>250)")

# Required section order.
required_order = [
    "# Lay Summary",
    "# Individual organization remains detectable across acute perturbations in bats",
    "## Abstract",
    "# Introduction",
    "# Methods",
    "# Results",
    "# Discussion",
    "# Data and code availability",
    "# References",
    "# Figure legends",
]
positions = []
for token in required_order:
    pos = text.find(token)
    if pos < 0:
        raise SystemExit(f"STOP: required section missing: {token}")
    positions.append(pos)
if positions != sorted(positions):
    raise SystemExit("STOP: Complete Anonymous Text section order is invalid")

# Double-anonymization guard.
for token in [
    "zuizui0223",
    "github.com/zuizui0223",
    "[AUTHOR 1",
    "[CORRESPONDING AUTHOR",
    "ZHANG Ruiqi",
    "張瑞琪",
]:
    if token.lower() in text.lower():
        raise SystemExit(f"STOP: identifying token present: {token}")

if "[ANONYMIZED_REVIEW_ARCHIVE_URL]" not in text:
    raise SystemExit("STOP: anonymized review archive placeholder missing")

# Internal-only labels should not appear.
for token in [
    "**Working target:**",
    "**Status:**",
    "**Author metadata:**",
    "# References — working list",
    "## Figure files",
    "## Disclosure note — draft",
]:
    if token in text:
        raise SystemExit(f"STOP: internal-only token present: {token}")

bad = [(i, ord(ch)) for i, ch in enumerate(text) if ord(ch) < 32 and ch != "\n"]
if bad:
    raise SystemExit(f"STOP: control characters present: {bad[:10]}")

print(f"PASS anonymous submission guard: title={len(title)} chars; abstract={abs_n} words; lay={lay_n} words")
