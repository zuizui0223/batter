# Source A structural-column value allowlist v1

## Status

**FROZEN BEFORE ANY DATA ROW FROM `allPairs.xlsx` OR `dataInfo_mompup.xlsx` IS READ.**

Parent contracts:
- `SCHEMA_PREFLIGHT_CONTRACT_V1.md`
- `SOURCE_A_STRUCTURAL_MEMBER_HEADER_OPENING_V1.md`

Purpose:
determine whether Source A has enough **mother–pup / developmental chronology / independent-night support** to open the prospective maternal-to-self route-crossover analysis.

This gate does not open a new route-similarity outcome.

## Source-native developmental interpretation fixed before row values

From the already-authorized published MATLAB code:

- stage 2 = maternal **drop-off** stage: mother deposits the pup, forages separately, and later picks it up;
- stages 4–5 are described by the source code as **late independent navigation and exploration**;
- mother and pup are stored as paired subfolders and linked by `index`.

These definitions are inherited from source code and are not estimated from the data values below.

## `GPS data/allPairs.xlsx` — allowed columns

Only the following columns may be read from data rows:

### Pair / chronology
- `index`
- `Date`
- `dateNum`
- `trackNum`
- `analyze`
- `stage`
- `stagePossible`
- `stagePossible1`
- `source`
- `cave`

### Source-coded mother/pup timing and independence structure
- `exitMom`
- `exitPup`
- `enterMom`
- `enterPup`
- `dropOff`
- `pickUp`
- `leaveCaveTogether_`
- `returnTogether`
- `pupExited`
- `drop_off_y_n_`
- `pickup_YN`

### Source-defined drop-off/task identity
- `dropOffNumber`
- `DO_tree`
- `DO_tree_hebrew`

### Inherited-source revisit flag
- `visitsPup`

`visitsPup` is permitted **only as an eligibility/task-availability flag**. The source paper already establishes that independent pups revisit maternally experienced sites. It must not be treated as a new outcome, effect size, or evidence for the prospective maternal-vs-self route contrast.

## `GPS data/dataInfo_mompup.xlsx` — allowed columns

Sheet `Sheet1` only:
- `batFolder`
- `index`
- `analyze`

No values from sheet `SI` are authorized.

## `GPS data/trees_mompup.xlsx`

**No row values are authorized at this gate.**

The tree table remains header-only. Exact tree coordinates are not needed to decide whether the biological replication/support gate can pass.

## Explicitly forbidden columns / values

Do not read row values for:
- `dropOffLat`, `dropOffLon`;
- forearm, body mass, GPS mass or maternal mass;
- any acceleration variables;
- distance-to-cave or distance-to-dropoff variables;
- visit duration or visit-count response variables other than the single inherited `visitsPup` availability flag;
- speed indices;
- foraging duration;
- commuting duration;
- path length;
- tree-use percentages;
- any route, overlap, similarity, entropy, or trajectory statistic.

## Structural support summaries authorized

For each unique source `index`, report only:

- mapped `batFolder` if available;
- count of unique source dates with `analyze` admitted;
- count of source dates in each developmental `stage`;
- count of stage-2 dates with a source-defined drop-off identifier;
- whether at least one stage-2 maternal drop-off exposure exists;
- count of stage-4/5 independent dates;
- whether >=4 stage-4/5 independent dates exist;
- whether chronology supports first-two / later-two independent dates;
- whether at least one source-coded independent revisit of a maternally experienced drop-off is structurally available;
- PASS/STOP against the already frozen Source A gate.

### Frozen Source A structural gate

A pup can be structurally eligible only if it has:

1. a reproducible mother–pup pair/index and mapped source folder;
2. >=1 maternal drop-off exposure before independent navigation;
3. >=4 unique independent-navigation dates in source stages 4–5;
4. therefore at least one later target date with >=2 strictly prior independent dates;
5. at least 2 early and 2 later independent dates by chronological order;
6. a source-defined maternally experienced task/destination that is available for independent revisit/route comparison.

The programme opens only if **>=5 independent pups** satisfy the full structural gate.

## Important ceiling

Passing this gate does **not** authorize reading any route coordinates.

If >=5 pups pass, the next action must be:
1. freeze the exact route estimator and sampling standardization;
2. freeze the exact set of archive members/individuals to open;
3. only then read route geometry.

If <5 pass, Source A route-crossover remains STOPPED and thresholds may not be relaxed.
