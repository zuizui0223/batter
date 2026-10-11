# JAE v0.4.0 RC2: public DataCite source rights metadata — executed audit, 2026-10-10

**EVIDENCE TIER: source-specific rights declarations recorded in DataCite metadata; NOT legal sign-off, owner correspondence or permission to relicense data.** This is an editorial source audit only. No original bat event records, locations, tag identifiers, numerical analyses, JAE scientific claims or frozen manuscript files were opened or modified.

## Freeze and authoritative execution
- Original fixed ten-DOI list: `submission/jae_v0_4_0_original_source_rights.template.json`, all licence status `UNVERIFIED` before querying.
- Pre-source contract: `submission/JAE_RC2_DATACITE_SOURCE_RIGHTS_METADATA_GATE_2026_10_10.md`.
- Official executed [GitHub Actions **38057807343**](https://github.com/zuizui0223/batter/actions/runs/38057807343) — **SUCCESS**, job `114229757731`. The report JSON is retained as the run artifact `jae-rc2-ten-original-source-doi-metadata-only` (artifact ID **11672108870**).
- Script `scripts/inspect_jae_v0_4_0_original_doi_rights_metadata.py` queried **only** `api.datacite.org/dois/{exact frozen DOI}`, checking returned exact DOI identity, extracting recorded `rightsList` and publication year, never data files.
- **All 10 canonical DOI lookups returned HTTP 200**, all ten DataCite responses contained explicit Creative Commons terms, and all status codes remain `METADATA_CC_CANDIDATE_NEEDS_DATASET_TERMS_CONFIRMATION`, not permission accepted.

## Rights declarations present in the DOI records (verbatim licence types)

| Published source dataset DOI | Source scope | Exact machine-readable licence in DataCite |
|---|---|---|
| `10.5441/001/1.52nn82r9` | Original *Tadarida teniotis* | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5441/001/1.k8n02jn8` | Original *Eidolon helvum* | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5441/001/1.278` | Original *Hypsignathus monstrosus* | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5441/001/1.282` | Original *Phyllostomus hastatus* 2016 | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5441/001/1.321` | Original *Phyllostomus hastatus* 2022 | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5441/001/1.322` | Original *Phyllostomus hastatus* 2023 | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5281/zenodo.7535030` | External boundary *Nyctalus noctula* | **CC BY 4.0 International** (`cc-by-4.0`) |
| `10.5061/dryad.j0zpc86r1` | External boundary *Hipposideros armiger/pratti* | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5441/001/1.kk3bg2f4` | External boundary *Myotis vivesi* | **CC0 1.0 Universal** (`cc0-1.0`) |
| `10.5441/001/1.5bd6pq55` | External boundary *Pteropus poliocephalus* | **CC0 1.0 Universal** (`cc0-1.0`) |

DataCite reports direct licence URLs `https://creativecommons.org/publicdomain/zero/1.0/legalcode` (CC0) and `https://creativecommons.org/licenses/by/4.0/legalcode` (CC BY). The source-reported `Nyctalus` entry also separately says “Open Access,” which is NOT a substitute for its CC BY attribution conditions.

## What this means — and what remains unverified

- [Movebank's original Terms of Use](https://www.movebank.org/cms/movebank-content/general-movebank-terms-of-use) specifically say that public downloadable CC0, CC BY or CC BY-NC content ordinarily does **not** require extra individual owner permission for permitted licensed uses, while scholarly citation, license conditions and respectful reasonable owner contact for new applications remain relevant. This general rule does not establish whether a specific archived data **version** has special publisher/depositor instructions, restrictions on sensitive site disclosure or derivative sharing; humans must examine each DOI landing rights text.
- CC0 is a public-domain dedication with minimal enforceable attribution licence conditions; scholarly citation of original data collectors and source papers is **still scientifically expected**. CC BY `Nyctalus` requires attribution, licence notice and appropriate indication of changes if applicable. Do not erroneously classify it CC0 because the majority are CC0.
- Public licence permission for *data reuse* is distinct from the right to republish **raw wildlife GPS telemetry**, reuse restricted images or claim original animal ethics approval. No original raw tracking data or sensitive coordinates were uploaded in this check.
- A repository root `LICENSE` for newly written code **does not licence or change** the ten original datasets. The authors must choose exactly one compatible rights-holder-approved code licence in the frozen final release pipeline.
- This metadata audit should allow coauthors to resolve source-rights questions **faster**, but the automated journal signoff must stay `HOLD_HUMAN_POLICY_SIGNOFF` until author-approved verified source term/attribution metadata and substantive AI/inclusion declarations are complete.

## No-go assertions
No claim that all source owners were contacted, consented, waived publication credit, approved sensitive derived maps, approved author's code licensing or approved JAE submission is warranted by public DataCite metadata. Do not alter frozen JAE p-values/manuscript or proactively distribute original raw files based on this audit.

**Scientific workflow disposition:** `DOI_RIGHTS_METADATA_CANDIDATES_ALL_TEN_OBTAINED; DATASET_TERMS_AND_HUMAN_SIGNOFF_STILL_REQUIRED`.
