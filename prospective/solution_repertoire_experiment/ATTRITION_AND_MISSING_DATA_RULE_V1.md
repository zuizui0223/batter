# Attrition and missing-data rule v1

## Status

**PROSPECTIVE CONFIRMATORY MISSING-DATA RULE.**

This rule is frozen before confirmatory randomization.

## 1. Unit-level endpoint completeness

An animal is primary-endpoint complete only if it has the full frozen number of policy-valid common-OPEN probe flights in **both** matched families A and B.

Replacement attempts are allowed only within the frozen attempt ceiling.

No imputation.

No shortening of one family/window.

No using unequal early/late windows.

## 2. Post-randomization incomplete animals

If a randomized animal is endpoint-incomplete:
- retain that animal in the archived randomization schedule;
- do not delete or redraw its treatment assignment;
- do not replace it with a new animal under the same randomization slot;
- exclude its missing primary contribution from the statistic for **every** allowed randomization assignment.

The set of endpoint-complete animals is therefore held fixed across the exact randomization distribution.

## 3. Preserve the original assignment space

Do not drop entire randomization blocks merely to restore balance.

Enumerate the legal treatment assignments from the **original frozen randomized cohort**.

For every legal assignment:
- map OPEN versus CONSTRAINED family for all originally randomized IDs;
- calculate Delta_A only over the same frozen endpoint-complete subset.

Reference code must support this architecture.

## 4. Attrition gates

Clean confirmatory interpretation requires:
- >=16 endpoint-complete animals;
- <=10% post-randomization endpoint incompleteness;
- no more than one endpoint-incomplete animal in any original four-animal block.

If >=16 remain but attrition is >0 and <=10%:
a positive primary is labelled **SUPPORTED_WITH_ATTRITION** unless the attrition-sensitivity audit shows no material vulnerability.

If:
- <16 endpoint-complete animals;
- >10% endpoint incompleteness;
- or >=2 incomplete animals occur in the same original block;

return:
**STRUCTURAL_STOP_ATTRITION**.

No threshold relaxation.

## 5. Attrition-sensitivity audit

If any randomized animal is endpoint-incomplete, report:

1. counts by original randomized OPEN family;
2. counts by starting-family order;
3. counts by block;
4. reason for incompleteness;
5. timing of incompleteness;
6. whether incompleteness occurred before or during the common-OPEN probe.

No causal claim that missingness is treatment-independent is made from balance alone.

## 6. Claim boundary

Exact randomization inference with a fixed observed subset conditions on that subset.

If missingness is itself treatment-affected, conditioning may not fully recover the original causal estimand.

Therefore any attrition weakens the claim.

The strongest clean causal result requires complete primary endpoints for all randomized animals.

## 7. Prohibitions

Do not:
- remove a block because its treatment contrast is unfavorable;
- replace missing animals after treatment assignment;
- choose complete cases separately for each permutation;
- impute I/M from acquisition trials;
- use later probe flights to fill a failed frozen primary window;
- redefine valid tracking after attrition is observed.
