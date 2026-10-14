# Source-DOI and high-risk 2026 bibliography audit v2

**Date:** 2026-10-14  
**Scope:** Source-provenance and targeted public publisher/index verification; **not** an all-34-reference Crossref audit.

## Critical corrected source-to-panel mapping

During the integrated Supporting Information review, all three *Phyllostomus hastatus* year-to-Movebank DOI associations were found to be cyclically incorrect in the initial U3/S3 register. The six-panel original JAE rc2 Methods and the original immutable source-data preflight script independently agree on this correct mapping:

| Original analysis panel | DOI | Source-state / support |
|---|---|---|
| *P. hastatus* **2016** | **10.5441/001/1.282** | older single-source 2016 panel, primary vertical datum MSL |
| *P. hastatus* **2022** (2021–2022 source) | **10.5441/001/1.321** | longitudinal 2021–2022 source, primary vertical datum MSL |
| *P. hastatus* **2023** | **10.5441/001/1.322** | 2023 source, ellipsoid-height vertical datum |

**Independent primary source evidence:** JAE branch release/jae-v0.4.0-rc2, manuscript/MANUSCRIPT_DRAFT_V0_4_0.md, subsection “Independent comparative panels”; source-ingestion scripts/preflight_new_panel_context.py (phyllostomus_2016, phyllostomus_2021_2022, phyllostomus_2023 identifier/DOI pairs). The earlier unified SI draft had incorrectly assigned .282 to 2022, .321 to 2023 and .322 to 2016. This was a **source attribution transcription error**, not a changed or recomputed numerical outcome.

**Repair:** Both SUPPORTING_INFORMATION_DRAFT_V1.md and SUPPORTING_INFORMATION_ANONYMOUS_DRAFT_V1.md now use the source-matched mapping. CI source-attribution guards must reject any future wrong mapping in either table. Original JAE rc2 and BE experimental frozen sources remain unchanged.

## Targeted reference metadata verification

The following publisher/index sources were inspected, independently of the text in the repo:

| Publication | Verified publication | Corrected/current reference | Authority |
|---|---|---|---|
| Mathejczyk et al., individuality across contexts | *eLife* **13:RP98171**, version of record April 13, 2026 | Base DOI 10.7554/eLife.98171 is a valid work identifier; publisher identifies version of record DOI **10.7554/eLife.98171.5**, used in the updated integrated reference list | https://elifesciences.org/articles/98171/figures |
| Gallagher et al., clonal mollies stress | *Ecology Letters* **29(9):e70454**, first published September 14, 2026 | DOI **10.1111/ele.70454** verified; prior art supports mean shifts without change in total individuality, not the wild bat mechanism | https://onlinelibrary.wiley.com/doi/10.1111/ele.70454 |
| de Bivort, developmental origins | *Annual Review of Cell and Developmental Biology* **41:331–352**, 2025 | DOI **10.1146/annurev-cellbio-101323-025423** verified, Benjamin L. de Bivort | https://www.annualreviews.org/content/journals/10.1146/annurev-cellbio-101323-025423 |
| Teshima et al., bat flight | *Proceedings of the Royal Society B* **293(2076):20261463**, August 2026 | DOI **10.1098/rspb.2026.1463** confirmed; six-author list updated | https://pubmed.ncbi.nlm.nih.gov/42580728/ |
| Eveland et al., bat corridor flight | *Journal of Comparative Physiology A* **212(5):995–1008**, online July 24, 2026 | DOI **10.1007/s00359-026-01818-0** confirmed; five authors and volume/pages updated | https://link.springer.com/article/10.1007/s00359-026-01818-0 and https://pubmed.ncbi.nlm.nih.gov/42496733/ |
| Behavioral Ecology author guidance | OUP Behavioral Ecology current author instructions | Lay Summary <=75 words, abstract <=250 words, double-anonymous review, source data repository, single PDF SI, manuscript section order | https://academic.oup.com/beheco/pages/information_for_authors |

## Work remaining

- Verification covers a targeted high-risk subset, **not** all 34 main references or source-archive DOIs.
- Remaining paper metadata should be resolved against publishers and citation records, including author lists, capitalization, issue/pages and author/year matching.
- Source data permissions do not follow from DOI resolution; the unverified Taub & Yovel Dropbox licence remains a hard stop for bundling that raw archive.
- The bibliography union has 45 source-listed DOI entries; citing the eLife version-of-record DOI does not create a new publication or change historical source records.
- Reviewer-facing source references remain anonymized per journal guidance.
