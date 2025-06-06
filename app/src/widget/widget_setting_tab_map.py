
def setup(main_wdw):
    wgt = main_wdw.setting_widget
    wgt.tab_map_button_group_background.buttonClicked.connect(
        lambda clicked_button: _changeMapBackground(main_wdw, clicked_button))

    wgt.tab_map_combo_box_amplitude_dates.currentIndexChanged.connect(
        lambda index: _amplitudeIndexChanged(main_wdw, index))

    wgt.tab_map_spin_box_amplitude_n_average.valueChanged.connect(
        main_wdw.plot.plotAmplitudeWithLocalAverage)

    wgt.tab_map_combo_box_strech.currentTextChanged.connect(
        lambda value: _backgroundStretch(main_wdw, value))

    # background options
    wgt.tab_map_push_button_background_aspect.clicked.connect(main_wdw.plot.plotAspect)
    wgt.tab_map_push_button_background_labels.clicked.connect(main_wdw.plot.plotLabels)
    wgt.tab_map_combo_box_background_cmap.currentTextChanged.connect(main_wdw.plot.plotCmap)

    # background points
    wgt.tab_map_push_button_points_1st_order.clicked.connect(
        lambda status: _pushButton1stOrderChange(main_wdw, status))
    wgt.tab_map_push_button_points_2nd_order.clicked.connect(
        lambda status: _pushButton2ndOrderChange(main_wdw, status))

    # separate
    wgt.tab_map_push_button_separate.clicked.connect(
        lambda status: _separateMainMap(main_wdw, status))

    # coherence combobox
    wgt.tab_map_combo_box_points_2nd_order.currentIndexChanged.connect(
        lambda index: _p2ComboBoxIndexChanged(main_wdw, index))

    # point p2 signals
    wgt.tab_map_radio_button_group_p2_plot_type.buttonClicked.connect(
        lambda: _connectP2PointsPlotType(main_wdw))
    wgt.tab_map_combo_box_points_cmap.currentTextChanged.connect(
        lambda cmap: _pointCmapChange(main_wdw, cmap))

    wgt.tab_map_push_botton_points_2nd_order_decrease.clicked.connect(
        lambda: _p2MarkerSizeDecrease(main_wdw))
    wgt.tab_map_push_botton_points_2nd_order_increase.clicked.connect(
        lambda: _p2MarkerSizeIncrease(main_wdw))

    wgt.tab_map_push_botton_points_1st_order_decrease.clicked.connect(
        lambda: _p1MarkerSizeDecrease(main_wdw))
    wgt.tab_map_push_botton_points_1st_order_increase.clicked.connect(
        lambda: _p1MarkerSizeIncrease(main_wdw))



def _changeMapBackground(main_wdw, clicked_button):
    wgt = main_wdw.setting_widget
    options_dict = {"tab_map_push_button_background_mean_amplitude": "mean amplitude",
                    "tab_map_push_button_background_amplitude": "amplitude",
                    "tab_map_push_button_background_temp_coh": "temporal coherence",
                    "tab_map_push_button_background_amplitude_dispersion": "amplitude dispersion",
                    "tab_map_push_button_background_none": "none"}
    background_type = options_dict[clicked_button.objectName()]
    main_wdw.plot.parms.background_type = background_type
    if background_type in main_wdw.plot.parms.background_stretch:
        wgt.tab_map_combo_box_strech.setCurrentText(
            main_wdw.plot.parms.background_stretch[background_type])
    is_amplitude = background_type == "amplitude"
    wgt.tab_map_combo_box_amplitude_dates.setEnabled(is_amplitude)
    wgt.tab_map_spin_box_amplitude_n_average.setEnabled(is_amplitude)
    wgt.tab_map_group_box_select_amplitude.setEnabled(is_amplitude)
    main_wdw.plot.plotBackground()


def _amplitudeIndexChanged(main_wdw, index):
    wgt = main_wdw.setting_widget
    main_wdw.plot.parms.background_amplitude_ind = index
    if (wgt.tab_map_button_group_background.checkedButton() ==
            wgt.tab_map_push_button_background_amplitude):
        main_wdw.plot.plotAmplitude(index)


def _backgroundStretch(main_wdw, value):
    wgt = main_wdw.setting_widget
    options = {wgt.tab_map_push_button_background_mean_amplitude: "mean amplitude",
               wgt.tab_map_push_button_background_amplitude: "amplitude",
               wgt.tab_map_push_button_background_temp_coh: "temporal coherence",
               wgt.tab_map_push_button_background_amplitude_dispersion: "amplitude dispersion",
               wgt.tab_map_push_button_background_none: "none"}
    checked_button = wgt.tab_map_button_group_background.checkedButton()
    main_wdw.plot.plotStretch(value, options[checked_button])


def _pushButton1stOrderChange(main_wdw, status):
    wgt = main_wdw.setting_widget
    main_wdw.plot.plotP1(status)
    qbutton_list = [wgt.tab_map_push_botton_points_1st_order_increase,
                    wgt.tab_map_push_botton_points_1st_order_decrease]
    if status == 0:
        [qbutton.setEnabled(False) for qbutton in qbutton_list]
    else:
        [qbutton.setEnabled(True) for qbutton in qbutton_list]


def _pushButton2ndOrderChange(main_wdw, status):
    wgt = main_wdw.setting_widget
    main_wdw.plot.plotP2(status)
    qbutton_list = [wgt.tab_map_push_button_none,
                    wgt.tab_map_push_button_velocity,
                    wgt.tab_map_push_button_temp_coh,
                    wgt.tab_map_push_button_dem_error,
                    wgt.tab_map_push_botton_points_2nd_order_increase,
                    wgt.tab_map_push_botton_points_2nd_order_decrease]
    if status == 0:
        [qbutton.setEnabled(False) for qbutton in qbutton_list]
    else:
        [qbutton.setEnabled(True) for qbutton in qbutton_list]


def _separateMainMap(main_wdw, status):
    """
    Separate or integrate the main map widget based on the provided status.

    :param status: If True, separate the main map widget; if False, integrate it back.

    """
    wgt = main_wdw.main_map_widget
    if status:  # separate
        wgt.setParent(None)
        wgt.show()
    else:  # integrate
        main_wdw.ui.dock_widget_main_map.setWidget(wgt)


def _p2ComboBoxIndexChanged(main_wdw, index):
    wgt = main_wdw.setting_widget
    status = main_wdw.data.updateP2File(index)
    if status:
        main_wdw.plot.clearP2Plots()
    if wgt.tab_map_push_button_points_2nd_order.isChecked():
        main_wdw.plot.plotP2(True)


def _connectP2PointsPlotType(main_wdw):
    selected_button = main_wdw.setting_widget.tab_map_radio_button_group_p2_plot_type.checkedButton()
    options_dict = {"tab_map_push_button_none": "none",
                    "tab_map_push_button_velocity": "velocity",
                    "tab_map_push_button_temp_coh": "coherence",
                    "tab_map_push_button_dem_error": "demerr"}
    main_wdw.plot.parms.p2_plot_type = options_dict[selected_button.objectName()]
    main_wdw.plot.plotP2(main_wdw.setting_widget.tab_map_push_button_points_2nd_order.isChecked())


def _pointCmapChange(main_wdw, cmap):
    main_wdw.plot.parms.p2_plot_cmap = cmap
    main_wdw.plot.plotPointCmap()


def _p2MarkerSizeDecrease(main_wdw):
    main_wdw.plot.parms.p2_marker_size /= 1.5
    main_wdw.plot.plotP2(True)


def _p2MarkerSizeIncrease(main_wdw):
    main_wdw.plot.parms.p2_marker_size *= 1.5
    main_wdw.plot.plotP2(True)


def _p1MarkerSizeDecrease(main_wdw):
    main_wdw.plot.parms.p1_marker_size /= 1.5
    main_wdw.plot.plotP1(True)


def _p1MarkerSizeIncrease(main_wdw):
    main_wdw.plot.parms.p1_marker_size *= 1.5
    main_wdw.plot.plotP1(True)