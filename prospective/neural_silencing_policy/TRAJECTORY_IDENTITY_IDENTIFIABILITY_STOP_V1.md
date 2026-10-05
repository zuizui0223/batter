# Neural-silencing trajectory identity identifiability stop v1

## Status

**STOP — deposited trajectory cohort is too small for a conventional exact individual-identity primary at alpha <= .05.**

This stop is issued before trajectory numeric values are opened by this programme.

Parent:
- `SOURCE_RECEIPT_V1.md`
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- `CODE_MAT_STRUCTURE_CONTRACT_V1.md`

Authoritative structural runs:
- metadata: **37390747844**
- code/MAT structure: **37390924693**

## Deposited movement cohort

Zenodo DOI:
`10.5281/zenodo.13857870`

The record contains exactly three trajectory MAT files:

- `jane_trajectorydata.mat`
- `bea_trajectorydata.mat`
- `jason_trajectorydata.mat`

The deposited source trajectory code loads exactly these three files:

`megabattrajectory = [jane, bea, jason]`

and accesses explicit movement/treatment fields including:
- `trialtreatment`;
- `xcoord`, `ycoord`, `zcoord`;
- `velocityx`, `velocityy`, `velocityz`, `velocity3d`;
- trial/session information and source-derived trajectory metrics.

Source code defines:
- `trialtreatment == 1`: saline;
- `trialtreatment == 2`: ligand.

A fourth DREADDs behavioral subject is represented in the broader behavioral/audio archive, but no fourth trajectory MAT is deposited.

## Exact inference ceiling

For a pure trajectory individual-correspondence test with three biological subjects, the exact identity permutation space is:

[
3! = 6.
]

Therefore the smallest possible exact one-sided probability is:

[
p_{min}=1/6=0.1667.
]

A confirmatory 5%-level identity-retention test is mathematically unattainable.

Repeated trajectories/sessions cannot be treated as additional independent biological individuals.

## Decision

`STOP_TRAJECTORY_IDENTITY_IDENTIFIABILITY`

Do not:
- open trajectory values merely to report an underidentified new identity p-value;
- use trial rows as independent replicates;
- add the audio-only fourth subject to movement analysis;
- use asymptotic p-values to evade the six-permutation ceiling;
- mix sham behavioral subjects into a trajectory identity test when comparable trajectory deposits are absent.

## Scientific use

The published experiment remains strong **external causal evidence** that reversible inferior-colliculus suppression changes flight trajectories and elicits immediate compensatory sensorimotor behavior.

The public archive additionally establishes that detailed 3-D trajectories exist for three DREADDs subjects.

But this archive cannot provide the new confirmatory question needed here:

> whether a pre-perturbation personal movement-policy coordinate remains individually identifiable under neural silencing.

That question requires more trajectory-available biological individuals or new data.

## JAE firewall

No change to JAE v0.4.0.
