import pandas as pd
import os
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral3
from bokeh.embed import file_html
from bokeh.resources import CDN
import sample_data
from PyQt5 import QtWidgets, QtCore
import numpy as np

from bokeh.models import HoverTool

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
        x = np.append(x, spectrum[i][0])
        y = np.append(y, spectrum[i][1])

    return [x, y]


class BokehWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, p0=None, p1=None, error_range=None):
        super().__init__(parent)
        self.p0 = p0
        self.p1 = p1

        spec = sample_data.return_data1()

        # [xv, yv] = convert_spectrum_to_xy(spec[3])

        [self.blue, self.gray] = compare_ms.classify_peaks(p0, p1, error_range)

        [title, pep_mass] = (self.p0[0], self.p0[1])
        [blue_x, blue_y] = convert_spectrum_to_xy(self.blue)
        [gray_x, gray_y] = convert_spectrum_to_xy(self.gray)


        hoverTool = HoverTool(
            tooltips=[
                ("m/z = ", "@mz"),
                ("intensity = ", "@intensity"),
    
            ]
        )
            
        p = figure(width=900, height=400, sizing_mode='stretch_both', tools=[hoverTool],)

        spec = sample_data.return_data1()

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

        # p.add_tools(HoverTool(hoverTool))

        parent.browser.setHtml(html)

        # show(p)