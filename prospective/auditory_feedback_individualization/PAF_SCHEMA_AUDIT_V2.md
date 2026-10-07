# Auditory-feedback PAF schema audit v2

**MATLAB TABLE STRUCTURE ONLY — NO ACOUSTIC FEATURE VALUES REPORTED.**

- rows: **28091**
- columns: **38**
- bats: **10**
- hearing/deaf rows: **16937 / 11154**
- H female/male rows: **7541 / 9396**
- D female/male rows: **6508 / 4646**
- fixed acoustic features: **28** (columns 5:32)

## Structural columns

- 1: BatID
- 2: Acoustic Group
- 3: Sex
- 4: Hearing_Deaf

## Fixed feature column names

- 01: Duration (ms)
- 02: RMS mean
- 03: Pitch Saliency (AU)
- 04: Fundamental mean (kHz)
- 05: Fundamental CV
- 06: Spectral mean (kHz)
- 07: Spectral std (kHz)
- 08: Spectral kurtosis (Hz)
- 09: Spectral skewness (Hz)
- 10: Spectral entropy
- 11: Temporal mean (ms)
- 12: Temporal std (ms)
- 13: Temporal kurtosis (ms)
- 14: Temporal skewness (ms)
- 15: Temporal entropy
- 16: 1st Spectral Quartile (kHz)
- 17: 2nd Spectral Quartile (kHz)
- 18: 3rd Spectral Quartile (kHz)
- 19: Mic Spectral mean (kHz)
- 20: Mic Spectral std (kHz)
- 21: Mic Spectral kurt (Hz)
- 22: Mic Spectral skew (Hz)
- 23: Mic Spectral ent
- 24: Mic 1st Spectral Quartile (kHz)
- 25: Mic 2nd Spectral Quartile (kHz)
- 26: Mic 3rd Spectral Quartile (kHz)
- 27: Amplitude Periodicity Frequency (log(Hz))
- 28: Amplitude Periodicity Power

## Bat support

| BatID | calls | H/D | sex |
|---|---:|---|---|
| F3 | 1322 | D | F |
| M3 | 6080 | H | M |
| F1 | 3041 | D | F |
| M2 | 1582 | D | M |
| F5 | 2940 | H | F |
| F4 | 2577 | H | F |
| F6 | 2024 | H | F |
| M4 | 3316 | H | M |
| M1 | 3064 | D | M |
| F2 | 2145 | D | F |

## Structural fourth column

- name: Hearing_Deaf
- class: categorical
- level D: 11154 rows
- level H: 16937 rows

No acoustic value, centroid, identity score, treatment effect, or dispersion was calculated.
