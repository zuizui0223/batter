# 2026-10-10 PRIOR-ART FALSIFICATION: "same space, different time" already tested in this species

**Evidence type:** independently published original research and previously executed source-backed observations. No new 2024 OSF bat event values reopened and no new outcome models. Frozen JAE/BE statistics remain untouched.

## Source that materially changes the novelty claim

**Melber, M., Fleischmann, D. & Kerth, G. (2013)**. *Female Bechstein's Bats Share Foraging Sites with Maternal Kin but do not Forage Together with them — Results from a Long-Term Study.* **Ethology** 119:793–801. DOI https://doi.org/10.1111/eth.12123 .

The original abstract explicitly reports 22 female *Myotis bechsteinii* tracked over several years (9 mother–daughter dyads, 7 less-closely related dyads, 6 unrelated dyads). Spatial overlap of foraging ranges was positively associated with relatedness, while **most colony members that shared foraging areas were unlikely to forage together** based on simultaneous radio-fixes. This is published **space–time dissociation**, and its authors already explicitly discuss kin selection vs direct social foraging benefit.

Earlier directly relevant foundation: **Kerth, Wagner & König (2001)**, *Roosting Together, Foraging Apart: Information Transfer About Food Is Unlikely to Explain Sociality in Female Bechstein's Bats*, DOI https://doi.org/10.1007/s002650100352 .

**Hernández-Montero et al. (2026)**, DOI https://doi.org/10.1002/ece3.73604, explicitly state that the 65-receiver BLE grid was designed using prior VHF telemetry **at the same study site** (Melber et al. 2013). This makes the prior work **directly relevant same species/site historical antecedent** but does not establish overlap in the identical marked *individual cohort* (2013 vs 2024) or equivalence of data quality/time scales.

## Current original public data (new measurement, not new law)

Frozen source: author OSF `sg6dz`, 16 bat×dated-night CSVs (2024-05-15/16), eight distinct RFID/transmitter-paired animals. Prior source-backed GitHub runs:
- all-night same-receiver within 60 source-clock seconds: 17/28 bat dyads positive (May 15), 14/28 (May 16); joint receiver-minute counts 347 and 516 respectively; [CI 38012845003](https://github.com/zuizui0223/batter/actions/runs/38012845003).
- post-outcome exploratory binary recurrence: 13/28 dyads positive on both full source nights; [CI 38014108133](https://github.com/zuizui0223/batter/actions/runs/38014108133).
- ONE fixed post-outcome central scheduled-window sensitivity 23:00–02:00: positive 6/28 and 8/28, with 5/28 positive on both nights; source-minute incidence 17 and 108; [CI 38014791593](https://github.com/zuizui0223/batter/actions/runs/38014791593).

**What the comparison is NOT:**
- BLE shared receiver in same 60 seconds (~35 m station footprint, possibly up to ~70 m pairwise physical distance) is **not** Melber et al.'s *simultaneously located physically close foraging bats*.
- The 23:00–02:00 window is NOT the 2026 source authors' 2h post-sunset / 3h pre-sunrise foraging-area exclusion. Original timestamp wall-time zone and receiver uptime/drift remain unverified, and V1a night-wide bins can include commuting and roost swarming.
- The author paper retained **7 of 8** May-2024 tagged animals for published UD analysis, while our source-wide eligibility was all 8. The original authors' UD and ours cannot yet be compared pairwise within an established identical cohort.
- No physical bat–bat contact, social attitude, direct reward/prey capture, 3D height, sensory masking or randomized competition manipulation is contained in the present source-derived co-receiver aggregates.
- 28 possible dyads share eight animals and two nights; no independent dyad-replicate n=28 and **no significance test** of excess co-occurrence has been performed.

## Consequence: change the target from descriptive repeatability to a novel measurable causal boundary

**Rejected novelty propositions:**
1. "Some bats retain individual space use without temporal co-foraging" — known by 2001/2013.
2. "Home-range overlap is compatible with time separation" — known by 2013, same species/site historical line.
3. "Repeated pairs at shared receivers imply social attraction" — invalid without availability, clock and full station-outage controls; may be dominated by transit/roost access.
4. "One-minute co-receiver recurrence demonstrates stable personal 3D motor policy" — different observational level; no.

**Only defensible narrower novel inference if new independent data later permit:** explicitly compare personal *motor/sensory-response rules* measured on truly held-out occasions, physical overlap and controlled interference **within the same individuals**, and report independently verified prey capture/time/energy consequences. In the current open-source constraints, no fully crossed dataset meeting all these levels has been validated, and the two-night receiver dataset **cannot** test that claim.

If a *methodology* paper is desired, independent hardware/time validation of BLE receiver co-detection against simultaneous high-resolution animal positions and known noninteracting controls could be interesting; existing 2026 validation was **human GPS vs BLE UD**, not a calibration of social pairwise *synchrony*. This requires new joint ground truth, not another permutation of two-night source events.

## Scientific editorial decision

- **Maintain actual V1a, V1b, V2 receipts as descriptive independent observational facts, with explicit source-level limitations and post-outcome labels.**
- **DO NOT** frame them as a third scientific discovery of "share space but not time", which is directly anticipated by Melber et al. 2013.
- **Do not** use co-receiver data as support for an adaptive explanation of frozen JAE vertical-identity results.
- Complete a **source-code-only engineering audit** of clock/original UD inclusion and station-uptime metadata if obtainable. If unavailable, STOP inferential social-time use rather than attempting more hour/RSSI/tolerance windows.
- JAE and Behavioral Ecology submissions require human PI/coauthor review, not continued unblinded postfreeze mechanism searches.

**Final prior-art gate:** `STOP_CLAIM_OF_NOVEL_SPACE_TIME_DISSOCIATION`. The JAE paper's distinct conditional **terrain-relative vertical distribution-shape** question remains unchanged.
