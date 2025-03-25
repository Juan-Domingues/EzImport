from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
import pyodbc
import pandas as pd

app = Flask(__name__)

# Variáveis de conexão
server = 'SQL19BICR\\SQL19BI,61161'
database = 'RevenueManagement'
username = 'job.revenue'
password = 'Job@r3v3nu3'

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

@app.route('/run_update_table', methods=['POST'])
def run_update_table():
    try:
        # Ler o caminho do arquivo salvo
        with open('uploads/last_uploaded_file.txt', 'r') as f:
            file_path = f.read().strip()

        # Nome da tabela baseado no nome do arquivo de upload
        file_name = os.path.basename(file_path)
        table_name = f'dbo.Tb_{file_name.split(".")[0]}'

        # Conectar ao banco de dados
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        cursor = conn.cursor()

        # Ler o arquivo de upload em um DataFrame do Pandas
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return f"Formato de arquivo não suportado", 400

        # Criar a tabela se ela não existir
        columns = ', '.join([f"{col} NVARCHAR(MAX)" for col in df.columns])
        create_table_query = f"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name.split('.')[1]}' AND xtype='U') CREATE TABLE {table_name} ({columns})"
        cursor.execute(create_table_query)

        # Atualizar a tabela no banco de dados
        for index, row in df.iterrows():
            columns = ', '.join(row.index)
            values = ', '.join([f"'{str(value)}'" for value in row.values])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            cursor.execute(query)

        # Commit e fechar a conexão
        conn.commit()
        cursor.close()
        conn.close()
        return f"Tabela {table_name} atualizada com sucesso!", 200
    except Exception as e:
        return f"Erro ao atualizar a tabela: {str(e)}", 500

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
    try:
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
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
    try:
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
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
