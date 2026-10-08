# Wilkinson et al. 2025 clutter tracking public-source structural preflight

**Date:** 2026-10-08. **Evidence:** publication abstract and public Johns Hopkins Dataverse *metadata only*, NOT raw audio/video/flight outcome inspection.

## Authenticated public scholarly source
- Wilkinson, Wang, Cowan & Moss (2025). *Echolocating bats adjust sonar call features and head/ear position as they track moving targets in the presence of clutter*. JASA 157, 2236–2247. doi: https://doi.org/10.1121/10.0036252
- Public data DOI: https://doi.org/10.7281/T1WF3NZ7
- JHU archived repository displays `VideoData.zip` (81.1 MB), `AudioData.zip` (639.8 MB), and README/code, with derived MAT files indexed by **five physical bat labels** `11B5,15BA,63E4,68A7,6C1A`.
- Published experimental task: **perched** *Eptesicus fuscus* track an approaching moving prey-like target with head/ear position and sonar calls while clutter is moved to different target-relative distances and angles. Bats were **not performing free 3D flight trajectories** during the primary tracking task. The authors already show population-level short calls/increased head motion/changed spectral features in clutter; those are published prior art and not novel outcomes here.

## Relevance and strict limitation
This is a real, openly archived, individually labeled **sensory response-to-clutter** source, not a sample of 3D flight paths. It could eventually ask whether identifiable bats differ in their *sensory reaction norms* conditional on well-supported independent sessions, if source metadata documents:
- matched clutter/reference contexts for each bat;
- at least several genuinely independent occasions (not hundreds of adjacent samples within one recording);
- stable physical IDs and device/sensor calibration and randomized/counterbalanced context schedule;
- endpoints frozen before numerical audio/head movement results are opened.

### Current categorical support
Five named bat identifiers in derived archive metadata; contexts of variable clutter described in published experiment. But **distinct dated sessions per bat, device crossover, and matched repeated condition×occasion support were NOT established** from public visible metadata. The 721 MB archive was **not downloaded**, no MAT outcomes/feature magnitudes were opened.

**Decision:** `HOLD_SENSORY_ANALOG_METADATA_ONLY` — a narrow *parallel* candidate for active-sensing context personalization; **STOP_NOT_3D_FLIGHT_PRIMARY** for the particular 3D trajectory/reaction-norm gate of PR #95. Do not treat perched head movement as an animal's 3D flight route or foraging fitness. No repurposing into confirmation after seeing numerical results.

The existence of 5 bat labels and many audio/video samples cannot create extra biological individuals, repeat study days, or make this a randomized fitness experiment.

## Status relation to mechanism
A source-backed sensorimotor parallel could in principle help differentiate context-specific sensing from a pure fixed speed-vigor scalar, but not mediate JAE field vertical occupancy or establish acoustic–spatial substitution without synchronized same-animal flight and outcome intervention data. Do not claim sensory reactions are newly discovered: Wilkinson et al. already tested many such responses at the group level.
