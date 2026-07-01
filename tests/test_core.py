import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from elpo_sim.configs import params_112g, params_clean
from elpo_sim.bayes_opt import (
    GaussianProcessRegressor,
    default_tx_ffe_bounds,
    expected_improvement_minimize,
    expand_taps,
)
from elpo_sim.metrics import ber_from_indices
from elpo_sim.mlse import causal_fir, estimate_noise_whitening_pr, estimate_pr_filter, hard_mlse
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
    cfg["output_plots"] = False
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
    cfg["output_plots"] = False
    result = run_link(cfg, artifact_dir="artifacts/test")
    assert result["bit_count"] > 1000
    assert np.isfinite(result["ber_final"])
    assert result["rx_ffe_taps"].size == cfg["rx_ffe"]["n_taps"]
    assert len(result["partial_response"]) == 2


def test_noise_whitening_pr_mlse_improves_colored_noise():
    n_symbols = 3000
    rng = np.random.default_rng(7)
    bits = random_bits(2 * n_symbols, seed=7)
    symbols, idx = bits_to_symbols(bits)
    rho = 0.85
    white = rng.normal(0.0, 0.45, n_symbols)
    noise = np.zeros(n_symbols)
    for k in range(1, n_symbols):
        noise[k] = rho * noise[k - 1] + white[k]
    ffe_out = symbols + noise
    ber_ffe, _, _ = ber_from_indices(idx, slicer(ffe_out))
    pr = estimate_noise_whitening_pr(ffe_out[:1200], symbols[:1200], memory_depth=1)
    pr_out = causal_fir(ffe_out, pr)
    mlse_levels = hard_mlse(pr_out, pr)
    ber_mlse, _, _ = ber_from_indices(idx, slicer(mlse_levels))
    assert np.allclose(pr, [1.0, -rho], atol=0.05)
    assert ber_mlse < ber_ffe * 0.25

def test_tx_ffe_taps_expand_around_main_tap():
    taps = expand_taps([-0.08, 1.0, -0.05], n_taps=9)
    assert np.allclose(taps, [0.0, 0.0, 0.0, -0.08, 1.0, -0.05, 0.0, 0.0, 0.0])


def test_white_box_gp_expected_improvement_prefers_promising_region():
    x = np.array([[-1.0], [0.0], [1.0]])
    y = np.array([1.0, 0.0, 1.0])
    bounds = np.array([[-1.5, 1.5]])
    gp = GaussianProcessRegressor(bounds, length_scale=0.5).fit(x, y)
    candidates = np.array([[-1.4], [0.1], [1.4]])
    mean, std = gp.predict(candidates)
    ei = expected_improvement_minimize(mean, std, np.min(y), xi=0.0)
    assert ei[1] > ei[0]
    assert ei[1] > ei[2]
    assert default_tx_ffe_bounds(expand_taps([-0.08, 1.0, -0.05])).shape == (9, 2)
