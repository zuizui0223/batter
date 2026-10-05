# Bivariate field-policy to vertical-shape localization diagnostic v1

## Status

**POST-OUTCOME MECHANISM DIAGNOSTIC. CANNOT REOPEN THE FROZEN FIELD BRIDGE OR MODIFY JAE.**

Frozen after:
- fixed-bin 360-s bivariate (horizontal, vertical) policy persistence was supported in P. hastatus 2022 and 2023;
- the one-dimensional FlightIntensity-to-vertical-shape boundary diagnostic was unsupported.

No bivariate policy-to-shape result has yet been calculated.

## Question

Was the failed policy-to-vertical-shape bridge caused by projecting a genuinely two-dimensional movement policy onto the scalar FlightIntensity axis?

## Panels

Analyse separately:
- P. hastatus 2022;
- P. hastatus 2023.

No cross-year pooling is a confirmatory claim.

## Policy coordinate

Use exactly the supported fixed-bin bivariate policy:

H = mean(z median horizontal speed, z p90 horizontal speed)

V = mean(z median absolute vertical speed, z p90 absolute vertical speed)

with the same cohort standardization and 360-s fixed-bin session eligibility as the frozen bivariate carrier diagnostic.

For target vertical-shape session t of individual i:

- focal policy history theta_i,-t = equal-session mean (H,V) over i's other fixed-bin-valid sessions;
- donor policy theta_j = equal-session mean (H,V) over donor j's fixed-bin-valid sessions;
- require >=2 donor individuals.

Distance:
Euclidean distance in the 2-D (H,V) policy space.

## Vertical-shape target

Use exactly the centered vertical-distribution estimator already frozen in
WILD_POLICY_TO_VERTICAL_SHAPE_ESTIMATOR_APPENDIX_V1.md:

- same centered height bins;
- same 5-km horizontal cells;
- same alpha=0.5;
- same minimum scored fixes;
- same donor vertical log-score gain G_tj.

For each target:
- identify policy-nearest donor(s) in 2D;
- C_t = mean G_nonnearest - mean G_nearest.

Positive C means the donor nearest in persistent 2D movement policy has a more similar held-out vertical-shape distribution.

Aggregate:
- equal targets within individual;
- equal individuals within year.

## Null

Within each frozen cohort independently:
- permute complete biological identities assigned to the 2-D policy histories;
- preserve policy vectors, cohort membership and support;
- vertical target/focal/donor identities remain fixed.

9,999 permutations.

Seeds:
- 2022: 202610051471
- 2023: 202610051472

## Interpretation

### Supported in both years

Evidence that persistent low-dimensional movement policy organizes vertical-shape similarity, while scalar FlightIntensity was an inadequate projection.

### Unsupported in both years

Strong evidence that the persistent movement-policy carrier and persistent vertical-shape individuality are distinct layers of organization.

### Mixed

Relationship is context dependent; no general mechanism bridge.

## Hard ceiling

This post-outcome diagnostic:
- cannot reopen the frozen JAE field bridge;
- cannot establish causal mediation;
- cannot alter original PASS/FAIL classifications;
- cannot claim generality outside P. hastatus.
