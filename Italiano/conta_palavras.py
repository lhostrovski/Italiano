import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import os

def escolher_arquivo():
    caminho = filedialog.askopenfilename(title='Escolha o arquivo', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
    if caminho:
        arquivo_var.set(caminho)
        resultado_var.set('')

def contar_palavras():
    caminho = arquivo_var.get()
    if not caminho or not os.path.isfile(caminho):
        messagebox.showerror('Erro', 'Selecione um arquivo válido.')
        return
    try:
        with open(caminho, encoding='utf-8') as f:
            texto = f.read()
        # Remove números e pontuação, deixa só letras
        palavras = re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', texto)
        diferentes = set(p.lower() for p in palavras)
        resultado_var.set(f'{len(diferentes)} palavras diferentes')

        # Salva as palavras únicas em palavrasunicas.txt no mesmo diretório
        dir_arquivo = os.path.dirname(caminho)
        caminho_saida = os.path.join(dir_arquivo, 'palavrasunicas.txt')
        with open(caminho_saida, 'w', encoding='utf-8') as fout:
            for palavra in sorted(diferentes):
                fout.write(palavra + '\n')
    except Exception as e:
        resultado_var.set(f'Erro: {e}')

# Botão para gerar arquivo de palavras únicas
def gerar_palavras_unicas():
    caminho = arquivo_var.get()
    if not caminho or not os.path.isfile(caminho):
        messagebox.showerror('Erro', 'Selecione um arquivo válido.')
        return
    try:
        with open(caminho, encoding='utf-8') as f:
            texto = f.read()
        palavras = re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', texto)
        diferentes = set(p.lower() for p in palavras)
        nome_arquivo = os.path.splitext(os.path.basename(caminho))[0]
        caminho_saida = os.path.join(os.path.dirname(caminho), f'{nome_arquivo}_palavrasunicas.txt')
        with open(caminho_saida, 'w', encoding='utf-8') as fout:
            for palavra in sorted(diferentes):
                fout.write(palavra + '\n')
        messagebox.showinfo('Sucesso', f'Arquivo gerado: {caminho_saida}')
    except Exception as e:
        messagebox.showerror('Erro', f'Erro ao gerar arquivo: {e}')

root = tk.Tk()
root.title('Contador de Palavras Diferentes')
root.geometry('500x200')

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill='both', expand=True)

arquivo_var = tk.StringVar()
resultado_var = tk.StringVar()

btn_escolher = ttk.Button(main_frame, text='Escolher arquivo', command=escolher_arquivo)
btn_escolher.grid(row=0, column=0, padx=5, pady=5)

arquivo_entry = ttk.Entry(main_frame, textvariable=arquivo_var, width=50, state='readonly')
arquivo_entry.grid(row=0, column=1, padx=5, pady=5)

btn_contar = ttk.Button(main_frame, text='Contar palavras diferentes', command=contar_palavras)
btn_contar.grid(row=1, column=0, columnspan=2, pady=15)

btn_gerar = ttk.Button(main_frame, text='Gerar arquivo de palavras únicas', command=gerar_palavras_unicas)
btn_gerar.grid(row=2, column=0, columnspan=2, pady=5)

resultado_label = ttk.Label(main_frame, textvariable=resultado_var, font=('Arial', 14))
resultado_label.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
