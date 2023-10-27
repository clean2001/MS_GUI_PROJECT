# foo.params 파일 생성하는 함수 (query별로)
def make_parameter_file(
    project_file:str, query_file:list, target_lib_file:list, decoy_lib_file:list, pept_tol_value, 
    isotope_tol_value_min, isotope_tol_value_max, frag_tol_value, make_decoy: int):
   
    params_content = "Project=" + project_file + "\n"
    for query in query_file:
        params_content += "Spectra=" + query + "\n"
    
    for target in target_lib_file:
        params_content += "TargetLib=" + target + "\n"
    
    params_content += "MakeDecoy=" + str(make_decoy) + "\n"

    for decoy in decoy_lib_file:
        params_content += "DecoyLib=" + decoy + "\n"

    params_content += "PeptTolerance=" + str(pept_tol_value) + "\n"
    params_content += "C13Isotope=" + str(isotope_tol_value_min) + "," + str(isotope_tol_value_max) + "\n"
    params_content += "FragTolerance=" + str(frag_tol_value) + "\n"
    
    # index별로 파일 생성
    params_filename = './deephos/foo.params'
    
    with open(params_filename, 'w') as params_file:
        params_file.write(params_content)
    