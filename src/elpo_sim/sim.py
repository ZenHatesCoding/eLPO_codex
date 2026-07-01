import os
import numpy as np

from .devices import adc_model, dac_model, driver_model, mzm_model, optical_channel_model, pd_tia_model
from .dsp import train_rx_ffe_lms, dd_lms_update, level_scale_from_training, apply_level_scale
from .filters import apply_fir, ctle, waveform_from_symbols, sample_at_sps, resample_linear
from .metrics import ber_from_indices, ser_from_indices, pam4_eye_openings
from .mlse import causal_fir, estimate_noise_whitening_pr, hard_mlse
from .pam4 import bits_to_symbols, random_bits, slicer, PAM4_LEVELS
from .plotting import save_eye, save_bathtub_like_hist


def _ac_normalize(x, target_rms=None):
    y = np.asarray(x, dtype=float) - np.mean(x)
    rms = np.sqrt(np.mean(y * y)) + 1e-15
    if target_rms is None:
        target_rms = np.sqrt(np.mean(PAM4_LEVELS * PAM4_LEVELS))
    return y / rms * target_rms


def _rate_plan(cfg):
    dsp_sps = int(cfg.get("dsp_sps", 2))
    dac_sps = int(cfg.get("dac_sps", dsp_sps))
    adc_sps = int(cfg.get("adc_sps", dsp_sps))
    if dac_sps != dsp_sps or adc_sps != dsp_sps:
        raise ValueError("This simulator version expects DAC, ADC, and DSP to share dsp_sps=2.")
    channel_sps = int(cfg.get("channel_sps", dsp_sps * int(cfg.get("channel_oversample", 4))))
    eye_sps = int(cfg.get("eye_sps", cfg.get("waveform_sps", 50)))
    return dsp_sps, channel_sps, eye_sps


def run_link(cfg, artifact_dir="artifacts"):
    rng = np.random.default_rng(cfg.get("seed", 1))
    n_symbols = int(cfg.get("n_symbols", 10000))
    dsp_sps, channel_sps, eye_sps = _rate_plan(cfg)
    symbol_rate = cfg["symbol_rate_hz"]
    dsp_sample_rate = symbol_rate * dsp_sps
    channel_sample_rate = symbol_rate * channel_sps

    bits = random_bits(2 * n_symbols, seed=cfg.get("seed", 1))
    tx_symbols, tx_idx = bits_to_symbols(bits)
    tx_precoded = apply_fir(tx_symbols, cfg.get("tx_ffe_taps", [1.0]), mode="same")

    tx2 = waveform_from_symbols(tx_precoded, dsp_sps)
    dac2 = dac_model(tx2, dsp_sample_rate, cfg.get("dac", {}), rng)

    tx_ctle = cfg.get("tx_ctle", {})
    if tx_ctle.get("enable", False):
        dac2 = ctle(
            dac2,
            dsp_sample_rate,
            tx_ctle.get("zero_hz"),
            tx_ctle.get("pole1_hz"),
            tx_ctle.get("pole2_hz"),
            tx_ctle.get("dc_gain", 1.0),
        )

    channel_in = resample_linear(dac2, dsp_sps, channel_sps)
    if cfg.get("ideal_link", False):
        tia_ch = channel_in.copy()
    else:
        drv = driver_model(channel_in, channel_sample_rate, cfg.get("driver", {}), rng)
        optical_tx = mzm_model(drv, cfg.get("mzm", {}))
        optical_rx = optical_channel_model(optical_tx, channel_sample_rate, cfg.get("optical_channel", {}), rng)
        tia_ch = pd_tia_model(optical_rx, channel_sample_rate, cfg.get("rx", {}), rng)

    adc_input2 = sample_at_sps(tia_ch, channel_sps, dsp_sps, phase_ui=0.0)
    adc2 = adc_model(adc_input2, cfg.get("rx", {}), rng)
    x2 = _ac_normalize(adc2)

    rx_ffe_cfg = cfg.get("rx_ffe", {})
    ffe = train_rx_ffe_lms(x2, tx_symbols, rx_ffe_cfg)
    y_raw, taps_dd = dd_lms_update(
        x2,
        ffe["taps"],
        ffe["phase"],
        ffe["symbol_delay"],
        rx_ffe_cfg,
    )
    aligned_tx = tx_symbols[: len(y_raw)]
    n_scale = min(rx_ffe_cfg.get("n_train", 1000), len(y_raw), len(aligned_tx))
    gain, offset = level_scale_from_training(y_raw[:n_scale], aligned_tx[:n_scale])
    y = apply_level_scale(y_raw, gain, offset)
    rx_idx_ffe = slicer(y)

    mlse_cfg = cfg.get("mlse", {})
    mlse_enabled = bool(mlse_cfg.get("enable", True))
    pr = None
    y_pr = None
    rx_idx_mlse = None
    y_mlse_levels = None
    if mlse_enabled:
        memory_depth = int(mlse_cfg.get("memory_depth", 1))
        n_pr = min(int(mlse_cfg.get("train_symbols", 3000)), len(y), len(aligned_tx))
        pr = estimate_noise_whitening_pr(y[:n_pr], aligned_tx[:n_pr], memory_depth)
        y_pr = causal_fir(y, pr)
        y_mlse_levels = hard_mlse(y_pr, pr)
        rx_idx_mlse = slicer(y_mlse_levels)

    ber_ffe, bit_errors_ffe, bit_count = ber_from_indices(tx_idx, rx_idx_ffe)
    ser_ffe, sym_errors_ffe, sym_count = ser_from_indices(tx_idx, rx_idx_ffe)
    if rx_idx_mlse is None:
        ber_mlse = None
        ser_mlse = None
        bit_errors_mlse = None
        sym_errors_mlse = None
        rx_idx_final = rx_idx_ffe
    else:
        ber_mlse, bit_errors_mlse, _ = ber_from_indices(tx_idx, rx_idx_mlse)
        ser_mlse, sym_errors_mlse, _ = ser_from_indices(tx_idx, rx_idx_mlse)
        rx_idx_final = rx_idx_mlse

    ber_final, bit_errors_final, _ = ber_from_indices(tx_idx, rx_idx_final)
    ser_final, sym_errors_final, _ = ser_from_indices(tx_idx, rx_idx_final)

    name = cfg.get("name", "run")
    out_dir = os.path.join(artifact_dir, name)
    os.makedirs(out_dir, exist_ok=True)
    eye_wave = resample_linear(x2[: min(len(x2), 2 * 5000 * dsp_sps)], dsp_sps, eye_sps)
    phase_samples = ffe["phase"] * eye_sps / float(dsp_sps)
    save_eye(eye_wave, eye_sps, os.path.join(out_dir, "eye_rx_input_50sps.png"), f"{name} RX input eye, 50 sps", phase_samples=phase_samples)
    save_bathtub_like_hist(y, os.path.join(out_dir, "ffe_hist.png"), f"{name} 1 sps RX FFE output")

    return {
        "name": name,
        "bit_rate_gbps": cfg.get("bit_rate_gbps"),
        "symbol_rate_hz": symbol_rate,
        "rates": {
            "dsp_sps": dsp_sps,
            "dac_sps": dsp_sps,
            "adc_sps": dsp_sps,
            "channel_sps": channel_sps,
            "eye_sps": eye_sps,
            "dsp_sample_rate_hz": dsp_sample_rate,
            "channel_sample_rate_hz": channel_sample_rate,
        },
        "ffe": ffe,
        "rx_ffe_taps": taps_dd,
        "level_scale": (gain, offset),
        "partial_response": pr,
        "mlse_enabled": mlse_enabled,
        "ber_ffe": ber_ffe,
        "ser_ffe": ser_ffe,
        "bit_errors_ffe": bit_errors_ffe,
        "sym_errors_ffe": sym_errors_ffe,
        "ber_mlse": ber_mlse,
        "ser_mlse": ser_mlse,
        "bit_errors_mlse": bit_errors_mlse,
        "sym_errors_mlse": sym_errors_mlse,
        "ber_final": ber_final,
        "ser_final": ser_final,
        "bit_errors_final": bit_errors_final,
        "sym_errors_final": sym_errors_final,
        "bit_count": bit_count,
        "sym_count": sym_count,
        "eye_openings": pam4_eye_openings(y),
        "artifact_dir": out_dir,
        "rx_idx_ffe": rx_idx_ffe,
        "rx_idx_mlse": rx_idx_mlse,
        "rx_idx_final": rx_idx_final,
        "y_ffe": y,
        "y_pr": y_pr,
        "y_mlse_levels": y_mlse_levels,
        "snapshots": {
            "tx_symbols": tx_symbols,
            "tx2": tx2,
            "channel_in_8sps": channel_in,
            "tia_channel_8sps": tia_ch,
            "adc2": adc2,
            "x2_dsp": x2,
        },
    }

