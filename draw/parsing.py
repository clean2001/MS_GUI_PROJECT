filename = 'toy.mgf'

with open(filename) as f:
    lines = f.read().splitlines()

line_len = len(lines)

data = []   # 작은 list
newlist = []
flag = True
idx = 0     # 큰 list의 index

while idx < line_len - 1:
    while flag:
        if lines[idx] == '':
            idx += 1
            if idx == line_len:
                flag = False

        elif lines[idx] == 'BEGIN IONS':
            idx += 1
        elif lines[idx][0] == 'T':
            split_str = lines[idx].split('=')
            data.append(split_str[1])
            idx += 1
        elif lines[idx][0] == 'C':
            split_str = lines[idx].split('=')
            data.append(split_str[1])
            idx += 1
        elif lines[idx][0] == 'P':
            split_str = lines[idx].split('=')
            data.append(split_str[1])
            idx += 1
        elif lines[idx][0] == 'S':
            split_str = lines[idx].split('=')
            data.append(split_str[1])
            idx += 1
        elif lines[idx] == 'END IONS':
            idx += 1
            flag = False
        else:
            data.append(lines[idx])
            idx += 1

    newlist.append(data)
    data = []   # 다시 빈 list로 만들어주기
    flag = True