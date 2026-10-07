#!/usr/bin/env python3
"""Behavioral Ecology anonymous-manuscript format guard v1."""

from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
P=HERE/"MANUSCRIPT_ANONYMIZED_BEHAVIORAL_ECOLOGY_V1.md"
text=P.read_text(encoding="utf-8")

forbidden=[
    "zuizui0223",
    "github.com/zuizui0223",
    "**Author metadata:**",
    "**Working target:**",
    "**Status:**",
]
for token in forbidden:
    if token.lower() in text.lower():
        raise SystemExit(f"STOP identifying/internal token in anonymous manuscript: {token!r}")

required_order=[
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
positions=[]
for token in required_order:
    pos=text.find(token)
    if pos<0:
        raise SystemExit(f"STOP required anonymous section missing: {token!r}")
    positions.append(pos)
if positions != sorted(positions):
    raise SystemExit(f"STOP anonymous section order invalid: {list(zip(required_order,positions))}")

def section(start_token,end_token):
    s=text.index(start_token)+len(start_token)
    e=text.index(end_token,s)
    return text[s:e].strip()

lay=section("# Lay Summary","# Individual organization remains detectable across acute perturbations in bats")
lay_words=len(re.findall(r"\b\S+\b",lay))
if lay_words>75:
    raise SystemExit(f"STOP Lay Summary too long: {lay_words} words")

abstract=section("## Abstract","**Keywords:**")
abstract_words=len(re.findall(r"\b\S+\b",abstract))
if abstract_words>250:
    raise SystemExit(f"STOP abstract too long: {abstract_words} words")

if "[ANONYMIZED_REVIEW_ARCHIVE_URL]" not in text:
    raise SystemExit("STOP anonymous archive placeholder missing")

if "FAIL_PRIMARY_FORMATION_RULE" not in text:
    raise SystemExit("STOP frozen formation-primary failure missing")
if "post-primary" not in text.lower():
    raise SystemExit("STOP post-primary evidence-tier wording missing")
if "2/4" not in text or "FAIL" not in text:
    raise SystemExit("STOP frozen wild bridge failure missing")

bad=[(i,ord(ch)) for i,ch in enumerate(text) if ord(ch)<32 and ch!="\n"]
if bad:
    raise SystemExit(f"STOP control characters in anonymous manuscript: {bad[:10]}")

print(f"PASS Behavioral Ecology anonymous manuscript guard v1; lay={lay_words}; abstract={abstract_words}")
