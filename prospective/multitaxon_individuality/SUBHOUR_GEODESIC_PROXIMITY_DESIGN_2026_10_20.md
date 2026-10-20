# Freeze before output: grid-free sub-hour geodesic proximity among matched GPS fixes

**Post-inspection exploratory sensitivity (20 Oct 2026).** The earlier
seasonal geographic X, 1-km grid clock-bin D and sub-hour timestamp
eligibility outputs HAVE BEEN INSPECTED. This is not independent
preregistration. Fix every new proximity threshold and control
before opening new geodesic-distance outcome values.

## Empirical question
Does the winter excess of **1-km source-clock-bin time-label alignment**
seen in the white-tailed deer source survive an **origin-independent
great-circle distance metric** and truly closer GPS timestamps?
Do not equate a GPS proximity proxy to direct animal interactions or
social association. Specifically distinguish an observed nearby-position
fraction from a null expected nearby fraction based on the *same daily
measured fixes but reassigned which matched times belong together*.

## Sources and source-data acceptance
Exactly the three prior original published and checksum-pinned
Movebank sources: wild turkey 10.5441/001/1.671, American black
bear 10.5441/001/1.706, white-tailed deer 10.5441/001/1.718.
Years 2019 and 2020, including black bear 2019 as an explicit STOP.

Complete original GPS/reference files, reference animal-tag join,
sensor=GPS, explicit visibility, outlier policy, native timestamps
and positional event QC must pass *publisher MD5, previously pinned
SHA256, and exact animal/day/position multiset equality*. No original
positions, animal IDs, dates or sub-hour timestamps may appear in
published results. The original clock basis (UTC vs GPS) and source
location-error magnitude are NOT independently verified.

## Frozen opportunity risk set
Only the previously verified source-year **geographic** matched pair
risk sets: annual day-balanced source-GPS centroids within **25 km**,
>=7 pair-common observed dates in >=2 calendar months of both winter
(Jan, Feb, Dec within same year) and summer (Jun, Jul, Aug).
The source-year original baseline pair counts are 112/21 (turkeys
2019/2020), 1/104 (bear), 55/205 (white-tailed deer). These year
labels represent a source-calendar *category*, not chronologically
consecutive winters or migration phases.

Then apply the independently tested, predeclared native GPS
timestamp-matching screen: **one-to-one greedy maximal matches**
between the two animals' recorded GPS times on the SAME date, with
maximum absolute time gaps of **15 minutes primary** (900 s)
or **30 minutes secondary** (1800 s). No reuse of a fix.
Require >=3 time-matched original fix pairs on each qualifying date,
>=7 qualifying dates per qualifying month, and >=2 qualifying
months separately in winter and summer. Verify EXACT agreement with
the prior 15/30-min feasibility output counts before calculating
any distances. Previous 15-min result: turkeys 2019 n112, 2020 n21;
black bear 2019 n0 STOP, 2020 n38; white-tailed deer 2019 n55,
2020 n205. For 30 min, only bear2020 changes to n47.
These dyads meet only a *sampling opportunity floor*, not verified
within-population biological association.

For each supported dyad and each of **12 deterministic SHA256 seeds
0–11**, select exactly two eligible months per season, exactly
seven qualifying pair-common dates per selected month, then exactly
**three one-to-one paired real GPS fixes per selected date** without
replacement. Fix samples depend on (source, year, tolerance,
animal pair, month, day, seed), and MUST be shared over all tested
distance thresholds. Per day, the selected three fix pairs
have matched source timestamps but potentially different exact
minutes/seconds, bounded by the declared gap. Source rows may not
be interpolated or spatially jittered. Report conditional
time-gap summaries and explicitly retain all denominator attrition.

## Frozen continuous-distance response and exact within-day null
Calculate the **haversine great-circle distance** between original
GPS positions, no spatial grid. Declare **1-km radius primary**
and **0.5 and 2-km radii secondary**, before viewing results.

For the three selected same-time matched pairs per date,
\(a_1,a_2,a_3\) and \(b_1,b_2,b_3\), define:

- Observed nearby fraction \(O_r=(1/3)\sum_{k=1}^{3}
  1[\operatorname{dist}(a_k,b_k)\le r]\).
- Exact within-date fixed-marginal random-pair expectation
  \(N_r=(1/9)\sum_{k=1}^{3}\sum_{l=1}^{3}
  1[\operatorname{dist}(a_k,b_l)\le r]\).
- Relative time-aligned nearby fraction \(D_r=O_r-N_r\).

The N term corresponds to independent permutation of **the spatial
partner assignments among those 3 existing matched time slots**,
holding both animals' observed GPS positions, source fix times,
each date and support fixed. It does NOT randomize biology; real
motion autocorrelation and habitat cues can invalidate interpreting
N as a causal no-interaction null. A positive D is NOT evidence of
direct social interaction or observed physical encounter.

Average date values equally within month, exactly two months equally
within season, and eligible dyads equally within each year/cohort.
For each tolerance × radius × seed, report winter/summer O, N, D;
winter-minus-summer contrasts, eligible dyad and animal counts,
exact pair-date and pair-fix counts and mean observed source-clock
time gaps. Produce all **2 gaps × 3 radii × 12 seeds** for each
estimable source/year; retain negative and near-zero results.
Missing dyads/time overlap are NOT estimated, not zero nearness.
The 12 seeds, thresholds, dependent dyads and repeated source years
are NOT independent inferential replicates or population confidence
intervals/p-values.

## Robustness, interpretation and stop
Hard-stop when original-source MD5/SHA changes, accepted
position/time multiset changes, selected pair counts disagree
with the independent timestamp-only preflight, any unsupported
day/month is scored, or a component violates 0<=O,N<=1 and
D=O−N. If fewer than eight same-source season-supported dyads
or fewer than three animals, declare STOP_SMALL_OPPORTUNITY and
do not compute the spatial response. This is a conservative
source-level feasibility gate, not a claim that interactions do
not occur.

Even if the original 1-km grid-clock D signal reproduces at
continuous 1-km distance, the conclusion is only **source-GPS
matched-fix relative geographic proximity**. Accuracy, local
population membership, genuine simultaneity and independent
resource exposure still require new validation before describing
encounters, avoidance, niche partitioning or causal mechanisms.
