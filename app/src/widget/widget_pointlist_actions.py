

def connectPointsListWidgetSignals(main_wdw):
    """
    Connect signals from the point list widget to their respective functions.
    """
    wgt = main_wdw.points_widget
    wgt.push_button_list_point_delete.clicked.connect(
        lambda: _listWidgetItemDelete(main_wdw))

    wgt.push_button_list_point_clear.clicked.connect(
        lambda: _listWidgetClear(main_wdw))

    wgt.push_button_list_point_plot.clicked.connect(
        lambda: _listWidgetItemPlot(main_wdw))

    wgt.push_button_list_point_add.clicked.connect(
        lambda: _listWidgetAddItem(main_wdw))

    wgt.button_group_list_point_add.buttonClicked.connect(
        lambda: _listWidgetChangeType(main_wdw))
    #

    wgt.push_button_plot_hold.toggled.connect(
        lambda status: _pushButtonHoldPlotChanged(main_wdw, status))

    wgt.push_button_plot_hover.toggled.connect(
        lambda status: _pushButtonHoverPlotChanged(main_wdw, status))

    wgt.push_botton_plot_clear.clicked.connect(
        lambda: _plotClear(main_wdw))

    wgt.push_botton_reset_reference.clicked.connect(
        lambda: _resetReference(main_wdw))

    wgt.list_widget_clicked_points.itemSelectionChanged.connect(
        lambda: _listWidgetSelectionChanged(main_wdw))

    wgt.list_widget_clicked_points.itemDoubleClicked.connect(
        lambda: _listWidgetItemPlot(main_wdw))
    # snap points

    wgt.push_button_plot_snap_1st_order.clicked.connect(
        lambda status: _setSnapP1(main_wdw, status))

    wgt.push_button_plot_snap_2nd_order.clicked.connect(
        lambda status: _setSnapP2(main_wdw, status))
    # marker
    wgt.push_botton_marker_decrease.clicked.connect(
        lambda: _mapMarkerSizeDecrease(main_wdw))
    wgt.push_botton_marker_increase.clicked.connect(
        lambda: _mapMarkerSizeIncrease(main_wdw))


def _listWidgetItemDelete(self):
    """
    Delete selected items from the list widget and corresponding data from the clicked_points_database.

    """
    selected_items = self.points_widget.list_widget_clicked_points.selectedItems()
    if selected_items:
        for item in selected_items:
            row = self.points_widget.list_widget_clicked_points.row(item)
            self.points_widget.list_widget_clicked_points.takeItem(row)
            self.plot.clicked_points_database.pop(row)


def _listWidgetClear(self):
    """
    Clear all items from the list widget and reset the plot's clicked_points_database.

    """
    self.points_widget.list_widget_clicked_points.clear()
    self.plot.clicked_points_database = []


def _listWidgetItemPlot(self):
    """
    Plot selected items from the list widget.

    """
    selected_indexes = self.points_widget.list_widget_clicked_points.selectedIndexes()
    selected_rows = [selected_index.row() for selected_index in selected_indexes]
    self.plot.plotTimeseriesList(selected_rows)
    self.plot.plotTemporalUwList(selected_rows)


def _listWidgetAddItem(self):
    inserted_text = self.points_widget.text_edit_list_point_add.toPlainText()
    items = [text.split(",") for text in inserted_text.split("\n")]
    self.plot.addInsertedPointToList(items)


def _listWidgetChangeType(self):
    # TODO: add point_list_type to config.json
    selected_button = self.points_widget.button_group_list_point_add.checkedButton()

    options_dict = {"push_button_list_point_add_ra_az": "range_azimuth",
                    "push_button_list_point_add_id": "id",
                    "push_button_list_point_add_la_lo": "lat_lon", }
    self.plot.parms.point_list_type = options_dict[selected_button.objectName()]

    count = self.points_widget.list_widget_clicked_points.count()
    items = [self.points_widget.list_widget_clicked_points.item(i) for i in range(count)]

    if self.plot.parms.point_list_type == "id":
        for item, point in zip(items, self.plot.clicked_points_database):
            text = f"{point.point_id}"
            if point.ref_point_id is not None:
                text += f", {point.ref_point_id}"
            item.setText(text)

    elif self.plot.parms.point_list_type == "range_azimuth":
        for item, point in zip(items, self.plot.clicked_points_database):
            text = f"{point.x1}, {point.y1}"
            if point.x2 is not None:
                text += f", {point.x2}, {point.y2}"
            item.setText(text)

    elif self.plot.parms.point_list_type == "lat_lon":
        pass


def _pushButtonHoldPlotChanged(self, status):
    """
    Update the plot_keep attribute in the plot_timeseries object.

    :param status: The status to set (0 to disable, any other value to enable).
    :type status: int
    """
    self.plot.plot_timeseries.plot_keep = False if status == 0 else True
    self.plot.plot_temporal_unwrapping.plot_keep = False if status == 0 else True


def _pushButtonHoverPlotChanged(self, status):
    """
    Update the plot_hover attribute in the plot_timeseries object.

    :param status: The status to set (0 to disable, any other value to enable).
    :type status: int
    """
    self.plot.parms.plot_hover = False if status == 0 else True
    self.plot.plot_temporal_unwrapping.parms.plot_hover = False if status == 0 else True


def _plotClear(self):
    """
    Clear the timeseries plot.

    """
    self.plot.plot_timeseries.clear()
    self.plot.plot_temporal_unwrapping.clear()


def _resetReference(self):
    self.plot.plot_timeseries.last_idx = None
    self.plot.plot_timeseries.ref_idx = None
    self.plot.plot_timeseries.default_ref = True
    self.plot.last_right_clicked_x_ref, self.plot.last_right_clicked_y_ref = None, None


def _listWidgetSelectionChanged(self):
    """
    Handle changes in the selection of items in the list widget.

    """
    selected_indexes = self.points_widget.list_widget_clicked_points.selectedIndexes()
    if len(selected_indexes) == 0:  # when triggered by removing selected item
        return
    selected_rows = [selected_index.row() for selected_index in selected_indexes]
    self.plot.pointSelectionChanged(selected_rows)


def _listWidgetItemPlot(main_wdw):
    """
    Plot selected items from the list widget.

    """
    selected_indexes = main_wdw.points_widget.list_widget_clicked_points.selectedIndexes()
    selected_rows = [selected_index.row() for selected_index in selected_indexes]
    main_wdw.plot.plotTimeseriesList(selected_rows)
    main_wdw.plot.plotTemporalUwList(selected_rows)


def _setSnapP1(self, status: int):
    """
    Set the snap_to_p1 attribute in the plot object.

    :param status: The status to set (0 to disable, any other value to enable).
    :type status: int
    """
    self.plot.parms.snap_to_p1 = False if status == 0 else True


def _setSnapP2(self, status: int):
    """
    Set the snap_to_p2 attribute in the plot object.

    :param status: The status to set (0 to disable, any other value to enable).
    :type status: int
    """
    self.plot.parms.snap_to_p2 = False if status == 0 else True


def _mapMarkerSizeDecrease(self):
    ratio = 1 / 1.5  # TODO: read ratio from config
    self.plot.parms.left_click_marker_size *= ratio
    self.plot.parms.right_click_marker_size *= ratio
    self.plot.parms.hover_marker_size *= ratio
    self.plot.updateClickedMarkers()


def _mapMarkerSizeIncrease(self):
    ratio = 1 / 1.5  # TODO: read ratio from config
    self.plot.parms.left_click_marker_size /= ratio
    self.plot.parms.right_click_marker_size /= ratio
    self.plot.parms.hover_marker_size /= ratio
    self.plot.updateClickedMarkers()
