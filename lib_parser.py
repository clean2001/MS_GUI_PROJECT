import numpy as np
import json
import re
import sys

def parse_lib(lib_file: str, num_peaks: int, offset: int):
    f = open(lib_file, 'r')
    f.seek(offset)

    mz, intensity = [], []

    for i in range(num_peaks):
        line = f.readline()
        tokens = line.split()
        mz.append(float(tokens[0]))
        intensity.append(float(tokens[1]))

    return mz, intensity
