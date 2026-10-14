# Integrated bat individuality SVG render QA — draft scientific review v1

**Date:** 2026-10-14  
**Scope:** Independent preview of regenerated source-backed SVG files, not final printer proof or author sign-off.

## Recovered machine-authored figure bundle

- Original integrated six-SVG reproducibility workflow run [38507711979](https://github.com/zuizui0223/batter/actions/runs/38507711979): **PASS**.
- Source-controlled bundle artifact ID **11868212829**, artifact name \`unified-manuscript-figures-svg-v1\` (six source-generated SVGs).
- A separate later source-summary validation run [38508239184](https://github.com/zuizui0223/batter/actions/runs/38508239184) also passed.
- The exact original 103-individual JAE heatmap PNG and source CSV/JSON were restored by one-time workflow run [38507348011](https://github.com/zuizui0223/batter/actions/runs/38507348011). The write-privileged workflow file used to import them was intentionally removed from the working PR **after** successful checksum verification; original files remain and are continuously guarded by \`figures/validate_integrated_figures_v1.py\`.

## Preview procedure

The completed GitHub Actions SVG bundle was downloaded, unpacked and rendered as ordinary PNG previews by a local CairoSVG renderer at output width 1350 pixels per figure. A six-panel preview sheet was inspected for major layout issues, with separate full-size visual inspections of the ecology-focused Fig. 6, centered-shape Fig. 5A and developmental Fig. 2. The restored original Figure 5B source PNG was also opened directly at its native pixel dimensions and inspected for panel count and scale labels.

No numerical outcomes were altered during rendering. These previews do **not** count as approval by human authors or as a target-journal full-size grayscale/print proof.

## Findings

| Figure | Preview observations | Scientific/caption caveat |
|---|---|---|
| 1. Four-layer architecture | Four boxes and failed laboratory-style field bridge visually legible; conceptual dashed connections distinguished | No causal arrows or universal latent state implied |
| 2. Formation/development | 14 source B slopes shown with 8 positives, 6 nonpositives; primary FAIL, late-history secondary and two separate developmental contrasts legible | Small n / unsupported total dispersion not treated as equivalence; B_i from rounded frozen figure input |
| 3. Acute perturbation | Four rows visible with biological n, positive fraction, p and mapping ranks; no merged numerical K axis | Only within-study identity correspondence, no broad prevalence |
| 4. Portability | Coarse representation versus fixed detailed geometry cards and scalar field-bridge boundary visibly distinct | Unsupported detailed transfer does not prove no fine movement individuality |
| 5A. Field centered-shape | Six original panels and the focal negative *Tadarida* excess visibly distinguishable, labels readable at 1350 px | Full distribution inference, not individual tail-component inference |
| 5B. Original profile heatmap | Actual original image: five panels, 103 individual rows and 10 centered bins; one shared probability bar, panel names and n visible | Descriptive original only; no new inferential component tests |
| 6. Field fidelity/partitioning | Separate axes for V_rel, S_rel and co-use excess; center 95% S-null and dyad-bootstrap compatibility intervals distinct; H negative side and P2023 positive co-use visible | Two species only; one co-use positive exception; windows/scopes differ |

### Presentational caveat for final production

Figure 6 is dense when reduced to a narrow column. It should be submitted as a **full-width/two-column plate** or redesigned with larger type at the target journal's printed dimensions. Figures 2 and 5B also benefit from full-page/two-column placement. Their small footnotes should be moved to captions rather than reduced to illegible on-figure text.

**No demonstrable major clipping was observed in the inspected preview images**, but the figure quality assessment remains limited to preview PNGs and assistant visual inspection, not all journal compositor output formats or a human coauthor proof.

## Next gate

- Make the main Figure 5A+5B assembly journal-size and check label readability at realistic print width.
- Perform side-by-side original-result and visual-source audit by a human coauthor.
- Convert figure set to required journal vector/raster formats without editing data and inspect exported files.
- Check color-vision/grayscale differentiation for supported versus unsupported symbols and uncertainty bands.
- Secure permission-compliant source archive and final figure captions before submission.
