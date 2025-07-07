import numpy as np
from typing import Dict, Union
from numpy.lib.stride_tricks import sliding_window_view

class SlidingWindowCalculator:
    """
    滑动窗口计算类，用于计算音频数组的统计特征
    """
    
    def __init__(self, window_size=10):
        """
        初始化滑动窗口计算器
        
        Args:
            window_size (int): 滑动窗口大小
        """
        if window_size <= 0:
            raise ValueError("窗口大小必须大于0")
        self.window_size = window_size
    
    def calculate(self, audio_array: np.ndarray) -> Dict[str, np.ndarray]:
        """
        对输入音频数组进行滑动窗口计算
        
        Args:
            audio_array (np.ndarray): 输入的1D音频数组
            
        Returns:
            Dict[str, np.ndarray]: 包含均值、最大值、最小值的字典
        """
        if audio_array.ndim != 1:
            raise ValueError("输入必须是1D数组")
        
        if len(audio_array) == 0:
            raise ValueError("输入数组不能为空")
        
        # 左侧零填充，填充长度为 window_size - 1
        padding_length = self.window_size - 1
        padded_array = np.pad(audio_array, (padding_length, 0), mode='constant', constant_values=0)
        
        # 初始化结果数组
        result_length = len(audio_array)
        means = np.zeros(result_length)
        maxs = np.zeros(result_length)
        mins = np.zeros(result_length)
        
        # 滑动窗口计算
        for i in range(result_length):
            window_start = i
            window_end = i + self.window_size
            window_data = padded_array[window_start:window_end]
            
            means[i] = np.mean(window_data)
            maxs[i] = np.max(window_data)
            mins[i] = np.min(window_data)
        
        return {
            'mean': means,
            'max': maxs,
            'min': mins
        }
    
    def calculate_vectorized(self, audio_array: np.ndarray) -> Dict[str, np.ndarray]:
        """
        使用向量化操作的高效实现版本
        
        Args:
            audio_array (np.ndarray): 输入的1D音频数组
            
        Returns:
            Dict[str, np.ndarray]: 包含均值、最大值、最小值的字典
        """
        if audio_array.ndim != 1:
            raise ValueError("输入必须是1D数组")
        
        if len(audio_array) == 0:
            raise ValueError("输入数组不能为空")
        
        # 左侧零填充
        padding_length = self.window_size - 1
        padded_array = np.pad(audio_array, (padding_length, 0), mode='constant', constant_values=0)
        
        # 使用sliding window view进行向量化计算
        
        
        windows = sliding_window_view(padded_array, window_shape=self.window_size)
        
        means = np.mean(windows, axis=1)
        maxs = np.max(windows, axis=1)
        mins = np.min(windows, axis=1)
        
        return {
            'mean': means,
            'max': maxs,
            'min': mins
        }


# 示例使用
if __name__ == "__main__":
    # 创建测试数据
    test_audio = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float32)
    
    # 创建计算器
    calculator = SlidingWindowCalculator(window_size=3)
    
    # 计算结果
    result = calculator.calculate_vectorized(test_audio)
    
    print("输入数组:", test_audio)
    print("窗口大小:", calculator.window_size)
    print("均值:", result['mean'])
    print("最大值:", result['max'])
    print("最小值:", result['min'])
    print("输出长度:", len(result['mean']))
