import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import csv

def escolher_arquivo():
    caminho = filedialog.askopenfilename(title='Escolha o arquivo', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
    if caminho:
        arquivo_var.set(caminho)
        resultado_var.set('Arquivo selecionado!')

def processar_arquivo():
    caminho = arquivo_var.get()
    if not caminho or not os.path.isfile(caminho):
        messagebox.showerror('Erro', 'Selecione um arquivo válido.')
        return

    try:
        with open(caminho, encoding='utf-8') as f:
            linhas = f.readlines()

        blocos = []
        todas_anteriores = set()
        for i in range(0, len(linhas), 10):
            bloco = linhas[i:i+10]
            texto_bloco = ' '.join(bloco)
            palavras = set(re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', texto_bloco.lower()))
            # Remove palavras já presentes nos blocos anteriores
            palavras_unicas = palavras - todas_anteriores
            blocos.append(sorted(palavras_unicas))
            todas_anteriores.update(palavras_unicas)

        nome_arquivo = os.path.splitext(os.path.basename(caminho))[0]
        caminho_saida = os.path.join(os.path.dirname(caminho), f'{nome_arquivo}_palavrasunicas.csv')
        # Escreve o CSV com encoding utf-8-sig para garantir compatibilidade com acentos
        with open(caminho_saida, 'w', encoding='utf-8-sig', newline='') as fout:
            writer = csv.writer(fout)
            for idx, palavras in enumerate(blocos, start=1):
                writer.writerow([f'Linha {((idx-1)*10)+1}-{min(idx*10, len(linhas))}'] + palavras)

        resultado_var.set(f'Arquivo gerado: {caminho_saida}')
        messagebox.showinfo('Sucesso', f'Arquivo gerado: {caminho_saida}')
    except Exception as e:
        resultado_var.set(f'Erro: {e}')
        messagebox.showerror('Erro', f'Erro ao processar arquivo: {e}')

root = tk.Tk()
root.title('Listagem de Palavras Únicas por Bloco')
root.geometry('600x200')

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill='both', expand=True)

arquivo_var = tk.StringVar()
resultado_var = tk.StringVar()

btn_escolher = ttk.Button(main_frame, text='Escolher arquivo', command=escolher_arquivo)
btn_escolher.grid(row=0, column=0, padx=5, pady=5)

arquivo_entry = ttk.Entry(main_frame, textvariable=arquivo_var, width=50, state='readonly')
arquivo_entry.grid(row=0, column=1, padx=5, pady=5)

btn_processar = ttk.Button(main_frame, text='Gerar listagem de palavras únicas', command=processar_arquivo)
btn_processar.grid(row=1, column=0, columnspan=2, pady=15)

resultado_label = ttk.Label(main_frame, textvariable=resultado_var, font=('Arial', 12))
resultado_label.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()