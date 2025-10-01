from __future__ import annotations

from math import pi

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

from audio_filters.iir_filter import IIRFilter


def _calculate_fft(filter_type: IIRFilter, samplerate: int) -> np.ndarray:
    """
    G6/G7 Optimization: Helper function using bulk processing.
    Calculates the impulse response and FFT efficiently.
    """
    size = 512
    inputs = np.zeros(size)
    inputs[0] = 1.0

    outputs = scipy.signal.lfilter(filter_type.b_coeffs, filter_type.a_coeffs, inputs)

    filler = np.zeros(samplerate - size)  # zero-padding
    full_output = np.concatenate((outputs, filler))
    return np.fft.fft(full_output)


def show_frequency_response(filter_type: IIRFilter, samplerate: int) -> None:
    """
    Show frequency response of a filter

    >>> from audio_filters.iir_filter import IIRFilter
    >>> filt = IIRFilter(4)
    >>> show_frequency_response(filt, 48000)
    """
    fft_out = _calculate_fft(filter_type, samplerate)
    fft_db = 20 * np.log10(np.abs(fft_out))

    # Frequencies on log scale from 24 to nyquist frequency
    plt.xlim(24, samplerate / 2 - 1)
    plt.xlabel("Frequency (Hz)")
    plt.xscale("log")

    # G9 Optimization: Inlined the get_bounds() function to remove a function call.
    lowest = min([-20, np.min(fft_db[1 : samplerate // 2 - 1])])
    highest = max([20, np.max(fft_db[1 : samplerate // 2 - 1])])
    plt.ylim(max([-80, lowest]), min([80, highest]))
    plt.ylabel("Gain (dB)")

    plt.plot(fft_db)
    plt.show()


def show_phase_response(filter_type: IIRFilter, samplerate: int) -> None:
    """
    Show phase response of a filter

    >>> from audio_filters.iir_filter import IIRFilter
    >>> filt = IIRFilter(4)
    >>> show_phase_response(filt, 48000)
    """
    fft_out = _calculate_fft(filter_type, samplerate)
    phase_unwrapped = np.unwrap(np.angle(fft_out), -2 * pi)

    # Frequencies on log scale from 24 to nyquist frequency
    plt.xlim(24, samplerate / 2 - 1)
    plt.xlabel("Frequency (Hz)")
    plt.xscale("log")

    plt.ylim(-2 * pi, 2 * pi)
    plt.ylabel("Phase shift (Radians)")
    plt.plot(phase_unwrapped)
    plt.show()