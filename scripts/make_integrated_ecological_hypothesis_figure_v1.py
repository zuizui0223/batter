#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "integrated_ecological_hypothesis_v1.svg"

fig, ax = plt.subplots(figsize=(10.4, 5.8))
ax.set_axis_off()

def box(x, y, text, width=0.23, height=0.15):
    patch = plt.Rectangle((x-width/2, y-height/2), width, height, fill=False)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=9.5, wrap=True)

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle="->"))

ax.text(
    0.5, 0.95,
    "Post-hoc hypothesis generation: when can vertical individuality be expressed?",
    ha="center", va="center", fontsize=13
)

# Upper pathway
box(0.11, 0.73, "Persistent resource\nor feeding area", width=0.19)
box(0.34, 0.73, "Same ecological task\nrecurs across visits", width=0.20)
box(0.58, 0.73, "Several repeatable\nvertical solutions exist", width=0.21)
box(0.84, 0.73, "Individuals can repeatedly\nuse different solutions", width=0.22)
arrow(0.205,0.73,0.24,0.73)
arrow(0.44,0.73,0.475,0.73)
arrow(0.685,0.73,0.73,0.73)

ax.text(
    0.58, 0.57,
    "Examples of alternative solutions: approach height • canopy layer • route geometry",
    ha="center", va="center", fontsize=8.5
)
arrow(0.84,0.655,0.84,0.52)
box(0.84, 0.44, "Stronger repeatable centered\nvertical individuality", width=0.25)

# Lower pathways
box(0.15, 0.24, "Mobile / ephemeral prey", width=0.22)
box(0.41, 0.24, "The spatial problem changes\nfrom visit to visit", width=0.23)
box(0.68, 0.24, "Fewer reusable\nvertical solutions", width=0.20)
arrow(0.26,0.24,0.295,0.24)
arrow(0.525,0.24,0.58,0.24)

box(0.15, 0.08, "Surface-constrained feeding", width=0.22)
box(0.41, 0.08, "The task permits little\nvertical freedom", width=0.23)
arrow(0.26,0.08,0.295,0.08)
arrow(0.525,0.08,0.58,0.18)

box(0.88, 0.16, "Weaker expected centered\nvertical individuality", width=0.22)
arrow(0.78,0.24,0.78,0.19)
arrow(0.78,0.19,0.77,0.16)

ax.text(
    0.08, 0.48,
    "Generated from current systems;\nnot fitted to them",
    ha="center", va="center", fontsize=8
)
ax.text(
    0.50, 0.015,
    "Future confirmation uses only new sources whose ecology is coded before vertical outcomes are examined.",
    ha="center", va="bottom", fontsize=8.5
)
ax.text(
    0.985, 0.42,
    "Competing predictors:\nwing morphology\nphylogeny / sensory ecology\nhabitat structure\n"
    "atmospheric forcing\ntracking technology",
    ha="right", va="center", fontsize=7.5
)

ax.set_xlim(0,1)
ax.set_ylim(0,1)
fig.tight_layout()
fig.savefig(OUT)
print(OUT)
