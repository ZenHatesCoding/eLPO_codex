import numpy as np

from .pam4 import slicer, symbol_indices_to_bits


def ber_from_indices(tx_idx, rx_idx):
    n = min(len(tx_idx), len(rx_idx))
    tx_bits = symbol_indices_to_bits(tx_idx[:n])
    rx_bits = symbol_indices_to_bits(rx_idx[:n])
    errors = int(np.sum(tx_bits != rx_bits))
    return errors / max(1, tx_bits.size), errors, tx_bits.size


def ser_from_indices(tx_idx, rx_idx):
    n = min(len(tx_idx), len(rx_idx))
    errors = int(np.sum(np.asarray(tx_idx[:n]) != np.asarray(rx_idx[:n])))
    return errors / max(1, n), errors, n


def eye_matrix(wave, sps=50, ui=2):
    wave = np.asarray(wave, dtype=float)
    span = int(sps * ui)
    n = wave.size // sps - ui
    if n <= 0:
        return np.empty((0, span))
    mat = np.zeros((n, span), dtype=float)
    for i in range(n):
        mat[i, :] = wave[i * sps : i * sps + span]
    return mat


def pam4_eye_openings(samples_1sps):
    samples = np.asarray(samples_1sps, dtype=float)
    idx = slicer(samples)
    openings = []
    for low, high in [(0, 1), (1, 2), (2, 3)]:
        lo = samples[idx == low]
        hi = samples[idx == high]
        if lo.size < 4 or hi.size < 4:
            openings.append(np.nan)
        else:
            openings.append(np.percentile(hi, 5) - np.percentile(lo, 95))
    return np.array(openings)

