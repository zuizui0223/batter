# Rousettus original-author release: four-CSV pre-outcome key audit

Frozen on 2026-11-20. Intended to answer whether the author's **own GitHub release** contains structural support for linking manipulation date, treated individual, visits and independently recorded Ficus locations. **No experiment outcome is inspected.**

Source: `EmmLourie/Information-transfer-analysis`, fixed commit `1d7edbdbb87d9df048ab42a0b425a1966d491e86`, separately published by the study authors. **Not byte-identical to Dryad** DOI `10.5061/dryad.51c59zwgp` (publisher byte-size comparison already failed).

Four fixed Git blob objects and lengths: field manipulation (291 B), tag/manipulation join (1,371 B), visit tree stops (197,784 B), and Ficus tree locations (62 B). Do not reinterpret the author release as the Dryad original file. All blobs are verified as Git blobs using `sha1('blob '+size+'\0'+bytes)`; this matches Git's object SHA, not the publisher MD5.

**Predeclared key-only support:** literal overlap of manipulation dates, cave labels, tag IDs, tag×date pairs, and Ficus tree X/Y pairs. Key columns alone selected from CSV arrays. Outcome values such as `Visited`, `n_visited_*`, visit duration or location-referenced bat movement are never accessed or recorded. The aggregate output has no tag IDs, no coordinates and no per-row measurements.

Literal overlap is a structural diagnostic, not a completed bat×tree×date event join: dates may have differing formats; tree coordinates may use differing reference/rounding; cave labels might differ in capitalization. Future transformations must be justified from original metadata **before** opening observed outcomes; do not retry matching choices merely to maximize support.

If source qualification succeeds, the next, separately frozen task is a **2D experimental cue/visitation** heldout contrast in this one source, NOT a food-availability or high-dimensional bat distribution effect. If it fails, preserve STOP. The cactus source remains the stronger 3D-with-food candidate but original Mendeley public API is HTTP401.
