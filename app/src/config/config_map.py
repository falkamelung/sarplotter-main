def configMapTab(obj, widget):
    ### widget setting
    widget.tab_map_spin_box_amplitude_n_average.setValue(obj.background_amplitude_n_average)
    widget.tab_map_combo_box_background_cmap.setCurrentText(obj.background_cmap)
    widget.tab_map_combo_box_points_cmap.setCurrentText(obj.p2_plot_cmap)

    if obj.equal_aspect:
        widget.tab_map_push_button_background_aspect.click()
    if obj.background_label:
        widget.tab_map_push_button_background_labels.click()

    def _setCheckedByText(button_group, button_text):
        for button in button_group.buttons():
            if button.text().lower() == button_text.lower():
                button.setChecked(True)
                break

    _setCheckedByText(widget.tab_map_button_group_background, obj.background_type)
    _setCheckedByText(widget.tab_map_radio_button_group_p2_plot_type, obj.p2_plot_type)

def configPointsTab(obj, widget):
    # points widget
    widget.push_button_plot_snap_2nd_order.setChecked(obj.snap_to_p2)
    widget.push_button_plot_hover.setChecked(obj.plot_hover)
    widget.push_button_plot_hold.setChecked(obj.plot_hold)
