# Naive-learning policy decomposition source receipt v1

## Status

**PROSPECTIVE EXTERNAL LEARNING PROGRAMME. NO RAW ROW VALUE OPENED.**

Branch:
`prospective/naive-learning-policy-decomposition-v1`

This programme is separate from JAE v0.4.0 and from the completed task-reset post-primary analyses.

## Source paper

Yamada, Y., Mibe, Y., Yamamoto, Y., Ito, K., Heim, O. & Hiryu, S. (2020).

*Modulation of acoustic navigation behaviour by spatial learning in the echolocating bat Rhinolophus ferrumequinum nippon*.

Scientific Reports 10.

DOI:
`10.1038/s41598-020-67470-z`

## Public raw dataset

Figshare article id:
`19102712`

DOI:
`10.6084/m9.figshare.19102712.v1`

Dataset title:
*row dataset for article entitled "Modulation of acoustic navigation behaviour by spatial learning in the echolocating bat Rhinolophus ferrumequinum nippon"*

The public availability of this dataset is explicitly documented by the later BMC Biology echo-space study that reused it.

## Experimental leverage inherited from the source paper

The source experiment has unusually strong relevance to the present mechanism problem:

- species: *Rhinolophus ferrumequinum nippon*;
- 14 bats;
- two obstacle conditions, seven bats per condition;
- all bats were naive to the tested obstacle course before the experiment;
- each bat flew 12 consecutive repeated flights;
- the first flight is source-defined as unfamiliar-space behaviour;
- repeated experience changed movement and echolocation variables;
- the source study contrasted the first and twelfth flights.

The present programme does **not** claim these source-paper results as new findings.

## New mechanism question

The unresolved batter question is not whether bats learn the obstacle course.

It is:

> **When behaviour changes with experience, what happens to the individual-specific movement-policy coordinate?**

Specifically:

1. Is there a personal movement-policy ordering already on the first naive flight?
2. Does that ordering survive a large common learning shift?
3. Does repeated experience create stronger individual self-predictability than is present initially?
4. Are learning-induced changes mostly common across bats, or do individuals diverge toward different learned solutions?

This directly distinguishes:

- stable personal prior;
- common learning response;
- individual-specific learned lock-in.

## Relationship to current batter results

Current internal evidence supports a low-dimensional portable personal policy in another *R. nippon* obstacle-flight dataset, dominated by:
- FlightIntensity;
- ManeuveringExtent / route-organization.

The current programme does **not** assume that the same axes are available in the 2020 dataset.

Axis definitions must follow the publicly available source variables under a new frozen estimator contract after schema inspection.

## Outcome firewall

Before any data row is read:

1. inventory Figshare metadata only;
2. identify files, sizes, hashes and content types;
3. freeze a file/schema opening allowlist;
4. open headers/schema only;
5. determine whether individual identity and flight order 1–12 are recoverable;
6. freeze the exact policy variables and learning contrasts;
7. only then open row values.

## Claim ceiling

A positive result may support:

> stable individual movement tendencies survive experimentally observed learning, or alternatively personal movement policy emerges/diverges during repeated experience.

It cannot by itself establish:
- neural mechanism;
- reinforcement learning algorithm;
- fitness optimality;
- generality across bat species;
- that the current batter policy axes and the 2020 variables are identical.
