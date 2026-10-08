# Public bat reward/3D route dataset preflight — one source only (2026-10-08)

## Status
**SOURCE AVAILABILITY / DESIGN STRUCTURE ONLY. NO NEW BAT OUTCOME VALUES OPENED.**
This record screens one potentially valuable independent public experiment before proposing further real-data attribution. It does not reopen the frozen five-bat Rhinolophus archive or the stopped wild individual-policy carrier gate.

## Screened candidate
Forli, Fan, Qi et al. 2025, *Replay and representation dynamics in the hippocampus of freely flying bats*, Nature 645:974–980, DOI `10.1038/s41586-025-09341-z`.

Authoritative paper:
https://www.nature.com/articles/s41586-025-09341-z

Experimental architecture from published Methods:
- six Egyptian fruit bats (`Rousettus aegyptiacus`) in the principal neural/behavioral analysis, 23 recorded sessions;
- simultaneously tracked free-flight 3D paths (indoor 120 Hz optical motion capture, outdoor 100 Hz UWB localization) and hippocampal neural recordings;
- food reward delivered at electronically controlled feeders;
- reward probability 0.2–0.8 and puree volume 0.1–0.3 ml adjusted by the experimenter to shape behavior;
- some sessions include obstacles or altered lighting, but this is a different study question.

## Availability
Nature's Data Availability states: **full dataset available from corresponding author on reasonable request**; a **demo session** and associated material were deposited at Zenodo DOI `10.5281/zenodo.15738988`. Code link: https://github.com/kevin-qi/ripple-bat.

These facts do not establish that the public demo contains a complete individually replicated 3D choice × payoff/fitness table or trial-wise experimental reward schedule.

## Causal design eligibility
The present PR #83's causal route-history × payoff test would require at minimum:
1. randomly assigned initial feasible route S independent of each animal's prior route preference;
2. independent randomized route payoff B and held-out comparable route-choice events;
3. a common immediate route reset;
4. before/after independently sampled **all-route** flight performance to identify route-specific skill gain;
5. biological replication and a frozen payoff and route-opportunity definition.

**None** of the critical prospective randomized-history/counterfactual-performance conditions is demonstrated by the accessible article Methods. In particular, adjusting feeders with reward probabilities is *not evidence* that payoff labels were independently randomized against past route assignments.

Therefore:
`STOP_PUBLIC_REWARD_ROUTE_CAUSAL_TEST_NO_MATCHED_RANDOMIZATION_OR_FULL_PUBLIC_OUTCOMES`.

This is a **single-source structural screen**, not a claim that no suitable public bat dataset exists anywhere and not a negative effect estimate. A source meeting the above support in a future verified public archive would be eligible for a *new* frozen prospective analysis, not an after-the-fact rescue of JAE or the present synthetic result.
