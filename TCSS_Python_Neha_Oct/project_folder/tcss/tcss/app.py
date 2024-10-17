import json
from datetime import datetime
from calendar import calendar
from enum import unique
from statistics import pstdev
from venv import create

from werkzeug.security import generate_password_hash, check_password_hash

import addDevelopment
import viewLecturers, editLecturer, addLecturer, deleteLecturer, viewSubjects, editSubject, addSubject, deleteSubject, viewSchedule, manageSchedule, viewInstance, workload
from flask import Flask, render_template, request
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.utils import redirect

now = datetime.now()
year = now.year
month = now.strftime("%B")
date = {
    "year": year,
    "month": month
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tcss.db"
app.config['SECRET_KEY'] = '26350e389debee0ff7f0a893c78cb2b1cd3519c31957af3866171d5e30ce0941'
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    account_level = db.Column(db.Integer())
    enabled = db.Column(db.Boolean, default=True)

    def get_id(self):
        return self.id

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.html'

@login_manager.user_loader
def load_user(email):
    db.engine.dispose()
    db.engine.connect()
    return User.query.get(email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        print(user.id)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/home')
        else:
            msg="Incorrect Credentials"
            return render_template('login.html', msg=msg)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html')

@app.route('/')
@app.route('/home')
def home_page():
    if current_user.is_authenticated:
        account_level = current_user.account_level
        if account_level < 3:
            return redirect('/manage_schedule')
        else:
            return redirect('/view_schedule')
    else:
        return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    account_level = current_user.account_level
    return render_template('dashboard.html', account_level=account_level)

# MANAGE LECTURERS (VIEW/EDIT/DELETE/ADD)
@app.route('/view_lecturers')
def view_lecturers():
    account_level = current_user.account_level
    lecturer_data = viewLecturers.generate_lecturer_data()
    return render_template('fulltimelecturers.html', date=date, lecturer_data=lecturer_data, account_level=account_level)

@app.route('/edit_lecturer', methods=['GET','POST'])
def edit_lecturer():
    account_level = current_user.account_level
    if request.method == 'POST':
        lecturer_id = request.form['lecturer_id']
        lecturer = editLecturer.generate_lecturer_data(lecturer_id)
        subjects = editLecturer.generate_subject_data()
        sme = editLecturer.generate_sme(lecturer_id)

        return render_template('edit_lecturer.html',lecturer_id=lecturer_id,lecturer=lecturer, subjects=subjects, sme=sme, account_level=account_level)

@app.route('/update_lecturer', methods=['GET','POST'])
def update_lecturer():
    account_level = current_user.account_level
    if request.method == 'POST':
        lect_id = request.form['lecturer_id']
        name = request.form['lecturer_name']
        workload = request.form['lecturer_workload']
        sme = request.form.getlist('sme')

        editLecturer.update_lecturer(lect_id, name, workload, sme)

        return redirect('/view_lecturers')

@app.route('/delete_lecturer', methods=['GET','POST'])
def delete_lecturer():
    account_level = current_user.account_level
    if request.method == 'POST':
        lecturer_id = request.form['lecturer_id']
        lecturer = editLecturer.generate_lecturer_data(lecturer_id)

        return render_template('/delete_lecturer.html', lecturer=lecturer, account_level=account_level)

@app.route('/confirm_delete_lecturer', methods=['GET','POST'])
def confirm_delete_lecturer():
    account_level = current_user.account_level
    if request.method == 'POST':
        lecturer_id = request.form['lecturer_id']

        deleteLecturer.delete_lecturer(lecturer_id)

        return redirect('/view_lecturers')

@app.route('/add_lecturer', methods=['GET','POST'])
def add_lecturer():
    account_level = current_user.account_level
    if request.method == 'POST':
        name = request.form['lecturer_name']
        workload = request.form['lecturer_workload']
        sme = request.form.getlist('sme')

        addLecturer.add_lecturer(name, workload, sme)

        return redirect('/view_lecturers')

    subjects = editLecturer.generate_subject_data()
    return render_template('/add_lecturer.html', subjects=subjects, account_level=account_level)

# MANAGE SUBJECTS (VIEW/EDIT/DELETE/ADD)
@app.route('/view_subjects')
def view_subjects():
    account_level = current_user.account_level
    subjects = viewSubjects.generate_subject_data()
    return render_template('/view_subjects.html', subjects=subjects, account_level=account_level)

@app.route('/edit_subject', methods=['GET','POST'])
def edit_subject():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        subject = editSubject.generate_subject_data(subject_id)

        return render_template('edit_subject.html', subject=subject, account_level=account_level)

@app.route('/update_subject', methods=['GET','POST'])
def update_subject():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        code = request.form['subject_code']
        name = request.form['subject_name']

        editSubject.update_subject(subject_id,code,name)
        return redirect('/view_subjects')

@app.route('/add_subject', methods=['GET','POST'])
def add_subject():
    account_level = current_user.account_level
    if request.method == 'POST':
        code = request.form['subject_code']
        name = request.form['subject_name']
        instance_count = 0

        addSubject.add_subject(code,name,instance_count)
        return redirect('/view_subjects')

    return render_template('/add_subject.html',account_level=account_level)

@app.route('/delete_subject', methods=['GET','POST'])
def delete_subject():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        subject = editSubject.generate_subject_data(subject_id)
        return render_template('/delete_subject.html', subject=subject, account_level=account_level)

@app.route('/confirm_delete_subject', methods=['GET','POST'])
def confirm_delete_subject():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        deleteSubject.delete_subject(subject_id)
        return redirect('/view_subjects')

@app.route('/view_schedule')
def view_schedule():
    account_level = current_user.account_level
    lecturer = viewSchedule.get_lecturer(current_user.id)
    all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    try:
        schedule_dates, lecturer_instances, assistant_instances, development_instances = viewSchedule.generate_schedule(current_user.id)
    except:
        lecturer_instances = False
        assistant_instances = False
        development_instances = False
        schedule_dates = False
    return render_template('/schedule.html',all_months=all_months, date=date, lecturer=lecturer,lecturer_instances=lecturer_instances,assistant_instances=assistant_instances,development_instances=development_instances, schedule_dates=schedule_dates, account_level=account_level)

@app.route('/manage_schedule')
def manage_schedule():
    account_level = current_user.account_level
    schedule_data = manageSchedule.generate_schedule_data()
    calendar_dates = manageSchedule.generate_calendar_dates()
    return render_template('/manage_schedule2.html', schedule_data=schedule_data,
                           calendar_dates=calendar_dates, account_level=account_level)

@app.route('/view_instance', methods=['GET','POST'])
def view_instance():
    account_level = current_user.account_level
    if request.method == 'POST':
        instance_id = request.form['instance_id']
        instance_data, possible_lecturers = viewInstance.generate_instance_data(instance_id)
        assigned_staff = viewInstance.generate_assigned_lecturers(instance_id)
        return render_template('/view_instance.html',instance_data=instance_data,
                               assigned_staff=assigned_staff, possible_lecturers=possible_lecturers,
                               instance_id=instance_id, account_level=account_level)

@app.route('/update_instance', methods=['GET','POST'])
def update_instance():
    account_level = current_user.account_level
    if request.method == 'POST':
        instance_id = request.form['instance_id']
        lecturer_id = request.form['lecturer_id']
        assistant_id = request.form['assistant_id']
        student_count = request.form['student_count']
        manageSchedule.update_instance(instance_id, lecturer_id, assistant_id, student_count)
        workload.calculate_instance_load()
        instance_data, possible_lecturers = viewInstance.generate_instance_data(instance_id)
        assigned_staff = viewInstance.generate_assigned_lecturers(instance_id)
        return render_template('/view_instance.html', instance_data=instance_data,
                               assigned_staff=assigned_staff, possible_lecturers=possible_lecturers,
                               instance_id=instance_id, account_level=account_level)

@app.route('/new_instance', methods=['GET', 'POST'])
def new_instance():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = int(request.form['subject_id'])
        possible_lecturers, subject_data, years = viewInstance.generate_create_new_data(subject_id)
        return render_template('create_instance.html', subject_data=subject_data,
                            possible_lecturers=possible_lecturers, years=years, account_level=account_level)

@app.route('/year_select', methods=['GET','POST'])
def year_select():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        selected_year = int(request.form['instance_year'])
        months = viewInstance.generate_possible_months(subject_id, selected_year)
        possible_lecturers, subject_data, years = viewInstance.generate_create_new_data(subject_id)
        return render_template('create_instance.html', selected_year=selected_year, subject_data=subject_data,
                            possible_lecturers=possible_lecturers, years=years, months=months, account_level=account_level)

@app.route('/create_instance', methods=['GET','POST'])
def create_instance():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id2']
        student_count = request.form['student_count']
        instance_month = request.form['instance_month']
        instance_year = request.form['instance_year2']
        workload.calculate_instance_load()
        manageSchedule.create_instance(subject_id,student_count,instance_month,instance_year)
        return redirect('/manage_schedule')

@app.route('/delete_instance', methods=['GET','POST'])
def delete_instance():
    account_level = current_user.account_level
    if request.method == 'POST':
        instance_id = request.form['delete_id']
        manageSchedule.delete_instance(instance_id)
        return redirect('/manage_schedule')

@app.route('/add_development', methods=['GET','POST'])
def add_development():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        subject = editSubject.generate_subject_data(subject_id)
        dates = addDevelopment.generate_dates()
        return render_template('/add_development.html', account_level=account_level, subject=subject, dates=dates)

@app.route('/year_select_dev', methods=['GET','POST'])
def year_select_dev():
    account_level = current_user.account_level
    if request.method == 'POST':
        dev_year = request.form['dev_year']
        months = addDevelopment.generate_months(dev_year)
        subject_id = request.form['subject_id']
        selected_year = int(request.form['dev_year'])
        subject = editSubject.generate_subject_data(subject_id)
        dates = addDevelopment.generate_dates()
        return render_template('/add_development.html', account_level=account_level, subject=subject, dates=dates, months=months, selected_year=selected_year)

@app.route('/month_select_dev', methods=['GET','POST'])
def month_select_dev():
    account_level = current_user.account_level
    if request.method == 'POST':
        dev_year = request.form['dev_year2']
        months = addDevelopment.generate_months(dev_year)
        dev_month = request.form['dev_month']
        subject_id = request.form['subject_id']
        selected_year = int(dev_year)
        selected_month = dev_month
        subject = editSubject.generate_subject_data(subject_id)
        dates = addDevelopment.generate_dates()
        possible_lecturers = addDevelopment.generate_possible_lecturers(subject_id, dev_year, dev_month)

        return render_template('/add_development.html', account_level=account_level, subject=subject, dates=dates, months=months, selected_year=selected_year, selected_month=selected_month, possible_lecturers=possible_lecturers)

@app.route('/submit_dev', methods=['GET','POST'])
def submit_dev():
    account_level = current_user.account_level
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        start_id = request.form['start_id']
        lecturer_id = request.form['lecturer_id']
        addDevelopment.add_development(subject_id,start_id,lecturer_id)
        return redirect('/view_subjects')

@app.route('/manage_development')
def manage_development():
    account_level = current_user.account_level
    development_instances = addDevelopment.get_instances()
    return render_template('/manage_development.html', account_level=account_level, development_instances=development_instances)

@app.route('/delete_development', methods=['GET','POST'])
def delete_development():
    account_level = current_user.account_level
    if request.method == 'POST':
        instance_id = request.form['instance_id']
        instance = addDevelopment.get_instance(instance_id)
        return render_template('/delete_development.html', account_level=account_level, instance=instance)

@app.route('/confirm_delete_development', methods=['GET','POST'])
def confirm_delete_development():
    account_level = current_user.account_level
    if request.method == 'POST':
        instance_id = request.form['instance_id']
        addDevelopment.delete_development(instance_id)
        development_instances = addDevelopment.get_instances()
        return render_template('/manage_development.html', account_level=account_level,
                               development_instances=development_instances)

def create_user(email, password, account_level):
    new_user = User(email=email, password=generate_password_hash(password, method='sha256'), account_level=account_level)
    db.session.add(new_user)
    db.session.commit()
    return
#
# def delete_user(user):
#     db.session.delete(user)
#     db.session.commit()

if __name__ == '__main__':
    app.run(port=8080)