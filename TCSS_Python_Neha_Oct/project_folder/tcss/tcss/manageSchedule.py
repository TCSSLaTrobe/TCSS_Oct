import sqlite3
from turtledemo.penrose import start

from sqlalchemy.engine import connection_memoize

def generate_schedule_data():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
               SELECT id, code, name
                FROM subjects;
           ''')
    data = cursor.fetchall()

    subjects = []
    for item in data:
        subject = {"subject_id": item[0],
                   "subject_code": item[1],
                   "subject_name": item[2],
                   "instances": []
                   }
        subjects.append(subject)

    cursor.execute('''
        SELECT id, subject_id, start_id, lecturer_id
        FROM instances;
    ''')
    data = cursor.fetchall()

    cursor.execute('''
            SELECT calendar.id, calendar.month, calendar.month_name, calendar.year
            FROM instances
            JOIN calendar
            ON instances.start_id = calendar.id
            GROUP BY instances.start_id;
            ''')
    calendar_length = len(cursor.fetchall())

    instances = []
    for item in data:
        instance = {"instance_id": item[0],
                    "subject_id": item[1],
                    "instance_start_id": item[2],
                    "instance_lecturer_id": item[3]
                    }
        instances.append(instance)

    for subject in subjects:
        for instance in instances:
            if instance["subject_id"] == subject["subject_id"]:
                subject["instances"].append(instance)
    return subjects

def generate_instance_dates():
    connection  = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, subject_id, start_id
        FROM instances;
    ''')
    data = cursor.fetchall()
    connection.close()

    instances = {}

    for instance_id, subject_id, start_id in data:
        if subject_id not in instances:
            instances[subject_id] = []
        instances[subject_id].append(instance_id)

    return instances

def generate_calendar_dates():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT calendar.year
        FROM instances
        JOIN calendar 
        ON instances.start_id = calendar.id
        GROUP BY calendar.year;
    ''')
    data = cursor.fetchall()

    years = []
    for item in data:
        year = {"year": item[0],
                "months": []
                }
        years.append(year)

    cursor.execute('''
        SELECT calendar.id, calendar.month, calendar.month_name, calendar.year
        FROM instances
        JOIN calendar 
        ON instances.start_id = calendar.id
        GROUP BY instances.start_id;
        ''')
    data = cursor.fetchall()

    months = []
    for item in data:
        month = {"start_id": item[0],
                 "month_num": item[1],
                 "month_name": item[2][:3].upper(),
                 "year": item[3]
                 }
        months.append(month)

    for year in years:
        for month in months:
            if month["year"] == year["year"]:
                year["months"].append(month)

    calendar_dates = years

    return calendar_dates

def generate_subject_data():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
           SELECT id, code, name
            FROM subjects;
       ''')
    data = cursor.fetchall()
    connection.close()

    subjects = []

    for item in data:
        subject = {"id": item[0], "code": item[1], "name": item[2]}
        subjects.append(subject)

    return subjects

def generate_row_data():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT subjects.id, subjects.code, subjects.name, calendar.year, calendar.month
        FROM subjects
        JOIN instances
        ON subjects.id = instances.subject_id
        JOIN calendar
        ON calendar.id = instances.start_id
          ''')
    data = cursor.fetchall()
    connection.close()

    rows = []
    subject_data = {}

    for subject_id, subject_code, subject_name, year, month in data:
        if subject_id not in subject_data:
            subject_data[subject_id] = {
                "code": subject_code,
                "name": subject_name,
                "start_dates": {}
            }

        if year not in subject_data[subject_id]["start_dates"]:
            subject_data[subject_id]["start_dates"][year] = []

        subject_data[subject_id]["start_dates"][year].append(month)

    for subject_id, subject_info in subject_data.items():
        rows.append({
            "id": subject_id,
            "code": subject_info["code"],
            "name": subject_info["name"],
            "start_dates": subject_info["start_dates"]
        })

    return rows

def generate_instance_ids():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT instances.id
        FROM instances
        JOIN subjects
        ON subjects.id = instances.subject_id
        ORDER BY subjects.id
    ''')
    data = cursor.fetchall()

    instance_ids = [x[0] for x in data]

    return instance_ids

def generate_assigned_lecturers():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, lecturer_id, assistant_id
        FROM instances; 
        ''')
    data = cursor.fetchall()

    assigned_lecturers = {}
    for instance_id, lecturer_id, assistant_id in data:
        assigned_lecturers[instance_id] = {
            "lecturer": lecturer_id,
            "assistant": assistant_id
        }

    return assigned_lecturers

def update_instance(instance_id, lecturer_id, assistant_id, student_count):
    if not lecturer_id:
        lecturer_id = None

    if not assistant_id:
        assistant_id = None

    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE instances
        SET student_count = ?,
        lecturer_id = ?,
        assistant_id = ?
        WHERE id = ? 
    ''',(student_count,lecturer_id, assistant_id, instance_id))

    connection.commit()
    connection.close()

    return

def create_instance(subject_id, student_count, instance_month, instance_year):

    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()

    cursor.execute('''
        SELECT MIN(id)
        FROM calendar
        WHERE month_name = ?
        AND year = ?
    ''',(instance_month,instance_year))
    start_id = cursor.fetchone()[0]

    cursor.execute('''
        SELECT id
        FROM calendar
        WHERE full_date = 
            (SELECT three_months
            FROM calendar
            WHERE id = ?)
    ''',(start_id,))
    end_id = cursor.fetchone()[0]

    cursor.execute('''
        INSERT INTO instances (subject_id, start_id, end_id, student_count, workload_value)
        VALUES (?,?,?,?, 0.0)
    ''',(subject_id,start_id,end_id,student_count))
    #
    connection.commit()
    connection.close()
    return

def delete_instance(instance_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        DELETE FROM instances
        WHERE id = ?
    ''',(instance_id,))

    connection.commit()
    connection.close()
    return

