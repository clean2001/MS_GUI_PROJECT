import numpy as np
import json
import re
import sys
import process_sequence

# 라이브러리를 파싱하여 dict(hashmap)으로 바꾼뒤 json 파일로 저장
def lib_scanner(filename: str) -> dict:
    f = open(filename, 'r')
    
    result = dict()
    seq, precursor_ion, num_peaks = None, None, None
    idx = 0
    while True:
        line = f.readline()
        if not line:
            break
        if line[:5] == 'Name:':
            tokens = re.split('[ /_\n]', line) # ' ', /, _구분자 여러 개로 split
            seq = tokens[1]
            seq = process_sequence.brace_modifications(seq) # 57.021 => [57.021]
            precursor_ion = tokens[2]
        elif line[:3] == 'MW:':
            continue
        elif line[:8] == 'Comment:':
            continue
        elif line[:10] == 'Num peaks:':
            num_peaks = int(line.split(' ')[2]) # 피크 개수를 저장
            offset = f.tell()
            idx += 1
            result[str(seq)+'_'+str(precursor_ion)] = {'num_peaks':num_peaks, 'offset':offset, 'index':idx}

    f.close()

    return result



if __name__ == "__main__":
    lib, output = sys.argv[1], sys.argv[2]
    rslt = lib_scanner(lib)
    with open(output, 'w') as f:
        json.dump(rslt, f)