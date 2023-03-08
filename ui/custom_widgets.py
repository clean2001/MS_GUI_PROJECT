import sys
from PyQt5.QtWidgets import *
# from PyQt5.Qtgui import QIcon

class ColorThemeBtn(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.btn = QPushButton(self)
        self.btn.setText('change color theme')

        self.btn.clicked.connect(self.change_mode)

    def change_mode(self):
        with open("dark_mode", 'r') as f:
            self.setStyleSheet(f.read())



