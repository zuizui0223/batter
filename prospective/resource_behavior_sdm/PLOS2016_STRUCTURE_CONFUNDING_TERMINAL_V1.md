# PLOS 2016 experimental flower-vs-sham: terminal strict LOBO gate and confounding counterexample

2026-11-20 | [source gate run #44727854884](https://github.com/zuizui0223/batter/actions/runs/44727854884). **No X/Y/Z source values have been opened.**

## Exact source-only outcome

Official original DOI `10.1371/journal.pone.0163492.s001`, original SHA256 `3cce76e3f75c1eb49ac1a8344880a42da1de163886372a944080e074cdd1fb42`. Verified 3,226 row records with usable Bat/Target/Test labels; 5 bats, 2 target categories, 15 source sequences per category, **30 source trial groups**. However the **Bat×Target pairing is incomplete**: only 8 of 10 combinations, three bats have both categories, two appear in only one, per-bat trial totals 3/3/8/8/8. Five pair cells have three trials each, three have five. These were all examined **without numeric XYZ or target-distance values**. No original bat IDs, target values or coordinates were persisted.

**Frozen 5-bat fully paired LOBO gate FAIL**: do not reinterpret this as 5 balanced paired-target bats or score a pooled frame-level target effect as five independent contrasts. The source manuscript's described n=5 and 15 approaches per target is not evidence that S1 presents exactly three sequences from every bat in both target types. This does not imply an error in the original paper: source reconstruction selection/labelling may differ from its experimental sampling denominator.

## A mathematical warning with the identical source margins

`plos2016_target_confounding_counterexample.py` defines one **synthetic** 5-bat, 30-trial, 15/15 target distribution with the **same 8 bat×target-pair support** and 3/3/8/8/8 totals. Every synthetic bat uses one height bin in *both* targets; the true target effect is exactly zero. Two bats that only appear in one target have low height, and three with both target categories have high height in both.

The resulting pooled, *noncausal* target–height mutual information is **0.1638965900 nats**, even though **I(Target;Height | Bat) = 0** by construction. Thus a positive target-conditioned pooled-information statistic can be entirely induced by bat-composition differences. This is a mathematically explicit identifiability counterexample, **not** an estimate or explanation for the original bats.

A separate future study using only the three structurally paired bats would have a minimum possible one-sided exact signflip p of 1/8 = **0.125**. Such a study may be exploratory, but cannot meet the original 0.05 bat-level criterion and must not be used to rescue the five-bat pre-outcome gate after seeing this pairing.

## Ecological decision and next source target

Retain the S1 original for general source method comparison, not as a confirmed population-general resource×flight-height SDM. The more ecologically direct Goldshtein et al. (2020) flower abundance × tracked 3D bats is DOI `10.17632/jxghjjsttw.1`, but publisher API requires OAuth and returned HTTP401 in the original source gate; no original bat-height-to-flower join is open or fitted. The previous NeoBat source-rank shadow S3–S1 remains negative, the true partner M3–M1/N1 remains unfitted, and the five-panel bat individuality results remain distinct source-specific evidence.

Do not relabel a controlled acoustic/scent target as measured fruit abundance. No existing frozen JAE or BE result is modified.
