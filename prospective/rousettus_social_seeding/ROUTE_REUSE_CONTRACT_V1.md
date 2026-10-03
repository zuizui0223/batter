# Social-seeding → personal-route-reuse contract v1

## Status

PROSPECTIVE EXTERNAL MECHANISM TEST.

This contract is frozen before any raw ATLAS route geometry from Dryad DOI `10.5061/dryad.51c59zwgp` is opened for this analysis.

This test is outside JAE v0.4.0 and may not modify its frozen manuscript or claim.

## Biological question

The source experiment already establishes that roost-level social information can increase discovery of spatially predictable target trees without requiring following.

The new question is:

> After social information changes **where a naive bat goes**, is **how it gets there** better predicted by that bat's own pre-manipulation movement corridor than by conspecific corridors?

This directly tests a two-level distributed-airway model:

1. **social seeding** provides destination/resource information;
2. **personal route reuse** supplies the spatial solution used to reach that destination.

## Primary population

Use **naive bats only** from the peer-reviewed experimental population.

Source-defined target-event set:
- first post-manipulation visit to either focal *Ficus sycomorus* tree;
- 1–6 nights after the corresponding campaign manipulation;
- source-defined naive visitor identity.

Frozen naive visitor IDs:
`6399, 6411, 6414, 6635, 6428, 6641, 6640, 6991, 6824, 6993`.

Exclude tag **6641** before route analysis because source metadata code it as `pup` and source analysis warns pups may be carried by mothers.

Thus the maximum candidate set before raw support filtering is **9 independent naive visitors**.

Manipulated / directly smeared bats are excluded from the primary route-reuse test.

## Raw source and schema gate

Raw geometry may be read only from the pinned Dryad SQLite files in `EXTERNAL_SOURCE_RECEIPT_V1.md`.

Before opening route geometry:
1. verify file identity / current Dryad file ID;
2. inspect SQLite schema only;
3. identify tag ID, timestamp and x-y coordinate fields;
4. verify coordinate CRS / metric interpretation;
5. reproduce presence of the source-defined campaign dates and candidate tags;
6. do not calculate route similarity, route overlap or any self-versus-other distance.

If coordinate semantics cannot be established reproducibly, STOP.

## Route definition

For each qualifying naive visitor, define the target route as the **first inbound approach** to its first source-defined focal-tree visit after manipulation.

The target-tree coordinate is taken from the source tree-location data and fixed by the visited target identity.

Route geometry is restricted to the target-centred annulus:

- outer radius: **2,000 m**
- inner exclusion radius: **500 m**

Use fixes from first entry into the 2-km radius until first entry into the 500-m radius.

Rationale fixed before outcome:
- the inner 500 m is dominated by the novel final approach to the socially seeded target itself;
- beyond 2 km, the segment increasingly mixes unrelated whole-night movement;
- these scales are fixed independently of this outcome and correspond to the fine-place scales already used in the broader batter programme.

No alternative annulus may rescue a failed result.

## Sampling standardization

ATLAS sampling varies approximately from 0.125–0.5 Hz.

Before geometry:
- sort fixes by timestamp;
- retain the first valid fix in each **30-s** bin;
- do this identically for target routes and history routes;
- no interpolation between missing fixes.

This prevents high-frequency periods from dominating route distance.

## Self-history library

For each target visitor:

- use only its own tracking **before the campaign manipulation timestamp**;
- source article states naive animals were tracked for more than two weeks before manipulation; raw support must be reproduced;
- retain 30-s-standardized fixes in the same target-centred 500–2,000 m annulus;
- organize history by complete shifted calendar night;
- target campaign night and all post-manipulation data are excluded from self history.

## Other-history library

Use other naive bats from the same **roost × campaign**.

For each donor:
- use only pre-manipulation data;
- use the identical target-centred annulus and 30-s sampling;
- retain complete-night identity.

Donor weighting is equal biological individual, not equal fix.

## Outcome-blind structural support gate

Before any self-versus-other route distance is calculated, a target visitor is evaluable only if:

- independent non-pup identity;
- target inbound annulus segment contains >=10 standardized fixes;
- own pre-manipulation history has >=3 distinct nights with >=5 standardized annulus fixes each;
- >=3 other naive non-pup individuals in the same roost × campaign each have >=1 pre-manipulation night with >=5 annulus fixes.

The analysis opens only if **>=5 independent naive target visitors** pass all support criteria.

If fewer than five pass: STOP. Do not relax radius, sampling interval, nights, fix thresholds or donor count.

## Primary route-reuse statistic

For one target fix q and one pre-manipulation history night h:

`d(q,h) = minimum Euclidean distance from q to any standardized fix in h`.

For the focal bat:
- calculate d(q,h) for each eligible own-history night;
- average equally across own-history nights to obtain `d_self(q)`.

For one donor individual:
- calculate the same equal-night mean for that donor;
- then average equally across eligible donor individuals to obtain `d_other(q)`.

Per target route:

`R_route = mean_q [ d_other(q) - d_self(q) ]`.

Positive R_route means the socially seeded target approach lies closer to the bat's own established pre-manipulation corridor than to conspecific history.

Aggregate:
- equal standardized fix within route;
- one first target route per biological individual;
- equal individual for the experiment-level statistic.

Primary experiment statistic:
`R = equal-individual mean R_route` in metres.

## Primary calibration

Whole-history identity permutation within exact **roost × campaign**.

For each permutation:
- keep each target route, target identity, target tree and manipulation campaign fixed;
- keep every pre-manipulation individual's complete set of history nights intact;
- permute complete prehistory libraries among naive non-pup identities within roost × campaign;
- recompute self and other libraries and the complete R statistic.

Use **9,999 permutations**.

Fixed seed:
`20261003071`.

Support for personal route reuse requires:
- observed R - mean(null R) > 0;
- one-sided p(null >= observed R) <= 0.05.

## Secondary comparison: contemporaneous traffic

Only if the primary support gate passes, predeclared secondary:

Compare the target route with same-night routes of other tracked naive bats from the same roost × campaign, using the identical 500–2,000 m annulus and 30-s sampling.

This asks whether own pre-manipulation corridor predicts the approach better than contemporaneous traffic.

It is secondary because the source paper already found little evidence for following, and because same-night availability can be sparse.

Failure or ineligibility of this secondary test cannot alter the primary result.

## Descriptive stratification

Report, without changing the primary analysis:
- roost;
- campaign;
- nights after manipulation;
- age class when available;
- sex when available.

Do not create age-specific inferential subgroups after route results are opened.

## Claim interpretation

If primary R is supported:

> Following a socially seeded destination change, naive bats approach the new target along paths closer to their own established movement corridors than to conspecific corridors.

This supports **social seeding + personal route reuse** as a distributed navigation architecture.

If R is unsupported:
- do not infer route copying;
- do not infer absence of spatial memory;
- the target may require a genuinely novel corridor or the chosen annulus may contain little reusable history.

## Stop rules

After raw route outcome is opened:
- no alternate radii;
- no alternate downsampling interval;
- no DTW / Fréchet / KDE / kernel-overlap rescue;
- no target-visitor subset rescue;
- no manipulated-bat rescue;
- no inclusion of explicitly coded pups;
- no switching to the tree-sequence endpoint as a substitute primary.

If raw Dryad tracking cannot be retrieved or schema-validated, preserve this as **pending-data preregistration** and stop.

## JAE firewall

No result from this external test may be used to modify or rescue JAE v0.4.0.
