import mysql.connector
from db_connection_config import HOST, USER, PASSWORD, DATABASE

###########################
# Database Connection
def get_db_connection():
    connection = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE)
    return connection

def fetch_query_results(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def execute_query(query, params=None):
    connection = get_db_connection()
    cursor = connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()

