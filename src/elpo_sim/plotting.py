import os
import numpy as np

os.environ.setdefault("MPLCONFIGDIR", os.path.abspath(os.path.join("artifacts", ".mplconfig")))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .metrics import eye_matrix


def _normalize_for_eye(wave):
    y = np.asarray(wave, dtype=float)
    y = y - np.mean(y)
    rms = np.sqrt(np.mean(y * y)) + 1e-15
    return y / rms


def save_eye(wave, sps, path, title, phase_samples=0, max_traces=1200, normalize=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wave = np.asarray(wave, dtype=float)
    if normalize:
        wave = _normalize_for_eye(wave)
    phase_samples = int(round(phase_samples)) % max(1, int(sps))
    if phase_samples:
        wave = wave[phase_samples:]
    mat = eye_matrix(wave, sps=sps, ui=2)
    t = np.arange(mat.shape[1]) / float(sps) if mat.size else []
    plt.figure(figsize=(7.5, 4.5))
    if mat.size:
        step = max(1, mat.shape[0] // max_traces)
        for row in mat[::step]:
            plt.plot(t, row, color="#1f77b4", alpha=0.035, linewidth=0.65)
        q05 = np.percentile(mat, 5, axis=0)
        q50 = np.percentile(mat, 50, axis=0)
        q95 = np.percentile(mat, 95, axis=0)
        plt.plot(t, q05, color="#d62728", alpha=0.8, linewidth=0.8)
        plt.plot(t, q50, color="#111111", alpha=0.8, linewidth=0.8)
        plt.plot(t, q95, color="#d62728", alpha=0.8, linewidth=0.8)
        plt.axvline(1.0, color="#2ca02c", alpha=0.5, linewidth=1.0)
    plt.title(title)
    plt.xlabel("UI")
    plt.ylabel("Normalized amplitude" if normalize else "Amplitude")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, dpi=170)
    plt.close()


def save_bathtub_like_hist(samples, path, title):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.hist(samples, bins=120, color="#444444", alpha=0.85)
    plt.title(title)
    plt.xlabel("FFE/MLSE input amplitude")
    plt.ylabel("Count")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
