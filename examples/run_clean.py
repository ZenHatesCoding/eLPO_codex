import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from elpo_sim.configs import params_clean
from elpo_sim.sim import run_link


def fmt_ber(value, errors, total):
    if value is None:
        return "disabled"
    return f"{value:.3e} ({errors}/{total})"


if __name__ == "__main__":
    cfg = params_clean(112)
    result = run_link(cfg)
    print("Clean 112G PAM4 code-validation run")
    print(f"BER FFE  : {fmt_ber(result['ber_ffe'], result['bit_errors_ffe'], result['bit_count'])}")
    print(f"BER MLSE : {fmt_ber(result['ber_mlse'], result['bit_errors_mlse'], result['bit_count'])}")
    print(f"SER MLSE : {fmt_ber(result['ser_mlse'], result['sym_errors_mlse'], result['sym_count'])}")
    print(f"Rates    : {result['rates']}")
    print(f"RX FFE phase={result['ffe']['phase']} delay={result['ffe']['symbol_delay']} mse={result['ffe']['mse']:.3e}")
    print(f"Artifacts : {result['artifact_dir']}")
