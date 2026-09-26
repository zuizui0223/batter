# JAE submission readiness v0.3.2

Checked: 2026-09-27

## Current target

First shot: **Journal of Animal Ecology — Research Article**.

Backup: **Movement Ecology**.

## JAE format gates already implemented

- main text in English;
- standard Introduction / Methods / Results / Discussion structure;
- numbered abstract with five factual statements;
- abstract CI limit: <=350 words;
- alphabetized keywords: <=8;
- manuscript CI word-count ceiling: <=8,500 words;
- central claim reconciled with focal V2 negative;
- public-data source universe frozen and closed.

The automated gate is `scripts/check_jae_submission.py`.

## Scientific gates already closed

- focal conditional identity repeatability;
- focal residual-map negative retained;
- AGL / terrain semantic validation;
- same-night context control;
- pairwise alternative-individual robustness;
- *Eidolon* independent replication;
- *Hypsignathus* independent replication;
- *Phyllostomus* marginal-dominant counterexample;
- 2023 temporal panel;
- untouched 2016 prospective 2022-like prediction failure;
- common uplift mechanism negative;
- outcome-blind 23-dataset public search closeout.

No additional public-data mining belongs in this paper.

## Remaining submission tasks

### Required before submission

1. Produce Figure 1 conceptual schematic from the frozen definitions.
2. Generate final Figures 2–6 and inspect labels at journal size.
3. Add a complete formatted reference list.
4. Add explicit Data and Code Availability statements with repository/data-package DOIs.
5. Add an Ethics statement clarifying that this is a reanalysis of public tracking data and
   citing original source-study approvals where required.
6. Add author contribution, funding, conflicts and acknowledgements on the separate title page.
7. Render a double-spaced, continuously line-numbered anonymous review PDF.

### Editorial polishing

- shorten Methods implementation detail that belongs in Supporting Information;
- make the ecological principle explicit in the first and final Introduction paragraphs;
- keep ODSP to motivation/provenance only;
- call G_cond - G_marg **conditional advantage**, not a latent interaction;
- preserve prospective negative results in main text rather than hiding them in supplement.

## Cover-letter angle

A short optional JAE cover letter should emphasize:

- individual specialization is usually treated as a magnitude, but this paper asks how identity
  is spatially organized;
- an outcome-blind public-data screen yields contrasting predictive architectures rather than a
  uniformly positive result;
- a stronger focal mechanism test and a prospective within-species prediction both fail and are
  retained, sharpening the claim rather than rescuing it.

## Stop rule

If Figures 1–6, references and availability/ethics statements are complete and the automated JAE
gate passes, the manuscript is submission-ready under the current empirical freeze.
