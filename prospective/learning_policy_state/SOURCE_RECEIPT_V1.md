# Spatial-learning policy-state source receipt v1

## Status

**PROSPECTIVE EXTERNAL FORMATION/UPDATING PROGRAMME. NO RAW LEARNING OUTCOME OPENED.**

Branch:
`prospective/learning-policy-state-v1`

This programme is independent of:
- JAE v0.4.0;
- the adult field-maintenance paper;
- the Teshima 2026 task-reset / low-dimensional-policy diagnostics.

## Source paper

Yamada, Y., Mibe, Y., Yamamoto, Y., Ito, K., Heim, O. & Hiryu, S. (2020).
*Modulation of acoustic navigation behaviour by spatial learning in the echolocating bat Rhinolophus ferrumequinum nippon*.
Scientific Reports 10:10751.

DOI:
`10.1038/s41598-020-67470-z`

## Public raw dataset

Figshare article:
`19102712`

DOI:
`10.6084/m9.figshare.19102712.v1`

Title:
*row dataset for article entitled "Modulation of acoustic navigation behaviour by spatial learning in the echolocating bat Rhinolophus ferrumequinum nippon"*

Licence:
CC BY 4.0.

The dataset was explicitly identified by later peer-reviewed work as the raw dataset used in the 2020 paper.

## Published design facts

The source study reports:

- 14 *R. ferrumequinum nippon*;
- two acoustic conditions:
  - acoustically permeable obstacle walls;
  - acoustically reflective obstacle walls;
- 7 individuals per condition;
- all animals naïve to their assigned obstacle layout at first exposure;
- 12 repeated flights per animal;
- no obstacle collisions across repeated trials.

Published learning effects include:
- reduced meandering width with familiarity;
- changed pulse-emission behaviour;
- in the permeable condition, maximum speed rose from about 2.5 m/s at flight 1 to about 3.4 m/s at flight 12.

These published findings are inherited source knowledge, not new outcomes.

## New question

The task-reset programme indicates that individual movement-policy information in *R. nippon* is approximately low-dimensional.

The unresolved causal question is:

> **Does spatial learning move all individuals along common policy axes while preserving stable individual coordinates, or does learning erase/reorder individual policy differences?**

This directly separates:

1. **policy updating**
   - experience changes the mean behavioural state;

from

2. **individual-policy maintenance**
   - animals retain relative personal positions despite updating.

## Core model family

The new programme will test whether repeated-flight behaviour is compatible with:

[
y_{it}
=
mu_t
+
	heta_i
+
epsilon_{it},
]

or, where condition matters,

[
y_{ict}
=
mu_{ct}
+
	heta_i
+
epsilon_{ict}.
]

Here:
- (mu_{ct}) is the learning/environment trajectory shared across individuals;
- (	heta_i) is persistent individual policy position;
- (epsilon) is residual trial variation.

A stronger individual reaction-norm model may later add individual learning slopes, but only under a separately frozen contract.

## Why this matters

If shared learning changes coexist with persistent individual offsets, then the emerging mechanism is:

> **experience updates policy, while individual specialization is maintained as a persistent offset/state within that adaptive policy space.**

This would reconcile:
- learning/plasticity;
- persistent individuality;
- lack of continued spatial partitioning.

## Firewall

Before any raw row value is opened:

1. inventory Figshare metadata;
2. identify files and schemas;
3. identify individual, condition, trial, speed, path-shape and sensing columns without reading data rows;
4. freeze primary endpoints and support rules;
5. only then open row values.

No raw result may modify JAE v0.4.0.
