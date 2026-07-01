import numpy as np


def apply_fir(x, taps, mode="same"):
    taps = np.asarray(taps, dtype=float)
    if taps.size == 0:
        return np.asarray(x, dtype=float)
    return np.convolve(np.asarray(x, dtype=float), taps, mode=mode)


def normalize_taps(taps, target_sum=1.0):
    taps = np.asarray(taps, dtype=float)
    s = np.sum(taps)
    if abs(s) < 1e-15:
        return taps
    return taps * (target_sum / s)


def fft_filter(x, sample_rate_hz, response_fn):
    x = np.asarray(x, dtype=float)
    freqs = np.fft.rfftfreq(x.size, d=1.0 / sample_rate_hz)
    X = np.fft.rfft(x)
    H = response_fn(freqs)
    y = np.fft.irfft(X * H, n=x.size)
    return np.real(y)


def lowpass(x, sample_rate_hz, bandwidth_hz, order=1):
    if bandwidth_hz is None or bandwidth_hz <= 0:
        return np.asarray(x, dtype=float)

    def response(freqs):
        mag = 1.0 / np.sqrt(1.0 + (freqs / bandwidth_hz) ** (2 * order))
        return mag

    return fft_filter(x, sample_rate_hz, response)


def insertion_loss(x, sample_rate_hz, loss_db_at_hz, ref_hz, exponent=1.0, dc_loss_db=0.0):
    if loss_db_at_hz is None or loss_db_at_hz <= 0 or ref_hz is None or ref_hz <= 0:
        return np.asarray(x, dtype=float)

    def response(freqs):
        ratio = np.clip(freqs / ref_hz, 0.0, None)
        loss_db = dc_loss_db + loss_db_at_hz * ratio ** exponent
        return 10.0 ** (-loss_db / 20.0)

    return fft_filter(x, sample_rate_hz, response)


def imdd_chromatic_dispersion(x, sample_rate_hz, length_km, dispersion_ps_nm_km=0.0, wavelength_nm=1310.0):
    if not length_km or abs(dispersion_ps_nm_km) <= 1e-15:
        return np.asarray(x, dtype=float)
    c = 299792458.0
    wavelength_m = wavelength_nm * 1e-9
    dispersion_s_m2 = dispersion_ps_nm_km * 1e-6
    length_m = length_km * 1e3

    def response(freqs):
        phase = np.pi * dispersion_s_m2 * wavelength_m * wavelength_m * length_m * freqs * freqs / c
        return np.cos(phase)

    return fft_filter(x, sample_rate_hz, response)


def ctle(x, sample_rate_hz, zero_hz, pole1_hz, pole2_hz=None, dc_gain=1.0):
    if not zero_hz or not pole1_hz:
        return np.asarray(x, dtype=float)

    def response(freqs):
        s = 1j * freqs
        h = (1.0 + s / zero_hz) / (1.0 + s / pole1_hz)
        if pole2_hz:
            h = h / (1.0 + s / pole2_hz)
        h = h * dc_gain
        return h

    return fft_filter(x, sample_rate_hz, response)


def resample_linear(x, in_sps, out_sps):
    x = np.asarray(x, dtype=float)
    if in_sps == out_sps:
        return x.copy()
    n_symbols = x.size / float(in_sps)
    n_out = int(np.floor(n_symbols * out_sps))
    src = np.arange(x.size, dtype=float)
    dst = np.arange(n_out, dtype=float) * (in_sps / float(out_sps))
    return np.interp(dst, src, x)


def waveform_from_symbols(symbols, sps):
    return np.repeat(np.asarray(symbols, dtype=float), int(sps))


def sample_at_sps(wave, input_sps, output_sps=2, phase_ui=0.0):
    wave = np.asarray(wave, dtype=float)
    step = input_sps / float(output_sps)
    start = phase_ui * input_sps
    n = int(np.floor((wave.size - start) / step))
    idx = start + np.arange(n) * step
    return np.interp(idx, np.arange(wave.size), wave)
