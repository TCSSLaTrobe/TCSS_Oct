import sqlite3
from werkzeug.security import check_password_hash
import dbconnector

def check_login(email, password):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            SELECT password 
            FROM user
            WHERE email = ?
        ''',(email,))
        data = cursor.fetchone()

        if data:
            if check_password_hash(data[0],password):
                connection.commit()
                return True
        else:
            return False

    except sqlite3.Error:
        return False

    finally:
        connection.close()

class User:
    def __init__(self,user_id,account_level,is_active):
        self.user_id = user_id
        self.account_level = account_level
        self.is_active = is_active

def set_user(email):
    connection, cursor = dbconnector.db_connection()
    try:
        cursor.execute('''
            SELECT id, account_level
            FROM user
            WHERE email = ?
        ''', (email,))
        data = cursor.fetchone()
        user_id = int(data[0])
        account_level = int(data[1])
        current_user = User(user_id,account_level,True)
        return current_user

    except sqlite3.Error:
        return

    finally:
        connection.close()