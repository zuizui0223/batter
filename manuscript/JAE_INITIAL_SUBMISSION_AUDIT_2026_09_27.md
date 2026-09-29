# Journal of Animal Ecology initial-submission audit

Checked against the journal's public initial-submission author guidelines on 2026-09-27.

Guideline:
https://besjournals.onlinelibrary.wiley.com/hub/journal/13652656/author-guidelines

## Current compliance

- **Article type:** Research Article.
- **Word limit:** journal limit 8,500 words including title page, abstract, references and legends.
  Repository v0.3.8 main-manuscript CI estimate is 7,887 words; final combined count must be reconfirmed
  after title-page metadata are filled.
- **Abstract:** 282 words, below the 350-word limit.
- **Abstract structure:** five numbered statements.
- **Keywords:** seven, alphabetized, below the maximum of eight.
- **Review format:** double-spaced, continuous line numbering and page numbering are produced by
  the review-PDF workflow.
- **Double anonymization:** the v0.3.8 review generator suppresses the author-identifying repository
  owner; the dedicated leak guard passes on the 26-page review PDF.
- **Separate title page:** the frozen scaffold is `manuscript/TITLE_PAGE_TEMPLATE_V0_3_8.md`; the journal-upload title page is generated as `manuscript/TITLE_PAGE_V0_3_8.md` from the one-source metadata JSON.
- **Data availability:** the title-page scaffold lists all six Movebank dataset DOIs. The final versioned Zenodo DOI is inserted only in the post-DOI metadata stage, after Zenodo has archived the GitHub release.
- **Human metadata:** authorship, affiliations, corresponding-author details, CRediT, acknowledgements, funding and conflict declaration are all centralized in `submission/jae_v0_3_8_metadata.json`; none are inferred.
- **References:** all 16 references currently in v0.3.8 include DOI links.
- **Graphical abstract:** not treated as an initial-submission blocker; the journal requests it at
  revision stage.

- **Cross-panel confound audit:** completed under pre-output frozen contracts; failures and sample-size attrition are retained in the main manuscript.
- **Effect-size null calibration:** pairwise and metre-scale biological translations use their own session-label exchangeability baselines.
- **Final tag-altitude-bias audit:** complete under pre-output frozen rules; 5/6 panels retain centered-shape identity and 2/2 structurally eligible panels retain identity after stationary offset correction.
- **Ecological shape visualization:** descriptive Figure 6 reconstructs the already-tested common-cell self profiles and visually illustrates variation in central concentration and tail use. Those component ranges are not separately exchangeability-calibrated and may include finite-session estimation noise; the inferential claim remains at the full centered-profile level.

## Remaining blockers

1. fill the one-source metadata JSON except `archive_doi`;
2. choose/add the matching repository software LICENSE;
3. pass the pre-release metadata assembler and Zenodo release gate;
4. enable the repository in Zenodo and publish the GitHub release;
5. insert the minted version DOI into the same metadata JSON;
6. pass the post-DOI assembler and final JAE upload gate;
7. confirm the generated combined word count remains <=8,500;
8. perform final journal upload.

The metadata path has passed an end-to-end synthetic Actions self-test (v0.3.8 metadata self-test).

No additional ecological analysis is required or authorized before submission.
