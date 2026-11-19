# H1 ecological-context direct-data test: field Saccopteryx distress playback (source gate V1)

2026-11-19. This protocol is committed **before** downloading or inspecting the supplementary trial outcomes. No new biological effect is claimed. It does not alter the frozen JAE bat-individuality paper.

## Prior art / provenance
Eckenweber & Knörnschild (2016), Royal Society Open Science 3:160151, DOI 10.1098/rsos.160151; original supplement `rsos160151supp1.xlsx` attached to original article and PMC4892459. Original paper already establishes context-dependent reaction (within or near a stable roost, not at nearby foraging ground). This analysis must **not** claim that finding as new.

Original sampling (published): 19 valid playback sessions on 11 Saccopteryx bilineata colonies, sampled during 2012–2014; eight colonies resampled in different years. Each session covers three speaker locations: (1) inside roost, (2) 3–5 m proximity, (3) foraging area 10–25 m away; each with conspecific Saccopteryx and heterospecific Molossus distress-call playback. Responses are S. bilineata echolocation counts before, during and just after call presentation. The previous authors combined playback and post minutes as "reaction" and used reaction minus pre activity as responsiveness. Counts are acoustic detections, not distinct individual bats.

## Data and hierarchy gate — outcome-blind
Obtain exact published original Excel (or original PMC supplementary archive containing it). Inspect ZIP/XLSX integrity, sheet names, header cells, row counts, source URL and SHA-256. Do not ingest animal outcome values until primary analysis data columns are named in a subsequent frozen amendment. Download gate statuses distinguish open public metadata from accessible raw bytes. Original file is not committed to GitHub.

A separate 2015 Carter et al. Molossus distress playback article (DOI 10.1371/journal.pone.0136146) points to an archived Figshare DOI 10.6084/m9.figshare.1454597 with both Molossus and Saccopteryx response columns under silence/noise/distress. Check via official Figshare metadata whether original files exist; do NOT assume 0-kB UI indicates a usable original archive.

## Confirmatory target once schema/source eligible
Principal research question: **does the effect of the same alarm/distress signal change with the social relevance of a place**, versus merely being greater at a dense roost irrespective of which species called? This is a prior-art mechanistic boundary check, not a new untested theory.

With within-session paired conspecific Saccopteryx and heterospecific Molossus trials and documented before/playback/post fields, compute (only when each cell is measured):
- C_{session,location,caller} = mean(reaction and post period detection rate) − pre detection rate (published direction, not assuming equal phase duration).
- D_{session,location} = C_{conspecific} − C_{heterospecific} (call-specific contrast at same site and session).
- Key target: delta_i = D_{inside-roost} − D_{foraging-ground}, with near-roost as descriptive intermediate. This difference-of-differences conditions on overall locale, but is **not automatically a randomized causal contrast**; speaker location and sequence order may be confounded with dawn/dusk and active density.
- If treatment order is not counterbalanced or data cannot distinguish caller-specific pre observation, STOP causal cue×place interaction; report only conditional within-session contrasts.
- Assess uncertainty at 11 **colony** clusters with cluster-level sign-flip/permutation and leave-one-colony-out descriptive direction; 19 sessions are repeated measures, not 19 independent colonies. Define outcome contrasts once, no outcome-dependent exclusions.
- A distinct *across-study generality test* would require another study with identical signal, response, context, controls, and independent colony populations. 2015 Carter et al. uses a different mix of sampling and 2026 Wilson different caller signals/sites/species; neither automatically supplies a matched replication.

## Key structural and interpretive stops
- If fewer than 8 independent colony clusters contain fully matched original measurements, do not report confirmatory population-wide p-values; present descriptive sample, missingness and bounds.
- No population-specific individual identities; repeated detection passes are NOT independent bats.
- No inference on reciprocal altruism, group mobbing, spatial memory or 3D individual strategies merely from phonotaxis.
- No biological outcome sign from manuscript abstracts alone counted as a new independent post hoc observation.
- Do not conflate original-source reanalysis, known mathematical negative controls and new biological effect/causality.

Primary sources: https://doi.org/10.1098/rsos.160151 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC4892459/ ; https://doi.org/10.1371/journal.pone.0136146 ; https://doi.org/10.6084/m9.figshare.1454597 .
