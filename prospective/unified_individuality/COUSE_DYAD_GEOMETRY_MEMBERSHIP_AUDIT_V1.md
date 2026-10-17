# How much of the original co-use analysis is represented among geometry-eligible bats?

**Date: 17 October 2026.** Original-source-derived **support composition audit**, not a new biological test, original GPS/DEM rerun, estimate of interaction or statistical subgroup test.

## Question and independently verified support

The prior exact cohort/ID crosswalk showed that the original joint V/S 3D geometry and co-use I analyses share **5/3/5/5 panel-qualified bats** despite different full eligible cohorts. To assess what that means for a possible *future* linked bat-level design, we inspected the original co-use **dyad memberships** and existing matched-event counts from the four original successful result artifacts. Each original co-use dyad is categorized by whether **both**, **exactly one**, or **neither** of its original bat IDs occurs in that panel's V/S-eligible geometry source set.

| Original panel | All source co-use dyads | Both V/S bats | Exactly one V/S bat | Neither V/S bat | Events in both-eligible dyads / all original matched events |
|---|---:|---:|---:|---:|---:|
| *Hypsignathus monstrosus* | 22 | **9** | 11 | 2 | 592 / 883 |
| *Phyllostomus hastatus* 2022 | 10 | **3** | 6 | 1 | 284 / 347 |
| *P. hastatus* 2023 | 8 | **5** | 3 | 0 | 650 / 679 |
| *P. hastatus* 2016 | 8 | **8** | 0 | 0 | 16,096 / 16,096 |
| **Total (4 panel-specific original designs)** | **48** | **25** | **20** | **3** | **17,622 / 18,005** |

All figures were checked against the **actual original archived co-use dyad JSON** and **native/terrain joint-geometry eligible individual-ID sets**, with the same exact source collection-cohort-plus-ID keys as the previous audit. The complete co-use original 16 ZIP source hash inventory remains unchanged. Original matched-event counts are repeated observations of the same animals/dyads, **not independent bat replicates**. The 2016 source itself contributes **16,096 of the 18,005** matching events and uses a 600-second, endpoint-excluded window, while 2023 uses 600-second *all-space* and the first two panels use 60-second endpoint-excluded windows. These encounter definitions are not exchangeable by pooling.

## The nontrivial outcome is extreme heterogeneity of dyad support

- **2016:** The original five co-use-eligible bats are all in the nine-bat geometry-eligible set, so **every** one of its eight original co-use dyads involves two geometry bats. This is the strongest **membership** basis for a future same-individual association, but it does not mean a statistically robust association already exists.
- **2023:** Original geometry and co-use both contain six bats but share **five**, and **five of eight** existing co-use dyads use two geometry bats. Those five dyads account for **650 of 679** original matched events. Their unequal encounter weights and reused individual partners must not be turned into 650 independent comparisons.
- **2022:** Only **three of ten** co-use dyads involve two geometry bats. Recalculating a panel I statistic from only these selected dyads would change the original sample and require a separately frozen null; the original source p=0.9186 is *not* a valid restricted-subset p-value.
- ***Hypsignathus*:** **9/22** dyads involve two geometry bats, while 11 have one such bat and two have neither. Any bat-level comparison would have a structured dyad network rather than 22 independent bat observations.

The original co-use summary does **not** retain a ready-made per-animal *co-use effect* with its own calibrated null, and an individual belongs to more than one dyad. The existing dyad-level **observed median centered-deviation mismatch** alone is not a dyad-specific observed-minus-phase-shift-null effect. Therefore membership/event support does **not** license computing an ecological V–I correlation or significance by treating dyad medians as independent responses or by borrowing original full-panel p-values.

## Publication claim boundary

**Safe:** "The original co-use assay comprised 48 retained dyads across four heterogeneous panels; 25 dyads connected bats both eligible for the separate 500-m joint V/S geometry analysis. These source results have verified partly overlapping individual memberships, but no jointly calibrated individual-level fidelity–co-use relationship has been estimated."

**Unsafe:** "Co-use effects were absent in the same specialist bats", "17,622 encounters support no avoidance", "2023’s positive I is attributable to the overlapping five bats", or "the 2016 source allows a direct mechanism test with the already-reported I p-value." Source co-use I continues to measure **session-centered relative-height deviation differences**, not physically calibrated altitude gap.

## Reproducibility and privacy

[Machine-readable source-only aggregate support ledger](figures/FROZEN_SHARED_GEOMETRY_COUSE_DYAD_SUPPORT_V1.json) stores each original panel's dyad/event counts by geometry-membership class, original artifact IDs and the exact Git SHA of the source crosswalk. The [independent cross-estimand verifier](validate_cross_estimand_eligibility_v1.py) checks the aggregate figures and original source hashes in routine CI; its optional **authorized-local-original-ZIP** mode rehashes all 16 original artifacts and independently recalculates every dyad membership class/event count without publishing ID labels or dyad records. We directly verified the local original ZIPs before generating the ledger.

Original source ID-bearing ZIPs have current GitHub expiration dates in **December 2026**. The public integration stores no original animal-ID values, dyad partner names, coordinates or source ZIP archives. Preserving their full future auditability requires the data owners' permission to retain appropriate original data or a sanctioned repository copy; the public hash and aggregate alone cannot regenerate original IDs after expiration.

**Human editorial decision:** This supports a precise **feasibility and inference ceiling**, not a new biological result. The strongest original wild claim remains the centered individual-height predictor; source V and S are algebraically coupled, and I is a different co-use measure, with only partially shared bat samples and no linked per-individual causal test.
