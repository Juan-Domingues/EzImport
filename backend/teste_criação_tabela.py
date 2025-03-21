import pandas as pd
import pyodbc
import os

# leitura do arquivo CSV
file_paths = ['C:\\Users\\juan.domingues\\OneDrive - Azul Linhas Aéreas\\Desktop\\teste pyimport\\teste_import.csv']

# Loop para ler o formato dos arquivos
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

for file_path in file_paths:
    df = read_file(file_path)

#obter nome do arquivo sem extensão 
file_name = os.path.splitext(os.path.basename(file_path))[0]

#Padroniza o nome da tabela
table_name = f'dbo.Tb_{file_name}'

#Loop para definir o tipo das colunas no sql
def get_sql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BIT'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'DATETIME'
    else:
        return 'VARCHAR(MAX)'

columns = ','.join([f'{col} {get_sql_type(dtype)}' for col, dtype in df.dtypes.items()])

#Estabeleça conexão via pyodbc
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};' 
    'SERVER= SQL19BICR\\SQL19BI,61161;'
    'DATABASE=RevenueManagement;'
    'UID=job.revenue;'
    'PWD=Job@r3v3nu3;'
)
cursor = conn.cursor()

#Gerar String que cria tabela
create_table_query = f'CREATE TABLE {table_name} ({columns})'

#Executar a criação
cursor.execute(create_table_query)
conn.commit()

#Inserir os dados
for index, row in df.iterrows():
    values = ','.join([f"'{str(value).replace('\'', '\'\'')}'" for value in row])
    insert_query = f'INSERT INTO {table_name} VALUES ({values})'
    cursor.execute(insert_query)
    conn.commit()

cursor.close()
conn.close()
