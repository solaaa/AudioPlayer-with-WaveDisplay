import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QWheelEvent, QFont
from PySide6.QtWidgets import QApplication
import numpy as np
import sys


class CustomPlotWidget(pg.PlotWidget):
    """Custom plot widget with x-axis at bottom, y-axis at right, no labels, grid enabled, 
    mouse wheel controls x-axis zoom only.
    
    Features:
    - X-axis displayed at bottom, Y-axis at right
    - Grid enabled for better visualization
    - Smart mouse wheel zoom based on cursor position
    - Timeline drawing capability
    """
    
    def __init__(self, parent=None):
        """Initialize the CustomPlotWidget.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._setup_axes()
        self._setup_grid()
        self._setup_mouse_behavior()
        self.timeline_item = None  # Store reference to timeline item
    
    
    def _setup_axes(self):
        """Configure axis positions and labels."""
        # Get plot item
        plot_item = self.getPlotItem()
        
        # Hide default left and bottom axes
        plot_item.hideAxis('left')
        plot_item.hideAxis('bottom')
        
        # Show right and bottom axes
        plot_item.showAxis('right')
        plot_item.showAxis('bottom')
        
        # Hide axis labels
        plot_item.getAxis('right').setLabel('')
        plot_item.getAxis('bottom').setLabel('')
        
        # Set axis style, remove label text
        plot_item.getAxis('right').setStyle(showValues=True)
        plot_item.getAxis('bottom').setStyle(showValues=True)

        # Set X-axis display limit values
        self.x_lim = [0, 10]


    
    
    def set_xlim(self, x_min, x_max):
        """Set x-axis limits.
        
        Args:
            x_min (float): Minimum x value.
            x_max (float): Maximum x value.
        """
        self.x_lim = [x_min, x_max]

    def set_axis_font_size(self, size):
        """Set axis font size independently.
        
        Args:
            size (int): Font size for axis labels.
        """
        plot_item = self.getPlotItem()
        
        axis_font = QFont()
        axis_font.setPointSize(size)
        axis_font.setFamily("consolas")
        
        plot_item.getAxis('right').setStyle(tickFont=axis_font)
        plot_item.getAxis('bottom').setStyle(tickFont=axis_font)
        print("set_axis_font_size")

    def _setup_grid(self):
        """Enable grid display."""
        plot_item = self.getPlotItem()
        plot_item.showGrid(x=True, y=True, alpha=0.3)
    
    def _setup_mouse_behavior(self):
        """Setup mouse interaction behavior."""
        # Disable default mouse interaction
        self.setMouseEnabled(x=True, y=True)
        
        # Get view box and configure mouse mode
        view_box = self.getPlotItem().getViewBox()
        view_box.setMouseEnabled(x=True, y=True)
    
    def wheelEvent(self, event: QWheelEvent):
        """Override wheel event for intelligent zoom based on mouse position.
        
        - Mouse on right y-axis area: zoom y-axis
        - Mouse on left side of y-axis: zoom x-axis
        
        Args:
            event (QWheelEvent): Mouse wheel event.
        """
        
        # Get view box and plot item
        view_box = self.getPlotItem().getViewBox()
        plot_item = self.getPlotItem()
        
        # Get mouse position in widget
        mouse_pos = event.position()  # PySide6 uses position() instead of pos()
        mouse_x = mouse_pos.x()
        
        # Get right y-axis pixel position
        right_axis = plot_item.getAxis('right')
        axis_rect = right_axis.geometry()
        y_axis_x = axis_rect.left()  # Left edge position of y-axis
        
        # Calculate scale factor
        delta = -event.angleDelta().y()
        scale_factor = 1.1 if delta > 0 else 1.0 / 1.1

        # Get mouse pointer's current axis coordinates
        scene_pos = self.mapToScene(mouse_pos.toPoint())
        axis_pos = view_box.mapSceneToView(scene_pos)
        mouse_axis_x = axis_pos.x()
        mouse_axis_y = axis_pos.y()
        
        # Decide zoom direction based on mouse position
        if mouse_x >= y_axis_x:
            # Mouse in y-axis area or right side, zoom y-axis
            view_box.scaleBy(x=1.0, y=scale_factor, center=mouse_axis_y)
        else:
            # Mouse on left side of y-axis (plot area), zoom x-axis
            view_box.scaleBy(x=scale_factor, y=1.0, center=mouse_axis_x)
        
        event.accept()
    
    def draw_timeline(self, t, color='r', width=1):
        """Draw vertical timeline at specified x-axis position.
        
        Args:
            t (float): X-axis position for timeline.
            color (str, optional): Line color. Defaults to 'r' (red).
            width (int, optional): Line width. Defaults to 1.
        """
        # Remove existing timeline if present
        if self.timeline_item is not None:
            self.removeItem(self.timeline_item)
        
        # Create vertical line
        self.timeline_item = pg.InfiniteLine(
            pos=t, 
            angle=90,  # Vertical line
            pen=pg.mkPen(color=color, width=width)
        )
        
        # Add to plot
        self.addItem(self.timeline_item)
    

    def _add_space_y_axis(self, space=24):
        """Add space to the right y-axis.
        
        Args:
            space (float): Space to add to the right y-axis.
        """
        right_axis = self.getPlotItem().getAxis('right')

        # Get current width
        current_width = right_axis.width()
        
        # Calculate required width with "space" pixel buffer
        new_width = current_width + space
        
        # Set the new width
        right_axis.setWidth(new_width)

    def paintEvent(self, event):
        """Override paintEvent to call _add_space_y_axis during redraws.
        
        Args:
            event: Paint event.
        """
        # Call parent's paintEvent first
        super().paintEvent(event)
        
        # Use fixed width to show y-axis
        if hasattr(self, 'flag_redraw_y_axis') == False:
            self.flag_redraw_y_axis = 1
            self._add_space_y_axis() 

    def plot2d(self, x_axis, y_axis, data2d):
        img = pg.ImageItem()
        self.addItem(img)
        img.setImage(data2d)
        x_min, x_max = x_axis.min(), x_axis.max()
        y_min, y_max = y_axis.min(), y_axis.max()

        img.setRect(pg.QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min))
        # set colormap
        img.setColorMap(pg.colormap.get('inferno'))
        img.setLevels([-120, 0])

if __name__ == '__main__':
    from PySide6.QtCore import QTimer
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create custom plot widget
    widget = CustomPlotWidget()
    widget.setWindowTitle('Custom Plot Widget Demo')
    widget.resize(800, 600)
    
    # Generate sample data (simulating audio waveform)
    t = np.linspace(0, 1000, 100000)
    y1 = np.sin(2 * np.pi * t) * np.exp(-t/5)
    y2 = 0.5 * np.cos(4 * np.pi * t) * np.exp(-t/8)
    
    # Add data curves
    widget.plot(t, y1, pen='r', name='Signal 1')
    widget.plot(t, y2, pen='b', name='Signal 2')
    
    # Timeline animation parameters
    current_time = 0.0
    time_step = 0.02
    max_time = 1000.0
    
    def update_timeline():
        """Update timeline position."""
        global current_time
        widget.draw_timeline(current_time, color='g', width=2)
        current_time += time_step
        if current_time > max_time:
            current_time = 0.0  # Restart
    
    # Create timer for timeline animation
    timer = QTimer()
    timer.timeout.connect(update_timeline)
    timer.start(20)  # Update every 20ms
    
    # Show widget
    widget.show()
    
    # Run application
    sys.exit(app.exec())
