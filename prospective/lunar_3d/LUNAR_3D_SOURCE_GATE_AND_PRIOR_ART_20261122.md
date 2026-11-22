# Lunar responses in three-dimensional bat airspace — prior-art-corrected prospective protocol v1

Date: 2026-11-22. Status: **SOURCE/EXPOSURE ADMISSION ONLY; no lunar effect estimated and no height response inspected**. This is a new prospective branch. It does not revise the frozen JAE v0.3.8 manuscript, `main`, or the resource×height evidence ledger.

## 1. Prior art and the remaining question

The broad hypothesis “moonlight changes bat vertical flight / forest strata use” is **not new**:
- Hecker & Brigham (1999), *J Mammalogy* 80:1196–1201, DOI **10.2307/1383170**: moonlight × forest stratum interaction, with canopy-level activity higher on bright nights.
- Roeleke et al. (2018), *Movement Ecology* 6:11, DOI **10.1186/s40462-018-0131-7**: 3D GPS + canopy model in *Nyctalus noctula*; moonlit nights showed lower flight altitudes, reduced forest use, more open-field use; remaining forest flights were primarily below canopy.
- Śmielak (2023), *Behavioral Ecology and Sociobiology* 77:21, DOI **10.1007/s00265-022-03287-2**: lunar phase alone is an inadequate measure of instant ground illumination because lunar altitude, twilight, clouds and vegetation matter.

**Revised question:** Where does time-varying lunar geometry add transferable predictive information to recorded bat use — horizontal location, state allocation, or conditional vertical distribution — and do response directions differ among ecological contexts? This design must not claim the original 3D lunar pattern as a discovery.

## 2. Competing mechanisms; evidence hierarchy

**Predation risk:** reduced use of exposed heights/places during visible bright moon. **Resource reallocation:** some open/upper flight may increase if prey shifts there; test requires independently measured prey to call this mechanism established. **State-mixture change:** flight-height differences might reflect changed commuting/foraging allocation rather than within-state change; only assess state with height-independent state assignments. A lunar response in observational GPS alone cannot separate predation from prey changes or internal lunar clocks.

Lunar ephemerides are externally determined, but **they are not random treatment assignment**: moon phase covaries with tracking date, nocturnal time, possible prey emergence and individual sampling; cloud cover also affects prey, temperature and detection. Treat comparisons as observational/quasi-experimental *at most*, not as clean causal identification.

## 3. Source universe and strict support gate

The existing batter validated six panels belong to four taxa: *Tadarida teniotis* (DOI 10.5441/001/1.52nn82r9), *Eidolon helvum* (1.k8n02jn8), *Hypsignathus monstrosus* (1.278) and *Phyllostomus hastatus* (1.282, 1.321, 1.322). All sources remain hash-pinned in `config/bat_panel_sources_v1.json`. *Nyctalus* does **not** belong to the six eligible comparative panels; its recovered migration source had only three height-bearing individuals and no repeated individuals according to `BAT_PANEL_SEARCH_CLOSEOUT.md`. Do not advertise it as a passing fifth taxon. Roeleke's published *N. noctula* data are prior art, not an independent newly tested result.

**Source-only gate, before opening numeric heights:**
- Read source timestamps (UTC), IDs, XY, source outlier flags and **only non-empty presence** of the native height field.
- Assign approximate local-solar night, dusk-to-dawn. Derive per-fix Moon altitude and fractional illumination plus Sun altitude from ephemerides. For the source screening only, bin observations in 15-min and 0.25-degree cells.
- Retain Sun altitude <-12°; label **bright** when Moon altitude >=10° and illuminated fraction >=0.80, **dark** when Moon altitude <=-5° or fraction <=0.20; other exposures remain intermediate. This is **moon geometry, not calibrated ground lux**. Actual modeling must use continuous modelled irradiance and weather/terrain/forest exposure where feasible.
- An individual-night is eligible at >=30 valid fixes, and one exposure is supported at >=20 fixes. A provisional confirmatory within-animal source **PASS** requires >=5 individuals with >=2 bright and >=2 dark nights each, and >=35 days' population night span; report within-night dual-exposure nights separately. Pre-specified thresholds check power/support, **not significance**.
- **STOP** confirmatory height-model fitting if no panel passes. Report sample and exposure support rather than substituting between-animal moon phase differences. Do not tune inclusion thresholds after inspecting height outcomes.
- Track tag altitude datum and local terrain accuracy before opening/claiming AGL. The existing centered-height identity result does not guarantee absolute-height calibration for each source.

## 4. Estimands and comparators (only after source gate)

Condition on observed recording/flight fixes; do not claim a nightly population activity suppression outcome without a valid schedule of recording effort/non-flight observations.

Decompose the **recorded-fix distribution**:
`p(x,y,z | recorded, moon, H) = p(x,y | recorded, moon, H) * p(z | x,y, recorded, moon, H)`.

1. **Horizontal choice:** conventional movement/available-step model with XY, night time, individual and environment; compare with additional lunar terms, held out by whole night / individual. The candidate/reference selection and absolute log scores must be identical within comparisons.
2. **Conditional height (primary novel extension):** compare `p(z | XY,time,environment,individual)` to the same model with lunar exposure × habitat or exposure interaction. Score **exactly the same height-bearing heldout fixes** with a proper log score; integrate independently justified sensor/terrain error. Keep absolute scores, paired increments, and uncertainty at independent-night/animal level.
3. **State mixture:** only when a training-only, height-independent XY/acceleration classifier is supported; integrate state posterior probabilities instead of labeling height-defined feeding states.
4. **Within-state shape:** secondary test of centered-height profile, not a substitute for AGL or the primary height location response.

Default heldout unit: whole local night; separately withhold individuals and spatial regions as different generalization targets. Avoid random GPS-row cross-validation. Adjust for time since sunset, date/season, weather and habitat; require overlap (positivity) within animal/place/time. Fit continuous physical exposure only after weather/source admission.

**Predeclared falsification:** Fractional moon illumination should not be interpreted as instantaneous light if its association persists when the moon is below the horizon; such a finding can signal lunar-cycle biology or calendar confounding, but is not an illumination effect. Compare moon-visible and moon-invisible windows conditional on time of night; cloud stratification is supportive, not a randomized instrument.

## 5. Interpretation ceiling / claim decision

A successful heldout lunar increment in conditional height would show lunar geometry carries predictive information beyond matched XY and environmental baselines. It **does not by itself** identify predators, prey, perceived fear, culture, causal mediation, a universal bat law or improve geographic species occupancy predictions. Four source taxa, with only one aerial insectivore among the six panels, are insufficient for a robust diet-guild generality claim.

A defensible title if the actual data support it: **“Lunar exposure reorganizes bat airspace use through context-dependent horizontal and vertical responses.”** If no panel passes exposure support or heldout gains are not positive, report the support/negative result without retrofitting a positive story.
