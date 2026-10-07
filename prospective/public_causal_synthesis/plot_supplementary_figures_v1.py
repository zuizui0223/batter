#!/usr/bin/env python3
"""Generate supplementary figures S1-S3 for the public causal synthesis."""

from pathlib import Path
import math
import matplotlib.pyplot as plt
import numpy as np

OUT=Path("figures/public_causal_supplement")
OUT.mkdir(parents=True,exist_ok=True)

def save(fig,name):
    fig.tight_layout()
    fig.savefig(OUT/name,bbox_inches="tight")
    plt.close(fig)

# Figure S1 — provenance timeline (stage sequence, not calendar time).
sources=[
    "Harten first-flight",
    "Rachum enrichment",
    "Elie auditory feedback",
    "Pipistrellus masker",
    "Myotis masking",
    "Eptesicus midbrain",
    "Aharon navigation",
    "Rhino policy",
    "Carollia transfer",
    "Wild carrier bridge",
]
stages=["freeze","structure","numeric","result","implementation note"]
notes={
    "Rachum enrichment":"receipt push race only",
    "Eptesicus midbrain":"Euclidean syntax fix only",
    "Aharon navigation":"public-file access route resolved",
}
fig,ax=plt.subplots(figsize=(11.5,6.5))
for yi,src in enumerate(sources):
    xs=[1,2,3,4]
    ax.plot(xs,[yi]*4,marker="o",linewidth=1)
    if src in notes:
        ax.scatter([5],[yi],marker="s")
        ax.text(5.08,yi,notes[src],va="center",fontsize=8)
ax.set_xticks(range(1,6),stages)
ax.set_yticks(range(len(sources)),sources)
ax.invert_yaxis()
ax.set_xlim(0.7,6.4)
ax.set_title("Analysis provenance: frozen scientific choices precede numerical opening")
ax.set_xlabel("Programme stage (ordered, not calendar time)")
save(fig,"FIGURE_S1_PROVENANCE_TIMELINE_V1.svg")

# Figure S2 — developmental descriptive decompositions.
rachum_names=["Boldness","Exploration","Activity"]
rachum=np.array([0.465792,0.250837,0.018070],dtype=float)

elie_names=[
    "Temporal entropy",
    "Mic 1st spectral quartile",
    "Mic 2nd spectral quartile",
    "Mic 3rd spectral quartile",
    "Fundamental mean",
    "Temporal kurtosis",
    "Spectral mean",
    "3rd spectral quartile",
    "2nd spectral quartile",
    "1st spectral quartile",
    "Fundamental CV",
    "Spectral kurtosis",
    "Mic spectral entropy",
    "Spectral SD",
    "RMS mean",
    "Mic spectral mean",
    "Mic spectral skew",
    "Temporal SD",
    "Amplitude periodicity power",
    "Mic spectral kurtosis",
    "Pitch saliency",
    "Spectral entropy",
    "Temporal skewness",
    "Spectral skewness",
    "Temporal mean",
    "Amplitude periodicity frequency",
    "Mic spectral SD",
    "Duration",
]
elie=np.array([
    -1.212594,
    -0.997132,
    -0.801085,
    -0.668213,
    -0.602536,
    +0.555672,
    +0.524287,
    +0.412367,
    +0.395018,
    +0.357930,
    +0.340236,
    -0.325049,
    +0.286859,
    +0.180443,
    -0.170454,
    +0.162048,
    +0.156351,
    +0.152631,
    -0.114663,
    +0.113034,
    -0.110172,
    +0.070713,
    -0.052974,
    -0.051179,
    -0.044985,
    +0.026596,
    -0.021200,
    +0.012555,
],dtype=float)

if abs(float(np.sum(rachum))-0.734699)>2e-6:
    raise SystemExit(f"STOP Rachum contribution sum drift: {np.sum(rachum)}")
if abs(float(np.sum(elie))-(-1.425497))>2e-6:
    raise SystemExit(f"STOP Elie contribution sum drift: {np.sum(elie)}")
if int(np.sum(elie>0))!=15 or int(np.sum(elie<0))!=13:
    raise SystemExit("STOP Elie sign-count drift")

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,9),gridspec_kw={"width_ratios":[1,2.2]})
x=np.arange(len(rachum_names))
ax1.bar(x,rachum)
ax1.axhline(0,linewidth=1)
ax1.set_xticks(x,rachum_names,rotation=25,ha="right")
ax1.set_ylabel("Additive contribution to frozen D")
ax1.set_title("A. Rachum enrichment\n3/3 contributions positive; descriptive only")
ax1.text(0.02,0.98,"Sum = +0.734699\nPrimary p = 0.167785",
         transform=ax1.transAxes,va="top",fontsize=9)

y=np.arange(len(elie_names))
ax2.barh(y,elie)
ax2.axvline(0,linewidth=1)
ax2.set_yticks(y,elie_names,fontsize=7.5)
ax2.invert_yaxis()
ax2.set_xlabel("Additive contribution to frozen D")
ax2.set_title("B. Elie auditory-feedback decomposition\n15 positive / 13 negative; descriptive only")
ax2.text(0.98,0.02,"Sum = -1.425497\nCancellation ratio = 0.840173",
         transform=ax2.transAxes,ha="right",va="bottom",fontsize=9)
save(fig,"FIGURE_S2_DEVELOPMENTAL_DECOMPOSITIONS_V1.svg")

# Figure S3 — exact-null resolution versus biological n.
systems=["Eptesicus\nmidbrain","Aharon\nnavigation","Myotis\nmasking"]
n_bio=np.array([4,4,3],dtype=int)
assignments=np.array([24,576,1296],dtype=int)
min_p=np.array([1/24,1/576,1/1296],dtype=float)

fig,ax=plt.subplots(figsize=(8.5,5.5))
x=np.arange(len(systems))
ax.bar(x,assignments)
ax.set_yscale("log")
ax.set_xticks(x,systems)
ax.set_ylabel("Number of legal exact identity/null assignments (log scale)")
ax.set_title("Exact-null resolution is not biological replication", pad=16)
ax.set_ylim(15, 2600)
for i in range(len(systems)):
    ax.text(i,assignments[i]*1.12,
            f"biological n={n_bio[i]}\nmin p={min_p[i]:.6f}",
            ha="center",va="bottom",fontsize=9)
save(fig,"FIGURE_S3_EXACT_NULL_RESOLUTION_V1.svg")

print("generated",len(list(OUT.glob("FIGURE_S*_V1.svg"))),"supplementary SVG files")
