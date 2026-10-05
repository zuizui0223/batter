# Raw-trajectory two-axis structural STOP v1

## Status

**STRUCTURAL STOP — no raw-trajectory policy-axis outcome was adjudicated.**

Branch:
`prospective/learning-policy-state-v1`

Parent contract:
`RAW_TRAJECTORY_TWO_AXIS_CONTRACT_V1.md`

Authoritative fail-closed diagnostic workflow:
- run: **37300236004**
- head: `ba9e4b3fe6692eb0e9ff1a8a64d72c9ee923b7cf`
- conclusion: **failure by intended structural stop**

## What happened

The frozen raw-trajectory contract required every linked flight to retain:
- at least **100** finite unique-time rows;
- at least **50** strictly positive time intervals;
- at least **20** finite horizontal turning-rate values.

A subject required both its trial-1 and trial-12 trajectories to pass, and the primary required:
- at least **12** evaluable subjects total;
- at least **5** per acoustic condition.

The outcome-blind linkage had already passed:
- **28/28** trajectory sheets linked;
- **14/14** subjects linked;
- no missing or duplicated subject × trial assignment.

The fail-closed structural diagnostic then showed:
- finite unique-time rows across the 28 linked flights ranged from **43 to 91**;
- **28/28** flights were below the frozen 100-row requirement;
- therefore **0/14** subjects were evaluable;
- condition support was **0/7** and **0/7**.

The failure is therefore not a parser/linkage failure. The source trajectories are simply shorter than the independently frozen support rule.

## False-green workflow audit

Earlier workflow runs **37252201696** and **37284338873** displayed GitHub Actions conclusion `success` even though the Python primary terminated with:

`STOP raw trajectory support bats=0 cond={}`

Cause:
the workflow piped Python into `tee` without Bash `pipefail`, so the pipeline inherited the successful exit status of `tee`.

This has been corrected:
- the workflow now executes with `set -o pipefail`;
- structural STOP exits non-zero;
- the STOP JSON is emitted before exit;
- failure artifacts are retained with `if: always()`.

The linkage workflow was hardened against the same pipeline failure mode.

## Scientific interpretation

Do **not** lower the 100-row threshold inside this prospective primary after observing structural support.

The correct verdict is:

> **The Yamada raw trajectories cannot adjudicate the frozen external two-axis policy-replication primary under its predeclared trajectory-support rule.**

This does not overturn the independent summary-endpoint learning-state primary:
- 14 subjects;
- personal policy-state advantage `K_policy = +0.67436`;
- 11/14 positive;
- permutation `p = 0.0027`.

That result remains evidence that repeated learning changes population-level flight behaviour while preserving relative individual policy state.

## No rescue

Do not:
- lower the 100-row requirement within this primary;
- redefine one trajectory sample as multiple interpolated samples;
- smooth or upsample to manufacture support;
- drop short flights selectively;
- reinterpret the structural STOP as a negative biological result.

A lower-support raw-trajectory estimator, if scientifically justified, must be a separately labelled post-STOP programme and cannot count as the frozen external replication.
