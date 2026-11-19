# Original 2024 Rousettus manipulation: source consistency audit

2026-11-19. Read-only examination of independent author data and Rmd (not a rerun of original randomization or the bat tracking file).

Source paper: Lourie, Shamay, Toledo & Nathan (2024) https://doi.org/10.1098/rstb.2024.0060 .
Original source repository: https://github.com/EmmLourie/Information-transfer-analysis

Verified files (source Git blob SHA-1 at retrieval):
- data_R/Field_Manipulation_Table.csv — `781f419a599e39f9aaf862b03ff0854a14719ec0`
- data_R/Tags_manipulated_and_visiting.csv — `48a2ed7b76d27402daf9544a1d9836165b7c0e44`
- data_R/Ficus_Sycamorus_Experiment_Analysis.Rmd — `089de09fc57bfdc2b475c80c1eb9cae0c24c2096`

## Deterministic source check

The 5 nonempty cave × manipulation-period records give 16 manipulated bats, 56 naive bats and 14 total visitors. The per-tag visitors file has 14 unique bat tags; the author's script explicitly identifies four smeared tags, yielding 10 naive visitors. Therefore the published naive proportion is independently recomputable from author table/ID membership as 10/56 = 0.1785714 (17.86%). This only verifies the descriptive count, NOT the p-value or causal identification. The original 2024 article reports its permutation comparison p<0.01 for 1–6 night comparisons; the independent null distributions were not locally rerun.

## Source discrepancy, not a biological reanalysis

On 19 July 2020 for the Gershom roost, the author `Field_Manipulation_Table.csv` contains:
- `No_manipulated_bats=4`
- `n_naive=19`
- `n_total=22`

But 4+19=23; the published article's corresponding Table 1 reports 23 total and sums to 72 overall. Thus the raw author CSV `n_total` has a one-bat undercount and sums to 71 instead of 72. The naive denominator used by the Rmd's `man_tags_nights$observed_proportion` explicitly is 56 (not the erroneous total), and the tag-based 10 visitors are unaffected by this cell; **the discrepancy does not by itself overturn the published main result**. A descriptive all-bats proportion computed from `n_total` would instead use a wrong denominator (14/71 instead of 14/72).

The separate Dryad tracking README quotes 14 manipulated and 57 control tracked bats; it describes a movement-track distribution that should not be conflated with the manuscript's broader included field-experiment roster without checking inclusion logic and dataset versions. It is NOT proof that the manuscript's 16/56 table is incorrect.

## Inferential boundaries

The study is strong evidence for an experimentally introduced conspecific-borne odour cue changing where naive bats flew to assess known trees. Neither this count check nor the study proves that personally memorized tree locations were verified for each of 56 bats, that specific odor–location associations had a unique cognitive substrate, that natural odor intensity matches the manipulation, or that memory and social information always complement across species. Individual bats are nested within manipulation date/roost; 56 is not 56 independent field treatment assignments.

New contribution here: transparent provenance/quality audit; original biological discovery belongs to Lourie et al. 2024.
