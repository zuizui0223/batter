#!/usr/bin/env python3
"""Submission-format guard for COMPLETE_ANONYMOUS_TEXT_V1.md."""

from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
P=HERE/"COMPLETE_ANONYMOUS_TEXT_V1.md"
text=P.read_text(encoding="utf-8")

problems=[]

if re.search(r"(?m)^\[$",text) or re.search(r"(?m)^\]$",text):
    problems.append("raw square-bracket equation delimiter")
if re.search(r"\bP\s+le\s+",text):
    problems.append("raw 'P le' comparison")
if "^circ" in text:
    problems.append("raw ^circ degree notation")
if re.search(r"[A-Za-z]_\{[^}]+\}",text):
    problems.append("raw TeX-style subscript")

# Lists need explicit paragraph boundaries for stable Pandoc conversion.
lines=text.splitlines()
for i,line in enumerate(lines):
    if re.match(r"^\s*-\s+\S",line):
        # Reference entries are intentionally plain paragraphs after normalization,
        # so any remaining dash is a real list and should start after a blank line.
        if i>0 and lines[i-1].strip() and not re.match(r"^\s*-\s+\S",lines[i-1]):
            problems.append(f"list without blank-line boundary at line {i+1}")
            break

# References should be paragraphs, not bullet entries.
in_refs=False
for i,line in enumerate(lines):
    s=line.strip()
    if s=="# References":
        in_refs=True
        continue
    if in_refs and s.startswith("# ") and s!="# References":
        in_refs=False
    if in_refs and re.match(r"^\s*-\s+\S",line):
        problems.append(f"reference retained as bullet at line {i+1}")
        break

if problems:
    raise SystemExit("STOP anonymous submission-format guard: "+"; ".join(problems))

print("PASS anonymous submission-format guard v1")
