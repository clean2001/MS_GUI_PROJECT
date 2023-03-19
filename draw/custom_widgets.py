import sys, os

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

import pandas as pd

# import MS_GUI_PROJECT.draw.custom_widgets
from . import bokehWidget, convert_data
from . import custom_widgets

# sys.path.append(os.getcwd())
module_path = os.path.abspath(os.getcwd() + '\\..')
if module_path not in sys.path:
    sys.path.append(module_path)


cur_path = os.path.dirname(os.path.realpath(__file__))
cur_path = cur_path.replace('\\', '/')

class ColorThemeBtn(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.btn = QPushButton(self)
        self.btn.setText('change color theme')

        self.btn.clicked.connect(self.change_mode)

    def change_mode(self):
        with open("dark_mode", 'r') as f:
            self.setStyleSheet(f.read())


class SpectrumCombobox(QWidget):
    def __init__(self, parent=None, list_of_title=None):
        super().__init__(parent)
        self.parent = parent

        self.spectrumComboBox = QComboBox(self)
        num_of_spectrum = len(list_of_title)

        for i in range(0, num_of_spectrum):
            self.spectrumComboBox.addItem(str(list_of_title[i]))

        self.spectrumComboBox.activated[str].connect(self.onActivated)
        self.setFixedHeight(22)

    def changeContents(self, title_list):
        self.spectrumComboBox.clear()
        for i in range(0, len(title_list)):
            self.spectrumComboBox.addItem(title_list[i])

        self.spectrumComboBox.update()



    def onActivated(self):
        print(self.spectrumComboBox.currentIndex())
        comparison_idx = self.spectrumComboBox.currentIndex()
        self.parent.comparison = (self.parent.df.loc[comparison_idx])
        bokehWidget.BokehWidget(self.parent, self.parent.query, self.parent.comparison, self.parent.e)


class Toolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        exitAction = QAction(QIcon(cur_path + '/image/exit-btn.png'), 'Exit', parent)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        openAction = QAction(QIcon(cur_path + '/image/open-file.png'), 'Open File', parent)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open a file(.mgf)')
        openAction.triggered.connect(self.openFile)

        self.toolbar = parent.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar = parent.addToolBar('Open File')
        self.toolbar.addAction(openAction)

    def openFile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')
        seq_list = Toolbar.parsing_file(self, fname[0])
        print('file name: ', fname[0])

        # if fname[0]:
        #     f = open(fname[0], 'r')
        #
        #     with f:
        #         self.dialog.setWindowTitle('Dialog')
        #         self.dialog.resize(700, 500)
        #
        #         data = f.read()
        #         self.dialog.textEdit.setText(data)
        #
        #         self.dialog.show()

        split = Toolbar.split_list(self, seq_list)
        title, charge, pep_mass, scans, seq, x, y = Toolbar.split_list(self, seq_list)
        # print("split title: ", title)
        # print("split charge: ", charge)
        # print("split pep_mass: ", pep_mass)
        # print("split scans: ", scans)
        # print("split seq: ", seq)
        # print("split x: ", x)
        # print("split y: ", y)

        data = convert_data.convert_to_dataframe(split)
        self.parent.df = pd.DataFrame(data)
        self.parent.query = self.parent.df.loc[0]
        self.parent.comparison = self.parent.df.loc[0]

        title_list = self.parent.df['title']
        self.parent.file_combo_box.changeContents(title_list)



        # parent.file_combo_box.__init__(parent,)

    def parsing_file(self, filename):
        # filename = 'toy.mgf'
        # filename = 'MS_GUI_PROJECT/draw/toy.mgf'
        print("parsing function")

        with open(filename) as f:
            lines = f.read().splitlines()

        line_len = len(lines)

        data = [' ' for i in range(5)]  # 작은 list
        newlist = []
        flag = True
        idx = 0  # 큰 list의 index

        while idx < line_len - 1:
            x = []
            y = []
            while flag:
                if lines[idx] == '':
                    idx += 1
                    if idx == line_len:
                        flag = False

                elif lines[idx] == 'BEGIN IONS':
                    idx += 1
                elif lines[idx][0] == 'T':
                    split_str = lines[idx].split('=')
                    data[0] = split_str[1]
                    idx += 1
                elif lines[idx][0] == 'C':
                    split_str = lines[idx].split('=')
                    data[1] = split_str[1]
                    idx += 1
                elif lines[idx][0] == 'P':
                    split_str = lines[idx].split('=')
                    data[2] = split_str[1]
                    idx += 1
                elif lines[idx][0] == 'S':
                    split_str = lines[idx].split('=')
                    if split_str[0] == 'SCANS':
                        data[3] = split_str[1]
                    if split_str[0] == 'SEQ':
                        data[4] = split_str[1]
                    idx += 1
                elif lines[idx] == 'END IONS':
                    idx += 1
                    flag = False
                else:
                    split_xy = lines[idx].split(' ')
                    x.append(split_xy[0])
                    y.append(split_xy[1])

                    # data.append(lines[idx])
                    idx += 1

            data.append(x)
            data.append(y)
            newlist.append(data)
            data = [' ' for i in range(5)]  # 다시 빈 list로 만들어주기
            flag = True

        return newlist

    def split_list(self, seq_list):
        title = []
        charge = []
        pep_mass = []
        scans = []
        seq = []
        x = []
        y = []
        print(len(seq_list))

        for i in range(len(seq_list)):
            title.append(seq_list[i][0])
            charge.append(seq_list[i][1])
            pep_mass.append(seq_list[i][2])
            scans.append(seq_list[i][3])
            seq.append(seq_list[i][4])
            x.append(seq_list[i][5])
            y.append(seq_list[i][6])

        print(len(title))
        print(len(charge))
        print(len(pep_mass))
        print(len(scans))
        print(len(seq))
        print(len(x))
        print(len(y))

        return title, charge, pep_mass, scans, seq, x, y