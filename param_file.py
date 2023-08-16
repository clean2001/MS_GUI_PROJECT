# foo.params 파일 생성하는 함수 (query별로)
def make_parameter_file(
    query_file, target_lib_file, decoy_lib_file, pept_tol_value, 
    isotope_tol_value_min, isotope_tol_value_max, frag_tol_value, index):
    
    # query_file_paths = '\n'.join([f'Spectra= {query_file}' for query_file in query_file_list])
    
    params_content = f"""\
# Spectra=[FILENAME]
# Specifies path to the spectra file or directory to search
# Supported formats: *.mgf, *.pkl, *.dta, *.ms2, *mzXML, *mzML 
# Given a directory, all spectra files in it are searched.
Spectra= {query_file}

# TargetLib=[FILENAME]
# Specifies path to the target spectral library file to search
TargetLib= {target_lib_file}

# DecoyLib=[FILENAME]
# For FDR estimation, specifies path to the decoy spectral library file to search
DecoyLib= {decoy_lib_file}

# PeptTolerance=[VALUE]
# Sets a precursor mass tolerance in ppm. (Default value is 10)
PeptTolerance= {pept_tol_value}

# C13Isotope=[MIN],[MAX]
# Sets the numbers of C13 (or isotope error) allowed in peptide masses. (Default values are 0,2)
# 1.00235 Da is used as an isotope spacing
C13Isotope= {isotope_tol_value_min},{isotope_tol_value_max}

# FragTolerance=[MASS]
# Sets a fragment ion mass tolerance in dalton. (Default value is 0.02)
FragTolerance= {frag_tol_value}
        """
    
    # index별로 파일 생성
    params_filename = f'./deephos/foo{index}.params'
    
    with open(params_filename, 'w') as params_file:
        params_file.write(params_content)
    