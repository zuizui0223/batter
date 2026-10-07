# Collective-versus-personal 3D predictive decomposition v1

## Question

Existing results show that the same bat reuses a characteristic 3D configuration. This analysis asks whether that repeatability has two nested components:

1. a **shared group template** that can be recovered from other individuals;
2. a **personal refinement** that is carried only by the focal individual's own past.

A separate strict lane asks whether a pooled 3D configuration persists across nights whose tracked memberships do not overlap at all.

## Lane A — strict collective persistence

Only the two panels that passed the structural gate are opened:

- *Phyllostomus hastatus* 2022: 53 zero-identity-overlap night pairs, 19 unique nights;
- *P. hastatus* 2016: 16 pairs, 8 nights.

For each night, individual session distributions are centered by their own session median and pooled with equal biological-individual weight. The primary endpoint is conditional vertical overlap inside shared 500-m cells.

The null independently scrambles the mapping between horizontal cell and complete vertical profile within every individual-night. It preserves tracked membership, horizontal occupancy and the session's collection of local vertical profiles.

## Lane B — past-to-future decomposition

Only panels that passed the prospective structural gate are opened:

- *Hypsignathus monstrosus*: 71 target sessions / 17 individuals;
- *P. hastatus* 2022: 66 / 18;
- *P. hastatus* 2023: 8 / 6.

Every target is predicted only from sessions at least three days in its past.

For the same target fixes:

`shared group gain = log P(other-individual conditional) - log P(other-individual marginal)`

`personal increment = log P(self conditional) - log P(other-individual conditional)`

Therefore:

`total personal-history gain = shared group gain + personal increment`.

This makes the ecological alternatives explicit:

- shared + personal: a common spatial template exists, and individuals refine it;
- shared only: individual apparent repeatability is mostly a common template;
- personal only: predictability is carried mainly by individual history;
- neither: the archive does not support either predictive component.

## Claim ceiling

Even the strict turnover result cannot identify social or cognitive memory from tracking alone. A persistent resource/terrain configuration could regenerate the same collective 3D shape. The word **memory** is reserved for the biological hypothesis; the directly tested quantities are collective spatial persistence and cross-individual predictive information.
