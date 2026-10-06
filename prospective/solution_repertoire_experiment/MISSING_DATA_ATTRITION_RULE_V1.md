# Missing-data and attrition rule v1

## Status

**SUPERSEDED COMPATIBILITY RECORD. DO NOT USE FOR CONFIRMATORY INFERENCE.**

The authoritative rule is:

`ATTRITION_AND_MISSING_DATA_CONTRACT_V1.md`

The authoritative contract is stricter than this earlier version.

Current clean-confirmatory requirement:
- capability/eligibility exclusions occur before randomization;
- confirmatory inference uses complete four-animal randomized blocks;
- any post-treatment incomplete randomized block -> **ATTRITION_STOP** for the clean causal claim;
- any result calculated from remaining complete blocks after such attrition is **sensitivity-only**.

This supersedes the earlier rule that allowed confirmatory analysis after dropping incomplete blocks.

No outcome was opened to make this correction.
