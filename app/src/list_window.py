from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                               QDialog, QPushButton, QLineEdit, QLabel, QAbstractItemView)


class ListDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Items")
        self.setGeometry(100, 100, 300, 200)

        label_lt = QLabel()
        label_lt.setText("-")
        label_gt = QLabel()
        label_gt.setText("")
        text_box_end_date = QLineEdit()
        text_box_start_date = QLineEdit()
        layout_text_box = QHBoxLayout()

        [layout_text_box.addWidget(wgt) for wgt in [label_gt, text_box_start_date, label_lt, text_box_end_date]]

        push_button_ok = QPushButton()
        push_button_ok.setText("Ok")
        push_button_select_all = QPushButton()
        push_button_select_all.setText("Select All")
        push_button_select_revert = QPushButton()
        push_button_select_revert.setText("Revert selection")
        push_button_select_none = QPushButton()
        push_button_select_none.setText("Select None")
        push_button_cancel = QPushButton()
        push_button_cancel.setText("Cancel")
        layout_push_buttons_selection = QHBoxLayout()
        layout_push_buttons_action = QHBoxLayout()
        [layout_push_buttons_selection.addWidget(wgt) for wgt in [push_button_select_none,
                                                                  push_button_select_revert,
                                                                  push_button_select_all]]
        [layout_push_buttons_action.addWidget(wgt) for wgt in [push_button_cancel, push_button_ok]]

        [layout.setContentsMargins(0, 0, 0, 0) for layout in [layout_push_buttons_selection,
                                                              layout_push_buttons_action,
                                                              layout_text_box]]
        [layout.setSpacing(0) for layout in [layout_push_buttons_selection,
                                             layout_push_buttons_action,
                                             layout_text_box]]

        layout_push_buttons = QVBoxLayout()
        [layout_push_buttons.addLayout(layout) for layout in [layout_text_box,
                                                              layout_push_buttons_selection,
                                                              layout_push_buttons_action]]

        container_push_buttons = QWidget()
        container_push_buttons.setLayout(layout_push_buttons)
        container_push_buttons.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(list_widget)
        layout.addWidget(container_push_buttons)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for button in [push_button_ok, push_button_select_all, push_button_select_revert,
                       push_button_select_none, push_button_cancel]:
            button.setDefault(False)
            button.setAutoDefault(False)

        self.list_widget = list_widget
        self.setLayout(layout)
        self.selected_index = []
        self.text_box_start_date = text_box_start_date
        self.text_box_end_date = text_box_end_date

        push_button_ok.clicked.connect(self.okClicked)
        push_button_cancel.clicked.connect(self.cancelClicked)
        push_button_select_all.clicked.connect(self.selectAll)
        push_button_select_none.clicked.connect(self.selectNone)
        push_button_select_revert.clicked.connect(self.selectRevert)

        text_box_start_date.editingFinished.connect(self.textBoxChanged)
        text_box_end_date.editingFinished.connect(self.textBoxChanged)

    def addItems(self, items, selection_list=None):
        self.list_widget.addItems(items)
        if selection_list is None:
            self.list_widget.selectAll()
        else:
            for index in range(self.list_widget.count()):
                item = self.list_widget.item(index)
                item.setSelected(index in selection_list)

    def okClicked(self):
        self.selected_index = [item.row() for item in self.list_widget.selectedIndexes()]
        self.accept()

    def cancelClicked(self):
        self.reject()

    def selectAll(self):
        self.list_widget.selectAll()

    def selectNone(self):
        self.list_widget.clearSelection()

    def selectRevert(self):
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            item.setSelected(not item.isSelected())

    def textBoxChanged(self):
        text_gt = self.text_box_start_date.text()
        text_lt = self.text_box_end_date.text()
        if text_gt == '':
            text_gt = '0'
        if text_lt == '':
            text_lt = '9'
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            item.setSelected((item.text() > text_gt) & (item.text() < text_lt))

