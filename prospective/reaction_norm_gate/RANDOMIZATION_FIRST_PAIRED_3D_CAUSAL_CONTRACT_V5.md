# Randomization-first ecological identifiability gate V5 — potential outcomes, not recycled residuals

**PRE-OUTCOME METHODOLOGICAL CONTRACT, 2026-10-08.** New independent experiment concept and synthetic test only. No actual bat measurements or trajectories analyzed. Retains JAE, frozen PR #79, previous #95 math and acoustic bench gate #93.

## The reason for this switch

The executed V4 simulation proved that independently sign-flipping four-feature bat×environment residuals after estimating the *same-sample* environment mean violates the deterministic constraint that centered residuals sum to zero. A method that requires externally known mean context conditions or exact residual symmetry is unsuitable as a drop-in to the available five-bat archive.

Instead, a future study can make the intervention randomized **by design**. A genuine treatment-label swap within a prespecified matched pair is valid for the **sharp null of no effects on either potential outcome**, even when baseline bat and context means are completely unknown and individual noise variances differ. This is not the earlier after-the-fact bat-label exchangeability null.

## Prospective paired challenge design (not permission for real experiments)

For each physical bat i across genuinely independent sessions s, define a *pair of matched opportunity trials* with two physically equivalent trial slots j ∈ {0,1}. Independently and fairly randomize whether challenge c=1 is applied in the first or the second slot, so one challenge and one verified reference are present in every pair.

Before observing outcomes:
- establish and freeze the **one** 3-D context intervention: obstacle geometry / number of safe routes / sensing mask, not interchangeable mixtures of different interventions;
- verify physical/audio apparatus equivalence at the same anchor route (see #93), safety and carryover/washout;
- block by physical bat×independent session, record actual assignment probabilities and time/order slot and confirm no interference or spillover between matched trials;
- freeze one interpretable primary response (e.g. task success per verified trial, or flight intensity, but do NOT choose a favorable one from several outcomes);
- balance baseline geometry, reward and target properties, observe independently calibrated sensor output and distinct real bat identities.

Potential outcomes for slot (i,s,j) are Y_isj(0) and Y_isj(1). For the sharp null, **all** Y_isj(1)=Y_isj(0), so the observed two outcome values in a block remain fixed under every legal randomized assignment. If the first slot's treatment assignment was randomized, let d_is = observed slot0 outcome - observed slot1 outcome. The signed challenge-reference contrast is D_is=(2Z_is0-1)d_is.

For a prespecified equal-bat average endpoint:
  T = (1/N_bats) Σ_i (1/S_i) Σ_s D_is,
where the S_i genuine independent blocks are **not** repeated frames. Enumerate all 2^(Σ_i S_i) legal treatment assignments for small schematic examples. Under sharp no effects, use the empirical assignment distribution of T for an exact one-sided or two-sided p-value; there is no need to know μ_e or impose bat-exchangeable σ_i.

## Proof by randomization rather than Gaussianity

Conditional on observed fixed potential outcomes under Fisher's no-effect sharp null and independently fair within-pair treatment flips, every assignment in the experiment's assigned support is equally likely. Hence under H0 the rank/tail probability of a randomly realized T is super-uniform (ties make it conservative). This holds for **any fixed bat-specific baseline differences/variances**, because the null is about assigned treatment, not exchangeability of bats.

Published prior art:
- Rosenbaum (2010) matched pair randomization and Fisher sharp null methodology (not a novelty of this research).
- Wu & Ding (2021) JASA, doi:10.1080/01621459.2020.1750415 distinguish sharp null and weak mean-zero null; weak-null testing requires further safeguards.
- Caughey et al. (2023) JRSSB, randomized treatment effect quantile/bounded nulls, demonstrates inference beyond sharp null has distinct methods.

## Explicit limitations

1. **Rejecting the sharp no-effect null does NOT establish heterogeneous or enduring personal policies.** All bats could respond identically to treatment. The test detects *some* effect, not its distribution.
2. It is NOT by itself a calibrated test of the **weak null** that the average intervention effect is zero. General treatment-effect heterogeneity is not sharp; missing potential outcomes cannot be imputed solely from mean-zero.
3. It is NOT an exact test of "each bat has a different response"; that requires genuinely independent replicated bat-specific challenge contrasts, test/validation splitting, bat-level uncertainty, a heterogeneity estimator and appropriate randomization/measurement structure.
4. The matched-pair valid-assignment assumption is **non-negotiable**. If experimental condition changes the paired trial via learning/carryover, shared food rewards, sonar adaptation, stress, or interacting simultaneously flying bats, the two trial outcomes depend on prior assignment or other bats. The simplistic independent paired swap no longer matches the actual randomization/potential outcome design.
5. A significant bat-specific performance change alone does not prove adaptive *fitness* benefit or that same rules drive field 3D vertical-niche structure.
6. Even under exact randomization, only 5 independent bats cannot establish cross-population generality.

## Separate ecological estimand required for the high-impact claim

A genuinely useful mechanism story would combine:
- **Stage A: causal opportunity effect on task success**, via randomization with physical integrity, appropriate consent/ethics and an absolute-scale functionally meaningful outcome;
- **Stage B: independently held-out persistence of individual response slopes**, using multiple predeclared 3D challenges, repeated independent occasions, independent device calibration and well-supported biological n;
- **Stage C: if claiming that individualized policies mediate reward**, identify mediation separately. Increased success + route preference is not proof that success caused preference; even randomized treatment effects do not automatically identify a mediator.

The existing source never supplies this prospective intervention, therefore **STOP_EMPIRICAL_EFFECT**, even if synthetic tests all pass.

## Synthetic implementation frozen before numerical run

Script `paired_assignment_randomization_synthetic_v5.py` MUST:
- create only fictitious 5 bats × 3 independent matched blocks = 15 fair binary allocations;
- use fixed arbitrary bat-specific noise amplitudes (not homoscedastic or normal by assumption), arbitrarily different bat intercepts and unknown block means as fixed no-treatment slot outcomes;
- enumerate exactly 2^15=32768 potential assignments under sharp no-effect and compute T for each;
- verify the fraction of legal assignments having exact one-sided p≤.05 does not exceed .05, and similarly at .01; demonstrate invariance of signed slot differences to adding arbitrary common block means and personal baseline intercepts;
- include an explicit shared-effect counterexample scenario in documentation or code showing rejection of the no-effect sharp null is not evidence for individual response heterogeneity;
- STOP/raise when called without `--self-test`, and do not open any actual bat file.

**Output contract:** `PASS_EXACT_DESIGN_BASED_SHARP_NULL_SYNTHETIC` is a software and statistical check only, not biological effect or test of individual policy slopes.
