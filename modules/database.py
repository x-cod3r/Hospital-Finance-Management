import sqlite3
import os

DB_CONNECTIONS = {}

def get_db_connection(db_name):
    """
    Returns a database connection. If a connection to the database
    already exists, the existing connection is returned. Otherwise, a new
    connection is created and stored in the DB_CONNECONNECTIONS dictionary.
    """
    if db_name not in DB_CONNECTIONS:
        db_path = os.path.join("db", db_name)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        DB_CONNECTIONS[db_name] = sqlite3.connect(db_path)
    return DB_CONNECTIONS[db_name]

def close_all_connections():
    """
    Closes all open database connections.
    """
    for connection in DB_CONNECTIONS.values():
        connection.close()
    DB_CONNECTIONS.clear()
