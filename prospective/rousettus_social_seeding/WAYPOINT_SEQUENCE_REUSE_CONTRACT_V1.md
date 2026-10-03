# Social seeding → personal waypoint-sequence reuse contract v1

## Status

PROSPECTIVE EXTERNAL MECHANISM TEST.

This is a distinct discrete-waypoint test. It does **not** replace the pending raw-ATLAS continuous route-reuse test and cannot be used to rescue it.

The contract is frozen before the full `all_tree_visits_main.csv` target sequences are opened for this analysis.

## Biological question

After social information seeds a visit to a normally fruitless focal tree, does a naive bat approach that target through an ordered sequence of tree waypoints that resembles its **own pre-manipulation waypoint sequences** more than those of other bats?

This tests a discrete form of:

> **shared destination information + personal route grammar**

rather than continuous geometric route overlap.

## Pinned public source

Repository:
`EmmLourie/Information-transfer-analysis`

Commit:
`1d7edbdbb87d9df048ab42a0b425a1966d491e86`

Primary stop table:
`data_R/all_tree_visits_main.csv`

Pinned Git blob SHA:
`3c3cd695bd74d82c87e4c1ff77683e0248bb6971`

The source Rmd defines:
- `TAG` as individual;
- `TAG_Night` as individual-night;
- `date_global` as shifted night date;
- `cluster_ID` as visited tree/stop identity;
- `dummy == cave` as roost/cave stops to exclude.

Exact time/order columns must be identified by an outcome-blind schema preflight before sequences are opened.

## Target population

Inherit the pinned public-source preflight.

Source-defined naive target visitors:
`6399, 6411, 6414, 6428, 6635, 6640, 6641, 6824, 6991, 6993`.

Exclude source-coded pup **6641**.

Maximum independent candidate set:
`6399, 6411, 6414, 6428, 6635, 6640, 6824, 6991, 6993`.

Directly smeared bats are excluded.

## Campaign manipulation dates

- 22 June 2020
- 19 July 2020
- 7 December 2020

Each target individual is assigned to the manipulation campaign recorded in the pinned source visitor table.

## Target sequence

For each qualifying naive visitor:

1. identify its **first** source-defined focal *Ficus sycomorus* visit 1–6 nights after the relevant manipulation;
2. select the same `TAG_Night`;
3. retain tree stops occurring before the start of the focal target visit;
4. exclude cave/roost stops;
5. exclude the focal target tree itself;
6. order remaining stops by source start time;
7. replace each stop by its exact source `cluster_ID`;
8. collapse only **consecutive** duplicate cluster IDs.

The resulting ordered list is the **pre-target waypoint sequence**.

No tree species aggregation is allowed.

## Self prehistory

For the focal individual:
- use the **14 calendar days immediately before** the manipulation date;
- exclude manipulation date itself;
- divide by complete `TAG_Night`;
- remove cave stops;
- use exact `cluster_ID`;
- order by source start time;
- collapse consecutive duplicates identically.

The 14-day window is inherited from the source study's own pre-manipulation comparison and is not selected from the route-reuse outcome.

## Other prehistory

Donor histories use:
- other naive, non-pup bats tracked in the same manipulation campaign;
- the same 14-day pre-manipulation window;
- identical sequence construction.

Where an exact night-level cave/roost field is present and can be matched reproducibly, primary donors must share the target individual's target-night cave/roost. If no reproducible night-level roost field exists, the structural preflight fails; campaign-only pooling is **not** substituted.

## Outcome-blind structural gate

Before any waypoint identities are compared between target and history:

For each target individual require:
- target pre-target sequence has >=3 non-target waypoint stops after consecutive-deduplication;
- own prehistory contains >=3 nights, each with >=3 waypoint stops;
- >=3 other naive non-pup donor individuals from the same campaign and target-night roost each contain >=3 qualifying prehistory nights.

The analysis opens only if **>=5 independent target visitors** pass.

Structural preflight may count stops and nights but may not calculate:
- waypoint overlap;
- shared cluster IDs;
- LCS;
- transition overlap;
- self-versus-other similarity.

If <5 visitors pass, STOP with no threshold relaxation.

## Primary sequence similarity

For two waypoint sequences A and B:

`LCS(A,B)` = length of their longest common subsequence using exact `cluster_ID` equality.

Normalize to the target sequence:

`S(A,B) = LCS(A,B) / len(A)`

where A is always the target pre-target sequence.

For focal self history:
- calculate S(target, history_night) for every eligible own prehistory night;
- average equally across own nights to obtain `S_self`.

For one donor:
- calculate the same equal-night average over that donor's eligible prehistory nights.

Then average equally across donor individuals to obtain `S_other`.

Per target individual:

`W_i = S_self - S_other`.

Primary experiment statistic:

`W = equal-individual mean W_i`.

Positive W means the socially seeded target-night waypoint order resembles the focal bat's own established waypoint grammar more than conspecific histories.

## Primary null

Whole-prehistory identity permutation within exact **campaign × target-night roost**.

For each permutation:
- keep target sequences and target identities fixed;
- keep each individual's complete 14-day prehistory library intact;
- permute complete prehistory libraries among eligible naive non-pup identities within the same stratum;
- reconstruct S_self, S_other, W_i and W.

B = **9,999**.

Seed = **20261003072**.

Support requires:
- observed W - mean(null W) > 0;
- one-sided p(null >= observed W) <= 0.05.

## Secondary descriptive quantities

Report only:
- target sequence length;
- own eligible history nights;
- donor count;
- S_self;
- S_other;
- W_i;
- campaign / roost;
- nights after manipulation;
- source age/sex when available.

No age-specific inferential subgroup is authorized.

## Claim interpretation

If supported:

> Naive bats reaching a socially seeded destination reused an ordered tree-waypoint pattern more similar to their own pre-manipulation movement history than to conspecific histories.

This supports a distributed architecture in which **social information seeds where to go while personal history contributes how to get there**.

It does not establish:
- continuous geometric corridor reuse;
- direct route copying;
- cultural transmission;
- cognitive-map algorithms;
- ontogenetic formation;
- reinforcement learning;
- optimality.

## Stop rules

After sequence outcome opening:
- no switch from LCS to set overlap, Jaccard, transition overlap, edit distance or DTW;
- no alternative prehistory window;
- no lowering the 3-waypoint / 3-night / 3-donor / 5-individual gates;
- no inclusion of 6641;
- no inclusion of directly smeared bats;
- no campaign-only donor rescue if roost matching fails;
- no species-level aggregation of waypoints.

## JAE firewall

This test is outside JAE v0.4.0 and cannot alter or rescue it.
