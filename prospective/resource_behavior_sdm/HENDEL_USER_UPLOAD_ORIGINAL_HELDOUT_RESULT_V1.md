# Hendel user-uploaded original: heldout bat–prey activity prediction (2026-11-21)

**Status: source-local, exploratory empirical positive; NOT resource-conditioned 3D flight.**
The frozen 2026-11-20 ridge evaluator now has an actual independent field **source** from Germany (different from Brazil Ducke). Publisher HTTP401 blocked the cloud runner, not user-uploaded original XLSX. No source rows/animal records committed.

## Original integrity and eligibility
- User-uploaded filename: Hendel_etal_2024_Data_DRYAD(1).xlsx. SHA-256: b550d9b2ed1448191dfee85caaa5f27321c6a78c65c8925816a340695513b5a3. This is an **upload checksum**, not publisher checksum verification.
- 65 complete, distinct forest plots × 23 source columns. Paper [Hendel et al. 2025](https://doi.org/10.1111/1365-2664.14822) describes 64 sites; author-defined exclusion identity is not known. Do NOT select a favorable row to remove; exhaustive 65 possible 64-row sensitivity below.
- Source-to-frozen-engine aliases: mothcount_total → mothcount; carabidae_SR → carabidae_S. The previous synthetic-only runner expected non-existent source column names.
- Four **overlapping acoustic** response channels (SRE, MRE, Ppip, LRE), not four exclusive diet guild shares. Do not use a multinomial.

## Frozen-spec empirical leave-entire-plot-out prediction
Forest baseline: elevation + DOY + temp_min + Opn_mean + ndsm_sd + ForMI; ridge 0.15; source food counts log1p transformed; targets log1p, then training-only standardized. Same 65 withheld plots across models. Gain is mean negative squared standardized-log-acoustic-activity forecast error improvement, not a p-value, ecological coefficient or abundance effect.

| Acoustic response | + moth abundance | + moth richness | + beetle richness | + beetle abundance & richness |
|---|---:|---:|---:|---:|
| SRE | −0.01199 | −0.03064 | −0.01762 | −0.01593 |
| MRE | **+0.10990** | +0.08252 | −0.02311 | −0.04865 |
| P. pipistrellus | **+0.16283** | +0.13841 | −0.02356 | −0.03292 |
| LRE | −0.02618 | −0.02344 | **+0.13708** | **+0.17649** |

Site-level positive contrasts: MRE/moth abundance 40/65; Ppip/moth abundance 38/65; LRE/beetle richness 38/65. Sites are not independent studies.

**All 65 delete-one-site variants**, rerunning a complete 64-plot heldout CV:
- MRE/moth abundance +0.0665 to +0.1401, 65/65 positive.
- Ppip/moth abundance +0.1002 to +0.1901, 65/65 positive.
- LRE/beetle richness +0.0939 to +0.1727, 65/65 positive.
- LRE/beetle abundance+richness +0.1307 to +0.2105, 65/65 positive.
- SRE/moth abundance full-sample negative (−0.01199), with 65/65 delete-one runs negative.
These ranges are **robustness envelopes**, not confidence intervals.

## Post-outcome robustness: exploratory diagnostics
- Expanding baseline to all 13 available forest/weather/understory controls retains MRE/moths +0.0904, Ppip/moths +0.1754, LRE/beetle richness +0.2016.
- Ridge penalties 0.05, 0.15, 0.5 and 1.0 preserve signs of these three effects.
- Alternative heldout mean absolute standardized log activity error also improves: +0.0417, +0.0581, +0.0575 respectively.
- Moth abundance–richness log correlation 0.805; beetle abundance–richness 0.789; do not infer unique causal abundance-versus-richness mechanism.

## Boundary and interpretation
This independently **observed** German prey–bat acoustic signal extends the **predictor principle** (measured local resources can improve site-level bat-use prediction), not numeric transport of Ducke's guild-composition coefficient. Their scores and responses differ and cannot be pooled as an effect-size meta-analysis. Authors already reported source SEM associations; the new result here is heldout predictive scoring conditional on specified covariates and **is exploratory source-open analysis**.

SRE shows no new-site moth gain although the authors' descriptive SEM suggested SRE associations. MRE and Ppip mostly consume flies, not demonstrably these moths; prey records can be broader habitat/arthropod proxies. Moth light traps were on night two, whereas bat acoustics were nights one and three, and ground beetles were sampled in an earlier seasonal window. Acoustic recording/detection and unmeasured vegetation remain confounders.

**NOT inferred**: prey consumption, behavioral state switching, individual GPS movements, flight height, conditional 3D vertical niche, geographically independent transfer, or whole-species range. The 64/65 discrepancy is unresolved. Protect JAE/BE and main. Keep PR draft.

Reproduction adapter: hendel_uploaded_xlsx_original_adapter_v1.py, within this folder; original XLSX needed locally. Source DOI: https://doi.org/10.5061/dryad.xksn02vr1


## Conditional coefficient directions (post-outcome association diagnostic, NOT mechanism)

Across the 65 leave-one-plot-out **training fits**, the fitted standardized ridge coefficient of the added prey variable is stable in direction:
- MRE on log-moth abundance: mean coefficient **−0.2952** (65/65 fits negative).
- Ppip on log-moth abundance: **−0.3722** (65/65 negative).
- LRE on log-ground-beetle richness: **−0.3370** (65/65 negative).
- SRE on log-moth abundance: **+0.0960** (65/65 positive), although its withheld-site prediction gain is negative.

With all seven other source forest covariates included in the baseline (13 controls in total), the four coefficient means remain **−0.2921, −0.3903, −0.3700, +0.0596**, respectively, with the same 65/65 sign stability. Source-open association diagnostics computed independently with a NumPy ridge implementation using the frozen model's exact fold-wise training standardization; they do not establish dietary use or causal resource effects.

**Key separation:** The positive forecast information in MRE, Ppip and LRE is *not* evidence that those measured insects positively attract those guilds. Opposite signs among acoustic groups, and the SRE positive coefficient without improved heldout forecast, motivate resource composition/structural-proxy hypotheses. This is a prospective interpretation, not an independently verified mechanism.


## Further post-outcome grouped validation (predictor retention, NOT independent geographic transfer)

To distinguish site-by-site interpolation from broader within-source transfer, the same source-local train-only scaling / fixed ridge contrast was re-evaluated holding out (A) **all plots with the same source DOY label** (17 distinct groups), and (B) **entire contiguous elevation quintiles** (five groups). Score averages below are **site-weighted** over disjoint test groups, not independent-study p-values:

| Target resource contrast | One entire DOY-label group out | One elevation-quintile group out | Favorable DOY groups | Favorable elevation groups |
|---|---:|---:|---:|---:|
| MRE, + moth abundance | +0.1254 | +0.1380 | 11/17 | 5/5 |
| Ppip, + moth abundance | +0.1942 | +0.1895 | 10/17 | 4/5 |
| LRE, + beetle richness | +0.1197 | +0.1173 | 10/17 | 4/5 |

Elevation quintile boundaries from source values were 512, 678.6, 821, 925.6, 992.4 and 1334 m; group membership was determined from source elevation alone. DOY groups have 1–6 plots each, and the single-site DOY=231 group has an outsized Ppip advantage. Gains vary substantially across DOY groups; these sensitivities **do not** establish that resource predictivity is uniform among environments. Neither grouping excludes spatial proximity among training and test plots: **NOT a geographically independent transport validation**. These are additional post-outcome tests, not part of the original frozen primary estimator.
