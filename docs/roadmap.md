# Roadmap

## Done In This Baseline

- Local Python project and `.venv` workflow.
- End-to-end 112G PAM4 IMDD simulation with an IEEE 802.3ck-like electrical insertion-loss anchor.
- DAC/DSP/ADC aligned at 2 sps.
- Channel/device analog path at 8 sps.
- 50 sps eye rendering from aligned RX input.
- Device block placeholders with visible equations.
- LMS/DD-LMS RX FFE that targets the original PAM4 symbol stream.
- Burg-estimated post-FFE noise-whitening PR filter.
- Hard MLSE using the PR filter response.
- Separate FFE-output BER and MLSE-output BER.
- Clean ideal validation case that preserves rate conversion and should produce zero BER.
- Controlled colored-noise PR-MLSE demo.
- Tests and smoke examples.

## Next Engineering Steps

1. Add measured S-parameter import and causal impulse response fitting.
2. Add clock recovery and sampling phase adaptation.
3. Add explicit transmitter calibration for MZM bias and extinction ratio.
4. Bring up and validate 224G / 802.3dj-like profile; current 224G function is a placeholder, not a signed-off default.
5. Add COM-style channel presets for CEI/IEEE use cases.
6. Add spreadsheet templates for sweeping bandwidth, noise, tap count, and PR memory depth.
7. Add compliance-like eye mask reporting and bathtub/Q extrapolation.
8. Add soft-output or reliability-aware MLSE hooks for FEC-facing studies.

