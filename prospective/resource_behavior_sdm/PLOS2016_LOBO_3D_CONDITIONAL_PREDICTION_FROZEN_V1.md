# Freeze before outcome: PLOS 2016 natural-flower vs artificial-target 3D conditional prediction

2026-11-20. Original publisher S1 XLSX `10.1371/journal.pone.0163492.s001` identified by SHA256 `3cce76e3f75c1eb49ac1a8344880a42da1de163886372a944080e074cdd1fb42`. Header precisely: `X Ref Target`, `Y Ref Target`, `Z Ref Target`, `Distance toT`, `Target`, `Bat`, `Test`. Raw numeric trajectory outcomes have **not yet been opened**.

### Source admission (no height access)

Only source columns E/F/G (`Target`/`Bat`/`Test`) are read before outcome modeling to verify paper's **five bats × two experimental targets × three reconstructed sequences** and independent trial count 30. The original Z (response), X/Y (predictors), and **Distance toT**, which combines XYZ and leaks the heldout Z, remain unopened. All source IDs remain in the RAM of the Actions runner only. Structural gate stops on any bat/target imbalance or absent grouping.

### If 30 source groups pass, primary prediction will be

1. **One entire heldout bat per outer fold (5 folds)**, all its 3 flower and 3 sham trials in test. Baseline `p(Zbin | XY radial-bin)` versus target-aware `p(Zbin | XY radial-bin, target)`; the target is the experimenter-assigned real flower versus acrylic hemisphere, not a habitat abundance estimate.
2. Input radius is `sqrt(X²+Y²)` only, **NEVER `Distance toT`** (which contains Z). Vertical Z is relative to target. If values or unit systems are incompatible between targets, STRUCTURAL STOP before fitting.
3. Three **training-only equal-frequency** radial bins (1/3, 2/3) and five **training-only equal-frequency** Z bins (0.2,0.4,0.6,0.8), calculated with each training trajectory contributing total weight one, to avoid variable-frame-count domination. No data-driven choice among bin widths and endpoints. No bat-specific effect fitted for the heldout animal.
4. Conditional multinomial estimates per radial bin with fixed Jeffreys pseudocount 0.5 per Z bin. Candidate and baseline learn from identical training tracks. Score the exact same heldout target events. Each trial's mean log score is averaged within bat and target, then equally across the five bats.
5. Primary contrast: equal-bat mean Δlogscore (target-aware minus target-blind) on the height category, in nats/recorded position. All frames within a trial are repeated measures. Two complementary diagnostics: 5 equal-bat signs and the exact 32-element bat-level signflip null; with only five bats this is exploratory and a positive estimate is **not** an independent study replication.
6. Fixed negative control: shuffle flower vs hemisphere labels among training trial groups while retaining the original 3+3 per bat, not the test labels. Report test outcome only on fixed heldout bats. This can show label specificity under the original experimental target contrast, not isolate echo versus scent (both are changed).

### Hard ecological boundaries

The published experiment already reports target-specific changes in 3D approaches; this predictive reanalysis tests out-of-bat *forecastability*, not original discovery of target discrimination. This source is an indoor 4×4×3 m flight-cage sequence and **does not contain fruit availability, geographic occurrence, wild foraging ranges, colony interaction, or regional NeoBat M3/M1**. Its bat identity/height channel may inform a LOCAL decision kernel in a future 5-D SDM but is not a validated species distribution model.

Do not pool these five bats with Goldshtein et al. (2020) wild Saguaro tracking: distinct samples, cactus plant species, locality, instrumentation, and experimental context.
