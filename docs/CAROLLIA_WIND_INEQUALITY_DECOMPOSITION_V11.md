# V11b exact inequality decomposition
Based on existing user-supplied MD5/SHA-verified 116 morphology records. No response data. Let a_i=log A_i(0) for common reference energy; r_i=log[A_i(w)/A_i(0)], m_i=log(M_i/geometric mean M). If E_i scales as M_i^alpha, A_i scales as E_i^2. Then
Var(log A_w(alpha))-Var(log A_0(alpha)) = Var(r)+2Cov(a,r)+4 alpha Cov(m,r).
This identity is exact for finite sample variance/covariance using the same n-1 denominator. Wind-induced log-area inequality decreases iff the RHS is negative, increases iff positive. It is not a universal ecological theorem about realized utilization, nor necessarily a CV threshold. If Cov(m,r)=0, sign is independent of alpha. If r is constant across individuals, effect is zero regardless of alpha; even strong area contraction need not alter log-area variance. For arbitrary log E_i replace alpha*m_i by log E_i. This separates relative geometric compression and energetic heterogeneity. 
Local NumPy/SciPy sensitivity with .02 m/s grid, 180 angles:
model; speed band; w; CV crossing alpha (all 116 / collision removed 114); delta CV at alpha=0,.75,1 (all); logvariance crossing all
Norberg;5–7;2;1.06051/1.06412;-.01239,-.01091,-.00306;1.06169
Norberg;5–7;4;.90389/.90570;-.04494,-.02268,+.01516;.90689
Norberg;2–7;4;.93054/.93266;-.04865,-.02732,+.01155;.93271
Norberg;5–9;4;.90054/.90231;-.04568,-.02261,+.01590;.90361
V5 reduced;5–7;4;.30230/.29668;-.01181,+.02580,+.03220;.30944
At reduced w=2 CV changes of ~1e-5 are near grid resolution and not meaningful (root ~.596). The strong dependence of boundary on power model prohibits treating 0.904 as a validated or generally portable parameter; even the sign at alpha=.75 differs. Equal-budget compression and mass-proportional expansion agree in the tested w=4 scenarios. Distinct time-energy joint constraint results in V11 record. 
Runnable reproduction script scripts/carollia_budget_geometry_v11.py uses same V10 geometry helper, .01 speed grid and explicit two-leg .1 grid for time cap. Local standalone analysis actually executed, repo version not independently CI verified yet. No AFPT individual result in V11, no empirical budget exponent or field separation. V12 workflow tests frequency assumptions and common speed support conditional on obtaining exact source from official public URL. ART data source is distinct publication but overlap not verified. No submission or merge.
