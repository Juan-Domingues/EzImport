import pyodbc
import pandas as pd
import sys
import os

# Variáveis de conexão
server = 'SQL19BICR\\SQL19BI,61161'
database = 'RevenueManagement'
username = 'job.revenue'
password = 'Job@r3v3nu3'

# Caminho do arquivo de upload
file_path = sys.argv[1]

# Nome da tabela baseado no nome do arquivo de upload
file_name = os.path.basename(file_path)
table_name = f'dbo.{file_name.split(".")[0]}'

try:
    # Conectar ao banco de dados
    conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    cursor = conn.cursor()

    # Ler o arquivo de upload em um DataFrame do Pandas
    if file_name.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_name.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError('Formato de arquivo não suportado')

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
except Exception as e:
    print(f"Erro ao atualizar a tabela: {str(e)}")
    sys.exit(1)
