import matplotlib.pyplot as plt
import mass_plot as mp
import spectrum_utils.spectrum as sus

def mass_error_plot(spectrum_top, spectrum_bottom):
    ## spectrum_utils 라이브러리(mp)의 mass_errors 함수 적용
    fig = mp.facet(
        spec_top=spectrum_top,
        spec_mass_errors=spectrum_top,
        spec_bottom=spectrum_bottom,
        mass_errors_kws={"plot_unknown": False},
        height=15,
        width=9,
    )   
    
    return fig
