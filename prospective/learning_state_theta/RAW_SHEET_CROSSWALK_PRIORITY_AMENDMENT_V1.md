# Raw-sheet crosswalk key-priority amendment v1

## Status

**FROZEN AFTER THE FIRST OUTCOME-BLIND CROSSWALK STOP AND BEFORE ANY KINEMATIC OUTCOME IS OPENED.**

The first crosswalk attempt used the union of candidate letters from:
- `origin_name`;
- `for_article_datasets_name`.

That rule produced deterministic ambiguity for four source bats because both source names corresponded to valid raw-sheet letters.

No speed, trajectory or acoustic outcome was opened.

## Source-semantic correction

The source table explicitly names one field:

`for_article_datasets_name`

This field is therefore the preferred mapping key for the **article dataset workbook**.

Revised rule:

1. For each source bat, extract candidate label(s) from `for_article_datasets_name`.
2. If exactly one raw workbook label in the same acoustic condition matches, use it.
3. Only if **zero** article-name candidates match a raw workbook label may `origin_name` be used as a fallback.
4. If the article-name field yields >1 raw match, STOP.
5. If article-name yields zero and origin-name yields !=1 raw match, STOP.

This priority is based only on source-field semantics and raw-sheet names, not on any behavioural outcome.

## Expected diagnostic behavior

This generic rule is allowed to resolve the known provenance irregularity where a source article name is absent from the raw workbook but an origin name is present.

No bat-specific override is allowed.

## Full pass rule unchanged

The crosswalk passes only if:
- all 14 source bats resolve uniquely;
- all 28 bat×trial records resolve;
- every raw worksheet is used exactly once;
- no duplicate raw worksheet assignment occurs.

All other parent-contract rules remain unchanged.
