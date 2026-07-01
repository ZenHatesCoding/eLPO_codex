import itertools
import numpy as np

from .pam4 import PAM4_LEVELS, slice_to_levels


def burg_ar(x, order):
    x = np.asarray(x, dtype=float) - np.mean(x)
    if order <= 0:
        return np.array([1.0]), 0.0
    ef = x[1:].copy()
    eb = x[:-1].copy()
    a = np.array([1.0], dtype=float)
    e = np.mean(x * x) + 1e-15
    for m in range(1, order + 1):
        den = np.dot(ef, ef) + np.dot(eb, eb) + 1e-15
        k = -2.0 * np.dot(eb, ef) / den
        a_new = np.r_[a, 0.0]
        a_new[1:] += k * a[::-1]
        a = a_new
        e *= max(1.0 - k * k, 1e-12)
        if m < order:
            ef_next = ef[1:] + k * eb[1:]
            eb_next = eb[:-1] + k * ef[:-1]
            ef, eb = ef_next, eb_next
    return a, e


def estimate_pr_filter(y, order=3, refine_symbols=None):
    y = np.asarray(y, dtype=float)
    ar, _ = burg_ar(y, order)
    h = np.r_[1.0, -ar[1:]]
    h = h / (np.sqrt(np.sum(h * h)) + 1e-15)
    if refine_symbols is None:
        refine_symbols = slice_to_levels(y)
    d = np.asarray(refine_symbols, dtype=float)
    n = min(len(y), len(d)) - order
    if n > order + 4:
        A = np.zeros((n, order + 1), dtype=float)
        b = y[order : order + n]
        for row in range(n):
            k = order + row
            A[row, :] = d[k - np.arange(order + 1)]
        try:
            h = np.linalg.lstsq(A, b, rcond=None)[0]
            h = h / (np.max(np.abs(h)) + 1e-15)
        except np.linalg.LinAlgError:
            pass
    return h


def hard_mlse(y, h):
    y = np.asarray(y, dtype=float)
    h = np.asarray(h, dtype=float)
    memory = max(0, len(h) - 1)
    if memory == 0:
        return slice_to_levels(y)
    states = list(itertools.product(PAM4_LEVELS, repeat=memory))
    state_to_i = {s: i for i, s in enumerate(states)}
    n_states = len(states)
    inf = 1e300
    metric = np.full(n_states, inf)
    metric[state_to_i[tuple([0.0] * memory)] if tuple([0.0] * memory) in state_to_i else 0] = 0.0
    prev_state = np.zeros((len(y), n_states), dtype=np.int32)
    prev_sym = np.zeros((len(y), n_states), dtype=float)
    for k, sample in enumerate(y):
        new_metric = np.full(n_states, inf)
        for si, state in enumerate(states):
            base = metric[si]
            if base >= inf / 2:
                continue
            for sym in PAM4_LEVELS:
                seq = (sym,) + state
                pred = float(np.dot(h, np.asarray(seq[: len(h)])))
                new_state = seq[:-1]
                ni = state_to_i[new_state]
                m = base + (sample - pred) ** 2
                if m < new_metric[ni]:
                    new_metric[ni] = m
                    prev_state[k, ni] = si
                    prev_sym[k, ni] = sym
        metric = new_metric
    si = int(np.argmin(metric))
    out = np.zeros(len(y), dtype=float)
    for k in range(len(y) - 1, -1, -1):
        out[k] = prev_sym[k, si]
        si = int(prev_state[k, si])
    return out

