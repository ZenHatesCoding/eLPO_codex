# TX FFE Bayesian Optimization

## Motivation

The current TX FFE default, `[-0.08, 1.0, -0.05]`, is a placeholder preset. It is now treated as the starting point for optimization rather than a validated transmitter setting. When a 9-tap optimization is requested, shorter presets are zero-extended around their largest-magnitude main tap, so the current preset becomes:

```text
[0, 0, 0, -0.08, 1.0, -0.05, 0, 0, 0]
```

## White-Box Algorithm

The implementation in `src/elpo_sim/bayes_opt.py` does not call a third-party optimizer. It keeps the Bayesian optimization loop explicit:

1. Evaluate the current 9-tap vector and several random initial vectors.
2. Fit a Gaussian-process surrogate with an RBF kernel using direct NumPy linear algebra and Cholesky factorization.
3. Score candidate tap vectors with expected improvement for minimization.
4. Evaluate the best candidate by calling the existing `run_link()` simulation.
5. Repeat until the simulation budget is exhausted.

The scalar objective is `log10(smoothed BER)` at the MLSE output. If MLSE is disabled, the final BER is used. Smoothing uses `(bit_errors + 0.5) / (bit_count + 1)` so zero-error smoke runs remain comparable.

## Simulation Controls

`run_link()` now honors:

```python
cfg["output_plots"] = False
```

This disables eye and histogram rendering for optimization sweeps while leaving normal example runs unchanged.

## Entry Point

Single-point simulation with the current TX FFE expanded to 9 taps:

```powershell
.\.venv\Scripts\python examples\optimize_tx_ffe.py --mode single
```

Bayesian optimization:

```powershell
.\.venv\Scripts\python examples\optimize_tx_ffe.py --mode optimize --initial 8 --iterations 24
```

The optimization history is written to:

```text
artifacts/tx_ffe_bo/history.csv
```

Columns include iteration index, objective, MLSE BER, final BER, error counts, bit count, and all tap values.

## Research Notes

The BO design follows the standard pattern described in Peter Frazier's tutorial: use a probabilistic surrogate for an expensive black-box function and an acquisition function to trade off exploration and exploitation. Expected improvement was chosen because it has a simple closed form under a Gaussian posterior and is easy to audit in code.

## Notes For Chip-Oriented Follow-Up

- Current bounds are local search bounds around the starting taps, not standard-constrained TX FFE limits.
- The acquisition search uses random and local candidate sets rather than gradient-based acquisition optimization.
- The GP kernel hyperparameters are fixed defaults for auditability; later work can add explicit grid-search hyperparameter fitting if needed.
- For statistically stable BER ranking, increase `--n-symbols`; the default remains short enough for development iteration.