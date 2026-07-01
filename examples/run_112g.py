import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from elpo_sim.configs import params_112g
from elpo_sim.sim import run_link


if __name__ == "__main__":
    cfg = params_112g()
    result = run_link(cfg)
    print("112G PAM4 LPO smoke run")
    print(f"BER FFE   : {result['ber_ffe']:.3e} ({result['bit_errors_ffe']}/{result['bit_count']})")
    print(f"BER final : {result['ber_final']:.3e} ({result['bit_errors_final']}/{result['bit_count']})")
    print(f"SER final : {result['ser_final']:.3e} ({result['sym_errors_final']}/{result['sym_count']})")
    print(f"RX FFE phase={result['ffe']['phase']} delay={result['ffe']['symbol_delay']} mse={result['ffe']['mse']:.3e}")
    print(f"Partial response: {result['partial_response']}")
    print(f"Artifacts: {result['artifact_dir']}")

