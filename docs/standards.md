# Standards And Public Parameter Anchors

This file records public references used to build the current 112G-first standard-like profile. Keep new citations here so future parameter changes are traceable.

## Current Anchor: IEEE 802.3ck 100 Gb/s Per Electrical Lane

Source:

- IEEE 802.3ck objectives PDF: https://www.ieee802.org/3/ck/P802_3ck_Objectives_2018mar.pdf

Values used in the current 112G baseline:

- Electrical lane family: 100 Gb/s per lane.
- Single-lane 100 Gb/s AUI objectives for chip-to-module and chip-to-chip applications.
- Electrical backplane objective: insertion loss <= 28 dB at 26.56 GHz.
- Twinax objective: length up to at least 2 m.

Mapping in `src/elpo_sim/configs.py`:

- `params_112g()` represents a 106.25 Gb/s / 53.125 GBd 100G-per-lane profile, commonly called 112G PAM4 in lab shorthand.
- `electrical_channel.loss_db_at_hz = 28.0`.
- `electrical_channel.loss_ref_hz = 26.56e9`.
- The insertion-loss curve is a simple monotonic frequency-domain fit anchored to that objective, not the full standard COM/channel model.

## TODO Reference: IEEE 802.3dj 200 Gb/s Per Electrical Lane And Optical Reach

Source:

- IEEE P802.3dj adopted objectives PDF: https://www.ieee802.org/3/dj/projdoc/objectives_P802d3dj_240314.pdf

Values recorded for future 224G bring-up:

- BER objective at MAC/PLS service interface: <= 1e-13.
- Optional single-lane 200 Gb/s AUIs for chip-to-module and chip-to-chip applications.
- Electrical backplane objective: die-to-die insertion loss <= 40 dB at 53.125 GHz.
- Twinax reach objective: up to at least 1.0 m.
- SMF reach objectives include 500 m and 2 km for 200G/400G/800G/1.6T related objectives.
- Longer SMF objectives listed in the same document include 10 km, 20 km, and 40 km variants for higher aggregate rates/wavelength groupings.

Planned mapping:

- Future `params_224g()` should represent a 212.5 Gb/s / 106.25 GBd 200G-per-lane profile.
- Electrical channel target should use 40 dB at 53.125 GHz.
- 224G validation is not part of the current signed-off baseline.

## Optical Reach Profiles In This Repository

The current optical reach presets are deliberately simple. They are not full IEEE PMD compliance models.

| Profile | Length | Wavelength | Fiber loss | Connector loss | Dispersion |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dr` | 0.5 km | 1310 nm | 0.35 dB/km | 1.0 dB | 0 ps/nm/km |
| `fr` | 2.0 km | 1310 nm | 0.35 dB/km | 1.5 dB | 0 ps/nm/km |
| `lr` | 10.0 km | 1310 nm | 0.35 dB/km | 2.0 dB | 0 ps/nm/km |
| `fr_lband` | 2.0 km | 1550 nm | 0.35 dB/km | 1.5 dB | 17 ps/nm/km |
| `lr_lband` | 10.0 km | 1550 nm | 0.35 dB/km | 2.0 dB | 17 ps/nm/km |

Notes:

- 1310 nm dispersion is set to zero as a first-order approximation near the SMF zero-dispersion region.
- 1550 nm presets use 17 ps/nm/km as a generic SMF dispersion placeholder.
- Real PMD work needs optical modulation amplitude, TDECQ/SECQ, launch power, receiver sensitivity, extinction ratio, RIN, connector budgets, and compliance masks from the specific clause or implementation agreement.

## What Is Not Yet Captured

- Full IEEE/OIF channel masks or COM workflows.
- S-parameter import for package, board, connector, module, or test fixture.
- Exact transmitter FFE tap limits from a chosen clause or IA.
- Exact CTLE pole/zero presets from a selected reference receiver.
- Optical PMD compliance metrics such as TDECQ/SECQ and stressed sensitivity.

When these are added, update this file first, then the profile dictionaries.
