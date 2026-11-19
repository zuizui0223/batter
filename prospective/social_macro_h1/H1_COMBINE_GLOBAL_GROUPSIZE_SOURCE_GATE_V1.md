# Global bat COMBINE social-group size: original-data admissibility gate v1

Date 2026-11-19. Status **PRE-OUTCOME STRUCTURE GATE**, not a pre-registered independent study. Safi & Kerth 2007 original male social-group coding was publisher 403; no substitute is called 'male sociality'.

## Original sources
Soria et al. 2021 COMBINE (Ecology DOI 10.1002/ecy.3344), Figshare version 4 DOI 10.6084/m9.figshare.13028255.v4, source article_id 13028255. The codebook defines `social_group_n` as number of individuals spending most of their daily time together, **not** feeding information, male grouping, or reciprocity. COMBINE contains 6234 mammal species/54 traits and imputes missing nonbiogeographic traits given coverage. The DATA-S1 source includes original trait provenance and original/imputed datasets. Do not assume a row with a number is an observation.

## Source-only preliminary gate (no trait response distribution)
1. Fetch **Figshare version 4** public metadata and each original file's metadata (name, size, MD5), verify package authenticity by original MD5, ZIP structure and member list.
2. Inspect ZIP member names and schema headers only, not the values of `social_group_n` or diets in the first gate. Do not commit original ZIP or animal-level values.
3. Identify original-vs-imputed indicator and exact species/order/taxon field, response field, diet/foraging fields, body mass and roost substrate fields if present. Avoid treating all taxa with data as bats by using current taxon labels explicitly.
4. Freeze the species coverage audit design after schema gate, before calculating direction/effect.

## Subsequent admissible descriptive coverage audit
Among order Chiroptera, report total taxa, nonmissing *directly measured* social_group_n, nonmissing diet, intersection, distinct families and continents. If only an imputed group-size value exists, separate it; no species-level H1 inferential model can use it as validated social behavior. Count male-specific social groups and direct info-sharing separately (likely absent).

## Conditional ecological comparison (only if at least 30 independently observed group-size taxa)
Exploratory alternative question: whether *daily social group size* covaries with plant-vs-invertebrate diets, foraging stratum and body size across bat species. The following are strict limitations: (a) roost substrate/space availability may dominate group size; (b) taxa nested in family/phylogeny and regional sampling; (c) source-derived reused values and imputation bias; (d) this is a test of **group size**, NOT social information, male group formation, resource predictability, cognitive memory, or reciprocity.

Use log1p(social_group_n) and group-equal species observations; source metadata controls; phylogeny only if a taxonomically reconciled independent tree posterior is available. Do not silently upgrade a simple correlation to a phylogenetic evolutionary causal result. The 2007 Safi/Kerth study is prior art and not an external test for this different response.

If <30 genuinely observed bat species overlap or no known measured-vs-imputed distinction, STOP formal association and report a descriptive data-quality limitation. No unauthorized source replacement or forcing 'positive' result.
