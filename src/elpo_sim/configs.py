def base_params(bit_rate_gbps=112):
    symbol_rate_hz = bit_rate_gbps * 1e9 / 2.0
    dsp_sps = 2
    channel_oversample = 4
    return {
        "name": f"{bit_rate_gbps}G_PAM4_LPO",
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
        "mzm": {
            "vpi_v": 3.5,
            "bias_v": 0.0,
            "optical_power_w": 1.0e-3,
            "extinction_ratio_db": 6.0,
        },
        "optical_channel": {
            "loss_db": 3.0,
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
            "pr_order": 3,
            "train_symbols": 3500,
        },
    }


def params_112g():
    return base_params(112)


def params_224g():
    cfg = base_params(224)
    cfg["dac"]["bits"] = 6
    cfg["rx"]["adc_bits"] = 6
    cfg["driver"]["noise_rms"] = 0.003
    cfg["rx"]["input_noise_rms_v"] = 0.0012
    cfg["optical_channel"]["loss_db"] = 4.0
    cfg["rx_ffe"]["n_taps"] = 23
    cfg["rx_ffe"]["mu"] = 0.025
    return cfg


def params_clean(bit_rate_gbps=112):
    cfg = base_params(bit_rate_gbps)
    cfg["name"] = f"{bit_rate_gbps}G_PAM4_CLEAN_IDEAL"
    cfg["ideal_link"] = True
    cfg["tx_ffe_taps"] = [1.0]
    cfg["tx_ctle"]["enable"] = False
    cfg["dac"].update({"bits": None, "bandwidth_hz": None, "noise_rms": 0.0})
    cfg["driver"].update({"gain_v_per_unit": 1.0, "bandwidth_hz": None, "clip_v": None, "noise_rms": 0.0})
    cfg["mzm"].update({"model": "linear", "optical_power_w": 0.0, "linear_gain_w_per_unit": 1.0})
    cfg["optical_channel"].update({"loss_db": 0.0, "bandwidth_hz": None, "rin_db_per_hz": None})
    cfg["rx"].update({
        "responsivity_a_per_w": 1.0,
        "tia_ohm": 1.0,
        "bandwidth_hz": None,
        "input_noise_rms_v": 0.0,
        "adc_bits": None,
        "adc_noise_rms_v": 0.0,
    })
    cfg["rx_ffe"].update({"n_taps": 7, "mu": 0.05, "dd_mu": 0.0, "n_train": 1000, "dd_start": 1000, "max_symbol_delay": 6})
    cfg["mlse"].update({"enable": False, "pr_order": 1, "train_symbols": 1000})
    return cfg
