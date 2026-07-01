# Current Results

These results were regenerated after clearing historical debug artifacts. They are the current baseline for this repository.

## Validation Commands

```powershell
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python examples\run_clean.py
.\.venv\Scripts\python examples\run_pr_mlse_demo.py
.\.venv\Scripts\python examples\run_112g.py
```

## Results

### Pytest

```text
5 passed
```

### Clean Ideal Link

```text
BER FFE  : 0.000e+00 (0/23994)
BER MLSE : disabled
```

### Controlled Colored-Noise PR-MLSE Demo

```text
BER FFE  : 9.533e-02 (2288/24000)
BER MLSE : 8.833e-03 (212/24000)
Estimated PR whitening filter: [1.0, -0.86469111]
```

### 112G / IEEE 802.3ck-Like Profile

```text
BER FFE  : 9.204e-02 (2208/23990)
BER MLSE : 2.526e-02 (606/23990)
SER MLSE : 5.052e-02 (606/11995)
Partial response: [1.0, 0.78578145]
```

Interpretation:

- The clean case validates symbol mapping, rate conversion, FFE alignment, and BER accounting.
- The colored-noise demo validates the post-FFE noise-whitening PR + MLSE algorithm in isolation.
- The 112G profile uses the IEEE 802.3ck public objective of 28 dB insertion loss at 26.56 GHz as the electrical-channel anchor. It is still not a full compliance model.

## Artifacts Kept

Only current example outputs should remain under `artifacts/`:

- `112G_PAM4_CLEAN_IDEAL/`
- `112G_PAM4_LPO_8023CK_LIKE/`

The PR-MLSE colored-noise demo is algorithmic and does not write plots.
