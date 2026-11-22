# Resource-mediated high-D SDM: executable factorial discrimination v1

Date 2026-11-20 | **source-free model, not observed bat ecology** | in draft batter PR #102

## What is now executable

The 5-D utilization model is factored as:

P(i, x, t, b, z) = P(x,t) P(i) pi_i(b | x,t,R) phi_i(z | x,t,b,R)

The earlier model could vary behavior state from externally assigned resource indices; new code in resource_factorial_policy_v1.py explicitly varies both the behavior component (pi) and **within-state vertical kernel** (phi). Coefficients are inputs, not inferred. It constructs four matched models with identical P(x,t):

- base: no resource response in pi or phi;
- state_only: resource changes pi(b), phi(z|b) unchanged;
- height_only: resource changes phi(z|b), pi(b) unchanged;
- state_and_height: both channels allowed.

Each candidate returns a fully normalized 5-D use probability. All four integrate exactly to the SAME P(x,t); this ensures higher-dimensional differences cannot merely masquerade as expansion of horizontal 2-D occupancy.

The paired evaluator scores exactly the same predeclared events using: (a) height conditional on bat, XY and time with behavior marginalized; or (b) independently labeled behavior plus height; or (c) height given independently validated behavior. It returns channel-specific heldout log-score increments and an arithmetic non-additivity term. A non-additive score is not a causal statistical interaction or a mediation effect. If either candidate has zero support on any target event, the contrast fails closed instead of dropping the event.

## How this uses the actual old observations

Existing batter post-freeze **5/5** speed-state and **5/5** speed×turn-state individual specificity, and 4/4 qualified 2-km plus kinematics residual specificity, establish a powerful empirical constraint: a **coarse kinematic state-mixture-only explanation cannot fully remove individual height-map identity in these source cohorts**. But velocity/turn classes are NOT independently measured foraging states, and such tests share sources, so they are not 14 independent biological replications.

The next test is whether *independent resource opportunity* explains vertical variation **within a matched kinematic state** better than a context-blind, resource-free height policy. Positive residual identity is allowed to coexist with high physical 3-D overlap and no positive spatial R3–R1 AUC.

## Independent source data admission, dated status

1. **Lourie–Nathan Rousettus 2024 Dryad** DOI 10.5061/dryad.51c59zwgp: official dataset/version/file metadata gate PASSED. Original 3-tiny-CSV header-and-checksum workflow #44682168574 FAILED when the official file download returned **HTTP401**. Those originals were NOT opened, joined or reinterpreted. The experiments manipulate odor cues at fruitless Ficus targets, NOT measured food supply; no valid 5-D trophic test regardless.
2. **Goldshtein et al. 2020 Leptonycteris** DOI 10.17632/jxghjjsttw.1: original publication confirms GPS-derived height above ground, mapped cactus positions/flowers for 8 tracked bats within the same study. Added strict original Mendeley metadata gate and synthetic tests. Workflow #44683043418: source-free job PASS; live official Mendeley metadata GET **HTTP401**, so original filenames, bytes, bat height columns and cactus resource joins remain UNVERIFIED. Do not retry by guessing download links or treating paper data as already opened.
3. **Existing NeoBat 35-plant source-disjoint input**: 36/84 bat-country folds prefit; true ecological M3–M1/N1 remains NOT ESTIMATED. Its 49-fold climate-only presence-source shadow showed no consistent linked fruit partner gain. It cannot be welded to unrelated 500-m wild individual GPS cohorts to claim independent food-linked 3D behavior.

## Frozen pre-empirical comparison and stopping rules

- Outcome: held-out GPS height state on the same bat source, identical eligible events and height reference; whole-night or bat-ID validation; uncertainty clustered at bat / distinct field site rather than fix-level bootstrap.
- Exposure: true independently enumerated resource availability at spatial/temporal resolution supported by the same GPS survey, not modeled from bat visits or linked literature records alone. Availability measurement timing must be source-verified.
- State: classify from independent video or XY-time kinematics only **before** numeric heldout height; never use Goldshtein's published cactus visit criterion, which includes **height below 20 m**, as a height predictor.
- Counterfactual: location / source-matched resource permutation within mapped survey blocks (not NeoBat degree-rewired species links when predicting patches of one cactus species), same observation effort and holdout splits.
- Null outcomes: neither candidate original archive yielded verified joined biological values in this turn. Both have a source-access STOP. Synthetic coefficient change, simulated log score and mathematical MI never qualify as confirmed ecological results.
- Main manuscript source frozen. New code and source metadata gates stay in draft PR #102.

## Next unblocked empirical objective

Obtain independently accessible original resource × altitude **row-level data** through the publishers' authorized download interface, or discover an alternative original publisher-hosted archive with independently verified hashes. Qualify file headers and exact time/animal/cactus join BEFORE any response/model selection. In the meantime, use the factorial software only for protocol and known-truth validation, not ecological effect reports.
