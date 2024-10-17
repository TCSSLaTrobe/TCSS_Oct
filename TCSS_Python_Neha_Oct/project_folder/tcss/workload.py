import sqlite3
from datetime import datetime

def calculate_instance_load():
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT id, lecturer_id, assistant_id, student_count, workload_value
        FROM instances;
    ''')
    data = cursor.fetchall()

    instances = []
    for item in data:
        instance = {
            "id": item[0],
            "lecturer_id": item[1],
            "assistant_id": item[2],
            "student_count": item[3],
            "weight": item[4]
        }
        instances.append(instance)

    for instance in instances:
        weight = 1
        if instance["assistant_id"]:
            weight -= 1
        student_count = instance["student_count"]
        count = 0
        if student_count > 20:
            count += student_count // 20
            weight += count
        instance["weight"] = weight

    for instance in instances:
        cursor.execute('''
            UPDATE instances
            SET workload_value = ?
            WHERE id = ?
        ''',(instance["weight"],instance["id"]))

    connection.commit()
    connection.close()

    return

def calculate_workload(lecturer_id, month_start_id):
    connection = sqlite3.connect('tcss.db')
    cursor = connection.cursor()
    cursor.execute('''
    SELECT workload_value
    FROM instances 
    JOIN calendar 
    ON instances.start_id = calendar.id 
    WHERE lecturer_id = ? 
    AND instances.start_id > (SELECT id 
                              FROM calendar 
                              WHERE three_months = (SELECT full_date 
                                                    FROM calendar 
                                                    WHERE id = ?
                                                    )
                            )
    AND instances.start_id < (SELECT id 
                              FROM calendar
                              WHERE full_date = (SELECT three_months 
                                                 FROM calendar
                                                 WHERE id = ?
                                                 )
                             )
    ''',(lecturer_id,month_start_id,month_start_id))
    delivering_data = cursor.fetchall()

    running_workload = 0
    for item in delivering_data:
        running_workload += item[0]

    cursor.execute('''
        SELECT COUNT(workload_value)
        FROM instances 
        JOIN calendar 
        ON instances.start_id = calendar.id 
        WHERE assistant_id = ? 
        AND instances.start_id > (SELECT id 
                                  FROM calendar 
                                  WHERE three_months = (SELECT full_date 
                                                        FROM calendar 
                                                        WHERE id = ?
                                                        )
                                )
        AND instances.start_id < (SELECT id 
                                  FROM calendar
                                  WHERE full_date = (SELECT three_months 
                                                     FROM calendar
                                                     WHERE id = ?
                                                     )
                                 )
    ''', (lecturer_id,month_start_id,month_start_id))
    assisting_data = cursor.fetchone()[0]

    running_workload +=  assisting_data

    cursor.execute('''
        SELECT COUNT(development_instances.id)
        FROM development_instances 
        JOIN calendar 
        ON development_instances.start_id = calendar.id 
        WHERE lecturer_id = ? 
        AND development_instances.start_id > (SELECT id 
                                  FROM calendar 
                                  WHERE three_months = (SELECT full_date 
                                                        FROM calendar 
                                                        WHERE id = ?
                                                        )
                                )
        AND development_instances.start_id < (SELECT id 
                                  FROM calendar
                                  WHERE full_date = (SELECT three_months 
                                                     FROM calendar
                                                     WHERE id = ?
                                                     )
                                 )
    ''',(lecturer_id,month_start_id,month_start_id))
    developing_workload = cursor.fetchone()[0]

    running_workload += (2*developing_workload)

    return running_workload








