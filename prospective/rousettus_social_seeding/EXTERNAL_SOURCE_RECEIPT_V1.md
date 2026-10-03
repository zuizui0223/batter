# External source receipt v1 — Rousettus social seeding

## Scope

Prospective follow-up only. This source is independent of the JAE v0.4.0 bat panels.

Question supported by this source:

> When social information seeds a new destination choice, does an individual reach that destination by reusing its own established movement corridor rather than adopting another bat's route?

No route-geometry outcome has been opened.

## Peer-reviewed source

Lourie et al. (2024), *Spatial memory obviates following behaviour in an information centre of wild fruit bats*, Philosophical Transactions of the Royal Society B.

DOI: **10.1098/rstb.2024.0060**

The peer-reviewed Methods/Table 1 are authoritative for experimental sample counts:

- manipulated / odour-exposed bats: **16**
- naive bats tracked during the manipulation campaigns: **56**
- total experimental bats: **72**
- naive bats that subsequently visited one of the two target *Ficus sycomorus* trees: **10 / 56**
- manipulated bats that subsequently visited: **4 / 16**

The original paper's inference that social information increased visits to otherwise fruitless target trees is inherited source knowledge and is **not** retested here.

## Canonical experimental campaigns

Peer-reviewed Table 1 defines:

| campaign | roost | manipulated | naive | total | naive visitors | manipulated visitors |
|---|---|---:|---:|---:|---:|---:|
| 22 Jun 2020 | Gershom | 3 | 9 | 12 | 4 | 2 |
| 22 Jun 2020 | Zemer | 4 | 6 | 10 | 2 | 1 |
| 19 Jul 2020 | Gershom | 4 | 19 | 23 | 1 | 0 |
| 19 Jul 2020 | Zemer | 0 | 0 | 0 | 0 | 0 |
| 7 Dec 2020 | Gershom | 4 | 15 | 19 | 2 | 1 |
| 7 Dec 2020 | Zemer | 1 | 7 | 8 | 1 | 0 |
| **total** | | **16** | **56** | **72** | **10** | **4** |

## Dryad raw tracking source

Dataset DOI: **10.5061/dryad.51c59zwgp**

Current version used for source pinning: **22 May 2024**.

Raw ATLAS SQLite files:

- June campaign: `Syc_Manipulation_June2020_Filtered.sqlite`
  - displayed size: 121.79 MB
  - Dryad file_stream ID: **3182077**
- July campaign: `Syc_Manipulation_July2020_Filtered.sqlite`
  - displayed size: 115.77 MB
  - Dryad file_stream ID: **3182078**
- December campaign: `Syc_Manipulation_Dec2020_Filtered.sqlite`
  - displayed size: 47.51 MB
  - Dryad file_stream ID: **3182076**

The raw SQLite files are the only allowed route-geometry source. If they cannot be retrieved and schema-validated, the route-reuse outcome remains unopened.

## Public analysis/source repository

Repository:
`EmmLourie/Information-transfer-analysis`

Pinned commit:
`1d7edbdbb87d9df048ab42a0b425a1966d491e86`

Pinned files:

- `data_R/Tags_manipulated_and_visiting.csv`
  - blob SHA `48a2ed7b76d27402daf9544a1d9836165b7c0e44`
- `data_R/ind_info.csv`
  - blob SHA `992637c190c2918bb6a95d8eb31235df8ea313c4`
- `data_R/Field_Manipulation_Table.csv`
  - blob SHA `781f419a599e39f9aaf862b03ff0854a14719ec0`
- `data_R/Ficus_Sycamorus_Experiment_Analysis.Rmd`
  - blob SHA `089de09fc57bfdc2b475c80c1eb9cae0c24c2096`
- `Sharing_Information_Trees.Rmd`
  - blob SHA `91bd598d2cf2543814aab89b4fb42ac496b0abe5`

These files may be read from the public source but are not re-hosted in this repository.

## Visitor identities

The pinned source analysis defines directly smeared visitor tags as:

`6485, 6637, 6654, 6639`

The source visitor table contains 14 target-tree visitors. Removing the four smeared visitors yields the peer-reviewed count of **10 naive target visitors**:

`6399, 6411, 6414, 6635, 6428, 6641, 6640, 6991, 6824, 6993`

This identity list is frozen before any raw route geometry is opened.

## Pup exclusion

The source individual table explicitly codes tag **6641** as `pup`.

The authors' tree-encounter analysis explicitly removes pups because some may be attached to their mothers.

Therefore tag 6641 is excluded from any analysis claiming independent personal route geometry.

The maximum source-defined candidate set before raw-track support filtering is therefore **9 naive visitors**.

No other age category is excluded automatically. Missing age is not converted into a pup classification.

## Source inconsistencies and adjudication

### 14 / 57 in Dryad README

A Dryad README version describes 14 manipulated animals and 57 controls.

This conflicts with the peer-reviewed Methods/Table 1, which give 16 manipulated and 56 naive.

**Adjudication:** peer-reviewed Methods/Table 1 are authoritative: 16 + 56 = 72.

### July row in Field_Manipulation_Table.csv

The public CSV contains a Gershom July row whose component counts are internally inconsistent with its total.

**Adjudication:** use the peer-reviewed Table 1 campaign counts. Do not reconstruct experimental sample size from this CSV.

### Figure comparison n=71

The source article reports n=71 for one pre-manipulation comparison.

This does not redefine the experiment population of 72; it reflects availability for that comparison.

## Claim boundary

A positive prospective route-reuse result may support:

> social information can seed destination choice while an individual's established movement history remains informative about how it reaches that destination.

It cannot by itself establish:
- a cognitive-map algorithm;
- cultural transmission;
- reinforcement learning;
- active route copying;
- ontogenetic route formation;
- fitness optimality.
