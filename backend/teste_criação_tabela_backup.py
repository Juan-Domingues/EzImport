import sys
import pyodbc
from datetime import datetime

def backup_table(table_name, server, database, uid, pwd):
    conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={uid};PWD={pwd}')
    cursor = conn.cursor()

    today = datetime.today().strftime('%Y%m%d')
    backup_table_name = f"{table_name}_backup_{today}"
    cursor.execute(f"SELECT * INTO {backup_table_name} FROM {table_name}")
    conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    table_name = sys.argv[1]
    server = 'SQL19BICR\\SQL19BI,61161'
    database = 'RevenueManagement'
    uid = 'job.revenue'
    pwd = 'Job@r3v3nu3'
    backup_table(table_name, server, database, uid, pwd)