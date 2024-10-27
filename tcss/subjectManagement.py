import sqlite3
import dbconnector

def add_subject(code,name,instance_count):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            INSERT INTO subjects (code,name,instance_count)
            VALUES (?,?,?)
        ''',(code,name,instance_count))

        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()

def delete_subject(subject_id):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            DELETE FROM instances
            WHERE subject_id = ?
        ''', (subject_id,))

        # NEED TO UPDATE INSTANCES/SCHEDULE ONCE DELETED
        cursor.execute('''
            DELETE FROM lecturer_sme 
            WHERE subject_id = ?
        ''', (subject_id,))

        cursor.execute('''
            DELETE FROM subjects
            WHERE id = ?
        ''', (subject_id,))
        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_subject_data(*args):
    connection, cursor = dbconnector.db_connection()

    if args:
        subject_id = args[0]
        try:
            cursor.execute('''
                SELECT *
                FROM subjects
                WHERE id = ?
            ''', (subject_id,))

            subject_data = cursor.fetchall()
            subject_data = subject_data[0]
            subject = {
                "id": subject_data[0],
                "code": subject_data[1],
                "name": subject_data[2],
                "instances": subject_data[3]
            }

            return subject

        except sqlite3.Error:
            return

        finally:
            connection.close()
    else:
        try:
            cursor.execute('SELECT * FROM subjects')
            subject_data = cursor.fetchall()
            subjects = []
            for subject in subject_data:
                subjects.append({
                    "id": subject[0],
                    "code": subject[1],
                    "name": subject[2]
                })
            return subjects

        except sqlite3.Error:
            return

        finally:
            connection.close()

def update_subject(subject_id,code,name):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            UPDATE subjects
            SET code = ?, name = ?
            WHERE id = ? 
        ''', (code, name, subject_id))

        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()

