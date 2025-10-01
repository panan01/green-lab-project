from __future__ import annotations

from abc import abstractmethod
from math import pi
from typing import Protocol

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

# 为了使用 lfilter, 我们需要访问滤波器的系数。
# 因此，我们直接使用 IIRFilter 类而不是更通用的协议。
from audio_filters.iir_filter import IIRFilter


def get_bounds(
    fft_results: np.ndarray, samplerate: int
) -> tuple[int | float, int | float]:
    """
    Get bounds for printing fft results

    >>> import numpy
    >>> array = numpy.linspace(-20.0, 20.0, 1000)
    >>> get_bounds(array, 1000)
    (-20, 20)
    """
    lowest = min([-20, np.min(fft_results[1 : samplerate // 2 - 1])])
    highest = max([20, np.max(fft_results[1 : samplerate // 2 - 1])])
    return lowest, highest


def _calculate_fft(filter_type: IIRFilter, samplerate: int) -> np.ndarray:
    """
    G7 Optimization: Helper function using bulk processing.
    Calculates the impulse response and FFT efficiently.
    """
    size = 512
    # G7: Create impulse signal as a NumPy array for bulk processing
    inputs = np.zeros(size)
    inputs[0] = 1.0

    # G7: Use scipy.signal.lfilter for efficient bulk processing
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

    # Display within reasonable bounds
    bounds = get_bounds(fft_db, samplerate)
    plt.ylim(max([-80, bounds[0]]), min([80, bounds[1]]))
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