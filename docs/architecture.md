# Architecture

The simulator is split into small white-box functions:

- `pam4.py`: Gray mapping, slicer, and level normalization.
- `filters.py`: FIR, CTLE, low-pass, resampling, and 50 sps waveform helpers.
- `devices.py`: DAC, driver, MZM, optical channel, PD/TIA, and ADC models.
- `dsp.py`: 2 sps RX FFE training and 2 sps to 1 sps downsampling.
- `mlse.py`: Burg AR estimation, partial-response estimation, and hard-decision Viterbi MLSE.
- `metrics.py`: BER, SER, eye matrices, and eye-opening estimates.
- `sim.py`: End-to-end IMDD link orchestration.

The data path is:

1. Generate PAM4 symbols from Gray-coded random bits.
2. Apply TX FFE at 1 sps.
3. Expand to a 50 sps waveform for device and eye work.
4. Apply optional TX CTLE.
5. Run DAC, driver, MZM, optical channel, PD/TIA, and ADC models.
6. Sample the ADC waveform to 2 sps for DSP.
7. Train RX FFE with LMS while searching phase and coarse symbol delay.
8. Continue with optional DD-LMS.
9. Estimate a partial-response target using Burg-initialized modeling plus hard-decision refinement.
10. Run hard-decision MLSE and compute BER/SER.

The RX FFE operates on 2 sps input but emits one output per UI, so it is both the equalizer and the 2 sps to 1 sps downsampler.

