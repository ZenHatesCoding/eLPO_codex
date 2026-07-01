import copy
import csv
import math
import os

import numpy as np

from .configs import params_112g
from .sim import run_link


def expand_taps(taps, n_taps=9, main_index=None):
    taps = np.asarray(taps, dtype=float).ravel()
    if taps.size == 0:
        taps = np.array([1.0], dtype=float)
    if main_index is None:
        main_index = n_taps // 2
    old_main = int(np.argmax(np.abs(taps)))
    out = np.zeros(int(n_taps), dtype=float)
    for old_i, value in enumerate(taps):
        new_i = main_index + old_i - old_main
        if 0 <= new_i < out.size:
            out[new_i] = value
    return out


def default_tx_ffe_bounds(seed_taps, side_span=0.35, main_span=0.35, hard_limit=1.8):
    seed = np.asarray(seed_taps, dtype=float)
    bounds = []
    main = int(np.argmax(np.abs(seed)))
    for i, value in enumerate(seed):
        span = main_span if i == main else side_span
        lo = max(-hard_limit, value - span)
        hi = min(hard_limit, value + span)
        if i == main:
            lo = max(0.2, lo)
        bounds.append((float(lo), float(hi)))
    return np.asarray(bounds, dtype=float)


def normalized_objective_from_ber(ber, bit_errors, bit_count):
    if bit_count <= 0:
        return 0.0
    if ber is None:
        return 0.0
    smoothed = (float(bit_errors) + 0.5) / (float(bit_count) + 1.0)
    return float(math.log10(max(smoothed, 1e-16)))


def evaluate_tx_ffe(cfg, taps, artifact_dir=None):
    run_cfg = copy.deepcopy(cfg)
    run_cfg["tx_ffe_taps"] = [float(x) for x in taps]
    run_cfg["output_plots"] = False
    result = run_link(run_cfg, artifact_dir=artifact_dir)
    target_ber = result["ber_mlse"] if result["ber_mlse"] is not None else result["ber_final"]
    target_errors = result["bit_errors_mlse"] if result["bit_errors_mlse"] is not None else result["bit_errors_final"]
    objective = normalized_objective_from_ber(target_ber, target_errors, result["bit_count"])
    return {
        "objective": objective,
        "ber_mlse": result["ber_mlse"],
        "ber_final": result["ber_final"],
        "bit_errors_mlse": result["bit_errors_mlse"],
        "bit_errors_final": result["bit_errors_final"],
        "bit_count": result["bit_count"],
        "ser_mlse": result["ser_mlse"],
        "rx_ffe_mse": result["ffe"]["mse"],
        "partial_response": result["partial_response"],
    }


class GaussianProcessRegressor:
    def __init__(self, bounds, length_scale=0.45, signal_var=1.0, noise_var=1e-6):
        self.bounds = np.asarray(bounds, dtype=float)
        self.length_scale = float(length_scale)
        self.signal_var = float(signal_var)
        self.noise_var = float(noise_var)
        self.x_train = None
        self.y_mean = 0.0
        self.y_std = 1.0
        self._xn = None
        self._yn = None
        self._chol = None
        self._alpha = None

    def _normalize_x(self, x):
        x = np.asarray(x, dtype=float)
        span = self.bounds[:, 1] - self.bounds[:, 0]
        return (x - self.bounds[:, 0]) / np.maximum(span, 1e-12)

    def _kernel(self, a, b):
        a = np.atleast_2d(a)
        b = np.atleast_2d(b)
        diff = a[:, None, :] - b[None, :, :]
        dist2 = np.sum(diff * diff, axis=2)
        return self.signal_var * np.exp(-0.5 * dist2 / (self.length_scale * self.length_scale))

    def fit(self, x_train, y_train):
        self.x_train = np.asarray(x_train, dtype=float)
        y = np.asarray(y_train, dtype=float)
        self.y_mean = float(np.mean(y))
        self.y_std = float(np.std(y))
        if self.y_std < 1e-12:
            self.y_std = 1.0
        self._xn = self._normalize_x(self.x_train)
        self._yn = (y - self.y_mean) / self.y_std
        k = self._kernel(self._xn, self._xn)
        k += (self.noise_var + 1e-10) * np.eye(k.shape[0])
        jitter = 1e-10
        chol = None
        for _ in range(8):
            try:
                chol = np.linalg.cholesky(k + jitter * np.eye(k.shape[0]))
                break
            except np.linalg.LinAlgError:
                jitter *= 10.0
        if chol is None:
            raise np.linalg.LinAlgError("GP covariance matrix is not positive definite")
        self._chol = chol
        tmp = np.linalg.solve(self._chol, self._yn)
        self._alpha = np.linalg.solve(self._chol.T, tmp)
        return self

    def predict(self, x):
        x = np.asarray(x, dtype=float)
        xn = self._normalize_x(x)
        ks = self._kernel(xn, self._xn)
        mean_n = ks @ self._alpha
        v = np.linalg.solve(self._chol, ks.T)
        var_n = np.maximum(self.signal_var - np.sum(v * v, axis=0), 1e-12)
        mean = self.y_mean + self.y_std * mean_n
        std = self.y_std * np.sqrt(var_n)
        return mean, std


def _normal_pdf(z):
    return np.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def _normal_cdf(z):
    z = np.asarray(z, dtype=float)
    return 0.5 * (1.0 + np.vectorize(math.erf)(z / math.sqrt(2.0)))


def expected_improvement_minimize(mean, std, best_y, xi=0.01):
    std = np.maximum(np.asarray(std, dtype=float), 1e-12)
    improvement = float(best_y) - np.asarray(mean, dtype=float) - float(xi)
    z = improvement / std
    return improvement * _normal_cdf(z) + std * _normal_pdf(z)


def propose_candidates(bounds, rng, best_x=None, n_uniform=1200, n_local=600, local_sigma=0.12):
    bounds = np.asarray(bounds, dtype=float)
    lo = bounds[:, 0]
    hi = bounds[:, 1]
    uniform = rng.uniform(lo, hi, size=(int(n_uniform), bounds.shape[0]))
    if best_x is None or n_local <= 0:
        return uniform
    span = hi - lo
    local = rng.normal(np.asarray(best_x, dtype=float), local_sigma * span, size=(int(n_local), bounds.shape[0]))
    local = np.clip(local, lo, hi)
    return np.vstack([uniform, local])


def optimize_tx_ffe(
    cfg=None,
    n_taps=9,
    n_initial=8,
    n_iter=24,
    bounds=None,
    seed=None,
    log_path=None,
    artifact_dir=None,
):
    cfg = params_112g() if cfg is None else copy.deepcopy(cfg)
    rng_seed = seed if seed is not None else cfg.get("optimizer_seed", cfg.get("seed", 1))
    rng = np.random.default_rng(rng_seed)
    start = expand_taps(cfg.get("tx_ffe_taps", [1.0]), n_taps=n_taps)
    if bounds is None:
        bounds = default_tx_ffe_bounds(start)
    bounds = np.asarray(bounds, dtype=float)

    samples = []
    samples.append((start.copy(), evaluate_tx_ffe(cfg, start, artifact_dir=artifact_dir)))
    for _ in range(max(0, int(n_initial) - 1)):
        x = rng.uniform(bounds[:, 0], bounds[:, 1])
        samples.append((x, evaluate_tx_ffe(cfg, x, artifact_dir=artifact_dir)))

    if log_path is not None:
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        _write_log(log_path, samples, n_taps)

    for _ in range(int(n_iter)):
        x_train = np.array([x for x, _ in samples], dtype=float)
        y_train = np.array([m["objective"] for _, m in samples], dtype=float)
        gp = GaussianProcessRegressor(bounds).fit(x_train, y_train)
        best_i = int(np.argmin(y_train))
        cand = propose_candidates(bounds, rng, best_x=x_train[best_i])
        mean, std = gp.predict(cand)
        acq = expected_improvement_minimize(mean, std, np.min(y_train))
        x_next = cand[int(np.argmax(acq))]
        samples.append((x_next, evaluate_tx_ffe(cfg, x_next, artifact_dir=artifact_dir)))
        if log_path is not None:
            _write_log(log_path, samples, n_taps)

    best_i = int(np.argmin([m["objective"] for _, m in samples]))
    return {
        "start_taps": start,
        "bounds": bounds,
        "samples": samples,
        "best_taps": samples[best_i][0],
        "best_metrics": samples[best_i][1],
        "best_index": best_i,
    }


def _write_log(path, samples, n_taps):
    fields = ["iter", "objective", "ber_mlse", "ber_final", "bit_errors_mlse", "bit_errors_final", "bit_count"]
    fields += [f"tap{i}" for i in range(n_taps)]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for i, (x, metrics) in enumerate(samples):
            row = {key: metrics.get(key) for key in fields if key in metrics}
            row["iter"] = i
            for tap_i, value in enumerate(x):
                row[f"tap{tap_i}"] = float(value)
            writer.writerow(row)