import numpy as np

# identify하고자 하는 peptide ms와 대조군 ms를 비교하는 함수가 들어있다.

'''
대조군인 spectrum_1에서 p0_mz와 일치하는 peak를 찾아내는 함수이다.
_error_range만큼의 오차를 허용한다.
'''


def find_peak(p0_mz, spectrum_1, _error_range):
    e = float(_error_range)

    p0_mz = float(p0_mz)
    mz_1 = spectrum_1['m/z']

    start = 0
    end = len(mz_1)
    i = 0
    while start <= end:
        i += 1
        mid = int((start + end) / 2)

        if mid >= len(mz_1):
            break

        if start < 0:
            break

        f1 = False
        f2 = False

        mz = float(mz_1[mid])
        f1 = (float(mz) <= float(p0_mz + e))

        f2 = (float(mz) >= float(p0_mz - e))

        if f1 and f2:
            return True

        if mz > p0_mz:
            end = mid - 1

        if mz < p0_mz:
            start = mid + 1

    return False


def get_mz(p):
    return p['m/z']

def get_intensity(p):
    return p['intensity']

def get_spectrum(p):
    return p[['m/z', 'intensity']]


def classify_peaks(p0, p1, _error_range):
    # array to return
    gray = np.empty((0, 2), float)
    blue = np.empty((0, 2), float)

    error_range = _error_range

    mz_0 = get_mz(p0) # query의 mz list
    mz_1 = get_mz(p1) # comparision의 mz list 
    intensity_0 = get_intensity(p0)
    intensity_1 = get_intensity(p1)

    sp_0 = get_spectrum(p0)
    sp_1 = get_spectrum(p1)



    num_of_peaks = len(mz_0)

    for i in range(0, num_of_peaks):
        cur_mz = sp_0['m/z'][i]
        cur_intensity = sp_0['intensity'][i]

        if find_peak(cur_mz, sp_1, error_range):
            blue = np.append(blue, np.array([[cur_mz, cur_intensity]]), axis=0)
        else:
            gray = np.append(gray, np.array([[cur_mz, cur_intensity]]), axis=0)

    return [blue, gray]