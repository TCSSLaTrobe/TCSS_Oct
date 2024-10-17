import sqlite3
from datetime import datetime
from sqlite3.dbapi2 import sqlite_version_info
from turtledemo.penrose import start

from sqlalchemy.engine import connection_memoize

import viewInstance
import workload

now = datetime.now()
date = now.date()

def generate_dates():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT year, month_name, month
        FROM calendar
        WHERE full_date > ?
        GROUP BY year, month, month_name
    ''',(date,))
    data = cursor.fetchall()

    result = []
    current_year = None
    current_months = []

    for item in data:
        year = item[0]
        month = item[1]

        if year != current_year:
            if current_year:
                result.append({"year": current_year, "months": current_months})
            current_year = year
            current_months = []

        current_months.append(month)

    if current_year:
        result.append({"year": current_year, "months": current_months})

    dates = result
    return dates

def generate_months(year):
    data = generate_dates()
    months = []
    for item in data:
        if int(year) == item["year"]:
            months.append(item["months"])


    return months[0]

def generate_possible_lecturers(subject_id, year, month):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT MIN(id)
        FROM calendar
        WHERE month_name = ? AND year = ?
    ''', (month,year))
    start_id = cursor.fetchone()[0]


    possible_lecturers = viewInstance.generate_possible_lecturers(subject_id)
    print(possible_lecturers)

    for lecturer in possible_lecturers:
        running_workload = workload.calculate_workload(lecturer["id"],start_id)
        added_load = (2 / lecturer["max_workload"]) * 100
        lecturer["added_load"] = int(added_load)
        current_load = int((running_workload / lecturer["max_workload"]) * 100)
        lecturer["workload"] = current_load

    return possible_lecturers

def add_development(subject_id, start_id, lecturer_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    year = start_id[:4]
    month = start_id[6:]
    cursor.execute('''
           SELECT MIN(id)
           FROM calendar
           WHERE month_name = ? AND year = ?
       ''', (month, year))
    start_id = cursor.fetchone()[0]
    print(start_id)

    cursor.execute('''
        INSERT INTO development_instances (subject_id, lecturer_id, start_id)
        VALUES (?,?,?)
    ''',(subject_id,lecturer_id,start_id))

    connection.commit()

def get_instances():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT development_instances.id, lecturers.name, subjects.name, calendar.month_name, calendar.year
        FROM development_instances
        JOIN lecturers ON lecturers.id = development_instances.lecturer_id
        JOIN subjects ON subjects.id = development_instances.subject_id
        JOIN calendar ON calendar.id = development_instances.start_id
    ''')
    data = cursor.fetchall()

    instances = []
    for item in data:
        instance = {
            "id": item[0],
            "lecturer_name": item[1],
            "subject_name": item[2],
            "period": item[3] + " - " + str(item[4])
        }
        instances.append(instance)
    return instances

def delete_development(instance_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
        DELETE FROM development_instances
        WHERE id = ?
    ''',(instance_id,))

    connection.commit()

    return

def get_instance(instance_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT development_instances.id, lecturers.name, subjects.name, calendar.month_name, calendar.year
        FROM development_instances
        JOIN lecturers ON lecturers.id = development_instances.lecturer_id
        JOIN subjects ON subjects.id = development_instances.subject_id
        JOIN calendar ON calendar.id = development_instances.start_id
        WHERE development_instances.id = ?
    ''',(instance_id,))
    data = cursor.fetchone()

    instance = {
        "id": data[0],
        "lecturer_name": data[1],
        "subject_name": data[2],
        "period": data[3] + " - " + str(data[4])
    }

    return instance

