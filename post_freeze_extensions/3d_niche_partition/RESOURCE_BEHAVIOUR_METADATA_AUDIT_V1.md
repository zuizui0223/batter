# Resource / behaviour metadata audit v1

## Purpose

Assess whether the public source archives can directly connect the new 3D geometry to resource identity, feeding-site identity or validated behavioural state.

## Raw archive result

The original GPS and reference CSVs were audited for:
- behaviour/activity/state fields;
- feeding/foraging/resource/tree/patch fields;
- site/roost/lek fields;
- low-cardinality categorical metadata.

### GPS event tables

For:
- Hypsignathus monstrosus;
- Phyllostomus hastatus 2016;
- P. hastatus 2022;
- P. hastatus 2023;

the raw Movebank GPS tables do **not** contain a direct per-fix:
- feeding tree ID;
- resource ID;
- feeding patch ID;
- validated foraging/commuting state;
- prey/diet identity.

Available event fields are mainly:
- timestamp;
- longitude/latitude;
- native height;
- ground speed and device/GPS fields where available;
- individual/tag identifiers.

Therefore direct resource-partitioning analysis cannot be recovered from the raw event tables alone.

### Reference tables

Useful non-event metadata include:
- study site;
- animal-group-id;
- sex;
- reproductive condition;
- morphology/measurements for some deployments.

For P. hastatus 2023, the six frozen co-use individuals are all males at Aj-cave and split between source group labels MT-1 and MT-3. Seven of eight frozen co-use dyads are within the same source group label.

These metadata are useful contextual descriptors but are not resource identities.

## Published behavioural classification exists externally

The source study:
**Calderón-Capote et al. 2024, "Consistent long-distance foraging flights across years and seasons at colony level in a neotropical bat"**

states that the authors classified locations using a two-state HMM:
- foraging: short movements with low directional persistence, potentially including resting;
- commuting: fast, directed movement.

The source workflow is public at:
`mccalderonc/P_hastatus_Consistentlong-distance_foragingflights`

Provenance checked:
- branch: main
- commit: `644a8ed8371f55cac7bb51bbecfec33048f10e35`
- cleaning file: `2.CleaningData_2023_gh.Rmd`
- behaviour file: `5.Behavioral_classification.Rmd`

The code:
1. cleans the raw Movebank tracks;
2. downsamples 2023 to approximately 2-min intervals;
3. regularizes missing intervals;
4. fits a two-state momentuHMM model using step length and turning angle;
5. maps state 1 to foraging and state 2 to commuting;
6. applies additional speed-based/manual corrections.

## Important limitation

The classified per-fix HMM output (`Phyllostomus_HMMbehaviors.RData`) is saved in the author's local path in the workflow but is **not committed in the public source repository**.

Therefore an exact event-level behaviour join cannot currently be performed by downloading an existing classified file.

It would require a separate reconstruction of the authors' full cleaning/merge/HMM workflow across the public movement datasets.

Such a reconstruction should be treated as a new provenance-controlled programme rather than silently replacing the current stationary-like descriptive proxy.

## Ecological implication

The public archives currently support:
- geometry of personal strategies;
- terrain correction;
- synchronous co-use geometry;
- source group/colony context.

They do **not** currently support a direct claim about:
- food-resource partitioning;
- feeding-tree partitioning;
- competition at a known resource.

The strongest next mechanistic bridge is the **published foraging/commuting HMM**, if reproducibly reconstructed.

After that, the key question would be:

> Is terrain-relative vertical strategy fidelity concentrated in foraging state, commuting state, or both?

A foraging-specific signal would connect the geometry much more directly to ecological resource use; a commuting-specific signal would instead point toward route memory/navigation.
