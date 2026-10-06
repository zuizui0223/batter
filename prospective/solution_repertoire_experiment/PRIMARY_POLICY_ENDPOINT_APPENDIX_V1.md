# Primary I/M endpoint appendix v1

## Status

**PROSPECTIVE FIXED ENDPOINT DEFINITION.**

This appendix ports the already-frozen transparent *Rhinolophus* movement-policy representation into the designed solution-repertoire experiment.

No weights, signs or feature choices are learned from the new experiment.

Parent definitions:
- \`prospective/task_reset_lockin/TRANSPARENT_TWO_AXIS_POLICY_CONTRACT_V1.md\`
- \`prospective/task_reset_lockin/rhino_configuration_identity_primary_v1.py\`

---

## 1. Input trajectory

For each flight use time-ordered finite 3-D positions:

\[
(t_k,x_k,y_k,z_k).
\]

Requirements:
- sort by time;
- retain first occurrence of duplicate timestamps;
- require at least 100 valid coordinate rows;
- require positive total duration;
- require positive finite path length;
- require at least 50 positive-dt displacement intervals.

If any requirement fails:
the flight is not policy-valid.

No interpolation or smoothing is authorized for the primary.

---

## 2. Consecutive displacement quantities

For every consecutive pair:

\[
\Delta \mathbf{x}_k=
(x_{k+1}-x_k,\ y_{k+1}-y_k,\ z_{k+1}-z_k)
\]

and:

\[
\Delta t_k=t_{k+1}-t_k.
\]

Use only intervals with positive finite \(\Delta t_k\).

### 3-D speed

\[
v_k=
\frac{\|\Delta \mathbf{x}_k\|}{\Delta t_k}.
\]

### Absolute vertical speed

\[
v_{z,k}
=
\left|
\frac{\Delta z_k}{\Delta t_k}
\right|.
\]

---

## 3. Horizontal turning rate

For each horizontal displacement with positive magnitude:

\[
\phi_k=\operatorname{atan2}(\Delta y_k,\Delta x_k).
\]

For adjacent finite headings:

\[
\Delta\phi_k
=
\operatorname{atan2}
\left[
\sin(\phi_{k+1}-\phi_k),
\cos(\phi_{k+1}-\phi_k)
\right].
\]

Associated turn interval:

\[
\Delta t^{turn}_k
=
\frac{\Delta t_k+\Delta t_{k+1}}{2}.
\]

Absolute horizontal turning rate:

\[
\omega_k=
\frac{|\Delta\phi_k|}{\Delta t^{turn}_k}.
\]

Require at least one finite turning-rate value.

---

## 4. Route-level quantities

### Path length

\[
L=\sum_k \|\Delta\mathbf{x}_k\|.
\]

### Net displacement

\[
D=
\|\mathbf{x}_{last}-\mathbf{x}_{first}\|.
\]

### Path efficiency

\[
E=D/L.
\]

### Vertical range

\[
R_z=\max(z)-\min(z).
\]

---

## 5. Frozen eight-feature vector

For every policy-valid flight:

1. \(f_1\): median 3-D speed;
2. \(f_2\): p90 3-D speed;
3. \(f_3\): median absolute vertical speed;
4. \(f_4\): p90 absolute vertical speed;
5. \(f_5\): median absolute horizontal turning rate;
6. \(f_6\): p90 absolute horizontal turning rate;
7. \(f_7\): path efficiency;
8. \(f_8\): vertical range.

All eight must be finite.

No feature substitution.

---

## 6. Primary common-OPEN standardization

The confirmatory primary is calculated only from the frozen common-OPEN probe.

For each matched family separately:

1. pool the eight-feature vectors from **all policy-valid primary-probe flights of all eligible confirmatory animals**;
2. ignore biological identity and OPEN/CONSTRAINED acquisition labels when calculating scaling;
3. calculate family-specific feature mean \(\mu_{f,k}\);
4. calculate sample SD \(s_{f,k}\) with ddof = 1;
5. require every SD to be finite and >0;
6. standardize:

\[
z_{i,t,k}
=
\frac{f_{i,t,k}-\mu_{f,k}}{s_{f,k}}.
\]

This is a treatment-blind coordinate transformation.

If any required feature has zero/nonfinite SD in either family:
**PRIMARY STRUCTURAL STOP.**

Do not pool A and B before standardization.

Do not standardize OPEN-acquired and CONSTRAINED-acquired trials separately.

---

## 7. Frozen transparent coordinates

### FlightIntensity

\[
I
=
\operatorname{mean}(z_1,z_2,z_3,z_4).
\]

### ManeuveringExtent

\[
M
=
\operatorname{mean}(-z_1,z_5,z_6,z_7,z_8).
\]

No fitted weights.

No PCA.

No sign changes.

No additional normalization of I and M after construction.

---

## 8. Policy distance

For two policy vectors:

\[
\theta_a=(I_a,M_a),\quad
\theta_b=(I_b,M_b),
\]

use Euclidean distance:

\[
d(\theta_a,\theta_b)
=
\sqrt{(I_a-I_b)^2+(M_a-M_b)^2}.
\]

No Mahalanobis distance, learned metric or axis rescaling in the primary.

---

## 9. Family-specific common-OPEN identity score

The frozen primary probe for each family contains an even number of planned policy-valid trials.

Split:
- first half = early history;
- second half = held-out targets.

For individual \(i\) in family \(f\):

### Own early centroid

\[
\bar\theta_{i,f}^{early}
=
\operatorname{mean}_{t\in early}
\theta_{i,t,f}.
\]

### Donor early centroids

For each other eligible individual \(j\neq i\):

\[
\bar\theta_{j,f}^{early}.
\]

Donors are all other endpoint-eligible individuals in that family, regardless of their randomized acquisition treatment.

For every late target \(q\):

\[
a_q
=
\operatorname{mean}_{j\neq i}
d(\theta_q,\bar\theta_{j,f}^{early})
-
d(\theta_q,\bar\theta_{i,f}^{early}).
\]

Individual × family identity score:

\[
A_{i,f}
=
\operatorname{mean}_{q\in late} a_q.
\]

Positive \(A_{i,f}\) means held-out late behavior is closer to that animal's own early common-OPEN policy than to other animals' early policies.

---

## 10. Primary treatment contrast

For each animal:
- one family was randomized to OPEN acquisition;
- the other to CONSTRAINED acquisition.

Define:

\[
D_i
=
A_{i,OPEN-acquired}
-
A_{i,CONSTRAINED-acquired}.
\]

Primary statistic:

\[
\Delta_A
=
\operatorname{mean}_i D_i.
\]

Equal-individual weighting only.

No weighting by number of valid trajectory rows or flight duration.

---

## 11. Missing probe flights

The final planned probe count and attempt ceiling are frozen after the engineering pilot.

The primary endpoint requires the full frozen number of policy-valid flights in **both** matched families for an animal.

Failed, aborted or tracking-invalid attempts may be replaced only under the predeclared attempt-ceiling rule.

After the attempt ceiling:
- if the required valid count is not reached in either family, that animal is endpoint-incomplete;
- apply the frozen attrition/block rule;
- do not shorten the early/late windows.

No imputation.

No unequal-window rescue.

---

## 12. Hard prohibition

After common-OPEN outcomes are visible, do not:
- alter any trajectory-validity threshold;
- change feature definitions;
- remove one of the eight features;
- change the sign of z1 in M;
- reweight I or M;
- rotate I/M;
- replace Euclidean distance;
- standardize by treatment;
- select only routes or trials showing stronger identity.

A failed I/M primary remains failed.
