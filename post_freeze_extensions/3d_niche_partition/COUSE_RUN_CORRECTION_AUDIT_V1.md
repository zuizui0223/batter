# Co-use vertical runner correction audit v1

## Chronology

A historical first-output workflow completed before the final implementation audit:
- run `36953505648`
- head `e57022ae12eac8de81e6f37c3982e42f710875f4`

After that output existed, the implementation audit identified one null-simulation issue:

The old code called the phase-shift function separately for the A and B endpoint arrays. If the same individual×session×500-m-cell phase group appeared as the A member of one dyad and the B member of another, it could receive two different random circular shifts within the same permutation replicate.

The corrected implementation draws exactly one random shift per phase group per replicate and applies it consistently to every occurrence of that group.

The observed encounter set, observed separations, z values, dyad weighting, B, seeds and decision rule were unchanged.

## Historical versus corrected result

| panel | historical p | corrected p | historical excess | corrected excess | decision changed? |
|---|---:|---:|---:|---:|---|
| *Hypsignathus* | 0.9077 | 0.9045 | -1.996 m | -1.983 m | no |
| *P. hastatus* 2022 | 0.9057 | 0.9186 | -0.931 m | -0.947 m | no |
| *P. hastatus* 2023 | 0.0214 | 0.0231 | +3.605 m | +3.574 m | no |
| *P. hastatus* 2016 | 0.8595 | 0.8611 | -0.854 m | -0.854 m | no |

Observed panel statistics are exactly identical between runs.

Therefore the implementation correction changes only small Monte-Carlo/null details and leaves all four qualitative decisions unchanged.

## Reporting rule

Use the corrected workflow `36953712597` as authoritative.

Retain the historical workflow in provenance. Do not describe the corrected run as having been specified before all vertical output existed; it is an implementation correction made after the historical first output, with unchanged scientific decisions.
