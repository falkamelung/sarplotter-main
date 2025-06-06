
from PySide6.QtGui import QKeySequence, QAction
from app.src.widget.widget_setting_tab_network import showNetworkWidget
from app.src.widget.widget_setting_tab_ts import showTimeSeriesWidget
from app.src.widget.widget_setting_tab_tempuw import showTemporalUnwrapWidget
from app.src.widget import screenshot

def connectMenuBarActions(main_window):
    menubar = main_window.ui.menuBar()
    file_menu = menubar.addMenu("File")
    window_menu = menubar.addMenu("Window")

    save_window_action = QAction("Save Snapshot", main_window)
    save_window_action.setShortcut(QKeySequence("Ctrl+S"))
    save_window_action.triggered.connect(
        lambda: screenshot.screenShot(main_window))
    file_menu.addAction(save_window_action)

    save_pretty_window_action = QAction("Save Pretty Snapshot", main_window)
    save_pretty_window_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
    save_pretty_window_action.triggered.connect(
        lambda: screenshot.screenShotPretty(main_window))
    file_menu.addAction(save_pretty_window_action)

    setting_doc_action = QAction("Main Settings", main_window)
    setting_doc_action.setCheckable(True)
    setting_doc_action.setShortcut(QKeySequence("Ctrl+T"))
    setting_doc_action.triggered.connect(_showSettingWidget)
    window_menu.addAction(setting_doc_action)

    point_list_action = QAction("Point List", main_window)
    point_list_action.setCheckable(True)
    point_list_action.setShortcut(QKeySequence("Ctrl+0"))
    point_list_action.triggered.connect(_showPointListWidget)
    window_menu.addAction(point_list_action)

    timeseries_action = QAction("Time series", main_window)
    timeseries_action.setCheckable(True)
    timeseries_action.setShortcut(QKeySequence("Ctrl+1"))
    timeseries_action.triggered.connect(lambda status: showTimeSeriesWidget(main_window, status))
    window_menu.addAction(timeseries_action)

    temporal_uw_action = QAction("Temporal Unwrap", main_window)
    temporal_uw_action.setCheckable(True)
    temporal_uw_action.setShortcut(QKeySequence("Ctrl+2"))
    temporal_uw_action.triggered.connect(lambda status: showTemporalUnwrapWidget(main_window, status))
    window_menu.addAction(temporal_uw_action)

    network_action = QAction("Network", main_window)
    network_action.setCheckable(True)
    network_action.setShortcut(QKeySequence("Ctrl+3"))
    network_action.triggered.connect(lambda status: showNetworkWidget(main_window, status))
    window_menu.addAction(network_action)

    return menubar


def _getMenuAction(main_window, menu_name, action_name):
    """get a reference to submenu"""
    action = None
    menu = next((item for item in main_window.menubar.actions() if item.text().lower() == menu_name.lower()), None)
    if menu:
        action = next((sub_item for sub_item in menu.menu().actions()
                       if sub_item.text().lower() == action_name.lower()), None)
    return action


def checkMenuAction(main_window, menu_name, action_name, status):
    action = _getMenuAction(main_window, menu_name, action_name)
    if action is not None:
        action.setChecked(status)


def _showSettingWidget(main_window):
    main_window._toggleDock(main_window.ui.dock_widget_setting)


def _showPointListWidget(main_window):
    main_window._toggleDock(main_window.ui.dock_widget_point_list)


def _toggleDock(dock):
    if dock.isVisible():
        dock.close()
    else:
        dock.show()
