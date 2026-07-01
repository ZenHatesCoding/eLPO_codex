import os
import numpy as np

from .devices import dac_model, driver_model, mzm_model, optical_channel_model, pd_tia_adc_model
from .dsp import train_rx_ffe_lms, dd_lms_update, level_scale_from_training, apply_level_scale
from .filters import apply_fir, ctle, waveform_from_symbols, sample_at_sps
from .metrics import ber_from_indices, ser_from_indices, pam4_eye_openings
from .mlse import estimate_pr_filter, hard_mlse
from .pam4 import bits_to_symbols, random_bits, slicer, PAM4_LEVELS
from .plotting import save_eye, save_bathtub_like_hist


def run_link(cfg, artifact_dir="artifacts"):
    rng = np.random.default_rng(cfg.get("seed", 1))
    n_symbols = int(cfg.get("n_symbols", 10000))
    bits = random_bits(2 * n_symbols, seed=cfg.get("seed", 1))
    tx_symbols, tx_idx = bits_to_symbols(bits)
    tx_precoded = apply_fir(tx_symbols, cfg.get("tx_ffe_taps", [1.0]), mode="same")

    wave_sps = int(cfg.get("waveform_sps", 50))
    sample_rate = cfg["symbol_rate_hz"] * wave_sps
    wave = waveform_from_symbols(tx_precoded, wave_sps)

    tx_ctle = cfg.get("tx_ctle", {})
    if tx_ctle.get("enable", False):
        wave = ctle(
            wave,
            sample_rate,
            tx_ctle.get("zero_hz"),
            tx_ctle.get("pole1_hz"),
            tx_ctle.get("pole2_hz"),
            tx_ctle.get("dc_gain", 1.0),
        )

    dac = dac_model(wave, sample_rate, cfg.get("dac", {}), rng)
    drv = driver_model(dac, sample_rate, cfg.get("driver", {}), rng)
    optical_tx = mzm_model(drv, cfg.get("mzm", {}))
    optical_rx = optical_channel_model(optical_tx, sample_rate, cfg.get("optical_channel", {}), rng)
    adc_wave = pd_tia_adc_model(optical_rx, sample_rate, cfg.get("rx", {}), rng)

    x2 = sample_at_sps(adc_wave, wave_sps, int(cfg.get("dsp_sps", 2)), phase_ui=0.0)
    x2 = x2 - np.mean(x2)
    x2_rms = np.sqrt(np.mean(x2 * x2)) + 1e-15
    x2 = x2 / x2_rms * np.sqrt(np.mean(PAM4_LEVELS * PAM4_LEVELS))
    ffe = train_rx_ffe_lms(x2, tx_symbols, cfg.get("rx_ffe", {}))
    y_raw, taps_dd = dd_lms_update(
        x2,
        ffe["taps"],
        ffe["phase"],
        ffe["symbol_delay"],
        cfg.get("rx_ffe", {}),
    )
    aligned_tx = tx_symbols[: len(y_raw)]
    gain, offset = level_scale_from_training(
        y_raw[: cfg["rx_ffe"].get("n_train", 1000)],
        aligned_tx[: cfg["rx_ffe"].get("n_train", 1000)],
    )
    y = apply_level_scale(y_raw, gain, offset)
    rx_idx_ffe = slicer(y)

    mlse_cfg = cfg.get("mlse", {})
    pr = None
    rx_idx_final = rx_idx_ffe
    y_mlse_levels = PAM4_LEVELS[rx_idx_ffe]
    if mlse_cfg.get("enable", True):
        n_pr = min(int(mlse_cfg.get("train_symbols", 3000)), len(y))
        pr = estimate_pr_filter(y[:n_pr], int(mlse_cfg.get("pr_order", 3)), aligned_tx[:n_pr])
        mlse_levels = hard_mlse(y, pr)
        rx_idx_final = slicer(mlse_levels)
        y_mlse_levels = mlse_levels

    ber_ffe, bit_errors_ffe, bit_count = ber_from_indices(tx_idx, rx_idx_ffe)
    ser_ffe, sym_errors_ffe, sym_count = ser_from_indices(tx_idx, rx_idx_ffe)
    ber_final, bit_errors_final, _ = ber_from_indices(tx_idx, rx_idx_final)
    ser_final, sym_errors_final, _ = ser_from_indices(tx_idx, rx_idx_final)

    name = cfg.get("name", "run")
    out_dir = os.path.join(artifact_dir, name)
    os.makedirs(out_dir, exist_ok=True)
    save_eye(adc_wave[: min(len(adc_wave), 5000 * wave_sps)], wave_sps, os.path.join(out_dir, "eye_50sps.png"), f"{name} RX eye at 50 sps")
    save_bathtub_like_hist(y, os.path.join(out_dir, "ffe_hist.png"), f"{name} 1 sps RX FFE output")

    return {
        "name": name,
        "bit_rate_gbps": cfg.get("bit_rate_gbps"),
        "symbol_rate_hz": cfg.get("symbol_rate_hz"),
        "ffe": ffe,
        "rx_ffe_taps": taps_dd,
        "level_scale": (gain, offset),
        "partial_response": pr,
        "ber_ffe": ber_ffe,
        "ser_ffe": ser_ffe,
        "bit_errors_ffe": bit_errors_ffe,
        "sym_errors_ffe": sym_errors_ffe,
        "ber_final": ber_final,
        "ser_final": ser_final,
        "bit_errors_final": bit_errors_final,
        "sym_errors_final": sym_errors_final,
        "bit_count": bit_count,
        "sym_count": sym_count,
        "eye_openings": pam4_eye_openings(y),
        "artifact_dir": out_dir,
        "rx_idx_final": rx_idx_final,
        "y_ffe": y,
        "y_mlse_levels": y_mlse_levels,
    }


