# Manuscript spine v0.3.1 — predictive architectures of 3-D vertical identity

## Working title

**Bat vertical individuality has conditional and marginal predictive architectures**

Alternative:
**The predictive architecture of individual vertical identity varies across bat systems**

## One-sentence claim

Across four bat taxa, cross-night vertical identity is repeatable but not organized in one
universal way: some systems are **conditional-dominant**, where horizontal location strongly
increases individual vertical information, whereas another independent panel is
**marginal-dominant**, and that balance changes across temporal contexts within a species.

## Biological question

Individual specialization is usually described by horizontal space or resource use. Flying
animals additionally occupy a vertical axis.

Does individual identity recur in vertical state across nights, and is that identity carried
mainly by:

1. an animal-wide vertical distribution; or
2. additional information that appears when vertical state is conditioned on horizontal place?

## Predictive decomposition

For a held-out session:

```text
G_cond = mean log P_self(z|x,y) - log P_other(z|x,y)
G_marg = mean log P_self(z)     - log P_other(z)
G_adv  = G_cond - G_marg
```

We call positive `G_adv` **conditional-dominant** and the opposite pattern
**marginal-dominant**.

Crucially, `G_adv` is a predictive contrast. It is not identical to a latent
individual × location interaction.

## H1. Individual vertical identity recurs across nights

Supported in multiple systems.

The focal early/late identity-assignment test is particularly strong:
*Tadarida* diagonal gain +0.1682, exact permutation p=0.000174, 6/8 positive.

## H2. Vertical identity is universally marginal

Not supported.

At 5 km, *Tadarida*, *Eidolon* and *Hypsignathus* all have conditional identity greater than
marginal identity.

## H3. Vertical identity is universally conditional-dominant

Also not supported.

The prospectively frozen *Phyllostomus hastatus* 2022 panel is marginal-dominant:

- conditional +0.056;
- marginal +0.176;
- conditional advantage -0.120.

## H4. Focal conditional dominance is robust, but stable residual maps are not established

Supported predictive result:

- *Tadarida* MSL conditional +0.428 versus marginal +0.052;
- AGL conditional +0.337 versus marginal -0.255;
- terrain-only conditional +0.007;
- same-bat other-night prediction usually beats contemporaneous other bats;
- direct pairwise conditional self-win exceeds marginal self-win.

But the separately frozen early/late residual-map refinement fails:

- residual gain +0.0240;
- exact permutation p=0.160;
- 5/8 positive.

Therefore the focal data support **conditional-dominant identity**, not proof of a stable
individual-specific place × height route.

## H5. Conditional dominance replicates independently

### *Eidolon helvum*

- 20 evaluable individuals;
- conditional +0.219;
- marginal +0.002;
- conditional advantage +0.217;
- 17/20 conditional-positive.

### *Hypsignathus monstrosus*

- 24 evaluable individuals;
- conditional +0.029;
- marginal -0.021;
- conditional advantage +0.050.

Direct pairwise analyses preserve the same direction in both species.

## H6. Predictive architecture varies within *Phyllostomus*

- 2022: marginal-dominant (+0.176 marginal vs +0.056 conditional);
- 2023: weak conditional dominance (+0.033 vs +0.013);
- 2016 La Gruta: +0.058 vs +0.016.

An untouched 2016 dry-season panel was prospectively frozen to reproduce the strong 2022
marginal-dominant architecture and failed. A simple dry-season explanation is therefore blocked.

## H7. One common uplift mechanism explains the focal result

Not supported. The frozen *Tadarida* uplift-reaction endpoint was weakly estimable and conflicting
(permutation p=0.334).

Mechanism remains open.

## Ecological interpretation

The population-level vertical distribution can be a mixture of non-exchangeable individuals, but
the way identity appears predictively differs among systems.

Some panels carry much more individual information when horizontal place is known. Another panel
carries stronger individual information in the overall vertical distribution.

This difference is ecologically meaningful without requiring a claim that one stable
place-specific route map has been identified.

## Comparative panel

An outcome-blind public search covered 23 Movebank bat parent datasets plus legacy child-handle
recovery. Six sources from four taxa passed fixed repeated same-event x-y-height requirements.
Source admission did not use numeric height outcomes.

## Main figures

1. Concept: marginal-dominant versus conditional-dominant predictive identity.
2. Focal *Tadarida*: conditional/marginal results plus explicit V2 residual-map negative.
3. Architecture plane: x=marginal identity, y=conditional advantage.
4. Independent *Eidolon* and *Hypsignathus* replications.
5. *Phyllostomus* 2016/2022/2023 context instability.
6. Pairwise robustness and scale profiles.

## Paper-level conclusion

> **Individual vertical identity in bat airspace has multiple predictive architectures. Across
> nights, identity may be expressed mainly in an animal-wide height distribution or become much
> stronger when vertical state is conditioned on horizontal place, and that balance can vary
> across ecological contexts.**

## Claim ceiling

Do not claim:

- stable individual-specific place × height maps from the focal dataset;
- personality, learning, optimality or adaptation;
- validated foraging specialization;
- a universal environmental mechanism.

The v0.3.1 claim-language amendment changes wording only; the v0.3 empirical freeze remains
unchanged.
