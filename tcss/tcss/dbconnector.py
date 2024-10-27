import sqlite3

def db_connection():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    return connection, cursor