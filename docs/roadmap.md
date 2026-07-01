# Roadmap

## Done In This Baseline

- Local Python project and `.venv` workflow.
- End-to-end 112G/224G PAM4 IMDD simulation.
- DAC/DSP/ADC aligned at 2 sps.
- Channel/device analog path at 8 sps.
- 50 sps eye rendering from aligned RX input.
- Device block placeholders with visible equations.
- LMS/DD-LMS RX FFE.
- Burg-initialized PR estimation and hard MLSE.
- Separate FFE-output BER and MLSE-output BER.
- Clean ideal validation case that preserves rate conversion and should produce zero BER.
- Tests and smoke examples.

## Next Engineering Steps

1. Add measured S-parameter import and causal impulse response fitting.
2. Add clock recovery and sampling phase adaptation.
3. Add explicit transmitter calibration for MZM bias and extinction ratio.
4. Add COM-style channel presets for CEI/IEEE use cases.
5. Add fixed-point hooks for FFE, MLSE branch metrics, ADC, and DAC datapaths.
5. Add spreadsheet templates for sweeping bandwidth, noise, tap count, and PR order.
6. Add compliance-like eye mask reporting and bathtub/Q extrapolation.
7. Add soft-output or reliability-aware MLSE hooks for FEC-facing studies.

