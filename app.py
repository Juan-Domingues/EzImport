from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
import subprocess
import pyodbc

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

@app.route('/clear_uploads', methods=['POST'])
def clear_uploads():
    folder = 'uploads'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            return f"Erro ao limpar uploads: {str(e)}", 500
    return "Uploads limpos com sucesso!", 200

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

@app.route('/delete_table/<table_name>', methods=['POST'])
def delete_table(table_name):
    server = 'SQL19BICR\\SQL19BICR,61161'
    database = 'RevenueManagement'
    uid = 'job.revenue'
    pwd = 'Job@r3v3nu3'
    try:
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={uid};PWD={pwd}')
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE {table_name}")
        conn.commit()
        cursor.close()
        conn.close()
        return f"Tabela {table_name} excluída com sucesso!", 200
    except Exception as e:
        return f"Erro ao excluir a tabela {table_name}: {str(e)}", 500

@app.route('/delete_table_with_query', methods=['POST'])
def delete_table_with_query():
    data = request.get_json()
    query = data.get('query')
    server = 'SQL19BICR\\SQL19BICR,61161'
    database = 'RevenueManagement'
    uid = 'job.revenue'
    pwd = 'Job@r3v3nu3'
    try:
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={uid};PWD={pwd}')
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        return "Query de exclusão executada com sucesso!", 200
    except Exception as e:
        return f"Erro ao executar a query: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
