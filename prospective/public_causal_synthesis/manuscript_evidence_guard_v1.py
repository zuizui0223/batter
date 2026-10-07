#!/usr/bin/env python3
"""Static submission-package evidence/provenance guard v2."""

from pathlib import Path

HERE = Path(__file__).resolve().parent

FILES = {
    "manuscript": HERE / "MANUSCRIPT_DRAFT_V1.md",
    "anonymous": HERE / "MANUSCRIPT_ANONYMIZED_BEHAVIORAL_ECOLOGY_V1.md",
    "master": HERE / "MASTER_RESULTS_TABLE_V1.md",
    "figure_plan": HERE / "FIGURE_PLAN_V1.md",
    "captions": HERE / "FIGURE_CAPTIONS_V1.md",
    "supplement": HERE / "SUPPLEMENTARY_MATERIAL_DRAFT_V1.md",
    "claims": HERE / "ABSTRACT_AND_CLAIMS_V1.md",
}

texts = {k: p.read_text(encoding="utf-8") for k, p in FILES.items()}

manuscript = texts["manuscript"]
anonymous = texts["anonymous"]
master = texts["master"]

required_manuscript = [
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
]

for token in required_manuscript:
    if token not in manuscript:
        raise SystemExit(f"STOP: required manuscript evidence token missing: {token!r}")

# Anonymous manuscript must carry the same central evidence hierarchy.
for token in [
    "FAIL_PRIMARY_FORMATION_RULE",
    "L_obs = **+112.5554**",
    "Q = **+144.079**",
    "randomized two-sided P = **0.3244**",
    "K=+0.55428",
    "K=+0.34758",
    "K=-0.0350",
]:
    if token not in anonymous:
        raise SystemExit(f"STOP: anonymous manuscript stale/missing token: {token!r}")

# Master table must preserve evidence tiers.
for token in [
    "**PRIMARY FAIL**",
    "**SUPPORTED SECONDARY**",
    "**POST-PRIMARY DIAGNOSTIC**",
    "**FAIL TREATMENT EFFECT**",
    "**FAILED FROZEN GATE**",
    "**EXPLORATORY ONLY**",
]:
    if token not in master:
        raise SystemExit(f"STOP: master evidence tier missing: {token!r}")

forbidden_anywhere = [
    "Held-out environment prediction was also supported",
    "held-out prediction p = 0.0002",
    "held-out environment prediction p = 0.0002",
    "SUPPORTED, non-randomized history refinement",
    "personal organization is substantially refined through individual history",
]

for label, text in texts.items():
    for token in forbidden_anywhere:
        if token in text:
            raise SystemExit(f"STOP: stale/over-promoted token in {label}: {token!r}")

# Q=144 may appear only when its post-primary status is explicit in the same file.
for label, text in texts.items():
    if ("144.079" in text or "144.08" in text) and not any(
        marker in text
        for marker in [
            "post-primary",
            "POST-PRIMARY",
            "cannot rescue",
            "diagnostic",
            "Diagnostic",
        ]
    ):
        raise SystemExit(f"STOP: Q=144 appears without diagnostic boundary in {label}")

# Submission package must explicitly retain wild provenance boundary.
for label in ["manuscript", "anonymous", "master", "figure_plan", "captions", "supplement"]:
    text = texts[label]
    if "2/4" not in text and "two-of-four" not in text.lower():
        raise SystemExit(f"STOP: wild 2/4 boundary missing from {label}")
    if "exploratory" not in text.lower():
        raise SystemExit(f"STOP: post-outcome exploratory boundary missing from {label}")

# No hidden control characters except newline.
for label, text in texts.items():
    bad = [(i, ord(ch)) for i, ch in enumerate(text) if ord(ch) < 32 and ch != "\n"]
    if bad:
        raise SystemExit(f"STOP: control characters in {label}: {bad[:10]}")

print("PASS submission-package evidence/provenance guard v2")
