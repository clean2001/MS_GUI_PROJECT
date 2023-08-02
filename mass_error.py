import matplotlib.pyplot as plt
# import spectrum_utils.plot as sup
# import spectrum_plot as sup
import mass_plot as mp
import spectrum_utils.spectrum as sus

def mass_error_plot(spectrum_top):
    ## spectrum_utils 라이브러리(mp)의 mass_errors 함수 적용
    fig, ax = plt.subplots(figsize=(10.5, 4))
    mp.mass_errors(spectrum_top, plot_unknown=False, ax=ax)
    plt.show()
    # plt.close()