
def configTemporalUnwrapTab(obj, obj_plot, widget):
    if obj_plot.plot_enable:
        widget.push_button_enable_temporal_unwrapping.click()

    # widget.tab_tempuw_check_box_remove_seasonal_before_tu.setChecked(obj.remove_seasonal_before_temp_uw)
    # widget.tab_tempuw_check_box_remove_seasonal_after_tu.setChecked(ojb.remove_seasonal_after_temp_uw)

    if obj.reference_type.lower().startswith("arc"):
        widget.tab_tempuw_push_button_reference_arc.setChecked(True)
        status = False
    else:
        widget.tab_tempuw_push_button_reference_window.setChecked(True)
        status = True
    widget.tab_tempuw_spin_box_window_size_azimuth.setEnabled(status)
    widget.tab_tempuw_spin_box_window_size_range.setEnabled(status)
    widget.tab_tempuw_spin_box_window_size_azimuth.setValue(obj.window_size_azimuth)
    widget.tab_tempuw_spin_box_window_size_range.setValue(obj.window_size_range)
    widget.tab_tempuw_push_button_window_sizes_sync.setChecked(obj_plot.window_size_sync)
    widget.tab_tempuw_spin_box_vel_min.setValue(obj.velocity_bound_min * 100)
    widget.tab_tempuw_spin_box_vel_max.setValue(obj.velocity_bound_max * 100)
    widget.tab_tempuw_push_button_vel_bound_sync.setChecked(obj_plot.velocity_bound_sync)
    widget.tab_tempuw_slider_vel_n_samples.setValue(obj.velocity_num_samples)
    widget.tab_tempuw_label_vel_n_samples.setText(f"{obj.velocity_num_samples} samples")
    widget.tab_tempuw_spin_box_demerr_min.setValue(obj.demerr_bound_min)
    widget.tab_tempuw_spin_box_demerr_max.setValue(obj.demerr_bound_max)
    widget.tab_tempuw_push_button_dem_bound_sync.setChecked(obj_plot.demerr_bound_sync)
    widget.tab_tempuw_slider_demerr_n_samples.setValue(obj.demerr_num_samples)
    widget.tab_tempuw_label_demerr_n_samples.setText(f"{obj.demerr_num_samples} samples")
    widget.tab_tempuw_push_button_scatter_label.setChecked(obj_plot.plot_phase_label)
    widget.tab_tempuw_push_button_remove_seasonal_before_tu.setChecked(obj.remove_seasonal_before_temp_uw)
    widget.tab_tempuw_push_button_remove_seasonal_after_tu.setChecked(obj.remove_seasonal_after_temp_uw)
