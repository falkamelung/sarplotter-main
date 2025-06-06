
def configTimeseriesTab(obj, widget):
    if obj.plot_enable:
        widget.push_button_enable_timeseries.click()
    widget.tab_ts_push_button_replicate_ts.setChecked(obj.replicate_ts_plot)
    widget.tab_ts_push_button_remove_dem_error.setChecked(obj.remove_topo_error)
    widget.tab_ts_push_button_fit_seasonal.setChecked(obj.fit_seasonal)

    check_box_lookup = {"poly-1": widget.tab_ts_push_button_fit_1st,
                        "poly-2": widget.tab_ts_push_button_fit_2nd,
                        "poly-3": widget.tab_ts_push_button_fit_3rd,
                        "exp": widget.tab_ts_push_button_fit_exp,}

    for model in check_box_lookup.keys():
        status = True if model in obj.fit_models else False
        check_box_lookup[model].setChecked(status)


