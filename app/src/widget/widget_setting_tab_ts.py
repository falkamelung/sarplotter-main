

def setup(main_wdw):
    wgt = main_wdw.setting_widget

    wgt.push_button_enable_timeseries.clicked.connect(
        lambda status: showTimeSeriesWidget(main_wdw, status))

    wgt.tab_ts_push_button_replicate_ts.clicked.connect(
        lambda status: _pushButtonTimeseriesReplicateChanged(main_wdw, status))
    wgt.tab_ts_push_button_remove_dem_error.clicked.connect(
        lambda status: _pushButtonTimeseriesDemErrorChanged(main_wdw, status))

    # fit
    wgt.tab_ts_button_group_fit.buttonClicked.connect(
        lambda: connectTimeseriesPlotFit(main_wdw))
    wgt.tab_ts_push_button_fit_seasonal.clicked.connect(
        lambda: connectTimeseriesSeasonalFit(main_wdw))


def _pushButtonTimeseriesReplicateChanged(main_wdw, status):
    if status:
        main_wdw.plot.plot_timeseries.parms.replicate_ts_plot = True
    else:
        main_wdw.plot.plot_timeseries.parms.replicate_ts_plot = False
    main_wdw.plot.onClick()


def _pushButtonTimeseriesDemErrorChanged(main_wdw, status):
    if status:
        main_wdw.plot.plot_timeseries.parms.remove_topo_error = True
    else:
        main_wdw.plot.plot_timeseries.parms.remove_topo_error = False
    main_wdw.plot.onClick()


def connectTimeseriesPlotFit(main_wdw):
    wgt = main_wdw.setting_widget
    selected_buttons = [button for button in wgt.tab_ts_button_group_fit.buttons() if
                        button.isChecked()]
    check_box_lookup = {wgt.tab_ts_push_button_fit_1st: "poly-1",
                        wgt.tab_ts_push_button_fit_2nd: "poly-2",
                        wgt.tab_ts_push_button_fit_3rd: "poly-3",
                        wgt.tab_ts_push_button_fit_exp: "exp",}
    main_wdw.plot.plot_timeseries.parms.fit_models = [check_box_lookup[button] for button in selected_buttons]
    main_wdw.plot.plot_timeseries.fitModel()


def connectTimeseriesSeasonalFit(main_wdw):
    wgt = main_wdw.setting_widget
    fit_seasonal = wgt.tab_ts_push_button_fit_seasonal.isChecked()
    main_wdw.plot.plot_timeseries.parms.fit_seasonal = fit_seasonal
    main_wdw.plot.plot_timeseries.fitModel()


def showTimeSeriesWidget(main_wdw, status):
    if status:
        main_wdw.ui.dock_widget_timeseries.show()
        main_wdw.plot.plot_timeseries.parms.plot_enable = True
    else:
        main_wdw.ui.dock_widget_timeseries.close()
        main_wdw.plot.plot_timeseries.parms.plot_enable = False
    main_wdw.plot.onClick()

