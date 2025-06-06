
from PySide6.QtWidgets import QWidget, QVBoxLayout

def setup(main_wdw):
    # main map
    _addCanvasToDock(main_wdw.ui.dock_widget_main_map,
                     main_wdw.plot.canvas,
                     main_wdw.plot.map_toolbar)

    # TS
    _addCanvasToDock(main_wdw.ui.dock_widget_timeseries,
                     main_wdw.plot.plot_timeseries.canvas,
                     main_wdw.plot.plot_timeseries.mpl_toolbar)

    # Temporal Unwrapping
    _addCanvasToWidget(main_wdw.plot_tu_widget.widget_temporal_uw_phase_plot,
                       main_wdw.plot.plot_temporal_unwrapping.canvas_phase_plot,
                       main_wdw.plot.plot_temporal_unwrapping.mpl_toolbar_phase_plot)

    # Temporal Unwrapping search space
    _addCanvasToWidget(main_wdw.plot_tu_widget.widget_temporal_uw_search_space,
                       main_wdw.plot.plot_temporal_unwrapping.canvas_search_space,
                       main_wdw.plot.plot_temporal_unwrapping.mpl_toolbar_search_space)

    # network
    _addCanvasToDock(main_wdw.ui.dock_widget_network,
                     main_wdw.plot.plot_network.canvas,
                     main_wdw.plot.plot_network.mpl_toolbar)
    

def _addCanvasToDock(dock, canvas, map_toolbar=None):
    """
    adds a matplotlib canvas to a QDockWidget

    :param canvas: Matplotlib canvas to be added.
    :param dock: QDockWidget to which the canvas will be added.
    :param map_toolbar: Optional Matplotlib toolbar to be added. If not provided, no toolbar is added.

    """
    layout = QVBoxLayout()
    layout.addWidget(canvas)
    if map_toolbar is not None:
        layout.addWidget(map_toolbar)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    widget = QWidget()
    widget.setLayout(layout)
    dock.setWidget(widget)
    return widget

def _addCanvasToWidget(widget, canvas, map_toolbar=None):
    """
    adds a matplotlib canvas to a QWidget

    :param canvas: Matplotlib canvas to be added.
    :param widget: QWidget to which the canvas will be added.
    :param map_toolbar: Optional Matplotlib toolbar to be added. If not provided, no toolbar is added.

    """
    layout = QVBoxLayout()
    layout.addWidget(canvas)
    if map_toolbar is not None:
        layout.addWidget(map_toolbar)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    widget.setLayout(layout)
    return widget