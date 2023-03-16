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


def make_title_list_for_combobox(entire_peptides):
    num_of_peptides = len(entire_peptides)

    title_list = []
    for i in range(0, num_of_peptides):
        title = entire_peptides[0]
        title_list.append(title)

    return title_list


def get_peptide_data(index, entire_peptides):
    return entire_peptides[index]

def get_peptide_title(peptide):
    return peptide[0]

def get_peptide_mz(peptide):
    return peptide(4)

def get_peptide_intensity(peptide):
    return peptide(5)