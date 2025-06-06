from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
from .marker import Marker, LineMarker
from .plot_timeseries  import TimeseriesPlot
from .plot_temporal_uw  import TemporalUnwrappingPlot
from .plot_network import NetworkPlot
from .config.load_config import loadConfig

logger = logging.getLogger(__name__)


config = loadConfig()
config = config['main_plot']


class Parms:
    def __init__(self):
        self.background_type = "amplitude"
        self.background_amplitude_ind = 0
        self.background_amplitude_n_average = 0
        self.background_cmap = "gray"
        self.equal_aspect = False
        self.background_label = False
        self.background_stretch = {"amplitude": "100%",
                                   "mean amplitude": "100%",
                                   "temporal coherence": "100%",
                                   "amplitude dispersion": "100%"}

        self.left_click_marker_size = 5
        self.right_click_marker_size = 5
        self.hover_marker_size = 5
        self.vel_unit = "cm/yr"

        # p1
        self.p1_marker_size = 5
        self.p1_marker = 'o'
        self.p1_marker_face_color = "white"
        self.p1_marker_edge_color = "white"
        self.p1_marker_alpha = 0.5
        # p2
        self.p2_plot_type = 'none'
        self.p2_plot_cmap = 'jet'
        self.p2_marker_size = 5
        # snap options
        self.snap_to_p1 = False
        self.snap_to_p2 = False
        # hover
        self.plot_hover = False
        self.plot_hold = False

        # plot
        self.mpl_toolbar_height = 20

        self.point_list_type = 'id'


class Plot:
    """
    This class constructs the main plot for SARPlotter and provides methods to manipulate them.
    """

    def __init__(self, data):
        """
        :param data:
            data (Data): Data class instance.

        instance variables
            data (Data): An instance of the Data class.
            canvas (FigureCanvasQTAgg): Matplotlib canvas for PySide6 integration.
            ax (AxesSubplot): Matplotlib axis for creating plots.
            background_plot (AxesImage): Background plot, representing SAR amplitude, or temporal coherence
            map_toolbar (NavigationToolbar): Matplotlib navigation toolbar for the map plot.
            #TODO: complete the list
        """
        self.parms = Parms()
        self.data = data
        self.setupSnap()
        # network
        self.plot_network = NetworkPlot(self.data)

        self.canvas = None
        self.figure = None
        self.ax = None
        self.map_toolbar = None
        self.initMainFigure()
        self.background_plot = None
        self.setupBackground()
        self.plotBackground()
        # markers
        self.left_click_markers = None
        self.right_click_markers = None
        self.hover_marker = None
        self.left_right_click_lines = None
        # points
        self.p1_plot = None
        self.p2_patch_collection = None
        self.p2_plot = None

        self.p2_cbar = None

        # amplitude plot
        self.combo_box_amplitude_dates = None

        # timeseries plot
        self.plot_timeseries = TimeseriesPlot(self.data)
        self.plot_timeseries.parms.plot_enable = False
        # point list
        self.list_widget_clicked_points = None
        self.last_left_clicked_x = None  # TODO: correct the initial reference point
        self.last_left_clicked_y = None
        self.last_left_clicked_id = None
        self.last_right_clicked_x_ref = None
        self.last_right_clicked_y_ref = None
        self.last_right_clicked_id = None
        self.clicked_points_database = []
        # hover
        self.hover_last_idx = -999
        self.hover_last_xy = [-990, -999]
        # temporal unwrapping plot
        self.plot_temporal_unwrapping = TemporalUnwrappingPlot(self.data)
        self.plot_temporal_unwrapping.parms.plot_enable = False
        self.status_bar = None

    def initMainFigure(self):
        """
        initMainFigure initializes the main plot for SARPlotter

        """
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_off()
        self.figure.set_constrained_layout(True)
        #
        self.map_toolbar = NavigationToolbar(self.canvas)
        self.map_toolbar.setFixedHeight(self.parms.mpl_toolbar_height)
        self.canvas.mpl_connect("button_press_event", lambda event: self.onClickMap(event))
        self.canvas.mpl_connect('motion_notify_event', lambda event: self.onHoverMap(event))
        self.canvas.draw_idle()

    def setupAmplitudeList(self):
        self.combo_box_amplitude_dates.addItems(
            [f"{i+1}: {date.strftime('%Y-%m-%d')}" for (i, date) in enumerate(self.data.slc_dates)])

    def setupBackground(self):
        if self.data.no_background is None:
            self.data.no_background = np.ones(self.data.slc_dimension[1:])
        self.background_plot = self.ax.imshow(self.data.no_background, cmap=self.parms.background_cmap)

        if self.data.orbit_direction.lower().startswith('a'):
            self.ax.invert_yaxis()
        elif self.data.orbit_direction.lower().startswith('d'):
            self.ax.invert_xaxis()

    def plotBackground(self):
        background_type = self.parms.background_type
        if background_type.lower() == "mean amplitude":
            self.plotMeanAmplitude()
        if background_type.lower() == "amplitude":
            self.plotAmplitude()
        elif background_type.lower() == "temporal coherence":
            self.plotTemporalCoherence()
        elif background_type.lower() == "none":
            self.plotNoBackground()

    def plotMeanAmplitude(self):
        """
        Updates the background plot with data.mean_amplitude.
        If mean_amplitude data is not already loaded, it is read the data source.

        """
        if self.data.mean_amplitude is None:
            self.data.mean_amplitude = self.data.readMeanAmplitude()
        self.background_plot.set_data(self.data.mean_amplitude)
        self.background_plot.set_clim(np.nanmin(self.data.mean_amplitude), np.nanmax(self.data.mean_amplitude))
        self.background_plot.set_cmap(self.parms.background_cmap)
        self.plotStretch(None, "mean amplitude")
        self.canvas.draw_idle()

    def plotAmplitude(self, ind=None):
        """
        Updates the background plot with one amplitude image.
        If amplitude data is not already loaded, it is read the data source.

        """
        if ind is not None:
            self.parms.background_amplitude_ind = ind

        if self.parms.background_amplitude_n_average == 0:
            amplitude, _ = self.data.readAmplitudeFromSlc(self.parms.background_amplitude_ind)
            slc_inds = [self.parms.background_amplitude_ind]
        else:
            ind1 = self.parms.background_amplitude_ind
            ind2 = ind1 + self.parms.background_amplitude_n_average
            inds = np.sort([ind1, ind2])
            slc_inds = np.arange(inds[0], inds[1]+1)
            amplitude, slc_inds = self.data.readAmplitudeFromSlc(slc_inds)

        self.background_plot.set_data(amplitude)
        self.background_plot.set_clim(np.nanmin(amplitude), np.nanmax(amplitude))
        self.background_plot.set_cmap(self.parms.background_cmap)
        if self.plot_network.parms.plot_enable:
            self.plot_network.plotDatesMarker(slc_inds)

        self.plotStretch(None, "amplitude")
        self.canvas.draw_idle()

    def plotAmplitudeWithLocalAverage(self, ind):
        if self.parms.background_type.lower() == "amplitude":
            self.parms.background_amplitude_n_average = ind
            self.plotAmplitude()

    def plotTemporalCoherence(self):
        """
        Updates the background plot with data.temporal_coherence.
        If temporal coherence data is not already loaded, it is read the data source.

        """
        if self.data.temporal_coherence is None:
            self.data.readTemporalCoherence()
        self.background_plot.set_data(self.data.temporal_coherence)
        self.background_plot.set_clim(np.nanmin(self.data.temporal_coherence), np.nanmax(self.data.temporal_coherence))
        self.background_plot.set_cmap(self.parms.background_cmap)
        self.plotStretch(None, "temporal coherence")
        self.canvas.draw_idle()

    def plotStretch(self, stretch=None, background=None):
        if not background or background == "none":
            return

        stretch = stretch or self.parms.background_stretch.get(background)
        if not stretch:
            return

        self.parms.background_stretch[background] = stretch
        background_array = self.background_plot.get_array()
        data_min = background_array.min()
        data_max = background_array.max()
        data_mean = background_array.mean()
        data_std = background_array.std()
        data_range = data_max - data_min

        try:
            if stretch.endswith("%"):
                p = int(stretch[:-1]) / 100
                p = p if p < 0.5 else 1 - p
                self.background_plot.set_clim([data_min + data_range * p, data_max - data_range * p])
            elif stretch.lower().endswith(("s", "std")):
                n = float(stretch.lower().split('s')[0])
                self.background_plot.set_clim([data_mean - data_std * n, data_mean + data_std * n])
            else:
                self.parms.background_stretch = None
        except Exception as e:
            print(f"Could not apply stretching: {e}")

        self.canvas.draw_idle()


    def plotNoBackground(self):
        """
        Updates the background plot with data.no_background.
        data.data_no_background has the same size as amplitude

        """
        self.background_plot.set_data(self.data.no_background)
        self.background_plot.set_clim(0, 1)
        self.canvas.draw_idle()

    def plotAspect(self, status):
        """
        switch between plot auto and equal aspects

        :param status: Status indicator for equal axis.
            - 0: Set plot aspect to 'auto'.
            - Any other value: Set plot aspect to 'equal'.

        """
        if status == 0:
            self.ax.set_aspect("auto")
            self.canvas.draw_idle()
        else:
            self.ax.set_aspect("equal")
            self.canvas.draw_idle()

    def plotLabels(self, status):
        """
        Toggle the visibility of plot axis labels.
        :param status: Status indicator for axis labels.
            - 0: Turn off axis labels.
            - Any other value: Turn on axis labels.

        """
        if status == 0:
            self.ax.set_axis_off()
            self.canvas.draw_idle()
        else:
            self.ax.set_axis_on()
            self.canvas.draw_idle()

    def plotCmap(self, cmap):
        """
        Update the color map of the background plot.

        :param cmap: Color map to be applied.

        Note:
            - This method handles dynamic changes that may occur while the text is being changed.
        """
        try:
            self.background_plot.set_cmap(cmap)
            self.parms.background_cmap = cmap
            self.canvas.draw_idle()
        except Exception as e:
            pass

    def plotP1(self, status):
        """
        Plot first order (P1) points on the map.

        :param status: Status indicator for plotting P1 points.
           - 0: Remove existing P1 points.
           - Any other value: Plot P1 points.

        """
        if self.p1_plot is not None:
            self.p1_plot.remove()
            self.p1_plot = None
            self.canvas.draw_idle()
        if status == 0:
            return
        if self.data.p1 is None:
            self.data.readP1()

        self.p1_plot = Marker(self.data.p1.coord_xy[:, 1],
                              self.data.p1.coord_xy[:, 0],
                              edgecolor=self.parms.p1_marker_edge_color,
                              facecolor=self.parms.p1_marker_face_color,
                              size=self.parms.p1_marker_size,
                              alpha=self.parms.p1_marker_alpha).simpleMarker(self.ax, marker=self.parms.p1_marker)
        self.canvas.draw_idle()

    def setupSnap(self):
        if not self.data.p2_file_exist:
            self.parms.snap_to_p2 = False
        if not self.data.p1_file_exist:
            self.parms.snap_to_p2 = False

    def plotP2(self, status):
        """
        Plot second order (P2) points on the map.

        :param status: Status indicator for plotting P2 points.
           - False: Remove existing P2 plot and return.
           - True: Plot P2 points.

        If p2_patch_collection is not already created:
            - Check and load data.p2 if it is not already loaded.
            - Create p2_patch_collection.
        """
        self.clearP2Plots()

        if not status:
            return
        clim = [0, 1]
        if self.data.p2 is None:
            self.data.readP2()
        if self.parms.p2_plot_type == 'velocity':
            color_data = self.data.p2_velocity
            color_data = self.data.convertMetrictUnit(color_data, unit0="m/yr", unit1=self.parms.vel_unit)
            clim = [-np.max(np.abs(color_data)), np.max(np.abs(color_data))]
            label = "Vel "+self.parms.vel_unit
        elif self.parms.p2_plot_type == 'coherence':
            color_data = self.data.p2_coherence
            clim = [0, 1]
            label = 'Coherence'
        elif self.parms.p2_plot_type == 'demerr':
            color_data = self.data.p2_demerr
            clim = [-np.max(np.abs(color_data)), np.max(np.abs(color_data))]
            label = "DEM error (m)"
        elif self.parms.p2_plot_type == 'none':
            this_config = config["p2"]
            color_data = this_config.get("color", "white")
        else:
            color_data = 'black'
        self.p2_plot = Marker(self.data.p2.coord_xy[:, 1],
                              self.data.p2.coord_xy[:, 0],
                              edgecolor='none',
                              size=self.parms.p2_marker_size,
                              facecolor=color_data,
                              cmap=self.parms.p2_plot_cmap).simpleMarker(self.ax)
        self.p2_plot.set_clim(clim)
        p2_plot_types = ['velocity', 'coherence', 'demerr']
        if self.parms.p2_plot_type in p2_plot_types:
            self.plotP2Cbar(label=label)
        self.canvas.draw_idle()

    def plotP2Cbar(self, label=""):
        this_config = config["cbar"]
        cbar_pad = this_config.get("pad", 0.01)
        cbar_aspect = this_config.get("aspect", "aspect")
        cbar_shrink = this_config.get("shrink", "shrink")
        cbar_orientation = this_config.get("orientation", "horizontal")
        cbar_location = this_config.get("location", "top")
        cbar = self.figure.colorbar(self.p2_plot, ax=self.ax, pad=cbar_pad, aspect=cbar_aspect,
                                    shrink=cbar_shrink, orientation=cbar_orientation, location=cbar_location)

        this_config = config["cbar"]["ticks"]
        ticks_direction = this_config.get("direction", "in")
        ticks_labelsize = this_config.get("labelsize", "small")
        ticks_length = this_config.get("length", 6)
        cbar.ax.tick_params(direction=ticks_direction, labelsize=ticks_labelsize, length=ticks_length)

        this_config = config["cbar"]["label"]
        label_x = this_config.get("x", 1.05)
        label_y = this_config.get("y", 0)
        label_va = this_config.get("va", "buttom")
        label_ha = this_config.get("ha", "left")
        label_rotation = this_config.get("rotation", 0)
        cbar.ax.text(label_x, label_y, label, va=label_va, ha=label_ha, rotation=label_rotation, transform=cbar.ax.transAxes)
        self.p2_cbar = cbar
        self.canvas.draw_idle()

    def plotPointCmap(self):
        """
        Update the color map of the points.

        :param cmap: Color map to be applied.

        Note:
            - This method handles dynamic changes that may occur while the text is being changed.
        """
        try:
            self.p2_plot.set_cmap(self.parms.p2_plot_cmap)
            self.canvas.draw_idle()
        except Exception as e:
            pass

    def onClickMap(self, event):
        """
        Handle click events on the map.

        :param event: Matplotlib event object representing the click event.

        """
        if event.inaxes != self.ax:
            return
        if self.map_toolbar.mode.name in ['ZOOM', 'PAN']:
            return
        x, y, idx_p1, idx_p2 = self.snapClickedPoint(event.xdata, event.ydata)
        # handle left/right click
        update_plot = False
        if event.button == 1:  # Left mouse button
            self.plot_timeseries.last_idx = idx_p2
            update_plot = True if (x, y) != (self.last_left_clicked_x, self.last_left_clicked_y) else False
            # keep last point
            self.last_left_clicked_x, self.last_left_clicked_y = x, y
            self.last_left_clicked_id = self.rangeAzimuthToId(x, y)
        elif event.button == 3:  # right mouse button
            self.plot_timeseries.ref_idx = idx_p2
            update_plot = True if (x, y) != (self.last_right_clicked_x_ref, self.last_right_clicked_y_ref) else False
            self.last_right_clicked_x_ref, self.last_right_clicked_y_ref = x, y
            self.last_right_clicked_id = self.rangeAzimuthToId(x, y)
            self.plot_timeseries.default_ref = False

        self.plot_timeseries.plot_update = True if idx_p2 is not None else False
        self.addClickedMarkers([self.last_left_clicked_x], [self.last_left_clicked_y],
                                        [self.last_right_clicked_x_ref], [self.last_right_clicked_y_ref])

        # add points to widget list
        if update_plot:
            self.onClick()
            self._addClickedPointToList()
            self.clicked_points_database.append(ClickedPoint(x1=self.last_left_clicked_x,
                                                             y1=self.last_left_clicked_y,
                                                             x2=self.last_right_clicked_x_ref,
                                                             y2=self.last_right_clicked_y_ref,
                                                             point_id=self.last_left_clicked_id,
                                                             ref_point_id=self.last_right_clicked_id,
                                                             idx_p1=idx_p1,
                                                             idx_p2=self.plot_timeseries.last_idx,
                                                             ref_idx_p2=self.plot_timeseries.ref_idx,
                                                             default_ref=self.plot_timeseries.default_ref))

    def onClick(self):
        # plot timeseries
        self.plot_timeseries.plotTimeseries(self.plot_timeseries.last_idx, self.plot_timeseries.ref_idx,
                                            default_ref=self.plot_timeseries.default_ref)
        # plot temporal unwrapping
        if self.plot_temporal_unwrapping.parms.plot_enable:
            self.plot_temporal_unwrapping.plotTemporalUW(self.last_left_clicked_x,
                                                         self.last_left_clicked_y,
                                                         self.last_right_clicked_x_ref,
                                                         self.last_right_clicked_y_ref)
        self.setStatusBar()

    def setStatusBar(self):
        """
        write a message to the status bar of the main window

        """
        message = ""
        if self.last_left_clicked_x is not None or self.last_left_clicked_x is not None:
            message += f"{self.last_left_clicked_x}, {self.last_left_clicked_y}, "
        if self.plot_temporal_unwrapping.parms.plot_enable:
            if self.plot_temporal_unwrapping.tu.temporal_coherence is not None:
                message += f"[Temp. uw. T\u03B3, Vel (cm/a), DEM error (m): "
                message += f"{self.plot_temporal_unwrapping.tu.temporal_coherence:.2f}, "
                message += f"{self.plot_temporal_unwrapping.tu.velocity*100:.1f}, "
                message += f"{self.plot_temporal_unwrapping.tu.dem_error:.1f}]"
        if self.plot_timeseries.parms.plot_enable:
            if self.plot_timeseries.ts_fit_velocity is not None:
                message += f"[Timeseries Vel (cm/a): "
                message += f"{self.plot_timeseries.ts_fit_velocity:.1f}]"
        self.status_bar.showMessage(message)

    def onHoverMap(self, event):
        if self.parms.plot_hover is False:
            return
        if event.inaxes != self.ax:
            return
        if self.map_toolbar.mode.name in ['ZOOM', 'PAN']:
            return
        self.data.readP2()

        x_hover, y_hover = round(event.xdata), round(event.ydata)
        if x_hover == self.hover_last_xy[0] and y_hover == self.hover_last_xy[1]:
            return
        x_hover, y_hover, idx_p1, idx_p2 = self.snapClickedPoint(event.xdata, event.ydata)
        self.hover_last_xy = [x_hover, y_hover]

        if idx_p2 is not None:
            self.plot_timeseries.plotTimeseries(idx_p2, self.plot_timeseries.ref_idx,
                                                default_ref=self.plot_timeseries.default_ref)
        self.plot_temporal_unwrapping.plotTemporalUW(x_hover, y_hover,
                                                     self.last_right_clicked_x_ref,
                                                     self.last_right_clicked_y_ref)
        self.addHoverMarker([x_hover], [y_hover])
        self.setStatusBar()

    def plotTimeseriesList(self, selected_indices: list):
        """
        Plot time series for selected indices of the clicked_points_database.

        :param selected_indices: List of selected row indices.
        :type selected_indices: list[int]
        """
        self.plot_timeseries.plot_update = True
        for index in selected_indices:
            clicked_point = self.clicked_points_database[index]
            self.plot_timeseries.plotTimeseries(clicked_point.idx_p2, clicked_point.ref_idx_p2,
                                                clicked_point.default_ref)

        self.last_left_clicked_x = clicked_point.x1
        self.last_left_clicked_y = clicked_point.y2
        self.last_left_clicked_id = clicked_point.point_id
        self.last_right_clicked_x_ref = clicked_point.x2
        self.last_right_clicked_y_ref = clicked_point.y2
        self.last_right_clicked_id = clicked_point.ref_point_id


    def plotTemporalUwList(self, selected_indices: list):
        if len(selected_indices) < 1:
            return
        index = selected_indices[-1]
        point = self.clicked_points_database[index]
        self.plot_temporal_unwrapping.plotTemporalUW(point.x1, point.y1, point.x2, point.y2)
        self.setStatusBar()

    def _addClickedPointToList(self):
        """
        Add the clicked point to the list widget.

        This method adds a clicked point to the list widget in the format
        "<x1, y1>" or "<x1, y1, x2, y2>" depending on the presence of
        right-clicked reference point coordinates.
        """
        if self.list_widget_clicked_points is None:
            return
        point_list_type = self.parms.point_list_type
        if self.last_left_clicked_x is not None:
            if point_list_type == "id":
                text = f"{self.last_left_clicked_id}"
            elif point_list_type == "range_azimuth":
                text = f"{self.last_left_clicked_x}, {self.last_left_clicked_y}"
        if self.last_right_clicked_x_ref is not None:
            if point_list_type == "id":
                text += f", {self.last_right_clicked_id}"
            elif point_list_type == "range_azimuth":
                text += f", {self.last_right_clicked_x_ref}, {self.last_right_clicked_y_ref}"
        self.list_widget_clicked_points.addItem(text)

    def snapClickedPoint(self, x_clicked, y_clicked, snap_to_p2=None, snap_to_p1=None):
        """
        Snap the clicked point to nearest points (p1 and/or p2) if enabled.

        This method snaps the clicked point to the nearest points (p1 and/or p2) if
        the corresponding snapping options are enabled (snap_to_p1 and/or snap_to_p2).

        :param x_clicked: X-coordinate of the clicked point.
        :type x_clicked: float
        :param y_clicked: Y-coordinate of the clicked point.
        :type y_clicked: float

        :return: Tuple containing the snapped coordinates (x, y), and indices of snapped points (idx_p1, idx_p2).
        :rtype: tuple[float, float, int, int]
        """
        if (x_clicked is None) or (y_clicked is None):
            return None, None, None, None
        x_clicked_round = int(np.round(x_clicked))
        y_clicked_round = int(np.round(y_clicked))
        idx_p1 = None
        idx_p2 = None
        # handle snap to p1 and p2
        if snap_to_p1 is None:
            snap_to_p1 = self.parms.snap_to_p1
        if snap_to_p2 is None:
            snap_to_p2 = self.parms.snap_to_p2
        if snap_to_p1:
            self.data.readP1()
            idx_p1 = self.data.p1_point_tree.query([x_clicked_round, y_clicked_round])[1]
            y_snap_to_p1, x_snap_to_p1 = self.data.p1.coord_xy[idx_p1, :]
        if snap_to_p2:
            self.data.readP2()
            idx_p2 = self.data.p2_point_tree.query([x_clicked_round, y_clicked_round])[1]
            y_snap_to_p2, x_snap_to_p2 = self.data.p2.coord_xy[idx_p2, :]

        if self.plot_timeseries.parms.plot_enable:
            self.data.readP2()
            idx_closest_p2 = self.data.p2_point_tree.query([x_clicked_round, y_clicked_round])[1]
            if np.all(self.data.p2.coord_xy[idx_closest_p2, :] == [y_clicked_round, x_clicked_round]):
                idx_p2 = idx_closest_p2

        # check snap to p1 and p2
        if snap_to_p1 and not snap_to_p2:
            x, y = x_snap_to_p1, y_snap_to_p1
        elif not snap_to_p1 and snap_to_p2:
            x, y = x_snap_to_p2, y_snap_to_p2
        elif snap_to_p1 and snap_to_p2:
            x, y = self._findCloserPoint(x_clicked_round, y_clicked_round, x_snap_to_p1, y_snap_to_p1, x_snap_to_p2, y_snap_to_p2)
        else:
            x, y = x_clicked_round, y_clicked_round
        return x, y, idx_p1, idx_p2

    def addInsertedPointToList(self, items):
        """

        :param items: nested list of coordinates or ids
        :return:
        """

        for item in items:
            point_x, point_y, point_id = None, None, None
            ref_point_x, ref_point_y, ref_point_id = None, None, None
            max_x = self.data.n_pixels
            max_y = self.data.n_lines
            max_id = max_x * max_y

            # inserted_text = self.points_widget.text_edit_list_point_add.toPlainText()
            # items = inserted_text.split(",")
            text = None
            if self.parms.point_list_type == "id":
                if len(item) in [1, 2]:
                    point_id = int(item[0])
                    if point_id >= max_id:
                        return
                    else:
                        text = f"{point_id}"
                        point_x, point_y = self.idToRangeAzimuth(point_id)
                else:
                    pass  # TODO: show some error message
                if len(item) == 2:
                    ref_point_id = int(item[1])
                    if ref_point_id >= max_id:
                        return
                    else:
                        text += f", {ref_point_id}"
                        ref_point_x, ref_point_y = self.idToRangeAzimuth(ref_point_id)

            elif self.parms.point_list_type == "range_azimuth":
                if len(item) in [2, 4]:
                    point_x = int(item[0])
                    point_y = int(item[1])
                    if (point_x >= max_x) or (point_y >= max_y):
                        return
                    else:
                        text = f"{point_x}, {point_y}"
                        point_id = self.rangeAzimuthToId(point_x, point_y)
                else:
                    pass  # TODO: show some error message
                if len(item) == 4:
                    ref_point_x = int(item[2])
                    ref_point_y = int(item[3])
                    if (ref_point_x >= max_x) or (ref_point_y >= max_y):
                        return
                    else:
                        text += f", {ref_point_x}, {ref_point_y}"
                        ref_point_id = self.rangeAzimuthToId(ref_point_x, ref_point_y)

            if text is None:
                return

            self.list_widget_clicked_points.addItem(text)

            x, y, idx_p1, idx_p2 = self.snapClickedPoint(point_x, point_y, snap_to_p1=False, snap_to_p2=False)
            if (x != point_x) or (y != point_y):
                idx_p1, idx_p2 = None, None

            x, y, ref_idx_p1, ref_idx_p2 = self.snapClickedPoint(ref_point_x, ref_point_y, snap_to_p1=False,
                                                                 snap_to_p2=False)
            if (x != ref_point_x) or (y != ref_point_y):
                ref_idx_p1, ref_idx_p2 = None, None

            self.last_left_clicked_x = point_x
            self.last_left_clicked_y = point_y
            self.last_left_clicked_id = point_id
            self.last_right_clicked_x_ref = ref_point_x
            self.last_right_clicked_y_ref = ref_point_y
            self.last_right_clicked_id = ref_point_id

            self.clicked_points_database.append(ClickedPoint(x1=point_x,
                                                             y1=point_y,
                                                             x2=ref_point_x,
                                                             y2=ref_point_y,
                                                             point_id=point_id,
                                                             ref_point_id=ref_point_id,
                                                             idx_p1=idx_p1,
                                                             idx_p2=idx_p2,
                                                             ref_idx_p2=ref_idx_p2,
                                                             default_ref=self.plot_timeseries.default_ref))

        self.addClickedMarkers([self.last_left_clicked_x], [self.last_left_clicked_y],
                               [self.last_right_clicked_x_ref], [self.last_right_clicked_y_ref])
        self.onClick()

    def addLeftClickedMarkers(self, x: list, y: list, *, marker=None, facecolor=None, edgecolor=None,
                              alpha=None, edge_width=None):
        """
        Add left-clicked markers to the map.

        :param x: List of X-coordinates of the markers.
        :param y: List of Y-coordinates of the markers.
        :param facecolor: Face color of the markers. Default is 'white'.
        :param edgecolor: Edge color of the markers. Default is 'white'.
        :param alpha: Transparency of the markers. Default is 0.8.

        """
        this_config = config["left_click_point"]
        if marker is None:
            marker = this_config.get("marker", "s")
        if facecolor is None:
            facecolor = this_config.get("facecolor", "none")
        if edgecolor is None:
            edgecolor = this_config.get("edgecolor", "black")
        if alpha is None:
            alpha = this_config.get("alpha", 0.8)
        if edge_width is None:
            edge_width = this_config.get("edge_width", 10)

        size = self.parms.left_click_marker_size
        if self.left_click_markers is not None:
            self.left_click_markers.remove()
        self.left_click_markers = Marker(x, y, facecolor=facecolor, edgecolor=edgecolor, size=size,
                                         alpha=alpha, linewidth=edge_width).simpleMarker(self.ax, marker=marker)
        self.canvas.draw_idle()

    def addRightClickedMarkers(self, x: list, y: list, *, marker=None, facecolor=None, edgecolor=None,
                               alpha=None, edge_width=None):
        """
        Add right-clicked markers to the map.

        :param x: List of X-coordinates of the markers.
        :param y: List of Y-coordinates of the markers.
        :param facecolor: Face color of the markers. Default is 'white'.
        :param edgecolor: Edge color of the markers. Default is 'white'.
        :param alpha: Transparency of the markers. Default is 0.8.

        """
        this_config = config["right_click_point"]
        if marker is None:
            marker = this_config.get("marker", "s")
        if facecolor is None:
            facecolor = this_config.get("facecolor", "none")
        if edgecolor is None:
            edgecolor = this_config.get("edgecolor", "black")
        if alpha is None:
            alpha = this_config.get("alpha", 0.8)
        if edge_width is None:
            edge_width = this_config.get("edge_width", 1)

        size = self.parms.right_click_marker_size
        if self.right_click_markers is not None:
            self.right_click_markers.remove()
        self.right_click_markers = Marker(x, y, facecolor=facecolor, edgecolor=edgecolor, size=size,
                                          alpha=alpha, linewidth=edge_width).simpleMarker(self.ax, marker=marker)
        self.canvas.draw_idle()

    def addClickedMarkers(self, x, y, x_ref, y_ref, line_style=None, line_width=None):
        """
        Add clicked markers and lines to the map.

        :param line_width_ratio:
        :param line_syle:
        :param x: List of X-coordinates of the left clicks.
        :param y: List of Y-coordinates of the left clicks.
        :param x_ref: List of X-coordinates of right clicks.
        :param y_ref: List of Y-coordinates of right clicks.

        """
        # TODO: add addLeftClickedMarkers parameters to addClickedMarkers
        this_config = config["clicked_point"]
        if line_style is None:
            line_style = this_config.get("line_style", "-")
        if line_width is None:
            line_width = this_config.get("line_width", 1)

        self.addLeftClickedMarkers(x, y)
        self.addRightClickedMarkers(x_ref, y_ref)
        if self.left_right_click_lines is not None:
            [marker.remove() for marker in self.left_right_click_lines]
        self.left_right_click_lines = LineMarker(x1=x, y1=y,
                                                 x2=x_ref, y2=y_ref,
                                                 linewidth=line_width).simpleMarker(self.ax, style=line_style)
        self.canvas.draw_idle()

    def updateClickedMarkers(self):
        self.addClickedMarkers(x=[self.last_left_clicked_x], y=[self.last_left_clicked_y],
                               x_ref=[self.last_right_clicked_x_ref], y_ref=[self.last_right_clicked_y_ref])
        self.canvas.draw_idle()

    def addHoverMarker(self, x: list, y: list, *, marker=None, facecolor=None, edgecolor=None,
                       alpha=None, edge_width=None):
        """
        Add left-clicked markers to the map.

        :param x: List of X-coordinates of the markers.
        :param y: List of Y-coordinates of the markers.
        :param facecolor: Face color of the markers. Default is 'white'.
        :param edgecolor: Edge color of the markers. Default is 'white'.
        :param alpha: Transparency of the markers. Default is 0.8.
        :param linewidth: Width of the marker edges. Default is 2.

        """
        this_config = config["hover_point"]
        if marker is None:
            marker = this_config.get("marker", ".")
        if facecolor is None:
            facecolor = this_config.get("facecolor", ".")
        if edgecolor is None:
            edgecolor = this_config.get("edgecolor", ".")
        if alpha is None:
            alpha = this_config.get("alpha", ".")
        if edge_width is None:
            edge_width = this_config.get("edge_width", 1)

        size = self.parms.hover_marker_size
        if self.hover_marker is not None:
            self.hover_marker.remove()
        self.hover_marker = Marker(x, y, facecolor=facecolor, edgecolor=edgecolor,
                                   size=size, alpha=alpha, linewidth=edge_width).simpleMarker(self.ax, marker=marker)
        self.canvas.draw_idle()

    def _findCloserPoint(self, x_reference, y_reference, x1, y1, x2, y2):
        """
        Calculate the point closer to a certain point.

        :param x_reference: X-coordinate of the reference point.
        :param y_reference: Y-coordinate of the reference point.
        :param x1: X-coordinate of the first point.
        :param y1: Y-coordinate of the first point.
        :param x2: X-coordinate of the second point.
        :param y2: Y-coordinate of the second point.

        :return: Tuple containing the coordinates of the point closer to the reference point.

        """
        d1 = np.sqrt((x_reference - x1) ** 2 + (y_reference - y1) ** 2)
        d2 = np.sqrt((x_reference - x2) ** 2 + (y_reference - y2) ** 2)
        return (x1, y1) if d1<d2 else (x2, y2)

    def pointSelectionChanged(self, selected_indices):
        """
        Handle changes in the selection of clicked points.

        This method updates the plot by adding markers for the selected points in
        the clicked_points_database. It adds left-clicked markers for (x1, y1)
        coordinates and right-clicked markers for (x2, y2) coordinates, if available.

        :param selected_indices: List of selected item indices.
        :type selected_indices: list[int]
        """
        # add left-click points
        point_db = self.clicked_points_database
        x1 = [point_db[row].x1 for row in selected_indices]
        y1 = [point_db[row].y1 for row in selected_indices]

        # add right-click points
        x_ref, y_ref = [], []
        for row in selected_indices:
            x_ref.append(point_db[row].x2)
            y_ref.append(point_db[row].y2)
        self.addClickedMarkers(x1, y1, x_ref, y_ref)

    def clearP2Plots(self):
        if self.p2_cbar is not None:
            self.p2_cbar.remove()
            self.p2_cbar = None
        if self.p2_plot is not None:
            self.p2_plot.remove()
            self.p2_plot = None
            self.canvas.draw_idle()

    def rangeAzimuthToId(self, x, y):
        if (x is None) or (y is None):
            return None
        else:
            return self.data.point_id_image[y, x]

    def idToRangeAzimuth(self, point_id):
        if point_id is None:
            return None
        else:
            x = np.mod(point_id, self.data.n_pixels)
            y = point_id // self.data.n_pixels
            return x, y


class ClickedPoint:
    """
    ClickedPoint class represents information about clicked points.

    This class stores information about clicked points, including their
    coordinates, indices, and reference indices.

    :param x1: X-coordinate of the first point.
    :type x1: float or None
    ...
    """
    def __init__(self, x1=None, y1=None, x2=None, y2=None, point_id=None, ref_point_id=None, idx_p1=None, idx_p2=None, ref_idx_p1=None, ref_idx_p2=None,
                 default_ref=False):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.point_id = point_id
        self.ref_point_id = ref_point_id
        self.idx_p1 = idx_p1
        self.idx_p2 = idx_p2
        self.ref_idx_p1 = ref_idx_p1
        self.ref_idx_p2 = ref_idx_p2
        self.default_ref = default_ref
