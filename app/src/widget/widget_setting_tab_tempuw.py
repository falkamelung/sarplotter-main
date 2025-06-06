

def setup(main_wdw):
    # temporal unwrapping settings
    wgt = main_wdw.setting_widget
    wgt.tab_tempuw_button_group_reference.buttonClicked.connect(
        lambda: _setTemporalUwReference(main_wdw))

    wgt.tab_tempuw_spin_box_window_size_azimuth.editingFinished.connect(
        lambda: _setTemporalUwWindosSize(main_wdw, wgt.tab_tempuw_spin_box_window_size_azimuth))
    wgt.tab_tempuw_spin_box_window_size_range.editingFinished.connect(
        lambda: _setTemporalUwWindosSize(main_wdw, wgt.tab_tempuw_spin_box_window_size_range))

    # temporal unwrapping bounds
    wgt.tab_tempuw_spin_box_vel_min.editingFinished.connect(
        lambda: _setTemporalUwBounds(main_wdw, wgt.tab_tempuw_spin_box_vel_min))
    wgt.tab_tempuw_spin_box_vel_max.editingFinished.connect(
        lambda: _setTemporalUwBounds(main_wdw, wgt.tab_tempuw_spin_box_vel_max))
    wgt.tab_tempuw_spin_box_demerr_min.editingFinished.connect(
        lambda: _setTemporalUwBounds(main_wdw, wgt.tab_tempuw_spin_box_demerr_min))
    wgt.tab_tempuw_spin_box_demerr_max.editingFinished.connect(
        lambda: _setTemporalUwBounds(main_wdw, wgt.tab_tempuw_spin_box_demerr_max))

    #
    wgt.tab_tempuw_slider_vel_n_samples.sliderReleased.connect(
        lambda: _setNSamples(main_wdw))
    wgt.tab_tempuw_slider_demerr_n_samples.sliderReleased.connect(
        lambda: _setNSamples(main_wdw))

    wgt.tab_tempuw_push_button_remove_seasonal_before_tu.clicked.connect(
        lambda status: _checkBoxSetTemporalUwSeasonalBerofeTempUw(main_wdw, status))
    wgt.tab_tempuw_push_button_remove_seasonal_after_tu.clicked.connect(
        lambda status: _checkBoxSetTemporalUwSeasonalAfterTempUw(main_wdw, status))

    wgt.tab_tempuw_push_botton_scatter_size_decrease.clicked.connect(
        lambda: _TUMarkerSizeDecrease(main_wdw))
    wgt.tab_tempuw_push_botton_scatter_size_increase.clicked.connect(
        lambda: _TUMarkerSizeIncrease(main_wdw))
    wgt.tab_tempuw_push_button_scatter_label.clicked.connect(
        lambda status: _TULabel(main_wdw, status))

    # window enable
    wgt.push_button_enable_temporal_unwrapping.clicked.connect(
        lambda status: showTemporalUnwrapWidget(main_wdw, status))


def _setTemporalUwReference(main_wdw):
    """
    Switch temporal unwrapping reference between 'arc' and 'window'

    When 'arc' is selected, disables the azimuth and range window size inputs in the GUI.
    When 'window' is selected, enables the azimuth and range window size inputs
    """
    wgt = main_wdw.setting_widget
    tu = main_wdw.plot.plot_temporal_unwrapping.tu
    if wgt.tab_tempuw_push_button_reference_arc.isChecked():
        tu.parms.reference_type = "arc"
        wgt.tab_tempuw_spin_box_window_size_azimuth.setEnabled(False)
        wgt.tab_tempuw_spin_box_window_size_range.setEnabled(False)
        main_wdw.plot.onClick()
    if wgt.tab_tempuw_push_button_reference_window.isChecked():
        tu.parms.reference_type = "window"
        wgt.tab_tempuw_spin_box_window_size_azimuth.setEnabled(True)
        wgt.tab_tempuw_spin_box_window_size_range.setEnabled(True)
        _setTemporalUwWindosSize(main_wdw)


def _setTemporalUwWindosSize(main_wdw, sender=None):
    """
    Sets the window size for temporal unwrapping in azimuth and range directions.
    """

    wgt = main_wdw.setting_widget

    def _syncWindows(sync_boxes, sync_flag):
        """
        sync window sizes
        """
        if sync_flag and sender == sync_boxes[0]:
            sync_boxes[1].setValue(sync_boxes[0].value())
        if sync_flag and sender == sync_boxes[1]:
            sync_boxes[0].setValue(sync_boxes[1].value())

    _syncWindows([wgt.tab_tempuw_spin_box_window_size_azimuth,
                  wgt.tab_tempuw_spin_box_window_size_range],
                 wgt.tab_tempuw_push_button_window_sizes_sync.isChecked())

    azimuth_window_size = int(wgt.tab_tempuw_spin_box_window_size_azimuth.value())
    range_window_size = int(wgt.tab_tempuw_spin_box_window_size_range.value())
    if azimuth_window_size % 2 == 0 or range_window_size % 2 == 0:
        return
    tu = main_wdw.plot.plot_temporal_unwrapping.tu
    tu.parms.window_size_range = range_window_size
    tu.parms.window_size_azimuth = azimuth_window_size
    main_wdw.plot.onClick()


def _setTemporalUwBounds(main_wdw, sender=None):
    """
    Sets the demerr and velocity bounds for temporal unwrapping
    """

    wgt = main_wdw.setting_widget

    def _syncBounds(sync_boxes, sync_flag):
        """
        sync bounds
        """
        if sync_flag and sender == sync_boxes[0]:
            sync_boxes[1].setValue(-int(sync_boxes[0].value()))
        if sync_flag and sender == sync_boxes[1]:
            sync_boxes[0].setValue(-int(sync_boxes[1].value()))

    _syncBounds([wgt.tab_tempuw_spin_box_demerr_min,
                 wgt.tab_tempuw_spin_box_demerr_max],
                wgt.tab_tempuw_push_button_dem_bound_sync.isChecked())

    _syncBounds([wgt.tab_tempuw_spin_box_vel_min,
                 wgt.tab_tempuw_spin_box_vel_max],
                wgt.tab_tempuw_push_button_vel_bound_sync.isChecked())

    demerr_bound_min = int(wgt.tab_tempuw_spin_box_demerr_min.value())
    demerr_bound_max = int(wgt.tab_tempuw_spin_box_demerr_max.value())
    velocity_bound_min = int(wgt.tab_tempuw_spin_box_vel_min.value())
    velocity_bound_max = int(wgt.tab_tempuw_spin_box_vel_max.value())
    tu = main_wdw.plot.plot_temporal_unwrapping.tu
    tu.parms.demerr_bound_min = demerr_bound_min
    tu.parms.demerr_bound_max = demerr_bound_max
    tu.parms.velocity_bound_min = velocity_bound_min / 100
    tu.parms.velocity_bound_max = velocity_bound_max / 100
    main_wdw.plot.onClick()


def _setNSamples(main_wdw):
    wgt = main_wdw.setting_widget
    vel_n_samples = int(wgt.tab_tempuw_slider_vel_n_samples.value())
    demerr_n_samples = int(wgt.tab_tempuw_slider_demerr_n_samples.value())
    wgt.tab_tempuw_label_vel_n_samples.setText(str(vel_n_samples) + " samples")
    wgt.tab_tempuw_label_demerr_n_samples.setText(str(demerr_n_samples) + " samples")
    tu = main_wdw.plot.plot_temporal_unwrapping.tu
    tu.parms.velocity_num_samlpes = vel_n_samples
    tu.parms.demerr_num_samples = demerr_n_samples
    main_wdw.plot.onClick()


def _checkBoxSetTemporalUwSeasonalBerofeTempUw(main_wdw, status):
    tu = main_wdw.plot.plot_temporal_unwrapping.tu
    tu.parms.remove_seasonal_before_temp_uw = True if status else False
    main_wdw.plot.onClick()


def _checkBoxSetTemporalUwSeasonalAfterTempUw(main_wdw, status):
    tu = main_wdw.plot.plot_temporal_unwrapping.tu
    tu.parms.remove_seasonal_after_temp_uw = True if status else False
    main_wdw.plot.onClick()


def _TUMarkerSizeDecrease(main_wdw):
    main_wdw.plot.plot_temporal_unwrapping.setTempUwPhaseMarkerSize(2. / 3)


def _TUMarkerSizeIncrease(main_wdw):
    main_wdw.plot.plot_temporal_unwrapping.setTempUwPhaseMarkerSize(1.5)


def _TULabel(main_wdw, checkbox):
    main_wdw.plot.plot_temporal_unwrapping.plot_phase_label = checkbox
    if checkbox:
        main_wdw.plot.plot_temporal_unwrapping.addLabelsToTempUw()
    else:
        main_wdw.plot.plot_temporal_unwrapping.removeLabelsFromTempUw()


def showTemporalUnwrapWidget(main_wdw, status):
    if status:
        main_wdw.ui.dock_widget_temporal_uw.show()
        main_wdw.plot.plot_temporal_unwrapping.parms.plot_enable = True
    else:
        main_wdw.ui.dock_widget_temporal_uw.close()
        main_wdw.plot.plot_temporal_unwrapping.parms.plot_enable = False
    main_wdw.plot.onClick()
