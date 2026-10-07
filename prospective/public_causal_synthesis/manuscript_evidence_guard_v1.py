#!/usr/bin/env python3
"""Static manuscript evidence/provenance guard v1."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
MANUSCRIPT = HERE / "MANUSCRIPT_DRAFT_V1.md"

text = MANUSCRIPT.read_text(encoding="utf-8")

required = [
    "FAIL_PRIMARY_FORMATION_RULE",
    "B_obs = **+0.16733**",
    "L_obs = **+112.5554**",
    "Q = **+144.079**",
    "randomized two-sided P = **0.3244**",
    "D=+0.734699",
    "P=0.167785",
    "D=-1.425497",
    "P=0.716667",
    "K=+4.941",
    "K=+6.779",
    "A=+0.377542",
    "K=+1.004452",
    "K=+3.695264",
    "K=+0.55428",
    "K=+0.34758",
    "K=-0.0350",
    "2/4",
    "FAIL",
    "not as a preregistered multi-study experiment",
    "not as a prospectively preregistered multi-study meta-analysis",
]

for token in required:
    if token not in text:
        raise SystemExit(f"STOP: required manuscript evidence token missing: {token!r}")

forbidden = [
    "Held-out environment prediction was also supported",
    "held-out prediction p = 0.0002",
    "SUPPORTED, non-randomized history refinement",
    "personal organization is substantially refined through individual history",
]

for token in forbidden:
    if token in text:
        raise SystemExit(f"STOP: stale/over-promoted manuscript token present: {token!r}")

# No hidden control characters except newline.
bad = [(i, ord(ch)) for i, ch in enumerate(text) if ord(ch) < 32 and ch != "\n"]
if bad:
    raise SystemExit(f"STOP: control characters in manuscript: {bad[:10]}")

print("PASS manuscript evidence/provenance guard v1")
