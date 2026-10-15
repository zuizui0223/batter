# One-commit recovery of the source code for the original bat terrain-relative 3D result

**Recovery audit:** 2026-10-15. **Reproducibility tier:** source-code/contract/checksum closure, **not** a full rerun of GPS/DEM observations or a new scientific outcome.

## Why this matters

The original 500-m terrain-relative wild bat result was obtained from a successful 2026 workflow. However, the final JAE frozen branch `release/jae-v0.4.0-rc2` retains the original terrain driver but **omits files it dynamically imports**, including the original joint-3D `run_v1.py`, external geometry helper, and its native source contract. Therefore the frozen branch alone cannot honestly be called fully re-executable at that stage.

Rather than silently rebuilding lost scripts from memory, the unified-manuscript PR now provides a recoverable **single historical execution-source tree** taken from the *exact historical terrain workflow source commit*:

- **Original terrain workflow:** [36946126004](https://github.com/zuizui0223/batter/actions/runs/36946126004).
- **Source Git commit:** [`819acc829d615485b57033f1ddcbebf64b4b49a0`](https://github.com/zuizui0223/batter/tree/819acc829d615485b57033f1ddcbebf64b4b49a0).
- **Native 3D ancestor workflow:** [36881187913](https://github.com/zuizui0223/batter/actions/runs/36881187913), with original native result `summary_v1.json` stored **unchanged** under both the native-recovery evidence and this exact historical source tree.
- **Source manifest:** [`source_recovery/terrain_source_closure_manifest_v1.json`](source_recovery/terrain_source_closure_manifest_v1.json) pins **21 historical source files by original Git blob SHA-1**.
- **Source recovery program:** [`source_recovery/recover_terrain_source_closure_v1.py`](source_recovery/recover_terrain_source_closure_v1.py) fetches only the exact source files from GitHub at that commit, validates the original Git blob identity of each, parses the Python/JSON structures, checks the direct intra-repository imports, and generates one deterministic source-only ZIP.

The recovered tree includes four source-specific *Phyllostomus*/*Hypsignathus* contracts, original terrain DEM preflight checksums, run-driver, both dynamically imported 3D geometry modules, calibration/tag-offset/source preprocessing scripts, the `batter.analysis` package and historical `pyproject.toml`.

## What was (and was not) independently checked

**Now checkable from original version-controlled historical bytes:**

- Exact single-commit source identity of each runner, loader, analysis helper, preflight receipt and panel contract.
- That the dynamic runner's relative import paths exist in the recovered historical source tree, even when those imports are missing from the later frozen JAE branch.
- Native 3D result provenance `run_id=36881187913` and historical source contract `batter-original-panel-terrain-3d-geometry-v1`.
- Source-definition distinction between normalized per-session (R_{3D}=1-O_{XYZ}/O_{XY}) and panel summaries: averaging per-pair ratios is **not** a ratio of already pooled mean overlaps.
- No raw Movebank GPS fixes, tag files, private source archives, large DEM tiles, or reanalysis-generated inferential statistics are written into the output archive.

**Not established by source closure alone:**

- End-to-end numerical reproduction of the terrain geometry original results or its 9,999 label-permutation nulls.
- Availability and redistribution rights of the original Movebank GPS/event files, DEM tiles or other third-party bitstreams.
- Exact package versions and full computational operating system from the historical success run. In particular, the historical Python runners import `pandas` and `requests` as well as the declared `numpy` and `pyproj`; the original `pyproject.toml` alone does not freeze those versions.
- Correctness of original source authors' animal-ID cross-study mappings, ecological causal mechanisms or any unreported sensitivity family.

## Reviewer procedure

1. Check out this unified PR branch. Run the Python 3.12 script with `--inventory-only` to validate its fixed 21-file manifest without networking.
2. Invoke the script with an output directory; it retrieves each GitHub historical source file and checks its expected Git blob SHA before writing anything. It creates `terrain_original_3d_source_closure_v1.zip` containing the original relative directory structure and a frozen manifest. `--offline` revalidates a previously retrieved tree without any networking.
3. Use GitHub Actions workflow [`unified-historical-terrain-source-closure-v1.yml`](../../.github/workflows/unified-historical-terrain-source-closure-v1.yml) to obtain the same source-only ZIP as a PR artifact. No original raw bat tracking or DEM has been duplicated into this package.
4. A subsequent **separate permissions-checked reproducibility project** may use the exact historical source and the original source-specified data/DEM checksums to try a complete rerun. Such a rerun is explicitly **not claimed in the present paper integration** and must not be described as a confirmed raw-data replication without an actual completed results audit.

## Ecological inference unchanged

The previous original results retain their separate test/evidence tiers: terrain-relative individual vertical fidelity supported in 4/4 original structural panels (two species), **positive** added segregation S_rel not supported in any of those 4, and synchronous extra co-use separation supported only in one heterogeneous 2023 *P. hastatus* design. Recovered code cannot retroactively elevate post-outcome diagnostics to independent prospective confirmation. The new original native 3D overlaps also remain distinct from the one-dimensional Figure S1 shape-overlap coefficients calculated from different, nonidentical original panel records and supports.

**Publication status:** historical code-provenance recovery for reviewer transparency; no journal submission, new animal study, scientific outcome claim or amendment of original frozen JAE/BE branches.
