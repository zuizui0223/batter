#!/usr/bin/env python3
from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"post_freeze_extensions/3d_niche_partition/specialization_partitioning_phase_space_v1.csv"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/specialization_partitioning_phase_space_v1.svg"

rows=[]
with DATA.open(newline="",encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        r["V_rel"]=float(r["V_rel"])
        r["couse_excess_m"]=float(r["couse_excess_m"])
        r["tolerance_s"]=int(r["tolerance_s"])
        r["couse_supported"]=r["couse_supported"].lower()=="true"
        rows.append(r)

fig,ax=plt.subplots(figsize=(9.0,5.8))
ax.axhline(0,linewidth=1)
ax.axvline(0,linewidth=1)

for r in rows:
    marker="o" if r["couse_supported"] else "o"
    if r["couse_supported"]:
        ax.scatter(r["V_rel"],r["couse_excess_m"],s=80,marker=marker)
    else:
        ax.scatter(r["V_rel"],r["couse_excess_m"],s=70,marker=marker,facecolors="none",edgecolors="black")
    name=r["panel"].replace("Hypsignathus monstrosus","H. monstrosus").replace("Phyllostomus hastatus","P. hastatus")
    label=f"{name}\n{r['tolerance_s']} s, {r['scope'].replace('_','-')}"
    ax.annotate(label,(r["V_rel"],r["couse_excess_m"]),xytext=(6,5),textcoords="offset points",fontsize=8)

ax.set_xlabel("Terrain-relative personal vertical-strategy fidelity (V_rel)")
ax.set_ylabel("Extra synchronous co-use vertical separation (m)")
ax.set_title("Personal specialization versus interaction-dependent vertical separation")
ax.text(0.107,4.6,"specialization + co-use separation",ha="right",fontsize=9)
ax.text(0.107,-2.6,"specialization without co-use separation",ha="right",fontsize=9)
ax.set_xlim(-0.01,0.115)
ax.set_ylim(-3.0,5.0)
fig.tight_layout()
fig.savefig(OUT)
print(OUT)
