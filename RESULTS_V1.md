# Result v1 — repeatability of location-conditioned vertical use

Date: 2026-09-26  
Workflow run: 36229132196  
Head: `ef7aaa17f7fe670ba3eb24dd6a25e982918e348e`  
Artifact: `batter-individual-vertical-strategy-v1` (10902326132)

## Primary result

The exact checksum-pinned Movebank source was recovered successfully. After excluding 462
source-marked manual outliers, 9,873 finite GPS events from 8 bats formed 16 tracking sessions.

The primary 5-km leave-one-session-out test was evaluable for 6 bats. For each target session,
the same bat's other session(s) were compared with an equal-individual predictor learned from
all other bats in the same supported x-y cells.

- equal-individual mean self-transfer gain: **+0.425955 nats/fix**
- positive individual means: **5/6**
- Bat3: +0.274
- Bat4: +0.842
- Bat5: +0.453
- Bat6: +0.791
- Bat7: **-0.205**
- Bat8: +0.402

Bat1 had two sessions but too little shared-cell coverage for the frozen scoring threshold.
Bat2 had only one retained session.

## Interpretation

This result is consistent with repeatable individuality in vertical flight use. It is stronger
than the earlier observation that a pooled x-y-conditioned vertical map fails to transfer among
bats: for five of six evaluable animals, knowing that the donor is the same individual improves
prediction of another session.

The exception is biologically important. Bat7 was negative in all three evaluable sessions.
The current pattern is therefore not "every bat has one fixed altitude strategy." A better
working hypothesis is that a population contains **different degrees of vertical consistency**:
some animals repeat individualized local vertical-use rules, whereas others are more flexible.

## Conditional-versus-marginal decomposition

A post-primary decomposition used the exact same scored target fixes and compared four models:
same-individual versus other-individuals, each with and without x-y conditioning.

At the 5-km primary scale:

- conditional identity gain: **+0.426 nats/fix**
- marginal-altitude identity gain: **+0.053 nats/fix**
- identity × location increment: **+0.373 nats/fix**
- positive individual identity × location increments: **5/6**

The marginal result is positive for only 2/6 evaluable bats, whereas the location-conditioned
identity increment is positive for 5/6. Thus the primary signal is not well described as
"individual A flies high and individual B flies low." It is predominantly **individualized
coupling between horizontal place and vertical state**.

Descriptively, the current bats also hint at multiple strategy types:

- Bat3/Bat4/Bat5: strong local-routing individuality despite non-positive marginal-altitude identity;
- Bat6: strong marginal-altitude individuality, with little added benefit from identity-specific location coupling;
- Bat8: moderate marginal-altitude individuality plus a small location-specific increment;
- Bat7: neither predictor gives a positive identity advantage at 5 km, consistent with a more flexible/context-driven individual.

These labels are exploratory descriptions, not latent classes.

## Spatial-scale robustness

Post-primary checks inherited the already-used ODSP scale/bin family; they cannot redefine the
primary endpoint.

| Configuration | Evaluable bats | Mean gain | Positive bats |
|---|---:|---:|---:|
| 2.5-km cells | 5 | +0.8588 | 4/5 |
| **5-km primary** | **6** | **+0.4260** | **5/6** |
| 10-km cells | 7 | -0.0334 | 5/7 |
| fine z bins | 6 | +0.4259 | 5/6 |
| coarse z bins | 6 | +0.4259 | 5/6 |
| source outliers retained | 6 | +0.3638 | 5/6 |

The z-bin result is very stable, whereas horizontal scale matters strongly. The self-transfer
signal is strongest at fine-to-intermediate spatial resolution and disappears in the 10-km mean.

This favors a **local vertical-routing** hypothesis over a simple individual-wide altitude
set-point: individuality may reside in how bats couple altitude to particular parts of the
landscape.

## What is not established yet

- Height is GPS height above mean sea level, not height above ground.
- GPS tracks are not yet classified into foraging versus commuting/other flight.
- Wind, topography and orographic uplift are not yet conditioned on.
- Only eight animals are available, with one to three sessions each.
- The 30-s fixes are not treated as independent biological replicates.

Therefore the current claim is **repeatable individual vertical flight-use organization**, not
yet individual specialization in foraging altitude.

## Next mechanism test

The next high-value analysis is an individual reaction-norm model:

`vertical state ~ uplift/topography + night conditions + (1 + uplift | individual)`

using terrain-relative height where reproducibly available. If individual random slopes are
repeatable, the ecological story becomes: bats share a nocturnal energy landscape but differ in
how they exploit it. If the random slopes collapse after weather/topography are included, the
current individuality is better explained by context-specific routes rather than intrinsic
strategy.
