# 2024 Rousettus source bridge: can original roost odour data estimate the new memory × social-timing interaction?

**2026-11-19. Result: STOP individualized causal interaction in the already-published archive, due to missing exposure-denominator and memory measurement crosswalk.** This is a *source-structure* statement, not an outcome-level null, and not a claim about absence of social learning.

Original source: Lourie et al. (2024), DOI \`10.1098/rstb.2024.0060\`, authors' published repository \`EmmLourie/Information-transfer-analysis\`, dataset for GPS tracks Dryad \`10.5061/dryad.51c59zwgp\`.

## Source fields actually inspected (schema-only)

- \`data_R/Field_Manipulation_Table.csv\`: \`date_manipulation,No_manipulated_bats,Cave_roost,n_total,n_naive,n_visited_North_Tree,n_visited_either_tree\`. This is an **aggregate** treatment/date/roost count, not the 56 individual naïve bat identifiers and their no-visit outcomes.
- \`data_R/Tags_manipulated_and_visiting.csv\`: \`tags,Visited,When?,Cave origin,date_manipulation,Nights_after_manipulation,visit_start,visit_end,time_of_visit,n_trees_before_same night,n_trees_before_all_nights,n_trees_after_night,Explored_more_that_night\`. Previous original audit verified 14 individual *visitor* tags, four manipulated and 10 naïve. This table is **outcome-selected** (all visitor rows) and is not a complete list of **56 exposed naïve bats**, nor a complete tagged nonvisitor outcome roster.
- \`data_R/ind_info.csv\`: \`TAG,TAG_Week,cave_origin,sex,age,weight,FA,pregnency,testis\`. Contains demographic/timing metadata but no explicit \`cue_exposure_id\`, manipulated vs naïve exposure, or resource timing cue-assignment field.
- \`data_R/visits_to_f.sycamorus.csv\`: \`TAG,duration,num_loc,position_qlt,dummy,medX,medY,night_number,time_start,time_end,month,X_tree,Y_tree,tree_sp,cluster_ID,TAG_Night,date_global,Number_of_Nights,cave_origin\`. Supports historical focal-tree *visits*, not an independently calibrated individual spatial-memory success probability \(m\).
- \`data_R/all_tree_visits_main.csv\` header was not returned by the line-based connector for its large size, but the source README and original Rmd describe it as GPS-derived *tree stops*. The author implementation assembles the experiment response from **aggregated** \`Field_Manipulation_Table.csv\`, not a complete individual-by-exposure matrix.

Original repo README says the field-manipulation comparison uses the aggregate table of bat visits and bats that did not visit; the main tree-stops tables are separated by analytic inclusion (>3 nights for tree-encounter analysis). Original authors' 2024 study already established the real behavioral odor-cue result.

## Prevent selection bias and circular "memory" in H1

One might regress post-manipulation *visit* on pre-experiment number of visited trees among the 14 visitor tags. That is invalid as a response model: it lacks the 46 naïve *nonvisitor* IDs and likely has differential GPS coverage, and \`n_trees_before\` measures experience/exploration, **not probability of remembering the focal Ficus tree in a no-cue navigation test**. The 10/56 naïve visitor ratio is genuine descriptive prior art but is not a joint estimate of \`m\` and cue success rate.

To identify the new decision model for this source, require **for every exposed naïve individual**:
1. stable tag ID × site × exact exposure date/roost, including nonvisitors, and a valid bat observation effort/exposure denominator;
2. independently measured pre-cue re-location success of the *specific focal target* (or a validated no-social-cue memory task), not total trees visited or Y=postvisit itself;
3. cue positive/negative availability base rates and error rates, resource reward, visit/search costs and an actual cue-free control group with comparable exposure/effort;
4. held-out genuinely independent site/season validation rather than adjusting memory thresholds to the original significant response.

**Decision:** Author data are excellent for the published social temporal-cue story but do not currently identify the quantitative private-memory×social-value *new effect*. No extra same-archive significance fishing. Existing 10/56 count remains untouched; this document changes no JAE/BE result.

Source: https://github.com/EmmLourie/Information-transfer-analysis and https://doi.org/10.1098/rstb.2024.0060 .
