# sequence에 끼어있는 [+57.021]과 같은 부분을 제거
def remove_modifications(seq : str) -> str:
    modi = ''
    rslt = seq[:]
    for i in range(len(seq)):
        if seq[i] == '[' or seq[i].isdigit() or seq[i] == '.' or seq[i] == '-' or seq[i] == '+':
            modi += seq[i]
        elif seq[i] == ']':
            modi += seq[i]
            rslt = rslt.replace(modi, '')
            modi = ''
    return rslt

# AAC+57.021CA.. 와 같이 질량이 더하거나 빼진 부분을 []로 감싸기
def brace_modifications(seq : str) -> str:
    modi = ''
    processed = []
    rslt = seq[:]
    for i in range(len(seq)):
        if seq[i] == '+' or seq[i] == '-' or seq[i] == '.' or seq[i].isdigit():
            modi += seq[i]
        elif len(modi) and modi not in processed:
            rslt = rslt.replace(modi, '['+modi+']')
            m = modi[:]
            processed.append(m)
            modi = ''
        elif len(modi) and modi in processed:
            modi = ''

    if modi and modi not in processed:
        rslt = rslt.replace(modi, '['+modi+']')

    return rslt


def process_text(text : str) : # AC+57.021AAC
    residue = ""
    rslt = []
    for amino in text:
        if amino == '+' or amino == '-' or amino == '.' or amino.isdigit():
            residue += amino
        else: # alphabet
            if len(residue):
                rslt.append(residue[:])
            
            residue = ""
            residue += amino
    
    if len(residue):
        rslt.append(residue)
    return rslt

