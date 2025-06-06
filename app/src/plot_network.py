import logging
import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.gridspec import GridSpec

logger = logging.getLogger(__name__)


class Parms:
    def __init__(self):
        """
        Initialize an instance of the Params class for NetworkPlot.
        Keep all parameters that are handled in GUI here.
        Anything related to data that is not modified in GUI should be kept in NetworkPlot
        """
        # network
        self.network_type = 'ifg_stack'
        self.ref_index = 0
        # plot
        self.plot_enable = True
        self.mpl_toolbar_height = 10
        # network
        self.network_marker = 'o'
        self.network_marker_size = 0.5
        self.network_marker_color = 'red'
        self.network_line_color = 'gray'
        self.network_line_width = 0.5
        self.network_line_style = '-'
        # selected date
        self.selected_date_marker = 'o'
        self.selected_date_markersize = 5
        self.selected_date_markerfacecolor = 'blue'
        self.selected_date_markeredgecolor = 'black'
        self.selected_date_alpha = 0.5

        # labels
        self.network_y_label = r"$\perp$ Base. [m]"
        self.network_x_label = r"[years]"
        # histogram
        self.hist_bins = 100
        self.hist_temporal_x_label = "Temp. Base. [days]"
        self.hist_temporal_y_label = "freq."
        self.hist_perpendicular_x_label = r"$\perp$ Base. [m]"
        self.hist_perpendicular_y_label = "freq."
        #
        self.x_tick_direction = 'in'
        self.y_tick_direction = 'in'


class NetworkPlot:
    def __init__(self, data):
        """
        Initialize an instance of the NetworkPlot class.

        All parameters that are modified in GUI should be kept in Parms class.
        """
        self.parms = Parms()
        self.data = data
        self.data.network_type = self.parms.network_type
        self.data.ifg_dynamic_network.ref_index = self.parms.ref_index
        self.canvas = None
        self.mpl_toolbar = None
        self.plot_update = True
        self._initFigure()
        self.selected_date_marker_instance = None

    def _initFigure(self):
        """
        Initialize and configure a network figure.

        :return: None
        """
        figure = Figure()
        self.canvas = FigureCanvas(figure)
        figure.tight_layout()
        gs = GridSpec(4, 2, figure=figure)
        self.ax1 = figure.add_subplot(gs[0:3, :])
        self.ax2 = figure.add_subplot(gs[3, 0])
        self.ax3 = figure.add_subplot(gs[3, 1])
        self.all_axs = [self.ax1, self.ax2, self.ax3]
        figure.set_constrained_layout(True)
        self.mpl_toolbar = NavigationToolbar(self.canvas)
        self.mpl_toolbar.setFixedHeight(self.parms.mpl_toolbar_height)
        self.tickIn()

    def plotNetwork(self):
        """
        """
        if self.parms.plot_enable is False:
            return
        if not self.plot_update:
            self.clear()
            return

        self.clear()
        ifg_net = self.data.ifg_network
        dt = [datetime.date.fromisoformat(d) for d in ifg_net.dates]

        self.ax1.plot(dt, ifg_net.pbase, self.parms.network_marker,
                      color=self.parms.network_marker_color,
                      markersize=self.parms.network_marker_size)
        for idx in ifg_net.ifg_list:
            xx = [dt[idx[0]], dt[idx[1]]]
            yy = [ifg_net.pbase[idx[0]], ifg_net.pbase[idx[1]]]
            self.ax1.plot(xx, yy, self.parms.network_line_style,
                          linewidth=self.parms.network_line_width,
                          color=self.parms.network_line_color)
        self.ax1.set_ylabel(self.parms.network_y_label)
        self.ax1.set_xlabel(self.parms.network_x_label)
        self.ax2.hist(ifg_net.tbase_ifg * 365.25, bins=self.parms.hist_bins)
        self.ax2.set_xlabel(self.parms.hist_temporal_x_label)
        self.ax2.set_ylabel(self.parms.hist_temporal_y_label)
        self.ax3.hist(ifg_net.pbase_ifg, bins=self.parms.hist_bins)
        self.ax3.set_xlabel(self.parms.hist_perpendicular_x_label)
        self.ax3.set_ylabel(self.parms.hist_perpendicular_y_label)
        self.canvas.draw_idle()

    def plotDatesMarker(self, ind):
        if not self.parms.plot_enable:
            return
        if self.selected_date_marker_instance is not None:
            self.selected_date_marker_instance.remove()
        try:  # TODO: remove try bu checking the plot when map initialized.
            ifg_net = self.data.ifg_network
            dt = [datetime.date.fromisoformat(ifg_net.dates[i]) for i in ind]
            self.selected_date_marker_instance = self.ax1.plot(
                dt, ifg_net.pbase[ind], linestyle="",
                marker=self.parms.selected_date_marker,
                markersize=self.parms.selected_date_markersize,
                markerfacecolor=self.parms.selected_date_markerfacecolor,
                markeredgecolor=self.parms.selected_date_markeredgecolor,
                alpha=self.parms.selected_date_alpha)[0]
            self.canvas.draw_idle()
        except:
            pass

    def clear(self):
        for ax in self.all_axs:
            ax.clear()
        self.canvas.draw_idle()

    def tickIn(self):
        for ax in self.all_axs:
            ax.tick_params(axis='x', direction=self.parms.x_tick_direction)
            ax.tick_params(axis='y', direction=self.parms.y_tick_direction)