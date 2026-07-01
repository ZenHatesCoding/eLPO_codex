# Status

## Current Focus

The current validated bring-up target is 112G lab shorthand / 100G-per-lane PAM4, using an IEEE 802.3ck-like electrical insertion-loss anchor.

224G / 200G-per-lane work is intentionally parked in the roadmap. The public 802.3dj anchors are recorded in `docs/standards.md`, but 224G is not treated as a signed-off simulation profile yet.

## Completed In The Current Baseline

- Project layout, `.venv` dependency flow, tests, examples, and GitHub repository.
- End-to-end 112G PAM4 IMDD simulation.
- IEEE 802.3ck-like electrical insertion-loss anchor: 28 dB at 26.56 GHz.
- Source ledger for public standards references in `docs/standards.md`.
- TX FFE and TX CTLE hooks.
- DAC/DSP/ADC at 2 sps.
- 8 sps channel simulation through electrical IL, driver, MZM, optical channel, and PD/TIA.
- Optical reach placeholders with fiber length/loss/dispersion fields.
- RX FFE with 2 sps input and 1 sps output.
- LMS training plus optional DD-LMS.
- Burg-estimated post-FFE noise-whitening PR filter.
- Hard-decision MLSE using the PR filter response.
- Separate FFE and MLSE BER reporting.
- 50 sps eye rendering from aligned RX input.
- Clean ideal validation case with zero BER.
- Controlled colored-noise PR-MLSE demo.
- TX FFE 9-tap single-point and white-box Bayesian optimization entry point.
- Plot suppression switch for simulation sweeps.

## Important Limitations

- Device models are behavioral models, not calibrated compact models.
- The electrical channel uses a fitted insertion-loss curve anchored to a public objective, not a full COM/channel package.
- No measured S-parameter import yet.
- No CDR/timing recovery loop yet; phase is searched during FFE training.
- TX FFE taps and TX CTLE poles/zeros are placeholders, not yet constrained to an exact clause or IA tap table/reference transmitter.
- TX FFE Bayesian optimization uses local engineering bounds around the placeholder preset; standards/conformance tap limits still need to be added.
- Optical DR/FR/LR reach profiles are placeholders; PMD optical budgets and compliance metrics are not implemented yet.
- MLSE currently uses a hard-decision Viterbi detector with short PR memory; no soft metrics or FEC interface yet.
- Eye plotting is visualization-oriented. Compliance-style eye masks and bathtub extrapolation are not implemented yet.
