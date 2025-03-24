import sys
import pandas as pd
import pyodbc
import os

# Conexão com o banco de dados
def connect_to_db(server, database, username, password):
    conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER= {server};DATABASE={database};UID={username};PWD={password}'
    )
    return conn

#Função para carregar novos dados
def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file_path)
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(file_path)
    elif ext == '.json':
        return pd.read_json(file_path)
    elif ext == '.parquet':
        return pd.read_parquet(file_path)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {ext}")

# Função para atualizar tabela
def update_table_with_new_data(conn, table_name, new_data):
    cursor = conn.cursor()

    for index, row in new_data.iterrows():
        #Cria a consulta para atualizar
        columns = ','.join(new_data.columns)
        values = ','.join([f" ' {row[col]}' " for col in new_data.columns])
        update_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        try:
            cursor.execute(update_query)
        except Exception as e:
            print(f"Erro ao atualizar tabela: {e}")
            return
    
    conn.commit()

#Definições de conexão de tabela
server = 'SQL19BICR\\SQL19BI,61161'
database = 'RevenueManagement'
username = 'job.revenue'
password = 'Job@r3v3nu3'
table_name = 'dbo.Tb_teste_import'
file_path = sys.argv[1]

#Conecta ao banco de dados
conn = connect_to_db(server, database, username, password)

#Carrega novos dados
new_data = read_file(file_path)

#Atualiza tabela com novos dados
update_table_with_new_data(conn, table_name, new_data)

#Encerrar conexão
conn.close()