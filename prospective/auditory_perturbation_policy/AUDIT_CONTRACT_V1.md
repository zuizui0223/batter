# Auditory-perturbation vocal-policy structural audit v1

## Status

**OUTCOME-BLIND STRUCTURAL AUDIT. NO VOCAL OUTCOME VALUES OPENED.**

## Source

Study:
Diebold, Lawlor et al. (2024),
*Rapid sensorimotor adaptation to auditory midbrain silencing in free-flying bats*,
Current Biology 34:5507–5517.e3.
DOI: `10.1016/j.cub.2024.10.045`.

Public archive:
Zenodo `10.5281/zenodo.13857870`.

The published behavioral DREADDs cohort contains four adult *Eptesicus fuscus*.

The public figure-generation code names the four audio individuals:

- jane;
- bea;
- jason;
- stella.

The same code defines:
- treatment 1 = saline;
- treatment 2 = ligand;
- the common behavioral filter `trialtype < 4`;
- trial-level call duration;
- call bandwidth;
- call onset / IPI;
- call rate;
- trial identity and outcome fields.

Public trajectory code contains only:
- jane;
- bea;
- jason.

Therefore a four-individual confirmatory identity test is structurally plausible only in the audio layer.

## Stage 1 authorized opening

Download exactly:

- `jane_audiopooldata.mat`;
- `bea_audiopooldata.mat`;
- `jason_audiopooldata.mat`;
- `stella_audiopooldata.mat`.

Read only structural information:

- top-level MATLAB variable names;
- `audiopoolstruct` field names;
- array/cell lengths;
- treatment-label counts;
- trialtype-label counts;
- number of trials structurally available for each frozen candidate endpoint.

Do not calculate or print:
- call duration values;
- bandwidth values;
- IPI values;
- call-rate values;
- any treatment mean;
- any individual mean;
- any distance between individuals;
- any p-value.

## Candidate endpoint order

The endpoint architecture is fixed before numerical values are opened.

Primary candidate representation:

[
V=(D,B,I,C)
]

where trial-level components are:

- D = mean call duration in the trial;
- B = mean call bandwidth in the trial;
- I = mean inter-pulse interval in the trial;
- C = call rate in the trial.

These four components are chosen because the source's released analysis code computes all four for every bat under the same saline/ligand filtering architecture.

No endpoint may be removed because it later weakens identity.

## Structural proceed gate

Proceed to the numerical primary only if all four biological individuals have:

- >=5 valid saline trials;
- >=5 valid ligand trials;
- all four frozen vocal components structurally computable under `trialtype < 4`.

If any bat fails:
**STOP_FOUR_BAT_VOCAL_POLICY_PRIMARY**.

Do not drop one bat and proceed with n=3.

## Planned numerical question if the gate passes

> After removing the shared treatment-level shift, does each bat's ligand vocal-policy state remain closer to its own saline state than to the saline states of other bats?

The exact numerical estimator and randomization null must be frozen in a separate contract before values are opened.

## Exact-resolution boundary

With four complete biological identities:

[
4! = 24
]

condition-preserving identity permutations are available.

Minimum attainable exact one-sided probability:

[
1/24 = 0.04167.
]

Thus conventional p<=0.05 is mathematically attainable, but only at the most extreme rank.

This discreteness must be stated explicitly.

## Trajectory boundary

The released trajectory layer contains only three DREADDs bats.

For n=3:

[
3! = 6,qquad p_{min}=1/6=0.1667.
]

Therefore no new confirmatory individual-identity trajectory primary is authorized from the public trajectory archive.

Trajectory analyses may be descriptive/mechanistic only after the vocal primary is disposed.

## Claim ceiling

A positive vocal result could support:

> an individual-specific vocal control organization remains identifiable across reversible central auditory perturbation, despite a treatment-induced shift in expressed vocal behavior.

It would not establish:
- the developmental origin of the bias;
- a movement-policy carrier;
- neural storage in the inferior colliculus itself;
- wild-field vertical individuality;
- universal bat personality.
