# Post-freeze mechanism synthesis v7

## Scope

This document integrates the closed archival mechanism programme and the subsequently frozen independent external validation.

The v0.3.8 JAE submission on `main` remains unchanged.

## Core ecological rule

Across the original comparative programme, individual identity predicts the **centered organization of vertical space use** after coarse horizontal occupancy and additive altitude level are controlled.

The central question is:

> **Do individuals retain repeatable vertical organization beyond where they are, how high their tag is offset, and what broad movement mode they are in?**

## Independent external validation: Nyctalus noctula

A genuinely independent source was selected prospectively after the original Movebank search universe had been closed.

Source:
- taxon: *Nyctalus noctula*
- repository: Zenodo
- DOI: `10.5281/zenodo.7535030`
- study: *Wind energy production in forests conflicts with tree-roosting bats*
- 60 individuals, 107 explicit tracks, 8,129 positions
- source HMM movement states: ARM / COM / undefined

Source admission, cohorting, structural eligibility, exact n, estimators, vertical bins, permutation counts/seeds and interpretation matrix were frozen **before numeric Height values were opened**.

### Prospective primary replication

5-km horizontal matching + track-median centering:

- exact n: **36**
- observed identity: +0.00527 nats/fix
- permutation-null mean: -0.08074
- calibrated excess: **+0.08600**
- p(null >= observed): **0.0115**
- verdict: **PASS**

Therefore the central rule independently replicates in a new species, study, repository and tracking programme.

### Prospective movement-state mechanism replication

5-km horizontal cell × source HMM movement state (ARM/COM):

- exact n: **27**
- observed identity: +0.02401
- null mean: -0.02673
- calibrated excess: **+0.05074**
- p(null >= observed): **0.0707**
- verdict: **FAIL**

The direction remains positive, but the preregistered p<=0.05 criterion is not met.

**External-validation conclusion:** centered vertical individuality generalizes; persistence within independently classified movement state is not externally established.

## What now generalizes most strongly

The strongest general rule is no longer limited to the original six public datasets:

> **Individual bats can retain repeatable information in the shape of centered vertical space use after coarse horizontal occupancy and additive altitude level are removed.**

Evidence:
- original five comparative panels: supported;
- independent prospective *N. noctula*: supported;
- focal *Tadarida* remains the principal boundary case for centered shape.

The centered-shape result therefore now spans four taxa with positive evidence (*Eidolon*, *Hypsignathus*, *Phyllostomus*, *Nyctalus*) plus a contrasting *Tadarida* boundary.

## What does not yet generalize mechanistically

The original post-freeze mechanism work showed:
- speed-state conditioning: 5/5 original comparative panels retain identity;
- speed × turning conditioning: 5/5 retain identity;
- 500-m place × speed×turn: 4/4 structurally evaluable panels retain identity;
- 250-m place × speed×turn: 3/3 evaluable systems retain identity;
- >=1-day self-history separation: 4/4 retain identity;
- >=3-day separation: 3/3;
- >=7-day separation: 2/2;
- simple body-mass similarity: 0/4 support;
- relative tag burden: unsupported;
- broad same-night context: insufficient in 3/4 at 2 km;
- support-matched temporal-phase attribution: unsupported.

However, the independent *Nyctalus* source does **not** pass the preregistered within-HMM-state test.

Thus the following stronger claim is **not universalized**:

> individual vertical organization necessarily persists after conditioning on independently classified behavioural state.

Behavioural-state allocation may contribute more strongly in some ecological systems, including *Nyctalus*.

## Revised causal interpretation

The evidence now supports a layered rather than single-mechanism picture.

### Layer 1 — general individual organization

Supported externally:

`individual identity -> repeatable centered vertical-distribution organization`

This is the most defensible general ecological principle.

### Layer 2 — how that organization is generated

Not universal.

In the original comparative panels, broad speed/turning composition is insufficient.

In external *Nyctalus*, the state-conditioned effect remains positive but falls short of the frozen inferential criterion.

Therefore vertical individuality can plausibly arise through different mixtures of:

1. **behavioural allocation**
   - commuting vs area-restricted/foraging-like movement;
   - temporal allocation among movement modes;

2. **fine resource/route/microhabitat allocation**
   - exact feeding sites;
   - narrow corridors;
   - canopy openings;
   - microtopography;
   - local atmospheric exposure;

3. **stable within-context individual organization**
   - unmeasured wing morphology / wing loading;
   - learned routines;
   - memory and experience;
   - persistent individual environmental reaction norms.

The data reject a single simple universal cause.

## Spatial localization from the original archive

Where structural support permits:
- 2 km matching: 4/4 retain identity;
- 500 m: 4/4;
- 250 m: 3/3;
- 100 m common test: structurally unavailable.

Thus the unresolved spatial mechanism is below roughly 250–500 m in the original structurally evaluable systems.

This spatial localization is **not** externally replicated in *Nyctalus*, because the prospective 500-m HMM-state family failed structural preflight and was never opened.

## Temporal stability from the original archive

Where structural support permits:
- >=1 day: 4/4 retain identity;
- >=3 days: 3/3;
- >=7 days: 2/2.

This supports a multi-day and, in two systems, week-scale stable component.

This temporal persistence is **not** externally replicated in *Nyctalus*, because the preregistered >=1-day HMM-state family failed structural support and was never opened.

## Technical alternatives

### Tag burden

Relative tag mass / body mass is not a general predictor of calibrated identity strength.

### Body mass

Cross-individual body-mass similarity is 0/4 as a predictor of vertical-profile transfer in the original evaluable subset.

Thus simple body size is not a general explanation, although detailed wing morphology remains unmeasured.

## Final causal position

The programme now distinguishes **generality of the ecological rule** from **generality of the mechanism**.

### Generalized result

> **Repeatable centered vertical-space organization is a real cross-system individual property in bats and now has prospective independent support.**

### Mechanism status

> **No single mechanism is established as universal.**

The original systems support individuality beyond broad kinematic-state composition and, where testable, beyond 250–500 m spatial matching and multi-day separation.

The independent *Nyctalus* source confirms the centered rule but does not pass the stronger within-source-HMM-state replication.

This is consistent with **mechanistic pluralism**: different systems may generate the same distribution-level individuality through different combinations of behavioural allocation, fine spatial/resource specialization and stable within-context flight organization.

## Stop rule

The archival and independent-validation programmes are closed.

Do not add:
- new spatial grids;
- new lag thresholds;
- alternate movement-state definitions;
- sex/age/turbine-distance rescue analyses;
- alternative vertical bins or endpoint definitions;
- additional external datasets chosen after seeing the Nyctalus outcome.

Further mechanism progress requires:
1. a new independently preregistered external programme with a future search cutoff; or
2. new field data designed for cross-individual overlap in exact resource/route/environment contexts.
