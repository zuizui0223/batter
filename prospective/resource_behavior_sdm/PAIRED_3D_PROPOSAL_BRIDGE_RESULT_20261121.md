# Bridged 3D M0–M3 benchmark: sampled-control proposal correction (2026-11-21)

**Status: source-free methodological extension only. No authentic Goldshtein GPS or night-matched flowers have been opened; empirical resource-conditioned height gain remains NOT ESTIMATED.** This lives only on prospective draft branch in batter PR #102. No JAE/BE or main modifications.

## Concrete implementation

Updated [paired_3d_ssf_resource_benchmark_v1.py](paired_3d_ssf_resource_benchmark_v1.py). The *same original nested M0–M3 estimation and paired joint/horizontal/conditional-height heldout scoring* now has two explicitly different modes:

1. **enumerated_xy_z (default, backward compatible)** — complete prespecified finite XY × height lattice, no duplicated endpoint and matching height support across XY; candidate score contains only 3D movement/habitat/resource/state terms. Its horizontal/height projection is an exact probability split of this finite candidate set, **not** a validated species-range occupancy SDM.
2. **known_q_sampled_controls** — one observed endpoint plus independent endpoint controls from known/frozen q, which can repeat endpoints or omit part of the XY × height candidate space in a step. Every nested M0–M3 candidate logit includes log(reference mass) minus log(proposal mass), under the **specific one-observed-p + iid-q-controls conditional-label likelihood**. No silent use of uniform candidate scores. A test-choice risk set must be identical across nested models; observed endpoint may not be used to construct or adapt q.

The fixed-ridge conditional softmax optimizer and bat/night/step balanced heldout evaluation are shared, not duplicated. For a sampled risk set, the exact identity

    log P(label j | candidate choices)
      = log P(observed label at XY(j) | choices)
        + log P(label j | observed XY(j), choices)

still holds, so all three increments compare the **same target labels**. These horizontal/height contributions are specifically **conditional on the sampled candidate set**, and must **NOT** be relabelled as ecological location intensity and height density across the full study area. To generate a regional animal-use/SDM probability map, a separately normalized continuous movement/use/detection or occupancy model is needed.

## Source-free acceptance tests

New [test_paired_3d_sampling_proposal_bridge_v1.py](test_paired_3d_sampling_proposal_bridge_v1.py):
- **Backward compatibility**: when q=reference measure on the complete grid, matched M0/M1/M2 score increments in both modes agree to 12 decimal places.
- **Nonuniform sampled controls**: resample eight controls per step from a site-dependent but fixed q over original six XY × height endpoints; repeated endpoints are legal. Run whole-site heldout scoring of M0/M1/M2 using training-only coefficients and q offsets; a constructed resource×height effect must improve height-given-XY label score. This is *simulation only*.
- **Sampling mode gates**: reject missing/zero/invalid q or reference mass, q purportedly fit on test endpoints, nonuniform sampled controls mislabelled as a complete grid, an unrecognized sampling mode and fake measured-food provenance.
- **No new empirical claims**: output always records original-source authentication unverified and a null empirical resource-height gain claim, even if a simulation generates a positive score.

For sampled controls the appropriate q over the full *unobserved* choice domain cannot be verified merely from a table of sampled candidates. A boolean provenance flag by itself is **not authentication**. A real-data adapter must pin original source files, GPS fixes, regular sampling, 3D move/end-point support, source-specific proposal construction and q positivity before this benchmark becomes eligible for biological interpretation.

## Scientific limits and dependency

The comparator is still a **finite matched case-control step-label model**, not Klappstein et al. (2026) [ssf3D](https://github.com/NJKlappstein/ssf3D)'s actual continuous 3D-SSF, sampling corrections or an integrated resource-conditioned regional bat SDM. In particular, the current implementation does not fit sensor-noise likelihood, habitat detection, or model the true continuous integral over accessible 3D volume.

The original Goldshtein et al. archive, [Mendeley Data 10.17632/jxghjjsttw.1](https://doi.org/10.17632/jxghjjsttw.1), remains publisher-API inaccessible (official original gate HTTP 401). The official public page displays the dataset and "Download All" but its browser-extracted HTML does not give a file roster. The published cactus locations for eight tracked bats are distinct from repeated flowering observations from 414 cacti; a dated resource–flight-height join is unverified. If the original source becomes readable, separate Stage A cactus position (stable habitat proxy) from Stage B actually dated flowers; do not use altitude-defined visit labels (height under 20 m) as independent behavior predictors. The real biological M2−M1 and M3−M2 effects remain NULL.

**Next methodological priority after bridge:** quantify horizontal and vertical scores under known measurement error in GPS AGL, distinguish observer/sensor errors from true within-state resource-driven height selection, and compare against a formally comparable continuous 3D-SSF baseline. Do not introduce new biological datasets/claims by imputation.
