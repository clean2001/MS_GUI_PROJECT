import sys, os


def return_root_dir():
    cur_path = os.path.dirname(os.path.realpath(__file__))
    cur_path = cur_path.replace('\\', '/')
    return cur_path

import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral3
import sample_data
import numpy as np
# output_file('simple_timeseries_plot.html')

# df = pd.read_csv('thor_wwii.csv')

#make sure MSNDATE is a datetime format
# df['MSNDATE'] = pd.to_datetime(df['MSNDATE'], format='%m/%d/%Y')

# grouped = df.groupby('MSNDATE')['TOTAL_TONS', 'TONS_IC', 'TONS_FRAG'].sum()
# grouped = grouped/1000

# source = ColumnDataSource(grouped)

def convert_spectrum_to_xy(spectrum):
    size_of_spectrum = len(spectrum)

    x = np.array([])  # m/z
    y = np.array([])  # intensity
    for i in range(0, size_of_spectrum):
        x = np.append(x, float(spectrum[i][0]))
        y = np.append(y, float(spectrum[i][1]))

    return [x, y]

def convert_spectrum_to_xy2(spectrum):
    size_of_spectrum = len(spectrum)

    x = []  # m/z
    y = []  # intensity
    for i in range(0, size_of_spectrum):
        x.append(float(spectrum[i][0]))
        y.append(float(spectrum[i][1]))

    return [x, y]


p = figure()

spec = sample_data.return_data1()

[xv, yv] = convert_spectrum_to_xy(spec[3])

df = pd.DataFrame({
    'mz':xv,
    'intensity':yv
})

grouped = df.groupby('mz').sum()
source = ColumnDataSource(grouped)

p.vbar(x='mz', top='intensity', source=source)
# print(spec[3][1])
show(p)