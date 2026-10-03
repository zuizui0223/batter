# Rousettus donor-identity preflight result v1

## Status

**STOP — waypoint-sequence similarity remains unopened.**

This preflight uses only the pinned target-visitor table, source-coded manipulation labels, age metadata, and the frozen donor-support rule. It does not read `all_tree_visits_main.csv` waypoint identities or calculate any sequence similarity.

## Why this gate exists

The frozen waypoint contract requires donor histories from:
- other **naive**;
- non-pup;
- same campaign;
- same target-night roost;
- with >=3 qualifying prehistory nights.

The public source repository identifies all 14 target-tree visitors and labels four of those visitors as directly smeared/manipulated.

It does **not** publish the identities of the other manipulated bats that did not visit a target tree. Therefore the full tracked population cannot safely be treated as naive: doing so could contaminate the donor pool with manipulated non-visitors.

## Source-defined naive target visitors

After removing the four directly smeared target visitors:

| campaign | source cave/roost | naive target visitors |
|---|---|---|
| 22 Jun 2020 | Gerhsom | 6399, 6411, 6414, 6635 |
| 22 Jun 2020 | Zemer | 6428, 6641 |
| 19 Jul 2020 | UK cave | 6640 |
| 7 Dec 2020 | Gershom | 6991, 6824 |
| 7 Dec 2020 | Zemer | 6993 |

Tag 6641 is source-coded as `pup` and is excluded before independent-route analysis.

Independent known-naive counts therefore become:

| stratum | independent known-naive target visitors | possible other known-naive donors per target |
|---|---:|---:|
| 22 Jun — Gershom | **4** | **3** |
| 22 Jun — Zemer | 1 | 0 |
| 19 Jul — UK cave | 1 | 0 |
| 7 Dec — Gershom | 2 | 1 |
| 7 Dec — Zemer | 1 | 0 |

Only the four June-Gershom targets can possibly satisfy the frozen requirement of >=3 same-stratum donors using identities whose naive status is explicitly known.

The frozen experiment-level minimum is **>=5 evaluable target visitors**.

Thus even before reading waypoint sequences:

> **known-status donor support has a hard upper bound of 4 evaluable targets < 5 required.**

## Missing information

To reopen the structural gate, an independent source would need to identify the full naive/manipulated membership of the tracked experimental animals, for example:
- raw Dryad metadata containing treatment labels;
- a published supplementary individual-membership table;
- another immutable source from the original study.

The current public GitHub files do not provide that list.

The raw Dryad SQLite retrieval gate is currently blocked by the repository's download/authentication layer in both Actions and direct download attempts, so those metadata cannot presently be audited.

## Decision

**STOP_PUBLIC_SOURCE_DONOR_IDENTITY**

Do not:
- treat all unlabelled tracked bats as naive;
- infer manipulation status from absence of a target-tree visit;
- pool across roosts;
- lower the >=3 donor gate;
- lower the >=5 target-individual gate;
- include pup 6641.

No LCS, waypoint overlap, transition overlap or other route-sequence outcome is opened.

## Consequence

The external Rousettus source still provides strong biological motivation for a two-level architecture:

> social information can seed destination choice, while personal spatial memory may determine how the animal moves through the landscape.

But the currently retrievable public data are insufficient for a clean self-versus-other waypoint-reuse test under the frozen design.
