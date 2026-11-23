# Happ real bat thermal stereo V4 independent matching audit (post-open, 2026-11-24)

The real published 2-camera candidate bat source was already numerically opened under the original-author matching protocol in successful [V3 Actions #45246661410](https://github.com/zuizui0223/batter/actions/runs/45246661410): original public author v1.0.1 source, 286 left + 314 right source 2D image candidate points across 257 original image timestamps, 243 original-author accepted stereo pairs in 198 source frames, 243 finite GPS-referenced reconstructed XYZ and median two-camera **pixel reprojection residual 0.5133967673 px** (90th 1.1312283 px). **This is a post-outcome technical verification, NOT independent scientific confirmation** and cannot be relabeled as a new biological validation.

Re-fetch exact original author Git commit `34d2f56bcee1eab9207890938aedd90a079bfcde` and original source byte hashes; reuse only the V2 original drone-A fitted PnP camera geometry (already independently heldout tested) and neither the author original `batflight3d.load_and_correspond_PTS` nor V3 wrapper for matching. Implement a separate **standard-library CSV** reader of original bat 2D camera detections and source image frame IDs. Compute epipolar fundamental matrix by a **separate projective formula** `F=[P_2 C_1]_× P_2 P_1^+`, where `C_1` is the homogeneous null vector of camera 1 projection, independent of V3's source relative-extrinsic formula. Normalize F; the sign does not matter.

Apply fixed original author source thresholds exactly:
- For each source image frame, every left candidate and every right candidate: epipolar perpendicular distance `abs([x2,y2,1] F [x1,y1,1]) / hypot((F*[x1,y1,1])_x,(F*[x1,y1,1])_y)` <= **6 px**.
- positive source detection area ratio between `(1/4, 4)` **strictly**, as the original author function.
- Enforce source matching uniqueness via first eliminating multiply matched original left candidates, **then** multiply matched original right candidates **after** the first elimination, exactly the original author's sequential one-to-one rule. Do not match with nearest distance or tune threshold after seeing V3.
- Preserve all original original `nr` timestamp frames, never impute missing camera position, use source-provided 2D data directly (no raw image re-detection, no manual source bat selection).
- Use original fixed camera P1/P2, independently recompute final XYZ for corresponding original pixel pairs, full finite XYZ QC, reproject onto both image planes and assess identical v3 0.5133967673 px median and p90 1.1312283. Compare to 243 pairs / 198 source frames, absolute pixel error tolerance 1e−7 px. Do not import V3 pairing or reprojection functions, do not import the author `batflight3d` matching function.
- Hard fail with **V4 independent replay mismatch** if a difference arises; do **not** rewrite the original V3 outcome or retune original threshold to get agreement. All results are source geometry/algorithm reproducibility only.

No original animal true GPS points, individual species IDs, calibrated q, source-matched forest LiDAR or independent forest holdout exists in this source. An independent matching result is **not** new ecological 3D SDM prediction evidence.

Existing `batter/main` JAE, ODSP N2 and esdm E5, and source-restricted Hermans field data remain untouched.
