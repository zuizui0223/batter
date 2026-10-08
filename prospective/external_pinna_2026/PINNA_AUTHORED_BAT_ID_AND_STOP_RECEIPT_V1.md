# Author code resolves number of biological bats in the 2026 PNAS ear-gaze exports

**EVIDENCE LEVEL: author public analysis configuration and corrected official Zenodo CSV HEADERS, not new bat phenotypes.**

Author source: https://github.com/fhaefele/target-focused-hearing-of-echolocating-bats-pnas/blob/main/code/config_03_lcs_UCLOUD.json

In the author's `params_specific.bat_ids` array:
- M. nattereri: [3,4,5,8] → **4 selected biological bats**.
- M. daubentonii: [101,102,7,9] → **4 selected biological bats**.
- P. pygmaeus: [1,9,10,12] → **4 selected biological bats**.

The author processing code `code/bat_ears_03_lcs.m` (lines 110–125 and 140–155) uses those bat IDs to map each source recording path with `get_bat_number` before aggregating features per individual, providing much stronger provenance for `batID` as an individual key than the string `batID` appearing by itself in a CSV header. `vid_select` has four bat indices per source species, and recording filenames appear in author exclusion lists. Thus the study is designed around repeated recordings **within up to four selected bats per species**, not a large independent cohort.

The fixed eligibility criterion in `PINNA_FLIGHT_IDENTITY_STRUCTURAL_CONTRACT_V1.md` was **at least five distinct biological individuals**, each with >=3 independent recording bouts, before physiological values would be opened for a new individuality primary. The categorical follow-up contract requires this within a species to avoid pooling distinct species as repeated instances of one biological strategy. The author-defined complete analyzed animal set is **4 per species**, below this support floor, so the proposed *new confirmatory personal pinna-gaze primary* must be labelled:

`STOP_NO_INDEPENDENT_INDIVIDUAL_BOUTS: INSUFFICIENT_WITHIN_SPECIES_N`.

Even if large numbers of per-frame measurements or repeated files exist, they are not independent biological animals. Cross-species aggregation into 12 without a justified, pre-frozen hierarchical transferable physiological endpoint would not rescue it. A separate categorical row-count workflow may confirm file/bout counts, but cannot change this hard N gate. No physiological numeric values have been opened or modeled in the new analysis.

## Reproducibility and source-reader corrections

- Source DOI 10.5281/zenodo.20927789, record ID 20927789, author PNAS 2026 doi 10.1073/pnas.2605701123.
- The initial GitHub Actions run 37767065293 made a **false-positive one-column CSV schema pass** because its first attempt did not decompress `Content-Encoding: gzip`. This must be kept in the audit trail; it was not a biological outcome.
- Subsequent run 37770167453 decompressed correctly but failed to recognize PIPE-delimited exports.
- Corrected run [37770368387](https://github.com/zuizui0223/batter/actions/runs/37770368387), artifact 11548135200, recognized the model CI file's six comma-delimited columns and the two true sensorimotor files' fifteen PIPE-delimited columns, including `batID`, `filename`, `dataStructNr`, `recTimePosix`. All three HTTP200.
- The author's full raw videos require contact; the Zenodo files are compiled figure-generation material, not necessarily all independent original trials.
- Independent numerical ear-to-heading prediction was NOT executed because minimum within-species biological N is not met and no one chosen physiological outcome contract was authorized.

## Scientific boundary
This is an **external sample-size/structure stop**, not a null of individual variation. The known 2026 finding that ears face prey remains valid published prior art. If the question changes to descriptive per-bat ear lateralization or a single-species small-n diagnostic, that would be a different and explicitly nonconfirmatory, post-source-exposure project; no favorable subset fishing permitted here.

The current programme should prioritize the already-frozen independent wild bat 3-D JAE manuscript and the separate causal experiments rather than manufacture another same-source n=4 individual repeatability claim.
