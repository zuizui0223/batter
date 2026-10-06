# Aharon 2017 public-source structural audit contract v1

## Status

**OUTCOME-BLIND PUBLIC-DATA STRUCTURAL AUDIT.**

No turning-point, slowing-point, speed, distance, or treatment-effect value may be opened in this stage.

## Source

Study:
Aharon, Sadot & Yovel (2017),
*Bats Use Path Integration Rather Than Acoustic Flow to Assess Flight Distance along Flyways*.

Public dataset:
- Mendeley Data id: `f6mvhj5gj9`
- version: 3
- DOI: `10.17632/f6mvhj5gj9.3`

The public landing-page description already states that:
- numeric prefixes such as 500/503/etc. represent biological bats;
- suffix X represents condition;
- turning-point matrices use one trial per column;
- slowing-point matrices use one trial per column;
- trial-level mean speed variables are present;
- some experiments alter tulle-wall detection distance (1 m versus 12 m).

This audit does not inspect matrix values.

## Biological leverage

The source experiment manipulates navigation information and physical context, including:
- acoustic flow;
- starting position;
- wind;
- landmark availability / wall-detection structure.

The public-data question is:

> can a fixed individual navigation-state summary be estimated under one condition and tested under independently manipulated conditions without redefining the endpoint?

This is potentially stronger than another repeatability dataset because current sensory/physical context is experimentally altered.

## Stage 1 — metadata/file inventory only

Read only:
- dataset identity;
- version;
- DOI;
- title;
- description;
- file UUIDs;
- filenames;
- sizes;
- content types;
- hashes;
- folder structure if exposed.

Do not download file contents.

## Proceed gate

Proceed to a variable-name/schema-only opening only if:
- the dataset/version matches exactly;
- at least one public file plausibly contains the Figure 1–4 variables described by the source;
- the file type can be opened without executing untrusted code;
- individual-coded variables and condition labels can be enumerated structurally.

## Future confirmatory target if structure passes

Preferred primary:

> same-individual navigation-state information transfers across a predeclared manipulation that changes external navigation cues.

Candidate source-native endpoints, to be selected before values are opened:
- turning-location organization;
- slowing-location organization;
- trial mean speed.

No endpoint may be selected by whichever gives the smallest p-value.

A later contract must fix:
- which figure/experiment;
- exact bats;
- exact conditions;
- scalar/vector endpoint;
- support minimum;
- null/permutation scheme;
- claim ceiling.

## Claim ceiling

Even a positive re-analysis would not establish:
- origin of the personal bias;
- learning versus biomechanics;
- equivalence to the JAE wild vertical-individuality carrier;
- a universal bat navigation law.

It could establish that individual navigation organization survives a controlled change in current cue structure.
