# Rousettus original author GitHub mirror vs official Dryad: a strict two-file publisher hash gate

2026-11-20. Source-gate only; no original animal, tree, treatment, or 3D movement response is fitted or committed.

Original publisher [Dryad DOI 10.5061/dryad.51c59zwgp](https://doi.org/10.5061/dryad.51c59zwgp) has now passed dataset DOI → version → file manifest official API verification, whereas direct content file GET is [HTTP401, with STOP artifact](https://github.com/zuizui0223/batter/actions/runs/44682168574). The original published [Lourie et al. 2024 article DOI 10.1098/rstb.2024.0060](https://doi.org/10.1098/rstb.2024.0060) names [author-maintained GitHub `EmmLourie/Information-transfer-analysis`](https://github.com/EmmLourie/Information-transfer-analysis), pinned to commit `1d7edbdbb87d9df048ab42a0b425a1966d491e86`.

Only two tiny author files are exact path candidates `data_R/Field_Manipulation_Table.csv` (291 bytes listed by GitHub), `data_R/Tags_manipulated_and_visiting.csv` (1371 bytes listed by GitHub). Their official **publisher-file** byte counts and digests will be compared with the exact downloaded author bytes; if a single mismatch occurs, fail closed and do not claim publisher-equivalent original source. The third relevant file `manipulations_trees_locations.csv` is NOT present in the author repo tree under that name. Missing third file is NOT imputed.

The workflow parses only header names AFTER original publisher hash match. It does not open biological data rows from CSV, download full 285 MB SQLite tracks, quantify experimental cue response, calibrate fruit abundance, verify 3D height, or fit a high-dimensional SDM. The published field manipulation includes fruitless *Ficus* targets and an information cue, not direct measurements of resource supply.

Success would authorize an *original-content authenticated partial 2D data source*, **not** an independent biological confirmation or solved animal×tree×height join. Status of the original Dryad direct-file access remains HTTP401 regardless of mirror matching.
