from geniusapp import app,login_manager,db,logging,csrf
from flask import Flask,render_template,request,url_for,flash,session,\
    make_response,redirect,abort,json,jsonify,render_template_string,abort
from geniusapp.model.tables import User_roles, Users,Subjects,Courses,Courses_mapper,\
Broadcast_classe_stream_records, Teacher_assing_course,Online_classes,\
Student_subscribe_courses,Chat,Ban_chat_users,Online_demo_classes,\
Pac_course,Pac_optional_subjects,Pac_compulsory_subjects,\
Student_package_subscription,Student_subs_pac_months,Student_subs_pac_optional,Months,Subscription_trans_log,Seminars, \
    Seminar_details,Seminar_attend
from flask_login import current_user,login_required
from geniusapp.dashboard.form import StudentSelectCourse
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from slugify import slugify
from _ast import Param
from functools import wraps
import random
import string
from werkzeug.utils import secure_filename
import os
from os.path import splitext

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get((int(user_id)))

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.user_role_id == 1:
            return f(*args, **kwargs)
        else:
            abort(401)
    return wrap

@app.route('/admin/subscription-students-report',methods=['POST','GET'])
@login_required
@admin_required
def subscription_students_report():

    if request.method=='POST':
        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        subs_type =  request.form.getlist('subs_type') or ''
        try:
            subs_arr=[]
            if subs_type:
                for sub in subs_type:
                    subs_arr.append(sub)
            if subs_arr:
                records = db.session.execute("Select student_package_subscription.* , users.first_name, users.last_name,\
                    users.mobile, users.email, pac_course.seo_title from student_package_subscription join users on \
                    student_package_subscription.student_id=users.id join pac_course on\
                    pac_course.id=student_package_subscription.package_id \
                    where payment_date between '"+start_date+"' and '"+end_date+"' and purpose in :param3",\
                        {"param3":subs_arr}).fetchall()
            else:
                records = db.session.execute("Select student_package_subscription.* , users.first_name, users.last_name,\
                    users.mobile, users.email, pac_course.seo_title from student_package_subscription join users on \
                    student_package_subscription.student_id=users.id join pac_course on\
                    pac_course.id=student_package_subscription.package_id \
                    where payment_date between '"+start_date+"' and '"+end_date+"'").fetchall()

            resp = make_response(render_template('admin/reports/subscription-students.html',records=records))
            return resp  
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)

    resp = make_response(render_template('admin/reports/subscription-students.html'))
    return resp   

  
@app.route('/admin/student-pac-report', methods=['POST','GET'])
@login_required
@admin_required
def student_pac_report():

    if request.method=='POST':
        stu_id = request.form.get('stu_id')
        subs_type =  request.form.getlist('subs_type') or ''
        subs_arr=[]
        if subs_type:
            for sub in subs_type:
                subs_arr.append(sub)
        try:
            if subs_arr:
                records = db.session.execute("Select student_package_subscription.* , users.first_name, users.last_name,\
                    users.mobile, users.email, pac_course.seo_title from student_package_subscription join users on\
                    student_package_subscription.student_id=users.id join pac_course on\
                    pac_course.id=student_package_subscription.package_id\
                    where student_package_subscription.student_id=:param1 and purpose in :param2",{"param1":stu_id,"param2":subs_arr}).fetchall()
            else:
                records = db.session.execute("Select student_package_subscription.* , users.first_name, users.last_name,\
                    users.mobile, users.email, pac_course.seo_title from student_package_subscription join users on\
                    student_package_subscription.student_id=users.id join pac_course on\
                    pac_course.id=student_package_subscription.package_id\
                    where student_package_subscription.student_id=:param1 ",{"param1":stu_id}).fetchall()

            students = Users.query.filter_by(online_register=True,is_active=True).all()
            resp = make_response(render_template('admin/reports/student-pac-report.html', students=students,records=records))
            return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)

    students = Users.query.filter_by(online_register=True,is_active=True).all()
    resp = make_response(render_template('admin/reports/student-pac-report.html', students=students))
    return resp
