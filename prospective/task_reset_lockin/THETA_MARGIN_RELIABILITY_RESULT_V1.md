# Rhino theta margin reliability — authoritative result v1

## Execution

- workflow run: **37638308700**
- head SHA: `b1b72d6e0339b1228662f9c4403bcf07b5fc277d`
- conclusion: **success**
- artifact: **11489384581**
- artifact zip SHA256: `70e7035b0047ef6721bc50da2a815bf9f08e0fa9db218ea55eff1389aad74a27`

## Result

Across 35 held-out pair × environment calibration points:

[
ho(|x|, correctness)=+0.2477.
]

Permutation calibration:
- 9,997 valid of 9,999;
- null mean = -0.0926;
- null 95% interval = [-0.5151,+0.4172];
- one-sided p = **0.0963**.

Frozen support rule therefore fails.

Descriptive sign accuracy:
- all points: 0.8286;
- |x| >= 0.25: 0.8438;
- |x| >= 0.50: 0.8846;
- |x| >= 0.75: 0.8889;
- |x| >= 1.00: 0.8333.

## Interpretation

Larger training-only theta separation tends to improve held-out ordering descriptively, but not strongly enough to support a simple margin-reliability law.

Important counterexamples remain:
- A–C reverses in Env3 despite |x|≈1.01;
- C–E reverses in Env4 despite |x|≈1.05.

Thus environment-specific rank reversals are not confined to near ties.

A stable theta remains useful for average cross-environment prediction, but a simple

[
y_{ie}=	heta_i+epsilon_{ie}
]

with exchangeable context noise is not sufficient to explain all individual × environment structure.
