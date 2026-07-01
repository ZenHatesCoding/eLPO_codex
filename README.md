# eLPO Python Simulation Platform

This repository is a white-box Python prototype for 112G-first PAM4 LPO/IMDD link simulation. 224G profile work is tracked as TODO.

The implementation keeps DSP algorithms in plain NumPy so the math remains visible and portable to later digital or mixed-signal implementation work. Third-party packages are limited to numerical plumbing, plotting, testing, and optional spreadsheet configuration.

## Current Features

- PAM4 Gray mapping, slicing, BER and SER metrics.
- DAC, ADC, and DSP aligned at 2 sps.
- Device/channel simulation at 8 sps (`channel_oversample = 4`).
- Eye-diagram rendering by upsampling the aligned RX input to 50 sps.
- TX FFE and optional TX CTLE.
- DAC, driver, MZM, optical channel, PD/TIA, and ADC first-order behavioral models.
- RX FFE that trains at 2 sps and outputs 1 sps.
- LMS training followed by optional DD-LMS.
- Burg-estimated post-FFE noise-whitening PR filter and hard-decision Viterbi MLSE.
- Separate FFE-output BER and MLSE-output BER reporting.
- 112G standard-anchored, clean ideal, and PR-MLSE code-validation example runs.
- Optional `.xlsx` parameter loading into flat dictionaries.

## Quick Start

```powershell
.\.venv\Scripts\python examples\run_clean.py
.\.venv\Scripts\python examples\run_pr_mlse_demo.py
.\.venv\Scripts\python examples\run_112g.py
.\.venv\Scripts\python examples\optimize_tx_ffe.py --mode single
.\.venv\Scripts\python -m pytest
```

Outputs are written under `artifacts/`. The main eye plot is now `eye_rx_input_50sps.png`.

## Design Notes

The project intentionally avoids a heavy object model. Parameters are dictionaries, and the simulation flow is a set of functions. This matches the intended use as a DSP/chip prototype platform rather than a production software framework.

See:

- `docs/architecture.md`
- `docs/parameters.md`
- `docs/status.md`
- `docs/roadmap.md`
- `docs/tx_ffe_bayes_opt.md`




