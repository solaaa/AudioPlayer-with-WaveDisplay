#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QIcon

# Add project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.ui.controllers.main_window_controller import MainWindowController
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are properly installed")
    sys.exit(1)


class MainApp:
    """application class.
    
    This class manages the main application lifecycle including initialization,
    dependency checking, and running the GUI application.
    """
    
    def __init__(self):
        """Initialize the application.
        
        Creates QApplication instance and sets up basic application properties.
        """
        # Create QApplication instance
        self.app = QApplication(sys.argv)
        
        # Setup application properties
        self._setup_application()
        
        # Initialize main window reference
        self.main_window = None
        
    def _setup_application(self):
        """Setup application properties and metadata.
        
        Configures application name, version, organization and other properties.
        """
        self.app.setApplicationName("Music Player Display")
        self.app.setApplicationDisplayName("Music Player Display")
        self.app.setApplicationVersion("0.0.1 Beta")
        self.app.setOrganizationName("Sola.")
        
        # Set application icon if available
        # icon_path = os.path.join(current_dir, "resources", "icons", "app_icon.ico")
        # if os.path.exists(icon_path):
        #     self.app.setWindowIcon(QIcon(icon_path))
        
        # Apply application styling
        self._set_application_style()
    
    def _set_application_style(self):
        """Set application style and theme.
        
        Configure the visual appearance of the application.
        """
        pass
    
    def _check_dependencies(self):
        """Check for required dependencies.
        
        Returns:
            bool: True if all dependencies are available, False otherwise.
        """
        try:
            import pyqtgraph
            import numpy
            import audioread
            return True
        except ImportError as e:
            QMessageBox.critical(
                None,
                "Dependency Check Failed",
                f"Missing required libraries:\n{e}\n\n"
            )
            return False
    
    def run(self):
        """Run the application.
        
        Returns:
            int: Application exit code (0 for success, 1 for error).
        """
        try:
            # Check dependencies
            if not self._check_dependencies():
                return 1
            
            # Create main window
            self.main_window = MainWindowController()
            
            # Show main window
            self.main_window.show()
            
            # Show startup message
            self.main_window.status_bar.showMessage("Started", 3000)
            
            # Run event loop
            return self.app.exec()
            
        except Exception as e:
            # Handle unhandled exceptions
            error_msg = f"An error occurred while running the program:\n{str(e)}"
            print(error_msg)
            
            if hasattr(self, 'app'):
                QMessageBox.critical(
                    None,
                    "Program Error",
                    error_msg
                )
            
            return 1
    
    def quit(self):
        """Quit the application gracefully."""
        if self.app:
            self.app.quit()


def main():
    """Main entry point of the application.
    
    Sets up high DPI support and runs the application.
    """
    # Enable high DPI support
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and run application
    app = MainApp()
    exit_code = app.run()
    
    # Exit program
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
