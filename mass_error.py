import matplotlib.pyplot as plt
import spectrum_utils.plot as sup
import spectrum_utils.spectrum as sus

def find_matching_mz(observed_mz, theoretical_mz, tolerance=0.5):
    matching_mz = []
    mirror_mz = []

    for mz_theoretical in theoretical_mz:
        for mz_observed in observed_mz:
            if abs(mz_observed - mz_theoretical) <= tolerance:
                matching_mz.append(mz_observed)
                mirror_mz.append(mz_theoretical)
                break
    
    return matching_mz, mirror_mz

def plot_mass_error(spectrum_top, spectrum_bottom):
    observed_mz = spectrum_top.mz  # 관찰된 스펙트럼의 m/z 정보
    observed_intensity = spectrum_top.intensity  # 관찰된 스펙트럼의 intensity 정보
    theoretical_mz = spectrum_bottom.mz  # 이론 스펙트럼의 m/z 정보
    theoretical_intensity = spectrum_bottom.intensity  # 이론 스펙트럼의 intensity 정보

    matching_mz, mirror_mz = find_matching_mz(observed_mz, theoretical_mz)
    print(matching_mz)
    print(mirror_mz)

    # mass error 계산
    mass_errors = [abs(x - y) for x, y in zip(matching_mz, mirror_mz)]
    print(mass_errors)

    fig, ax = plt.subplots(figsize=(10.5, 3))
    # sup.mass_errors(mass_errors, plot_unknown=False, ax=ax)
    ax.scatter(matching_mz, mass_errors, s=5, c='blue')  # m/z를 x축으로 사용
    ax.set_xlabel('m/z')
    ax.set_ylabel('Mass Error (Da)')
    ax.set_title('Mass Error Plot')

    ax.set_yticks([i * 0.01 for i in range(-4, 5)])
    ax.set_ylim(-0.5, 0.5)

    plt.show()
