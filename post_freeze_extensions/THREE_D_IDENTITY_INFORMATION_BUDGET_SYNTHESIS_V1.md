# 3D identity information budget synthesis v1

## Status

POST-HOC SYNTHESIS of already-opened results. No new biological endpoint is tested here.

Inputs:
- collective/personal 3D decomposition workflow 37614056083;
- personal 3D predictive ladder workflow 37617952904;
- spatial-scale individualization workflow 37617970268;
- shrinkage diagnostic workflow 37619301387.

## Factorization

On the exact fixed target-support universe, the self-versus-other joint 3D log-likelihood ratio can be decomposed conceptually into:

[
lograc{P_i(C_{10})}{P_{-i}(C_{10})}
+
lograc{P_i(C_{500}mid C_{10})}{P_{-i}(C_{500}mid C_{10})}
+
lograc{P_i(Zmid C_{500})}{P_{-i}(Zmid C_{500})}.
]

The first term is coarse 10-km horizontal identity.
The second is fine horizontal refinement inside the coarse sector.
The third is relative vertical conditional identity inside the 500-m cell.

Because the 500-m and 10-km horizontal models use nested grids with the same equal-session/equal-individual construction, the second term is represented by the observed 500-m self gain minus the 10-km self gain.

## Mean information budget

| panel | coarse horizontal | fine horizontal within 10 km | vertical conditional | joint total | mean fraction coarse / fine / vertical |
|---|---:|---:|---:|---:|---|
| *Hypsignathus monstrosus* | +0.354 | +2.819 | +0.426 | +3.599 | 9.8% / 78.3% / 11.8% |
| *Phyllostomus hastatus* 2022 | +0.184 | +2.682 | +0.246 | +3.113 | 5.9% / 86.2% / 7.9% |
| *P. hastatus* 2023 | +0.784 | +2.904 | +0.365 | +4.053 | 19.4% / 71.6% / 9.0% |

Cluster-bootstrap 95% intervals for the fine-horizontal fraction:
- *Hypsignathus*: 72.7–83.5%;
- P2022: 81.7–91.7%;
- P2023: 41.5–91.9% (n=6; much wider).

Thus the dominant relative identity signal in all three systems is **fine horizontal geography inside a broader movement sector**.

## Crucial distinction: identity information is not the same as positive forward shape value

The vertical-conditional term above is positive because the focal individual's conditional vertical map is less mismatched than another individual's map.

The predictive ladder showed that this does not generally imply that cell-specific vertical shape improves future prediction over the focal individual's own marginal vertical state:

- *Hypsignathus*: raw shape increment +0.033, unsupported; training-only shrinkage recovers +0.078 [0.035,0.127].
- P2022: raw -0.372; shrinkage approximately 0 (-0.001 [-0.011,0.013]).
- P2023: raw -0.089; shrinkage approximately 0 (+0.009 [-0.011,0.039]).

Therefore two statements must be kept separate:

1. **Who is it?** Fine horizontal and, secondarily, conditional vertical distributions carry identity information relative to other animals.
2. **What best predicts that animal's future?** Fine horizontal history is strongly predictive; extra vertical cell-specific shape is positively predictive only in the current *Hypsignathus* diagnostic after history-only regularization.

## Ecological interpretation

The emerging architecture is not a generic stable 3D niche map.

It is closer to:

> **personal spatial geography with system-dependent vertical realization.**

Across the three prospectively evaluable systems:
- coarse movement sectors can already be personal;
- individuality becomes much stronger within those sectors at 500-m scale;
- the same fine horizontal places are reused in an individual-specific way;
- vertical conditional maps are non-interchangeable among animals;
- but positive forward value of the detailed vertical map is not general.

This provides a sharper interpretation of the earlier 3D-overlap result: repeatable 3D geometry exists, but most of the transferable predictive identity is carried by horizontal spatial history rather than a universally stable cell-specific vertical probability shape.

## Claim ceiling

This synthesis does not identify:
- cognitive-map algorithms;
- social learning;
- fitness optimization;
- resource competition;
- colony memory.

"Memory" remains a mechanism hypothesis. The direct evidence concerns persistence and forward predictive information in different spatial components.
