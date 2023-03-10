annot_threshold = 1e5
threshold = 0

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd

import numpy as np

# import draw_src
# import sample_data
import compare_ms

# import plotly.graph_objects as go

class PlotlyWidget(QtWidgets.QWidget):
    
    def __init__(self, parent=None, p0=None, p1=None, error_range=None):
        super().__init__(parent)

        self.p0 = p0
        self.p1 = p1

        [self.blue, self.gray] = compare_ms.classify_peaks(p0, p1, error_range)

        self.spectrum = self.get_spectrum(self.p0)
        [title, pep_mass] = (self.p0[0], self.p0[1])
        [self.blue_x, self.blue_y] = self.convert_spectrum_to_xy(self.blue)
        [self.gray_x, self.gray_y] = self.convert_spectrum_to_xy(self.gray)

        list1 = [self.blue_x, self.blue_x, self.blue_y]

        df = pd.DataFrame({
            'Text': self.blue_x,
            'mz': self.blue_x,
            'intensity': self.blue_y
        })

        df = df[df.intensity > annot_threshold].reset_index()
        print(df)

        df1 = df.copy()
        # df1['Text'] = df1.mz.astype(str)
        # df1.loc[df1.intensity <= threshold, 'Text'] = None
        # df1.Text.notnull().sum()

        df2 = df.copy()
        df2['intensity'] = 0
        
        df3 = pd.concat([df1, df2]).sort_values(['mz', 'intensity'])
        
        fig = go.Figure(data=go.Scatter(x=df3['mz'], y=df3['intensity']))
        # fig.update_layout(showlegend=False)
        # fig.update_traces(line=dict(width=1, color='blue'))
        # fig.update_traces(textposition='top center')


        c_df = pd.DataFrame({
            'Text': self.gray_x,
            'mz': self.gray_x,
            'intensity': self.gray_y
        })

        c_df = c_df[c_df.intensity > annot_threshold].reset_index()
        print(c_df)

        c_df1 = c_df.copy()
        # c_df1['Text'] = c_df1.mz.astype(str)
        # c_df1.loc[df1.intensity <= threshold, 'Text'] = None
        # c_df1.Text.notnull().sum()

        c_df2 = c_df.copy()
        c_df2['intensity'] = 0
        
        c_df3 = pd.concat([c_df1, c_df2]).sort_values(['mz', 'intensity'])
        
        fig.add_trace(go.Scatter(x=c_df3['mz'], y=c_df3['intensity']))
        # fig.update_layout(showlegend=False)
        # fig.update_traces(line=dict(width=1, color='gray'))
        # fig.update_traces(textposition='top center')



        # fig.add_trace(go.line(df3, x='mz', y='intensity', color='index'))
        # fig.update_layout(showlegend=False)
        # fig.update_traces(line=dict(width=1, color='gray'))
        # fig.update_traces(textposition='top center')

        parent.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))


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
    
    # def show_graph(self, parent):
    #     fig = px.line(x=self.blue_x, y=self.blue_y)
    #     # fig.update_layout(xaxis_range=[0, 100000])
    #     fig.update_layout()
	    #     parent.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))