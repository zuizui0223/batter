# Resource × behavior SDM: paired conditional prediction contract v1

2026-11-20. Prospective statistical design and runnable source-free tests. No empirical resource-conditioned bat distribution model has been fitted.

## Biological contrast

Test whether independently measured resource opportunity predicts a bat's behavior/time/height *within the same horizontal region* beyond abiotic and generic food opportunity. A 2-D null does not imply a higher-dimensional benefit. A positive individual-height distribution also does not imply spatial partitioning or fruit use.

## Two independent model ladders

- Horizontal R0/R1/R3/RN1: abiotic; generic plants; source-linked partners; degree-preserving rewiring. Keep original esdm 84 source-fold roster, 36 strictly qualified prefit candidates, all STOPs and withheld source/publication embargo. This ladder has NOT yet passed ecological M3–M1/N1.
- Conditional B0/B1/B2/B3: height given individual/XY/time; add verified behavior state; add resource-conditioned behavior and height; then evaluate residual individual effects. Compare on identical heldout biological sessions. State labels cannot be estimated from the same heldout height target.
- Observation O: detector/GBIF recording probability is a separate factor; no absence is inferred from no detection. Botanical source-rank AUC cannot substitute for measured fruit supply.

## Runnable paired conditional scorer

conditional_scoring.py scores three targets: (1) height conditional on individual, place and time, marginalizing unknown activity; (2) jointly independently annotated behavior and height at the same place/time; (3) height conditional on independently annotated behavior. Comparisons re-use precisely the *same* heldout event vector and a fully normalized 5-D probability distribution. A zero-support event on either side yields STOP_UNMATCHED_HELDOUT_SUPPORT rather than favorable post-hoc intersection.

Toy known-truth tests demonstrate the *possibility* of a positive conditional height score with completely unchanged horizontal occupancy. Other fixtures prove the sign can reverse and that state-mixture identity is not identical to within-state identity. These are software validity tests, not new biological statistics.

## Nonnegotiable empirical joins

1. Link exact species, individual sessions, source country/region, and observation interval. NeoBat primary fruit-guild occurrences and batter GPS cohorts currently lack a matched study-level join. Phyllostomus hastatus is secondary/omnivorous, not proof of direct compatibility.
2. Measure local fruit or prey abundance/phenology independently within the tracked animal's accessible space and recorded time window. Country-level GBIF co-recording within 25-km cells and climatological plant scores are NOT measured local feeding opportunity.
3. Independently calibrate sensor altitude/terrain reference and identify forage/commute/other behavior without using the heldout height outcome as a label.
4. Reserve whole source-publications and source datasets outside both bat and plant training for the chosen heldout region. Freeze source-fold and spatial/temporal support before outcomes. Keep the same bat background/effort and regularization for actual partner vs rewired null.
5. Report whole-individual, source-population and geographic-block effects; GPS fixes are not independent replicates. A new animal without a learned individual policy is a separate cold-start STOP and must not be scored using a fictitious personal identity.

## Current admission

| Component | Status |
|---|---|
| Positive source-link recurrence | 46.94% vs 40.55%; source-internal only |
| Botanical GBIF record ranking | +0.02539 country-equal AUC; observation process only |
| Qualified inputs | 35 source-disjoint plants; 36/84 bat-country prefit candidates |
| Shadow linked-fruit identity | S3−S1 −0.00569; S3−SN1 −0.00800; not a general gain |
| Wild bat centered height and vertical individual fidelity | within-source positive, cannot infer food mechanism |
| Joint resource × behavior × 3D field validation | STOP_UNMATCHED_RESOURCE_BEHAVIOR_SOURCE |
| Ecological M3−M1/N1 and general 5-D SDM gain | NOT ESTIMATED |

Source crosswalk: esdm PRs #244, #259, #266, #268; batter PR #99; boids EVIDENCE_AND_PREDICTION. Frozen JAE/BE release files are untouched.
