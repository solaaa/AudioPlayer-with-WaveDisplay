# -*- coding: utf-8 -*-

import os
import numpy as np
import audioread
from typing import Tuple, Optional


class AudioFileReader:
    """Audio file reader utility class."""

    SUPPORTED_FORMATS = ['.wav', '.mp3']

    def __init__(self):
        self.file_path = None
        self.sample_rate = None
        self.channels = None
        self.audio_data = None
        self.duration = None

    @classmethod
    def is_supported_format(cls, file_path: str) -> bool:
        """Check if file format is supported.

        Args:
            file_path: Path to the audio file.

        Returns:
            True if format is supported, False otherwise.
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in cls.SUPPORTED_FORMATS

    def load_audio_file(self, file_path: str) -> bool:
        """Load audio file.

        Args:
            file_path: Path to the audio file.

        Returns:
            True if successfully loaded, False otherwise.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if not self.is_supported_format(file_path):
                raise ValueError(f"Unsupported file format: {file_path}")

            # Use audioread to read audio file
            with audioread.audio_open(file_path) as audio_file:
                self.sample_rate = audio_file.samplerate
                self.channels = audio_file.channels
                self.duration = audio_file.duration

                # Read audio data
                raw_audio = b''.join(audio_file)

                # Convert to numpy array
                # audioread returns 16-bit PCM data
                audio_array = np.frombuffer(raw_audio, dtype=np.int16)

                # Reshape array if multi-channel
                if self.channels > 1:
                    audio_array = audio_array.reshape(-1, self.channels)
                    # Transpose so each channel is a row
                    audio_array = audio_array.T
                else:
                    audio_array = audio_array.reshape(1, -1)

                # Convert to float and normalize to [-1, 1]
                self.audio_data = audio_array.astype(np.float32) / 32768.0

                self.file_path = file_path

                print(f"Audio file loaded successfully:")
                print(f"  File path: {file_path}")
                print(f"  Sample rate: {self.sample_rate} Hz")
                print(f"  Channels: {self.channels}")
                print(f"  Duration: {self.duration:.2f} seconds")
                print(f"  Data shape: {self.audio_data.shape}")

                return True

        except Exception as e:
            print(f"Failed to load audio file: {e}")
            self.clear()
            return False

    def get_channel_data(self, channel: int = 0) -> Optional[np.ndarray]:
        """Get audio data for specified channel.

        Args:
            channel: Channel index (starting from 0).

        Returns:
            Audio data array, or None if failed.
        """
        if self.audio_data is None:
            return None

        if channel >= self.channels:
            print(f"Warning: Channel index {channel} out of range, max channels: {self.channels}")
            return None

        return self.audio_data[channel]

    def get_time_axis(self) -> Optional[np.ndarray]:
        """Get time axis array.

        Returns:
            Time axis array in seconds, or None if failed.
        """
        if self.audio_data is None or self.sample_rate is None:
            return None

        samples = self.audio_data.shape[1]
        return np.linspace(0, samples / self.sample_rate, samples)

    def get_audio_info(self) -> dict:
        """Get audio file information.

        Returns:
            Dictionary containing audio information.
        """
        return {
            'file_path': self.file_path,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'duration': self.duration,
            'samples': self.audio_data.shape[1] if self.audio_data is not None else 0,
            'is_loaded': self.audio_data is not None
        }

    def clear(self):
        """Clear currently loaded audio data."""
        self.file_path = None
        self.sample_rate = None
        self.channels = None
        self.audio_data = None
        self.duration = None

    def is_loaded(self) -> bool:
        """Check if audio file is loaded."""
        return self.audio_data is not None


# Convenience functions
def load_audio_file(file_path: str) -> Tuple[Optional[np.ndarray], Optional[dict]]:
    """Convenience function: load audio file and return data and info.

    Args:
        file_path: Path to the audio file.

    Returns:
        Tuple of (audio_data, info): Audio data and info dictionary.
    """
    reader = AudioFileReader()
    if reader.load_audio_file(file_path):
        return reader.audio_data, reader.get_audio_info()
    return None, None
