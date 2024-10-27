import sqlite3
from datetime import datetime
import dbconnector
import workloadManagement

def generate_lecturer_data(*args):
    now = datetime.now()
    connection, cursor = dbconnector.db_connection()

    if args:
        lecturer_id = args[0]
        try:
            cursor.execute('''
                   SELECT id, name, load
                   FROM lecturers
                   WHERE id = ?
               ''', (lecturer_id,))
            data = cursor.fetchall()[0]

            lecturer = {
                "id": data[0],
                "name": data[1],
                "employment": data[2],
                "expertise": []
            }

            cursor.execute('''
                   SELECT lecturers.id, lecturers.name, lecturers.load, subjects.code, subjects.name FROM lecturer_sme
                   JOIN lecturers
                   ON lecturers.id = lecturer_sme.lecturer_id
                   JOIN subjects
                   ON lecturer_sme.subject_id = subjects.id
                   WHERE lecturers.id = ?
               ''', (lecturer_id,))
            lecturer_data = cursor.fetchall()

            for lecturer_tuple in lecturer_data:
                lecturer["expertise"].append(lecturer_tuple[3] + "-" + lecturer_tuple[4])

            return lecturer

        except sqlite3.Error:
            return

        finally:
            connection.close()

    else:
        try:
            cursor.execute('''
                SELECT MIN(id)
                FROM calendar
                WHERE month = ?
                AND year  = ?
            ''',(now.month, now.year) )
            start_id = cursor.fetchone()[0]

            lecturer_data = query_lecturer_details()
            lecturers = []
            i = 0
            for lecturer in lecturer_data[0]:
                lecturers.append(
                    {
                        "id": lecturer[0],
                        "name": lecturer[1],
                        "employment": lecturer[2],
                        "workload": workloadManagement.calculate_workload(lecturer[0], start_id),
                        "max_workload": lecturer[4],
                        "expertise": []
                    })

                for pair in lecturer_data[1]:
                    if pair[1] == lecturer[1]:
                        lecturers[i]["expertise"].append(pair[2] + " - " + pair[3])
                i += 1
            for lecturer in lecturers:
                running_workload = workloadManagement.calculate_workload(lecturer["id"], start_id)
                if running_workload != 0:
                    lecturer["workload"] = str(int((running_workload / lecturer["max_workload"]) * 100)) + "%"
                else:
                    lecturer["workload"] = "0%"
            return lecturers

        except sqlite3.Error:
            return

        finally:
            connection.close()

def query_lecturer_details():
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('SELECT id, name, load, workload, max_workload FROM lecturers')
        lecturer_names = cursor.fetchall()

        cursor.execute('''SELECT lecturers.id, lecturers.name, subjects.code, subjects.name FROM lecturer_sme
                        JOIN lecturers
                        ON lecturers.id = lecturer_sme.lecturer_id
                        JOIN subjects
                        ON lecturer_sme.subject_id = subjects.id
                        ''')
        lecturer_expertise = cursor.fetchall()
        return lecturer_names, lecturer_expertise

    except sqlite3.Error:
        return

    finally:
        connection.close()

def add_lecturer(name, workload, sme):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            INSERT INTO lecturers (name, load)
            VALUES (?,?)
        ''',(name,workload))

        lecturer_id = cursor.execute("SELECT MAX(id) FROM lecturers").fetchone()[0]

        for subject_id in sme:
            cursor.execute('''
                INSERT INTO lecturer_sme (lecturer_id, subject_id)
                VALUES (?,?)
            ''',(lecturer_id, subject_id))

        connection.commit()
        return True

    except sqlite3.Error:
        return False

    finally:
        connection.close()

def delete_lecturer(lecturer_id):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            UPDATE instances
            SET lecturer_id = NULL
            WHERE lecturer_id = ?
        ''', (lecturer_id,))

        cursor.execute('''
            UPDATE instances
            SET assistant_id = NULL
            WHERE assistant_id = ?
        ''', (lecturer_id,))

        cursor.execute('''
            DELETE FROM lecturer_sme
            WHERE lecturer_id = ?    
        ''', (lecturer_id,))

        cursor.execute('''
            DELETE FROM lecturers
            WHERE id = ?
        ''', (lecturer_id,))

        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_subject_data():
    connection, cursor = dbconnector.db_connection()

    try:
        # Get subject data for SME checkboxes
        cursor.execute('''
            SELECT code, name FROM subjects 
        ''')
        subject_data = cursor.fetchall()
        return subject_data

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_sme(lecturer_id):
    connection = sqlite3.connect("tcss.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        # Get subject data for SME checkboxes
        subjects = generate_subject_data()
        cursor.execute('''
                SELECT subject_id 
                FROM lecturer_sme 
                WHERE lecturer_id = ? 
            ''',(lecturer_id,))
        rows = cursor.fetchall()
        lecturer_sme = [row['subject_id'] for row in rows]

        all_sme = [0] * len(subjects)
        for subject_id in lecturer_sme:
            all_sme[subject_id - 1] = 1

        return all_sme

    except sqlite3.Error:
        return

    finally:
        connection.close()

def update_lecturer(lecturer_id, name, workload, sme):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            UPDATE lecturers
            SET name = ?, [load] = ?
            WHERE id = ?
        ''', (name, workload, lecturer_id))

        cursor.execute('''
            DELETE FROM lecturer_sme WHERE lecturer_id = ?
        ''', (lecturer_id,))

        for subject_id in sme:
            cursor.execute('''
                INSERT INTO lecturer_sme (lecturer_id, subject_id)
                VALUES(?,?)
            ''', (lecturer_id, subject_id))

        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()