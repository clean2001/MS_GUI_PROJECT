import sys, json
import spectrum_utils.iplot as sup
import spectrum_utils.spectrum as sus
import numpy as np
import altair as alt

import pandas as pd


import terminal


def parse_file(filename : str) :
    with open(filename) as f:
        lines = f.read().splitlines()

        line_len = len(lines)
    
    spectrum_index = 0
    data = {
            'idx': spectrum_index,
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

        spectrum_index += 1
        data = {
            'idx': spectrum_index,
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

def transparent_background(*args, **kwargs):
    return {
            "background": "transparent",
          }

# make naive, cterm, nterm graph as a html file
def display_graph(data, idx : int, tol : float):
    dict = data[idx] # dictionary

    # alt.themes.register('transparent_background', transparent_background)
    # alt.themes.enable('transparent_background')

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

    nterm_opacity = terminal.make_opacity_list(dict['mz'], nterm_list, tol) # tol은 전역변수이므로, 나중에 수정하기. 일단 0.5
    cterm_opacity = terminal.make_opacity_list(dict['mz'], cterm_list, tol)

    naive_w = [nterm_list[0] for i in range(len(nterm_list))]
    naive_opacity = [0 for i in range(len(nterm_list))]

    naive_df = pd.DataFrame({
        'w': naive_w,
        'opacity': naive_opacity
    })
    seq_to_list = [' ']
    reverse_seq_to_list = [' ']
    seq_to_list += list(dict['seq'])
    reverse_seq_to_list += list(dict['seq'][::-1])
    print(seq_to_list)

    cterm_df = pd.DataFrame({
        'w': cterm_list,
        'color': cterm_color,
        'opacity': cterm_opacity,
        'text': reverse_seq_to_list
    })


    nterm_df = pd.DataFrame({
        'w': nterm_list,
        'color': nterm_color,
        'opacity': nterm_opacity,
        'text': seq_to_list
    })


    chart += (
        alt.Chart(naive_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            opacity = alt.Opacity('opacity', scale=None, legend=None)
        ).interactive()
    )


    cterm_chart += (
        alt.Chart(cterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N', legend=None),
            opacity = alt.Opacity('opacity:Q', scale=None, legend=None),
        ).interactive()
    )

    cterm_chart += (
        alt.Chart(cterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
        ).mark_text(
            dx = -20,
            dy = -200,
            fontSize= 15
        ).encode(text='text').interactive()
    )

    nterm_chart += (
        alt.Chart(nterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N', legend=None),
            opacity = alt.Opacity('opacity:Q', scale=None, legend=None),
        ).interactive()
    )

    nterm_chart += (
        alt.Chart(nterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
        ).mark_text(
            dx = -20,
            dy = -230,
            fontSize = 15,
        ).encode(text='text').interactive()
    )

    ncterm_chart += (
        alt.Chart(nterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N', legend=None),
            opacity = alt.Opacity('opacity:Q', scale=None, legend=None),
        ).interactive()
    )

    ncterm_chart += (
        alt.Chart(cterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
            strokeDash=alt.StrokeDash('opacity:N', legend=None),
            opacity = alt.Opacity('opacity:Q', scale=None, legend=None),
        ).interactive()
    )


    ncterm_chart += (
        alt.Chart(nterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
        ).mark_text(
            dx = -20,
            dy = -230,
            fontSize = 15,
        ).encode(text='text').interactive()
    )

    ncterm_chart += (
        alt.Chart(cterm_df)
        .mark_line()
        .mark_rule()
        .encode(
            x='w',
            color=alt.Color('color:N', scale=None),
        ).mark_text(
            dx = -20,
            dy = -200,
            fontSize = 15,
        ).encode(text='text').interactive()
    )

    chart.properties(width=1000, height=500).save("./spectrums/spectrum_naive"+str(idx)+".html")
    cterm_chart.properties(width=1000, height=500).save("./spectrums/spectrum_cterm"+str(idx)+".html")
    nterm_chart.properties(width=1000, height=500).save("./spectrums/spectrum_nterm"+str(idx)+".html")
    ncterm_chart.properties(width=1000, height=500).save("./spectrums/spectrum_ncterm"+str(idx)+".html")


# 파일 직렬화
def serialize_spectrums_for_py(data: any, json_file: str) :
    with open(json_file, "w") as outfile:
        json.dump(data, outfile)
    # outfile.close()

def serialize_spectrums(data: any, json_file: str) :
    result = json.dumps(data)
    result = 'data = ' + result
    out = open(json_file, 'w')
    out.write(result)
    out.close()

def unserialize_spectrums(json_file: str):
    with open(json_file, "r") as file:
        rslt = json.load(file)
    
    return rslt
###

    
def main():
    if len(sys.argv) < 3:
        print("[ERROR]: Insufficient args")
        sys.exit()

    data = parse_file(sys.argv[1])
    tol = float(sys.argv[2])

    serialize_spectrums(data, "./objects/spectrums.json") # 직렬화
    # serialize_spectrums_for_py(data, "./spectrums/spectrums_for_python.json")

    # for i in range (len(data)):
    #     print(data[i])

    # rslt = unseialize_spectrums("spectrums.json") # 성공
    for i in range(len(data)):
        display_graph(data, i, tol) # html 생성

if __name__ == "__main__":
    main()