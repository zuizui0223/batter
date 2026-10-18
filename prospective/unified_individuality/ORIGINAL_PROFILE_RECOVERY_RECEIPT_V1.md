# Original JAE Figure 6 individual 3-D profile — recovery receipt v1

**Recovered:** 2026-10-14  
**Status:** ORIGINAL FROZEN SOURCE ARTIFACT RESTORED AND CHECKSUM VERIFIED — descriptive-only; no new biological analysis.

## Immutable origin

- Original repository: \`zuizui0223/batter\`.
- JAE original descriptive workflow run: **36375056204**.
- Original archived artifact ID: **10950667566**.
- Original artifact name: \`centered-shape-profile-descriptive-v1\`.
- Original source script: \`scripts/build_centered_shape_profile_descriptive_v1.py\` on JAE \`release/jae-v0.4.0-rc2\`; blob SHA \`7040e110de738766683c3cc06797a191dd4ff29e\`.
- Contract: \`contract/centered_shape_profile_descriptive_v1.json\`, frozen before opening descriptive profile outputs.
- Original result receipt: \`CENTERED_SHAPE_PROFILE_DESCRIPTIVE_RESULT_V1.md\`.
- Restoration CI run: [38507348011](https://github.com/zuizui0223/batter/actions/runs/38507348011), **PASS**.
- Imported into integration branch by narrowly scoped original-artifact restore workflow: \`.github/workflows/unified-restore-original-profile-v1.yml\`.

## Exact source file checksums

| Source archived path | Local integrated copy | Original bytes | SHA256 |
|---|---|---:|---|
| \`results/centered_shape_individual_profiles_v1.csv\` | \`figures/original_jae/centered_shape_individual_profiles_v1.csv\` | 34,609 | \`91cae4c22588db0976dfe3e273eabebaa89dc2844e996f42d01ef617672dc3f8\` |
| \`results/centered_shape_individual_profiles_v1.json\` | \`figures/original_jae/centered_shape_individual_profiles_v1.json\` | 78,654 | \`9efd5d2914ad012905a004aee1114d715deaaf94e3f54689deb4f1208a188cb2\` |
| \`figures/submission_v0_3_7/figure6_individual_centered_shape_profiles.png\` | \`figures/original_jae/figure6_individual_centered_shape_profiles.png\` | 190,935 | \`654350e40124f0b3e9430c594adc71ae4e4688c31ac78f633c5797b3b3297009\` |

**Do not alter these original files** to improve the appearance or significance of the results; any rescaled/reskinned version must be separately named and provenance recorded.

## Source data integrity

- **103 biological individual profiles** exactly:
  - *Eidolon helvum*: n = 20;
  - *Hypsignathus monstrosus*: n = 24;
  - *Phyllostomus hastatus* 2022: n = 33;
  - *P. hastatus* 2023: n = 16;
  - *P. hastatus* 2016: n = 10.
- Ten frozen bins of **session-median-centered residual height** per individual: below −400, −400 to −200, −200 to −100, −100 to −50, −50 to 0, 0 to 50, 50 to 100, 100 to 200, 200 to 400 and above 400 metres.
- The restored workflow checked file hashes, 103 profiles, exact panel counts, ten bins, each row's probability sum equal to one (tolerance 1e−9), summary central/lower/upper masses and the source \`new_hypothesis_test=false\` claim boundary.
- These profile rows reconstruct the original **leave-one-session-out, same-common-cell-weights self-predictor**, averaged equally within biological individual. They are *not* direct unweighted frequency histograms from raw GPS fixes.
- Rows in each panel are ordered by displayed upper-tail probability and each source panel shares the original heatmap's same color scale.

## What this restores to the integrated publication

**Figure 5A:** unified SVG showing six original panel-specific calibrated centered-shape identity results (five comparative PASS and the *Tadarida* boundary FAIL).

**Figure 5B:** the **exact original JAE descriptive figure** restored here as PNG, showing all 103 individual probability profiles in the five comparative panels. It was not synthetically regenerated from a summary or inferred from panel-level statistics.

Together they let the reader see the inferential full-distribution identity and the biological appearance of the estimated profile heterogeneity.

### Mandatory limits for the figure caption

1. The component-wise apparent ranges of central concentration and upper/lower tail mass are **descriptive only**, not separately exchangeability-calibrated; displayed between-individual range can include finite-session estimation noise.
2. The heatmap does not establish behavioral state, strategy classes, food choice, learned routes, performance optimality, ecological fitness or causal memory.
3. The visible descriptive profile differences do not establish which component carries the inferential whole-profile identity signal.
4. Additive height offsets have been removed by session centering; nonadditive tag/device error variance is still possible.
5. Figure 5B omits *Tadarida teniotis* by original frozen descriptive contract because its centered-shape primary is unsupported.

**Publication status:** image source completeness restored; a harmonized printable multi-panel Figure 5 package and final visual/source check remain editorial work, not new scientific inference.
