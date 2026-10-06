# Attrition and missing-data contract v1

## Status

**PROSPECTIVE FAIL-CLOSED MISSINGNESS RULE.**

This contract applies after treatment randomization and before any confirmatory common-OPEN outcome is interpreted.

Parent:
- PREREGISTRATION_CONTRACT_V1.md
- RANDOMIZATION_AND_INTERFERENCE_GUARD_V1.md

## 1. Why attrition is dangerous here

Treatment is assigned within four-animal randomization blocks.

If one randomized animal disappears after treatment exposure, simply analyzing the remaining animals changes the assignment space and can destroy the exact randomization guarantee.

Therefore post-randomization attrition is not handled as ordinary complete-case missingness.

## 2. Pre-randomization exclusion

All capability, health and structural eligibility exclusions occur before treatment randomization.

Animals excluded before randomization:
- do not enter the confirmatory estimand;
- do not count toward the randomized N;
- may be replaced before the randomization schedule is frozen.

## 3. After randomization but before any acquisition exposure

If a randomized animal becomes unavailable **before receiving any randomized acquisition treatment**:

- the affected four-animal block is void;
- none of the four assignments in that block are used;
- the block may be replaced only by a newly enrolled complete four-animal block;
- the replacement block receives a new block ID and a new independently generated assignment under the same frozen script and seed-extension rule.

The original void block remains archived.

No individual slot replacement inside a partially randomized block.

## 4. After first randomized acquisition exposure

Once any animal in a block has begun randomized acquisition exposure, the block is locked.

If any animal in that block later lacks the primary endpoint for any reason:
- the block is **post-treatment incomplete**;
- it cannot be silently dropped from a clean confirmatory analysis;
- no new animal may replace the missing animal in that block.

## 5. Clean confirmatory criterion

A **clean confirmatory causal claim** is authorized only if:

- at least 4 complete randomized blocks remain;
- every animal in those retained blocks has both family-specific primary scores;
- there are **zero post-treatment incomplete blocks** among randomized blocks intended for the confirmatory experiment.

Thus, if any randomized block becomes incomplete after treatment begins:

> **CLEAN CONFIRMATORY STATUS = STOP.**

The observed treatment contrast may still be reported as an attrition-complicated analysis, but not as the preregistered clean causal result.

## 6. Attrition-complicated analysis

If post-treatment attrition occurs:

Report:
- animal ID;
- block;
- treatment assignment;
- stage of loss;
- reason for loss;
- whether reason was plausibly treatment-related;
- all available pre-loss data.

Then report the complete-block randomization result only as:

**ATTRITION-COMPLICATED SENSITIVITY ANALYSIS.**

Do not use it to claim the clean confirmatory causal effect.

No inverse-probability weighting, imputation, model-based rescue, or missing-not-at-random sensitivity model may be promoted to replace the failed clean primary unless independently preregistered before outcome opening.

## 7. Trial-level missingness within an otherwise retained animal

The primary family-specific score requires a frozen minimum number of valid common-OPEN trials in both early and late probe halves.

Exact minimum:
**TBD BEFORE OUTCOME OPENING**.

If an animal fails the primary trial-support minimum in either family:
- that animal lacks the primary endpoint;
- its block becomes post-treatment incomplete;
- clean confirmatory status STOPs under Section 5.

Do not:
- borrow later trials to fill an early window;
- extend the probe adaptively;
- change early/late split;
- lower tracking-quality criteria.

## 8. Technical failure before treatment exposure

If a technical failure occurs before any randomized acquisition exposure and makes a block unusable:
- void the complete block;
- archive the reason;
- replace only with a new complete block before outcome opening.

If technical failure occurs after treatment begins, use the post-treatment rule.

## 9. Health / welfare withdrawals

Animal welfare always overrides the statistical design.

Withdraw an animal whenever required.

Statistical consequence:
- if before treatment: block can be voided and replaced as above;
- if after treatment: clean confirmatory status STOPs.

No animal should be retained in the experiment to preserve a statistical block.

## 10. Planning implication

Because clean inference requires complete randomized blocks, enrollment should target at least five complete blocks (20 evaluable animals) even though four complete blocks (16 animals) is the minimum inferential structure.

If attrition risk is nontrivial, recruit reserve animals **before randomization** so that a full replacement block can be formed if a block voids before treatment begins.

Reserve animals cannot repair post-treatment attrition.

## 11. No outcome-dependent exclusions

After randomization, do not exclude an animal because of:
- unusual route choice;
- weak individuality;
- extreme I/M score;
- poor fit to the expected policy model;
- apparent nonlearning;
- unfavorable treatment contrast.

Only frozen structural support and welfare/technical rules apply.

## 12. Claim labels

Use exactly:

- **CONFIRMATORY_CLEAN** — all clean criteria satisfied;
- **STRUCTURAL_STOP** — fewer than four complete valid blocks before treatment analysis;
- **ATTRITION_STOP** — any post-treatment incomplete randomized block;
- **ATTRITION_COMPLICATED_SENSITIVITY_ONLY** — optional descriptive/sensitivity result after ATTRITION_STOP.

No softer wording should obscure these states.
