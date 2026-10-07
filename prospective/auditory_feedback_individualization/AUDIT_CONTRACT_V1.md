# Auditory-feedback developmental individualization structural audit v1

## Status

**OUTCOME-BLIND PUBLIC-DATA STRUCTURAL AUDIT.**

No acoustic measurement values may be opened in this stage.

## Source

Elie et al. (2024),
*Role of auditory feedback for vocal production learning in the Egyptian fruit-bat*,
Current Biology 34:4062–4070.e7.
DOI: `10.1016/j.cub.2024.07.053`.

Public acoustic-measurement/code archive:
Mendeley Data `10.17632/h5ff9vv5pc.1`.

Published developmental manipulation:
- n = 10 pups total;
- 5 pups received kanamycin and became profoundly deaf;
- 5 pups received saline control;
- each treatment group contains 3 females and 2 males;
- adult vocalizations were recorded after years in a shared social environment.

The source paper already establishes treatment effects on subsets of the adult vocal repertoire.

## New programme question

The new question is not whether deafening changes the mean repertoire.

It is:

> **Does developmental auditory feedback alter the amount or stability of individual-specific vocal organization that forms by adulthood?**

This would address formation rather than current-context maintenance.

## Stage 1 authorized opening

Read only public source structure:

- file/folder names;
- sizes;
- hashes;
- code filenames;
- spreadsheet/MAT variable names;
- shapes/classes;
- column headers;
- individual identifiers;
- hearing-treatment labels;
- sex labels;
- call counts / structural repeated-measure counts.

Do not calculate:
- acoustic-feature means;
- treatment effects;
- individual centroids;
- identity accuracy;
- dispersion;
- p-values.

## Structural proceed gate

Proceed only if the public archive allows reconstruction of:

1. exactly 10 biological individuals or a clearly documented subset;
2. hearing/deaf treatment for each individual;
3. sex for each individual;
4. repeated adult vocal observations per individual;
5. one common multivariate acoustic representation measured identically in both treatment groups.

Preferred representation:
- source-provided acoustic feature matrix used in the publication;
- no outcome-driven feature selection.

## Design boundary

The publication excerpt available to this programme establishes a controlled treatment with balanced sex composition but does not, at this stage, establish random treatment assignment.

Therefore any later label permutation must be described as:
- a sex-stratified exchangeability test if random assignment cannot be verified;
- not a randomized-treatment test.

No stronger causal language is authorized without source documentation.

## Candidate later hypothesis

If structure passes, a later preregistration may test:

> after removing shared sex and call-class structure, hearing adults show a different amount of individual-specific vocal organization than deaf adults.

Possible directions are not frozen yet.

The next contract must choose one before acoustic values are opened.

## Claim ceiling

Even a positive result would concern adult vocal organization.

It would not establish:
- movement-policy formation;
- one universal individual-specialization mechanism;
- wild vertical individuality;
- a neural storage site;
- that auditory feedback is the only source of individuality.
