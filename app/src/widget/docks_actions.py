
from .menu_actions import checkMenuAction

def connectDockSignals(main_window):
    """connect dock signals"""
    main_window.ui.dock_widget_timeseries.visibilityChanged.connect(
        lambda status: _dockWidgetTimeseriesVisibilityChanged(main_window, status))

    main_window.ui.dock_widget_temporal_uw.visibilityChanged.connect(
        lambda status: _dockWidgetTemporalUwVisibilityChanged(main_window, status))
    main_window.ui.dock_widget_network.visibilityChanged.connect(
        lambda status: _dockWidgetNetworkVisibilityChanged(main_window, status))
    main_window.ui.dock_widget_point_list.visibilityChanged.connect(
        lambda status: _dockWidgetPointListVisibilityChanged(main_window, status))
    main_window.ui.dock_widget_setting.visibilityChanged.connect(
        lambda status: _dockWidgetSettingVisibilityChanged(main_window, status))


def _dockWidgetTimeseriesVisibilityChanged(main_window, status):
    main_window.setting_widget.push_button_enable_timeseries.setChecked(status)
    checkMenuAction(main_window, "window", "time series", status)


def _dockWidgetTemporalUwVisibilityChanged(main_window, status):
    main_window.setting_widget.push_button_enable_temporal_unwrapping.setChecked(status)
    checkMenuAction(main_window, "window", "temporal unwrap", status)


def _dockWidgetNetworkVisibilityChanged(main_window, status):
    main_window.setting_widget.push_button_enable_network.setChecked(status)
    checkMenuAction(main_window, "window", "network", status)


def _dockWidgetPointListVisibilityChanged(main_window, status):
    checkMenuAction(main_window, "Window", "Point List", status)


def _dockWidgetSettingVisibilityChanged(main_window, status):
    checkMenuAction(main_window,"Window", "Main Settings", status)


