# Individual covariate audit

Date: 2026-09-26

The checksum-pinned annotated and Movebank reference tables were compared after the primary
vertical-route results were obtained.

## Biological covariates

The authoritative Movebank reference table records all eight tracked bats as:

- adult;
- female;
- lactating;
- *Tadarida teniotis*.

Body mass spans 32.5–38.5 g. Thus sex, life stage and reproductive condition cannot explain the
observed among-individual vertical-route differences in this panel.

## Metadata inconsistencies in the annotated analysis table

Two identity/attribute discrepancies are present in the derived annotated file:

- Bat5 is marked `m` in the annotated `animal-sex` field but `f` in the Movebank reference data.
- Bat8 is stored as `Bat8` in the annotated table whereas the reference/raw tracking identity is
  `Bat8_3D6001852B9A7`.

These do not change the within-annotated-file self-transfer calculations, but reference-data
attributes and canonical raw IDs should be used for biological interpretation and manuscript
metadata.

## Remaining context confound

Animals were tracked during the same August 2017 field window. The next control therefore asks
whether a bat's other-night vertical rule predicts a target night better than contemporaneous
other bats flying under the same calendar-night context.
