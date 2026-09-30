#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "integrated_ecological_hypothesis_v1.svg"

fig, ax = plt.subplots(figsize=(10.0, 5.6))
ax.set_axis_off()

def box(x, y, text, width=0.24, height=0.16):
    patch = plt.Rectangle((x-width/2, y-height/2), width, height, fill=False)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=10, wrap=True)

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2,y2), xytext=(x1,y1), arrowprops=dict(arrowstyle="->"))

box(0.13, 0.75, "Persistent spatial\nresource anchoring")
box(0.13, 0.45, "Repeated vertical\nopportunity")
box(0.44, 0.60, "Stable alternative spatial\nsolutions repeatedly available", width=0.28)
box(0.76, 0.60, "Stronger expected expression\nof centered vertical individuality", width=0.30)

arrow(0.25,0.75,0.31,0.64)
arrow(0.25,0.45,0.31,0.56)
arrow(0.58,0.60,0.61,0.60)

box(0.13, 0.18, "Mobile / ephemeral prey\nor surface-constrained feeding", width=0.27)
box(0.44, 0.18, "Fewer repeatable\nvertical choices", width=0.24)
box(0.76, 0.18, "Weaker expected expression\nof centered vertical individuality", width=0.30)
arrow(0.27,0.18,0.32,0.18)
arrow(0.56,0.18,0.61,0.18)

ax.text(
    0.5, 0.94,
    "Post-hoc hypothesis generation: resource anchoring × vertical opportunity",
    ha="center", va="center", fontsize=13
)
ax.text(
    0.50, 0.03,
    "Current systems generated this hypothesis; they are not fitted or scored as predictor observations.\n"
    "Future confirmation uses only new sources coded before vertical outcomes are opened.",
    ha="center", va="bottom", fontsize=9
)
ax.text(
    0.92, 0.39,
    "Competing predictors:\nwing morphology\nphylogeny / sensory ecology\nhabitat structure\natmospheric forcing\ntracking technology",
    ha="center", va="center", fontsize=8
)

ax.set_xlim(0,1)
ax.set_ylim(0,1)
fig.tight_layout()
fig.savefig(OUT)
print(OUT)
