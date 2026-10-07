#!/usr/bin/env python3
"""Static provenance guard for public causal synthesis figures v1."""

from pathlib import Path
import ast
import re

HERE = Path(__file__).resolve().parent
PLOT = HERE / "plot_synthesis_figures_v1.py"
PLAN = HERE / "FIGURE_PLAN_V1.md"
CAPTIONS = HERE / "FIGURE_CAPTIONS_V1.md"
MASTER = HERE / "MASTER_RESULTS_TABLE_V1.md"

plot = PLOT.read_text(encoding="utf-8")
plan = PLAN.read_text(encoding="utf-8")
captions = CAPTIONS.read_text(encoding="utf-8")
master = MASTER.read_text(encoding="utf-8")

# Figure 2A: exact individual slope order/value check.
expected_names = [
    "Anka","Eli","Eva","Fima","K","Mazi","Nadav",
    "Nature","Nazir","Odelia","Shem_Tov","Tishray","Tzedi","V",
]
expected_vals = [
    0.166,0.290,0.259,-0.309,-0.383,-0.121,0.913,
    -0.486,-0.071,0.245,0.647,0.676,0.564,-0.049,
]

m_names = re.search(r'b_names=(\[[^\n]+\])', plot)
m_vals = re.search(r'b_vals=np\.array\((\[[^\n]+\])\)', plot)
if not (m_names and m_vals):
    raise SystemExit("STOP: Figure 2A slope arrays not found")
names = ast.literal_eval(m_names.group(1))
vals = ast.literal_eval(m_vals.group(1))
if names != expected_names:
    raise SystemExit(f"STOP: Figure 2A bat order drift: {names}")
if any(abs(a-b) > 1e-12 for a,b in zip(vals, expected_vals)) or len(vals) != len(expected_vals):
    raise SystemExit(f"STOP: Figure 2A slope values drift: {vals}")

# Figure 2B randomized developmental primaries.
required_plot_tokens = [
    "n=29 (14 enriched / 15 impoverished)",
    "V_enriched=2.656639",
    "V_impoverished=1.921940",
    "D=+0.734699",
    "p=0.167785",
    "UNSUPPORTED INDIVIDUALIZATION",
    "n=10 (5 hearing / 5 deafened)",
    "V_hearing=15.766760",
    "V_deaf=17.192257",
    "D=-1.425497",
    "exact p=0.716667",
    "NO DIFFERENCE IN AMOUNT",
    "n_bio=[6,3,4,4]",
    "positive=[5/6,3/3,4/4,4/4]",
    'rank_labels=["exact p=.04028","rank 1/1296","rank 1/24","rank 2/576"]',
    '("Rhino coarse I/M","SUPPORTED","K=+0.55428; 5/5 positive; p=.0001")',
    '("Carollia fixed Rhino I/M","SUPPORTED","K=+0.34758; p=.0007")',
    '("Carollia fixed detailed geometry","UNSUPPORTED","K=-0.0350; p=.2144")',
    '("Wild scalar carrier bridge","FAILED FROZEN GATE","2/4 panels < frozen 3/4 threshold")',
    '("Wild H/V localization","EXPLORATORY ONLY","post-outcome; cannot reopen frozen bridge")',
]
for token in required_plot_tokens:
    if token not in plot:
        raise SystemExit(f"STOP: required figure evidence token missing: {token!r}")

# Evidence-tier wording in plan/captions/master.
required_text_tokens = [
    ("plan", plan, "PRIMARY FAIL"),
    ("plan", plan, "predeclared secondary"),
    ("plan", plan, "Post-outcome H/V"),
    ("captions", captions, "PRIMARY FAIL"),
    ("captions", captions, "H/V component analyses were opened after that failure"),
    ("master", master, "**PRIMARY FAIL**"),
    ("master", master, "**SUPPORTED SECONDARY**"),
    ("master", master, "**POST-PRIMARY DIAGNOSTIC**"),
    ("master", master, "**FAILED FROZEN GATE**"),
    ("master", master, "**EXPLORATORY ONLY**"),
]
for label, text, token in required_text_tokens:
    if token not in text:
        raise SystemExit(f"STOP: {label} evidence-tier token missing: {token!r}")

# Stale/forbidden claims that were removed during numerical audit.
for label,text in [("plot",plot),("plan",plan),("captions",captions),("master",master)]:
    for token in [
        "held-out environment prediction",
        "held-out prediction p = 0.0002",
        "p=0.0002",
        "SUPPORTED, non-randomized history refinement",
    ]:
        if token.lower() in text.lower():
            raise SystemExit(f"STOP: stale token in {label}: {token!r}")

# Raw heterogeneous effect sizes must not be presented on one shared axis.
if "Raw K/A effect sizes are intentionally not pooled" not in plot:
    raise SystemExit("STOP: Figure 3 heterogeneity warning missing")

print("PASS public causal figure evidence/provenance guard v1")
