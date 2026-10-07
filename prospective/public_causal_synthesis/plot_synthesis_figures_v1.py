#!/usr/bin/env python3
"""Generate manuscript-facing public causal synthesis figures v1.

Uses only frozen/authoritative values copied into MASTER_RESULTS_TABLE_V1.md
or the source result records cited there.

No cross-endpoint raw effect-size pooling is performed.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

OUT=Path("figures/public_causal")
OUT.mkdir(parents=True,exist_ok=True)

def save(fig,name):
    fig.tight_layout()
    fig.savefig(OUT/name,bbox_inches="tight")
    plt.close(fig)

# Figure 1: causal layers / evidence architecture
fig,ax=plt.subplots(figsize=(11,4.8))
ax.set_axis_off()
boxes=[
    (0.02,0.60,0.22,0.28,"FORMATION / HISTORY",
     "Monotonic first-flight primary: FAIL\nLate-history secondary: supported\nEnrichment individualization: unsupported\nAuditory-feedback amount: no difference"),
    (0.27,0.60,0.22,0.28,"ACUTE MAINTENANCE",
     "Pipistrellus masker: supported\nMyotis graded masking: supported\nEptesicus midbrain: supported\nAharon navigation context: supported"),
    (0.52,0.60,0.22,0.28,"EXPRESSION / PORTABILITY",
     "Rhino coarse I/M: supported\nCarollia fixed I/M: supported\nCarollia detailed geometry: unsupported"),
    (0.77,0.60,0.21,0.28,"WILD CONSEQUENCE",
     "Frozen field carrier gate: 2/4 FAIL\nPost-outcome H/V: exploratory only"),
]
for x,y,w,h,title,body in boxes:
    rect=plt.Rectangle((x,y),w,h,fill=False,linewidth=1.5,transform=ax.transAxes)
    ax.add_patch(rect)
    ax.text(x+0.01,y+h-0.06,title,transform=ax.transAxes,fontsize=10,fontweight="bold",va="top")
    ax.text(x+0.01,y+h-0.11,body,transform=ax.transAxes,fontsize=8.5,va="top",linespacing=1.4)
for x1,x2 in [(0.24,0.27),(0.49,0.52),(0.74,0.77)]:
    ax.annotate("",xy=(x2,0.74),xytext=(x1,0.74),xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->",linestyle="--",linewidth=1))
ax.text(0.5,0.29,
        "Distinct empirical layers; arrows are conceptual, not a claim that every dataset measures one latent state.",
        transform=ax.transAxes,ha="center",fontsize=10)
save(fig,"FIGURE_1_CAUSAL_LAYERS_V1.svg")

# Figure 2A: first-flight monotonic formation primary
b_names=["Anka","Eli","Eva","Fima","K","Mazi","Nadav","Nature","Nazir","Odelia","Shem_Tov","Tishray","Tzedi","V"]
b_vals=np.array([0.166,0.290,0.259,-0.309,-0.383,-0.121,0.913,-0.486,-0.071,0.245,0.647,0.676,0.564,-0.049])
fig,ax=plt.subplots(figsize=(9,5.6))
y=np.arange(len(b_names))
ax.scatter(b_vals,y)
ax.axvline(0,linewidth=1)
ax.set_yticks(y,b_names)
ax.invert_yaxis()
ax.set_xlabel("Individual Spearman slope B_i")
ax.set_title("First-flight monotonic formation primary: 8/14 positive; frozen requirement 10/14")
ax.text(0.99,0.02,"Programme B=+0.16733; permutation p=0.0102; PRIMARY FAIL",
        transform=ax.transAxes,ha="right",va="bottom",fontsize=9)
save(fig,"FIGURE_2A_FIRST_FLIGHT_FORMATION_V1.svg")

# Figure 2B: developmental randomized primary summary (no shared effect-size axis)
fig,ax=plt.subplots(figsize=(10,4.6))
ax.set_axis_off()
tiles=[
    (0.04,0.18,0.43,0.68,"Randomized enrichment — Rachum et al.",
     "n=29 (14 enriched / 15 impoverished)\nV_enriched=2.656639\nV_impoverished=1.921940\nD=+0.734699\np=0.167785\nUNSUPPORTED INDIVIDUALIZATION"),
    (0.53,0.18,0.43,0.68,"Randomized auditory feedback — Elie et al.",
     "n=10 (5 hearing / 5 deafened)\nV_hearing=15.766760\nV_deaf=17.192257\nD=-1.425497\nexact p=0.716667\nNO DIFFERENCE IN AMOUNT"),
]
for x,y,w,h,title,body in tiles:
    ax.add_patch(plt.Rectangle((x,y),w,h,fill=False,linewidth=1.5,transform=ax.transAxes))
    ax.text(x+0.02,y+h-0.07,title,transform=ax.transAxes,fontweight="bold",fontsize=10,va="top")
    ax.text(x+0.02,y+h-0.16,body,transform=ax.transAxes,fontsize=9,va="top",linespacing=1.35)
ax.text(0.5,0.06,"Different frozen endpoints: D values are not quantitatively comparable across experiments.",
        transform=ax.transAxes,ha="center",fontsize=9)
save(fig,"FIGURE_2B_DEVELOPMENTAL_RANDOMIZATION_V1.svg")

# Figure 3: acute perturbation identity correspondence.
systems=["Pipistrellus\nmasker","Myotis\nmasking gradient","Eptesicus\nmidbrain","Aharon\nnavigation"]
n_bio=[6,3,4,4]
positive=[5/6,3/3,4/4,4/4]
pvals=[0.04028,1/1296,1/24,2/576]
rank_labels=["exact p=.04028","rank 1/1296","rank 1/24","rank 2/576"]
fig,ax=plt.subplots(figsize=(9.5,5.4))
x=np.arange(len(systems))
ax.scatter(x,positive,s=np.array(n_bio)*45)
ax.set_xticks(x,systems)
ax.set_ylim(0,1.08)
ax.set_ylabel("Fraction of biological individuals with positive identity advantage")
ax.set_title("Individual correspondence across controlled acute perturbations")
for i,(n,lab,p) in enumerate(zip(n_bio,rank_labels,pvals)):
    ax.text(i,positive[i]+0.035,f"n={n}\n{lab}",ha="center",va="bottom",fontsize=8.5)
ax.text(0.01,0.02,
        "Marker size reflects biological n. Raw K/A effect sizes are intentionally not pooled across heterogeneous endpoints.",
        transform=ax.transAxes,fontsize=8.5)
save(fig,"FIGURE_3_ACUTE_PERTURBATION_IDENTITY_V1.svg")

# Figure 4: portability vs realization vs wild bridge.
fig,ax=plt.subplots(figsize=(10.5,5.4))
ax.set_axis_off()
entries=[
    ("Rhino coarse I/M","SUPPORTED","K=+0.55428; 5/5 positive; p=.0001"),
    ("Carollia fixed Rhino I/M","SUPPORTED","K=+0.34758; p=.0007"),
    ("Carollia fixed detailed geometry","UNSUPPORTED","K=-0.0350; p=.2144"),
    ("Wild scalar carrier bridge","FAILED FROZEN GATE","2/4 panels < frozen 3/4 threshold"),
    ("Wild H/V localization","EXPLORATORY ONLY","post-outcome; cannot reopen frozen bridge"),
]
ys=np.linspace(0.82,0.18,len(entries))
for y,(name,status,detail) in zip(ys,entries):
    ax.text(0.03,y,name,transform=ax.transAxes,fontsize=10,fontweight="bold",va="center")
    ax.text(0.42,y,status,transform=ax.transAxes,fontsize=10,va="center")
    ax.text(0.65,y,detail,transform=ax.transAxes,fontsize=9,va="center")
ax.plot([0.40,0.40],[0.10,0.90],transform=ax.transAxes,linewidth=0.8)
ax.plot([0.63,0.63],[0.10,0.90],transform=ax.transAxes,linewidth=0.8)
ax.text(0.5,0.97,"Coarse organization, detailed realization and wild ecological consequence are distinct",
        transform=ax.transAxes,ha="center",va="top",fontsize=11)
save(fig,"FIGURE_4_PORTABILITY_AND_WILD_BOUNDARY_V1.svg")

print("generated",len(list(OUT.glob("FIGURE_*_V1.svg"))),"SVG files")
