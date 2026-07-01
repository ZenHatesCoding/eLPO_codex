import numpy as np

from .filters import lowpass


def quantize_uniform(x, bits, full_scale=None):
    x = np.asarray(x, dtype=float)
    if bits is None or bits <= 0:
        return x
    if full_scale is None:
        full_scale = np.max(np.abs(x)) * 1.05 + 1e-15
    levels = 2 ** int(bits)
    step = 2 * full_scale / (levels - 1)
    q = np.round((np.clip(x, -full_scale, full_scale) + full_scale) / step) * step - full_scale
    return q


def add_awgn_by_rms(x, noise_rms, rng):
    x = np.asarray(x, dtype=float)
    if noise_rms is None or noise_rms <= 0:
        return x
    return x + rng.normal(0.0, noise_rms, x.shape)


def dac_model(symbol_wave, sample_rate_hz, cfg, rng):
    y = quantize_uniform(symbol_wave, cfg.get("bits"), cfg.get("full_scale"))
    y = lowpass(y, sample_rate_hz, cfg.get("bandwidth_hz"), cfg.get("order", 1))
    y = add_awgn_by_rms(y, cfg.get("noise_rms", 0.0), rng)
    return y


def driver_model(v, sample_rate_hz, cfg, rng):
    y = np.asarray(v, dtype=float) * cfg.get("gain_v_per_unit", 1.0)
    y = lowpass(y, sample_rate_hz, cfg.get("bandwidth_hz"), cfg.get("order", 1))
    clip = cfg.get("clip_v")
    if clip:
        y = np.clip(y, -clip, clip)
    y = add_awgn_by_rms(y, cfg.get("noise_rms", 0.0), rng)
    return y


def mzm_model(v, cfg):
    v = np.asarray(v, dtype=float)
    if cfg.get("model") == "linear":
        return cfg.get("optical_power_w", 1e-3) + cfg.get("linear_gain_w_per_unit", 1e-3) * v
    vpi = cfg.get("vpi_v", 3.5)
    bias = cfg.get("bias_v", 0.0)
    optical_power_w = cfg.get("optical_power_w", 1e-3)
    extinction_ratio_db = cfg.get("extinction_ratio_db", 6.0)
    floor = 10 ** (-extinction_ratio_db / 10.0)
    # Quadrature-biased push-pull approximation; monotonic for small-signal PAM4.
    p = 0.5 * (1.0 + np.sin(np.pi * (v - bias) / vpi))
    p = np.clip(p, 0.0, 1.0)
    p = floor + (1.0 - floor) * p
    return optical_power_w * p


def optical_channel_model(power_w, sample_rate_hz, cfg, rng):
    y = np.asarray(power_w, dtype=float)
    y *= 10 ** (-cfg.get("loss_db", 0.0) / 10.0)
    y = lowpass(y, sample_rate_hz, cfg.get("bandwidth_hz"), cfg.get("order", 1))
    rin = cfg.get("rin_db_per_hz")
    if rin is not None:
        rin_lin = 10 ** (rin / 10.0)
        noise_rms = np.sqrt(max(rin_lin, 0.0) * sample_rate_hz / 2.0) * np.mean(np.abs(y))
        y = add_awgn_by_rms(y, noise_rms, rng)
    return np.maximum(y, 0.0)


def pd_tia_model(power_w, sample_rate_hz, cfg, rng):
    current = cfg.get("responsivity_a_per_w", 0.75) * np.asarray(power_w, dtype=float)
    q = 1.602176634e-19
    shot = np.sqrt(2.0 * q * np.maximum(np.mean(current), 0.0) * sample_rate_hz / 2.0)
    current = add_awgn_by_rms(current, shot, rng)
    volts = current * cfg.get("tia_ohm", 500.0)
    volts = lowpass(volts, sample_rate_hz, cfg.get("bandwidth_hz"), cfg.get("order", 1))
    volts = add_awgn_by_rms(volts, cfg.get("input_noise_rms_v", 0.0), rng)
    return volts


def adc_model(volts, cfg, rng):
    y = add_awgn_by_rms(volts, cfg.get("adc_noise_rms_v", 0.0), rng)
    return quantize_uniform(y, cfg.get("adc_bits"), cfg.get("adc_full_scale_v"))


def pd_tia_adc_model(power_w, sample_rate_hz, cfg, rng):
    volts = pd_tia_model(power_w, sample_rate_hz, cfg, rng)
    return adc_model(volts, cfg, rng)
