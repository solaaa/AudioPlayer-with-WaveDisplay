import numpy as np

def downsample_plot_data(x, y, method, step):
    """Downsample plot data for efficient visualization.
    
    Args:
        x (np.ndarray): X-axis data array.
        y (np.ndarray): Y-axis data array.
        method (str): Downsampling method ('bypass' or 'abs_max').
        step (int): Downsampling step size.
        
    Returns:
        tuple: Tuple of (x_downsampled, y_downsampled) - Downsampled data arrays.
    """
    if step == 1:
        return x, y
    
    if method == 'bypass':
        return x[::step], y[::step]
    elif method == 'abs_max':
        # Use vectorized operations to calculate absolute maximum in each step interval
        n_samples = len(x) // step * step  # Ensure divisible by step
        x_reshaped = x[:n_samples].reshape(-1, step)
        y_reshaped = y[:n_samples].reshape(-1, step)
        
        x_downsampled = x_reshaped[:, 0]  # Take first x value in each interval
        y_downsampled_idx = np.argmax(np.abs(y_reshaped), axis=1)  # Find absolute max index in each interval
        y_downsampled = y_reshaped[np.arange(len(y_downsampled_idx)), y_downsampled_idx]
       
        
        # Handle remaining incomplete interval
        if n_samples < len(x):
            x_downsampled = np.append(x_downsampled, x[n_samples])
            y_last_idx = np.argmax(np.abs(y[n_samples:]))
            y_downsampled = np.append(y_downsampled, y[n_samples:][y_last_idx])

        return x_downsampled, y_downsampled