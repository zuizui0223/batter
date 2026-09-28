# batter v0.3.7 — Journal of Animal Ecology submission archive

This release is the versioned code, analysis-contract and provenance snapshot accompanying the
Journal of Animal Ecology submission:

**Repeatable vertical identity in bat airspace persists after coarse horizontal occupancy is standardized**

## Scientific summary

Across six bat tracking panels, identity-matched vertical profiles retain more held-out predictive
information than expected under panel-specific whole-session exchangeability after self and other
profiles are standardized to the same occupancy among tested coarse 5-km horizontal cells.

The strongest comparative result is that all five non-*Tadarida* panels retain calibrated
individual identity in vertical-distribution shape after every session is translated to zero
median, which removes any additive constant altitude offset. The motivating *Tadarida teniotis*
panel is retained as a boundary case because its centered-shape identity is not supported.

The repository also preserves the methodological audit showing that intuitive zero or 0.5
references are not universal nulls for finite prediction pipelines. The complete analysis
pipeline is therefore calibrated under session-label exchangeability.

## Reproducibility and provenance

This release contains:

- frozen source-admission and analysis contracts;
- source checksums and provenance;
- all retained negative robustness results;
- cross-panel estimator calibration;
- endpoint-neighbourhood and effect-null audits;
- the final tag/device altitude-bias audit;
- figure-generation scripts;
- the comparative-first v0.3.7 manuscript and Supporting Information.

No new scientific analysis is authorized after the final tag/device audit.

## Public tracking data

The tracking datasets are archived in the Movebank Data Repository:

- *Tadarida teniotis*: 10.5441/001/1.52nn82r9
- *Eidolon helvum*: 10.5441/001/1.k8n02jn8
- *Hypsignathus monstrosus*: 10.5441/001/1.278
- *Phyllostomus hastatus*: 10.5441/001/1.282
- *P. hastatus*: 10.5441/001/1.321
- *P. hastatus*: 10.5441/001/1.322

## Release metadata

Author, affiliation, license and citation metadata are provided by the final `CITATION.cff` and
repository `LICENSE` included in the release.

Zenodo should archive this GitHub release and mint the version DOI. That version DOI is then added
to the separate journal title page; it is not required inside these release notes before minting.
