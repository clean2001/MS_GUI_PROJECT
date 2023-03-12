import numpy as np

# identify하고자 하는 peptide ms와 대조군 ms를 비교하는 함수가 들어있다.

'''
대조군인 spectrum_1에서 p0_mz와 일치하는 peak를 찾아내는 함수이다.
_error_range만큼의 오차를 허용한다.
'''


def find_peak(p0_mz, spectrum_1, _error_range):
    e = float(_error_range)

    p0_mz = float(p0_mz)

    start = 0
    end = len(spectrum_1)

    while start <= end:
        mid = int((start + end) / 2)

        if mid >= len(spectrum_1):
            break

        if start < 0:
            break

        f1 = False
        f2 = False

        mz = float(spectrum_1[mid][0])
        f1 = (float(mz) <= float(p0_mz + e))

        f2 = (float(mz) >= float(p0_mz - e))

        if f1 and f2:
            return True

        if mz > p0_mz:
            end = mid - 1

        if mz < p0_mz:
            start = mid + 1

    return False


def get_spectrum(p):
    return p[3]


def classify_peaks(p0, p1, _error_range):
    # array to return
    gray = np.empty((0, 2), float)
    blue = np.empty((0, 2), float)

    error_range = _error_range

    spectrum_0 = get_spectrum(p0)
    spectrum_1 = get_spectrum(p1)

    num_of_peaks = len(spectrum_0)

    for i in range(0, num_of_peaks):
        cur_mz = spectrum_0[i][0]
        cur_intensity = spectrum_0[i][1]

        if find_peak(cur_mz, spectrum_1, error_range):
            blue = np.append(blue, np.array([[cur_mz, cur_intensity]]), axis=0)
        else:
            gray = np.append(gray, np.array([[cur_mz, cur_intensity]]), axis=0)

    print(len(spectrum_0))
    print(len(blue))
    print(len(gray))
    return [blue, gray]