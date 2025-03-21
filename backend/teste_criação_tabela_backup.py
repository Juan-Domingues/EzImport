import pandas as pd
import pyodbc
from datetime import datetime

# Conexão com o banco de dados
def connect_to_db(server, database, username, password):
    conn = pyodbc.connect(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER= {server};DATABASE={database};UID={username};PWD={password}'
    )
    return conn
    

# Criação de dataframe apartir da tabela do banco de dados
def create_dataframe_from_table(conn, table_name):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    return df

# Obter o tipo das colunas apartir do dataframe
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

# Função para criar tabela de backup apartir dos dados do dataframe
def create_table_from_dataframe(conn, df, new_table_name):
    cursor = conn.cursor()

    #Verifica se a tabela já existe
    drop_table_query = f"IF OBJECT_ID('{new_table_name}', 'U') IS NOT NULL DROP TABLE {new_table_name}"
    cursor.execute(drop_table_query)
    conn.commit()

    #Cria tabela
    columns = ','.join([f'{col} {get_sql_type(dtype)}' for col, dtype in df.dtypes.items()])
    create_table_query = f"CREATE TABLE {new_table_name} ({columns})"

    #Adiciona uma impressão para depuração
    print(f"Create Table Query: {create_table_query}")

    try:
        cursor.execute(create_table_query)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        return

    #Inserir os dados do backup salvo
    for index, row in df.iterrows():
        insert_query = f"INSERT INTO {new_table_name} VALUES ("
        for col in df.columns:
            insert_query += f"'{row[col]}',"
        insert_query = insert_query.rstrip(',') + ')'
        cursor.execute(insert_query)
    conn.commit()

#Definições de conexão de tabela
server = 'SQL19BICR\\SQL19BI,61161'
database = 'RevenueManagement'
username = 'job.revenue'
password = 'Job@r3v3nu3'
table_name = 'dbo.Tb_teste_import'

#Conecta ao banco de dados
conn = connect_to_db(server, database, username, password)

#Cria um Dataframe a partir da tabela
df = create_dataframe_from_table(conn, table_name)

#Define o nome da nova tabela
today_date = datetime.now().strftime('%Y%m%d')
new_table_name = f"{table_name}_backup_{today_date}"

#Cria a nova tabela e insere os dados
create_table_from_dataframe(conn, df, new_table_name)

#Encerrar conexão
conn.close()



    
    
    


