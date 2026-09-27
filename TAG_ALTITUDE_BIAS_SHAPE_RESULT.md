# Tag altitude-bias audit v1 — shift-invariant shape result

Primary shape run used the contract frozen before centered-height output. The authoritative
successful run for the contract JSON at `239f707cbd285306745b5e92a36be2c0fe4f6c4c` is
**36324889866**.

Every retained session was median-centered before vertical binning. This removes any additive
constant device/tag offset exactly and also removes session-specific constant altitude shifts.

## Result

| panel | n | centered observed | null mean | calibrated excess | p upper | verdict |
|---|---:|---:|---:|---:|---:|---|
| *Tadarida teniotis* | 6 | -0.2629 | -0.2408 | -0.0222 | 0.5121 | **FAIL** |
| *Eidolon helvum* | 20 | +0.3719 | -0.0710 | +0.4429 | 0.0002 | **PASS** |
| *Hypsignathus monstrosus* | 24 | +0.0736 | -0.1032 | +0.1768 | 0.0002 | **PASS** |
| *P. hastatus* 2022 | 33 | -0.0394 | -0.1508 | +0.1114 | 0.0002 | **PASS** |
| *P. hastatus* 2023 | 16 | +0.0454 | -0.0726 | +0.1181 | 0.0002 | **PASS** |
| *P. hastatus* 2016 | 10 | -0.0084 | -0.5824 | +0.5740 | 0.0076 | **PASS** |

Thus **5/6 panels pass** after absolute vertical location is removed.

## Interpretation under the frozen decision matrix

The result falls in the predeclared **4–5/6 PASS** category.

Allowed conclusion:

> Additive tag/device altitude offsets are not a general explanation for the cross-panel bat
> vertical-identity result. Five panels retain repeatable identity in the shape of their vertical
> distributions after every session is translated to zero median.

Required qualification:

> Focal *Tadarida* does not retain calibrated identity after session centering. Its previously
> reported identity can therefore be dominated by an individual-specific absolute vertical
> location component. That component can be biological, device-related, or both; the archived
> data do not separate those possibilities.

This does **not** show that *Tadarida* tag bias exists. Session centering also removes genuine
biological mean-height specialization. It shows only that the focal evidence does not survive a
test designed to be invariant to additive altitude offsets.

Consequently the focal 256-m expected-AGL separation should no longer be used as headline evidence
of biological vertical separation. It may remain as a raw descriptive translation only if
explicitly labelled as potentially containing an additive device offset.
