# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from PyQt5 import QtWebEngineWidgets
import sys, os

import pandas as pd

import sample_data

sys.path.append(os.getcwd())
from PyQt5.QtWidgets import *

from PyQt5.QtGui import QIcon
from draw import bokehWidget
from draw import custom_widgets
from draw import convert_data
import help_functions

cur_path = os.path.dirname(os.path.realpath(__file__))


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()


        with open("light_mode", 'r') as f:
            self.setStyleSheet(f.read())

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.data = {
            'title': ["Open a mgf file."],
            'charge': [" "],
            'pepmass': [" "],
            'scan': [" "],
            'seq': [" "],
            'm/z': ["0"],
            'intensity': ["0"]
        }

        # self.data = convert_data.return_data()

        self.df = pd.DataFrame(self.data)
        self.query = self.df.loc[0]
        self.comparison = self.df.loc[0]

        self.file_combo_box = custom_widgets.SpectrumCombobox(self, self.df['title'])

        self.vbox = QVBoxLayout(self.main_widget)


        ###########
        # menubar #
        ###########
        exitAction = QAction(QIcon(cur_path +'ui\\image\\exit.png'), 'Exit', self)

        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        openFileAction = QAction(QIcon(cur_path), 'Open file', self)
        openFileAction.setShortcut('Ctrl+O')
        openFileAction.setStatusTip('Open a file(.mgf)')
        openFileAction.triggered.connect(self.openFile)

        self.statusBar()

        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        filemenu = self.menubar.addMenu('&File')

        filemenu.addAction(openFileAction)
        filemenu.addAction(exitAction)

        ##

        custom_widgets.Toolbar(self)

        # arg0 : parent / arg1: ms_data / arg2: comparative ms data / error_range
        self.e = float(0.2)
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        plot_widget = bokehWidget.BokehWidget(self, self.query, self.comparison, self.e)

        self.vbox.addWidget(self.file_combo_box)
        self.vbox.addWidget(self.browser)


        self.setWindowTitle('Mass Spectrometry Analysis Tool')
        img_path = cur_path + '/ui/image/icon.png'
        img_path = img_path.replace('\\', '/')

        self.setWindowIcon(QIcon(img_path))

        self.resize(1200, 800)

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topleft())

    def openFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')

        if fname[0]:
            f = open(fname[0], 'r')

            with f:

                self.dialog.setWindowTitle('Dialog')
                self.dialog.resize(700, 500)    

                data = f.read()
                self.dialog.textEdit.setText(data)

                self.dialog.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
