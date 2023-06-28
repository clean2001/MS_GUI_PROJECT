import sys
import spectrum_utils.iplot as sup
import spectrum_utils.spectrum as sus
import numpy as np
import altair as alt

import pandas as pd
import numpy as np


import terminal

tol = 0.5

def parse_file(filename : str) :
    with open(filename) as f:
        lines = f.read().splitlines()

        line_len = len(lines)

    data = {
            'title':' ',
            'charge': ' ',
            'pepmass': ' ',
            'scans': ' ',
            'seq': ' ',
            'mz': ' ',
            'intensity': ' '
            } 
    
    newlist = []
    flag = True
    idx = 0     # 큰 list의 index

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
                data['title'] = split_str[1]
                idx += 1
            elif lines[idx][0] == 'C':
                split_str = lines[idx].split('=')
                # print(split_str[1][-1]) # +? -?
                if split_str[1][-1] == '+':
                    data['charge'] = split_str[1][:-1]
                elif split_str[1][0] == '-':
                    data['charge'] = split_str[1][:-1]
                else:
                    data['charge'] = split_str[1]
                idx += 1
            elif lines[idx][0] == 'P':
                split_str = lines[idx].split('=')
                data['pepmass'] = split_str[1]
                idx += 1
            elif lines[idx][0] == 'S':
                split_str = lines[idx].split('=')
                if split_str[0] == 'SCANS':
                    data['scans'] = split_str[1]
                if split_str[0] == 'SEQ':
                    data['seq'] = split_str[1]
                idx += 1
            elif lines[idx] == 'END IONS':
                idx += 1
                flag = False
            else:
                split_xy = lines[idx].split(' ')
                x.append(split_xy[0])
                y.append(split_xy[1])

                idx += 1

        data['mz'] = x
        data['intensity'] = y
        newlist.append(data)

        data = {
            'title':' ',
            'charge': ' ',
            'pepmass': ' ',
            'scans': ' ',
            'seq': ' ',
            'mz': ' ',
            'intensity': ' '
            } 

        flag = True
    return newlist

# make naive, cterm, nterm graph as a html file
def display_graph(data, idx : int):
    dict = data[idx] # dictionary

    spectrum = sus.MsmsSpectrum(
        dict['title'],
        float(dict['pepmass']),
        int(dict['charge']),
        np.array(list(map(float, dict['mz']))),
        np.array(list(map(float, dict['intensity'])))
    )
    spectrum.annotate_proforma(dict['seq'], 10, "ppm", ion_types="by")
    chart = sup.spectrum(spectrum)
    nterm_chart = sup.spectrum(spectrum)
    cterm_chart = sup.spectrum(spectrum)
    ncterm_chart = sup.spectrum(spectrum)

    ### n-term, c-term
    nterm_list = terminal.make_nterm_list(dict['seq'])
    cterm_list = terminal.make_cterm_list(dict['seq'])

    nterm_color = ['blue' for i in range(len(nterm_list))]
    cterm_color = ['red' for i in range(len(cterm_list))]

    nterm_opacity = terminal.make_opacity_list(dict['mz'], nterm_list, tol) # tol은 전역변수이므로, 나중에 수정하기
    cterm_opacity = terminal.make_opacity_list(dict['mz'], cterm_list, tol)

    print(len(nterm_list), len(nterm_opacity))


    cterm_df = pd.DataFrame({
        'w': cterm_list,
        'color': cterm_color,
        'opacity': cterm_opacity
    })

    nterm_df = pd.DataFrame({
        'w': nterm_list,
        'color': nterm_color,
        'opacity': nterm_opacity
    })

    cterm_chart += (
        alt.Chart(cterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N'),
            opacity = alt.Opacity('opacity:Q', scale=None),
        ).interactive()
    )

    nterm_chart += (
        alt.Chart(nterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N'),
            opacity = alt.Opacity('opacity:Q', scale=None),
        ).interactive()
    )

    ncterm_chart += (
        alt.Chart(nterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N'),
            opacity = alt.Opacity('opacity:Q', scale=None),
        ).interactive()
    )

    ncterm_chart += (
        alt.Chart(cterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N'),
            opacity = alt.Opacity('opacity:Q', scale=None),
        ).interactive()
    )

    chart.properties(width=1100, height=400).save("spectrum_naive.html")
    cterm_chart.properties(width=1100, height=400).save("spectrum_cterm.html")
    nterm_chart.properties(width=1100, height=400).save("spectrum_nterm.html")
    ncterm_chart.properties(width=1100, height=400).save("spectrum_ncterm.html")


    
def main():
    if len(sys.argv) < 2:
        print("[ERROR]: Insufficient args")
        sys.exit()
    
    # print(sys.argv[0], sys.argv[1])

    data = parse_file(sys.argv[1])
    display_graph(data, 0)

if __name__ == "__main__":
    main()