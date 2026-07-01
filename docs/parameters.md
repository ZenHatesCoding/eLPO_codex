# Parameter Rationale

This project uses dictionary parameters and keeps defaults near common 112G/224G PAM4 IMDD/LPO assumptions. They are not compliance limits. They are starting points for design-space exploration.

## Rate Choices

For "112G PAM4" and "224G PAM4" lab shorthand, the default symbol rates are:

- 112 Gb/s PAM4 raw: 56 GBd.
- 224 Gb/s PAM4 raw: 112 GBd.

For Ethernet/OIF-style encoded lanes, common references are 53.125 GBd for 106.25 Gb/s/lane PAM4 and 106.25 GBd for 212.5 Gb/s/lane PAM4. The dictionaries can be changed directly if a standards-oriented run should use those values.

Public anchors used for this choice:

- IEEE 802.3ck covers 100 Gb/s per lane electrical interfaces and related PAM4 reference behavior.
- IEEE 802.3dj targets 200 Gb/s per lane and 1.6 Tb/s Ethernet-class work.
- OIF CEI-112G and CEI-224G implementation agreements define common electrical interface families used around 112G/224G ecosystems.
- Recent PR-PAM4/MLSE IMDD papers commonly combine partial-response shaping and MLSE to trade bandwidth for sequence detection robustness.

## Device Defaults

Bandwidths are expressed as fractions of symbol rate:

- DAC: about 0.45 UI Nyquist-equivalent bandwidth.
- Driver: about 0.55 times symbol rate.
- MZM: nonlinear cosine-squared transfer with `Vpi = 3.5 V`, about 6 dB extinction ratio.
- Optical channel: 4-5 dB loss and about 0.75 times symbol-rate electrical-equivalent bandwidth.
- PD/TIA/ADC: responsivity `0.75 A/W`, TIA gain `650 ohm`, about 0.55 times symbol-rate bandwidth.
- ADC/DAC: 6-7 bit defaults, intentionally modest for early chip-oriented exploration.

The models are first-order behavioral blocks, not final compact models. The important property is that all noise, clipping, bandwidth, and nonlinear effects are explicit and easy to replace.

## DSP Defaults

- Waveform and eye processing use 50 sps.
- DSP uses 2 sps.
- RX FFE uses 19 taps for 112G and 23 taps for 224G by default.
- LMS starts with known training symbols, then DD-LMS uses hard PAM4 decisions.
- MLSE uses a short partial-response memory by default (`pr_order = 3`) so the Viterbi state space remains transparent.

## Notes To Improve Later

- Replace the simple optical channel with measured S-parameter import or fitted pole-zero models.
- Add standards-specific presets for 802.3ck, 802.3dj, CEI-112G-VSR/MR/LR, and CEI-224G.
- Add calibration scripts that fit device dictionaries from lab data.

