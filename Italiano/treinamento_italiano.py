from googletrans import Translator
import tkinter as tk
from tkinter import ttk, messagebox
import os
import pyttsx3


# Função para ler frases do arquivo
FRASAS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frases.txt')


def ler_frases():
    if not os.path.exists(FRASAS_PATH):
        return ["Arquivo frases.txt não encontrado."]
    with open(FRASAS_PATH, encoding='utf-8') as f:
        linhas = f.readlines()
    frases = []
    for linha in linhas:
        frase = linha.strip()
        if frase:
            # Remove número da frente, se houver
            frase = frase.split(' ', 1)[-1]
            frases.append(frase)
    return frases

frases = ler_frases()

# Função para quebrar frase em duas linhas

def quebra_frase(frase):
    palavras = frase.split()
    meio = len(palavras) // 2
    return ' '.join(palavras[:meio]) + '\n' + ' '.join(palavras[meio:]) if len(palavras) > 4 else frase

# Função para carregar frase

def carregar_frase():
    try:
        num = int(num_var.get())
    except ValueError:
        messagebox.showerror('Erro', 'Digite um número válido entre 1 e 200.')
        return
    if num < 1 or num > len(frases):
        messagebox.showerror('Erro', f'Número fora do intervalo permitido (1 a {len(frases)}).')
        return
    if num > len(frases):
        frase = '(Frase não encontrada)'
    else:
        frase = frases[num-1]
    frase_var.set(frase)  # Sem quebra de linha automática
    # Oculta o texto em italiano e atualiza o botão
    frase_text_oculta.set(True)
    atualizar_frase_texto()
    btn_ocultar.config(text='Desocultar')
    traduzir_frase()

# Função para sintetizar e tocar áudio

def escutar_frase():
    frase = frase_var.get().replace('\n', ' ')
    if not frase or frase.startswith('('):
        messagebox.showerror('Erro', 'Nenhuma frase carregada.')
        return
    engine = pyttsx3.init()
    # Seleciona voz italiana se disponível
    voz_italiana = None
    for voz in engine.getProperty('voices'):
        if 'italian' in voz.name.lower() or 'it' in voz.id.lower():
            voz_italiana = voz.id
            break
    if voz_italiana:
        engine.setProperty('voice', voz_italiana)
    else:
        messagebox.showwarning('Aviso', 'Voz italiana não encontrada. Usando voz padrão.')
    engine.setProperty('rate', 120)
    engine.say(frase)
    engine.runAndWait()

# Funções para navegação

def anterior():
    n = int(num_var.get())
    if n > 1:
        num_var.set(str(n-1))
        carregar_frase()

def proximo():
    n = int(num_var.get())
    if n < len(frases):
        num_var.set(str(n+1))
        # Oculta o texto em italiano e atualiza o botão
        frase_text_oculta.set(True)
        atualizar_frase_texto()
        btn_ocultar.config(text='Desocultar')
        carregar_frase()

# Interface gráfica
root = tk.Tk()
root.title('Treinamento Italiano')
root.geometry('530x350')

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill='both', expand=True)

# Campo de número
num_var = tk.StringVar(value='1')
num_label = ttk.Label(main_frame, text='frase número:')
num_label.grid(row=0, column=0, sticky='e')
num_entry = ttk.Entry(main_frame, textvariable=num_var, width=5)
num_entry.grid(row=0, column=1, sticky='w')
# Faz com que pressionar Enter no campo de número chame carregar_frase
num_entry.bind('<Return>', lambda event: carregar_frase())

btn_carregar = ttk.Button(main_frame, text='Carregar', command=carregar_frase)
btn_carregar.grid(row=0, column=2, padx=10)

btn_ant = ttk.Button(main_frame, text='←', command=anterior)
btn_ant.grid(row=0, column=3, padx=5)
btn_prox = ttk.Button(main_frame, text='→', command=proximo)
btn_prox.grid(row=0, column=4, padx=5)



# Frase exibida (campo selecionável)
frase_var = tk.StringVar()
frase_text = tk.Text(main_frame, font=('Arial', 16), wrap='word', width=40, height=3)
frase_text.grid(row=1, column=0, columnspan=5, pady=30)
frase_text.config(state='disabled')

def atualizar_frase_texto():
    if not frase_text_oculta.get():
        frase_text.config(state='normal')
        frase_text.delete('1.0', tk.END)
        frase_text.insert(tk.END, frase_var.get())
        frase_text.config(state='disabled')
    else:
        frase_text.config(state='normal')
        frase_text.delete('1.0', tk.END)
        frase_text.config(state='disabled')

# Botão para ocultar/desocultar texto
frase_text_oculta = tk.BooleanVar(value=False)
def alternar_ocultar_frase():
    if frase_text_oculta.get():
        frase_text_oculta.set(False)
        atualizar_frase_texto()
        btn_ocultar.config(text='Ocultar')
    else:
        frase_text_oculta.set(True)
        atualizar_frase_texto()
        btn_ocultar.config(text='Desocultar')

btn_ocultar = ttk.Button(main_frame, text='Ocultar', command=alternar_ocultar_frase)
btn_ocultar.grid(row=2, column=0, columnspan=5, pady=(0, 10))


# Botão escutar agora vai para a linha abaixo do botão ocultar
btn_escutar = ttk.Button(main_frame, text='Escutar', command=escutar_frase)
btn_escutar.grid(row=3, column=0, columnspan=5, pady=10)



# Campo e função para tradução
traducao_var = tk.StringVar()

# Lê traduções do arquivo frases_traduzidas.txt
TRADUCOES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frases_traduzidas.txt')
if os.path.exists(TRADUCOES_PATH):
    with open(TRADUCOES_PATH, encoding='utf-8') as f:
        traducoes = [linha.strip() for linha in f.readlines()]
else:
    traducoes = []

def traduzir_frase():
    try:
        num = int(num_var.get())
    except ValueError:
        traducao_var.set('')
        messagebox.showerror('Erro', 'Número de frase inválido.')
        return
    if num < 1 or num > len(traducoes):
        traducao_var.set('Tradução não encontrada.')
        return
    traducao = traducoes[num-1]
    # Remove número e ponto do início, se houver (ex: '12. texto')
    import re
    traducao = re.sub(r'^\s*\d+\s*\.\s*', '', traducao)
    traducao_var.set(traducao)

carregar_frase()



# Campo de tradução na parte inferior (sem botão)
traducao_frame = ttk.Frame(root, padding=10)
traducao_frame.pack(fill='x', side='bottom')
# Substitui Entry por Text para permitir múltiplas linhas
traducao_text = tk.Text(traducao_frame, font=('Arial', 13), width=40, height=2, state='disabled', wrap='word')
traducao_text.pack(side='left', fill='x', expand=True)

def atualizar_traducao_texto(*args):
    traducao_text.config(state='normal')
    traducao_text.delete('1.0', tk.END)
    traducao_text.insert(tk.END, traducao_var.get())
    traducao_text.config(state='disabled')
traducao_var.trace_add('write', atualizar_traducao_texto)

root.mainloop()
