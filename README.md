# 🎵 Audio Player - Real-time Waveform Display

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![中文](https://img.shields.io/badge/lang-中文-red.svg)](README_zh.md)

> A lightweight audio player that supports real-time audio waveform display and custom signal processing functions

## ✨ Project Features

- **Lightweight Design** - Built on Python and PySide6 with minimal resource consumption
- **Real-time Waveform Display** - Display time-domain waveforms in real-time while playing audio
- **Extensible Algorithms** - Support custom signal processing algorithms for display analysis, such as:
    - Frequency domain waveform analysis
    - Time-domain signal envelope detection
    - Real-time filtering processing
    - Other custom audio analysis functions
- **Multi-format Support** - Support multiple audio formats (via ffmpeg)
- **Modern Interface** - Beautiful user interface based on Qt
- **AI-Assisted Development** - This is an AI programming experimental project where 80% of the code was completed by AI. The developer only provided requirements and implementation steps, intervening only when necessary. This is an interesting experiment that demonstrates the current capabilities of AI-assisted programming.

## 🛠️ Environment Requirements

### Python Version
- Python 3.10+

### Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| [PySide6](https://pypi.org/project/PySide6/) | 6.7.2 | GUI Framework |
| [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph) | Latest | Real-time Plotting Engine |
| [audioread](https://github.com/beetbox/audioread) | Latest | Audio File Decoding |

> ⚠️ **Note**: PySide6 version 6.9.1 has compatibility issues, version 6.7.2 is recommended

### External Tool Dependencies

**FFmpeg** - Audio codec support
- Download: [FFmpeg Official Website](https://ffmpeg.org/download.html#build-windows)
- After installation, add ffmpeg to system PATH environment variable

## 🚀 Quick Start

### 1. Clone the Project
```bash
git clone <repository-url>
cd MusicPlayer-With-WaveDisplay
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Program
```bash
python main.py
```

## 📖 Usage Guide

1. **Custom Algorithms**
    
    The GUI displays two subplots: the first shows the time-domain waveform, and the second displays the algorithm example defined in `src\core\algorithm_test\sliding_window_calculator.py`. This algorithm class is used in the `DisplayPanel.setup_algo()` function in `src\ui\widgets\display_panel.py`.

2. **Display Performance Optimization**
    
    Since the pyqtgraph plotting library doesn't support automatic downsampling, and audio file waveforms typically contain large amounts of data (e.g., a 1-minute audio file at 44.1kHz sampling rate contains over 2 million sample points), direct plotting can cause interface lag. User operations like dragging or zooming trigger redraws, further exacerbating the lag issue. This project employs two optimization strategies:
    
    - **Segmented Downsampling**: Implements downsampling algorithms in `src\utils\downsample.py`, sets maximum display points through `DisplayPanel.MAX_DISPLAY_LEN_1D`, and uses segmented downsampling to limit data length to a reasonable range
    - **Viewport Optimization**: Only displays waveform data within the current viewport range, rendering only the visible area when users zoom

3. **UI Feature Extension**
    
    When running the software, the GUI includes an incomplete "Parameter Settings" page that can serve as a feature extension interface. If this functionality is not needed, the relevant parts can be removed from the code.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

---

⭐ If this project helps you, please give it a star!
