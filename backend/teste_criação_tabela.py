import pandas as pd
import pyodbc
import os

# Lista de arquivos para processar
file_paths = ['C:\\Users\\juan.domingues\\OneDrive - Azul Linhas Aéreas\\Desktop\\teste pyimport\\teste_import.csv']  

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

    # Obter o nome do arquivo sem a extensão
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    # Padronizar o nome da tabela
    table_name = f'dbo.tb{file_name}'

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

    columns = ', '.join([f'{col} {get_sql_type(dtype)}' for col, dtype in df.dtypes.items()])

    conn = pyodbc.connect('DRIVER={SQL Server};'
                          'SERVER=seu_servidor;'
                          'DATABASE=seu_banco_de_dados;'
                          'UID=seu_usuario;'
                          'PWD=sua_senha')
    cursor = conn.cursor()

    create_table_query = f'CREATE TABLE {table_name} ({columns})'
    cursor.execute(create_table_query)
    conn.commit()

    for index, row in df.iterrows():
        values = ', '.join([f"'{str(value).replace('\'', '\'\'')}'" for value in row])
        insert_query = f'INSERT INTO {table_name} VALUES ({values})'
        cursor.execute(insert_query)
        conn.commit()

    cursor.close()
    conn.close()
