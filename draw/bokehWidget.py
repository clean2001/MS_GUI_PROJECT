import pandas as pd
import os
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral3
from bokeh.embed import file_html
from bokeh.resources import CDN
from PyQt5 import QtWidgets, QtCore
import numpy as np

from bokeh.models import HoverTool, BoxZoomTool, ResetTool, WheelZoomTool, PanTool

import compare_ms

def return_cur_dir():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    cur_path = cur_path.replace('\\', '/')
    return cur_path

def convert_spectrum_to_xy(spectrum):
    size_of_spectrum = len(spectrum)

    x = np.array([])  # m/z
    y = np.array([])  # intensity
    for i in range(0, size_of_spectrum):
        x = np.append(x, float(spectrum[i][0]))
        y = np.append(y, float(spectrum[i][1]))

    return [x, y]


class BokehWidget(QtWidgets.QWidget):
    
    # p0, p1은 각각 하나의 스펙트럼의 df 데이터 p0['mz'] 이런식으로 접근가능
    def __init__(self, parent=None, p0=None, p1=None, error_range=None): 
        super().__init__(parent)
        self.display_spectrum(parent, p0, p1, error_range)
        

    def display_spectrum(self, parent=None, p0=None, p1=None, error_range=None):
        [self.blue, self.gray] = compare_ms.classify_peaks(p0, p1, error_range)
        # [title, pep_mass] = (self.p0[0], self.p0[1])
        [blue_x, blue_y] = convert_spectrum_to_xy(self.blue)
        [gray_x, gray_y] = convert_spectrum_to_xy(self.gray)
        # p0, p1은 data frame이다.

        hoverTool = HoverTool(
            tooltips=[
                ("m/z = ", "@mz"),
                ("intensity = ", "@intensity"),
            ]
        )
            
        p = figure(max_height=1000,
                   sizing_mode='stretch_width',
                #    sizing_mode='scale_height',
                   tools=[hoverTool, BoxZoomTool(), ResetTool(), WheelZoomTool(zoom_on_axis=False), PanTool()],
                   toolbar_location="below",)

        blue_df = pd.DataFrame({
            'mz':blue_x,
            'intensity':blue_y
        })


        gray_df = pd.DataFrame({
            'mz': gray_x,
            'intensity': gray_y
        })

        grouped = blue_df.groupby('mz').sum()
        blue_source = ColumnDataSource(grouped)
        grouped = gray_df.groupby('mz').sum()
        gray_source = ColumnDataSource(grouped)

        p.vbar(x='mz', top='intensity', source=blue_source, width=1.5, color='red')
        p.vbar(x='mz', top='intensity', source=gray_source, width=0.7, color='gray')
        url = return_cur_dir() + '/boekehWidget.html'
        print(url)
        html = file_html(p, CDN, "my plot")


        parent.browser.setHtml(html)
