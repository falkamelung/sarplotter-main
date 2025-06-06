

def checkExistingData(main_wdw):
    """
    Disable certain UI elements based on the existence of specific data.

    If amplitude data does not exist, disable the corresponding radio button.
    If temporal coherence data does not exist, disable the corresponding radio button.
    If P1 file does not exist, disable the corresponding checkbox.

    """
    wgt = main_wdw.setting_widget
    if not main_wdw.data.mean_amplitude_file_exist and not main_wdw.data.slc_stack_file_exist:
        wgt.tab_map_push_button_background_mean_amplitude.setEnabled(False)

    if not main_wdw.data.temporal_coherence_exist:
        wgt.tab_map_push_button_background_temp_coh.setEnabled(False)

    if not main_wdw.data.p1_file_exist:
        wgt.tab_map_push_button_points_1st_order.setEnabled(False)
        main_wdw.points_widget.push_button_plot_snap_1st_order.setEnabled(False)

    if main_wdw.data.p2_file_exist:
        wgt.tab_map_combo_box_points_2nd_order.addItems(main_wdw.data.p2_files)

    else:
        wgt.tab_map_push_button_points_2nd_order.setEnabled(False)
        main_wdw.points_widget.push_button_plot_snap_2nd_order.setEnabled(False)
