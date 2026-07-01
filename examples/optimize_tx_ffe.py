import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from elpo_sim.bayes_opt import evaluate_tx_ffe, expand_taps, optimize_tx_ffe
from elpo_sim.configs import params_112g


def parse_taps(text):
    return np.array([float(x.strip()) for x in text.split(",") if x.strip()], dtype=float)


def fmt_ber(value, errors, total):
    if value is None:
        return "disabled"
    return f"{value:.3e} ({errors}/{total})"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single-point or Bayesian optimization run for 9-tap TX FFE.")
    parser.add_argument("--mode", choices=["single", "optimize"], default="single")
    parser.add_argument("--reach", default="dr", choices=["dr", "fr", "lr", "fr_lband", "lr_lband"])
    parser.add_argument("--n-symbols", type=int, default=12000)
    parser.add_argument("--n-taps", type=int, default=9)
    parser.add_argument("--taps", default=None, help="Comma-separated TX FFE taps. Short tap lists are zero-extended around the main tap.")
    parser.add_argument("--initial", type=int, default=8, help="Initial BO evaluations including the current tap vector.")
    parser.add_argument("--iterations", type=int, default=24, help="Bayesian optimization iterations after initialization.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--log", default=os.path.join("artifacts", "tx_ffe_bo", "history.csv"))
    args = parser.parse_args()

    cfg = params_112g(args.reach)
    cfg["n_symbols"] = args.n_symbols
    cfg["seed"] = args.seed
    cfg["output_plots"] = False

    if args.taps is not None:
        cfg["tx_ffe_taps"] = parse_taps(args.taps).tolist()
    taps = expand_taps(cfg["tx_ffe_taps"], n_taps=args.n_taps)

    if args.mode == "single":
        metrics = evaluate_tx_ffe(cfg, taps)
        print("TX FFE single-point simulation")
        print(f"Taps     : {np.array2string(taps, precision=5)}")
        print(f"BER MLSE : {fmt_ber(metrics['ber_mlse'], metrics['bit_errors_mlse'], metrics['bit_count'])}")
        print(f"BER final: {fmt_ber(metrics['ber_final'], metrics['bit_errors_final'], metrics['bit_count'])}")
        print(f"Objective: {metrics['objective']:.6f} log10(smoothed BER)")
    else:
        result = optimize_tx_ffe(
            cfg,
            n_taps=args.n_taps,
            n_initial=args.initial,
            n_iter=args.iterations,
            seed=args.seed,
            log_path=args.log,
        )
        best = result["best_metrics"]
        print("TX FFE Bayesian optimization")
        print(f"Start taps: {np.array2string(result['start_taps'], precision=5)}")
        print(f"Best taps : {np.array2string(result['best_taps'], precision=5)}")
        print(f"Best iter : {result['best_index']}")
        print(f"BER MLSE  : {fmt_ber(best['ber_mlse'], best['bit_errors_mlse'], best['bit_count'])}")
        print(f"Objective : {best['objective']:.6f} log10(smoothed BER)")
        print(f"Log       : {args.log}")