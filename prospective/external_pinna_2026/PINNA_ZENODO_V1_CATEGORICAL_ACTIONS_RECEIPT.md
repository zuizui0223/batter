# Zenodo 2026 PNAS pinna data — official categorical support receipt (post-header gate)

## Status
**CATEGORICAL STRUCTURE ONLY. No original ear-tip separation, 3-D motion, target distance, or any other physiological numeric outcome values opened.** A valid source-file header provides batID and filename strings. Reading their counts is NOT an individual sensorimotor effect estimate.

- Record: Zenodo 20927789, doi 10.5281/zenodo.20927789, official Zenodo record/API HTTP200.
- Source Gate 0/1 corrected gzip+pipe regression: [GitHub run 37770368387](https://github.com/zuizui0223/batter/actions/runs/37770368387), artifact 11548135200.
- Categorical Gate 2 contract committed before opening any `batID` and `filename` rows: `PINNA_FLIGHT_CATEGORICAL_SUPPORT_GATE_V1.md`, commit `c4a4699c`.
- Initial Gate 2 source-only run 37770695336 succeeded programmatically but gave a **false retrieval STOP** because it used only `links.content` and omitted the officially returned `links.self` download fallback. Its biological-ID count was zero *due to no download* and is NOT a valid scarcity estimate.
- Corrected Gate 2 script commit `f9c6b31c`; authoritative [run 37771077152](https://github.com/zuizui0223/batter/actions/runs/37771077152), workflow **success**, artifact **11547966827**.
- Published raw audio/video and massive original MATLAB sources were NOT downloaded. No archive beyond the two version-pinned small CSV exports was processed.

## Actual checked source support (only categorical values)

| Source species/file | Source observation rows | Distinct `batID` *labels* | Distinct `filename` records | Distinct batID×filename pairs | Labels appearing in >=3 distinct filenames |
|---|---:|---:|---:|---:|---:|
| `mdau_basement` (*M. daubentonii*) | **21,249** | **5** | **39** | **39** | **5** |
| `ppyg` (*P. pygmaeus*) | **60,416** | **4** | **56** | **56** | **4** |

These 81,665 records are **camera/frame-level repeated observations**, NOT 81,665 physical bats or 95 independent animals. `filename` defines a plausible independent recording *file*, not automatically an independent treatment/day after quality assessment. The categorical source lists 5.5k inCluster rows for mdau and 4,062 for ppyg; 6,546 ppyg frame records are flagged isExcluded. The tabulated file counts are raw and are **not adjusted for usable independent flight intervals or the clustered subset**.

Source counts for mdau by number of distinct file records per label were `[3,6,9,10,11]`; for ppyg `[8,14,15,19]`. No actual bat labels were copied into this GitHub report. The `batID` original code exists in author MATLAB source.

### Critical unexpected source mismatch: NOT new biological replication

The author's `code/config_03_lcs_UCLOUD.json` lists four included `mdau` bats with IDs [101,102,7,9], but the published `mdau_basement` CSV contains **five distinct batID keys**. Therefore it is **incorrect to assert that all five keys are verified eligible physical individuals** or to assert the CSV contains only four. The fifth may be a source extra, non-author-selected identity, placeholder or another recording/protocol configuration; only direct original source metadata can resolve it. No numeric response opened, no identity matching force-fit. Four author-selected bats remain the validated published set.

The other `ppyg` source has four bat labels, matching the number listed in author `bat_ids=[1,9,10,12]`, but the key identity mapping itself is not newly validated from the candidate compiled CSV values.

## Independent primary Gate conclusion
`STOP_NO_INDEPENDENT_INDIVIDUAL_BOUTS` remains authoritative **for the preregistered personal ear-to-flight-heading primary**, because:
1. per-species genuine physical identity >=5 is not documented in the author's analyzed four-bat cohorts;
2. the chosen compact CSVs record `earTipSep` rather than left/right ear/head/flight-heading 3-D vectors needed for the specified *ear-to-flight-heading policy*;
3. two prospectively verified comparable task/perturbation contexts are **not established** by the chosen individual export, regardless of file/bat label count;
4. inCluster/exclusion and independent flight file eligibility have not been validated without opening quantitative measures.

This is NOT an absence of individual ear-movement variability; it is a *data support and endpoint availability* stop. It is also not evidence for conspecific social-acoustic interference, which this wind-tunnel single-bat study did not manipulate.

### Prior-art and integrity firewall
The original PNAS 2026 finding—forward/target-focused hearing at high speed—is already published. The first public source-reader produced a false positive from HTTP gzip bytes; this was corrected. The source reader later misparsed pipe-separated columns, then fixed. The categorical scanner initially failed to follow official `links.self` and was corrected. All corrections and failed passes/stops are retained chronologically rather than erased or represented as animal results.

**Decision:** no numerical physiological model fitted and no per-bat predictive claims made. Freeze the source audit as a successful *availability/eligibility* result and prioritize the already-frozen JAE rc2 submission over a post-selected small n new sensory policy project.
