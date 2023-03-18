# title = []
# charge = []
# pep_mass = []
# scans = []
# seq = []
#
# seq_len = []    # 각 sequence의 길이를 저장하는 list
# pep_info = []   # 각 peptide의 정보 [title, charge, pep_mass, scans, seq, x, y] 저장하는 list
import pandas as pd

filename = 'c:\\Users\\somso\\Documents\\hyu\\4_1\\MS_GUI_PROJECT\\draw\\toy.mgf'
# filename = 'MS_GUI_PROJECT/draw/toy.mgf'


with open(filename) as f:
    lines = f.read().splitlines()

line_len = len(lines)

data = [' ' for i in range(5)]   # 작은 list
newlist = []
flag = True
idx = 0     # 큰 list의 index

while idx < line_len - 1:
    x = []
    y = []
    while flag:
        if lines[idx] == '':
            idx += 1
            if idx == line_len:
                flag = False

        elif lines[idx] == 'BEGIN IONS':
            idx += 1
        elif lines[idx][0] == 'T':
            split_str = lines[idx].split('=')
            data[0] = split_str[1]
            idx += 1
        elif lines[idx][0] == 'C':
            split_str = lines[idx].split('=')
            data[1] = split_str[1]
            idx += 1
        elif lines[idx][0] == 'P':
            split_str = lines[idx].split('=')
            data[2] = split_str[1]
            idx += 1
        elif lines[idx][0] == 'S':
            split_str = lines[idx].split('=')
            if split_str[0] == 'SCANS':
                data[3] = split_str[1]
            if split_str[0] == 'SEQ':
                data[4] = split_str[1]
            idx += 1
        elif lines[idx] == 'END IONS':
            idx += 1
            flag = False
        else:
            split_xy = lines[idx].split(' ')
            x.append(split_xy[0])
            y.append(split_xy[1])

            # data.append(lines[idx])
            idx += 1

    data.append(x)
    data.append(y)
    newlist.append(data)
    data = [' ' for i in range(5)]   # 다시 빈 list로 만들어주기
    flag = True

def return_data():
    # print(newlist)
    return convert_to_dataframe(newlist)


def print_data():
    list = return_data()

    for i in range(len(list)):
        print(len(list[i]))
        print(list[i][0])
        print(list[i][1])

#Title, charge, pepmass, scan, seq, x, y
def convert_to_dataframe(data_list):
    title_list, charge_list, pepmass_list, scan_list, seq_list, x_list, y_list = [],[],[],[],[],[],[]
    print(len(data_list))
    for i in range (0, len(data_list)):
        title_list.append(data_list[i][0])
        charge_list.append(data_list[i][1])
        pepmass_list.append(data_list[i][2])
        scan_list.append(data_list[i][3])
        seq_list.append(data_list[i][4])
        x_list.append(data_list[i][5])
        y_list.append(data_list[i][6])

    data = {
        'title': title_list,
        'charge': charge_list,
        'pepmass': pepmass_list,
        'scan': scan_list,
        'seq': seq_list,
        'm/z': x_list,
        'intensity': y_list,
    }

    return data
    # df = pd.DataFrame(data)
    # print(df)



# convert_to_dataframe(newlist)