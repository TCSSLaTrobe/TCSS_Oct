import sqlite3
import dbconnector
import workloadManagement

def generate_schedule_data():
    connection, cursor = dbconnector.db_connection()

    try:
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

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_instance_dates():
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            SELECT id, subject_id, start_id
            FROM instances;
        ''')
        data = cursor.fetchall()

        instances = {}

        for instance_id, subject_id, start_id in data:
            if subject_id not in instances:
                instances[subject_id] = []
            instances[subject_id].append(instance_id)

        return instances

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_calendar_dates():
    connection, cursor = dbconnector.db_connection()

    try:
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

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_subject_data():
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
               SELECT id, code, name
                FROM subjects;
           ''')
        data = cursor.fetchall()

        subjects = []

        for item in data:
            subject = {"id": item[0], "code": item[1], "name": item[2]}
            subjects.append(subject)

        return subjects
    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_row_data():
    connection, cursor = dbconnector.db_connection()
    try:
        cursor.execute('''
            SELECT subjects.id, subjects.code, subjects.name, calendar.year, calendar.month
            FROM subjects
            JOIN instances
            ON subjects.id = instances.subject_id
            JOIN calendar
            ON calendar.id = instances.start_id
              ''')
        data = cursor.fetchall()

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

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_instance_ids():
    connection, cursor = dbconnector.db_connection()

    try:
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

    except sqlite3.Error:
        return

    finally:
        connection.close()

def update_instance(instance_id, lecturer_id, assistant_id, student_count):
    if not lecturer_id:
        lecturer_id = None

    if not assistant_id:
        assistant_id = None

    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            UPDATE instances
            SET student_count = ?,
            lecturer_id = ?,
            assistant_id = ?
            WHERE id = ? 
        ''',(student_count,lecturer_id, assistant_id, instance_id))

        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()

def create_instance(subject_id, student_count, instance_month, instance_year):

    connection, cursor = dbconnector.db_connection()

    try:
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
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()

def delete_instance(instance_id):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            DELETE FROM instances
            WHERE id = ?
        ''',(instance_id,))

        connection.commit()
        return

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_instance_data(instance_id):
    connection, cursor = dbconnector.db_connection()

    try:
        cursor.execute('''
            SELECT subjects.id,subjects.code, subjects.name, instances.student_count, calendar.month_name, calendar.year,
             instances.start_id, instances.workload_value
            FROM instances
            JOIN subjects ON subjects.id = instances.subject_id
            JOIN calendar ON calendar.id = instances.start_id
            WHERE instances.id = ?;
        ''',(instance_id,))

        data = cursor.fetchall()

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
            running_workload = workloadManagement.calculate_workload(lecturer["id"], instance_data["start_id"])
            added_load = int((instance_data["weight"] / lecturer["max_workload"]) * 100)
            lecturer["added_load_lecturer"] = added_load
            assist_load = int((1 / lecturer["max_workload"]) * 100)
            lecturer["added_load_assistant"] = assist_load
            current_load = int((running_workload / lecturer["max_workload"]) * 100)
            lecturer["workload"] = current_load

        return instance_data, possible_lecturers

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_assigned_lecturers(instance_id):
    connection, cursor = dbconnector.db_connection()

    try:
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

        assigned_lecturers = {
            "lecturer": current_lecturer[0] if current_lecturer else None,
            "assistant": current_assistant[0] if current_assistant else None
           }

        return assigned_lecturers

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_possible_lecturers(subject_id):
    connection, cursor = dbconnector.db_connection()

    try:
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

        possible_lecturers = []
        for item in data:
            possible_lecturers.append({
                "id":item[0],
                "name":item[1],
                "workload":item[2],
                "max_workload":item[3]
            })
        return possible_lecturers

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_create_new_data(subject_id):
    connection, cursor = dbconnector.db_connection()

    try:
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

        return possible_lecturers, subject_data, years

    except sqlite3.Error:
        return

    finally:
        connection.close()

def generate_possible_months(subject_id, year):
    connection, cursor = dbconnector.db_connection()
    try:
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
        for item in data:
            months.append(item[1])

        return months

    except sqlite3.Error:
        return

    finally:
        connection.close()

