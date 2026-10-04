# Species-to-CSV batch provenance v1

## Status

**FROZEN BEFORE ANY CSV TRAJECTORY ROW VALUE IS READ.**

Parent:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- `CSV_HEADER_OPENING_ALLOWLIST_V1.md`
- `PICKLE_STRING_METADATA_AMENDMENT_V1.md`

## Source facts

The peer-reviewed source study reports two species and subject counts:

- *Rhinolophus nippon*: **5 individuals**;
- *Miniopterus fuliginosus*: **4 individuals**.

The Figshare landing page independently defines:
- `kiku` = *Rhinolophus nippon*;
- `yubi` = *Miniopterus fuliginosus*.

## Outcome-blind Figshare structure

The 64 CSV trajectory files form two non-overlapping upload-id batches.

### Batch G4

File ids:
`55033796 ... 55033850`

Observed metadata-only structure:
- 19 CSV files;
- bat labels present: A, B, C, D;
- **4 unique bat labels**;
- no BatE.

### Batch G5

File ids:
`55033853 ... 55033985`

Observed metadata-only structure:
- 45 CSV files;
- bat labels present: A, B, C, D, E;
- **5 unique bat labels**.

Five filename duplicates occur across the two batches, which is consistent with bat letters being species-local identities rather than globally unique animals.

## Frozen mapping

Because the source species sample sizes are 4 and 5 and the two metadata-only CSV batches contain exactly 4 and 5 distinct bat identities, respectively, the mapping is fixed as:

- G4 = `yubi` = *Miniopterus fuliginosus*;
- G5 = `kiku` = *Rhinolophus nippon*.

This mapping uses no trajectory values, file sizes, movement geometry, speed, pulse timing or model output.

## Trial semantics

Filename token `no#` is retained as a **within-file trial label only**.

It is **not** interpreted as:
- a global chronological trial index;
- the order in which environments were encountered;
- a learning-stage variable.

No source-native cross-environment chronology has been recovered.

Therefore the present programme cannot make a literal temporal reset/relearning claim from these CSVs.

## Consequence

The authorised next programme is:

> **configuration-conditioned individual route organization**

not temporal relearning.

The key question becomes:

> does a realized route change across obstacle configurations while individual-specific organization remains detectable within a configuration and/or in configuration-invariant movement features?

## Pickle probe result

The first 8 MiB of `kiku.pkl` and `yubi.pkl` contained no whitelisted source/file/species tokens under the frozen raw-string probe.

No numerical pickle payload was decoded and no pickle was executed.
