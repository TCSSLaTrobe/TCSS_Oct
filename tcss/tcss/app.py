from datetime import datetime
import Login
import developmentManagement
import lecturerManagement
import userManagement
import subjectManagement, individualScheduleManagement, scheduleManagement, workloadManagement
from flask import Flask, render_template, request, url_for
from werkzeug.utils import redirect

now = datetime.now()
year = now.year
month = now.strftime("%B")
date = {
    "year": year,
    "month": month
}

app = Flask(__name__)
app.config['SECRET_KEY'] = '26350e389debee0ff7f0a893c78cb2b1cd3519c31957af3866171d5e30ce0941'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if Login.check_login(email, password):
            global current_user
            current_user = Login.set_user(email)
            global account_level
            account_level = current_user.account_level
            return redirect('/home')
        else:
            msg="Incorrect Credentials"
            return render_template('login.html', msg=msg)
    return render_template('login.html')

@app.route('/logout')
def logout():
    global current_user
    current_user = None
    response = redirect(url_for('login'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/')
@app.route('/home')
def home_page():
    try:
        if current_user.is_active:
            if account_level < 3:
                return redirect('/scheduling')
            else:
                return redirect('/view_schedule')
        else:
            return render_template('login.html')
    except  NameError:
        return redirect('/login')

# MANAGE LECTURERS (VIEW/EDIT/DELETE/ADD)
@app.route('/view_lecturers')
def view_lecturers():
    try:
        if current_user.is_active:
            if account_level <= 1:
                lecturer_data = lecturerManagement.generate_lecturer_data()
                return render_template('view_lecturers.html', date=date, lecturer_data=lecturer_data, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/edit_lecturer', methods=['GET','POST'])
def edit_lecturer():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    lecturer_id = request.form['lecturer_id']
                    lecturer = lecturerManagement.generate_lecturer_data(lecturer_id)
                    subjects = lecturerManagement.generate_subject_data()
                    sme = lecturerManagement.generate_sme(lecturer_id)
                    return render_template('edit_lecturer.html',lecturer_id=lecturer_id,lecturer=lecturer, subjects=subjects, sme=sme, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')
@app.route('/update_lecturer', methods=['GET','POST'])
def update_lecturer():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    lecturer_id = request.form['lecturer_id']
                    name = request.form['lecturer_name']
                    workload = request.form['lecturer_workload']
                    sme = request.form.getlist('sme')
                    lecturerManagement.update_lecturer(lecturer_id, name, workload, sme)
                    return redirect('/view_lecturers')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/delete_lecturer', methods=['GET','POST'])
def delete_lecturer():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    lecturer_id = request.form['lecturer_id']
                    lecturer = lecturerManagement.generate_lecturer_data(lecturer_id)
                    return render_template('/delete_lecturer.html', lecturer=lecturer, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/confirm_delete_lecturer', methods=['GET','POST'])
def confirm_delete_lecturer():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    lecturer_id = request.form['lecturer_id']
                    lecturerManagement.delete_lecturer(lecturer_id)
                    return redirect('/view_lecturers')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/add_lecturer', methods=['GET','POST'])
def add_lecturer():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    name = request.form['lecturer_name']
                    workload = request.form['lecturer_workload']
                    sme = request.form.getlist('sme')
                    if lecturerManagement.add_lecturer(name, workload, sme):
                        return redirect('/view_lecturers')
                    else:
                        return redirect('/add_lecturer')
                subjects = lecturerManagement.generate_subject_data()
                return render_template('/add_lecturer.html', subjects=subjects, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

# MANAGE SUBJECTS (VIEW/EDIT/DELETE/ADD)
@app.route('/view_subjects')
def view_subjects():
    try:
        if current_user.is_active:
            if account_level <= 1:
                subjects = subjectManagement.generate_subject_data()
                return render_template('/view_subjects.html', subjects=subjects, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/edit_subject', methods=['GET','POST'])
def edit_subject():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    subject_id = request.form['subject_id']
                    subject = subjectManagement.generate_subject_data(subject_id)
                    return render_template('edit_subject.html', subject=subject, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/update_subject', methods=['GET','POST'])
def update_subject():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    subject_id = request.form['subject_id']
                    code = request.form['subject_code']
                    name = request.form['subject_name']
                    if subjectManagement.update_subject(subject_id,code,name):
                        return redirect('/view_subjects')
                    else:
                        subject_id = request.form['subject_id']
                        subject = subjectManagement.generate_subject_data(subject_id)
                        error = "Subject Code must be unique"
                        return render_template('edit_subject.html', subject=subject, account_level=account_level, error=error)

            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/add_subject', methods=['GET','POST'])
def add_subject():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    code = request.form['subject_code']
                    name = request.form['subject_name']
                    instance_count = 0
                    if subjectManagement.add_subject(code,name,instance_count):
                        return redirect('/view_subjects')
                    else:
                        error = "Subject Code must be unique"
                        return render_template('/add_subject.html', account_level=account_level,
                                               error=error)
                return render_template('/add_subject.html',account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/delete_subject', methods=['GET','POST'])
def delete_subject():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    subject_id = request.form['subject_id']
                    subject = subjectManagement.generate_subject_data(subject_id)
                    return render_template('/delete_subject.html', subject=subject, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/confirm_delete_subject', methods=['GET','POST'])
def confirm_delete_subject():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    subject_id = request.form['subject_id']
                    subjectManagement.delete_subject(subject_id)
                    return redirect('/view_subjects')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/view_schedule')
def view_schedule():
    try:
        if current_user.is_active:
            if account_level == 3:
                lecturer = individualScheduleManagement.get_lecturer(current_user.id)
                all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                try:
                    schedule_dates, lecturer_instances, assistant_instances, development_instances = individualScheduleManagement.generate_schedule(current_user.id)
                except:
                    lecturer_instances = False
                    assistant_instances = False
                    development_instances = False
                    schedule_dates = False
                return render_template('/schedule.html',all_months=all_months, date=date, lecturer=lecturer,lecturer_instances=lecturer_instances,assistant_instances=assistant_instances,development_instances=development_instances, schedule_dates=schedule_dates, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/scheduling')
def manage_schedule():
    try:
        if current_user.is_active:
            if account_level <= 2:
                schedule_data = scheduleManagement.generate_schedule_data()
                calendar_dates = scheduleManagement.generate_calendar_dates()
                return render_template('/manage_schedule2.html', title="Scheduling", schedule_data=schedule_data,
                                       calendar_dates=calendar_dates, account_level=account_level)
            else:
                return redirect('/login')
        else:
            return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/view_instance', methods=['GET','POST'])
def view_instance():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    instance_id = request.form['instance_id']
                    instance_data, possible_lecturers = scheduleManagement.generate_instance_data(instance_id)
                    assigned_staff = scheduleManagement.generate_assigned_lecturers(instance_id)
                    return render_template('/view_instance.html',instance_data=instance_data,
                                           assigned_staff=assigned_staff, possible_lecturers=possible_lecturers,
                                           instance_id=instance_id, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/update_instance', methods=['GET','POST'])
def update_instance():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    instance_id = request.form['instance_id']
                    lecturer_id = request.form['lecturer_id']
                    assistant_id = request.form['assistant_id']
                    student_count = request.form['student_count']
                    scheduleManagement.update_instance(instance_id, lecturer_id, assistant_id, student_count)
                    workloadManagement.calculate_instance_load()
                    instance_data, possible_lecturers = scheduleManagement.generate_instance_data(instance_id)
                    assigned_staff = scheduleManagement.generate_assigned_lecturers(instance_id)
                    return render_template('/view_instance.html', instance_data=instance_data,
                                           assigned_staff=assigned_staff, possible_lecturers=possible_lecturers,
                                           instance_id=instance_id, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/new_instance', methods=['GET', 'POST'])
def new_instance():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    subject_id = int(request.form['subject_id'])
                    possible_lecturers, subject_data, years = scheduleManagement.generate_create_new_data(subject_id)
                    return render_template('create_instance.html', subject_data=subject_data,
                                        possible_lecturers=possible_lecturers, years=years, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/year_select', methods=['GET','POST'])
def year_select():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    subject_id = request.form['subject_id']
                    selected_year = int(request.form['instance_year'])
                    months = scheduleManagement.generate_possible_months(subject_id, selected_year)
                    possible_lecturers, subject_data, years = scheduleManagement.generate_create_new_data(subject_id)
                    return render_template('create_instance.html', selected_year=selected_year, subject_data=subject_data,
                                        possible_lecturers=possible_lecturers, years=years, months=months, account_level=account_level)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/create_instance', methods=['GET','POST'])
def create_instance():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    subject_id = request.form['subject_id2']
                    student_count = request.form['student_count']
                    instance_month = request.form['instance_month']
                    instance_year = request.form['instance_year2']
                    workloadManagement.calculate_instance_load()
                    scheduleManagement.create_instance(subject_id,student_count,instance_month,instance_year)
                    return redirect('/scheduling')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/delete_instance', methods=['GET','POST'])
def delete_instance():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    instance_id = request.form['delete_id']
                    scheduleManagement.delete_instance(instance_id)
                    return redirect('/scheduling')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/add_development', methods=['GET','POST'])
def add_development():
    try:
        if current_user.is_active:
            if account_level <= 2:
                subjects = subjectManagement.generate_subject_data()
                dates = developmentManagement.generate_dates()
                return render_template('/add_development.html', account_level=account_level,
                                       subjects=subjects, dates=dates)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/year_select_dev', methods=['GET','POST'])
def year_select_dev():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    dev_year = request.form['dev_year']
                    months = developmentManagement.generate_months(dev_year)
                    selected_year = int(request.form['dev_year'])
                    subject_id = request.form['subject_id']
                    subject = subjectManagement.generate_subject_data(subject_id)
                    dates = developmentManagement.generate_dates()
                    return render_template('/add_development.html', account_level=account_level,
                                           subject=subject, dates=dates, months=months, selected_year=selected_year)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/month_select_dev', methods=['GET','POST'])
def month_select_dev():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    dev_year = request.form['dev_year2']
                    months = developmentManagement.generate_months(dev_year)
                    dev_month = request.form['dev_month']
                    selected_year = int(dev_year)
                    selected_month = dev_month
                    subject_id = request.form['subject_id']
                    subject = subjectManagement.generate_subject_data(subject_id)
                    dates = developmentManagement.generate_dates()
                    possible_lecturers = developmentManagement.generate_possible_lecturers(subject_id, selected_year, selected_month)
                    return render_template('/add_development.html', account_level=account_level,
                                           subject=subject, dates=dates, months=months, selected_year=selected_year,
                                           selected_month=selected_month, possible_lecturers=possible_lecturers)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/submit_dev', methods=['GET','POST'])
def submit_dev():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    subject_id = request.form['subject_id']
                    start_id = request.form['start_id']
                    lecturer_id = request.form['lecturer_id']
                    developmentManagement.add_development(subject_id,start_id,lecturer_id)
                    return redirect('/manage_development')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/manage_development')
def manage_development():
    try:
        if current_user.is_active:
            if account_level <= 2:
                development_instances = developmentManagement.get_instances()
                return render_template('/manage_development.html', account_level=account_level, development_instances=development_instances)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/delete_development', methods=['GET','POST'])
def delete_development():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    instance_id = request.form['instance_id']
                    instance = developmentManagement.get_instance(instance_id)
                    return render_template('/delete_development.html', account_level=account_level, instance=instance)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/confirm_delete_development', methods=['GET','POST'])
def confirm_delete_development():
    try:
        if current_user.is_active:
            if account_level <= 2:
                if request.method == 'POST':
                    instance_id = request.form['instance_id']
                    developmentManagement.delete_development(instance_id)
                    return redirect('/manage_development')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/user_management', methods=['GET','POST'])
def user_management():
    try:
        if current_user.is_active:
            if account_level <= 1:
                user_data = userManagement.load_users()
                return render_template('/user_management.html', account_level=account_level, title="User Management", users=user_data)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/create_user', methods=['GET','POST'])
def create_user():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    data = request.form.items()
                    if userManagement.create_user(data):
                        return redirect('/user_management')
                    else:
                        unattached_lecturers = userManagement.load_unattached_lecturers()
                        error = "Email is already in use"
                        return render_template('/create_user.html', account_level=account_level, title="Create User",
                                               unattached_lecturers=unattached_lecturers, error=error)
                else:
                    unattached_lecturers = userManagement.load_unattached_lecturers()
                    return render_template('/create_user.html', account_level=account_level, title="Create User", unattached_lecturers=unattached_lecturers)
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/edit_user', methods=['GET','POST'])
def edit_user():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    user_id = int(request.form['user_id'])
                    if user_id == current_user.user_id:
                        return redirect('/user_management')
                    else:
                        user_data, roles, linked_lecturer = userManagement.load_users(user_id)
                        unattached_lecturers = userManagement.load_unattached_lecturers()
                        return render_template('/edit_user.html', account_level=account_level, title="Edit User",
                                               unattached_lecturers=unattached_lecturers, user_data=user_data, roles=roles, linked_lecturer=linked_lecturer)
                else:
                    return redirect('/user_management')
            else:
                return redirect('/login')
    except AttributeError as e:
        return redirect('/login')

@app.route('/update_user',methods=['GET','POST'])
def update_user():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    data = request.form.items()
                    if userManagement.update_user(data):
                        return redirect('/user_management')
                    else:
                        return redirect('/edit_user')
                else:
                    return redirect('/edit_user')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/delete_user',methods=['GET','POST'])
def delete_user():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    user_id = int(request.form['user_id'])
                    if user_id == current_user.id:
                        return redirect('/user_management')
                    else:
                        user_data, roles, linked_lecturer = userManagement.load_users(user_id)
                        return render_template('/delete_user.html', account_level=account_level,
                                               title="Delete User", user_data=user_data)
                else:
                    return redirect('/user_management')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')

@app.route('/confirm_delete_user',methods=['GET','POST'])
def confirm_delete_user():
    try:
        if current_user.is_active:
            if account_level <= 1:
                if request.method == 'POST':
                    user_id = int(request.form['user_id'])
                    userManagement.delete_user(user_id)
                    return redirect('/user_management')
                else:
                    return redirect('/user_management')
            else:
                return redirect('/login')
    except  AttributeError:
        return redirect('/login')



if __name__ == '__main__':
    app.run(port=80)