import sys
import pandas as pd
import pyodbc
import os

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

def create_table_from_file(file_path, server, database, uid, pwd):
    df = read_file(file_path)

    # Obter o nome do arquivo sem a extensão
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    #Padronizar o nome da tabela
    table_name = f'dbo.Tb_{file_name}'

    columns = ', '.join([f'{col} {get_sql_type(dtype)}' for col, dtype in df.dtypes.items()])

    conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={uid};PWD={pwd}')
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

if __name__ == '__main__':
    file_path = sys.argv[1]
    server = 'SQL19BICR\\SQL19BI,61161'
    database = 'RevenueManagement'
    uid = 'job.revenue'
    pwd = 'Job@r3v3nu3'
    create_table_from_file(file_path, server, database, uid, pwd)
