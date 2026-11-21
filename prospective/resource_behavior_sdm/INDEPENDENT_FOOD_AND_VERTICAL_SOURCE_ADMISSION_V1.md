# Independent animal 3D and directly measured food sources: admission v1

2026-11-20. Prospective original-source gate. **No original bat, raster, fruit or insect rows downloaded in this step.**

## A. Independent vertical-habitat study

*Chrotopterus auritus* tracked in three Mexican landscapes: Trujillo et al. 2026, JAE DOI [10.1111/1365-2656.70391](https://doi.org/10.1111/1365-2656.70391), original Dryad [10.5061/dryad.7d7wm38c0](https://doi.org/10.5061/dryad.7d7wm38c0), published 2026-10-30.

Published scope: 17 bats, 57 nightly GPS trajectories, GPS `height.above.msl` (not ground-relative height), two XY-kinematic HMM states, seven 10-m landcover classes in three distinct study landscapes. Dryad lists five original files: `Raw_movement_data.zip` (native recorded height), `Movement_data.zip` (30-s interpolation; **interpolated points have missing original height and are not new GPS fixes**), `Landscape_data.zip` (seven binary landcover layers), `Chrotopterus_auritus_Movement_Ecology_Analysis.zip` (four scripts) and `README.md` (public metadata). The corresponding original publication already reports HMM behavior and forest habitat selection; these are not discoveries by `batter`.

**Prospective new target:** Does independently sourced categorical land cover improve heldout *raw recorded MSL-height* ranking conditional on XY/time and an HMM movement state, using equal-night/bat weighting? **Do not interpret MSL as altitude above ground** without independent terrain reference and calibration; do not treat landcover as prey abundance; do not calculate HMM labels from heldout Z. Leave one entire bat and one landscape out in separate estimands. Do not copy individual coordinates to git receipts.

## B. Independent true-food study

Capaverde et al. 2018 Biotropica DOI [10.1111/btp.12546](https://doi.org/10.1111/btp.12546), original Dryad [10.5061/dryad.9rb48c5](https://doi.org/10.5061/dryad.9rb48c5); original `Bats_Ducke_data_metadata.xlsx` (67.67 KB on publisher page). Published 49 field plots / 52 bat species, 1,138 captures and 7,056 net-hours, night-linked ripe-fruit plant counts and trapped insect biomass, terrain elevation and vegetation clutter.

**Prospective new target:** Is there an out-of-plot prediction gain for frugivore/night-capture or species/guild composition over elevation + vegetation when adding **measured actual fruit/insect availability**? Compare on the same 49 spatially blocked plots and net effort, with independent guild-specific nulls; retain original species/published prior effects as PRIOR ART rather than representing this as an independent replicated study.

## C. Hard cross-study boundary

The Mexican *Chrotopterus* 3D trajectories and Brazilian Ducke true-food plots have different animals, sites, taxa, observation units, heights and years. They are **two independent predictions**, not a joint resource × height sample. No product `p(Bat,Food,XY,T,Height)` can be estimated by multiplying learned marginals from these studies.

Data isolation: this new gate fetches only official Dryad REST v2 dataset metadata → exact current version → official file inventory and digests. Publisher source IDs and file-size checks are recorded, no animal rows or exact GPS coordinates. Failed publisher file access is `SOURCE_STOP` and not a biological no-effect result.

**Status before this gate:** Original source files not verified; 3D habitat × true resource gain NOT ESTIMATED; old 49-fold NeoBat weak source-rank partner identity remains negative; frozen JAE and `main` untouched.
