import numpy as np


PAM4_LEVELS = np.array([-3.0, -1.0, 1.0, 3.0])
GRAY_BITS = np.array([[0, 0], [0, 1], [1, 1], [1, 0]], dtype=np.int8)


def random_bits(n_bits, seed=1):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, int(n_bits), dtype=np.int8)


def bits_to_symbols(bits):
    bits = np.asarray(bits, dtype=np.int8)
    if bits.size % 2:
        bits = np.append(bits, 0)
    pairs = bits.reshape(-1, 2)
    idx = np.zeros(pairs.shape[0], dtype=np.int64)
    idx[(pairs[:, 0] == 0) & (pairs[:, 1] == 0)] = 0
    idx[(pairs[:, 0] == 0) & (pairs[:, 1] == 1)] = 1
    idx[(pairs[:, 0] == 1) & (pairs[:, 1] == 1)] = 2
    idx[(pairs[:, 0] == 1) & (pairs[:, 1] == 0)] = 3
    return PAM4_LEVELS[idx], idx


def symbol_indices_to_bits(indices):
    indices = np.asarray(indices, dtype=np.int64)
    return GRAY_BITS[np.clip(indices, 0, 3)].reshape(-1)


def slicer(x):
    x = np.asarray(x)
    return np.digitize(x, [-2.0, 0.0, 2.0]).astype(np.int64)


def slice_to_levels(x):
    return PAM4_LEVELS[slicer(x)]


def normalize_levels(x):
    x = np.asarray(x, dtype=float)
    y = x - np.mean(x)
    scale = np.sqrt(np.mean(y * y))
    if scale <= 1e-15:
        return y
    return y / scale * np.sqrt(np.mean(PAM4_LEVELS * PAM4_LEVELS))


def affine_to_pam4(y, ref_levels=PAM4_LEVELS):
    y = np.asarray(y, dtype=float)
    decisions = slice_to_levels(normalize_levels(y))
    a = np.vstack([y, np.ones_like(y)]).T
    gain, offset = np.linalg.lstsq(a, decisions, rcond=None)[0]
    if abs(gain) < 1e-15:
        return y - np.mean(y)
    return gain * y + offset

