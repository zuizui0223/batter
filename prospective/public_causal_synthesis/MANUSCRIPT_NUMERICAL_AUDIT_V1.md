# Manuscript numerical audit v1

## Status

**AUTHORITATIVE TRANSCRIPTION AUDIT FOR `MANUSCRIPT_DRAFT_V1.md`.**

Purpose:
ensure that every central numerical claim in the synthesis manuscript maps to a frozen source result or an authoritative completed workflow.

This is a transcription/provenance audit, not a new analysis.

| Manuscript result | Value used in manuscript | Authoritative source | Audit |
|---|---|---|---|
| Harten first-flight monotonic formation primary | B = +0.16733; p = 0.0102; 8/14 positive; frozen requirement 10/14 | `prospective/ontogenetic-path-dependence-v1: prospective/ontogenetic_path_dependence/SOURCE_B_SELF_HISTORY_PRIMARY_RESULT_V1.md` | **PASS** |
| Harten late-history secondary | L = +112.5554; p = 0.0001; 12/14 positive | same source result | **PASS** |
| Harten early-seed diagnostic | E = +15.1920; p = 0.1655; 8/14 positive | workflow run `37391282588`, job `112036685644`; frozen `EARLY_SEED_VS_RECENT_HISTORY_DIAGNOSTIC_V1.md` | **PASS — POST-PRIMARY DIAGNOSTIC** |
| Harten recent-vs-early diagnostic | Q = +144.0791; p = 0.0001; 10/14 positive | same workflow run/job | **PASS — POST-PRIMARY DIAGNOSTIC** |
| Rachum outdoor randomized history-carrier contrast | T = +0.7081; p = 0.3244 | `prospective/early-experience-history-carrier-v1: prospective/early_experience_history_carrier/NIGHTLY_STRATEGY_HISTORY_PRIMARY_RESULT_V1.md` | **PASS — FAIL_TREATMENT_EFFECT** |
| Rachum lab individualization | V enriched = 2.656639; V impoverished = 1.921940; D = +0.734699; p = 0.167785; n=29 | `prospective/early-experience-specialization-v1: prospective/early_experience_specialization/PRIMARY_RESULT_V1.json` | **PASS — UNSUPPORTED_INDIVIDUALIZATION** |
| Rachum state-rewriting secondary | mean errors B=3.137006; G=4.189011; B+S=2.628609 | `prospective/early-experience-specialization-v1: prospective/early_experience_specialization/STATE_REWRITING_SECONDARY_RESULT_V1.json` | **PASS — DESCRIPTIVE ONLY** |
| Elie auditory-feedback total individualization | V hearing=15.766760; V deaf=17.192257; D=-1.425497; exact p=0.716667; n=10 | `prospective/auditory-feedback-individualization-v1: prospective/auditory_feedback_individualization/PRIMARY_RESULT_V1.json` | **PASS — NO_DIFFERENCE_IN_AMOUNT** |
| Elie feature reallocation | positive sum +3.746740; negative sum -5.172237; 15/13 features; cancellation=0.840173 | `prospective/auditory-feedback-individualization-v1: prospective/auditory_feedback_individualization/FEATURE_REALLOCATION_RESULT_V1.md` | **PASS — DESCRIPTIVE ONLY** |
| Pipistrellus baseline→masker | K=+4.941406°; 5/6 positive; exact p=0.0402778 | workflow run `37390031185`, job `112032657710`, `P1` | **PASS** |
| Pipistrellus foam no-masker→masker | K=+6.778955°; 5/5 positive; exact p=0.025 | same workflow, `P2` | **PASS** |
| Myotis graded masking | A=+0.377542; 3/3 positive; exact p=1/1296=0.000771605 | `prospective/myotis-masker-personal-state-v1: prospective/myotis_masker_personal_state/MYOTIS_PERSONAL_STATE_RESULT_V1.json` | **PASS** |
| Eptesicus auditory-midbrain perturbation | K=+1.004452; 4/4 positive; rank 1/24; p=1/24=0.041667 | `prospective/auditory-perturbation-policy-v1: prospective/auditory_perturbation_policy/ACOUSTIC_POLICY_RESULT_V1.json` | **PASS** |
| Aharon navigation-context manipulation | K=+3.695264; 4/4 positive; rank 2/576; p=0.00347222 | `prospective/public-perturbation-audit-v1: prospective/public_perturbation_audit/AHARON_FIGURE1_PRIMARY_RESULT_V1.json` | **PASS** |
| Rhinolophus transparent I/M identity | K=+0.554281; 5/5 positive; p=0.0001 | workflow run `37250685433`, job `111577493779`, `T3_transparent_2D_identity` | **PASS** |
| Carollia fixed Rhino I/M external validation | K=+0.347582; 6/7 positive; p=0.0007 | workflow run `37279136453`, job `111662850801`, `C1_fixed_2D` | **PASS** |
| Carollia fixed detailed geometry | K=-0.0350363; 3/7 positive; p=0.2144 | workflow run `37402577260`, job `112072812621`, `E1_fixed_geometry` | **PASS — UNSUPPORTED** |
| Wild FlightIntensity bridge | frozen gate 2/4 = FAIL | `prospective/evidence-provenance-correction-v1: prospective/field_policy_bridge/FIELD_EVIDENCE_PROVENANCE_GUARD_V1.md` | **PASS — FAILED FROZEN GATE** |

## Provenance corrections retained

### Formation hierarchy

The manuscript must preserve:

1. Harten monotonic formation primary = **FAIL** because 8/14 positive < frozen 10/14 requirement, despite p=0.0102.
2. Late-history result = **predeclared secondary supported**.
3. Q=+144.079 recent-vs-earliest = **post-primary diagnostic only**.
4. Rachum randomized history-carrier treatment contrast = **FAIL**, p=0.3244.

No later draft may promote items 2–3 into the failed primary.

### Wild hierarchy

The manuscript must preserve:

1. frozen wild scalar FlightIntensity gate = **2/4 FAIL**;
2. later H/V decompositions = **post-outcome exploratory**;
3. no selected-panel analysis may reopen the laboratory-to-wild bridge.

### Removed unsupported transcription

An earlier synthesis draft contained:

> held-out environment prediction p = 0.0002

for the Rhino I/M programme.

That standalone number was not cleanly traceable to the authoritative current source receipt during this audit and has therefore been **removed** from the manuscript and synthesis.

The traced Rhino cross-configuration statistic remains:
- K = +0.554281;
- 5/5 positive;
- p = 0.0001.

## Overall verdict

**PASS_MANUSCRIPT_NUMERICAL_TRANSCRIPTION_V1**

All central numerical claims retained in `MANUSCRIPT_DRAFT_V1.md` are traceable to frozen source results or authoritative completed workflow output at the precision used in the manuscript.
