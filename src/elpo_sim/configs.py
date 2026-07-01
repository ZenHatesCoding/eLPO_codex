def _deep_update(dst, src):
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            _deep_update(dst[key], value)
        else:
            dst[key] = value
    return dst


def base_params(bit_rate_gbps=112):
    symbol_rate_hz = bit_rate_gbps * 1e9 / 2.0
    dsp_sps = 2
    channel_oversample = 4
    nyquist_hz = symbol_rate_hz / 2.0
    return {
        "name": f"{bit_rate_gbps}G_PAM4_LPO",
        "profile_name": "generic_behavioral",
        "bit_rate_gbps": bit_rate_gbps,
        "symbol_rate_hz": symbol_rate_hz,
        "n_symbols": 12000,
        "seed": 7,
        "dsp_sps": dsp_sps,
        "dac_sps": dsp_sps,
        "adc_sps": dsp_sps,
        "channel_oversample": channel_oversample,
        "channel_sps": dsp_sps * channel_oversample,
        "eye_sps": 50,
        "waveform_sps": 50,
        "ideal_link": False,
        "tx_ffe_taps": [-0.08, 1.0, -0.05],
        "tx_ctle": {
            "enable": True,
            "zero_hz": 0.18 * symbol_rate_hz,
            "pole1_hz": 0.75 * symbol_rate_hz,
            "pole2_hz": 1.4 * symbol_rate_hz,
            "dc_gain": 0.9,
        },
        "dac": {
            "bits": 7,
            "bandwidth_hz": 0.55 * symbol_rate_hz,
            "order": 1,
            "full_scale": 3.5,
            "noise_rms": 0.0015,
        },
        "driver": {
            "gain_v_per_unit": 0.42,
            "bandwidth_hz": 0.65 * symbol_rate_hz,
            "order": 1,
            "clip_v": 1.8,
            "noise_rms": 0.002,
        },
        "electrical_channel": {
            "enable": False,
            "loss_db_at_hz": None,
            "loss_ref_hz": nyquist_hz,
            "loss_exponent": 1.0,
        },
        "mzm": {
            "vpi_v": 3.5,
            "bias_v": 0.0,
            "optical_power_w": 1.0e-3,
            "extinction_ratio_db": 6.0,
        },
        "optical_channel": {
            "loss_db": 0.0,
            "connector_loss_db": 1.0,
            "fiber_length_km": 0.5,
            "fiber_loss_db_per_km": 0.35,
            "wavelength_nm": 1310.0,
            "dispersion_ps_nm_km": 0.0,
            "bandwidth_hz": 0.85 * symbol_rate_hz,
            "order": 1,
            "rin_db_per_hz": -155.0,
        },
        "rx": {
            "responsivity_a_per_w": 0.75,
            "tia_ohm": 650.0,
            "bandwidth_hz": 0.65 * symbol_rate_hz,
            "order": 1,
            "input_noise_rms_v": 0.0008,
            "adc_bits": 7,
            "adc_full_scale_v": 0.6,
            "adc_noise_rms_v": 0.0,
        },
        "rx_ffe": {
            "n_taps": 19,
            "mu": 0.035,
            "dd_mu": 0.004,
            "n_train": 3000,
            "dd_start": 3000,
            "max_symbol_delay": 12,
        },
        "mlse": {
            "enable": True,
            "memory_depth": 1,
            "train_symbols": 3500,
        },
    }


def apply_electrical_standard_channel(cfg, loss_db_at_hz, loss_ref_hz, exponent=1.0):
    cfg["electrical_channel"].update({
        "enable": True,
        "loss_db_at_hz": loss_db_at_hz,
        "loss_ref_hz": loss_ref_hz,
        "loss_exponent": exponent,
    })
    return cfg


def apply_optical_reach(cfg, reach):
    reach = reach.lower()
    profiles = {
        "dr": {"fiber_length_km": 0.5, "connector_loss_db": 1.0, "dispersion_ps_nm_km": 0.0, "wavelength_nm": 1310.0},
        "fr": {"fiber_length_km": 2.0, "connector_loss_db": 1.5, "dispersion_ps_nm_km": 0.0, "wavelength_nm": 1310.0},
        "lr": {"fiber_length_km": 10.0, "connector_loss_db": 2.0, "dispersion_ps_nm_km": 0.0, "wavelength_nm": 1310.0},
        "fr_lband": {"fiber_length_km": 2.0, "connector_loss_db": 1.5, "dispersion_ps_nm_km": 17.0, "wavelength_nm": 1550.0},
        "lr_lband": {"fiber_length_km": 10.0, "connector_loss_db": 2.0, "dispersion_ps_nm_km": 17.0, "wavelength_nm": 1550.0},
    }
    if reach not in profiles:
        raise ValueError(f"unknown optical reach profile: {reach}")
    cfg["optical_reach"] = reach
    cfg["optical_channel"].update(profiles[reach])
    return cfg


def params_112g(reach="dr"):
    # IEEE 802.3ck anchor: 100G/lane electrical backplane IL <= 28 dB at 26.56 GHz.
    symbol_rate_hz = 53.125e9
    cfg = base_params(106.25)
    cfg["name"] = "112G_PAM4_LPO_8023CK_LIKE"
    cfg["profile_name"] = "802.3ck_like_100G_per_lane"
    cfg["symbol_rate_hz"] = symbol_rate_hz
    cfg["bit_rate_gbps"] = 106.25
    _retune_rate_dependent_params(cfg)
    apply_electrical_standard_channel(cfg, 28.0, 26.56e9, exponent=1.0)
    apply_optical_reach(cfg, reach)
    return cfg


def params_224g(reach="dr"):
    # IEEE 802.3dj anchor: 200G/lane electrical backplane IL <= 40 dB at 53.125 GHz.
    symbol_rate_hz = 106.25e9
    cfg = base_params(212.5)
    cfg["name"] = "224G_PAM4_LPO_8023DJ_LIKE"
    cfg["profile_name"] = "802.3dj_like_200G_per_lane"
    cfg["symbol_rate_hz"] = symbol_rate_hz
    cfg["bit_rate_gbps"] = 212.5
    _retune_rate_dependent_params(cfg)
    apply_electrical_standard_channel(cfg, 40.0, 53.125e9, exponent=1.0)
    apply_optical_reach(cfg, reach)
    cfg["dac"]["bits"] = 6
    cfg["rx"]["adc_bits"] = 6
    cfg["driver"]["noise_rms"] = 0.003
    cfg["rx"]["input_noise_rms_v"] = 0.0012
    cfg["rx_ffe"]["n_taps"] = 31
    cfg["rx_ffe"]["mu"] = 0.018
    cfg["rx_ffe"]["max_symbol_delay"] = 20
    return cfg


def _retune_rate_dependent_params(cfg):
    rs = cfg["symbol_rate_hz"]
    cfg["tx_ctle"].update({
        "zero_hz": 0.18 * rs,
        "pole1_hz": 0.75 * rs,
        "pole2_hz": 1.4 * rs,
    })
    cfg["dac"]["bandwidth_hz"] = 0.55 * rs
    cfg["driver"]["bandwidth_hz"] = 0.65 * rs
    cfg["optical_channel"]["bandwidth_hz"] = 0.85 * rs
    cfg["rx"]["bandwidth_hz"] = 0.65 * rs
    cfg["electrical_channel"]["loss_ref_hz"] = rs / 2.0


def params_clean(bit_rate_gbps=112):
    cfg = base_params(bit_rate_gbps)
    cfg["name"] = f"{bit_rate_gbps}G_PAM4_CLEAN_IDEAL"
    cfg["profile_name"] = "clean_ideal"
    cfg["ideal_link"] = True
    cfg["tx_ffe_taps"] = [1.0]
    cfg["tx_ctle"]["enable"] = False
    cfg["dac"].update({"bits": None, "bandwidth_hz": None, "noise_rms": 0.0})
    cfg["driver"].update({"gain_v_per_unit": 1.0, "bandwidth_hz": None, "clip_v": None, "noise_rms": 0.0})
    cfg["mzm"].update({"model": "linear", "optical_power_w": 0.0, "linear_gain_w_per_unit": 1.0})
    cfg["electrical_channel"].update({"enable": False, "loss_db_at_hz": None})
    cfg["optical_channel"].update({"loss_db": 0.0, "connector_loss_db": 0.0, "fiber_length_km": 0.0, "bandwidth_hz": None, "rin_db_per_hz": None})
    cfg["rx"].update({
        "responsivity_a_per_w": 1.0,
        "tia_ohm": 1.0,
        "bandwidth_hz": None,
        "input_noise_rms_v": 0.0,
        "adc_bits": None,
        "adc_noise_rms_v": 0.0,
    })
    cfg["rx_ffe"].update({"n_taps": 7, "mu": 0.05, "dd_mu": 0.0, "n_train": 1000, "dd_start": 1000, "max_symbol_delay": 6})
    cfg["mlse"].update({"enable": False, "memory_depth": 1, "train_symbols": 1000})
    return cfg
