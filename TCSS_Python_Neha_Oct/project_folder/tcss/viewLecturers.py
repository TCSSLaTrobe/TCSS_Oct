import sqlite3
from datetime import datetime

import workload


def query_lecturer_details():
    connection = sqlite3.connect("tcss.db")
    cursor = connection.cursor()

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

def generate_lecturer_data():
    now = datetime.now()
    connection = sqlite3.connect("tcss.db")
    cursor = connection.cursor()

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
            "workload": workload.calculate_workload(lecturer[0], start_id),
            "max_workload": lecturer[4],
            "expertise": []
        })

        for pair in lecturer_data[1]:
            if pair[1] == lecturer[1]:
                lecturers[i]["expertise"].append(pair[2] + " - " + pair[3])
        i += 1
    for lecturer in lecturers:
        running_workload = workload.calculate_workload(lecturer["id"], start_id)
        if running_workload != 0:
            lecturer["workload"] = str(int((running_workload / lecturer["max_workload"]) * 100)) + "%"
        else:
            lecturer["workload"] = "0%"



    return lecturers