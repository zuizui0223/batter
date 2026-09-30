#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "integrated_inference_ladder_v1.svg"

fig, ax = plt.subplots(figsize=(10.2, 5.2))
ax.set_axis_off()

def box(x, y, w, h, text):
    patch = plt.Rectangle((x-w/2, y-h/2), w, h, fill=False)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=10)

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->"))

xs = [0.13, 0.38, 0.63, 0.87]
box(xs[0], 0.60, 0.21, 0.22, "1. Common-cell weighting\nSame 5-km x-y weights\nfor self and other")
box(xs[1], 0.60, 0.21, 0.22, "2. Session centering\nSubtract session median")
box(xs[2], 0.60, 0.21, 0.22, "3. Localization tests\nstate • place • time")
box(xs[3], 0.60, 0.21, 0.22, "4. External tests\nnew pre-specified source systems")

arrow(0.235, 0.60, 0.275, 0.60)
arrow(0.485, 0.60, 0.525, 0.60)
arrow(0.735, 0.60, 0.765, 0.60)

subs = [
    "coarse horizontal occupancy",
    "absolute altitude / additive offset",
    "broad contextual alternatives",
    "recurrence versus boundary",
]
for x, txt in zip(xs, subs):
    ax.text(x, 0.38, txt, ha="center", va="center", fontsize=9)

ax.text(0.50, 0.90, "Identifying vertical individuality and its ecological boundary",
        ha="center", va="center", fontsize=13)
ax.text(
    0.50, 0.10,
    "Established evidence remains separate from the post-hoc resource-anchoring × vertical-opportunity hypothesis.",
    ha="center", va="center", fontsize=9
)

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
fig.tight_layout()
fig.savefig(OUT)
print(OUT)
