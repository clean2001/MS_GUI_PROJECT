from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets

import numpy as np

import compare_ms

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

import plotly.express as px
import plotly.graph_objects as go


class Plot_Widget(QWidget):
    p0 = None
    p1 = None
    blue = None
    gray = None
    spectrum = None

    def __init__(self, parent, p0, p1, error_range):
        super(QWidget, self).__init__(parent)

        self.p0 = p0
        self.p1 = p1

        [self.blue, self.gray] = compare_ms.classify_peaks(p0, p1, error_range)

        self.fig = plt.figure(figsize=[70, 100]) 

        # 그리는 부분
        self.spectrum = self.get_spectrum(self.p0)
        [title, pep_mass] = (self.p0[0], self.p0[1])
        [blue_x, blue_y] = self.convert_spectrum_to_xy(self.blue)
        [gray_x, gray_y] = self.convert_spectrum_to_xy(self.gray)

        plt.bar(blue_x, blue_y, color='#FF0000', width=1.5)
        plt.bar(gray_x, gray_y, color='#BDBDBD', width=1.3)
        plt.axis('on')
        # plt.margins(x=-3, y=-3)

        plt.xlim(0, 2000)

        # 눈금 설정
        plt.xticks(np.arange(0, 2000, step=200))
        # plt.yticks(np.arange(0, 1000, step=10))

        # label
        plt.xlabel('m/z')
        plt.ylabel('intensity (real value)')

        # plt.text(2.0, 1e6, 'mass of peptide: ' + str(pep_mass))
        #
        # plt.tight_layout()
        # plt.subplots_adjust(left=0.125, bottom=0.1, right=0.9, top=0.9, wspace=0.2, hspace=0.2)
        # plt.subplots_adjust(right=2)
        self.canvas = FigureCanvas(self.fig)
        
        self.toolbar = NavigationToolbar(self.canvas, self)

        lay = QVBoxLayout()
        lay.addWidget(self.canvas)
        lay.addWidget(self.toolbar)

        self.setLayout(lay)


    def get_spectrum(self, ms_data):
        return ms_data[3]

    def convert_spectrum_to_xy(self, spectrum):
        size_of_spectrum = len(spectrum)

        x = np.array([])  # m/z
        y = np.array([])  # intensity
        for i in range(0, size_of_spectrum):
            x = np.append(x, spectrum[i][0])
            y = np.append(y, spectrum[i][1])

        return [x, y]

    def visual_ms_data(self):
        # spectrum: m/z - intensity의 pair 데이터
        # spectrum = self.get_spectrum(self.p0)
        [title, pep_mass] = (self.p0[0], self.p0[1])
        [blue_x, blue_y] = self.convert_spectrum_to_xy(self.blue)
        [gray_x, gray_y] = self.convert_spectrum_to_xy(self.gray)

        plt.bar(blue_x, blue_y, color='blue')
        plt.bar(gray_x, gray_y, color='gray')
        plt.axis('on')

        plt.xlim(0, 2000)

        # 눈금 설정
        plt.xticks(np.arange(0, 2000, step=200))
        # plt.yticks(np.arange(0, 1000, step=10))

        # label
        plt.xlabel('m/z')
        plt.ylabel('intensity (real value)')

        # title, info
        plt.title(title)
        plt.text(2.0, 1e6, 'mass of peptide: ' + str(pep_mass))


class PlotlyWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, p0=None, p1=None, error_range=None):
        super().__init__(parent)

        self.p0 = p0
        self.p1 = p1

        [self.blue, self.gray] = compare_ms.classify_peaks(p0, p1, error_range)

        self.spectrum = self.get_spectrum(self.p0)
        [title, pep_mass] = (self.p0[0], self.p0[1])
        [blue_x, blue_y] = self.convert_spectrum_to_xy(self.blue)
        [gray_x, gray_y] = self.convert_spectrum_to_xy(self.gray)

        fig = go.Figure(data=[
            go.Bar(x=blue_x, y=blue_y),
            go.Bar(x=gray_x, y=gray_y)
        ])

        fig.update_layout(barmode='overlay')
        fig.show()

    def get_spectrum(self, ms_data):
        return ms_data[3]


    def convert_spectrum_to_xy(self, spectrum):
        size_of_spectrum = len(spectrum)

        x = np.array([])  # m/z
        y = np.array([])  # intensity
        for i in range(0, size_of_spectrum):
            x = np.append(x, spectrum[i][0])
            y = np.append(y, spectrum[i][1])

        return [x, y]