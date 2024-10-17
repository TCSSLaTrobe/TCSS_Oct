import sqlite3

import workload


def generate_instance_data(instance_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT subjects.id,subjects.code, subjects.name, instances.student_count, calendar.month_name, calendar.year,
         instances.start_id, instances.workload_value
        FROM instances
        JOIN subjects ON subjects.id = instances.subject_id
        JOIN calendar ON calendar.id = instances.start_id
        WHERE instances.id = ?;
    ''',(instance_id,))

    data = cursor.fetchall()
    connection.close()

    instance_data = {}
    for item in data:
        instance_data = {
            "id": item[0],
            "code":item[1],
            "name":item[2],
            "student_count":item[3],
            "start_month":item[4],
            "start_year":item[5],
            "start_id":item[6],
            "weight":item[7]
        }

    possible_lecturers = generate_possible_lecturers(instance_data["id"])

    for lecturer in possible_lecturers:
        running_workload = workload.calculate_workload(lecturer["id"], instance_data["start_id"])
        added_load = int((instance_data["weight"] / lecturer["max_workload"]) * 100)
        lecturer["added_load_lecturer"] = added_load
        assist_load = int((1 / lecturer["max_workload"]) * 100)
        lecturer["added_load_assistant"] = assist_load
        current_load = int((running_workload / lecturer["max_workload"]) * 100)
        lecturer["workload"] = current_load

    return instance_data, possible_lecturers

def generate_assigned_lecturers(instance_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT lecturers.name
        FROM lecturers 
        JOIN instances on lecturers.id = instances.lecturer_id
        WHERE instances.id = ?;
    ''',(instance_id,))
    current_lecturer = cursor.fetchone()

    cursor.execute('''
        SELECT lecturers.name
        FROM lecturers 
        JOIN instances on lecturers.id = instances.assistant_id
        WHERE instances.id = ?;
    ''', (instance_id,))
    current_assistant = cursor.fetchone()

    connection.close()

    assigned_lecturers = {
        "lecturer": current_lecturer[0] if current_lecturer else None,
        "assistant": current_assistant[0] if current_assistant else None
       }

    return assigned_lecturers

def generate_possible_lecturers(subject_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT lecturers.id, lecturers.name, lecturers.workload, lecturers.max_workload
        FROM lecturers
        JOIN lecturer_sme ON lecturers.id = lecturer_sme.lecturer_id
        WHERE lecturers.id IN ( SELECT lecturer_sme.lecturer_id
                                FROM lecturer_sme
                                WHERE lecturer_sme.subject_id = ?)
        GROUP BY lecturers.id;
        ''', (subject_id,))
    data = cursor.fetchall()

    connection.close()

    possible_lecturers = []
    for item in data:
        possible_lecturers.append({
            "id":item[0],
            "name":item[1],
            "workload":item[2],
            "max_workload":item[3]
        })
    return possible_lecturers

def generate_create_new_data(subject_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT subjects.id, subjects.code, subjects.name
        FROM subjects
        WHERE subjects.id = ?
            ''', (subject_id,))
    data = cursor.fetchone()

    subject_data = {
        "id": data[0],
        "code": data[1],
        "name": data[2]
    }

    cursor.execute('''
        SELECT year
        FROM calendar 
        JOIN instances 
        ON instances.start_id = calendar.id 
        GROUP BY year
    ''')
    data = cursor.fetchall()
    years = []
    for item in data:
        years.append(item[0])
    years.append(years[-1]+1)

    possible_lecturers = generate_possible_lecturers(subject_id)

    connection.close()

    return possible_lecturers, subject_data, years

def generate_possible_months(subject_id, year):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT month, month_name
        FROM calendar
        WHERE month_name
        NOT IN (SELECT month_name
                FROM calendar
                JOIN instances
                ON instances.start_id = calendar.id
                WHERE instances.subject_id = ? AND year = ?
                GROUP BY month_name)
        GROUP BY month, month_name
        ''',(subject_id,year))
    data = cursor.fetchall()

    months = []
    months = []
    for item in data:
        months.append(item[1])

    return months

