# Anonymous review archive — public bat individuality synthesis

## Purpose

This archive supports anonymous peer review of a comparative secondary reanalysis of public bat experiments.

It contains:
- frozen source-level analysis contracts;
- executable analysis scripts where available;
- source-level result receipts where committed;
- manuscript-level numerical provenance;
- evidence-tier maps;
- synthesis figure-generation code;
- anonymous manuscript/supporting material files.

It does **not** assert authorship and contains no author-owned repository URL.

## Source data

All biological data originate from previously published public studies.

See:
- `DATA_SOURCE_MANIFEST.csv`

Most source datasets already have permanent DOI-based repositories.

Two source-specific permanence issues are intentionally flagged:
1. Eveland et al. source data are published by the source authors on GitHub under CC0; the exact used files can be mirrored legally into the final DOI archive.
2. Taub & Yovel source data are published by the source authors through Dropbox; this review archive does not redistribute those raw files because a dataset-specific redistribution license has not been independently verified.

## Reproducibility scope

The archive distinguishes:
- confirmatory/frozen source-level results;
- predeclared secondary results;
- post-primary diagnostics;
- descriptive/exploratory analyses;
- failed frozen gates.

The manuscript-level authoritative maps are:
- `synthesis/EVIDENCE_MATRIX_V1.md`
- `synthesis/MASTER_RESULTS_TABLE_V1.md`
- `synthesis/MANUSCRIPT_NUMERICAL_AUDIT_V1.md`

## Review anonymity

This bundle is built from an identified development repository but is sanitized before packaging.

The build fails if it detects:
- the development account name;
- the identified development-repository URL;
- explicit author-name tokens listed in the build guard.

The final review archive should be uploaded to an anonymized repository record or anonymous view-only review link before manuscript submission.

## Permanent publication archive

For publication, the archive should be deposited in a DOI-capable permanent repository accepted by Behavioral Ecology (e.g. Dryad, figshare, Harvard Dataverse, OSF, or Zenodo).

The final permanent record must include:
- source-data citations;
- any redistributable raw/derived data required by the journal data editor;
- README;
- analysis scripts/result receipts used for reported analyses.

Do not use GitHub alone as the final journal data archive.
