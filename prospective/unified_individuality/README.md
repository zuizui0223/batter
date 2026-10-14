# Unified bat individuality manuscript — integration v1

This directory develops a **single manuscript** by integrating the existing *Journal of Animal Ecology* wild 3D ecology candidate and the *Behavioral Ecology* controlled/developmental synthesis, without changing or superseding either frozen source in place.

## Start here

1. [INTEGRATED_MANUSCRIPT_V1.md](INTEGRATED_MANUSCRIPT_V1.md) — full new draft, including rewritten Abstract, Introduction, Methods, Results, Discussion, Conclusion and selected working references.
2. [EVIDENCE_CROSSWALK_V1.md](EVIDENCE_CROSSWALK_V1.md) — audited source-to-claim table, with experimental and wild evidence hierarchies and claims this integration does **not** establish.
3. [FIGURES_AND_SI_PLAN_V1.md](FIGURES_AND_SI_PLAN_V1.md) — six proposed main figures, supporting-information migration table, word-budget and release safeguards.
4. [INTEGRATION_QA_V1.md](INTEGRATION_QA_V1.md) — 35 selected numeric keys reconciled at source-text level, plus epistemic and submission gate checklist.
5. [FIGURE_ATLAS_AND_CAPTIONS_V1.md](FIGURE_ATLAS_AND_CAPTIONS_V1.md) — six rendered SVG main figures with source-conscious figure legends and encounter-design caveats.
6. [figures/FROZEN_FIGURE_DATA_V1.json](figures/FROZEN_FIGURE_DATA_V1.json) + [figure builder](figures/generate_integrated_figures_v1.cjs) + [validator](figures/validate_integrated_figures_v1.py) — pinned summary inputs, reproducible no-dependency rendering and scientific/XML gates.

## One biological question

**What persists when behavior remains individually predictable, and when does that persistence require ecological spatial partitioning?**

Three distinguishable empirical axes:

- **Maintenance:** acute context manipulations can preserve the correct individual correspondence.
- **Realization:** a coarse identity-bearing movement representation can transfer when fixed fine-grained trajectory geometry does not.
- **Ecological consequence:** individually repeatable wild vertical probability distributions can overlap without evidence of positive added segregation.

Developmental/early-history results constrain how the differences form. A frozen lab-style FlightIntensity field bridge **failed** its 3/4 threshold (PASS/PASS/FAIL/structural STOP); this remains a central limit on a causal interpretation.

## Critical source-of-truth rule

- JAE rc2: branch release/jae-v0.4.0-rc2, manuscript blob c4ef51a7f3f291a6f203d303dbf73f5b54fb7683.
- BE v1: branch prospective/public-causal-synthesis-v1, manuscript blob a83fed81a141c62df29f3c12f2fb5fd36399c160.

The older JAE manuscript copy on the BE branch is NOT authoritative. The unified draft only adds files under this new directory. **No existing experimental or field outcomes were recalculated or relabeled as newly confirmatory.**

## Publication rule

This is the **alternative one-paper route**, not a third simultaneous submission alongside both underlying research manuscripts. It requires a single coordinated human/coauthor publication decision and new submission approvals before any journal upload.

## Figure status (2026-10-14)

All six proposed main figures now exist as editable SVG. The source-generated figure suite treats S_rel null envelopes and co-use dyad-bootstrap intervals as distinct uncertainty objects. Field encounter windows are pinned at 60/60/600/600 seconds, with 2023 all-space and 2016 endpoint-excluded. The original JAE individual-profile descriptive heatmap is still an **unretrieved original artifact** and must not be replaced with fabricated profiles. SVG structural/reproducibility checks run in [the dedicated PR workflow](../../.github/workflows/unified-manuscript-figures-v1.yml), subject to workflow completion; final visual QA and submission assembly remain pending.
