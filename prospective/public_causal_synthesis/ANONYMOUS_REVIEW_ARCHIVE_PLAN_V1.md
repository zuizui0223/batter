# Anonymous review archive plan v1

## Current target

Generate one deterministic sanitized ZIP that can be uploaded to an anonymous review repository without hand-copying analysis files.

Output:
`dist/behavioral_ecology_anonymous_review_archive_v1.zip`

## Included synthesis files

- complete anonymous manuscript;
- evidence matrix;
- master results table;
- numerical audit;
- supplementary-material source;
- figure captions and alt text;
- synthesis figure-generation code;
- generated SVG figures;
- source-data permanence manifest.

## Included source-analysis families

### Ontogenetic history
From `prospective/ontogenetic-path-dependence-v1`.

### Randomized early-environment history carrier
From `prospective/early-experience-history-carrier-v1`.

### Randomized enrichment individualization
From `prospective/early-experience-specialization-v1`.

### Developmental auditory feedback
From `prospective/auditory-feedback-individualization-v1`.

### Pipistrellus sensory masker
From `prospective/reversible-sensory-perturbation-v2`.

### Myotis graded masking
From `prospective/myotis-masker-personal-state-v1`.

### Eptesicus auditory-midbrain perturbation
From `prospective/auditory-perturbation-policy-v1`.

### Aharon navigation-context manipulation
From `prospective/public-perturbation-audit-v1`.

### Rhino / Carollia portability
From `prospective/task-reset-lockin-v1`.

### Wild evidence boundary
From `prospective/evidence-provenance-correction-v1`.

## Raw source data

Most source data are not duplicated because they already live in DOI repositories.

One exact source subset **is** copied into this review bundle:

### Carollia / Eveland et al. 2026
- original source location: `00keveland/Tunnel_2026`;
- pinned commit: `59928a71887d521fec143080b0b187736c046a0e`;
- license: CC0 1.0;
- mirrored files: 28 C2-C8 trajectory MAT files;
- expected bytes: 5,286,659;
- file-level SHA256 receipt generated during archive build.

Taub raw data remain source-public on Dropbox but are not mirrored because dataset redistribution permission has not been independently verified.

A final Behavioral Ecology data deposit therefore has only one unresolved source-permanence issue: Taub.

## Stop rule

Do not upload the generated ZIP as-is to a public identified account for double-anonymized review.

First:
- inspect the generated anonymity scan;
- upload through an anonymized repository/review link;
- replace `[ANONYMIZED_REVIEW_ARCHIVE_URL]` in the Complete Anonymous Text.
