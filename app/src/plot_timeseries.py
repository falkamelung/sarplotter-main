from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from .model_fitting import FittingModels
import numpy as np

logger = logging.getLogger(__name__)


class Parms:
    def __init__(self):
        """
        Initialize an instance of the Params class for TimeseriesPlot.
        Keep all parameters that are handled in GUI here.
        Anything related to data that is not modified in GUI should be kept in TimeseriesPlot
        """
        self.plot_enable = False
        self.fit_models = ["poly-1"]
        self.fit_line_type = "--"  # TODO: specify one linetype per fit_model
        self.fit_seasonal = True
        self.remove_topo_error = True
        self.replicate_ts_plot = False
        self.mpl_toolbar_height = 10
        self.x_tick_direction = 'in'
        self.y_tick_direction = 'in'
        self.unit = "cm"
        self.ts_marker = "o"
        self.ts_marker_size = 2
        self.replicate_marker = "o"
        self.replicate_marker_size = 1
        self.replicate_marker_color = None


class TimeseriesPlot:
    def __init__(self, data):
        """
        Initialize an instance of the TimeseriesPlot class.

        All parameters that are modified in GUI should be kept in Parms class.

        :param data:
            data (Data): Data class instance.

        Initializes the following attributes:
        - data: Data instance.
        - plot_list: Dictionary to store plotted items.
        - canvas: The canvas for rendering the plot.
        - ax: The axes for the plot.
        - map_toolbar: Toolbar for map-related functionalities.
        - last_idx: Index of the last plotted point.
        - ref_idx: Reference index for plotting.

        Calls the private method _initFigure() to set up the figure.
        """
        self.parms = Parms()
        self.data = data
        self.plot_update = True
        self.plot_list = {}
        self.canvas = None
        self.ax = None
        self.mpl_toolbar = None
        self._initFigure()
        self.last_idx = None
        self.ref_idx = None
        self.default_ref = True
        # self._initDates()
        self.data.readIfgNetwork()
        self.ts_data = None
        self.fit_plot_list = []
        self.ts_fit_velocity = None
        self.plot_keep = False

    def _initFigure(self):
        """
        Initialize and configure a time series figure.

        :return: None
        """
        figure = Figure()
        self.canvas = FigureCanvas(figure)
        figure.tight_layout()
        self.ax = figure.add_subplot(111)
        figure.set_constrained_layout(True)
        self.mpl_toolbar = NavigationToolbar(self.canvas)
        self.mpl_toolbar.setFixedHeight(self.parms.mpl_toolbar_height)
        self.tickIn()

    # def _initDates(self):
    #     """
    #     Load timeseries dates.
    #
    #     :return: None
    #     """
    #     self.data.readDates()

    def plotTimeseries(self, idx: int, idx_ref: int, default_ref: bool=False):
        """
        Plot timeseries for a specific point index.

        :param idx: Index for the point to plot the timeseries.
        :param idx_ref: Index for the reference point.
                        If provided, the difference between the idx and idx_ref timeseries is plotted.
        :param default_ref:  use default reference point from data

        :return: None
        """
        if self.parms.plot_enable is False:
            return
        if self.plot_update is False:
            self.clear()
            return
        if (default_ref is False) and (idx_ref is None):
            self.clear()
            return
        if idx is None:
            self.clear()
            return
        if self.plot_keep is False:
            self.clear()
            self.plot_list = {}

        ts_data_phase = self.data.readTsForIdx(idx, idx_ref, remove_topo_error=self.parms.remove_topo_error)
        ts_data_distance = self.data.phaseToDistance(ts_data_phase, unit=self.parms.unit)
        this_ts_plot = self.ax.plot(self.data.slc_dates_ts,
                                    ts_data_distance,
                                    self.parms.ts_marker,
                                    markersize=self.parms.ts_marker_size)
        if self.parms.replicate_ts_plot:
            jump_in_unit = self.data.phaseToDistance(2 * np.pi, unit=self.parms.unit)
            self.ax.plot(self.data.slc_dates_ts,
                         ts_data_distance + jump_in_unit,
                         self.parms.replicate_marker,
                         markersize=self.parms.replicate_marker_size,
                         color=self.parms.replicate_marker_color)
            self.ax.plot(self.data.slc_dates_ts,
                         ts_data_distance - jump_in_unit,
                         self.parms.replicate_marker,
                         markersize=self.parms.replicate_marker_size,
                         color=self.parms.replicate_marker_color)
        self.ts_data = ts_data_distance
        self.fitModel()
        self.setLabels()
        self.canvas.draw_idle()
        self.plot_list[idx] = this_ts_plot

    def fitModel(self):
        [plot.remove() for plot in self.fit_plot_list]
        self.canvas.draw_idle()
        self.fit_plot_list = []
        if self.ts_data is None:
            return
        if self.parms.fit_models is []:
            return

        fit_seasonal = self.parms.fit_seasonal
        for fit_model, fit_line_type in zip(self.parms.fit_models, self.parms.fit_line_type):
            _, model_x, model_y = (
                FittingModels(self.data.slc_dates_ts, self.ts_data, model=fit_model).fit(seasonal=fit_seasonal))
            plot = self.ax.plot(model_x, model_y, fit_line_type)
            self.fit_plot_list.append(plot[0])
            self.canvas.draw_idle()

    def clear(self):
        self.ax.clear()
        self.canvas.draw_idle()

    def tickIn(self):
        [ax.tick_params(axis='x', direction=self.parms.x_tick_direction) for ax in [self.ax]]
        [ax.tick_params(axis='y', direction=self.parms.x_tick_direction) for ax in [self.ax]]

    def setLabels(self):
        self.ax.set_ylabel(self.parms.unit)
