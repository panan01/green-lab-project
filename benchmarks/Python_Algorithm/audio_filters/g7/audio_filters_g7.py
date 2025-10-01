import sys
import os
import argparse
import numpy as np
from pathlib import Path
import scipy.signal # G7: 引入 scipy.signal 用于lfilter
from scipy.io.wavfile import write as write_wav


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))
from butterworth_filter import make_lowpass, make_lowshelf, make_highshelf


SAMPLERATE = 48000
DURATION = 4
AMPLITUDE = 0.4
FADE_DURATION = 0.01

def generate_test_signal() -> np.ndarray:
    t = np.linspace(0., DURATION, int(SAMPLERATE * DURATION), endpoint=False)
    
    low_freq = np.sin(2 * np.pi * 200 * t)
    mid_freq = np.sin(2 * np.pi * 1500 * t)
    high_freq = np.sin(2 * np.pi * 7000 * t)
    
    signal = AMPLITUDE * (low_freq + mid_freq + high_freq) / 3

    fade_samples = int(SAMPLERATE * FADE_DURATION)
    fade_in = np.linspace(0., 1., fade_samples)
    fade_out = np.linspace(1., 0., fade_samples)
    signal[:fade_samples] *= fade_in
    signal[-fade_samples:] *= fade_out
    
    return signal

def save_wav(filename: str, signal: np.ndarray):
    # 归一化以防止削波
    max_abs_val = np.max(np.abs(signal))
    if max_abs_val > 0:
        normalized_signal = signal / max_abs_val
    else:
        normalized_signal = signal # 避免除以零
    int16_signal = np.int16(normalized_signal * 32767)
    write_wav(filename, SAMPLERATE, int16_signal)
    print(f"Successfully saved audio to: {filename}")

def main(preset: str) -> None:
    print(f"Selected preset: '{preset}'")
    
    input_signal = generate_test_signal()
    save_wav("input_original.wav", input_signal)

    filters = []
    output_filename = ""
    if preset == "small":
        print("Applying 'small' preset: A single 800Hz low-pass filter.")
        filters.append(make_lowpass(frequency=800, samplerate=SAMPLERATE))
        output_filename = "output_small_preset.wav"
    elif preset == "large":
        print("Applying 'large' preset: An EQ combo to boost bass and cut treble.")
        low_shelf = make_lowshelf(frequency=250, samplerate=SAMPLERATE, gain_db=6.0)
        high_shelf = make_highshelf(frequency=4000, samplerate=SAMPLERATE, gain_db=-8.0)
        filters.extend([low_shelf, high_shelf])
        output_filename = "output_large_preset.wav"

    print("Processing audio...")
    
    # G7 Optimization: Replace the slow sample-by-sample loop with fast, vectorized processing.
    processed_signal = input_signal.copy()
    for filt in filters:
        # 对整个信号数组应用每个滤波器
        processed_signal = scipy.signal.lfilter(
            filt.b_coeffs, filt.a_coeffs, processed_signal
        )
    output_signal = processed_signal
    
    save_wav(output_filename, output_signal)
    print(f"\nProcessing complete. You can now listen to and compare 'input_original.wav' and '{output_filename}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="An audio processing application using a custom IIR filter library.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--size",
        choices=["small", "large"],
        required=True,
        help=(
            "Select a filter preset:\n"
            "'small': Applies a simple low-pass filter to remove high frequencies.\n"
            "'large':   Applies an EQ combo to boost bass and cut treble."
        )
    )
    
    args = parser.parse_args()
    main(args.size)