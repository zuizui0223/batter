# First real-source ecological pattern audit: X is observable; R, T, E remain open

**Date:** 2026-10-19  
**Status:** Retrospective source-file descriptive pilot, NOT three-clade individual-specialization inference, NOT a journal result.  
**Raw:** Original public Movebank CC0 GPS event CSV; 351,693 rows scanned (wolves 15,159 + elephants 283,688 + green turtles 52,846) with individual identifiers/coordinates retained only transiently in analytical memory. DOI and bitstream UUIDs in `EXPLORATORY_SOURCE_2D_OVERLAP_2026_10_19.json`.

## Why this is an ecological-pattern study

The ecological state is multidimensional. `R` = held-out individuality of movement decisions within common ecological opportunities; `X` = estimated overlap of 2D space-use distributions; `T` = temporal sharing of patches and encounters; `E` = independently measured habitat/resource exposure (and diet only with independent feeding evidence). We **should not** substitute the easiest measured outcome, X, for all of ecology.

The new substantive contrast from actually opened sources is **ecological calendar/space-use configuration**. Tracking individuals from a *shared breeding hub* can create strong initial overlap followed by geographic divergence, whereas separate resident herd/individual source cohorts can be largely geographically disjoint. This is a descriptive result **already motivated or substantially anticipated by original studies**; it does **not** prove specialized movement policies, behavioral individuality or competitive partitioning.

| Original source and cohort slice | Study GPS support | Empirical X, mean 10-km estimated 2D UD overlap (day-balanced within animal) | Defensible interpretation |
|---|---|---:|---|
| *Canis lupus*, source 2007-03 | 12 individual IDs total (16 reference deployments); 7 animals/21 paired dyads this month | **0.0129** (19/21 pairs zero at 10 km) | Most study pairs share little *estimated geographic use* at 10 km; reference pack/home-range and common access unresolved |
| *Loxodonta africana*, source 2008-03 | 14 GPS animals, each a **different herd**; 14/91 dyads this month | **0.0633** (70/91 zero at 10 km) | Multiple herds in a large park are not a homogeneous shared-opportunity sample |
| *Chelonia mydas*, same 2018 July → November GPS animals | 32 GPS animals total, 12 same adults present in both months, 66 repeatedly paired dyads | **~1.000 → 0.000**; 10-km grid shifts give July **0.756–1.000**, November **0–0** | Nesting-area convergence followed by post-breeding spatial dispersal, NOT inferred persistent individual specialization |

Turtle historical tagging cohorts show directionally analogous, non-independent **within-species** before/after patterns:
- 2012 cohort, original n=8: 2012 October X10=0.5655 → 2013 January X10=0.0169.
- 2015 cohort, original n=8: first tabulated cohort-month 2015 August X10=0.2861 → November X10=0.00478. Do **not** falsely label August as the first month since tagging.
- The 2018 same-12 turtle contrast uses source-authored Fastloc quality selection **>=5 GPS satellites and residual <35**: 46,892 / 52,846 retained (5,954 excluded); no duplicate animal timestamps or accepted-sequence implausible >10 km/h travel steps. Reported differences are robust in direction to 5/10/20km cell widths and four 10-km grid offsets.

Published ecological context **must not be portrayed as discovered here**:
- Hays et al. (2024), *Journal of Applied Ecology* 61:658–668, doi:10.1111/1365-2664.14599, analyzed exactly this Movebank turtle source, 32 adults nesting on Diego Garcia and later distributed throughout western Indian Ocean foraging grounds, with small foraging home ranges. Our descriptive monthly overlap is an alternative quantification, not a new discovery of migration or home-range variation.
- Thaker et al. (2019), *Frontiers in Ecology and Evolution*, doi:10.3389/fevo.2019.00004, documented temperature-dependent elephant movement and shuttling to water in the same 14 different herds. We have **not** replicated its environmental model here.
- The original wolf source Latham & Boutin (2019) doi:10.5441/001/1.7vr1k987 concerns predator–prey and linear-feature ecology; no pack-level allocation was verified from our source reference yet.
- Caldwell et al. (2026), *Current Biology*, doi:10.1016/j.cub.2026.05.041, already linked inter-individual movement variation to community resource-use overlap in five ungulates. A future claim must go beyond describing individual variation and overlap.

## How these source metrics were calculated

1. Source-specific original event CSV, verified sensor-type GPS (not study-title GPS keyword), `visible=true`, nonmissing individual ID, timestamps, WGS84 coordinates. The turtle Fastloc source uses publication-specific satellite/residual and maximal 10km/h travel checks.
2. UTC calendar-year-month source windows, with ≥5 days and ≥10 fixes per individual-month (elephants: ≥40 fixes) and ≥3 simultaneous calendar tracking dates per dyad; per-animal-day rather than raw-fix event weighting.
3. Grid histogram `p_i(c)` with equal total per observed animal date; compute each pair's `O10 = sum_c min(p_i(c),p_j(c))`. Approximate source-mean-latitude equirectangular projection, 5/10/20 km sensitivity, and 2D half-grid origin shift for quality-controlled turtle 2018 cohort.
4. Report every original dataset separately, DOI and original file UUID, monthly cohort sizes, pair counts, cell-scale uncertainties. **No p-values**, no dyad-as-independent bootstrap, no false exact physical co-use equivalence.
5. Reproduction program: `source_2d_overlap_cli_v1.py`. It accepts a locally downloaded original source CSV and emits aggregate JSON with no animal ID, animal coordinates or exact tracking day exports. Self-test uses invented two-individual same/disjoint space; CI tests **synthetic only** and intentionally does not download sensitive GPS data.

## Sensor-specific stops

- Larus argentatus East Bay Island source doi:10.5441/001/1.1r1s4v8d: actual event sensor is **Argos Doppler shift 28,649/28,649**, despite metadata GPS candidate status; exclude from high-precision shared-site movement test. Do not count this as null biological individuality.
- Published Galápagos tortoise `Movement data.csv` is **2,980 rows of movement-derived monthly variables**, not directly source GPS; its huge original raw 136MB GPS file needs separate species/site/cadence/rights validation. Do not confuse monthly input summaries with independent GPS events.

## The legitimate scientific next test

**Do not immediately fit a clade-wide R–X regression**: 3 opened species/source groups with biologically different access regions and calendar phases are insufficient, and R was not computed. Instead search the full 437-package registry for eligible same-species, same-local-access, same-season sources and then:

- Estimate **R** from held-out within-context movement-mode choices at *verified shared places*; null labels must preserve animal day/session/colonial or herd structure, gap and local temporal opportunity. Most wolf/elephant dyads are **structural common-space stops**, not negative R.
- In green turtles, align nesting, migration and **foraging-residence** stages using source-independent behavioral state/time; after stage split, assess whether the same animal has ≥2 independent comparable re-exposure bouts before claiming repeatable individual decision signatures. A single one-way nesting-to-foraging migration is not replication of movement individuality.
- Source priority: further populations from official original GPS files (e.g., 35 source fox IDs in UK wet grasslands with 39 deployments, doi:10.5441/001/1.304; multi-site tapir; suitable bird GPS rather than Argos; elephant common-site subset). Split source sites, studies, deployment years, individuals and sensor tiers **before opening R**.
- Only after independent `R` and `X` cohorts are verified, estimate whether temporal sharing T or external resource/habitat exposure E adds an ecological difference that *is not determined merely by geographic separation*.

**Current bottom line:** real source data support contrasting spatial/calendar *patterns*, but **no verified cross-taxon ecological individuality-to-resource-partition result yet**. The manuscript's general contribution will depend on independent same-opportunity R/T/E tests and broad source sampling, not rebranding existing 2019/2024 species migration findings.
