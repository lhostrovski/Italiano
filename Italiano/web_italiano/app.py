from flask import Flask, render_template, jsonify, request
import os
import pyttsx3
import threading

app = Flask(__name__)

# Caminhos para os arquivos de frases
FRASAS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frases.txt')
TRADUCOES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frases_traduzidas.txt')

def ler_frases():
    if not os.path.exists(FRASAS_PATH) or not os.path.exists(TRADUCOES_PATH):
        return [], []
    
    # Lê frases em italiano
    with open(FRASAS_PATH, encoding='utf-8') as f:
        linhas_italiano = f.readlines()
    
    # Lê traduções em português
    with open(TRADUCOES_PATH, encoding='utf-8') as f:
        linhas_portugues = f.readlines()
    
    frases_italiano = []
    frases_portugues = []
    
    # Processa as frases em italiano
    for linha in linhas_italiano:
        frase = linha.strip()
        if frase:
            # Remove número da frente, se houver
            frase = frase.split(' ', 1)[-1]
            frases_italiano.append(frase)
    
    # Processa as traduções em português
    for linha in linhas_portugues:
        frase = linha.strip()
        if frase:
            # Remove número da frente, se houver
            frase = frase.split(' ', 1)[-1]
            frases_portugues.append(frase)
    
    # Garante que temos o mesmo número de frases em ambos os idiomas
    min_len = min(len(frases_italiano), len(frases_portugues))
    return frases_italiano[:min_len], frases_portugues[:min_len]

frases_italiano, frases_portugues = ler_frases()

@app.route('/')
def index():
    return render_template('index.html', total_frases=len(frases_italiano))

@app.route('/get_frase/<int:num>')
def get_frase(num):
    if num < 1 or num > len(frases_italiano):
        return jsonify({'error': f'Número fora do intervalo permitido (1 a {len(frases_italiano)})'})
    frase_italiano = frases_italiano[num-1]
    frase_portugues = frases_portugues[num-1]
    return jsonify({
        'frase_portugues': frase_portugues,
        'frase_italiano': frase_italiano
    })

@app.route('/falar_italiano/<int:num>')
def falar_italiano(num):
    if num < 1 or num > len(frases_italiano):
        return jsonify({'error': 'Número de frase inválido'})
    
    frase = frases_italiano[num-1]
    
    def falar():
        engine = pyttsx3.init()
        # Procura por voz em italiano
        voz_italiana = None
        for voz in engine.getProperty('voices'):
            if 'italian' in voz.name.lower() or 'it' in voz.id.lower():
                voz_italiana = voz.id
                break
        if voz_italiana:
            engine.setProperty('voice', voz_italiana)
        engine.setProperty('rate', 150)  # Velocidade um pouco mais lenta para melhor compreensão
        engine.say(frase)
        engine.runAndWait()
    
    # Executa a síntese de voz em uma thread separada para não bloquear a resposta
    thread = threading.Thread(target=falar)
    thread.start()
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)