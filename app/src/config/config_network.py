def configNetworkTab(obj, widget):
    ### widget setting
    if obj.plot_enable:
        widget.push_button_enable_network.click()

    def _setCheckedByText(button_group, button_text):
        for button in button_group.buttons():
            if button.text().lower() == button_text.lower():
                button.setChecked(True)
                break

    _setCheckedByText(widget.tab_network_button_network_type,
                      obj.network_type)

    widget.tab_network_spin_box_ref_image.setValue(obj.ref_index)
