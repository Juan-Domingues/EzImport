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
        
        # Aqui você pode chamar um script específico se necessário
        # Por exemplo, você pode passar o caminho do arquivo para o script
        # subprocess.run(['python', 'backend/seu_script.py', file_path], check=True)

    return redirect(url_for('index'))

@app.route('/run_script/<script_name>', methods=['POST'])
def run_script(script_name):
    script_path = os.path.join('backend', script_name)
    try:
        subprocess.run(['python', script_path], check=True)
        return f"Script {script_name} executado com sucesso!", 200
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o script {script_name}: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
