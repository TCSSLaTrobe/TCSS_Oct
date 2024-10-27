import sqlite3
from werkzeug.security import generate_password_hash
import dbconnector

def load_users(*args):
    connection, cursor = dbconnector.db_connection()

    try:
        if args:
            user_id = int(args[0])
            cursor.execute('''
                SELECT id, email, account_level 
                FROM user
                WHERE id = ?
            ''',(user_id,))
            data = cursor.fetchall()

            user = {}
            roles = ["Admin", "Manager", "Lecturer"]
            for item in data:
                user = {
                    "id": item[0],
                    "email": item[1],
                    "account_level": item[2],
                    "role": roles[item[2] - 1]
                }
            roles = [
                {"role":"Admin",
                 "account_level":1},
                {"role": "Manager",
                 "account_level": 2},
                {"role": "Lecturer",
                 "account_level": 3}
            ]
            cursor.execute('''
                SELECT id, name
                FROM lecturers
                WHERE user_id = ?
            ''',(user_id,))
            data = cursor.fetchone()
            if data:
                linked_lecturer = {"id":data[0],
                                   "name":data[1]}
            else:
                linked_lecturer = None
            return user, roles, linked_lecturer

        else:
            cursor.execute('''
                SELECT id, email, account_level FROM user
            ''')
            data = cursor.fetchall()

            users = []
            roles = ["Admin","Manager","Lecturer"]
            for item in data:
                user = {
                    "id": item[0],
                    "email": item[1],
                    "account_level": item[2],
                    "role": roles[item[2]-1]
                }
                users.append(user)
            return users

    except sqlite3.Error:
        return

    finally:
        connection.close()

def load_unattached_lecturers():
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
                SELECT id, name
                FROM lecturers
                WHERE user_id is NULL
            ''')
        data = cursor.fetchall()

        unattached_lecturers = []
        for item in data:
            lecturer = {
                "id": item[0],
                "name": item[1],
            }
            unattached_lecturers.append(lecturer)
        return unattached_lecturers

    except sqlite3.Error:
        return

    finally:
        connection.close()

def create_user(data):
    user_data = dict(data)
    email = user_data['user_email']
    hashed_password = generate_password_hash(user_data['user_password'])
    account_level = user_data['user_role']
    lecturer_id = user_data['lecturer_id']

    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            INSERT INTO user (email, password, account_level)
            VALUES (?,?,?)
        ''',(email,hashed_password,account_level))

        connection.commit()
        return True

    except sqlite3.Error:
        return False

    finally:
        connection.close()

def update_user(data):
    user_data = dict(data)
    user_id = user_data['user_id']
    email = user_data['user_email']
    account_level = int(user_data['user_role'])

    if len(user_data['new_password']) > 0:
        new_password = generate_password_hash(user_data['new_password'])
    else:
        new_password = None

    if len(user_data['lecturer_id']) > 0:
        new_lecturer_id = int(user_data['lecturer_id'])
    else:
        new_lecturer_id = None

    connection, cursor = dbconnector.db_connection()

    try:
        if new_password:
            cursor.execute('''
                UPDATE user
                SET password = ?
                WHERE id = ?
            ''',(new_password,user_id))
            connection.commit()

        if new_lecturer_id:
            cursor.execute('''
                UPDATE lecturers
                SET user_id = ?
                WHERE id = ?
            ''', (user_id, new_lecturer_id))
            connection.commit()

        cursor.execute('''
            UPDATE user
            SET account_level = ?
            WHERE id = ?
        ''',(account_level,user_id))

        connection.commit()
        return True

    except sqlite3.Error:
        return

    finally:
        connection.close()

def delete_user(user_id):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            UPDATE lecturers
            SET user_id = NULL
            WHERE user_id = ?
        ''',(user_id,))

        cursor.execute('''
            DELETE FROM user
            WHERE id = ?
        ''',(user_id,))

        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()



