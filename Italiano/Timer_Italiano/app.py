from flask import Flask, render_template, request, jsonify
import pandas as pd
import random
import os
from datetime import datetime

app = Flask(__name__)

def load_phrases():
    # Read phrases from files
    phrases_dir = os.path.join(os.path.dirname(__file__), '..')
    with open(os.path.join(phrases_dir, 'frases.txt'), 'r', encoding='utf-8') as f:
        italian_phrases = f.read().splitlines()
    with open(os.path.join(phrases_dir, 'frases_traduzidas.txt'), 'r', encoding='utf-8') as f:
        portuguese_phrases = f.read().splitlines()
    
    # Initialize or load CSV database
    csv_path = os.path.join(os.path.dirname(__file__), 'banco.csv')
    if not os.path.exists(csv_path):
        # Criar novo DataFrame apenas se o arquivo não existir
        df = pd.DataFrame({
            'ID': range(1, len(portuguese_phrases) + 1),
            'Frase_PT': portuguese_phrases,
            'Frase_IT': italian_phrases,
            'Score': [0] * len(portuguese_phrases)  # Score inicial 0 apenas para novas frases
        })
    else:
        # Carregar dados existentes mantendo os Scores
        df = pd.read_csv(csv_path)
        # Adicionar coluna Score se não existir
        if 'Score' not in df.columns:
            df['Score'] = df['Score'].fillna(0)
        
        # Check if there are new phrases to add
        total_phrases = len(portuguese_phrases)
        current_phrases = len(df)
        
        if total_phrases > current_phrases:
            # Add new phrases
            new_phrases_df = pd.DataFrame({
                'ID': range(current_phrases + 1, total_phrases + 1),
                'Frase_PT': portuguese_phrases[current_phrases:],
                'Frase_IT': italian_phrases[current_phrases:],
                'Score': [0] * (total_phrases - current_phrases)
            })
            df = pd.concat([df, new_phrases_df], ignore_index=True)
    
    # Make sure Score is numeric
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0).astype(int)
    
    # Save any changes made
    df.to_csv(csv_path, index=False)
    return df

def select_phrase(df):
    # Identify phrases that need more practice (Score <= 0)
    need_practice = df[df['Score'] <= 0]
    
    # Apply 70/30 rule:
    # 70% chance to select a phrase with low score (<=0)
    # 30% chance to select any phrase
    if random.random() < 0.7 and not need_practice.empty:
        selected = need_practice.sample(n=1).iloc[0]
    else:
        selected = df.sample(n=1).iloc[0]
    
    return selected

def calculate_timer(phrase):
    # Calculate time based on word count (1s per word + 5s extra)
    word_count = len(phrase.split())
    return word_count + 5

@app.route('/')
def index():
    df = load_phrases()
    total_phrases = len(df)
    return render_template('index.html', total_phrases=total_phrases)

@app.route('/get_phrase', methods=['POST'])
def get_phrase():
    start_phrase = int(request.form.get('start_phrase'))
    end_phrase = int(request.form.get('end_phrase'))
    df = load_phrases()
    
    # Filter by phrase range
    df_filtered = df[(df['ID'] >= start_phrase) & (df['ID'] <= end_phrase)]
    
    if df_filtered.empty:
        return jsonify({'error': 'No phrases available'})
    
    phrase = select_phrase(df_filtered)
    timer_seconds = calculate_timer(phrase['Frase_PT'])
    
    return jsonify({
        'id': int(phrase['ID']),
        'portuguese': phrase['Frase_PT'],
        'italian': phrase['Frase_IT'],
        'timer': timer_seconds
    })

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    phrase_id = data.get('id')
    score_change = int(data.get('scoreChange'))  # Convert to integer
    csv_path = os.path.join(os.path.dirname(__file__), 'banco.csv')
    df = pd.read_csv(csv_path)
    
    # Ensure Score column is numeric
    df['Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0).astype(int)
    
    # Update the score by adding the score_change (+1 or -1)
    mask = df['ID'] == phrase_id

    if mask.any():
        current_score = df.loc[mask, 'Score'].iloc[0]
        new_score = current_score + score_change
        df.loc[mask, 'Score'] = new_score
        
        
    try:
        # Forçar tipo inteiro na coluna Score antes de salvar
        df['Score'] = df['Score'].astype(int)
        # Salvar com modo de escrita explícito e encoding específico
        df.to_csv(csv_path, index=False, mode='w', encoding='utf-8')
        print(f"Arquivo salvo em: {csv_path}")
        # Verificar se salvou lendo o arquivo novamente
        df_check = pd.read_csv(csv_path)
        
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
