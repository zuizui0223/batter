#!/usr/bin/env python3
from pathlib import Path
import csv
import math
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"post_freeze_extensions/3d_niche_partition/spatial_geometry_phase_space_v1.csv"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/spatial_geometry_phase_space_v1.svg"

rows=[]
with DATA.open(newline="",encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        for k in ("H","V"):
            r[k]=float(r[k])
        r["S"]=float(r["S"]) if r["S"].strip() else None
        rows.append(r)

fig,ax=plt.subplots(figsize=(9.3,6.2))
ax.axhline(0,linewidth=1)
ax.axvline(0,linewidth=1)

for r in rows:
    filled=r["status"]=="inferential"
    marker="o" if filled else "o"
    size=55+320*abs(r["S"]) if r["S"] is not None else 55
    if filled:
        ax.scatter(r["H"],r["V"],s=size,marker=marker,zorder=3)
    else:
        ax.scatter(r["H"],r["V"],s=size,marker=marker,facecolors="none",edgecolors="black",zorder=3)

    label=r["system"]
    if label=="Hypsignathus monstrosus": label="H. monstrosus"
    elif label=="Phyllostomus hastatus 2022": label="P. hastatus 2022"
    elif label=="Phyllostomus hastatus 2023": label="P. hastatus 2023"
    elif label=="Phyllostomus hastatus 2016": label="P. hastatus 2016"
    elif label=="Myotis vivesi": label="M. vivesi"
    elif label=="Pteropus poliocephalus MSL": label="P. poliocephalus MSL"
    elif label=="Pteropus poliocephalus MSL-DEM": label="P. poliocephalus MSL−DEM"
    elif label=="Tadarida teniotis": label="T. teniotis (structural)"
    elif label=="Nyctalus noctula": label="N. noctula (structural)"
    sval="" if r["S"] is None else f"  S={r['S']:+.2f}"
    ax.annotate(label+sval,(r["H"],r["V"]),xytext=(5,5),textcoords="offset points",fontsize=8)

native=next(r for r in rows if r["system"]=="Pteropus poliocephalus MSL")
terrain=next(r for r in rows if r["system"]=="Pteropus poliocephalus MSL-DEM")
ax.annotate("",xy=(terrain["H"],terrain["V"]),xytext=(native["H"],native["V"]),
            arrowprops=dict(arrowstyle="->",linewidth=1.5))
ax.text(native["H"]+0.008,(native["V"]+terrain["V"])/2,"terrain subtraction",fontsize=8,rotation=90,va="center")

ax.set_xlabel("H = self − other horizontal overlap")
ax.set_ylabel("V = self − other vertical overlap within shared 500-m cells")
ax.set_title("Geometry of individual spatial specialization")
ax.set_xlim(-0.04,0.39)
ax.set_ylim(-0.14,0.33)
ax.text(0.355,0.30,"nested 3D",ha="right",va="top",fontsize=9)
ax.text(0.355,-0.12,"horizontal-dominant",ha="right",va="bottom",fontsize=9)
ax.text(-0.032,0.30,"vertical-dominant",ha="left",va="top",fontsize=9)
ax.text(-0.032,-0.12,"weak / exchangeable",ha="left",va="bottom",fontsize=9)
ax.text(0.01,0.315,"Point size ∝ |S|; S = extra between-individual separation revealed by height\nOpen points failed the fixed structural gate; Pteropus arrow is a secondary terrain diagnostic.",
        fontsize=7.5,va="top")
fig.subplots_adjust(left=0.11,right=0.98,top=0.90,bottom=0.12)
fig.savefig(OUT)
print(OUT)
