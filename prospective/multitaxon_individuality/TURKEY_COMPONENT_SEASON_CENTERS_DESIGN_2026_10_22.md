# Winter geography and component-specific GPS proximity — analysis design

**22 October 2026. Post-inspection exploratory; not a preregistration.** Already known: wild turkey 2019 contains two disconnected <=5km annual usage-center dyad graph components (11 animals/53 edges, 7 animals/20 edges). Turkey 2020 contains one 6-animal/14-edge <=5km component, and seven pairs with annual centers >5km contribute a positive source-wide winter-minus-summer L1 at <=500m. Original 2019/2020 source results, the 12-seed historical control and prior source-center summary were inspected. This plan fixes NEW component estimates and within-season geographic distances before opening their outcomes.

## Two ecological questions

1. Does the wild-turkey 2019 winter surplus of source-GPS same-day geographic nearness over preceding/following original day trajectories reproduce in **each** of the two disconnected, source-geometry-derived 5km components? Or is the source-level effect carried primarily by one component?
2. In wild turkey 2020, do pairwise **season-specific usage centers** move closer during the source-calendar winter for the five original dyads with annual usage centers >10km apart, or does the strong source-wide within-500m winter result arise without seasonal geographic convergence? The 2020 >10km five pairs and >5km seven pairs are small dependent subsets and cannot be promoted as independent biological replicates.

## Source and eligibility frozen

Re-read **exactly** original public wild-turkey Movebank DOI 10.5441/001/1.671 (2019, 2020), full original published GPS and reference files; publisher MD5, already pinned SHA256, exact animal-tag, time/position event multiset and exact original aggregate GPS seasonal L1 replay are hard prerequisites. Do not add another source if an estimate disagrees. Never output animal ID, exact date/time, GPS longitude/latitude, per-dyad position or centroid, or a geographic map locator.

Use exactly the previously verified matched pair/year sets for A->B and reversed B->A from day_shift_anchor_reverse_v1: source year 2019 112 pairs/19 animals; 2020 21 pairs/7 animals at both 15 and 30 minute tolerance. All pairs are chosen within 25km annual day-balanced original GPS utilization-center separation and >=7 matched days within >=2 calendar months in winter and summer. Winter is Jan-Feb-Dec **of one source year** (not contiguous); summer Jun-Aug. Original source G PS seasonal time tolerance 15 min primary, 30 min secondary. L1 is same-day O - average of previous/next source-day O, original GPS distance <=500m primary, 1km secondary, 2km tertiary. L1 does not imply social encounters or causality.

## Original 2019 geographically disconnected components

At <=5km annual source GPS center separation, build undirected graph of eligible fixed dyads. **Freeze expected 2019 two connected components: (11 animals,53 dyads) and (7 animals,20 dyads).** Report both **as geographically disconnected sample components, not proven independent populations**. The remaining 19th animal has no <=5km eligible edge and is not a new component with an estimable dyad score. Freeze expected 2020 component (6 animals,14 dyads) and one unmatched seventh animal.

For each of the two 2019 components, calculate original already-fixed L1 winter-minus-summer mean across its member edges for **each** original-source seed 0–11, both A/B orientations, both source time tolerances 900/1800 sec, and all 0.5/1/2km radii. Report n animals, n edges, mean/min/max of seed contrasts, positive/negative/zero seed counts. Report each component's 2019 effect on 500m and 1km as separately sample-supported descriptions, requiring >=8 fixed edges and >=3 animals. Recalculate original aggregate 25km and 5km results from the same original per-pair GPS samples and hard-fail any stored score discrepancy.

## Seasonal center test: full source versus paired-date subsets

Compute annual mean unit-sphere animal GPS location from original raw accepted source positions with equal **observed date** weights, using the existing verified source center algorithm. Then compute each animal's season centers using the same unit-sphere equal-observed-date rule but **only source GPS fixes in declared calendar month sets**:
- W = Jan-Feb-Dec (categorical winter, nonconsecutive),
- S = Jun-Jul-Aug,
- JF = Jan-Feb only,
- DEC = Dec only.

For each original eligible dyad, calculate great-circle distance between animal seasonal center unit vectors for these windows, if both animals have at least 7 observed original dates per window. Never impute missing distance as zero. For each group, report count of pairs with comparable winter/summer centers, median/mean/min/max winter distance, summer distance, and delta (winter minus summer) and fraction winter closer, distinguishing original annual-center bands <=5km, (5,10]km, (10,25]km, (5,25]km. For 2019 two <=5km disconnected components report each separately. Report JF-vs-summer and DEC-vs-summer comparisons separately as *clock/calendar-window robustness checks*. A JF or DEC group with unsupported pairs returns an explicit null/NOT_ESTIMABLE.

Secondary *paired-observation* center sensitivity: for each pair supported by original dual-anchor +/-15min day-shift GPS model, retain its previously fixed 12 seed-selected two months/season ×7 days/month ×3 exact A->B original time-matched source fixes/day. Calculate **per-dyad** winter and summer mean unit-vector original GPS centers of both animals, giving each selected date equal weight and each of the three original sampled fixes equal weight. Report 12 source-seed aggregates by group (median winter pair-center separation, median summer, fraction winter closer) at 900 and 1800s from the frozen source risk set. No exposure of any individual-specific center. This controls seasonal observation support more tightly than all-event source centers but uses different sampled dates in the two source seasons. No random sample p-values.

## Predeclared scale and small n

At <=5km, the 2019 11/53 and 7/20 components can each support an original observed L1 descriptive value. The 2020 <=5km n14 subset can also support L1. The 2020 (5,10]km n2 and (10,25]km n5 are **BELOW the earlier >=8-pair STOP**: report their distributions of original-source seasonal-center distance as source descriptive geometry, but do NOT assert statistical/general ecological replication, and do not change support threshold after the outcome.

If any component population membership cannot be checked against original source reference metadata, set population_independent=false. Both 2019 and 2020 derive from ONE published source, despite distinct animal IDs across years. No social flocks, mating, daily co-presence/encounter, habitat selection, seasonal migration mechanism, feeding or resource partitioning inferred. A winter source-center convergence is a spatial mechanism *candidate* at best: sampling geometry and year-end December heterogeneity are alternate explanations.

## Validation

Synthetic geographic-center tests: anti-meridian and unit-sphere daily balancing, unequal sampling intensity, missing winter month/true lack of dates, identical positions and unbalanced summer, disjoint components and safe no-raw-GPS output. Original source test hard-fails if years/pairs/components are different, if subset L1 aggregation does not replay previous pinned source SHA256 values within tolerance, if 12 seeds/radii/time tolerances are missing, if geodesic distance outside [0,20015] km, or if per-group per-seed support differs with distance radius. No individual GPS identifiers, original dates, coordinates, centroid vectors or per-dyad values are written to the repo or logged. Use a dedicated CI with ephemeral original full-source download and aggregate artifacts only.

**Interpretation gate:** Even if the 2019 components reproduce a winter L1 and 2020 winter source centers converge, neither is a verified independent demographic population or a causal response to winter resource conditions. This constitutes a falsifiable, spatially conditioned source-level pattern and boundary, not a universal rule.
