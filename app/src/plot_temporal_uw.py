from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib
import numpy as np
# import unwrapping
from .unwraping_temporal import TemporalUnwrapping
from .marker import Marker
# from .load_config import loadConfig

logger = logging.getLogger(__name__)

# config = loadConfig()
# config = config['temporal_uw_plot']


class Parms:
    def __init__(self):
        """
        Initialize an instance of the Params class for TemporalUnwrappingPlot.
        Keep all parameters that are handled in GUI here.
        Anything related to data that is not modified in GUI should be kept in TemporalUnwrappingPlot
        """
        self.plot_enable = True
        self.mpl_toolbar_height = 10
        self.x_tick_direction = 'in'
        self.y_tick_direction = 'in'
        self.unit = "cm"
        self.ts_marker = "o"
        self.ts_marker_size = 2

        self.plot_phase_label = False
        self.font_size = 8

        # scatter plots
        self.scatter_marker_size = 5
        self.scatter_cmap = "jet"
        self.scatter_alpha = 0.5
        self.scatter_marker = "."
        self.scatter_edge_color = 'black'
        self.scatter_edge_line_width = 0.3
        self.scatter_temporal_x_label = "Temp. Base."
        self.scatter_perpendicular_x_label = r"$\perp$ Base. [m]"
        self.scatter_label_loc_h = "left"
        self.scatter_label_loc_v = "top"

        # search space
        self.search_space_cmap = "jet"
        self.search_space_x_label = "DEM error (m)"
        self.search_space_y_label = "Velocity (cm/a)"
        self.search_space_optimum_marker = "o"
        self.search_space_optimum_face_color = "white"
        self.search_space_optimum_edge_color = "black"
        self.search_space_optimum_marker_size = 2

        self.search_space_click_marker = "o"
        self.search_space_click_face_color = "black"
        self.search_space_click_edge_color = "white"
        self.search_space_click_marker_size = 1

        #
        self.window_size_sync = True
        self.demerr_bound_sync = True
        self.velocity_bound_sync = True


class TemporalUnwrappingPlot:
    def __init__(self, data):
        self.parms = Parms()
        self.data = data
        self.plot_update = True  # not used yet.
        self.plot_list = {}
        self.canvas_search_space = None
        self.canvas_phase_plot = None
        self.ax = None
        self.mpl_toolbar_phase_plot = None
        self.mpl_toolbar_search_space = None
        self._initFigurePhase()
        self._initFigureSearchSpace()
        self.all_axs = self.axs + [self.ax_search_space]
        self.tickIn()
        # self._initDates()
        self.tu = TemporalUnwrapping(self.data)
        self.search_space_marker_instance = None
        self.temporal_uw_plots = []
        self.plot_keep = False


    def _initFigurePhase(self):
        """
        initialize phase figure
        """
        figure1 = Figure()
        self.canvas_phase_plot = FigureCanvas(figure1)
        self.axs = [figure1.add_subplot(321+i) for i in range(6)]
        figure1.set_constrained_layout(True)
        self.mpl_toolbar_phase_plot = NavigationToolbar(self.canvas_phase_plot)
        self.mpl_toolbar_phase_plot.setFixedHeight(self.parms.mpl_toolbar_height)
        self.setAxisLabels()
        self.plot_hover = False
        self.hover_last_xy = [-990, -999]

    def _initFigureSearchSpace(self):
        """
        initialize search space figure
        """
        figure = Figure()
        self.canvas_search_space = FigureCanvas(figure)
        figure.tight_layout()
        self.ax_search_space = figure.add_subplot(111)
        figure.set_constrained_layout(True)
        self.mpl_toolbar_search_space = NavigationToolbar(self.canvas_search_space)
        self.mpl_toolbar_search_space.setFixedHeight(self.parms.mpl_toolbar_height)
        self.canvas_search_space.mpl_connect("button_press_event", lambda event: self.onClickSearchSpace(event))
        self.canvas_search_space.mpl_connect('motion_notify_event', lambda event: self.onHoverSearchSpace(event))

    def plotTemporalUW(self, ra: int, az: int, ra_ref: int = None, az_ref: int = None):
        if self.parms.plot_enable is False:
            return
        if (ra is None or az is None) and (ra_ref is None or az_ref is None):
            return
        if self.plot_keep is False:
            self.clear()
            self.plot_list = {}

        tu = self.tu
        tu.temporal_uw(ra, az, ra_ref, az_ref)

        self.plotTemporalUWPhase(tu.velocity_phase, tu.dem_error_phase, tu.residual_phase,
                                 tu.model_tbase_lispace, tu.model_pbase_linspace, tu.model_phase)

        # plot search space
        self.ax_search_space.clear()
        plot = self.ax_search_space.imshow(np.flipud(tu.gamma_grid), extent=(tu.dem_error_range.min(),
                                                                             tu.dem_error_range.max(),
                                                                             tu.velocity_range.min() * 100,
                                                                             tu.velocity_range.max() * 100),
                                           cmap=self.parms.search_space_cmap)
        plot.set_clim(0, 1)
        self.ax_search_space.set_xlabel(self.parms.search_space_x_label)
        self.ax_search_space.set_ylabel(self.parms.search_space_y_label)
        self.ax_search_space.set_aspect("auto")

        self.ax_search_space.plot(tu.dem_error,
                                  tu.velocity * 100,
                                  marker=self.parms.search_space_optimum_marker,
                                  markersize=self.parms.search_space_optimum_marker_size,
                                  markerfacecolor=self.parms.search_space_optimum_face_color,
                                  markeredgecolor=self.parms.search_space_optimum_edge_color)
        self.ax_search_space.xaxis.label.set_fontsize(self.parms.font_size)
        self.ax_search_space.yaxis.label.set_fontsize(self.parms.font_size)
        self.ax_search_space.tick_params(axis='both', which='major', labelsize=self.parms.font_size)
        self.canvas_search_space.draw_idle()

    def plotTemporalUWPhase(self, velocity_phase, dem_error_phase, residual_phase,
                            model_tbase_lispace, model_pbase_linspace, model_phase):

        cmap = self.parms.scatter_cmap
        marker_size = self.parms.scatter_marker_size
        alpha = self.parms.scatter_alpha
        marker = self.parms.scatter_marker
        edge_color = self.parms.scatter_edge_color
        line_width = self.parms.scatter_edge_line_width
        # plot velocity
        Marker(self.tu.tbase_ifg, -self.tu.ifg_phase, facecolor=self.tu.pbase_ifg, edgecolor=edge_color,
               linewidth=line_width, size=marker_size, alpha=alpha, cmap=cmap).simpleMarker(self.axs[0], marker=marker)
        Marker(model_tbase_lispace, -velocity_phase, facecolor='tab:blue', edgecolor=edge_color,
               linewidth=1, size=1, alpha=alpha).simpleMarker(self.axs[0], marker='.')
        # plot dem_error
        Marker(self.tu.pbase_ifg, -self.tu.ifg_phase, facecolor=self.tu.tbase_ifg, edgecolor=edge_color,
               linewidth=line_width, size=marker_size, alpha=alpha, cmap=cmap).simpleMarker(self.axs[1], marker=marker)
        Marker(model_pbase_linspace, -dem_error_phase, facecolor='tab:blue', edgecolor=edge_color,
               linewidth=1, size=1, alpha=alpha).simpleMarker(self.axs[1], marker='.')
        # remove dem_error and plot velocity
        Marker(self.tu.tbase_ifg, -self.tu.residual_phase_dem, facecolor=self.tu.pbase_ifg, edgecolor=edge_color,
               linewidth=line_width, size=marker_size, alpha=alpha, cmap=cmap).simpleMarker(self.axs[2], marker=marker)
        Marker(model_tbase_lispace, -velocity_phase, facecolor='tab:blue', edgecolor=edge_color,
               linewidth=1, size=1, alpha=alpha).simpleMarker(self.axs[2], marker='.')
        # remove velocity and plot dem_error
        Marker(self.tu.pbase_ifg, -self.tu.residual_phase_velocity, facecolor=self.tu.tbase_ifg, edgecolor=edge_color,
               linewidth=line_width, size=marker_size, alpha=alpha, cmap=cmap).simpleMarker(self.axs[3], marker=marker)
        Marker(model_pbase_linspace, -dem_error_phase, facecolor='tab:blue', edgecolor=edge_color,
               linewidth=1, size=1, alpha=alpha).simpleMarker(self.axs[3], marker='.')

        # plot residuals
        self.axs[4].plot(self.tu.tbase_ifg[[0, -1]], [0, 0], '-', linewidth=1)
        Marker(self.tu.tbase_ifg, -residual_phase, facecolor=self.tu.pbase_ifg, edgecolor=edge_color,
               linewidth=line_width, size=marker_size, alpha=alpha, cmap=cmap).simpleMarker(self.axs[4], marker=marker)

        self.axs[5].plot([self.tu.pbase_ifg.min(), self.tu.pbase_ifg.max()], [0, 0], '-', linewidth=1)
        Marker(self.tu.pbase_ifg, -residual_phase, facecolor=self.tu.tbase_ifg, edgecolor=edge_color,
               linewidth=line_width, size=marker_size, alpha=alpha, cmap=cmap).simpleMarker(self.axs[5], marker=marker)

        self.addLabelsToTempUw()
        self.canvas_phase_plot.draw_idle()
        self.setAxisLabels()
        self._setAxisLims(self.tu)
        self.canvas_phase_plot.draw_idle()

    def onClickSearchSpace(self, event):
        """
        Handle click events on the temporal unwrapping search space.

        :param event: Matplotlib event object representing the click event.

        """
        if event.inaxes != self.ax_search_space:
            return
        if self.mpl_toolbar_search_space.mode.name in ['ZOOM', 'PAN']:
            return
        if self.search_space_marker_instance is not None:
            self.search_space_marker_instance.remove()
        dem_error, velocity = event.xdata, event.ydata/100
        tu = self.tu
        model_phase, dem_error_phase, velocity_phase, model_pbase_linspace, model_tbase_lispace = (
            tu.modelPhase(dem_error, velocity, tu.pbase_ifg, tu.tbase_ifg))
        residual_phase, res_phase_dem, res_phase_vel = tu.residualPhase(tu.ifg_phase, tu.design_matrix, dem_error, velocity)
        self.search_space_marker_instance = (
            self.ax_search_space.plot(dem_error, velocity * 100,
                                      self.parms.search_space_click_marker,
                                      markersize=self.parms.search_space_click_marker_size,
                                      markerfacecolor=self.parms.search_space_click_face_color,
                                      markeredgecolor=self.parms.search_space_click_edge_color))[0]

        self.canvas_search_space.draw_idle()

        [ax.clear() for ax in self.axs]

        self.plotTemporalUWPhase(velocity_phase, dem_error_phase, residual_phase,
                                 model_tbase_lispace, model_pbase_linspace, model_phase)

        self.canvas_phase_plot.draw_idle()
        self.setAxisLabels()
        self._setAxisLims(tu)
        self.canvas_phase_plot.draw_idle()

    def onHoverSearchSpace(self, event):
        if self.plot_hover is False:
            return
        if event.xdata is None or event.ydata is None:
            return
        x_hover, y_hover = round(event.xdata), round(event.ydata)
        if x_hover == self.hover_last_xy[0] and y_hover == self.hover_last_xy[1]:
            return
        self.onClickSearchSpace(event)

    def clear(self):
        [ax.clear() for ax in self.axs]
        [ax.clear() for ax in self.axs]
        self.ax_search_space.clear()
        self.canvas_search_space.draw_idle()
        self.canvas_phase_plot.draw_idle()

    def tickIn(self):
        [ax.tick_params(axis='x', direction=self.parms.x_tick_direction) for ax in self.all_axs]
        [ax.tick_params(axis='y', direction=self.parms.y_tick_direction) for ax in self.all_axs]

    def _setAxisLims(self, tu):
        [self.axs[i].set_xlim([tu.tbase_ifg.min(), tu.tbase_ifg.max()]) for i in [0, 2, 4]]
        [self.axs[i].set_xlim([tu.pbase_ifg.min(), tu.pbase_ifg.max()]) for i in [1, 3, 5]]

    def setAxisLabels(self):
        def _axYaxisCol1(ax):
            ax.set_ylim([-np.pi, np.pi])
            ax.set_yticks([-np.pi, 0, np.pi], [r"$-\pi$", r"0", r"$\pi$"])
        [_axYaxisCol1(self.axs[i]) for i in [0, 2, 4]]

        def _axYaxisCol2(ax):
            ax.set_ylim([-np.pi, np.pi])
            ax.set_yticks([-np.pi, 0, np.pi], [])
        [_axYaxisCol2(self.axs[i]) for i in [1, 3, 5]]

        def _axXaxisRow2(ax):
            ticks = ax.get_xticks()
            ax.set_xticks(ticks, [])
        [_axXaxisRow2(self.axs[i]) for i in [0, 1, 2, 3]]
        self.axs[4].set_xlabel(self.parms.scatter_temporal_x_label)
        self.axs[5].set_xlabel(self.parms.scatter_perpendicular_x_label)

        def _setFontSize(ax):
            ax.title.set_fontsize(self.parms.font_size)
            ax.xaxis.label.set_fontsize(self.parms.font_size)
            ax.yaxis.label.set_fontsize(self.parms.font_size)
            ax.tick_params(axis='both', which='major', labelsize=self.parms.font_size)
        [_setFontSize(ax) for ax in self.axs]

    def addLabelsToTempUw(self):
        if self.parms.plot_phase_label:
            loc_h = self.parms.scatter_label_loc_h
            loc_v = self.parms.scatter_label_loc_v

            y = 1 if loc_v == "top" else 0
            pad = -self.parms.font_size if loc_v == "top" else self.parms.font_size
            self.axs[0].set_title(r"$\varphi$", loc=loc_h, y=y, fontsize=self.parms.font_size, pad=pad)
            self.axs[1].set_title(r"$\varphi$", loc=loc_h, y=y, fontsize=self.parms.font_size, pad=pad)
            self.axs[2].set_title(r"$\varphi-\varphi_{dem}$", loc=loc_h, y=y, fontsize=self.parms.font_size, pad=pad)
            self.axs[3].set_title(r"$\varphi-\varphi_{vel}$", loc=loc_h, y=y, fontsize=self.parms.font_size, pad=pad)
            self.axs[4].set_title(r"$\varphi_{res}$", loc=loc_h, y=y, fontsize=self.parms.font_size, pad=pad)
            self.axs[5].set_title(r"$\varphi_{res}$", loc=loc_h, y=y, fontsize=self.parms.font_size, pad=pad)
        self.canvas_phase_plot.draw_idle()

    def removeLabelsFromTempUw(self):
        loc_h = self.parms.scatter_label_loc_h
        [ax.set_title("", loc=loc_h) for ax in self.axs]
        self.canvas_phase_plot.draw_idle()

    def setTempUwPhaseMarkerSize(self, size_change):
        self.parms.scatter_marker_size *= size_change
        def _setScatterSize(ax):
            scatter = None
            for artist in ax.collections:
                if isinstance(artist, matplotlib.collections.PathCollection):
                    scatter = artist
                    break
            if scatter:
                scatter.set_sizes([self.parms.scatter_marker_size])
            self.canvas_phase_plot.draw_idle()

        [_setScatterSize(ax) for ax in self.axs]

