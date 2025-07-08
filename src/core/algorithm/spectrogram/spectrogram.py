import numpy as np
from scipy.signal import stft

class Spectrogram:
    """
    A class to calculate the spectrogram of a time-domain signal using STFT.
    """

    def __init__(self, fft_points=1024):
        """
        Initializes the Spectrogram processor.

        Args:
            fft_points (int): The number of FFT points to use. Defaults to 1024.
        """
        if fft_points <= 0 or (fft_points & (fft_points - 1)) != 0:
            raise ValueError("fft_points must be a positive power of 2.")
        self.fft_points = fft_points
        self.window = 'hann'  # Default window

    def calculate(self, signal, fs, overlap_percent=50):
        """
        Calculates the spectrogram for a given time-domain signal.

        Args:
            signal (np.ndarray): The input time-domain signal (1D array).
            fs (int): The sampling frequency of the signal.
            overlap_percent (int): The desired overlap between segments, in percent.
                                   Valid values are 0, 25, 50, 75. Defaults to 50.

        Returns:
            dict: A dictionary containing the spectrogram results, including:
                  'frequencies': The array of sample frequencies (Hz).
                  't': The array of segment times (seconds).
                  'spectrogram': The complex-valued spectrogram (Zxx).
                  'spectrogram_db': The spectrogram in dBFS.
        """
        if overlap_percent not in [0, 25, 50, 75]:
            raise ValueError("overlap_percent must be one of 0, 25, 50, or 75.")

        nperseg = self.fft_points
        noverlap = int(nperseg * (overlap_percent / 100.0))

        f, t, zxx = stft(
            signal,
            fs=fs,
            window=self.window,
            nperseg=nperseg,
            noverlap=noverlap,
            nfft=self.fft_points,
            return_onesided=True
        )
        
        zxx = np.abs(zxx)
        # 使用业界标准的dB计算方法
        # 对于归一化音频[-1,1]，使用更合适的参考值和epsilon
        epsilon = 1e-12  # 更小的epsilon值
        spectrogram_db = 20 * np.log10(zxx + epsilon)
        
        # 可选：限制动态范围到合理区间（如-120dB到0dB）
        spectrogram_db = np.clip(spectrogram_db, -150, 0)

        return {
            'frequencies': f,
            't': t,
            'spectrogram': zxx,
            'spectrogram_db': spectrogram_db
        }

if __name__ == '__main__':
    # --- Example Usage ---
    fs = 44100
    duration = 2
    t_sig = np.linspace(0, duration, int(fs * duration), endpoint=False)
    test_signal = np.sin(2 * np.pi * 1000 * t_sig) + 0.5 * np.sin(2 * np.pi * 5000 * t_sig)

    # 1. Initialize the processor
    spec_processor = Spectrogram(fft_points=1024)

    # 2. Calculate the spectrogram
    spectrogram_data = spec_processor.calculate(test_signal, fs, overlap_percent=50)

    # 3. Print information
    print("--- Spectrogram Calculation Example ---")
    print(f"Frequencies shape: {spectrogram_data['frequencies'].shape}")
    print(f"Time segments shape: {spectrogram_data['t'].shape}")
    print(f"Spectrogram (dB) shape: {spectrogram_data['spectrogram_db'].shape}")
    print(f"Frequency axis ranges from {spectrogram_data['frequencies'][0]:.2f} Hz to {spectrogram_data['frequencies'][-1]:.2f} Hz.")