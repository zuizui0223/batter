# Source-GPS matched-time distance bands: post-inspection analysis plan

**Prepared 21 October 2026. Exploratory extension after the cumulative
geodesic results and preliminary signs were inspected. NOT a preregistration.**
This plan freezes interpretation, full coverage, checks and reporting
before committing the derived disjoint-distance-band artifact.

## Research question
Does source-observed GPS positional proximity in each season have different
*distance-band contributions* beyond a **fixed within-date time-assignment
reference**, despite cumulative proximity/occupancy indicators showing
apparently contradictory seasonal directions?

Source of all input data: the complete, already committed original-GPS
source aggregate files SUBHOUR_GEODESIC_{SOURCE}_2026_10_20.json.
Original Movebank DOIs: 10.5441/001/1.671 (wild turkey),
10.5441/001/1.706 (American black bear),
10.5441/001/1.718 (white-tailed deer). Prior original publisher MD5,
pinned SHA256, full GPS animal/date/position multiset reconstruction and
same-year +/-15 or +/-30 minute GPS-time pairing have been separately
verified. **This is an algebraic transformation of prior source
aggregates, NOT an independent original GPS download or replication.**

## All comparisons, no outcome-dependent exclusions
Use all three source taxa, 2019 and 2020, both source-recording
tolerances 900 and 1800 seconds, every original seed 0–11 and the
original cumulative haversine radii 0.5, 1.0 and 2.0 km.

Retain original verified source-year dyad counts:
- turkey 2019 112, 2020 21, both tolerances;
- white-tailed deer 2019 55, 2020 205, both tolerances;
- black bear 2019 0 (retain both NOT_ESTIMABLE STOP groups);
- black bear 2020 38 (900 seconds), 47 (1800 seconds); the
  difference in supported pairs prohibits treating those tolerance
  contrasts as same-pair biological effects.

Each eligible pair was evaluated on exactly three original one-to-one
GPS fix pairs/date, seven source-pair-common dates/month and two
months/season. Winter=(Jan, Feb, Dec) within one calendar year,
summer=(Jun, Jul, Aug), not a continuous winter. Original source-year
population membership is not independently verified; ≤25-km
annual-centroid separation is geometric, not a social relationship.

## Four disjoint distance bands
For each source/year/tolerance/seed and season:
- O(r) is the previously verified observed proportion of matched GPS
  fix pairs within radius r
- N(r) is the exact same-date expectation under reassignment of the
  three position pairings among observed time slots
- D(r)=O(r)-N(r) is conditional *source-clock matching surplus*.

Use four mutually exclusive intervals, with exact endpoints:
[0,0.5] km, (0.5,1] km, (1,2] km, and (2,infinity) km.

For M=O or N, define B1=M(0.5), B2=M(1)-M(0.5),
B3=M(2)-M(1), B4=1-M(2). Compute band D_B=O_B-N_B;
independently verify it also equals differencing cumulative D:
B1=D(0.5), B2=D(1)-D(0.5),
B3=D(2)-D(1), B4=-D(2).

Per individual seed and season, enforce sum O_B=1,
sum N_B=1, sum D_B=0, nonnegative O_B and N_B.
The winter minus summer D_B contrast also sums to zero.
**A positive surplus at short distance must be offset at
another distance by construction, but this does not specify
which distance band carries that offset.** Negative D_B is
NOT proof that animals avoid that separation distance.

## Output/interpretation rules
Keep ALL 5 estimable source/year groups ×2 tolerances ×4 bands,
12 seeds/band = 480 dependent band/seed rows and 40 summary rows,
plus both bear-2019 STOP groups. Report winter/summer band O, N, D,
winter-minus-summer D, 12-seed mean/min/max and sign counts.
Keep original dyad, date/fix denominators with the full results.

The white-tailed deer <=500 m and 1–2 km, 900-second examples are
POST-INSPECTION FOCAL RESULTS, not confirmatory generality.
Report turkey and black bear (including inconsistent patterns)
with the identical metrics and include 1800-second sensitivity
and >2 km complement. Do not convert 12 seeds, year repeats or
dyads sharing animals into independent samples, p-values, or CIs.

No source GPS fix positional accuracy, habitat/source clock
calibration, seasonal detection process or animal population has
been causally validated. Two GPS points within 500 m and
15 minutes are NOT verified physical interactions or social edges.
D is a conditional within-date diagnostic, not a causal
synchronization/avoidance test.

## Verification and next biological gate
Re-read source JSON by exact pinned byte SHA256. Verify all original
year/tolerance/seed/radius status and denominators, monotone
cumulative O and N, O-N=D, each nonnegative band, each four-band
partition sum, each sign count and mean against independently
calculated seed values. Release aggregate-only source/year summaries:
never animal IDs, exact dates, timestamps, GPS positions or cells.

A genuine ecological mechanism test requires original GPS fix
accuracy and sampling schedule review, local-population membership,
and autocorrelation-preserving source-time-shift or phase controls.
Without these, no active synchronization, avoidance, diet partition,
encounter or worldwide ecological law can be concluded.
