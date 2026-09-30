#!/usr/bin/env python3
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures"/"integrated_inference_ladder_v1.svg"

fig,ax=plt.subplots(figsize=(10,5.2))
ax.set_axis_off()

def box(x,y,w,h,text):
    p=plt.Rectangle((x-w/2,y-h/2),w,h,fill=False)
    ax.add_patch(p)
    ax.text(x,y,text,ha="center",va="center",fontsize=10,wrap=True)

def arrow(x1,y1,x2,y2):
    ax.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle="->"))

box(0.12,0.58,0.19,0.25,"1. Common-cell\nhorizontal standardization\n\nReduce coarse x-y leakage")
box(0.36,0.58,0.19,0.25,"2. Session centering\n\nRemove absolute altitude level\nand additive zero point")
box(0.60,0.58,0.19,0.25,"3. Place / state / time\nstress tests\n\nLocalize what does not\nabsorb the signal")
box(0.84,0.58,0.19,0.25,"4. External frozen tests\n\nMap recurrence and\necological boundary")
arrow(0.215,0.58,0.265,0.58)
arrow(0.455,0.58,0.505,0.58)
arrow(0.695,0.58,0.745,0.58)

ax.text(0.5,0.92,"Identifying vertical individuality and its ecological boundary",ha="center",va="center",fontsize=13)
ax.text(0.12,0.28,"Horizontal fidelity / terrain",ha="center",va="center",fontsize=9)
ax.text(0.36,0.28,"Tag/device altitude offset",ha="center",va="center",fontsize=9)
ax.text(0.60,0.28,"Broad behavioural / spatial context",ha="center",va="center",fontsize=9)
ax.text(0.84,0.28,"Universality versus heterogeneity",ha="center",va="center",fontsize=9)

ax.text(0.5,0.08,"Established evidence is kept separate from the post-hoc resource-anchoring × vertical-opportunity hypothesis.",ha="center",va="center",fontsize=9)

ax.set_xlim(0,1)
ax.set_ylim(0,1)
fig.tight_layout()
fig.savefig(OUT)
print(OUT)
