# Architecture

The simulator is split into small white-box functions:

- `pam4.py`: Gray mapping, slicer, and level normalization.
- `filters.py`: FIR, CTLE, low-pass, resampling, and waveform helpers.
- `devices.py`: DAC, driver, MZM, optical channel, PD/TIA, and ADC models.
- `dsp.py`: 2 sps RX FFE training and 2 sps to 1 sps downsampling.
- `mlse.py`: Burg AR noise-whitening PR estimation and hard-decision Viterbi MLSE.
- `metrics.py`: BER, SER, eye matrices, and eye-opening estimates.
- `sim.py`: End-to-end IMDD link orchestration.

## Multirate Data Path

The current data path is:

1. Generate PAM4 symbols from Gray-coded random bits.
2. Apply TX FFE at 1 sps.
3. Expand to 2 sps for DAC/DSP timing.
4. Run DAC at 2 sps.
5. Apply optional TX CTLE at 2 sps.
6. Upsample by 4 to run the analog channel path at 8 sps.
7. Run driver, MZM, optical channel, and PD/TIA at 8 sps.
8. Sample the ADC input back to 2 sps and quantize with the ADC model.
9. AC-normalize the RX DSP input.
10. Train RX FFE with LMS toward the original PAM4 symbols. This FFE is intended to complete equalization, with the LMS solution naturally balancing residual ISI and noise enhancement.
11. Continue the FFE with optional DD-LMS.
12. Estimate a noise-whitening partial-response filter from the FFE training residual. The default memory depth is 1, so the filter is `1 + alpha z^-1`.
13. Apply that PR/whitening filter to the FFE output. This whitens colored post-FFE noise but reintroduces controlled ISI.
14. Run hard-decision MLSE using the PR filter as the sequence-response model.
15. Compute both FFE-output and MLSE-output BER/SER.

The RX FFE operates on 2 sps input but emits one output per UI, so it is both the equalizer and the 2 sps to 1 sps downsampler.

## Eye Diagrams

Eye diagrams are not produced by running the full device model at 50 sps. Instead, the aligned 2 sps RX input is upsampled to 50 sps for visualization. The plotter removes DC, normalizes RMS, uses the selected FFE sampling phase when folding traces, and overlays 5/50/95 percentile curves.
