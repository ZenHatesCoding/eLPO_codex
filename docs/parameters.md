# Parameter Rationale

This project is currently focused on a 112G-lab-shorthand / 100G-per-lane PAM4 LPO/IMDD link. The 224G/200G-per-lane profile is kept as a TODO and is not treated as a validated default.

## Current Main Profile: 112G Lab Shorthand / 100G Per Lane

The main profile is `params_112g()`:

- Raw lane rate used in the simulator: 106.25 Gb/s.
- Symbol rate: 53.125 GBd PAM4.
- Standard anchor: IEEE 802.3ck 100 Gb/s per electrical lane objectives.
- Electrical insertion-loss anchor: 28 dB at 26.56 GHz.
- Default optical reach profile: `dr`, 500 m SMF placeholder.
- DAC/DSP/ADC: 2 sps.
- Analog channel/device grid: 8 sps.
- Eye rendering: 50 sps.

The function name remains `params_112g()` because 53.125 GBd PAM4 lanes are often called 112G-class lanes in lab shorthand, even though the Ethernet encoded lane rate is 106.25 Gb/s.

## Public Standards Ledger

See `docs/standards.md` for source links and the exact public values copied into the profile. The important current anchor is:

- IEEE 802.3ck: electrical backplane insertion loss <= 28 dB at 26.56 GHz for 100 Gb/s per electrical lane.

224G / IEEE 802.3dj values are recorded there as references, but 224G bring-up is now tracked as a roadmap item.

## Device Defaults

The 112G profile uses behavioral device models plus one standard-anchored aggregate electrical insertion-loss response:

- TX FFE: `[-0.08, 1.0, -0.05]`. This is a placeholder preset, not yet constrained to a specific standard tap table.
- TX CTLE: enabled by default with zero/pole values normalized to symbol rate. This is a placeholder analog pre-emphasis shape, not a standards-defined transmitter requirement.
- Electrical channel: frequency-domain insertion-loss curve fitted to 28 dB at 26.56 GHz.
- DAC: 7-bit quantizer, optional bandwidth/noise terms.
- Driver: gain, clipping, optional bandwidth/noise terms.
- MZM: quadrature-biased sine transfer with `Vpi = 3.5 V`, about 6 dB extinction ratio.
- Optical channel: fiber length/loss, connector loss, optional chromatic dispersion, RIN, and optional low-pass term.
- PD/TIA: responsivity `0.75 A/W`, TIA gain `650 ohm`, shot noise, bandwidth, and input noise.
- ADC: 7-bit quantizer at 2 sps.

These are still behavioral models. They are suitable for algorithm exploration, not module compliance prediction.

## Optical Reach Profiles

The optical reach presets are simple placeholders:

- `dr`: 0.5 km SMF.
- `fr`: 2 km SMF.
- `lr`: 10 km SMF.
- `fr_lband` and `lr_lband`: same lengths with 1550 nm and generic SMF dispersion.

Use `apply_optical_reach(cfg, "fr")` or similar to switch reach. These profiles need PMD-specific optical budgets and compliance metrics before they can be called standard-compliant.

## Clean Validation Preset

`params_clean()` disables the lossy/noisy device path and keeps the 2 sps -> 8 sps -> 2 sps rate conversion. It should produce zero BER. If it does not, the likely issue is symbol alignment, slicer mapping, FFE training, or BER accounting.

## DSP Defaults

- RX FFE uses 19 taps for the 112G main profile.
- LMS starts with known training symbols, then DD-LMS uses hard PAM4 decisions.
- The FFE target is the original PAM4 symbol stream; it is not intentionally left short of equalization to create PR ISI.
- MLSE uses a post-FFE noise-whitening partial-response filter. The default memory depth is 1, so the filter is `1 + alpha z^-1`.
- `alpha` is estimated from the FFE training residual using Burg AR estimation.
- BER is reported separately at the FFE output and MLSE output.

## MLSE Gain Conditions

The intended flow is: FFE completes equalization, FFE noise enhancement leaves colored residual noise, the PR filter whitens that noise and reintroduces controlled ISI, and MLSE detects through that PR response.

With the 112G 802.3ck-like profile, the current smoke run already shows MLSE gain because the estimated whitening filter has a meaningful memory term. If the residual noise is close to white, the estimated `alpha` will be small and MLSE will show little gain.

## Notes To Improve Later

- Replace the fitted insertion-loss curve with measured S-parameter import or a standard channel package.
- Add exact transmitter FFE/precoder constraints from the selected standard clause or IA.
- Add exact reference receiver CTLE/FFE settings from the selected clause or IA.
- Add optical PMD budgets and compliance metrics for DR/FR/LR.
