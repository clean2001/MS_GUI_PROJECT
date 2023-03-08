# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from PyQt5 import QtGui


import sample_data

import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont
from draw import plotWidget
from ui import custom_widgets


cur_path = os.path.dirname(os.path.realpath(__file__))


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()


        with open("light_mode", 'r') as f:
            self.setStyleSheet(f.read())

        # self.dialog = QDialog()
        # self.dialog.textEdit = QTextEdit()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        sample = [
            ['title1'],
            ['title2'],
            ['내일은 꼭 일찍'],
            ['일어나야지'],
            ['b1906_293T_proteinID_01A_QE3_122212.56082']
        ]
        file_combo_box = custom_widgets.SpectrumCombobox(self, sample)

        self.vbox = QVBoxLayout(self.main_widget)


        #########
        #menubar#
        #########
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

        # arg0 : parent / arg1: ms_data
        plot_widget = plotWidget.Plot_Widget(self, sample_data.return_data1(), sample_data.return_data2(), float(0.2))
        self.vbox.addWidget(file_combo_box)
        self.vbox.addWidget(plot_widget)


        self.setWindowTitle('Mass Spectrometry Analysis Tool')
        img_path = cur_path + '/ui/image/icon.png'
        img_path = img_path.replace('\\', '/')

        # self.changeFont()
        self.setWindowIcon(QIcon(img_path))
        self.setLayout(self.vbox)

        self.resize(1200, 800)

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topleft())

    # def changeFont(self):
    #     font = QFont("KIMM_Bold", 10, QFont.Bold);
    #     # font.setBold(True)
    #     # font.setPointSize(45)
    #     # font.setUnderline(True)
    #     self.setFont(font)
    #     self.menubar.setFont(font)

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


