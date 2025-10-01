from __future__ import annotations

from abc import abstractmethod
from math import pi
from typing import Protocol

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal  # G9: 引入scipy.signal以用单个调用替换多个调用

# G9: 为了使用lfilter，我们需要访问系数，因此直接依赖IIRFilter类
from audio_filters.iir_filter import IIRFilter


class FilterType(Protocol):
    @abstractmethod
    def process(self, sample: float) -> float:
        """
        Calculate y[n]

        >>> issubclass(FilterType, Protocol)
        True
        """


def show_frequency_response(filter_type: IIRFilter, samplerate: int) -> None:
    """
    Show frequency response of a filter

    >>> from audio_filters.iir_filter import IIRFilter
    >>> filt = IIRFilter(4)
    >>> show_frequency_response(filt, 48000)
    """

    size = 512
    # G9: 使用批量操作将512次process()调用减少为1次lfilter()调用
    inputs = np.zeros(size)
    inputs[0] = 1.0
    outputs = scipy.signal.lfilter(filter_type.b_coeffs, filter_type.a_coeffs, inputs)

    filler = np.zeros(samplerate - size)  # zero-padding
    full_output = np.concatenate((outputs, filler))
    fft_out = np.abs(np.fft.fft(full_output))
    fft_db = 20 * np.log10(fft_out)

    # Frequencies on log scale from 24 to nyquist frequency
    plt.xlim(24, samplerate / 2 - 1)
    plt.xlabel("Frequency (Hz)")
    plt.xscale("log")

    # G9: 内联 get_bounds() 函数以消除一次函数调用
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

    size = 512
    # G9: 使用批量操作将512次process()调用减少为1次lfilter()调用
    inputs = np.zeros(size)
    inputs[0] = 1.0
    outputs = scipy.signal.lfilter(filter_type.b_coeffs, filter_type.a_coeffs, inputs)

    filler = np.zeros(samplerate - size)  # zero-padding
    full_output = np.concatenate((outputs, filler))
    fft_out = np.angle(np.fft.fft(full_output))

    # Frequencies on log scale from 24 to nyquist frequency
    plt.xlim(24, samplerate / 2 - 1)
    plt.xlabel("Frequency (Hz)")
    plt.xscale("log")

    plt.ylim(-2 * pi, 2 * pi)
    plt.ylabel("Phase shift (Radians)")
    plt.plot(np.unwrap(fft_out, -2 * pi))
    plt.show()