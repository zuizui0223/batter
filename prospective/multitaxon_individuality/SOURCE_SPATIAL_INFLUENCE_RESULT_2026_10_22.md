# Seasonal GPS nearness depends on which animals are compared: geographic substructure and individual influence

**22 October 2026. Executed on complete original published Movebank GPS, post-inspection exploratory.**

## Revised biological finding (including an important limiting result)

The previous result — larger winter than summer *same-day within-500m GPS
nearness over preceding/following-day original trajectory controls* in
a southeastern-US wild-turkey source — **is supported in 2019 across
all three declared geographic pair restrictions** but is **NOT
stable in 2020 when compared animals are restricted to the closest
annual GPS-use centers**.

This matters ecologically: **day-specific geographical sharing is
conditional on which pairs of animals are eligible**, rather than
a species-wide winter-interaction coefficient. The annual usage
centers, repeated subjects, and orientation of the source-GPS
time comparison are distinct design axes. No causal drivers,
social flocks, or food-resource interactions are inferred.

The first discovery of the 2020 spatial sign reversal comes from
a post-inspection sensitivity, not a prospective confirmatory test.
No new radius was selected after the result: the 5, 10 and 25 km
pair-center filters, 500m/1km/2km nearby GPS radii, both 15/30-min
time gaps, both focal-original-animal directions and all 12 source
draws were fixed in the
[design](SOURCE_SPATIAL_INFLUENCE_DESIGN_2026_10_22.md)
before the original-GPS results were opened.

## 1. Original source integrity and what source metadata actually support

The original complete published GPS and reference files were
again downloaded in the same study-source definition, with
publisher MD5, pinned whole-file SHA256, unique animal-tag join
and exact accepted GPS time/position multiset verified against
the prior analyses. The source *per-dyad reconstructed original
GPS means* exactly reproduced **all 576** previously committed
A/B anchor × 12-seed × 3-radius summaries for the eight
estimable source/year/tolerance conditions.

| Published source | DOI | Accepted 2019–2020 GPS fixes | Median source fixes per animal-date | Median within-date GPS recording interval |
|---|---|---:|---:|---:|
| Wild turkey, southeastern US | [10.5441/001/1.671](https://doi.org/10.5441/001/1.671) | 435,214 | 17 | 3,600 s |
| White-tailed deer, western Virginia | [10.5441/001/1.718](https://doi.org/10.5441/001/1.718) | 371,080 | 24 | 3,600 s |
| Black bear, Connecticut | [10.5441/001/1.706](https://doi.org/10.5441/001/1.706) | 148,394 | 9 | 3,600 s |

In all three original reference tables and their source GPS columns,
the independently identified explicit study-site/animal-group
fields are absent. There are also no usable original fields
declaring tag-specific location-accuracy or scheduled GPS duty-cycle
parameters. **An observed median GPS interval of one hour is a
property of the retained fixes, NOT proof of a programmed hourly
sampling regime or calibrated GPS precision.** Native GPS/UTC
clock offset and biological local-population membership are not
verified. Dataset names give regions, not site/population
annotations at the individual level.

## 2. Two years are not the same replication type in the two taxa

| Source | 2019 eligible animals | 2020 eligible animals | Same original animal IDs across years | Reused eligible animal pairs |
|---|---:|---:|---:|---:|
| Wild turkey | 19 | 7 | **0** | **0** |
| White-tailed deer | 11 | 21 | **11** | **55** |

These counts use the *identical pre-existing same-24-hour dyad opportunity,
both GPS anchor directions and ±15-minute source-time requirement*.
The 30-minute comparison gives the same year-reuse counts.

Wild turkey therefore has **two distinct yearly sets of tracked
individuals**, an improvement on assuming 2019/2020 are merely the
same subjects. But it is **still ONE published source study**, with
unverified local populations and GPS duty cycles. In white-tailed
deer, all eleven 2019 animals recur in 2020, so one must not
present the two years as independent animal-level replicates.

## 3. Wild turkey geographic pair-distance filters change the 500m result

Below, compare **the same pre-existing source dyads, seasonal
month/date rules, original recorded fixes and day-shift control**,
with only a geometric restriction on the two animals' *annual
usage-center distance*. The response is the **winter-minus-summer
difference in L1 = O(same source date) − mean O(source previous
and next dates)** for recorded GPS positions within 500 m,
tolerance ±15 min. It is a **proportion difference**, not an
encounter rate. Positive means larger winter-specific same-day
nearness relative to adjacent-day original GPS paths.

| Year | Max separation of annual GPS-use centers | Dyads | Original A→B ΔL1 | Reversed B→A ΔL1 | Positive original draws | Positive reversed draws |
|---|---|---:|---:|---:|---:|---:|
| 2019 | 5 km | 73 | **+0.077354** | **+0.080289** | 12/12 | 12/12 |
| 2019 | 10 km | 78 | +0.072942 | +0.075346 | 12/12 | 12/12 |
| 2019 | 25 km | 112 | +0.050799 | +0.052473 | 12/12 | 12/12 |
| 2020 | 5 km | 14 | **−0.016652** | **−0.000425** | **3/12** | **6/12** |
| 2020 | 10 km | 16 | −0.000992 | +0.009735 | 5/12 | 9/12 |
| 2020 | 25 km | 21 | **+0.026644** | **+0.027211** | 12/12 | 12/12 |

The original two-year/25km result is *numerically correct*
but **over-general if described as a local-pair-specific
winter nearness pattern across both years**.

### What do geographically more separated pairs contribute?

A transparent algebraic decomposition of the saved **pair-weighted
mean** across nested centroid-distance filters recovers three
mutually exclusive, original-year-usage-center pair classes.
These are newly derived descriptive subset means, NOT
independent animal/population samples, and the 12-seed sign
distributions for each annulus have **not** been computed.

| Wild turkey year | Pairs with centroid separation | Original 500m ΔL1 | Reversed 500m ΔL1 |
|---|---:|---:|---:|
| 2019 | ≤5 km (73 pairs) | +0.077354 | +0.080289 |
| 2019 | 5–10 km (5 pairs) | +0.008526 | +0.003167 |
| 2019 | 10–25 km (34 pairs) | approximately 0 | approximately 0 |
| 2020 | ≤5 km (14 pairs) | **−0.016652** | **−0.000425** |
| 2020 | 5–10 km (2 pairs) | +0.108631 | +0.080853 |
| 2020 | 10–25 km (5 pairs) | +0.115079 | +0.083134 |

The strong positive 2020 aggregate at 25 km is thus
**concentrated in seven dyads with more widely separated
annual usage centers**, rather than the fourteen closest
pairs. Importantly, the >5km dyads may share an original
animal and do not represent seven independent biological
events. A large interanimal separation of **annual usage
centers** cannot establish that animals converged onto
one winter patch; only a separate source-month/season
distribution analysis with GPS errors could test that.

At the 1-km nearby-position radius, wild turkey 2020
remains mostly winter positive even under the 5km
annual-center pair restriction (11/12 original,
12/12 reversed). Therefore the loss of stability is
**specific to the 500m near-position endpoint** and
must not be generalized uncritically to 1km.

## 4. Source-centroid network components: geometric groups, not biological populations

Using source-verified original GPS year/day-balanced centroids,
the <=5km eligible pair graph splits into:
- wild turkey 2019: **two spatially separated components**
  comprising 11 and 7 tagged animals with 53 and 20
  eligible edges, respectively. The 19th animal has no
  pair within 5km and is not assigned to these edge
  components. Although both components have adequate
  geometric support, **their separate effect estimates
  have not been computed** — they cannot yet be declared
  independent replicated populations.
- wild turkey 2020: **one 6-animal graph component**
  with 14 edges; the seventh source animal has no
  within-5km eligible edge.

At <=10km the 2019 graph still has two components
(11/8 animals and 55/23 edges); at <=25km all 19
animals join one graph. This shows why a permissive
pair-center threshold can pool animals with distinct
home-range geography. It does not mean that disconnected
graphs are demographically independent social populations.

White-tailed deer shows two <=5km source components in
2019 and three in 2020, with repeating original subjects.
Its earlier weak original/reverse seasonal nearness
difference does not meet the same fixed two-direction
500m/1km stability gate.

## 5. One-animal deletion reveals a 2020 fragility

Each original tracked animal is omitted **one at a time**,
all GPS dyads incident to that animal are dropped, and
the previously generated original fix/date/season samples
for every remaining dyad are preserved. Missing or
insufficient residual risk sets are not coded as zero.
This is **not** an iid jackknife or a confidence interval.

| Wild turkey cohort | Radius | Source animals with estimable omissions | Original A→B omissions retaining ≥10/12 positive draws | Reversed B→A omissions retaining ≥10/12 positive draws |
|---|---|---:|---:|---:|
| 2019 | 500 m | 19 | **19/19** | **19/19** |
| 2019 | 1 km | 19 | **19/19** | **19/19** |
| 2020 | 500 m | 7 | **6/7** | **6/7** |
| 2020 | 1 km | 7 | **7/7** | **7/7** |

At 500 m in turkey 2020, the omission-level 12-seed
mean contrast spans **−0.015079 to +0.048214**
(original) and **−0.001852 to +0.044841**
(reversed), so exclusion of one source animal can
change the direction. At 1 km, both anchor
orientations maintain a positive omission-mean
across all seven choices and >=10/12 positive
source subsamples.

The **2019 500m winter GPS nearness pattern is
substantially stronger to these exact source
sensitivity controls** than the 2020 500m
pattern. A species-wide two-year general
"winter animal synchronization" conclusion is
not supported.

## 6. Reproduction, STOPs and nonclaims

Evidence provenance:
- [Source-outcome-independent post-inspection design](SOURCE_SPATIAL_INFLUENCE_DESIGN_2026_10_22.md)
- [Complete original-GPS pipeline, individual/site counts kept private](source_spatial_influence_v1.py)
- [Original-source synthetic and fixed-mask reconstruction tests](tests/test_source_spatial_influence_v1.py)
- [Fully source-pinned output validator](validate_source_spatial_influence_v1.py)
- [Full source/year/tolerance/centroid and LOO summary](SOURCE_SPATIAL_INFLUENCE_SUMMARY_2026_10_22.json)
- [144-row transparent reviewer table](SOURCE_SPATIAL_INFLUENCE_REVIEW_2026_10_22.csv)
- Original source aggregate archives:
  [turkey](SOURCE_SPATIAL_INFLUENCE_TURKEY_2026_10_22.json),
  [white-tailed deer](SOURCE_SPATIAL_INFLUENCE_WHITE_TAILED_DEER_2026_10_22.json),
  [black bear](SOURCE_SPATIAL_INFLUENCE_BLACK_BEAR_2026_10_22.json).
- [Publisher source original-data action](https://github.com/zuizui0223/batter/actions/runs/39713436699)
  and [checksum-pinned source publisher](https://github.com/zuizui0223/batter/actions/runs/39714223714).

**All original-GPS three-source matrix jobs passed, eight
synthetic contracts passed, 576 existing GPS seed/radius
scores replayed exactly, and the independent source
aggregate verifier passed.** The audit includes all 2019
and 2020, both preselected 15/30-minute time cutoffs,
all 500m/1km/2km radii, both A/B anchors and 12
original source samples. Four black-bear year/tolerance
groups remain STOP under original minimum-pair support
requirements; no zeros are substituted.

This observational signal cannot identify:
actual physical animal encounters or cooperation;
winter flocking, mating, migration stage or food
resource choice; background animal movement
autocorrelation and changing between-day weather;
tag GPS positional uncertainty or source clock
offset; independent local populations within
one published data package; a replicated taxon-wide
law, any population p-value or independent effect
confidence interval. Time schedules from recorded
source GPS have a median one-hour within-day
interval but device fix schedules are not
documented in the accepted public files.

**Biologically consequential next test:** estimate
season-specific shared usage geography and the
same-day original-source score separately in the
two 2019 geographically disconnected GPS components,
then compare independent source populations or
studies. If geographically distant annual-center
pairs contribute the 2020 winter signal because
winter home ranges converge, that must be shown
directly by source-season positions; it is a
hypothesis, not an established mechanism.
