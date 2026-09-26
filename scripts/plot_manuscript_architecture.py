#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"figures"/"architecture_summary_v0_3_1.csv"
OUT=ROOT/"figures"/"generated"
OUT.mkdir(parents=True,exist_ok=True)

rows=list(csv.DictReader(DATA.open(encoding="utf-8")))

# Figure 3: architecture plane.
fig,ax=plt.subplots(figsize=(7.2,5.6))
for row in rows:
    x=float(row["marginal_identity"])
    y=float(row["conditional_advantage"])
    label=row["panel"].replace("_"," ")
    ax.scatter(x,y,s=70)
    ax.annotate(label,(x,y),xytext=(5,5),textcoords="offset points",fontsize=8)
ax.axhline(0,linewidth=1)
ax.axvline(0,linewidth=1)
ax.set_xlabel("Marginal identity gain (nats/fix)")
ax.set_ylabel("Conditional advantage = conditional − marginal (nats/fix)")
ax.set_title("Predictive architecture of cross-night vertical identity")
fig.tight_layout()
fig.savefig(OUT/"figure3_architecture_plane.png",dpi=220)
fig.savefig(OUT/"figure3_architecture_plane.pdf")
plt.close(fig)

# Figure 5: within-species Phyllostomus context changes.
ph=[r for r in rows if r["taxon"]=="Phyllostomus hastatus"]
labels=[r["context"] for r in ph]
marg=[float(r["marginal_identity"]) for r in ph]
adv=[float(r["conditional_advantage"]) for r in ph]
x=list(range(len(ph)))
fig,ax=plt.subplots(figsize=(7.2,4.8))
ax.plot(x,marg,marker="o",label="Marginal identity")
ax.plot(x,adv,marker="o",label="Conditional advantage")
ax.axhline(0,linewidth=1)
ax.set_xticks(x,labels,rotation=20,ha="right")
ax.set_ylabel("nats/fix")
ax.set_title("Phyllostomus predictive architecture varies among temporal panels")
ax.legend()
fig.tight_layout()
fig.savefig(OUT/"figure5_phyllostomus_context.png",dpi=220)
fig.savefig(OUT/"figure5_phyllostomus_context.pdf")
plt.close(fig)

print(OUT)
