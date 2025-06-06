
from PySide6.QtGui import QKeySequence, QShortcut


def connectShortcuts(main_wdw):
    """
    add shortcuts to the main window

    """
    # main_wdw.points_widget.check_box_plot_hover.setShortcut(QKeySequence("Ctrl+Shift+h"))
    QShortcut(QKeySequence("Ctrl+Shift+h"), main_wdw.ui).activated.connect(
        lambda: _togglePushButton(main_wdw.points_widget.push_button_plot_hover))
    QShortcut(QKeySequence("Ctrl+0"), main_wdw.ui).activated.connect(
        lambda: _toggleDock(main_wdw.ui.dock_widget_point_list))
    QShortcut(QKeySequence("Ctrl+1"), main_wdw.ui).activated.connect(
        lambda: _togglePushButton(main_wdw.setting_widget.push_button_enable_timeseries))
    QShortcut(QKeySequence("Ctrl+2"), main_wdw.ui).activated.connect(
        lambda: _togglePushButton(main_wdw.setting_widget.push_button_enable_temporal_unwrapping))
    QShortcut(QKeySequence("Ctrl+3"), main_wdw.ui).activated.connect(
        lambda: _togglePushButton(main_wdw.setting_widget.push_button_enable_network))


def _togglePushButton(pushbutton):
    pushbutton.click()


def _toggleDock(dock):
    if dock.isVisible():
        dock.close()
    else:
        dock.show()
