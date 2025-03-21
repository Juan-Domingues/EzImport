from flask import Flask, request, render_template, redirect, url_for
import os
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join('uploads', uploaded_file.filename)
        uploaded_file.save(file_path)
        
        # Salvar o caminho do arquivo em uma variável de sessão ou em um arquivo temporário
        with open('uploads/last_uploaded_file.txt', 'w') as f:
            f.write(file_path)

    return redirect(url_for('index'))

@app.route('/run_script/<script_name>', methods=['POST'])
def run_script(script_name):
    # Ler o caminho do arquivo salvo
    with open('uploads/last_uploaded_file.txt', 'r') as f:
        file_path = f.read().strip()
    
    script_path = os.path.join('backend', script_name)
    try:
        subprocess.run(['python', script_path, file_path], check=True)
        return f"Script {script_name} executado com sucesso!", 200
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o script {script_name}: {str(e)}", 500

@app.route('/run_backup_script/<table_name>', methods=['POST'])
def run_backup_script(table_name):
    script_path = os.path.join('backend', 'teste_criação_tabela_backup.py')
    try:
        subprocess.run(['python', script_path, table_name], check=True)
        return f"Backup da tabela {table_name} executado com sucesso!", 200
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o backup da tabela {table_name}: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
