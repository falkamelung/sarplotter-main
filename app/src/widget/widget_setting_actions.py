
from app.src.widget import (widget_setting_tab_map, widget_setting_tab_tempuw,
                            widget_setting_tab_ts, widget_setting_tab_network)


def connectSettingWidgetSignals(main_wdw):
    """
    Connect signals from the setting widget to their respective functions.
    """
    widget_setting_tab_map.setup(main_wdw)
    widget_setting_tab_tempuw.setup(main_wdw)
    widget_setting_tab_ts.setup(main_wdw)
    widget_setting_tab_network.setup(main_wdw)
