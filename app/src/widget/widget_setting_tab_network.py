
from app.src.list_window import ListDialog


def setup(main_wdw):
    wgt = main_wdw.setting_widget

    wgt.push_button_enable_network.clicked.connect(
        lambda status: showNetworkWidget(main_wdw, status))

    wgt.tab_network_button_network_type.buttonClicked.connect(
        lambda: connectNetworkType(main_wdw))
    wgt.tab_network_spin_box_ref_image.editingFinished.connect(
        lambda: _setNetworkRefrenceIndex(main_wdw))

    wgt.tab_network_push_button_select_dates.clicked.connect(
        lambda: _openDateListDialog(main_wdw))
    wgt.tab_network_push_button_invert_dates.clicked.connect(
        lambda: _invertSelectedDates(main_wdw))

    wgt.tab_network_slider_tbase_max.sliderReleased.connect(
        lambda: _setNetworkMaxTbase(main_wdw))


def showNetworkWidget(main_wdw, status):
    if status:
        main_wdw.ui.dock_widget_network.show()
        main_wdw.plot.plot_network.parms.plot_enable = True
        main_wdw.plot.plot_network.plotNetwork()
    else:
        main_wdw.ui.dock_widget_network.close()
        main_wdw.plot.plot_network.parms.plot_enable = False


def connectNetworkType(main_wdw):
    selected_button = main_wdw.setting_widget.tab_network_button_network_type.checkedButton()
    options_dict = {"tab_network_push_button_ifg_stack": "ifg_stack",
                    "tab_network_push_button_star": "star",
                    "tab_network_push_button_sbas": "sbas",
                    "tab_network_push_button_adaptive": "improved"}
    main_wdw.plot.plot_network.network_type = options_dict[selected_button.objectName()]
    main_wdw.data.network_type = main_wdw.plot.plot_network.network_type
    if main_wdw.plot.plot_network.network_type == "ifg_stack":
        main_wdw.data.ifg_network = None
        main_wdw.data.readIfgNetwork()
    else:
        main_wdw.data.ifg_dynamic_network.type = main_wdw.plot.plot_network.network_type
        main_wdw.data.ifg_dynamic_network.ref_index = main_wdw.plot.plot_network.parms.ref_index
        main_wdw.data.constructDynamicNetwork()

    enabled = True if main_wdw.plot.plot_network.network_type == "star" else False
    main_wdw.setting_widget.tab_network_spin_box_ref_image.setEnabled(enabled)

    main_wdw.plot.plot_network.plotNetwork()
    main_wdw.plot.onClick()


def _setNetworkRefrenceIndex(main_wdw):
    reference_index = int(main_wdw.setting_widget.tab_network_spin_box_ref_image.value())
    main_wdw.plot.plot_network.parms.ref_index = reference_index
    connectNetworkType(main_wdw)
    main_wdw.setting_widget.tab_network_spin_box_ref_image.setMaximum(len(main_wdw.data.ifg_dynamic_network.slc_tbase) - 1)


def _openDateListDialog(main_wdw):
    dialog = ListDialog()
    slc_dates = main_wdw.data.slc_dates  #
    index = [i for i in range(len(slc_dates)) if slc_dates[i] in main_wdw.data.slc_selected_dates]
    slc_dates_in_format = [slc_date.strftime("%Y-%m-%d") for slc_date in main_wdw.data.slc_dates]
    dialog.addItems(slc_dates_in_format, index)
    if dialog.exec():
        items = dialog.selected_index
        main_wdw.data.slc_selected_dates = [slc_dates[i] for i in range(len(slc_dates)) if i in items]
        if main_wdw.plot.plot_network.network_type != "ifg_stack":
            main_wdw.data.constructDynamicNetwork()
            main_wdw.plot.plot_network.plotNetwork()
            main_wdw.plot.onClick()
        main_wdw.setting_widget.tab_network_push_button_select_dates.setChecked(
            len(slc_dates) != len(main_wdw.data.slc_selected_dates))


def _invertSelectedDates(main_wdw):
    if len(main_wdw.data.slc_selected_dates) == len(main_wdw.data.slc_dates):
        return
    main_wdw.data.slc_selected_dates = [date for date in main_wdw.data.slc_dates
                                        if date not in main_wdw.data.slc_selected_dates]
    if main_wdw.plot.plot_network.network_type != "ifg_stack":
        main_wdw.data.constructDynamicNetwork()
        main_wdw.plot.plot_network.plotNetwork()
        main_wdw.plot.onClick()


def _setNetworkMaxTbase(main_wdw):
    vel_max_tbase = int(main_wdw.setting_widget.tab_network_slider_tbase_max.value())
    main_wdw.data.ifg_dynamic_network.max_tbase = vel_max_tbase
    main_wdw.setting_widget.tab_network_label_tbase_max.setText(f"Max {vel_max_tbase} days")

