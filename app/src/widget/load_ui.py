
import os
from PySide6.QtUiTools import QUiLoader
from app.src.ui.resources import icons_rc


def loadUiFiles(main_window):
    """
    Load the user interface files.

    This method loads the main window, setting widget, and point list widget from
    their respective ui files.

    """
    # construct widgets
    main_window.ui = None
    main_window.setting_widget = None
    main_window.points_widget = None
    main_window.plot_tu_widget = None

    loader = QUiLoader()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_window.ui = loader.load(os.path.join(script_dir, "../ui/main_window.ui"))
    main_window.setting_widget = loader.load(os.path.join(script_dir, "../ui/widget_setting.ui"))
    main_window.ui.dock_widget_setting.setWidget(main_window.setting_widget)
    main_window.points_widget = loader.load(os.path.join(script_dir, "../ui/widget_point_list.ui"))
    main_window.plot_tu_widget = loader.load(os.path.join(script_dir, "../ui/widget_plot_temporal_uw.ui"))


def setWidgets(main_window):
    """
    Set the widgets in the main window.

    This method sets the setting widget, point list widget, and temporal unwrap plot widget
    in the main window.

    """
    main_window.ui.dock_widget_setting.setWidget(main_window.setting_widget)
    main_window.ui.dock_widget_point_list.setWidget(main_window.points_widget)
    main_window.ui.dock_widget_temporal_uw.setWidget(main_window.plot_tu_widget)

    # close docks
    main_window.ui.dock_widget_temporal_uw.close()
    main_window.ui.dock_widget_timeseries.close()
    main_window.ui.dock_widget_network.close()

