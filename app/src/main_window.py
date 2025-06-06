import os
from PySide6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QFileDialog
from PySide6.QtGui import QKeySequence, QShortcut
from .data import Data
from .plot_main import Plot, ClickedPoint
from .config.config import configApp
from .widget.menu_actions import connectMenuBarActions
from .widget.toolbar_actions import conncetToolbar
from .widget.docks_actions import connectDockSignals
from app.src.widget.load_ui import loadUiFiles
from app.src.widget.load_ui import setWidgets
from app.src.widget.widget_setting_actions import connectSettingWidgetSignals
from app.src.widget.widget_pointlist_actions import connectPointsListWidgetSignals
from app.src.widget.widget_setting_tab_network import connectNetworkType
from app.src.widget.shortcuts import connectShortcuts
from app.src.widget import set_canvas
from app.src.widget.check_existing_data import checkExistingData


class MainWindow(QMainWindow):
    """
    Main application window for SARPlotter.

    This class represents the main window of the SARPlotter application. It inherits
    from the PySide6 QMainWindow class and includes the necessary components for the
    application's user interface.

    Attributes:
        ui (QMainWindow): The main user interface window.
        setting_widget (QWidget): The setting widget displayed in ui.dock_widget_setting.
        points_widget (QWidget): The point list widget displayed in ui.dock_widget_point_list.

    """

    def __init__(self):
        super().__init__()
        # Load UI files and set widgets for setting and points in the corresponding dock widgets
        loadUiFiles(self)
        setWidgets(self)
        # create instances for data and plot
        self.data = Data(data_path=os.getcwd())
        self.plot = Plot(data=self.data)
        self.plot.list_widget_clicked_points = self.points_widget.list_widget_clicked_points
        self.plot.status_bar = self.ui.statusBar()
        self.plot.combo_box_amplitude_dates = self.setting_widget.tab_map_combo_box_amplitude_dates

        set_canvas.setup(self)
        connectSettingWidgetSignals(self)
        connectPointsListWidgetSignals(self)
        connectDockSignals(self)
        self.menubar = connectMenuBarActions(self)
        conncetToolbar(self)
        configApp(self)

        connectShortcuts(self)
        checkExistingData(self)
        connectNetworkType(self)

        self._connectMapBackground()

    def show(self):
        """
        Show the main window.
        """
        self.ui.show()

    def _connectMapBackground(self):
        self.plot.plotBackground()
        self.plot.setupAmplitudeList()
