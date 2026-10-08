# Predator-cue social-call response, original public dataset — structural eligibility v1

STATUS: independent empirical source preflight, NO RESPONSE VALUES OPENED. JAE and previous batter causal/synthetic results untouched.

SOURCES: Gamba-Rios, McCracken & Chaverri 2025 "Recognition of predator cues hinders social communication and group cohesion"; Dryad DOI 10.5061/dryad.6djh9w1d3. Original authors' GitHub public repository https://github.com/morceglo/Predator-recognition , tracked HEAD of main before read. Required original files data.csv, README.md, Analyses.R, calls.xlsx. This is an AUTHOR-DECLARED public mirror from the Dryad README. Do not substitute or mix unrelated dataset versions.

PUBLISHED PRIOR ART, NOT A NEW FINDING:
- Predator echolocation calls reduce response/social calls and cohesion.
- Nonpredator call structure resembling predator can induce cautious response.
- Original Analyses.R already models response ~ treatment*period + (1|bat), response ~ bat_type+(1|bat), and response ~ order*bat_type+(1|bat); pooled temporal and type effects are already analyzed.
- No 3D individual movement trajectories in the author GitHub file inventory. Our task is not to infer spatial accommodation from vocal suppression.

POSSIBLE DISTINCT BIOLOGICAL QUESTION:
Whether social-communication inhibition and its recovery are *stable individual response policies* across independently repeated predator playbacks, rather than only a species-wide mean decrease. This asks for individual-specific cross-event transfer of within-bat suppression, not just large bat random intercepts due to baseline calling rate. Do not use an individual's higher general baseline as evidence of stable *reactivity*.

SOURCE FIRST:
Gate 0 record original public GitHub repo and file blob SHA/commit, raw byte size, and extraction permission. Inspect only CSV header, README and R analysis code without opening response count values. The source's first-class "bat" is described as unique ID; "experiment" may mean a playback type, not an independent experimental session.

Gate 1 read *only categorical keys* bat, experiment, order, treatment, bat_type, period, plus key missingness and row counts; no response magnitudes. Determine if independent trial/session/bout keys are explicitly recorded or can be defensibly constructed from a verified experimental protocol. Do not infer distinct experimental dates from adjacent CSV rows or experimental labels alone.

NUMERIC ELIGIBILITY FOR WITHIN-BAT CROSS-EPISODE REACTIVITY:
- >=12 stable physical bats, each with at least TWO independent predator playback bouts;
- each eligible bout has source-defined before and during response count, and at least ONE after row, with a clearly paired nonpredator control or subject-specific reference;
- >=2 independent eligible predator bouts per bat plus >=2 physically distinct predator stimulus instances (or different dates) to make held-out transfer nontrivial;
- >=24 eligible distinct predator bouts across >=12 bats;
- the original data contain an explicit true bout/date/session ID or author-documented mapping that makes bouts independent.
These thresholds are source STRUCTURAL minima (not outcome-derived). All must pass for proposed transfer test; if not, STOP_NO_INDEPENDENT_PREDATOR_BOUTS. No pseudo-replication of before/during/after rows.

If these gates pass, commit a new NUMERIC outcome contract BEFORE reading "response" magnitudes: one natural baseline-normalized risk-suppression statistic per independent bout, held-out between-bout prediction by true bat vs matched other bat, bat-level uncertainty and rigorous identity permutation. Need guard treatment order/time/acoustic caller identity. No cross-validation on row-level splits.

A *weaker descriptive* within-bat predator vs nonpredator contrast is already partly covered by original study and cannot be promoted to original contribution if repeated-bout gate fails.

PROVENANCE / INTERPRETATION:
This single source is NOT independent validation for an unrelated bat flight coordinate. Source biology has predator-risk/social vocal output, not echolocation frequency compensation, 3D vertical shape, or prey capture fitness. A positive individual response stability would not on its own show fitness value, niche partition or strategy maintenance due to acoustics.

Machine receipt should include code/file content SHAs, CSV header and CATEGORICAL eligible counts, independent bout designation SOURCE-PROVEN only. No raw individual response values, means, fits, graphics, p-values or CI until numerical contract committed.