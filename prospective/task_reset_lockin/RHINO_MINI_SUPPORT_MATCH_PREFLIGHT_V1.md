# Rhino-to-Mini exact support-match preflight v1

## Status

Structural preflight only. No movement feature values or identity outcome is calculated.

## Question

Can the sparse *Miniopterus fuliginosus* sampling design be imposed exactly on the richer *Rhinolophus nippon* archive?

If yes, a later frozen rarefaction analysis can ask whether Rhino's one-dimensional individual policy survives under Mini-equivalent data support.

## Structural source

Use only Figshare file metadata and filenames from the shared Teshima archive.

From filenames recover:
- species block by frozen file-ID range;
- environment number;
- bat label;
- trajectory/trial filename.

Do not download trajectory CSV contents in this preflight.

## Exact match rule

Let the Mini design be the count table

`n_mini(environment, mini_bat)`.

Enumerate every injective mapping from the four Mini bat labels to four of the five Rhino bat labels.

A mapping is structurally valid only if, for every Mini bat × environment cell with count n>0, the mapped Rhino bat has at least n trajectories in the same environment.

No environment remapping is allowed.

## Gate

The follow-up support-matched analysis opens only if:
- at least 5 valid injective mappings exist.

Otherwise stop and use a looser count-matched design under a new contract.
