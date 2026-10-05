# Neural-silencing code and MAT-structure opening contract v1

## Status

**OUTCOME-BLIND STRUCTURAL OPENING. TRAJECTORY/BEHAVIOR NUMERIC VALUES REMAIN CLOSED.**

Parent:
- `METADATA_PREFLIGHT_CONTRACT_V1.md`
- metadata run **37390747844** — PASS

Zenodo metadata exposes:
- `jane_trajectorydata.mat`
- `jason_trajectorydata.mat`
- `bea_trajectorydata.mat`
- `DREADDs_allbatstrajectory_updated.m`
- `DREADD_OverallBehavior_updatedJL.m`
- `Dreadds_behav_structure.mat`
plus vocal and ABR files.

Notably, a `stella_trajectorydata.mat` file is absent from the deposited record even though `stella_audiopooldata.mat` is present.

## Authorized opening A — source MATLAB code

Download exactly:
- `DREADDs_allbatstrajectory_updated.m`
- `DREADD_OverallBehavior_updatedJL.m`

Verify Zenodo-record MD5 checksums.

Open source text in full.

Code is treated as source documentation, not as a new numerical outcome.

Extract/report:
- loaded file names;
- bat identifiers;
- treatment/condition strings;
- session/trial indexing;
- variable/field names;
- trajectory-coordinate field semantics;
- preprocessing/support rules;
- any source-defined exclusions.

Do not execute the MATLAB code.

## Authorized opening B — MAT metadata only

Download exactly:
- `jane_trajectorydata.mat`
- `jason_trajectorydata.mat`
- `bea_trajectorydata.mat`
- `Dreadds_behav_structure.mat`

Verify MD5.

Inspect only:
- MAT file version/header;
- top-level variable names;
- top-level shapes;
- top-level MATLAB classes/dtypes if safely available without decoding values.

For HDF5/v7.3 files, inspect object/group/dataset names and shapes only.

For pre-v7.3 MAT files, use a metadata-only variable directory reader such as `scipy.io.whosmat`.

Do not load variable values.

## Questions

Determine:

1. how many DREADDs behavioral bats have deposited trajectory data;
2. whether Jane, Jason and Bea are the DREADDs-treated bats or include sham controls;
3. whether a fourth DREADDs trajectory subject is absent or encoded elsewhere;
4. whether baseline/saline/ligand condition labels are explicit;
5. whether repeated sessions/trials are recoverable;
6. what trajectory coordinate fields are available;
7. whether an exact identity test can attain alpha <= .05 under the actually deposited movement cohort.

## Proceed rule

A new movement-bias primary may proceed only if:
- at least 4 biological individuals with comparable trajectory data are recoverable **or**
- another exact within-individual causal endpoint can be defined whose inferential unit is not artificially inflated from trial rows.

If only 3 comparable trajectory individuals are deposited:
- a 3! identity permutation has minimum p=1/6=.1667;
- STOP a conventional 5%-level confirmatory identity-retention primary.

Do not add audio-only individuals to a movement test.

## No rescue

Do not:
- treat sessions/trials as independent animals;
- infer missing trajectories from vocal data;
- combine DREADDs and sham subjects without source-defined linkage;
- open trajectory values before this structural adjudication.
