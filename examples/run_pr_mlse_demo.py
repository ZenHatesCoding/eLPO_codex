import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from elpo_sim.metrics import ber_from_indices
from elpo_sim.mlse import causal_fir, estimate_noise_whitening_pr, hard_mlse
from elpo_sim.pam4 import bits_to_symbols, random_bits, slicer


if __name__ == "__main__":
    n_symbols = 12000
    rng = np.random.default_rng(7)
    bits = random_bits(2 * n_symbols, seed=7)
    tx_symbols, tx_idx = bits_to_symbols(bits)

    # Model the FFE output after it has equalized the signal path. The remaining
    # noise is colored, which is what the PR/whitening filter is meant to handle.
    rho = 0.85
    white = rng.normal(0.0, 0.45, n_symbols)
    colored_noise = np.zeros(n_symbols)
    for k in range(1, n_symbols):
        colored_noise[k] = rho * colored_noise[k - 1] + white[k]
    ffe_out = tx_symbols + colored_noise

    rx_idx_ffe = slicer(ffe_out)
    ber_ffe, err_ffe, bit_count = ber_from_indices(tx_idx, rx_idx_ffe)

    pr = estimate_noise_whitening_pr(ffe_out[:3000], tx_symbols[:3000], memory_depth=1)
    pr_out = causal_fir(ffe_out, pr)
    mlse_levels = hard_mlse(pr_out, pr)
    rx_idx_mlse = slicer(mlse_levels)
    ber_mlse, err_mlse, _ = ber_from_indices(tx_idx, rx_idx_mlse)

    print("FFE noise-whitening PR-MLSE demo")
    print(f"BER FFE  : {ber_ffe:.3e} ({err_ffe}/{bit_count})")
    print(f"BER MLSE : {ber_mlse:.3e} ({err_mlse}/{bit_count})")
    print(f"Estimated PR whitening filter: {pr}")

