# Status

## Completed In The Current Baseline

- Project layout, `.venv` dependency flow, tests, examples, and GitHub repository.
- End-to-end PAM4 generation, Gray slicing, BER/SER accounting.
- TX FFE and TX CTLE hooks.
- DAC/DSP/ADC at 2 sps.
- 8 sps channel simulation through driver, MZM, optical channel, and PD/TIA.
- RX FFE with 2 sps input and 1 sps output.
- LMS training plus optional DD-LMS.
- Burg-estimated post-FFE noise-whitening PR filter.
- Hard-decision MLSE using the PR filter response.
- Separate FFE and MLSE BER reporting.
- 50 sps eye rendering from aligned RX input.
- Clean ideal validation case with zero BER.
- Controlled colored-noise PR-MLSE demo.

## Important Limitations

- Device models are first-order behavioral models, not calibrated compact models.
- Current bandwidth limits are parameterized first-order low-pass assumptions, not measured S-parameter-derived responses.
- No measured S-parameter import yet.
- No CDR/timing recovery loop yet; phase is searched during FFE training.
- MZM, PD/TIA, DAC, and ADC parameters are plausible defaults, not final selected silicon or module parameters.
- MLSE currently uses a hard-decision Viterbi detector with short PR memory; no soft metrics or FEC interface yet.
- Eye plotting is visualization-oriented. Compliance-style eye masks and bathtub extrapolation are not implemented yet.
