import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from elpo_sim.configs import params_112g, params_clean, params_pr_mlse_demo
from elpo_sim.mlse import estimate_pr_filter, hard_mlse
from elpo_sim.pam4 import bits_to_symbols, random_bits, slicer
from elpo_sim.sim import run_link


def test_pam4_gray_roundtrip_shapes():
    bits = random_bits(101, seed=11)
    symbols, idx = bits_to_symbols(bits)
    assert symbols.shape == idx.shape
    assert set(np.unique(idx)).issubset({0, 1, 2, 3})


def test_mlse_recovers_simple_partial_response():
    bits = random_bits(1000, seed=2)
    symbols, idx = bits_to_symbols(bits)
    h = np.array([1.0, 0.35, -0.12])
    y = np.convolve(symbols, h, mode="full")[: len(symbols)]
    est = estimate_pr_filter(y[:400], 2, symbols[:400])
    out = hard_mlse(y, est)
    rx = slicer(out)
    assert np.mean(rx[20:-20] != idx[20:-20]) < 0.08


def test_clean_link_has_zero_ber_and_expected_rates():
    cfg = params_clean(112)
    cfg["n_symbols"] = 2500
    cfg["rx_ffe"]["n_train"] = 800
    cfg["rx_ffe"]["dd_start"] = 800
    result = run_link(cfg, artifact_dir="artifacts/test")
    assert result["rates"]["dsp_sps"] == 2
    assert result["rates"]["dac_sps"] == 2
    assert result["rates"]["adc_sps"] == 2
    assert result["rates"]["channel_sps"] == 8
    assert result["rates"]["eye_sps"] == 50
    assert result["ber_ffe"] == 0.0
    assert result["ber_mlse"] is None
    assert result["ber_final"] == 0.0


def test_smoke_link_short():
    cfg = params_112g()
    cfg["n_symbols"] = 2500
    cfg["rx_ffe"]["n_train"] = 800
    cfg["rx_ffe"]["dd_start"] = 800
    cfg["mlse"]["train_symbols"] = 900
    result = run_link(cfg, artifact_dir="artifacts/test")
    assert result["bit_count"] > 1000
    assert np.isfinite(result["ber_final"])
    assert result["rx_ffe_taps"].size == cfg["rx_ffe"]["n_taps"]



def test_pr_target_mlse_improves_over_ffe_slicer():
    cfg = params_pr_mlse_demo(112)
    cfg["n_symbols"] = 3000
    cfg["rx_ffe"]["n_train"] = 1000
    cfg["rx_ffe"]["dd_start"] = 1000
    cfg["mlse"]["train_symbols"] = 1200
    result = run_link(cfg, artifact_dir="artifacts/test")
    assert result["ber_ffe"] > 0.05
    assert result["ber_mlse"] == 0.0
    assert np.allclose(result["partial_response"], cfg["rx_ffe"]["target_response"], atol=0.03)
