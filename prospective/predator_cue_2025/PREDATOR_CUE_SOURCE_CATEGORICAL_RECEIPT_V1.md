# Author-source categorical dataset gate v1 — STOP independent individual reactivity

**No bat response magnitudes opened, fitted or plotted.** This is the structural categorical inspection of the authors' GitHub source, not a new acoustic/behavioral result.

## Exact source provenance
- Original authors: https://github.com/morceglo/Predator-recognition
- Git HEAD pinned: `67f9469b58daa878a6858af20a5fccbefe5d7b9c`, last commit 2025-03-11T19:40:41Z.
- Native source: `data.csv` (semicolon-delimited, 9,979 bytes; 228 observations).
- Git blob SHA `b8a119df0204ed0beb90b971c97f60cafbdb74cd`.
- Original analysis code `Analyses.R` already tests `treatment * period` in a Poisson/NB mixed model with bat random intercept; `bat_type` and `order * bat_type` for the during period. This is prior art, not new personal memory work.

## Categorical fields (without the numeric "response" column)
`bat;experiment;order;treatment;bat_type;period;response`.

- 38 distinct physical bat labels.
- Every bat has EXACTLY **6 rows**, each representing two treatments × 3 periods before/during/after.
- Every bat belongs to exactly **ONE** source `experiment` and **ONE** `order`, with exactly two bat_type levels.
- All 228 categorical combinations (bat/experiment/order/treatment/type/period) are unique, no duplicates.
- Source experiment labels: CP (48 rows), PC (36), FP (42), PF (30), IP (42), PI (30). These code two source presentations within a single experimental sequence, **not two independent sessions per bat**.
- Order labels NP-P (132 rows) and P-NP (96).
- Conditions: 114 predator and 114 non-predator rows.
- Periods: 76 rows before, 76 during, 76 after.
- Playback categories: carnivorous 114, control 42, frugivorous 36, insectivorous 36.
- No `trial`, `bout`, `session`, `date`, or independently verifiable repeated-exposure field in the CSV.

## Frozen criterion and verdict

The precommitted `PREDATOR_CUE_STRUCTURAL_GATE_V1.md` requires ≥12 stable bats with ≥2 INDEPENDENT predator exposure bouts per bat (plus distinct stimulus/date support, baseline/after rows), and ≥24 independent bouts. In the actual source, **each of 38 bats has a single predator presentation in the source's one experimental sequence**. Therefore

```
STOP_NO_INDEPENDENT_PREDATOR_BOUTS
```

No effect size, permutation test, classifier accuracy, covariance matrix, between-bat random-slope repeatability, or forward prediction has been computed. A fixed bat-level intercept from one experiment is not evidence of stable individual *response plasticity*.

## Source validity, ecological scope and sensible follow-up
This experiment DOES support already-published *population-level* comparison of social calling before/during/after predator and nonpredator playback. It cannot establish stable individual response rules over separate predator encounters, much less relate them to independent 3-D corridors or prey acquisition.

No exploratory within-single-experiment subgroup is promoted as a replacement confirmation. An eligible future source would require repeated individually tagged bats encountering >1 independently identified masking/risk episodes, comparable controls, and ideally joint 3-D/social calls and performance. The published raw `data.csv` is not missing, inaccessible or unusable; it simply does not contain the necessary repeated-bout biological design.

The source artifact was inspected at pinned author GitHub commit; the raw CSV is not recopied into the batter repo.
