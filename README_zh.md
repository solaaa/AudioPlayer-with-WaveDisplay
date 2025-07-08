# 🎵 音频播放器 - 实时波形显示

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md)
[![中文](https://img.shields.io/badge/lang-中文-red.svg)](README_zh.md)


> 一个轻量级的音频播放器，支持实时显示音频波形和自定义信号处理功能

## ✨ 项目特性

- **轻量化设计** - 基于Python和PySide6构建，资源占用少
- **实时波形显示** - 播放音频的同时实时显示时域波形
- **可扩展算法** - 支持自定义信号处理算法进行显示分析，例如：
    - 频域波形分析
    - 时域信号包络检测
    - 实时滤波处理
    - 其他自定义音频分析功能
- **多格式支持** - 支持多种音频格式（通过ffmpeg）
- **现代化界面** - 基于Qt的美观用户界面
- **AI辅助开发** - 这是一个AI编程实验项目，80%的代码由AI完成。开发者仅提出需求和实现步骤，必要时进行干预。这是一次有趣的实验，展示了当前AI辅助编程能够达到的水平。

## 🛠️ 环境要求

### Python版本
- Python 3.10+

### 核心依赖

| 库名称 | 版本要求 | 用途 |
|--------|----------|------|
| [PySide6](https://pypi.org/project/PySide6/) | 6.7.2 | GUI框架 |
| [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph) | 最新版 | 实时绘图引擎 |
| [audioread](https://github.com/beetbox/audioread) | 最新版 | 音频文件解码 |

> ⚠️ **注意**: PySide6 6.9.1版本存在兼容性问题，建议使用6.7.2版本

### 外部工具依赖

**FFmpeg** - 音频编解码支持
- 下载地址：[FFmpeg官网](https://ffmpeg.org/download.html#build-windows)
- 安装后需将ffmpeg添加到系统PATH环境变量

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/solaaa/AudioPlayer-with-WaveDisplay.git
cd AudioPlayer-with-WaveDisplay
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行程序
```bash
python main.py
```

## 📖 使用指南

1. **自定义算法**
    
    GUI界面显示两个子图：第一个为时域波形图，第二个子图显示 `src\core\algorithm_test\sliding_window_calculator.py` 中定义的算法示例。该算法类在 `src\ui\widgets\display_panel.py` 的 `DisplayPanel.setup_algo()` 函数中被调用。

2. **显示性能优化**
    
    由于pyqtgraph绘图库不支持自动降采样，而音频文件的波形数据量通常很大（例如44.1kHz采样率的1分钟音频文件包含超过200万个采样点），直接绘制会导致界面卡顿。用户进行拖拽或缩放操作时会触发重绘，进一步加剧卡顿问题。本项目采用以下两种优化策略：
    
    - **分段降采样**：在 `src\utils\downsample.py` 中实现降采样算法，通过 `DisplayPanel.MAX_DISPLAY_LEN_1D` 设置最大显示点数，使用分段降采样将数据长度限制在合理范围内
    - **视口优化**：仅显示当前视口范围内的波形数据，当用户缩放时只渲染可见区域的波形

3. **UI功能扩展**
    
    软件运行时，GUI中包含一个未完成的"参数设置"页面，可作为功能扩展接口。如不需要此功能，可在代码中删除相关部分。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

⭐ 如果这个项目对您有帮助，请给个星标支持！




