# Strategy-maintenance mechanism preflight v1

## Status

POST-OUTCOME MECHANISM PREFLIGHT. No new environmental or vertical outcome may be opened until the structural/source gate below is complete.

The established observations motivating this preflight are:
- centered vertical individuality persists within broad movement-intensity states;
- it persists at 500-m place × speed × turning state in four structurally evaluable fruit-bat panels;
- simple resource-patch fidelity does not provide a general cross-panel explanation;
- it persists across >=1-day self-history in four panels;
- same-individual history outpredicts contemporaneous other individuals under 2-km place × kinematic matching in three of four evaluable panels;
- terrain-relative individuality need not imply positive vertical segregation or synchronous avoidance.

These results motivate a maintenance question rather than another existence test.

## Biological question

Why does an individual repeatedly return to a characteristic vertical solution?

We distinguish two maintenance architectures.

### H1 — strategy constancy / learned solution reuse

Individuals retain a relatively stable vertical solution across changing environmental contexts. Environmental change shifts the population response, but knowing an individual's previous vertical solution predicts its later solution beyond current environment.

Prediction: cross-context self-history remains predictive after environment matching, while individual-specific environmental slopes add little.

### H2 — individual environmental reaction norm

The maintained object is not a fixed height distribution but an individual-specific mapping from environmental conditions to vertical movement.

Prediction: held-out vertical use is better predicted by the individual's own environmental response estimated on other sessions than by (a) a population environmental response or (b) other individuals' response functions.

These hypotheses are not mutually exclusive.

## Source gate before outcome

For each of the four terrain-evaluable fruit-bat panels, inventory only metadata/source fields and externally joinable coordinates/timestamps before opening any new vertical response.

Candidate environmental families, in fixed priority order:
1. wind vector / wind speed;
2. boundary-layer or vertical-motion proxy if available at defensible resolution;
3. temperature;
4. precipitation;
5. radiation/cloud proxy.

A candidate family is admissible only if its provenance and temporal/spatial resolution are common enough to be defined identically across at least three of four panels. Do not select a variable because its vertical association is strongest.

## Identifiability gate

Before opening vertical outcomes, environmental values may be inspected only to assess support.

A panel is evaluable only if:
- >=5 repeat individuals;
- >=2 eligible sessions per individual;
- >=5 individuals have within-individual environmental span covering at least 40% of the panel's central 90% environmental range;
- at least 50% of target observations lie within environmental support represented by both self-history and >=2 other individuals;
- no single calendar night contributes >50% of the matched evaluation support.

At least three panels must pass for a cross-panel maintenance claim. Otherwise stop at feasibility/identifiability.

## Frozen primary comparison if gate passes

Use the already-established terrain-relative, session-centered vertical representation and 500-m horizontal place × broad kinematic-state matching.

For each held-out target session compare:
A. population environment model;
B. same-individual history with no individual × environment slope;
C. same-individual reaction-norm model estimated from other sessions.

Primary maintenance contrast:
C versus B, calibrated by whole-session individual-label permutation within panel/cohort while preserving environmental values and complete session blocks.

Secondary contrast:
B versus A.

Interpretation:
- C > B: evidence that an individual-specific environmental response contributes to maintenance;
- B > A but C not > B: stable solution reuse is more consistent with the data than a measurable individual reaction norm;
- neither: current environmental representation absorbs the prior identity signal or the mechanism is unresolved.

## Claim ceiling

Even a positive reaction-norm result does not establish adaptation, optimality, genetic determination, personality or learning. A constancy result does not prove memory. The strongest allowed language is that maintenance is statistically localized to stable self-history and/or repeatable individual environmental response.

## Stop rule

Do not:
- lower support gates after seeing vertical outcomes;
- switch environmental family after opening a failed primary outcome;
- search many weather variables for the best interaction;
- rescue failed panels by changing 500-m place or kinematic definitions;
- interpret a failed reaction norm as proof of learned memory.


## External environment source decision

The source-schema audit found no environmental field common to the four target GPS tables. Hypsignathus alone contains `eobs:temperature`; it is not eligible as a cross-panel primary predictor.

Therefore the external source is fixed before environmental numeric support is inspected:

- dataset: Copernicus/ECMWF ERA5 hourly single-level reanalysis;
- primary environmental family: horizontal wind;
- variables: 10-m u and v wind components, combined as wind speed and direction relative to movement where movement bearing is available;
- temporal resolution: hourly;
- horizontal resolution: 0.25 degree;
- join: nearest ERA5 grid point and nearest hour to each GPS timestamp;
- secondary preflight-only covariates retained for possible later contracts, not substitutes for failed wind: 2-m temperature and boundary-layer height.

ERA5 pressure-level vertical velocity is not promoted ahead of horizontal wind because the currently available time-series product is 6-hourly and coarse relative to the movement records. It may not rescue a failed wind primary.

The external join is intended to represent broad atmospheric context, not tree-scale or canopy-scale microclimate.


## Frozen implementation details for wind-support preflight

To avoid ambiguity before any ERA5 wind values are inspected:

- Public ERA5 mirror: Earthmover Icechunk ERA5 on anonymous AWS S3, bucket `earthmover-icechunk-era5`, prefix `icechunkV2`, branch `main`.
- Group: `single/temporal`, chosen because it is time-series optimized while holding values identical to the spatial layout.
- Variables: `u10` and `v10` only for the primary support gate.
- ERA5 coordinate matching: nearest 0.25-degree grid point and nearest hourly valid time.
- Movement universe: the exact x-y-time-derived 500-m place x frozen speed2_turn2 kinematic endpoint universe used by the completed 500-m stress test; no numeric height is parsed for the support preflight.
- A target session enters the environmental support calculation only if it retains >=50 endpoints whose 500-m place x kinematic stratum occurs in both (i) another session of the same individual and (ii) at least one other individual in the same cohort, matching the existing 500-m x-y-time support logic.
- Panel and individual wind ranges use the 5th to 95th percentiles of wind speed, sqrt(u10^2 + v10^2).
- Individual span fraction = individual q95-q05 divided by panel q95-q05.
- For each target session, self-history environmental support is the q05-q95 wind interval from the same individual's other eligible sessions.
- Other-individual support is counted individual-by-individual using each donor individual's q05-q95 interval. A target endpoint is environmentally matched only when its wind speed lies within self-history support and within the support interval of at least two other individuals from the same cohort.
- matched_target_fraction = matched endpoints / x-y-time-supported target endpoints, pooled with sessions equally weighted within individual and individuals equally weighted for the panel gate.
- calendar-night concentration is calculated on environmentally matched target endpoints; no single shifted calendar night may contribute >50% of the panel's matched endpoints.
- The expected x-y-time evaluable individual counts before ERA5 opening are inherited from the completed 500-m stress test: Hypsignathus 19, P. hastatus 2022 23, 2023 11, and 2016 9. Any mismatch invalidates the preflight rather than triggering retuning.


## Frozen reaction-norm outcome architecture after wind identifiability PASS

The wind identifiability gate passed in exactly three panels (Hypsignathus, P. hastatus 2022, P. hastatus 2023). P. hastatus 2016 is stopped and cannot be rescued.

Before any numeric vertical outcome is opened, the predictive comparison is fixed as follows.

### Wind state

Within each admitted cohort, classify ERA5 wind speed into exactly two states using the cohort median calculated from the x-y-time-supported 500-m place x speed2_turn2 endpoint universe. No alternative threshold or additional wind bins are opened.

### Structural support gate

For a target event, all three predictors must be structurally available:
- A: other-individual wind-conditioned profile at the same 500-m cell x kinematic state x wind state;
- B: same-individual unconditioned profile at the same 500-m cell x kinematic state, learned from other sessions;
- C: same-individual wind-conditioned profile at the same 500-m cell x kinematic state x wind state, learned from other sessions.

A target session requires >=50 events with all three predictors available. A panel must retain at least max(5, ceil(0.70 x completed 500-m baseline n)):
- Hypsignathus >=14 of 19;
- P. hastatus 2022 >=17 of 23;
- P. hastatus 2023 >=8 of 11.

All three panels must pass this x-y-time + wind structural gate before any numeric vertical response is opened. Failure stops the reaction-norm outcome family.

### Vertical representation

If the gate passes:
- use the same pinned SRTM/DEM source and bilinear interpolation as the completed terrain-relative 3-D diagnostic;
- terrain-relative height = native source height - DEM elevation;
- center terrain-relative height by subtracting the median of its complete retained session;
- fixed residual-height bins: -inf, -400, -200, -100, -50, 0, 50, 100, 200, 400, +inf m;
- Jeffreys alpha = 0.5.

### Predictors and scoring

For every held-out target session:
- A = P_other(z | 500-m cell, kinematic state, wind state), equal-weighted across other individuals;
- B = P_self(z | 500-m cell, kinematic state), equal-weighted across the focal individual's other sessions;
- C = P_self(z | 500-m cell, kinematic state, wind state), equal-weighted across the focal individual's other sessions.

All models are scored on the identical target events admitted by the structural gate.

Primary statistic:
- G_RN = mean log P_C(z) - log P_B(z), averaged events -> target session -> individual equally.

Secondary statistic:
- G_SELF = mean log P_B(z) - log P_A(z), with the same averaging.

### Calibration

Whole retained session blocks are permuted among individual labels within cohort, preserving:
- x-y-time trajectory;
- ERA5 wind values and wind state;
- terrain-relative centered vertical observations;
- exact session sizes;
- the original multiset of session counts assigned to individual labels.

B = 4,999 per panel.
Seeds:
- Hypsignathus: 2026100301
- P. hastatus 2022: 2026100302
- P. hastatus 2023: 2026100303

Support for repeatable individual wind response requires:
- G_RN - mean(null_RN) > 0; and
- one-sided p(null_RN >= observed G_RN) <= 0.05.

Support for stable self-history beyond population wind response requires the analogous rule for G_SELF.

### Interpretation matrix

- RN supported: repeatable individual-specific wind response contributes to maintenance.
- RN not supported, SELF supported: current data favor stable self-history/solution reuse over a measurable individual wind reaction norm; do not call this proof of memory.
- both supported: stable individual history and individual-specific wind response both contribute.
- neither supported: maintenance mechanism remains unresolved at the tested atmospheric scale.

Cross-panel wording:
- RN in 3/3 = replicated wind reaction-norm maintenance;
- RN in 2/3 = recurrent but context-dependent wind reaction norms;
- RN in 1/3 = panel-specific wind response only;
- RN in 0/3 with SELF in >=2/3 = evidence favors stable solution reuse over the tested broad wind reaction norm.

No other environmental variable may replace wind in this family after the outcome is opened.


### Permutation validity detail

A permutation replicate is valid only when the complete rescored pipeline retains at least five evaluable permuted individual labels in the panel. Invalid replicates are reported and excluded from the empirical null. No minimum beyond the already-frozen 50 supported target events per session is introduced after vertical opening.
