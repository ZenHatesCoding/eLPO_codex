import os
import numpy as np

os.environ.setdefault("MPLCONFIGDIR", os.path.abspath(os.path.join("artifacts", ".mplconfig")))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .metrics import eye_matrix


def save_eye(wave, sps, path, title):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mat = eye_matrix(wave, sps=sps, ui=2)
    t = np.arange(mat.shape[1]) / float(sps) if mat.size else []
    plt.figure(figsize=(7, 4))
    if mat.size:
        step = max(1, mat.shape[0] // 500)
        for row in mat[::step]:
            plt.plot(t, row, color="#1f77b4", alpha=0.04, linewidth=0.7)
    plt.title(title)
    plt.xlabel("UI")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
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




