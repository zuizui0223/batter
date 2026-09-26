# Public bat panel search closeout

Date: 2026-09-26

## Decision

The public-data expansion search is **closed**. No further bat dataset will be added to the
current comparative programme.

## Outcome-blind search path

DataCite discovery under Movebank DOI prefix `10.5441` returned 23 parent bat datasets with
plausible movement records.

Nineteen parent packages exposed raw event CSVs directly and were checksum-pinned before
structural screening. Four legacy parent packages required child-handle recovery and were screened
separately after their source identities/checksums were frozen.

At every admission stage, allowed reads were limited to:

- schema/header names;
- individual identifiers;
- timestamps;
- finite x-y structure;
- presence/missingness of a native vertical field as a string;
- source outlier flags;
- taxon labels.

Numeric height values were not used to select datasets.

## Structural result

The common gate required:

- a native same-event vertical coordinate;
- >=8 individuals with x-y-height presence;
- >=5 individuals with at least two eligible >=50-fix sessions.

Six sources from four taxa passed:

- *Tadarida teniotis*;
- *Eidolon helvum*;
- *Hypsignathus monstrosus*;
- *Phyllostomus hastatus* (three temporal datasets).

All other directly resolved datasets failed before vertical outcomes.

## Legacy recovered sources

Four additional child-handle datasets were recovered after their parent DOI packages failed
modern DSpace resolution. None passed the frozen gate:

| Dataset | Native height | Individuals | Repeat individuals | Decision |
|---|---|---:|---:|---|
| *Pteropus poliocephalus* | height above MSL | 4 | 4 | underpowered |
| *Nyctalus noctula* 3-D migration | height above MSL | 3 | 0 | underpowered |
| Christmas Island flying fox | height_raw | 27 | 4 | underpowered repeat panel |
| *Pteropus lylei* | none | 0 | 0 | vertical axis unavailable |

No numeric height values were parsed for these closeout decisions.

## Why stop here

Continuing to search after observing the comparative outcomes would turn source discovery into an
outcome-adaptive process. The current panel is therefore frozen at four taxa.

The appropriate next extension is a **new independent dataset collected or selected
prospectively under a new programme**, not further mining of the present search universe.
