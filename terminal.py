import pandas as pd

proton = 1.007276035
h2o = 18.0105647


amino_acid = pd.DataFrame({ 'AA Codes_1' : ['Gly', 'Ala', 'Ser', 'Pro', 'Val', 'Thr',
                                   'Cys', 'Leu', 'Ile', 'Asn', 'Asp',
                                   'Gln', 'Lys', 'Glu', 'Met', 'His',
                                   'Phe', 'Arg', 'Tyr', 'Trp'],
                     'AA Codes_2' : ['G', 'A', 'S', 'P', 'V', 'T', 'C', 'L', 'I', 'N',
                                     'D', 'Q', 'K', 'E', 'M', 'H', 'F', 'R', 'Y', 'W'],
                     'AA Residue Composition' : ['C2H3NO', 'D3H5NO', 'D3H5NO2', 'C5H7NO', 'C5H9NO',
                                                 'C4H7NO2', 'C3H5NOS', 'C6H11NO', 'C6H11NO', 'C4H6N2O2',
                                                 'C4H5NO3', 'C5H8N2O2', 'C6H12N2O', 'C5H7NO3', 'C5H9NOS',
                                                 'C6H7N3O', 'C9H9NO', 'C6H12N4O', 'C9H9NO2', 'C11H10N2O'],
                     'Mono.' : [57.021464, 71.037114, 87.032029, 97.052764, 99.068414,
                                101.04768, 103.00919, 113.08406, 113.08406, 114.04293,
                                115.02694, 128.05858, 128.09496, 129.04259, 131.04048,
                                137.05891, 147.06841, 156.10111, 163.06333, 186.07931],
                     'Avg.' : [57.05, 71.08, 87.08, 97.12, 99.07, 101.1, 103.1, 113.2, 113.2, 114.1,
                               115.1, 128.1, 128.2, 129.1, 131.2, 137.1, 147.2, 156.2, 163.2, 186.2]})


def make_nterm_list(seq : str) -> list:
    sum = proton
    # n_term = [float(amino_acid.loc[amino_acid['AA Codes_2'] == seq[0]]['Mono.'].iloc[0])]
    n_term = [sum]
    for animo in seq:
        w = float(amino_acid.loc[amino_acid['AA Codes_2'] == animo]['Mono.'].iloc[0])

        sum += w
        n_term.append(sum)
    
    return n_term

def make_cterm_list(seq: str) -> list:
    sum = proton + h2o
    seq = seq[::-1]
    # c_term = [float(amino_acid.loc[amino_acid['AA Codes_2'] == seq[0]]['Mono.'].iloc[0])]
    c_term = [sum]
    # print(float(amino_acid.loc[amino_acid['AA Codes_2'] == seq[0]]['Mono.'].iloc[0]))
    for animo in seq:
        w = float(amino_acid.loc[amino_acid['AA Codes_2'] == animo]['Mono.'].iloc[0])
        sum += w
        c_term.append(sum)
    
    return c_term


# _tol만큼의 오차를 허용하여 일치하는 피크를 찾기
def find_peak(_term: float, _mz: list, _tol: float) -> bool:
    e = float(_tol)

    start = 0
    end = len(_mz)
    i = 0
    while start <= end:
        i += 1
        mid = int((start + end) / 2)

        if mid >= len(_mz):
            break

        if start < 0:
            break

        f1 = False
        f2 = False

        mz = float(_mz[mid])
        f1 = (float(mz) <= float(_term + e))

        f2 = (float(mz) >= float(_term - e))

        if f1 and f2:
            return True

        if mz > _term:
            end = mid - 1

        if mz < _term:
            start = mid + 1

    return False


def make_opacity_list(mz: list, term: list, tol: float) -> list:
    opacity = [0]
    term = term[1:]
    for val in term:
        rslt = find_peak(float(val), mz, tol)
        if rslt:
            opacity.append(1)
        else:
            opacity.append(0)
    
    return opacity