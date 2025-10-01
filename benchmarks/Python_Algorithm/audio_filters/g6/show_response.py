from __future__ import annotations

from abc import abstractmethod
from math import pi
from typing import Protocol

import matplotlib.pyplot as plt
import numpy as np


class FilterType(Protocol):
    @abstractmethod
    def process(self, sample: float) -> float:
        """
        Calculate y[n]

        >>> issubclass(FilterType, Protocol)
        True
        """


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


def _calculate_fft(filter_type: FilterType, samplerate: int) -> np.ndarray:
    """
    G6 Optimization: Helper function to avoid redundant computation.
    Calculates the impulse response and FFT, which are common steps for
    showing both frequency and phase response.
    """
    size = 512
    inputs = [1] + [0] * (size - 1)
    outputs = [filter_type.process(item) for item in inputs]

    filler = [0] * (samplerate - size)  # zero-padding
    outputs += filler
    return np.fft.fft(outputs)


def show_frequency_response(filter_type: FilterType, samplerate: int) -> None:
    """
    Show frequency response of a filter

    >>> from audio_filters.iir_filter import IIRFilter
    >>> filt = IIRFilter(4)
    >>> show_frequency_response(filt, 48000)
    """
    # G6 Optimization: Call helper to get FFT result
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


def show_phase_response(filter_type: FilterType, samplerate: int) -> None:
    """
    Show phase response of a filter

    >>> from audio_filters.iir_filter import IIRFilter
    >>> filt = IIRFilter(4)
    >>> show_phase_response(filt, 48000)
    """
    # G6 Optimization: Call helper to get FFT result
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