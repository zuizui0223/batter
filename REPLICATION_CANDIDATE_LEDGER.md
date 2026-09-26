# Independent replication candidate ledger

Date: 2026-09-26

Candidate selection is based on source structure before numeric vertical outcomes are inspected.

## *Eidolon helvum* — admitted and completed

Repository DOI: `10.5441/001/1.k8n02jn8`

Structural preflight before numeric height open:

- 18,154 GPS rows;
- 63 individuals with x-y and native-height presence;
- 42 individuals with at least two >=50-fix sessions;
- native height: `height_above_ellipsoid`.

The candidate passed the frozen structural gate and was selected for independent replication.
The subsequent prospective replication was supported (20 evaluable individuals; 17/20 positive).

## *Tadarida brasiliensis* — structurally excluded

Repository DOI: `10.5441/001/1.td71sn54`

Outcome-blind repository/CSV preflight found:

- 564 GPS rows;
- 7 reference animals;
- GPS columns include time, x-y, individual identity and source outlier flags;
- **no native height field** among `height_above_msl`, `height_above_ellipsoid` or
  `height_raw`;
- numeric height values were never parsed.

Therefore this archive cannot test the vertical-specialization hypothesis and fails before any
biological outcome is available.

## Current expansion rule

Additional datasets may enter the comparative panel only if they have:

1. public checksum-pinnable GPS/event data;
2. a native vertical coordinate on the same event as x-y and time;
3. >=8 individuals with x-y-height presence;
4. >=5 individuals with at least two >=50-fix sessions;
5. enough within-context replication to prevent site/year identity from masquerading as
   individual identity.

No candidate is selected because its vertical outcome is favorable.
