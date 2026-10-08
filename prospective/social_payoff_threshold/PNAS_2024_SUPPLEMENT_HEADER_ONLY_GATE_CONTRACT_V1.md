# PNAS 2024 Supplementary Dataset S01 alternate public source gate — pre-header freeze

**2026-10-08, 23:39+09:00 continuation.** Source-structure only. No prior Mendeley outcome values opened. Mendeley public API metadata and file list both returned HTTP 401 in [CI 37793760213](https://github.com/zuizui0223/batter/actions/runs/37793760213). This is an **access-path failure**, not a proof that records do not exist.

Original article: Krivoruchko et al. (2024), `PNAS`, DOI `10.1073/pnas.2321724121`. Its [public PMC index](https://pmc.ncbi.nlm.nih.gov/articles/PMC11287165/) explicitly advertises **Dataset S01 (XLSX), 160 KB, `pnas.2321724121.sd01.xlsx`** as a separate supplement. It may contain plotted/aggregated data only. The exact content and downloadability have **not** been established. Do not claim it is the same as the 10-bat 5-sec Mendeley archive.

## Frozen download targets and source boundaries

Only request these two path forms (in order, HEAD/GET without arbitrary crawling):
1. `https://pmc.ncbi.nlm.nih.gov/articles/PMC11287165/bin/pnas.2321724121.sd01.xlsx`
2. `https://www.pnas.org/doi/suppl/10.1073/pnas.2321724121/suppl_file/pnas.2321724121.sd01.xlsx`

These are **candidate** canonical publisher/PMC paths, not verified download links. If both fail, `STOP_ALTERNATE_SUPPLEMENT_INACCESSIBLE` and do not silently swap to an unrelated file. Redirect target must stay under trusted `pnas.org`, `ncbi.nlm.nih.gov`, `nih.gov`, or `pmc.ncbi.nlm.nih.gov` hosts; stop if not.

A successfully downloaded resource must be an XLSX ZIP with expected workbook structures; at most 2 MiB; validate all ZIP uncompressed metadata safety budgets, no macros, no external links, no formula evaluation. At this phase **do not iterate worksheet numeric values**.

## Categorical/schema-only allowed extraction

- file size/SHA256 and recognized container mime;
- worksheet names and actual internal sheet paths;
- declared dimensions, approximate row counts, first-row **column headers** only (shared-string lookup allowed solely for row 1);
- existence of explicit fields for **physical bat ID**, **date/night/session/bout**, **time bin**, **call exposure**, **attempted attacks**, and **successful captured prey**. Classification by header labels, not by numeric values.
- never enumerate distinct numeric bat IDs or observation values, nor read biological value cells below row 1.

## Gate logic

- `STOP_ALTERNATE_SUPPLEMENT_INACCESSIBLE`: no valid XLSX obtained.
- `STOP_NO_BAT_BOUT_STRUCTURE_IN_SUPPLEMENT`: workbook accessible but lacks independent physical bat identifier and potential bout/session columns on any tab; likely figure-source table only, do not rescue it by guessing bat identities.
- `HOLD_HEADERS_ONLY_INDEPENDENT_BOUTS_NOT_YET_VERIFIED`: header patterns include bat ID and bout or day key, but **no real row-level structural count has been opened**, so cannot claim independent bouts or density crossing yet.
- `STOP_UNEXPECTED_SOURCE_SCHEMA_OR_SIZE`: corrupt/oversize/mismatched ZIP or unexpected source.
No `PASS` to numerical inference is available in this phase.

**Scientific ceiling:** this is merely a targeted attempt to verify whether an alternate source has the categorical keys needed for the independently defined functional personal social-threshold hypothesis. The already published population hump-shape is prior art; reading it again is not a new biological result. Human review and independent bat×bout source support are still necessary.
