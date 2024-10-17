from turtledemo.penrose import start

from flask import Flask, render_template
import sqlite3
import os

def generate_schedule(user_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT lecturers.id
        FROM lecturers
        WHERE lecturers.user_id = ?
    ''',(user_id,))
    lecturer_id = cursor.fetchone()[0]

    lecturer_schedule_dates, lecturer_instances = generate_lecturer_schedule(lecturer_id)
    assistant_schedule_dates, assistant_instances = generate_assistant_schedule(lecturer_id)
    development_schedule_dates, development_instances = generate_development_schedule(lecturer_id)

    schedule_dates = merge_schedule_dates(lecturer_schedule_dates,assistant_schedule_dates,development_schedule_dates)

    return schedule_dates, lecturer_instances, assistant_instances, development_instances

def merge_instances(lecturer_instances, assistant_instances, development_instances):
    return

def merge_schedule_dates(lecturer_schedule_dates,assistant_schedule_dates,development_schedule_dates):
    data = lecturer_schedule_dates + assistant_schedule_dates + development_schedule_dates
    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                   "November", "December"]

    result = []
    for item in data:
        year = item["year"]
        months = item["months"]
        existing_item = next((x for x in result if x["year"] == year), None)
        if existing_item:
            existing_item['months'].extend(months)
        else:
            result.append({'year': year, 'months': months})

    for item in result:
        item['months'] = list(set(item['months']))
        sorted_months = sorted(item['months'], key=lambda m: month_names.index(m))
        item['months'] = sorted_months

    merged_schedule_dates = result

    return merged_schedule_dates


def get_lecturer(user_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
            SELECT lecturers.id
            FROM lecturers
            WHERE lecturers.user_id = ?
        ''', (user_id,))
    lecturer_id = cursor.fetchone()[0]

    cursor.execute('''
            SELECT name
            FROM lecturers
            WHERE id = ?
            ''', (lecturer_id,))
    lecturer = cursor.fetchone()[0]

    return lecturer

def generate_lecturer_schedule(lecturer_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT calendar.year, calendar.month_name, calendar.month
        FROM calendar
        JOIN instances ON calendar.id = instances.start_id
        WHERE instances.lecturer_id = ?
        ORDER BY year, month
        ''', (lecturer_id,))
    data = cursor.fetchall()

    result = []
    current_year = None
    current_months = []

    for year, month, num in data:
        if year != current_year:
            if current_year:
                result.append({"year": current_year, "months": current_months})
            current_year = year
            current_months = []
        current_months.append(month)

    if current_year:
        result.append({"year": current_year, "months": current_months})

    schedule_dates = result

    if len(schedule_dates) == 0:
        return None

    cursor.execute('''
           SELECT subjects.code, subjects.name, instances.student_count, calendar.year, calendar.month_name, instances.assistant_id, instances.start_id
           FROM instances
           JOIN subjects ON instances.subject_id = subjects.id
           JOIN calendar ON instances.start_id = calendar.id
           JOIN lecturers ON instances.lecturer_id = lecturers.id
           WHERE lecturers.id = ?;
       ''', (lecturer_id,))
    data = cursor.fetchall()

    instances = []

    for code, name, student_count, year, month, assistant_id, start_id in data:
        instance = {
            "code": code,
            "name": name,
            "student_count": student_count,
            "year": year,
            "start_month": month,
            "months": get_month_array(start_id),
            "role": "Delivering",
            "length": 3,
        }
        if assistant_id:
            cursor.execute('''
                   SELECT lecturers.name
                   FROM lecturers
                   WHERE lecturers.id = ?
               ''', (assistant_id,))
            assistant = cursor.fetchone()[0]

            instance["assistant"] = assistant
        instances.append(instance)

    return schedule_dates, instances

def generate_assistant_schedule(lecturer_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
            SELECT calendar.year, calendar.month_name, calendar.month
            FROM calendar
            JOIN instances ON calendar.id = instances.start_id
            WHERE instances.assistant_id = ?
            ORDER BY year, month
        ''', (lecturer_id,))
    data = cursor.fetchall()

    result = []
    current_year = None
    current_months = []

    for year, month, num in data:
        if year != current_year:
            if current_year:
                result.append({"year": current_year, "months": current_months})
            current_year = year
            current_months = []
        current_months.append(month)

    if current_year:
        result.append({"year": current_year, "months": current_months})

    schedule_dates = result

    if len(schedule_dates) == 0:
        return None

    cursor.execute('''
           SELECT subjects.code, subjects.name, instances.student_count, calendar.year, calendar.month_name, instances.lecturer_id, instances.start_id
           FROM instances
           JOIN subjects ON instances.subject_id = subjects.id
           JOIN calendar ON instances.start_id = calendar.id
           JOIN lecturers ON instances.assistant_id = lecturers.id
           WHERE lecturers.id = ?;
       ''', (lecturer_id,))
    data = cursor.fetchall()

    instances = []

    for code, name, student_count, year, month, lecturer_id, start_id in data:
        instance = {
            "code": code,
            "name": name,
            "student_count": student_count,
            "year": year,
            "month": month,
            "months": get_month_array(start_id),
            "role": "Assisting",
            "length": 3,
        }
        if lecturer_id:
            cursor.execute('''
                   SELECT lecturers.name
                   FROM lecturers
                   WHERE lecturers.id = ?
               ''', (lecturer_id,))
            lecturer = cursor.fetchone()[0]

            instance["lecturer"] = lecturer
        instances.append(instance)

    return schedule_dates, instances

def generate_development_schedule(lecturer_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT calendar.year, calendar.month_name, calendar.month
        FROM calendar
        JOIN development_instances ON calendar.id = development_instances.start_id
        WHERE development_instances.lecturer_id = ?
        ORDER BY year, month
    ''', (lecturer_id,))
    data = cursor.fetchall()

    result = []
    current_year = None
    current_months = []

    for year, month, num in data:
        if year != current_year:
            if current_year:
                result.append({"year": current_year, "months": current_months})
            current_year = year
            current_months = []
        current_months.append(month)

    if current_year:
        result.append({"year": current_year, "months": current_months})

    schedule_dates = result

    if len(schedule_dates) == 0:
        return None

    cursor.execute('''
       SELECT subjects.code, subjects.name, calendar.year, calendar.month_name
       FROM development_instances
       JOIN subjects ON development_instances.subject_id = subjects.id
       JOIN calendar ON development_instances.start_id = calendar.id
       JOIN lecturers ON development_instances.lecturer_id = lecturers.id
       WHERE lecturers.id = ?;
   ''', (lecturer_id,))
    data = cursor.fetchall()
    instances = []

    for code, name, year, month, in data:
        instance = {
            "code": code,
            "name": name,
            "year": year,
            "month": month,
            "role": "Developing",
            "length": 1,
        }
        instances.append(instance)
    return schedule_dates, instances

def get_month_array(start_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    months = []

    cursor.execute('''
        SELECT full_date
        FROM calendar
        WHERE id = ?
    ''',(start_id,))
    date = cursor.fetchone()[0]

    # cursor.execute('''
    #     SELECT month_name
    #     FROM calendar
    #     WHERE full_date = date(?, '-2 month')
    # ''',(date,))
    # months.append(cursor.fetchone()[0])
    #
    # cursor.execute('''
    #         SELECT month_name
    #         FROM calendar
    #         WHERE full_date = date(?, '-1 month')
    #     ''', (date,))
    # months.append(cursor.fetchone()[0])

    cursor.execute('''
        SELECT month_name
        FROM calendar
        WHERE id = ?
    ''',(start_id,))
    months.append(cursor.fetchone()[0])

    cursor.execute('''
                SELECT month_name 
                FROM calendar
                WHERE full_date = date(?, '+1 month')
            ''', (date,))
    months.append(cursor.fetchone()[0])

    cursor.execute('''
                SELECT month_name 
                FROM calendar
                WHERE full_date = date(?, '+2 month')
            ''', (date,))
    months.append(cursor.fetchone()[0])

    return months


