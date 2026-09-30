# Comparative generality search stop rule v1

## Status

Frozen after the v10 external-boundary result and before opening any new vertical outcome in the comparative-generality programme.

## Closed search universe

Repositories:
- Dryad
- Zenodo
- Figshare
- Movebank Data Repository / public Movebank-derived records

Frozen query families are those in `contract_v1.json`.

The search snapshot is closed after:
1. every unique dataset returned by those frozen queries has been classified;
2. duplicates / historical opened sources are marked;
3. every plausible event-level tracking source has received metadata/schema screening.

Do **not** add new search terms after seeing a new source's vertical result.

## Current candidate classes

### Historical / already opened
- original six-panel archive;
- Nyctalus;
- Hipposideros.

They do not count as new prospective sources.

### New sources screened
- *Leptonycteris nivalis*: STRUCTURAL STOP before Altitude; 21 IDs but zero >=50-fix sessions.
- *Desmodus rotundus*: STRUCTURAL STOP before Altitude; no local with >=3 repeat individuals under the frozen >=50-fix session rule.
- *Hypsignathus monstrosus* Dryad 2022–2023: REJECT; event table documents x/y/time/ID but no raw vertical response.
- Airflows multispecies Zenodo 10.5281/zenodo.21915776: metadata/schema audit pending.

### Wrong data type / no raw vertical trajectory
Acoustic, monitoring, UAV-video, publication-only and derived-summary datasets returned by the frozen queries are rejected.

## Fail-closed rule

If no new source passes the frozen source-level structural gate:
- do not lower the >=50-fix session rule;
- do not lower the >=50 common-support target rule;
- do not redefine sessions post hoc;
- do not use absolute altitude or another vertical endpoint as rescue;
- do not continue searching with new query terms.

The comparative programme then reports a **structural scarcity result**: public independent bat tracking sources with adequate repeated-session support for this estimator are rare under the predeclared design.

## If Airflows produces candidate panels

All candidate study×species panels passing the metadata necessary screen are carried forward, not only the most promising taxon.

Exact duplicates of already opened sources are excluded from the *new prospective* count but retained in the provenance ledger.

A point-level source may advance only under a separately frozen source/panel preflight before any vertical effect is inspected.

## Outcome rule

A new-source FAIL remains in the comparative panel.

A new-source PASS does not reopen failed sources for threshold or endpoint rescue.

## Programme endpoint

The programme ends when either:

1. all frozen-query candidates have reached one of:
   - prospective vertical result,
   - structural STOP,
   - metadata/schema REJECT,
   - exact historical duplicate;

or

2. at least eight genuinely new, structurally eligible source panels have been prospectively opened, at which point the separately frozen stage-2 cross-source predictor design may begin.

No search expansion is permitted between stages.
