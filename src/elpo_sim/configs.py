def base_params(bit_rate_gbps=112):
    symbol_rate_hz = bit_rate_gbps * 1e9 / 2.0
    return {
        "name": f"{bit_rate_gbps}G_PAM4_LPO",
        "bit_rate_gbps": bit_rate_gbps,
        "symbol_rate_hz": symbol_rate_hz,
        "n_symbols": 12000,
        "seed": 7,
        "waveform_sps": 50,
        "dsp_sps": 2,
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
            "bandwidth_hz": 0.45 * symbol_rate_hz,
            "order": 1,
            "full_scale": 3.5,
            "noise_rms": 0.003,
        },
        "driver": {
            "gain_v_per_unit": 0.42,
            "bandwidth_hz": 0.55 * symbol_rate_hz,
            "order": 1,
            "clip_v": 1.8,
            "noise_rms": 0.004,
        },
        "mzm": {
            "vpi_v": 3.5,
            "bias_v": 0.0,
            "optical_power_w": 1.0e-3,
            "extinction_ratio_db": 6.0,
        },
        "optical_channel": {
            "loss_db": 4.0,
            "bandwidth_hz": 0.75 * symbol_rate_hz,
            "order": 1,
            "rin_db_per_hz": -150.0,
        },
        "rx": {
            "responsivity_a_per_w": 0.75,
            "tia_ohm": 650.0,
            "bandwidth_hz": 0.55 * symbol_rate_hz,
            "order": 1,
            "input_noise_rms_v": 0.0015,
            "adc_bits": 7,
            "adc_full_scale_v": 0.6,
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
    cfg["driver"]["noise_rms"] = 0.006
    cfg["rx"]["input_noise_rms_v"] = 0.0022
    cfg["optical_channel"]["loss_db"] = 5.0
    cfg["rx_ffe"]["n_taps"] = 23
    cfg["rx_ffe"]["mu"] = 0.025
    return cfg

