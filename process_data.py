import sys, json
import pandas as pd


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

    line = f.readline()

    while True:
        line = f.readline()
        if not line:
            break

        tokens = line.split('\t')
        data = {
            'spectrum_idx': spectrum_index,
            'File': tokens[0],
            'Index': tokens[1],
            'ScanNo': tokens[2],
            'Title': tokens[3],
            'PMZ': tokens[4],
            'Charge': tokens[5],
            'Peptide': tokens[6],
            'CalcMass': tokens[7],
            'SA': tokens[8],
            'QScore': tokens[9],
            '#Ions': tokens[10],
            '#Sig': tokens[11],
            'ppmError': tokens[12],
            'C13': tokens[13],
            'ExpRatio': tokens[14],
            'ProtSites': tokens[15],
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

def process_results(results : list[str]) -> dict[str]:
    rslt = dict()
    for r in results:
        rslt[r] = parse_result(r)
    
    return rslt