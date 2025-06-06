
from PySide6.QtWidgets import QFileDialog


def screenShotPretty(main_wdw):
    dock_setting_status = main_wdw.ui.dock_widget_setting.isVisible()
    dock_point_list_status = main_wdw.ui.dock_widget_point_list.isVisible()
    max_height = main_wdw.ui.dock_widget_main_map.maximumHeight()
    main_wdw.ui.dock_widget_main_map.setMaximumHeight(100)
    if dock_setting_status:
        main_wdw.ui.dock_widget_setting.hide()
    if dock_point_list_status:
        main_wdw.ui.dock_widget_point_list.hide()
    screenShot(main_wdw)
    if dock_setting_status:
        main_wdw.ui.dock_widget_setting.show()
    if dock_point_list_status:
        main_wdw.ui.dock_widget_point_list.show()
    main_wdw.ui.dock_widget_main_map.setMaximumHeight(max_height)


def screenShot(main_wdw):
    file_dialog = QFileDialog(main_wdw)
    file_dialog.setAcceptMode(QFileDialog.AcceptSave)
    file_dialog.setNameFilter("PNG Files (*.png); JPG Files (*.jpg); BMP Files (*.bmp);")
    file_dialog.setDefaultSuffix("png")
    file_dialog.selectFile("sarplotter.png")
    if file_dialog.exec():
        file_path = file_dialog.selectedFiles()[0]
        pixmap = main_wdw.ui.grab()
        pixmap.save(file_path, quality=50)
