import numpy as np

from .pam4 import PAM4_LEVELS, slice_to_levels


def ffe_output_2sps_to_1sps(x2, taps, phase, n_symbols):
    x2 = np.asarray(x2, dtype=float)
    taps = np.asarray(taps, dtype=float)
    y = np.zeros(n_symbols, dtype=float)
    for k in range(n_symbols):
        end = int(phase + 2 * k)
        idx = end - np.arange(taps.size)
        valid = (idx >= 0) & (idx < x2.size)
        y[k] = np.dot(taps[valid], x2[idx[valid]])
    return y


def _lms_train_once(x2, target, n_taps, phase, mu, n_train, symbol_delay):
    taps = np.zeros(n_taps, dtype=float)
    taps[n_taps // 2] = 1.0
    errs = []
    usable = min(n_train, target.size - symbol_delay)
    for k in range(max(0, usable)):
        end = int(phase + 2 * (k + symbol_delay))
        idx = end - np.arange(n_taps)
        if idx[-1] < 0 or idx[0] >= x2.size:
            continue
        valid = (idx >= 0) & (idx < x2.size)
        xv = np.zeros(n_taps, dtype=float)
        xv[valid] = x2[idx[valid]]
        y = float(np.dot(taps, xv))
        e = target[k] - y
        taps += mu * e * xv / (np.dot(xv, xv) + 1e-12)
        errs.append(e * e)
    mse = np.mean(errs[-max(16, len(errs) // 4) :]) if errs else np.inf
    return taps, mse


def train_rx_ffe_lms(x2, target_symbols, cfg):
    n_taps = int(cfg.get("n_taps", 17))
    mu = float(cfg.get("mu", 0.02))
    n_train = int(cfg.get("n_train", min(2048, len(target_symbols) // 2)))
    max_delay = int(cfg.get("max_symbol_delay", 24))
    best = None
    for phase in [0, 1]:
        for delay in range(max_delay + 1):
            taps, mse = _lms_train_once(x2, target_symbols, n_taps, phase, mu, n_train, delay)
            if best is None or mse < best["mse"]:
                best = {"taps": taps, "phase": phase, "symbol_delay": delay, "mse": mse}
    return best


def dd_lms_update(x2, initial_taps, phase, symbol_delay, cfg):
    n_taps = len(initial_taps)
    taps = np.asarray(initial_taps, dtype=float).copy()
    n_symbols = int((len(x2) - phase) // 2) - symbol_delay
    y = np.zeros(max(0, n_symbols), dtype=float)
    mu = float(cfg.get("dd_mu", cfg.get("mu", 0.005)))
    start = int(cfg.get("dd_start", cfg.get("n_train", 0)))
    for k in range(max(0, n_symbols)):
        end = int(phase + 2 * (k + symbol_delay))
        idx = end - np.arange(n_taps)
        valid = (idx >= 0) & (idx < x2.size)
        xv = np.zeros(n_taps, dtype=float)
        xv[valid] = x2[idx[valid]]
        y[k] = float(np.dot(taps, xv))
        if k >= start:
            d = slice_to_levels(y[k])
            e = d - y[k]
            taps += mu * e * xv / (np.dot(xv, xv) + 1e-12)
    return y, taps


def level_scale_from_training(y, target):
    n = min(len(y), len(target))
    a = np.vstack([y[:n], np.ones(n)]).T
    gain, offset = np.linalg.lstsq(a, target[:n], rcond=None)[0]
    return gain, offset


def apply_level_scale(y, gain, offset):
    return gain * np.asarray(y, dtype=float) + offset

