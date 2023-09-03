import matplotlib.pyplot as plt
from help_functions import process_sequence

def draw_nterm_line(myapp, n_terms: list, seq: str, s: int, e: int, n: int):
    for mz in n_terms:
        plt.plot([mz, mz], [s, e], color='blue', linestyle = ':', alpha = 0.5)
        plt.plot([mz, mz], [s, -e], color='blue', linestyle = ':', alpha = 0.5)
    text = process_sequence.process_text(seq)
    for i in range(0, len(n_terms)-1):
        start = n_terms[i]
        end = n_terms[i+1]
        plt.text((start + end)/2 - len(text[i])*7, n, text[i], fontsize=10, color='blue')

def draw_cterm_line(myapp, c_terms: list, seq: str, s: int, e: int, c: int):
    for mz in c_terms:
        plt.plot([mz, mz], [s, e], color='red', linestyle = ':', alpha = 0.5)
        plt.plot([mz, mz], [s, -e], color='red', linestyle = ':', alpha = 0.5)
    text = process_sequence.process_text(seq)
    text = text[::-1]
    for i in range(0, len(c_terms)-1):
        start = c_terms[i]
        end = c_terms[i+1]
        plt.text((start + end)/2 - len(text[i])*7, c, text[i],fontsize=10, color='red')