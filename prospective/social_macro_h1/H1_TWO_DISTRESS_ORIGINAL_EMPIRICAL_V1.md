# H1 distress-call context reanalysis: TWO original sources, no macro overclaim

**2026-11-19.** Both original public sources were checksum validated and the source-pinned pre-outcome contracts were executed. These are *published behavioral discoveries* reanalyzed under conservative observational-unit rules. They are **not** newly performed bat experiments, a global species-general effect, or evidence of reciprocity/personal memory. Frozen `batter` JAE and `main` remain unchanged.

## Source 1: 2016, context and caller identity

Eckenweber & Knörnschild 2016 [Royal Society Open Science](https://doi.org/10.1098/rsos.160151). Original supplementary XLSX obtained using official [Europe PMC REST](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4892459/supplementaryFiles), SHA-256 `28402ac6c969f7a6c13acf5f90192afbfa4b6c5158e1bbc8f657b55f255b05ef`. Original 114 observations = 19 independent **session labels** × 3 locales × 2 vocalizers, fully matched. The source authors describe 11 physical colonies, eight revisited in two years. The 19 labels in the sheet do **not** identify which eight physical colonies were revisited.

Means of **reaction minus pre-observation** in original echolocation-call-count scale, response S. bilineata:

| Caller | Within colony | Close to colony | Foraging site |
|---|---:|---:|---:|
| S. bilineata conspecific distress | +30.97 | +24.82 | −12.63 |
| M. molossus heterospecific distress | +3.21 | +1.26 | −1.13 |

The **predefined call identity × location contrast** [(conspecific−heterospecific) at roost] − [(conspecific−heterospecific) at foraging ground] is **+39.2579** calls in the original response scale, positive in 14/19 session labels. The comparable *close-minus-foraging* contrast is **+35.0474**, positive in 14/19.

**Strong mathematical partial-identification result, not an inferential p-value**: If 19 sessions arise from exactly eight physical colonies observed twice plus three observed once, then *for any valid unknown session-to-colony assignment*, the equal-11-colony mean of the roost-specificity contrast must lie between **+22.7682 and +56.2909**. The corresponding close-foraging range is **+17.0136 to +49.0182**. Thus the mean sign is invariant to possible pairings under the published repeat-count assumptions. It does not follow that a formal clustered uncertainty interval would exclude zero or that speaker location was randomized.

For the original authors' **conspecific-only roost-minus-foraging** contrast, 19-session mean **+43.60**, 13/19 positive; all possible equal-colony means are **+30.7182 to +57.6318**. This verifies a robust descriptive component of the original prior art.

Critical limitations: (i) unknown physical colony/year mapping precludes 11-colony p-values; (ii) speaker *location order* varies with dawn/dusk, so ecology can be confounded with time/order and different initial activity; (iii) *M. molossus* distress sound is **not** a silent negative control and the experiment did not manipulate resource abundance; (iv) detection calls are not independent marked individuals.

## Source 2: 2015, distress calls versus noise

Carter et al. 2015 [PLOS ONE](https://doi.org/10.1371/journal.pone.0136146) original [Figshare v2 CSV](https://doi.org/10.6084/m9.figshare.1454597.v2), exact source MD5 `991be124c47f48a955fa5a0a40dd864c`. 308 playback sequences, 155 M. molossus distress and 153 pink-noise, spanning 12 session codes and eight published physical sites (site crosswalk not in table). Unlike 2016, this has *noise* playback as the control; it does not compare the caller identity of two different bat species.

Primary **retain-all-trials** per sequence response is playback passes minus quiet passes. Both target recipient species have positive mean distress-minus-noise contrasts, but the 12 session effects are heterogeneous:

| Responding species | Equal-session mean (passes per playback minute) | Sessions with positive contrast |
|---|---:|---:|
| M. molossus | +0.54936 | 9/12 |
| S. bilineata | +0.25371 | 6/12 |

At the whole-sequence level, mean `D_distress−D_noise` for M. molossus is **+0.50441**, and for S. bilineata **+0.31187**. These are *not* species-independent replications and no eight-site p-value is identified without site–session crosswalk.

**Selection sensitivity:** author-style removal of both pre=0 and playback=0 recordings retains only 116 M. molossus and 59 S. bilineata trials. Distress-minus-noise contrast of the filtered means becomes **+1.25913** and **+1.66667**, respectively, versus all-trial contrasts +0.50441 and +0.31187. The larger magnitudes reflect a different response-selected sample; this check neither disproves the original study nor licenses replacing the original target post hoc.

## Geographic non-independence correction (mandatory)

**Both source studies were conducted at the same Smithsonian Barro Colorado Island field station, Panama**, not at independent landscapes: Carter et al. (2015) used eight M. molossus field sites at the BCI station; Eckenweber & Knörnschild (2016) repeatedly sampled 11 S. bilineata colonies on external walls of the same station during 2012–2014. **Published source papers do not provide a reconciled physical site/year identity crosswalk**, and some individual animals / local activity conditions may be shared. These are two distinct published experimental datasets with different response contrasts, but they must NOT be counted as independent **geographic population** replicates or as evidence of generalization to a new region. They were not scientifically independent sites merely because the papers have different years, stimuli or samples.

Sources: https://pmc.ncbi.nlm.nih.gov/articles/PMC4892459/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC4564210/ .

## Cross-study and novelty assessment

2016: a location/caller conditional ecological context *within one species*. 2015: a distress-vs-noise contrast in a two-recipient community under a different cue and observation process. They jointly reinforce **the need to distinguish sender identity, signal meaning, patch/roost setting, and observation opportunity**, but are not commensurate effect-size replications. Both response patterns have been published; the added derived novelty here is *source QA, unit-respecting reanalysis and a mathematically bounded 11-colony mean under unknown mapping*, not a new ecological law.

Also, these studies do NOT externally replicate the 2019 Lewanzik graded feeding-buzz × pre-playback-activity moderator. Wilson et al. 2026 showed signed attraction/avoidance/no-detectable-response for four bat taxa but original event-level raw denominators are not yet checked; do not count the abstract as negative trials or a positive meta-analytic sample.

**Current stop:** No standardized multi-study meta-effect or phylogenetic H1 coefficient; no 11-colony test p; no transfer claim to new countries. Instead, a source-verified evidence hierarchy (two additional original archives, explicit experimental contrasts, varying between-unit conclusions) is now ready for inclusion in a review or a genuinely prospective new database screening plan.

**Executed on independent runner:** https://github.com/zuizui0223/batter/actions/runs/44464841326 . The GitHub artifact contains **derived contrasts only**, no original raw audio or Excel/CSV.
