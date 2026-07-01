# eLPO Python Simulation Platform

This repository is a white-box Python prototype for 112G/224G PAM4 LPO/IMDD link simulation.

The implementation keeps DSP algorithms in plain NumPy so the math remains visible and portable to later digital or mixed-signal implementation work. Third-party packages are limited to numerical plumbing, plotting, testing, and optional spreadsheet configuration.

## Current Features

- PAM4 Gray mapping, slicing, BER and SER metrics.
- 50 sps waveform path for eye-diagram generation and device/channel modeling.
- 2 sps DSP path.
- TX CTLE and TX FFE.
- DAC, driver, MZM, optical channel, PD, TIA, and ADC first-order behavioral models.
- RX FFE that trains at 2 sps and outputs 1 sps.
- LMS training followed by optional DD-LMS.
- Burg-initialized partial-response estimation and hard-decision Viterbi MLSE.
- 112G and 224G example runs.
- Optional `.xlsx` parameter loading into flat dictionaries.

## Quick Start

```powershell
.\.venv\Scripts\python examples\run_112g.py
.\.venv\Scripts\python examples\run_224g.py
.\.venv\Scripts\python -m pytest
```

Outputs are written under `artifacts/`.

## Design Notes

The project intentionally avoids a heavy object model. Parameters are dictionaries, and the simulation flow is a set of functions. This matches the intended use as a DSP/chip prototype platform rather than a production software framework.

See:

- `docs/architecture.md`
- `docs/parameters.md`
- `docs/roadmap.md`

