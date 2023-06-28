# data frame 형식으로 table 만들기
import pandas as pd
import custom_widgets

# global 변수로 놓기
Proton = 1.007276035
H20 = 18.0105647

# amino_acid = pd.read_html('aaTable.mht', header=0, encoding='utf-8')
# print(amino_acid)

# IonSource Amino Acid Table 만들기
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

# y이온과 b이온 만들기
# B-ion = Sum of Amino acids + Proton
# Y-ion = Sum of Amino acids + H2O + Proton

# 각 SEQUENCE를 하나씩자르기
# 예시로 하나 가져오기
seq = 'PVTTPEEIAQVATISANGDK'
seq_list = list(seq)
sum_of_amino_acids_mono = 0
sum_of_amino_acids_avg = 0

# print(amino_acid_table['AA Codes_2'])

row = amino_acid.loc[amino_acid['AA Codes_2'] == 'S']
# print(row)
# print(row['Mono.'].values[0])

for i in seq_list:
    row = amino_acid.loc[amino_acid['AA Codes_2'] == 'S']
    sum_of_amino_acids_mono += row['Mono.'].values[0]
    sum_of_amino_acids_avg += row['Avg.'].values[0]

# print(sum_of_amino_acids_mono)
# print(sum_of_amino_acids_avg)

# Mono. 로 계산 한것
B_ion = sum_of_amino_acids_mono + Proton
Y_ion = sum_of_amino_acids_mono + H20 + Proton

print(B_ion)
print(Y_ion)

# Avg. 로 계산 한 것
B_ion_avg = sum_of_amino_acids_avg + Proton
Y_ion_avg = sum_of_amino_acids_avg + H20 + Proton

print(B_ion_avg)
print(Y_ion_avg)

# custom_wideget에 있는 parsing한 file에서 title~y값까지 각각 리스트로 반환한 것을
# 여기로 불러와서 일반화 시켜야됨