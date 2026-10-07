# Learning-state expression strength — authoritative result v1

## Execution

- workflow run: **37622303371**
- head SHA: `4c51592fa5488c109cc9550569997f2c7b2811ef`
- conclusion: **success**
- artifact: **11483787802**
- artifact zip SHA256: `a95d243b5c50403b5a5fb14aee6998ad54d1419488fc3af3ba1e7636d9420be5`

## Model

After removing the condition × trial mean speed:

[
y_{i,12}=alpha_c x_{i,1}+epsilon_i.
]

Here alpha measures how strongly naive individual speed differences are expressed after learning.

## Permeable / chain condition

Common mean learning shift:
**+0.8925 m/s**.

Personal-expression slope:
[
alpha_1=0.00198.
]

- Pearson r = 0.0026
- exact 7! one-sided p = **0.4982**
- bootstrap 95% CI = **[-0.934, 1.480]**
- familiar/naive SD ratio = 0.771

Thus the large population learning shift is accompanied by essentially no calibrated preservation of the naive individual ordering.

## Reflective / acrylic condition

Common mean learning shift:
**+0.2734 m/s**.

Personal-expression slope:
[
alpha_2=0.7997.
]

- Pearson r = 0.8980
- exact p = **0.00218**
- bootstrap 95% CI = **[0.413, 1.146]**
- familiar/naive SD ratio = 0.891

Thus individual faster/slower position is strongly expressed after learning in this condition.

## Between-condition contrast

[
Deltaalpha=alpha_{reflective}-alpha_{permeable}=+0.7977.
]

99,999-draw two-sided null:
- p = **0.09966**

Therefore the architecture is **suggestive of context-dependent expression**, but the direct condition contrast is not calibrated at 0.05.

## Interpretation

The data support neither extreme:

- theta is not simply erased by learning overall;
- theta is not guaranteed to be expressed with a fixed coefficient in every learning context.

A useful current model is

[
x_{i,e,t}=mu_{e,t}+alpha_{e,t}	heta_i+h_{i,e,t}+epsilon.
]

The evidence for context dependence of alpha remains suggestive rather than causal/confirmatory.
