import gui_functions as gf


def connect_signal_slot(self) -> None:

    self.ButtonQuery.clicked.connect(lambda: gf.run_query(self))
    self.ButtonClearQuery.clicked.connect(lambda: gf.filter_model_changed(self, self.ComboModelChoice.currentText()))
    self.ButtonNewEntry.clicked.connect(lambda: gf.submit_new_entry(self))
    self.ButtonRawDataInput.clicked.connect(lambda: gf.open_file_dialog(self))
    self.ButtonDelete.clicked.connect(lambda: gf.delete_entry(self))

    self.ComboModelChoice.currentTextChanged.connect(lambda model: gf.filter_model_changed(self, model))
    self.ComboModelChoiceNewEntry.currentTextChanged.connect(lambda model: gf.new_entry_model_changed(self, model))

    self.tabWidget.currentChanged.connect(lambda index: gf.on_tab_changed(self, index))

def connections_db_tables(self):
    # ordering
    self.header.sectionClicked.connect(lambda: gf.on_header_clicked(self))
