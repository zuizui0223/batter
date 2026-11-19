# Dixon et al. 2023: cue-conflict trial original-source gate and cognitive-niche prior-art firewall

Date: 2026-11-19. This is a *source-first extension of an already published experiment*, not the first test of diet × memory, not a new experiment, not a registration preceding the original authors' observations. Main JAE tracking result remains frozen.

## Original biological source

Dixon, Carter, Ryan & Page (2023) *Behavioral Ecology* 34:325–333, DOI [10.1093/beheco/arad001](https://doi.org/10.1093/beheco/arad001), article original data citation **Dixon et al. (2022) Dryad DOI `10.5061/dryad.pzgmsbcr7`** (cite checked in published journal reference list). Prior paper tested male *Artibeus jamaicensis* (frugivore, 12 trained) and *Lophostoma silvicolum* (predator of katydids, 10 trained) from Panama, both Phyllostomidae. Individual bats learned sound + scent + rewarded location, then three-way location vs odor, location vs sound, sound vs odor conflicts (one feeder was unrewarded/novel control); first choice and hourly counts were recorded. The paper already found **both species prioritized the trained location**, even the species that naturally hunts by acoustic prey cues.

Published first choices (DO NOT present as independently novel):
- *A. jamaicensis*, location vs odor 7/9 location first; location vs sound 8/11.
- *L. silvicolum*, location vs odor 8/10; location vs sound source text contains a **denominator discrepancy** ('five of eight' versus 'N=9' and 1 sound + 3 controls = 9). Treat as uncertain until original Dryad IDs verified, not fixed by assumption. Do not infer all 10 bats took every test.
- The paper's Table 1 collates five phyllostomid species preferring location (nectar-feeding *Glossophaga commissarisi*/*G. soricina*, fruit-feeding *Carollia perspicillata*/*A. jamaicensis*, predatory *L. silvicolum*). Original 2005 and 2010 papers may reuse or share groups; these are **prior art** not five new independent regional replicates.

## Outcome-blind data gate

1. Query original Dryad dataset `10.5061/dryad.pzgmsbcr7` by authoritative Dryad API and DataCite DOI (must confirm correct resolution, don't fabricate a file). Try metadata via REST, confirm paper link, listed CSV/TSV/R scripts. Any 401/403/404 => explicit source STOP, not an ecological null. Preserve URL/status.
2. If verified source exists, only fetch files under a conservative cap (e.g. 20 MB), record actual bytes+SHA256+header/categorical data schema before outcomes. **No raw bat or treatment rows committed to batter**, no dropping nonchoice records by outcome after seeing signs.
3. Determine whether physical bat IDs exist for each test and species, and whether training trials / first/total choices are separated; train/test condition must preserve within-bat link. If only group summaries, STOP joint individual contrast.
4. Species and experimental context are linked to **location versus physical feature cues**, NOT social timing from a conspecific, so their source cannot estimate the `H1_TWO_CHANNEL_DECISION_RULE_AND_FALSIFIERS_V1` memory × social timing Bayes model. A species's preference for trained location is **not** a quantitative independently measured probability of correct navigation in a natural patch, and no social demonstrator was used.
5. If source available, permitted *reanalysis* is a bounded source replication of published within-individual cue choice with those denominators, and a source-readiness audit for additional original experiments. **No global phylogenetic H1 or interpretation of individual vertical distribution shapes as memory.**

## Implication for next coherent theory

The five species in the published Table 1 span nectar, fruit and predatory diets but use location in their specific experimental paradigm. Thus the categorical assumption `invertebrate/predator diet => little spatial learning` is *already contradicted in the literature*, not a fresh global discovery. A more general ecological hypothesis must separate **experimental cue reliability / spatial navigational context / training exposure** from trophic guild; this was explicitly proposed by the original authors. Purely using the original 2023 data to restate this claim is not publication novelty.

Source links: https://academic.oup.com/beheco/article/34/3/325/7055811 and https://doi.org/10.5061/dryad.pzgmsbcr7 .
