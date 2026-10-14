# Panel-profile count and cross-source animal-identity QA

**2026-10-14 — source-integrity audit only. No new biological outcome or inferential analysis.**

## Audited source facts

The original JAE descriptive Figure 6 export contains **103 individual-by-source-panel profile records**, distributed across five tracking panels:

| Panel | Source panel profile rows | Within-panel distinct source identifiers |
|---|---:|---:|
| E. helvum | 20 | 20 |
| H. monstrosus | 24 | 24 |
| P. hastatus 2022 | 33 | 33 |
| P. hastatus 2023 | 16 | 16 |
| P. hastatus 2016 | 10 | 10 |
| **Total panel-indexed profiles** | **103** | **103 summed within panels** |

But there are only **101 distinct literal `individual` identifier strings across all five panels**: precisely **two source identifiers recur in both the 2016 and 2022 Phyllostomus panels**, at the La Gruta source collection site.

| Repeated source ID | Panel A | Panel B |
|---|---|---|
| `71A0D95` | P. hastatus 2016, La Gruta::2016 | P. hastatus 2022, La Gruta (Colony 1)::2022 |
| `74DDA80` | P. hastatus 2016, La Gruta::2016 | P. hastatus 2022, La Gruta (Colony 1)::2022 |

The labels are *strong candidates for a linked cross-year animal identity*. Calderón-Capote et al. (2025; https://doi.org/10.1371/journal.pone.0313782) report that bats at La Gruta were marked with subcutaneous PIT transponders and that recaptures from 2016 to 2022 were **low**; they also analyze both original source archives. The original O'Mara and Dechmann (2023) individual table contains one of these repeated label strings. These independent source details make actual recapture biologically plausible. **However, an archive-to-PIT identifier crosswalk for both repeated labels has not been independently verified**, so literal string recurrence is not proof of six-year movement-strategy persistence. The original Movebank metadata, source field team or longitudinal PIT registry should be checked before confirming individual-level recapture. Conversely, one cannot honestly claim all 103 panel-indexed records have **103 independent biological individuals across panels** based on the displayed rows.

**Required terminology**: “103 individual-by-panel profiles”, “103 evaluable source-panel records” or “20/24/33/16/10 evaluable individual profiles within panels”; **not** “103 globally distinct bats” or “103 independent individuals”. The original JAE authors' original figure caption and untouched archive are retained as provenance, but new integrative figure/caption text should use the careful terminology.

## Scope of the 684 source-cohort-restricted descriptive pairs

The new Figure S1 compares **only two *different within-panel animal IDs* belonging to exactly the same `panel` and `cohorts` string**. Every panel has distinct within-panel IDs. The 2016 and 2022 source panels are **never cross-compared**, and the repeated labels therefore never create an invalid same-bat-as-two-bats within any of the 684 computed pairs.

However, panels are not guaranteed independent ecological biological replicates of species or of 103 unique animals. Those 684 unordered dyads are also strongly nonindependent because they reuse 103 panel-profile rows in many pairs. Panel-specific original exchangeability tests are unchanged and should not be pooled as if they had species-level or animal-level independence across study years.

## Quantitative implications for manuscript and journal

- JAE original per-panel inferential gates and numerical outputs are unchanged; the completed overlap and calibration tests use source cohort/panel-specific identity sets.
- The overlap metrics describe **vertical probability *shape*** from differently supported horizontal contexts, not 3D habitat co-use.
- The two matching source labels could motivate future **metadata validation** of longitudinal recapture, but cannot be turned into new six-year route-memory/personal-strategy evidence based on current source text or the two profile curves alone.
- Because global animal identity is unresolved, do not treat 103 panel-profile rows as 103 independent biological animals in species comparisons, random effects, regressions or uncertainty estimation.
- Source-data permissions and the human source-investigator verification remain outstanding, so there is no action to merge 2016/2022 subjects in the original frozen sample or retrospectively alter its original permutation null.

## Independent executable guard

`validate_profile_panel_identity_scope_v1.py` verifies the **immutable original CSV SHA256**, all 103 panel-indexed rows, all per-panel distinct label counts, **101** unique cross-panel source identifier strings, exact **two cross-year label repeats** and that no derived overlap dyad compares different original cohorts/panels. It checks for manuscript terminology drift as a publication-integrity gate. This is source annotation/QA, not a new hypothesis test or animal-identity assertion.
