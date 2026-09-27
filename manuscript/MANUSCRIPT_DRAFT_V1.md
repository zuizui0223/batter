# Individual identity predicts vertical-state use in European free-tailed bats despite poor species-level transfer

**Working manuscript v1**  
**System:** European free-tailed bat, *Tadarida teniotis*  
**Data:** Movebank Data Repository DOI 10.5441/001/1.52nn82r9

## Abstract

Animal movement is often summarized at the species level, yet individuals may occupy the same horizontal landscape while using vertical space differently. We revisited a prospectively frozen analysis of eight European free-tailed bats in which the species-level location-conditioned altitude distribution was vertically thick but failed to predict two independently sealed individuals better than a species marginal altitude distribution. We asked whether that failure reflected stable individual specificity. Using the same 18 five-kilometre horizontal cells and fixed altitude bins, we divided each individual's eligible tracking data chronologically into early and late halves. Early individual maps were scored on all individuals' later observations, yielding a complete 8 × 8 transfer matrix. The identity-matched diagonal exceeded all but 0.017% of the 40,320 possible source-identity assignments (mean gain +0.168 nats per event; exact one-sided P=0.000174), with positive own-map gains in 6/8 individuals. Three prospectively frozen refinements then asked whether this individuality reduced to a marginal altitude preference, an individual-by-location residual after marginal preference was controlled, or individual reweighting of a shared spatial template. None met its frozen support rule. Thus vertical-state use was temporally repeatable and individual-specific, but the individuality was not captured by any single simple decomposition tested here. A vertically thick species-level state space can therefore conceal persistent individual structure while remaining poorly transferable as one species-average three-dimensional map.

## Introduction

Three-dimensional movement creates an ecological state space that is easily compressed by two-dimensional maps. For flying animals, individuals occupying the same broad horizontal range can still differ in flight altitude, vertical commuting structure, and use of atmospheric or topographic space. A species-level vertical niche therefore need not describe every individual equally well.

The key distinction is between **vertical thickness** and **transferable vertical organization**. A population can occupy many vertical states after horizontal location is known, yet the detailed distribution of those states may not generalize to new individuals. Such non-transfer can arise for at least two biologically different reasons. Vertical structure may be noisy and unstable, or it may be stable but individualized.

A preceding prospectively frozen analysis of European free-tailed bats created exactly this contrast. In the model pool, conditional vertical entropy was 1.392 nats, equivalent to 4.022 effective altitude states, but the species-level `P(z|x,y)` produced negative held-out gains for both sealed bats relative to `P(z)`. The correct conclusion was therefore not an absence of vertical structure, but a failure of species-average vertical organization to transfer across individuals.

Here we test the individual-specialization explanation directly. We preserve the original horizontal grid and vertical bins, split every tracked individual chronologically, and ask whether an individual's early vertical map predicts its own later states better than maps learned from other individuals. We then use three frozen explanatory refinements to test whether any identity signal is reducible to a simple marginal altitude preference or a simple individual-by-location component.

## Methods

### Source and inherited geometry

We used the checksum-pinned Movebank tracking stream from the original ODSP bat analysis (MD5 `570872ab7aba674b9bdc2f2ee6044a71`). The data contain eight tracked *T. teniotis* individuals with same-event longitude, latitude, timestamp and GPS height above mean sea level.

We inherited without modification the original primary geometry:

- EPSG:3035 horizontal coordinates;
- 5-km cells;
- the 18 frozen cells admitted by the original model-pool structural gate;
- fixed altitude bins `[-inf, 0, 50, 100, 200, 400, 800, 1600, 3200, inf]` m MSL.

The altitude axis is therefore not height above ground and is not terrain corrected.

### Temporal split

Within each individual, eligible events were ordered by timestamp. The first half was assigned to the early period and the second half to the late period. Every individual retained at least 100 eligible events in both halves.

The individual was the replication unit. Event counts were not treated as independent biological replicates.

### v1: identity-transfer analysis

From early data we estimated a species-level cell-specific altitude distribution and an individual-specific cell distribution. Individual distributions were shrunk toward the species cell distribution with a fixed equivalent sample size of 20 events.

For every source individual `i` and late target individual `j`, we calculated mean log-probability gain of source map `i` over the species cell-specific distribution on target `j`'s late events.

This yielded an 8 × 8 transfer matrix. The primary statistic was the equal-individual mean of its identity-matched diagonal. The exact null enumerated all `8! = 40,320` assignments of early source identities to late target identities.

The frozen support rule required an exact one-sided permutation P ≤ 0.05 and positive diagonal gain in at least six of eight individuals.

### Explanatory refinements

After v1 closed positively, three successive refinements were frozen and executed without changing the inherited cells, bins or early/late split.

**v2: residual location interaction.** Each individual's marginal altitude preference was first absorbed into a marginal-adjusted cell baseline. We then tested whether raw individual-by-cell information provided additional held-out gain.

**v3: marginal altitude identity.** Individual marginal altitude distributions alone were transferred across late individuals and tested with the same exact identity-permutation design.

**v4: reweighted shared template.** A shared species cell template was reweighted by each individual's marginal altitude distribution without fitting a residual individual-by-cell interaction.

Each refinement used its own frozen support rule and could not override the earlier v1 result.

## Results

### Vertical thickness existed but species-average transfer had failed

The preceding ODSP endpoint estimated `H(Z|X,Y)=1.3919` nats, equivalent to 4.022 effective vertical states. Nevertheless, the two independent sealed bats had species-level conditional-versus-marginal gains of -0.4354 and -0.02194 nats per event.

### Individual identity was strongly recoverable across time

The new v1 analysis retained 5,473 events inside the inherited 18-cell support.

The identity-matched early-to-late diagonal mean gain was **+0.1682 nats per event**. Under all 40,320 permutations of early map identity, the null mean was -0.0367 and the 5th–95th percentile interval was -0.1566 to +0.0707. The exact one-sided probability of obtaining a mean identity assignment at least as large as observed was **P=0.000174**.

Six of eight bats had positive own-map gain over the species cell-specific map. In five of eight, the individual's own map was the strict best-performing map among all eight candidate individual maps for its late observations.

The primary category therefore closed as **individual-specific vertical-state prediction supported**.

### Simple decomposition did not isolate the identity signal

The stricter v2 location-interaction refinement did not pass. After marginal altitude preference was absorbed, the residual identity-matched gain was +0.0240 nats/event (P=0.1605; 5/8 positive). Fixed shrinkage sensitivities were also non-supportive.

Marginal altitude preference alone was likewise insufficient. In v3, the identity diagonal was unusually high relative to random identity assignments (P=0.0224), but its absolute mean gain over the species marginal was -0.0311 nats/event and only 4/8 individuals were positive, failing the frozen support rule.

Finally, reweighting a shared spatial template by individual marginal altitude preference did not pass: v4 diagonal gain -0.00016 nats/event, P=0.0663, 5/8 positive. Both fixed shrinkage sensitivities remained outside the frozen support rule.

## Discussion

The combined result resolves an apparent contradiction in the original species-level analysis. European free-tailed bats occupied a vertically thick state space, but one species-average location-conditioned vertical map did not transfer to new individuals. The new early-to-late analysis shows that this failure of species-level transfer coexists with strong temporal repeatability of individual identity.

Thus the original non-transfer result is not evidence that vertical organization is absent. Instead, vertical-state use contains persistent between-individual structure.

At the same time, the follow-up analyses prevent an overly simple biological story. We did not obtain support for a single stable individual-by-location interaction after marginal altitude preference was controlled. Nor did individual marginal altitude distributions alone satisfy the frozen support rule. A model that merely reweighted a shared spatial template by individual marginal altitude preference also failed.

The most defensible interpretation is therefore **complex individual specificity**: an individual's vertical-state distribution is more predictive of its own future use than of another individual's, but the predictive identity signal was not reducible to any one simple component tested here.

This distinction matters for ecological mapping. A species-level three-dimensional niche representation may be descriptively rich while being a poor predictor for a new individual. Conversely, collapsing individual variation into one species map can erase repeatable structure that is ecologically real at the individual level.

The present study is deliberately limited. GPS altitude is height above mean sea level, not height above terrain. We do not infer causal habitat preference, behavioral personality, learning, energetic optimization or fitness consequences. With eight individuals from one published tracking system, the result establishes within-dataset individual specificity rather than species-wide universality.

## Main conclusion

> **A vertically thick species-level state space can conceal temporally repeatable individual structure: vertical-state maps were strongly identity-specific across time even though one species-average map failed cross-individual transfer, and that individuality was not reducible to a simple altitude set-point or location-specific component.**

## Data and reproducibility

The source dataset is public through Movebank Data Repository DOI 10.5441/001/1.52nn82r9. The analysis contract, exact source checksum, frozen geometry, full-permutation tests and result receipts are maintained in this repository.
