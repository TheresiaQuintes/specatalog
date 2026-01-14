import gui_functions as gf


def connect_signal_slot(self) -> None:

    self.Knopf_1.clicked.connect(lambda: gf.print_clicked())
    self.ComboModelChoice.currentTextChanged.connect(lambda text: gf.text_changed(self, text))

def connections_db_tables(self):
    # ordering
    self.header.sectionClicked.connect(lambda: gf.on_header_clicked(self))
