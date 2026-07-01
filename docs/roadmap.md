# Roadmap

## Done In This Baseline

- Local Python project and `.venv` workflow.
- End-to-end 112G/224G PAM4 IMDD simulation.
- Device block placeholders with visible equations.
- 50 sps eye output and 2 sps DSP path.
- LMS/DD-LMS RX FFE.
- Burg-initialized PR estimation and hard MLSE.
- Tests and smoke examples.

## Next Engineering Steps

1. Add measured S-parameter import and causal impulse response fitting.
2. Add clock recovery and sampling phase adaptation.
3. Add explicit transmitter calibration for MZM bias and extinction ratio.
4. Add COM-style channel presets for CEI/IEEE use cases.
5. Add fixed-point hooks for FFE, MLSE branch metrics, and ADC/FFE datapaths.
6. Add spreadsheet templates for sweeping bandwidth, noise, tap count, and PR order.

