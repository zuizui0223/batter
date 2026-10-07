# Public perturbation candidate ledger v2

## Status

**CURRENT PUBLIC-DATA MECHANISM PRIORITY LEDGER — supersedes V1.**

No new source is promoted because it is merely available. Priority is based on causal leverage, individual support, and whether a frozen exact test is identifiable.

## Priority 1 — Diebold et al. 2024 auditory-midbrain perturbation

Study:
*Rapid sensorimotor adaptation to auditory midbrain silencing in free-flying bats*.

Public source:
- Zenodo DOI `10.5281/zenodo.13857870`;
- four individual DREADD audio files: jane, bea, jason, stella;
- deposited source analysis code;
- reversible ligand perturbation of excitatory inferior-colliculus processing;
- Saline versus Ligand trial structure.

Why first:
- true within-individual neural/sensory perturbation;
- four DREADD bats in the public acoustic layer;
- exact identity permutation space `4! = 24`, so one-sided p <= .05 is barely identifiable;
- source-native acoustic variables and source treatment coding are already recoverable from deposited code;
- primary endpoint and numeric implementation have been frozen before outcome opening on branch `prospective/auditory-perturbation-policy-v1`.

Frozen question:

> after the shared Saline-to-Ligand shift is removed, does each bat retain a distinguishable multivariate acoustic-policy organization?

Hard boundary:
- trajectory layer has only three DREADD bats in deposited analysis code, so trajectory identity is not confirmatory;
- no feature fishing or trajectory rescue.

Current state:
**STRUCTURAL AUDIT QUEUED; NUMERIC PRIMARY FROZEN BUT NOT AUTHORIZED UNTIL STRUCTURAL PASS.**

## Priority 2 — Aharon et al. 2017 path-integration cue manipulation

Study:
*Bats Use Path Integration Rather Than Acoustic Flow to Assess Flight Distance along Flyways*.

Public dataset:
- Mendeley `f6mvhj5gj9` v3;
- DOI `10.17632/f6mvhj5gj9.3`.

Public description establishes:
- variable names encode biological bat ID;
- suffixes encode condition;
- turning-point matrices contain trials by column;
- slowing-point matrices contain trials by column;
- trial-level mean-speed variables exist;
- experiments alter cue structure including acoustic flow, start position and wind.

Why second:
- strong experimental manipulation and repeated individual trials;
- but public API currently returns 401 without authentication;
- exact bat × condition support has not yet been recovered outcome-blind;
- no numeric primary is opened.

Proceed only after a source-structure route recovers the exact repeated bats/conditions without using outcome values.

## Priority 3 — Ma et al. 2025 noise / prey-context manipulation

Study:
*Prey evasiveness and masking noise jointly promote the ultrahigh call rate in echolocating bats*.

Verified dataset:
- Mendeley `964fv73w94` v1;
- DOI `10.17632/964fv73w94.1`.

Published design:
- eight adults total;
- four foraging bats;
- four different landing bats;
- noise manipulation repeated within task;
- roughly 15 repeats per noise condition in the foraging experiment.

Why third:
- experimentally useful within-task context manipulation;
- but only four bats per task;
- foraging and landing cannot be used as within-individual cross-task transfer;
- public API route currently 401;
- best use is a narrow external heterogeneity/localization test after Priority 1/2 disposition.

## Priority 4 — developmental / social-learning public sources

Examples include mother-pup navigation learning and other developmental bat datasets.

Role:
- formation/history triangulation;
- not promoted until the adult perturbation programme is closed because many are observational or have weaker individual-level causal assignment.

## Programme rule

Proceed sequentially:

1. close Priority 1 with its frozen PASS/STOP rule;
2. only then spend analysis effort on Aharon;
3. Ma only if it adds a nonredundant manipulation layer;
4. do not reopen same-data Rhino geometry fishing or the failed wild H/V bridge.

## Public-data ceiling

Public perturbation data can potentially establish:

[
\text{individual organization persists}
+
\text{current context can be causally perturbed}
+
\text{expression changes without complete identity erasure}.
]

They cannot, with the currently recovered sources, directly randomize:

[
\text{number of feasible movement solutions}
\rightarrow
\text{formation of individual specialization}.
]

That remains the sharp boundary between public-data causal triangulation and a new designed experiment.
