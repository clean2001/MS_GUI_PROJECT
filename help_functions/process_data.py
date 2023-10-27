import sys, json
import pandas as pd
import re


def parse_file(filename : str) -> list:
    with open(filename) as f:
        lines = f.read().splitlines()

        line_len = len(lines)
    
    newlist = []

    data = {
        'idx': 0,
        'title':' ',
        'charge': ' ',
        'pepmass': ' ',
        'scans': ' ',
        'seq': ' ',
        'mz': ' ',
        'intensity': ' '
    }

    newlist.append(data)
    
    spectrum_index = 1
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

# 08.14 'Run' 기능을 구현하며 만든 함수.
# m/z, intensity 대신에 offset을 저장
def parse_query(filename : str) -> list:
    f = open(filename, 'r')

    result = []
    idx = 0
    data = {
        'title': " ",
        'charge': " ",
        'pepmass': " ",
        'scans': " ",
        'offset': " ",
    }
    result.append(data)
    while True:
        idx += 1
        line = f.readline()
        if not line:
            break

        line = line.rstrip()

        if line == "BEGIN IONS":
            data = {
                'title': " ",
                'charge': " ",
                'pepmass': " ",
                'scans': " ",
                'offset': " ",
            }
            continue
        elif line[:5] == "TITLE":
            data['title'] = line.split('=')[1]
        elif line[:6] == "CHARGE":
            data['charge'] = line.split('=')[1]
        elif line[:7] == "PEPMASS":
            data['pepmass'] = line.split('=')[1]
        elif line[:5] == "SCANS":
            data['scans'] == line.split('=')[1]
            offset = f.tell()
            data['offset'] = offset # int
            result.append(data)
        else:
            continue

    return result
    


# result file(.tsv)를 파싱
def parse_result(filename: str) -> list:
    f = open(filename, 'r')
    
    spectrum_index = 0
    
    result = []

    line = f.readline().rstrip()
    while True:
        line = f.readline().rstrip()
        if not line:
            break

        tokens = line.split('\t')
        data = {
            'spectrum_idx': spectrum_index,
            'File': tokens[0],
            'Index': int(tokens[1]),
            'ScanNo': int(tokens[2]),
            'Title': tokens[3],
            'PMZ': float(tokens[4]),
            'Charge': int(tokens[5]),
            'Peptide': tokens[6],
            'CalcMass': float(tokens[7]),
            'SA': float(tokens[8]),
            'QScore': float(tokens[9]),
            '#Ions': int(tokens[10]),
            '#Sig': int(tokens[11]),
            'ppmError': float(tokens[12]),
            'C13': int(tokens[13]),
            'ExpRatio': float(tokens[14]),
            'ProtSites': tokens[15],
            'LibrarySource': tokens[16]
        }

        spectrum_index += 1

        result.append(data)
    
    return result

# 08.11 추가
def process_queries(quries : list[str]) -> dict[str]:
    rslt = dict()
    for q in quries:
        rslt[q] = parse_query(q) # {key : value} == {query file name : list[dict]}
    return rslt

def process_results(results : list[str]):
    rslt = dict()
    rslt_list = []
    for r in results:
        val = parse_result(r)
        rslt[r] = val
        rslt_list += (val)
    return rslt, rslt_list


# project file (.devi)를 파싱
def parse_devi(devi_file_name : str):
    f = open(devi_file_name, 'r')
    target_libraries, decoy_libraries, make_decoy, pept_tolerance = list(), list(), None, None
    min_isotope_tolerance, max_isotope_tolerance, frag_tolerance, quries, results = None, None, None, list(), list()

    while True:
        line = f.readline()
        if not line:
            break

        if len(line) <= 2:
            continue

        line = line.rstrip()
        
        tokens = re.split('[= ]', line) # 구분자 여러 개로 split

        if tokens[0] == 'TargetLib':
            target_libraries.append(tokens[-1])
        elif tokens[0] == 'MakeDecoy':
            make_decoy = int(tokens[-1])
        elif tokens[0] == 'DecoyLib':
            decoy_libraries.append(tokens[-1])
        elif tokens[0] == 'PeptTolerance':
            pept_tolerance = float(tokens[-1].split('ppm')[0])
        elif tokens[0] == 'C13Isotope':
            tokens = tokens[-1].split(',')
            min_isotope_tolerance, max_isotope_tolerance = float(tokens[0]), float(tokens[1])
        elif tokens[0] == 'FragTolerance':
            frag_tolerance = float(tokens[-1].split('da')[0])
        elif tokens[0] == 'Analysis':
            quries.append(tokens[-2].strip(','))
            results.append(tokens[-1])
        else:
            continue
    return (target_libraries, decoy_libraries,
            make_decoy, pept_tolerance, min_isotope_tolerance,
            max_isotope_tolerance, frag_tolerance, quries, results)
