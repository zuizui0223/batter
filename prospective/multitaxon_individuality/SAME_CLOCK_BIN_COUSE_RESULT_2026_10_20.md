# The same places, but the same clock bins? Source-verified spatial–temporal sharing across birds and mammals

**Empirical exploratory finding, 20 October 2026 — POST-INSPECTION.**
Original complete Movebank GPS/reference files re-downloaded, published MD5
and earlier pinned SHA256 reverified, independent timestamp-to-position
reconstruction passed. All results are public **aggregate-only**; original
animal IDs, exact observation dates and coordinates are not exported.

## 1. Biological question and two distinct observable dimensions

**Does geographic occupancy overlap imply that two animals use the same
place at approximately the same time?** Test the distinction using source
native-clock GPS time; a **6-hour** shared clock bin is the primary
resolution, with **3-hour** binning as a declared secondary sensitivity.

For each matched dyad and source-calendar day, restrict both animals to
the *same two or more observed clock bins*. Draw one real original GPS
position per animal/bin, repeat for 12 deterministic source-subsampling
seeds. Let spatial cells be 1, 5 or 10 km as below:

- **X** = overlap of the two within-day cell-occupancy distributions,
  pooling those same fixes across their shared clock bins
- **T** = fraction of matched clock bins where the two animals' sampled
  positions fall in the **same cell** (T6 or T3, depending on clock width)
- **N** = exact expected T if each animal's sampled spatial cells are
  independently reassigned across its **same observed clock bins** within
  the date. This is the dot product of their within-day cell frequencies
- **D = T − N** = descriptive **source-clock-bin alignment beyond a
  within-day time-label reassignment reference**, not social interaction,
  competition, avoidance, foraging synchrony or a biological p-value

A finite coupling inequality gives **T ≤ X** for each sampled day.
Source-clock bins can be up to 6 hours wide, and even fixes from the
same bin need not be simultaneous. Consequently neither T nor D is
an observed physical encounter. The time-label reassignment may break
real biological autocorrelation, and must not be treated as a
biologically randomized null distribution.

## 2. Exact data scope and population/opportunity gates

| Original published source | DOI | Retained complete original GPS fixes, 2019–2020 |
|---|---|---:|
| Wild turkey (*Meleagris gallopavo*) | [10.5441/001/1.671](https://doi.org/10.5441/001/1.671) | 435,214 |
| American black bear (*Ursus americanus*) | [10.5441/001/1.706](https://doi.org/10.5441/001/1.706) | 148,394 |
| White-tailed deer (*Odocoileus virginianus*) | [10.5441/001/1.718](https://doi.org/10.5441/001/1.718) | 371,080 |

**Total valid original GPS fixes: 954,688.** No new data were synthesized.

The previously established geometric pair risk set requires annual
day-balanced utilization centroids ≤25 km apart, >=7 shared GPS-recorded
dates in >=2 months of winter (Jan/Feb/Dec within a calendar year) and
>=2 months of summer (Jun/Jul/Aug). This reconstructs exactly the
original V2 eligible-pair counts and is **not proof of common biological
population membership**. Source reference data contain no independently
usable within-population labels for these cohorts.

New time eligibility additionally requires >=2 observed *matching*
clock bins on each selected date, and >=7 such dates in >=2 months in
each season. Exactly two supported months and seven dates per month
are sampled per dyad, across 12 deterministic seeds. The same
month/date/fix samples apply to all declared spatial grids; dates with
only one shared clock bin are **unobserved temporal comparisons**, never
coded as zero alignment. Winter months are a categorical calendar
window rather than a consecutive season spanning two years.

| Cohort | Eligible old geographic pairs | Eligible 6h-time dyads | Eligible 3h-time dyads |
|---|---:|---:|---:|
| Turkey 2019 | 112 | 112 | 112 |
| Turkey 2020 | 21 | 21 | 21 |
| Black bear 2019 | 1 | **0 — STOP** | **1 — STOP** |
| Black bear 2020 | 104 | 61 | 61 |
| White-tailed deer 2019 | 55 | 55 | 55 |
| White-tailed deer 2020 | 205 | 205 | 205 |

Black bear loses **43/104 dyads (41.3%)** to the stricter
within-date common-clock support. This retention loss cannot be
converted into evidence of absent co-use, and must accompany all
bear estimates. For bear 2019, the only geographically qualified
dyad is insufficient for cohort-level timing comparison.

## 3. Reference: 1-km cells, 6-hour source-clock bins

All values are cohort means over **12 source-observation
subsampling seeds**, with **exactly the same evaluated pairs within
each individual cohort** in winter and summer.

| Cohort | Time-qualified pairs | X winter | X summer | D winter | D summer | Seeds with D winter > D summer |
|---|---:|---:|---:|---:|---:|---|
| Turkey 2019 | 112 | 0.23903 | 0.05642 | +0.02499 | +0.00737 | 12/12 |
| Turkey 2020 | 21 | 0.48094 | 0.19808 | +0.03984 | +0.01099 | 12/12 |
| Black bear 2020 | 61 | 0.01890 | 0.00390 | +0.00002 | +0.00027 | 4/12 |
| White-tailed deer 2019 | 55 | 0.03252 | 0.04575 | +0.00515 | −0.00005 | 12/12 |
| White-tailed deer 2020 | 205 | 0.03107 | 0.04582 | +0.00472 | +0.00039 | 12/12 |

### Non-obvious observation

**The white-tailed deer source in both years uses the same sampled
1-km cells less similarly in winter than summer (lower X), yet its
limited shared 1-km locations show greater winter *coarse time-label
alignment relative to same-date random bin assignment* (higher D).**

This is a distinction between the **amount of geographic sharing**
and the **temporal ordering of the observed shared-space use**.
It does **not** mean absolute winter encounters exceed summer
encounters: even the uncorrected T is lower in winter at 1 km
(2019: 0.03006 vs 0.04334; 2020: 0.02727 vs 0.04339).
The additional winter alignment beyond a clock-bin-shuffled
reference is modest in absolute terms (approximately +0.005
in the within-day cell-match proportion).

The wild turkey source also has larger positive 1-km winter D in
both years, but X is itself much higher in winter. Black bear 2020
shows almost no systematic excess clock alignment on the 1-km
source-clock measure, despite its estimable geographical X.
These are **three source-specific taxa and repeated source years**,
not independent ecological populations or a worldwide generality.

## 4. Declared scale/time-bin sensitivity changes the story

The **primary declared spatial reference** in the committed
design is 5-km origin (0,0), 6-hour bins. At that coarser
resolution, T approaches X and the excess time-ordering
measure D often nears zero:

| Cohort | X winter/summer, 5 km | T6 winter/summer, 5 km | D winter/summer, 5 km | Seeds with positive winter−summer D |
|---|---|---|---|---:|
| Turkey 2019 | 0.47490 / 0.32792 | 0.47433 / 0.32659 | +0.00120 / +0.00317 | 0/12 |
| Turkey 2020 | 0.64683 / 0.27537 | 0.64534 / 0.27480 | +0.01989 / +0.00655 | 12/12 |
| Black bear 2020 | 0.05796 / 0.05364 | 0.05796 / 0.05111 | 0 / −0.00023 | 7/12 |
| White-tailed deer 2019 | 0.09559 / 0.09343 | 0.09302 / 0.09302 | +0.00022 / −0.00010 | 7/12 |
| White-tailed deer 2020 | 0.09549 / 0.09145 | 0.09393 / 0.09135 | +0.00020 / −0.00001 | 8/12 |

This prevents a cherry-picked claim of a taxon-general winter
excess of T−N. The 1-km comparison is one of the **predeclared
secondary spatial scales** and is interpreted explicitly as
scale-conditional, not a replacement for the 5-km primary.
A half-cell shifted 5-km grid can also change the sign of D.

At **3-hour** bins, 1-km winter–summer D remains positive in
all 12 seed draws for turkey 2019 and 2020 and deer 2019 and
2020, but not in bear 2020. Mean 1-km winter D is approximately
+0.0350/+0.0550 for turkey 2019/2020 and
+0.00534/+0.00476 for deer 2019/2020.
Thus a *fine-grid source-clock temporal alignment* pattern
is repeatable in these specific two taxa/years under the declared
3h/6h sampling scenarios. It is **not** invariant across
spatial resolutions.

The complete experiment covers **5 time-qualified source/year
cohorts × 2 clock widths × 4 fixed grids × 12 seeds = 480 aggregate
scenario outcomes**. Six source-year combinations were considered,
and the two unsupported bear 2019 time-width entries are explicitly
NOT ESTIMABLE. These are not 480 independent animals,
populations or significance tests.

## 5. Reproduction and integrity

- [Committed design, including 6h primary and all sensitivities](SAME_CLOCK_BIN_COUSE_DESIGN_2026_10_20.md)
- [Source-native clock and original-GPS replay](same_clock_bin_couse_v1.py)
- [Synthetic controls including identical X and reversed clock ordering](tests/test_same_clock_bin_couse_v1.py)
- [Independent full-result verifier](validate_same_clock_bin_results_v1.py)
- [Aggregate reference table for all cohorts/grids](SAME_CLOCK_BIN_COUSE_SUMMARY_2026_10_20.json)
- Complete original-source results:
  [turkey](SAME_CLOCK_BIN_COUSE_TURKEY_2026_10_20.json),
  [black bear](SAME_CLOCK_BIN_COUSE_BLACK_BEAR_2026_10_20.json),
  [white-tailed deer](SAME_CLOCK_BIN_COUSE_WHITE_TAILED_DEER_2026_10_20.json)
- [GitHub Actions source-GPS run](https://github.com/zuizui0223/batter/actions/runs/39414865136) and
  [independent aggregate verification + upload run](https://github.com/zuizui0223/batter/actions/runs/39415766216).

The independent verifier requires **exact pinned SHA256** for all
three source result files and checks every calendar/year time
eligibility row, all 480 scenario identities and fixed
denominators, including 0≤T≤X, 0≤N≤X, T−N=D,
and no missing-as-zero or unsupported population status.
Publisher logs have no raw GPS records, IDs or positions.

## Interpretation and next scientific boundary

An original public GPS archive can reveal **space-use overlap and
the clock-ordered pattern of that overlap as different empirical
dimensions**, but these are not automatically separate ecological
niches or observed animal interactions. A model with group-level
temporal patterns can still arise from scheduled fix times,
GPS accuracy, day length, daily movement autocorrelation,
source-clock offsets or local habitat structure.
The exact independent label-permutation reference controls
within-day cell frequencies and clock-bin availability,
**not** all those biological and detection processes.
The source data do not establish independent local populations,
and the same animals may recur across years. There is no
biological significance test, no mechanistic identification,
no source-habitat resource exposure E, and no cross-source
movement identity R for these three taxa.

**Next defensible tests:** source-specific capture/population
provenance; finer observed-time lags using original timestamps
instead of treating hours-wide bins as encounters; location
uncertainty and temporally autocorrelated phase controls;
independent resource-layer exposure E. The core ecological
conclusion remains descriptive and scale-conditional.
