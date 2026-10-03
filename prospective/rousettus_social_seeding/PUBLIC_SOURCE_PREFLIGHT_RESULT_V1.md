# Rousettus public-source preflight result v1

## Status

**PASS — route geometry remains unopened.**

Authoritative workflow:
- run: **37112262092**
- artifact: **11270600021**
- conclusion: **success**

Pinned public source:
- repository: `EmmLourie/Information-transfer-analysis`
- commit: `1d7edbdbb87d9df048ab42a0b425a1966d491e86`

## Reproduced source identities

The pinned source analysis defines four directly smeared visitor tags:

`6485, 6637, 6639, 6654`

The visitor table contains 14 unique target-tree visitors. Removing the four smeared visitors reproduces exactly the 10 source-defined naive target visitors:

`6399, 6411, 6414, 6428, 6635, 6640, 6641, 6824, 6991, 6993`

## Pup exclusion

Pinned `ind_info.csv` identifies tag **6641** as `pup`.

Pinned `Sharing_Information_Trees.Rmd` explicitly removes pups because some may be attached to their mothers.

Thus the frozen maximum set of independent naive target visitors before raw-track support is **9**.

Age metadata in the pinned `ind_info.csv` are absent for:
`6399, 6411, 6414`.

Missing age is not converted into a pup classification and is not itself an exclusion.

## Source inconsistency reproduced

The pinned `Field_Manipulation_Table.csv` contains one internally inconsistent row:

- 19 Jul 2020, Gershom
- No_manipulated_bats = 4
- n_naive = 19
- n_total = 22

Because 4 + 19 != 22, that CSV is not used to reconstruct canonical experimental sample size.

Peer-reviewed Methods/Table 1 remain authoritative for the experiment n.

## Preflight checks

All frozen checks passed:
- 14 unique visitors;
- exact four smeared visitor IDs;
- exact ten naive visitor IDs;
- exact pup set = {6641};
- nine independent candidate naive visitors;
- source warning about mother-attached pups reproduced.

No ATLAS route similarity, corridor distance, target-annulus geometry or vertical outcome was opened.
