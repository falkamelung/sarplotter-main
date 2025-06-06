# main.py

"""
SARPlotter Main Module

This module is the entry point for the SARPlotter application.

Author: Mahmud Haghighi
Date: January 11, 2024
"""

import sys
import logging
# import matplotlib
# try:
#     matplotlib.use('TkAgg')
# except ImportError as e:
#     print(e)
from src.main_window import MainWindow

logging.basicConfig(level=logging.INFO)

try:
    from PySide6.QtWidgets import QApplication, QMainWindow
except ImportError:
    print("PySide6 is not installed.")
    print("Please install PySide6 using mamba:")
    print("   mamba install -c conda-forge pyside6")
    print("or using conda:")
    print("   conda install -c conda-forge pyside6")
    print("or using pip:")
    print("   pip install PySide6")
    sys.exit(1)


def main():
    """
    The main function for running the application

    Before running, ensure your terminal is in the processing directory (e.g., 'sbas').

    Usage:
        - Navigate to the SARvey processing directory in your terminal (e.g. sbas)
        - Run this script to start SARPlotter application

    Example:
        $ cd path/to/sarvey/processing/directory/sbas
        $ python main.py

    Note:
        None

    Returns:
        None
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
