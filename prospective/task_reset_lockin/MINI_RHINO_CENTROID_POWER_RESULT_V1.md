# Mini-Rhino centroid-support power result v1

## Execution

- workflow run: 37633588145
- artifact: 11488185428
- exact Mini occupancy mappings onto Rhino: 4,212
- calibrated Rhino mappings: 256

## Mini observed centroid-level PCA1

Using one equal-weight centroid per occupied bat × environment cell:

- K = **+0.11294**
- positive bats = **2/4**
- p = **0.2447**
- detected = false

Thus Mini remains unsupported after removing unequal within-cell trajectory replication.

## Rhino positive control under exact Mini occupancy support

Across all 4,212 exact occupancy mappings:

- median observed K = **+0.9711**
- 2.5–97.5% = **[-0.0310, +1.8676]**
- K > 0 in **96.0%** of mappings
- K > Mini K in **91.2%** of mappings

However, under the frozen 1,999-permutation calibration on 256 deterministic mappings:

- detected mappings = **101/256**
- detection fraction = **0.3945**

Frozen support category:

`POWER_LIMITED`

## Interpretation

This is an important ceiling on the Miniopterus negative result.

The sparse Mini cross-environment support can preserve a large positive Rhino-like observed K, but often cannot calibrate that effect to p<=0.05 with the required 3/4 individual sign consistency.

Therefore:

> the current Miniopterus archive does not support a portable linear individual policy, but its failure cannot be cleanly interpreted as evidence that such a policy is biologically absent or fundamentally higher-dimensional.

The correct interpretation is **non-identification under sparse cross-environment replication**.

The stronger contrast that remains valid is:
- Rhino: low-dimensional personal policy is positively demonstrated and rapidly convergent;
- Mini: the same quantity is not recoverable from the current archive.

This is an evidence-strength asymmetry, not yet a demonstrated species-level mechanistic difference.

## Additional implication

Observed K is not the main bottleneck. Calibration is.

This matters because simply adding dimensions does not solve the Mini problem: dimensions 1–8 all failed, while the matched Rhino positive control shows that a genuinely strong signal can also fail formal detection under the same sparse occupancy structure.

A stronger Mini dataset needs repeated cross-environment cells rather than a more flexible latent model.
