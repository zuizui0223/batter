# Vrtilek et al. 2018 vampire-bat maze: original-source and within-individual learning-retention protocol

2026-11-19. **Source-focused reanalysis of already published 2018 behavior; not original proof of social learning, novel H1 effect or a pre-2018 registration.**

Original paper: Vrtilek, Carter, Patriquin, Page & Ratcliffe (2018), Royal Society Open Science DOI `10.1098/rsos.172483`, PMCID `PMC6030285`. Supplement deposited at `10.6084/m9.figshare.c.4128575`, named `rsos172483supp1.csv` (~6.5KB) and `rsos172483supp2.r` (~4.7KB), published under article. Official Europe PMC REST `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6030285/supplementaryFiles` may provide original ZIP with both files.

## Exact documented scientific design

Captive common vampire bats `Desmodus rotundus` were trained to escape a 3D maze to rejoin colony. Groups of three naïve bats were tested without a trained demonstrator, then exposed to the trained demonstrator, then tested after its removal. Published outcomes: no naive bat succeeded in solo before/during all no-demonstrator baseline trials; five naïve bats exited in the demonstrator's presence; **four of those five** escaped afterwards without the demonstrator. The authors distinguish "social learning without directly following" from following and retention mechanisms. No direct tagged spatial memory *probability* measured independently *before social cue* for those five: retention after social experience is not initial private spatial memory m.

### Pre-original-outcome source gate
1. Retrieve original supplement through official Europe PMC/figshare collection, record exact archive/member SHA256, study DOI/PMCID.
2. Inspect header names and categorical levels, and test whether a stable physical individual ID links pre/during/post conditions. **Do not yet inspect exit outcomes or count results** for source schema gate. Confirm triad/colony identifiers and stage/period exposure denominators.
3. Only after field/unit validation, freeze a matched-bat analysis: for each initially naïve bat, `Y_pre`=any successful exit without demonstrator; `Y_during`=any successful exit with demonstrator; `Y_post`=any exit after demonstrator removed. Do not infer absence from unrecorded phases.
4. Primary descriptive transition: P(post success | during success) among exactly the bats with both outcomes. Report post successes and exact binomial uncertainty as **conditional on selected during-success bats**, not an unconditional social-effect estimate. Also count among all original naïve animals with all phases if available.
5. Source controls: compare without-demonstrator repeat trial 1→2 (individual/triad), but don't treat trials as independent bats and don't equate exposure order changes to randomized treatment.
6. Any effects are from one captive colony and one 2018 published test. Maze/rejoining has no food/reward and no ecological resource temporal availability; it cannot estimate H1 cue-value parameters (`m, prior fruiting, sensitivity, reward, visit cost`) or explain existing `batter` vertical individual niches.

## Additional independent within-family falsifier
Dixon et al. (2023) *Behavioral Ecology* DOI `10.1093/beheco/arad001` compared *Artibeus jamaicensis* (fruit) and *Lophostoma silvicolum* (katydid predator) with *trained location vs odor vs sound* conflicts; both favored location in the published original. This is evidence **against coarse guild labels as default spatial-memory scores**. The author's original Dryad accession is listed as `10.5061/dryad.pzgmsbcr7`; direct original metadata access is being audited separately under `h1_dixon2023_original_dryad_gate_v1.py`. *Cue preference ≠ social information transfer* and published 2023 data are from a different cohort/source than 2018 vampire bats.

**STOP** a new global cognition/social information H3 correlation or reciprocity claim from either experiment. The correct research question is how spatial cue reliability and prior experience affect a receiver's learning and social information value in a matched population, with no-cue controls and held-out study/region.
