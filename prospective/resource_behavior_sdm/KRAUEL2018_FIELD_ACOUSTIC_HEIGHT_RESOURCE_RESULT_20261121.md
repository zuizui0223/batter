# Krauel 2018: field acoustic resource-height holdout result

## Result

The fixed resource predictor **did not improve mean heldout prediction** of either recorder-height allocation or the acoustic feeding-buzz mark in this source. Adding measured ground moth catches to a calendar-day baseline changed the joint night-equal log score by **-0.004729 nats per recorded pass** under leave-one-night-out and **-0.016650** under the fixed adjacent-pair stress check. This is an actual reanalysis of a published field table, not a simulation.

This closes the previously specified two comparisons. There is no follow-on penalty search, subgroup selection or added predictor to turn the negative mean positive. PLOS2016 also remains closed.

## Source and sample

[Krauel et al. (2018), DOI 10.1139/cjz-2017-0284](https://doi.org/10.1139/cjz-2017-0284), [original-author accepted manuscript](https://krauel.com/publications/Krauel%20et%20al%202018%20CJZ%20early.pdf), Table 1, printed page 29. [USDA bibliographic record](https://www.ars.usda.gov/research/publications/publication/?seqNo115=338052) corroborates the publication and field design. The predictor is daily ground pheromone-trap catch; outcomes are recorded Tadarida brasiliensis passes and buzz-positive passes at three recorder heights. The source is one acoustic site and 13 dates. Three instrument failures leave ten complete nights for our paired comparison.

| Source-table QC | All available observations | Complete nights analyzed |
|---|---:|---:|
| Nights | 13 | 10 |
| Observed night x recorder cells | 36 | 30 |
| Recorded passes | 1,104 | 1,073 |
| Buzz-positive passes | 97 | 95 |

Null instrument cells were preserved and their entire nights excluded. The independent transcription agreed on every row. These are clustered recorded events, not 1,073 independent animals.

**Provenance precision:** the web PDF reader supplied an author-hosted accepted-manuscript table. Direct container retrieval returned HTML; original PDF byte authentication was unavailable. SHA256 `cc85b52cbb8d43fb9d580ae5c859c900d7d806b2d38386452ec53d186971d69e` authenticates the **canonical 13-row transcription**, not a final publisher file. No original PDF, input table, coordinates or animal identifiers are committed.

## Fixed comparison

[The frozen protocol and implementation plan](KRAUEL2018_FIELD_ACOUSTIC_HEIGHT_RESOURCE_FROZEN_20261121.md) was committed at [677efa1](https://github.com/zuizui0223/batter/commit/677efa131705736f860e15ad479f19532ffc4f2e). The table and the authors' conclusions had already been inspected, so this is explicitly **source-open exploratory**. The model/test commit [bff4c6b](https://github.com/zuizui0223/batter/commit/bff4c6be577e37bfea445bea5128a75a4ab1d4ff) preceded the original-table calculation.

The height factor is a three-class symmetric softmax with stratum-specific intercepts and calendar-day slopes. The conditional-buzz factor has stratum-specific intercepts and a shared day slope. Their resource variants add log1p moth catch, separately by stratum for height and as a common slope for the buzz mark. Fixed ridge penalties are 0.01 on intercepts and 0.15 on slopes. Scaling uses training nights only. Each training night has total weight one; each test score is a pass-weighted mean within that night and nights are then averaged equally.

The factorization is

`p(recorder stratum, buzz mark | recorded pass, day, moth index)`

`= p(recorder stratum | recorded pass, day, moth index)`

`  x p(buzz mark | recorded pass, recorder stratum, day, moth index)`.

Both components are scored on the same events. No ground or airborne count is converted to an hourly rate using the study-wide mean duration. No fecal-diet indicator is used as resource availability. The complementary buzz category is precisely a pass outside the table's complete-buzz numerator; it is not a known-assessed biological nonfeeding event.

## Exact heldout results

Positive values would favor adding the ground moth index. The two split designs reuse the same ten nights; they are not independent replications.

| Comparison | Mean height gain | Positive folds | Mean buzz-given-height gain | Positive folds | Mean joint gain | Positive folds |
|---|---:|---:|---:|---:|---:|---:|
| Leave one night out; 10 folds | -0.004403806 | 6/10 | -0.000325473 | 5/10 | -0.004729279 | 6/10 |
| Adjacent chronological pairs; 5 folds | -0.014254203 | 2/5 | -0.002395796 | 2/5 | -0.016649999 | 2/5 |

Units are natural-log score per recorded pass, averaged equally over nights. Six primary folds had a positive joint increment, but the larger losses in other folds made the mean negative. The result is therefore not a claim that every night was worse.

All four fixed joint candidates can be inspected directly:

| Joint model | Leave-night-out score | Adjacent-pair score |
|---|---:|---:|
| Calendar-day baseline in both factors | -1.400164105 | -1.434631396 |
| Moth index added to height only | -1.404567911 | -1.448885598 |
| Moth index added to buzz only | -1.400489578 | -1.437027192 |
| Moth index added to both | -1.404893384 | -1.451281395 |

Higher scores are better. The joint increment equals the sum of height and conditional-buzz increments. Absolute scores must not be numerically pooled with PLOS target-relative heights, Ducke captured-guild fractions or Hendel activity losses, which have different responses and sampling units.

The authors had already reported no explanatory relationship between the ground-trap index and their altitude activity index (p=0.86); their positive association involved diet richness. Our contribution is the fixed heldout-night comparison and its predictive decomposition, **not discovery of a previously unknown absence of a prey effect**. This reanalysis neither contradicts the paper nor independently replicates its biological conclusions.

## Verification

- Eighteen synthetic/input-contract tests passed before the first source fit: missing-versus-zero handling, counts, duplicates, feature exclusion, constant-resource control, designed height/buzz signals, per-night rescaling invariance, probability normalization and hand-calculated log scores.
- A separate NumPy/SciPy BFGS implementation was written from the frozen equations without importing the production engine. Across 15 folds, **195 fold-level comparisons and 18 aggregate comparisons** all met the fixed 1e-7-nat tolerance. The maximum absolute difference was **4.357141314415003e-10 nats**; all positive-fold counts agreed.
- The independent verifier fit 60 models. Its maximum absolute gradient was **1.4562954335346182e-10**, below the 1e-8 convergence gate. SciPy marked two fits with precision-loss messages at its tighter requested tolerance; both met that independent gate and agreed with the Newton result. No scientific model settings changed.
- Direct six-category scoring and the sum of the two component gains differed by at most **2.7755575615628914e-16** per night.
- Reference script SHA256: `089610c2c29f9f78c0f8372282b270e2dd7d8b112a26522d0bcb9cf480af4745`; reference output SHA256: `38a15b75ce55fcff0378aecc0295dfc691d20a8c4cbde08bed667dc33e3e91ca`. Versions: NumPy 2.3.5, SciPy 1.17.0.
- Final branch-wide Python 3.10/3.11/3.12 CI and independent review are recorded in [Draft PR #102](https://github.com/zuizui0223/batter/pull/102). CI checks software and claim boundaries; it does not download or authenticate original source bytes.

The [aggregate machine-readable receipt](krauel2018_field_acoustic_height_resource_receipt_20261121.json) includes all ordinal fold gains, numerical verification and explicit null fields for unsupported claims. The [production engine](krauel2018_acoustic_height_resource_v1.py) accepts a private, digest-checked JSON transcription via `--table-json` and emits an aggregate receipt via `--output`; it uses only the Python standard library.

## Interpretation and remaining boundary

This establishes a working **measured ground-prey index x recorded vertical stratum x acoustic feeding-mark** evaluation within one wild study. It does not establish improved prediction for that source under the frozen models. It cannot identify a zero ecological resource effect: the night sample is small, the resource index may mismatch what bats encounter aloft, and unmeasured conditions remain.

Recorder stratum is not each animal's true flight altitude, the ground catch is not height-resolved prey density, buzz absence is not verified transit, and effort/detection are uncalibrated. One site's selected autumn dates provide neither geographical validation nor an individual resource-height join. Calendar day is adjusted, weather is not. Same-night trap catches do not support a real-time forecast claim. All original `strict_unestimated` fields remain null; no ecological SDM, individual altitude policy or causal gain is promoted.

### Source access needed for the next height-resolved resource test

[Cistrone et al., DOI 10.1016/j.foreco.2026.124382](https://www.sciencedirect.com/science/article/pii/S0378112726008807) lists measured ground/canopy insects and bat activity from 20 plots, with data in Supplementary S1/S2. The public page identifies a January 2027 issue; it was already indexed and discoverable at this 2026-11-21 audit. Original supplements and join keys were not opened because the available publisher routes returned 403. Those two original supplements, bundled into one upload, are the concrete next input. Eligibility still depends on their actual site/stratum/date/effort fields, not on the abstract.

[Srilopan et al. (2026), DOI 10.1007/s10531-026-03307-x](https://link.springer.com/article/10.1007/s10531-026-03307-x) has measured prey and acoustic samples at five heights, but explicitly provides numerical data by author request. No contact was made. Neither source is counted as an empirical success here.

## Execution decisions

The project uses a remote Draft branch and local staging files rather than a local git checkout, so commits used GitHub tree/commit operations with an expected-head lease. The user's action-first instruction supplied continuation authority; no additional approval pause was inserted. The accepted-manuscript table version and lack of PDF byte checksum were preserved rather than relabeled as a final publisher dataset. The protocol and model family did not change after fitting.

Protected main branches and frozen JAE/BE manuscripts remain outside this change. 


### Independent review and correction

The independent reviewer re-extracted every source-table row and verified the canonical digest, reproduced the engine receipt, and identified one material direct-call scorer weakness: empty or malformed distributions could be silently truncated by `zip` or produce invalid positive scores. The defect was reproduced with failing regression tests. The scorer now rejects invalid count pairs, wrong prediction shapes, nonfinite/positive log probabilities and unnormalized distributions (log-normalizer tolerance 1e-10), while retaining legitimate finite extreme log support. No fitting equation, sample, penalty or split changed. Replaying the private input after this correction reproduced **every original engine-generated value exactly**. All **21 focused tests pass**.

The review also exposed a test-fixture weakness: the second factor's heldout-outcome test reused a mutated record. This was treated as a material coverage gap and corrected so each factor starts from a fresh record. The current test verifies both predictors exclude the heldout outcomes. There are no unresolved Critical/Important findings or deferred code-polish items.

**Scope rulings:** original-PDF byte authentication remains unavailable; the reproducible claim is restricted to the independently crosschecked accepted-manuscript transcription, with possible differences from the final version of record untested. Remote final-head CI and Draft state are verified separately on PR #102 after integration. Those limits do not justify changing a field result or promoting the table to individual GPS evidence.
