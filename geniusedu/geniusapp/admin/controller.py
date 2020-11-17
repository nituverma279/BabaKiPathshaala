from geniusapp import app,login_manager,db,logging
from flask import current_app,render_template,request,url_for,flash,session,make_response,redirect,abort,render_template_string,json,jsonify
from geniusapp.model.tables import User_roles, Users,Subjects,Courses,Courses_mapper,Teacher_assing_course,\
Student_subscribe_courses,Student_select_course,Contact_us,Online_classes,Online_demo_classes,\
Users_demo,Demo_student_attendence,Pac_course,Pac_compulsory_subjects,Pac_optional_subjects,Months,\
Student_package_subscription,Student_subs_pac_months,Student_subs_pac_optional,Seminars,Seminar_details,\
Seminar_attend,Subscription_trans_log,Broadcast_classe_stream_records,Broadcast_demo_classe_stream_records,Wallet,\
    Wallet_withdrawal_request, Wallet_trans_log, Referral_setting
from flask_login import login_user, current_user,login_required,logout_user
from geniusapp.admin.form import AdminLoginForm, AddSubjects,AddCourse,CoursesMapper,AddTeacher,\
AssignTeacherCourse,AssignStudentCourse,AddStudentForm,StudentResetPassForm,AdminResetPassForm,\
AddPackSubject,SeminarForm, ReferralSettingForm

from functools import wraps
from werkzeug.security import generate_password_hash
from sqlalchemy.sql.expression import null, desc
from _ast import Param
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from slugify import slugify
from _ast import Param
import random
import string
from werkzeug.utils import secure_filename
import os
from os.path import splitext


basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAC_COVER_BANNER = basedir+'/static/upload/package/'
SEMINAR_COVER_BANNER = basedir+'/static/upload/seminar/'


def randomkey(stringLength=10):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))

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

@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
     
    if request.method == 'POST':
        form = AdminLoginForm(request.form)
        if form.validate()== False:
            resp = make_response(render_template('admin/security/login.html',form=form))
            return resp
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            try:
                user = Users.query.filter_by(email=email).first()
                if user and user.check_password(request.form['password']):
                    login_user(user)
                    resp = make_response(redirect(url_for('admin_dashboard')))
                    return resp
                else:
                    flash(u"You have enter wrong email or passsord","danger")
                    resp = make_response(redirect(url_for('admin_login')))
                    return resp
            except Exception as e:
                return str(e)
    else:
        try:
            form = AdminLoginForm(request.form)
            resp = make_response(render_template('admin/security/login.html',form=form))
            return resp     
        except Exception as e:
            app.logger.error('Error: %s'%(str(e)))  
            return 'Template not found.'

@app.route('/admin/update-password',methods=['POST','GET'])
@login_required
@admin_required
def admin_update_password():

    if request.method=='POST':
        form =AdminResetPassForm(request.form)
        if form.validate()== False:
            resp = make_response(render_template('admin/security/update-password.html',form=form))
            return resp
        else:
            try:
                user = Users.query.filter_by(id=current_user.id).first()
                if user and user.check_password(request.form['old_password']):
                    user.password=generate_password_hash(request.form.get('new_password'))
                    db.session.commit()
                    flash('{0}, Your password is updated succesfully.'.format(current_user.first_name.title()),'success')
                    return make_response(redirect(url_for('admin_update_password')))
                else:
                    flash('Your old password is not valid','danger')
                    return redirect(url_for('admin_update_password'))
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
    else:
        form =AdminResetPassForm(request.form)
        resp = make_response(render_template('admin/security/update-password.html',form=form))
        return resp


@app.route('/admin/logout')
def admin_logout():
    logout_user()
    flash('You are succesfully logout.','success')
    resp = make_response(redirect(url_for('admin_login')))
    return resp

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    try:
        total_teachers = db.session.query(Users.id).filter_by(user_role_id=3).count()
        # total_students = db.session.query(Users.id).filter_by(user_role_id=4).count()
        total_students = db.session.execute("SELECT users.*, student_select_course.course_id, courses.course_name FROM \
                    users JOIN student_select_course ON users.id=student_select_course.user_id JOIN courses ON\
                    courses.id=student_select_course.course_id WHERE users.user_role_id=4 order by users.id desc").fetchall()

        total_courses = db.session.query(Courses.id).filter_by(is_active=True).count()
        total_subjects = db.session.query(Subjects.id).filter_by(is_active=True).count()

        student_subs_pac_list = Student_package_subscription.query.order_by(Student_package_subscription.id.desc()).all()
        if student_subs_pac_list:
            total_earn_subs=0
            for subs in student_subs_pac_list:
               total_earn_subs = total_earn_subs+subs.total_payable_amount


        resp = make_response(render_template('admin/dashboard.html',total_teachers=total_teachers,total_students=total_students,\
            total_courses=total_courses,total_subjects=total_subjects,student_subs_pac_list=student_subs_pac_list,total_earn_subs=total_earn_subs))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/admin/add-subject',methods=['GET','POST'])
@login_required
@admin_required
def add_subject():

    if request.method=='POST':
        form = AddSubjects(request.form)
        if form.validate()== False:
            subject_list = Subjects.query.all()
            resp = make_response(render_template('admin/add-subject.html', form=form,subject_list=subject_list))
            return resp
        else:
            try:
                subject_name = request.form.get('subject_name').title()
                subject = Subjects(subject_name=subject_name)
                db.session.add(subject)
                db.session.commit()
                flash('Subject {} is addedd to the list'.format(subject_name.title()),'success')
                resp = make_response(redirect(url_for('add_subject')))
                return resp
            except Exception as e:
                app.logger.error('Error: %s'%(str(e)))
                flash('Oops! something went wrong.','danger')
                return redirect('add-subject')
    else:
        try:
            form = AddSubjects()
            subject_list = Subjects.query.all()
            resp = make_response(render_template('admin/add-subject.html',form=form,subject_list=subject_list))
            return resp 
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


@app.route('/admin/delete-subject/<int:id>')
@login_required
@admin_required
def delete_subject(id):
    try:
        subject = Subjects.query.filter_by(id=id).delete()
        db.session.commit()
        resp = make_response(redirect(url_for('add_subject')))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)



@app.route('/admin/add-course',methods=['GET','POST'])
@login_required
@admin_required
def add_course():

    if request.method=='POST':
        form = AddCourse(request.form)
        if form.validate()== False:
            course_list = Courses.query.all()
            resp = make_response(render_template('admin/add-course.html', form=form,course_list=course_list))
            return resp
        else:
            try:
                course_name = request.form.get('course_name').title()
                course = Courses(course_name=course_name)
                db.session.add(course)
                db.session.commit()
                flash('Course {} is addedd to the list'.format(course_name.title()),'success')
                resp = make_response(redirect(url_for('add_course')))
                return resp
            except Exception as e:
                app.logger.error('Error: %s'%(str(e)))
                flash('Oops! something went wrong.','danger')
                return redirect('add-course')
    else:
        try:
            form = AddCourse()
            course_list = Courses.query.all()
            resp = make_response(render_template('admin/add-course.html',form=form, course_list=course_list))
            return resp 
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


@app.route('/admin/delete-course/<int:id>')
@login_required
@admin_required
def delete_course(id):
    try:
        course = Courses.query.filter_by(id=id).delete()
        db.session.commit()
        resp = make_response(redirect(url_for('add_course')))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


# @app.route('/admin/course-mapper',methods=['GET','POST'])
# @login_required
# @admin_required
# def course_mapper():
    
#     if request.method =='POST':
#         form = CoursesMapper(request.form)
#         course_id = request.form.get('course_id')
#         subject_id = request.form.get('subject_id') 
#         try:
#             course_mapper = Courses_mapper(course_id=course_id,subject_id=subject_id)
#             db.session.add(course_mapper)
#             db.session.commit()
#             flash("Course is mapped successfully.","success")
#             return make_response(redirect(url_for('course_mapper')))
#         except Exception as e:
#             app.logger.error('Error: %s'%(str(e)))
#             flash('Oops! something went wrong.','danger')
#             return make_response(redirect(url_for('course_mapper')))

#     else:
#         form = CoursesMapper()
#         form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
#         form.subject_id.choices = [(g.id, g.subject_name) for g in Subjects.query.order_by('subject_name')]
#         resp = make_response(render_template('admin/course-mapper.html',form=form))
#         return resp 



@app.route('/admin/create-course-package',methods=['GET','POST'])
@login_required
@admin_required
def create_course_package():

    if request.method =='POST':
        
        course_id = request.form.getlist('course_id')
        seo_title = request.form.get('seo_title')
        expire_month = request.form.get('expire_month')
        expire_year = request.form.get('expire_year')
        cover_banner =  request.files['cover_banner']
        description = request.form.get('description')
        price = request.form.get('price')
        is_crash_course = request.form.get('is_crash_course')
        discount_amt=0
        if is_crash_course:
            discount_amt = request.form.get('discount_amt')

        if cover_banner:
            
            try:
                filename=secure_filename(cover_banner.filename)
                filetype, extension = splitext(filename)
                newfilename =  str(randomkey(10)).lower() + extension
                cover_banner.save(os.path.join(PAC_COVER_BANNER, newfilename)) 
                cover_path='/static/upload/package/'+newfilename
                course_pac_details = Pac_course(course_id=course_id,seo_title=seo_title,\
                    cano_url=seo_title,cover_banner=cover_path,description=description,price=price,is_crash_course=is_crash_course, discount_amt=discount_amt,expire_month=expire_month,expire_year=expire_year)
                db.session.add(course_pac_details)
                db.session.commit()

                new_course_pac = Pac_course.query.filter_by(id=course_pac_details.id).first()
                if new_course_pac:
                    new_course_pac.cano_url=slugify(seo_title)+'-'+str(course_pac_details.id)
                    db.session.commit()

                flash('Package is created successfully','success')
                return redirect(url_for('create_course_package'))
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
        else:
            flash('Cover banner is required','danger')
            return redirect(url_for('create_course_package'))

    else:
        form = CoursesMapper()
        form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
        form.expire_month.choices = [(g.id, g.month_name) for g in Months.query.order_by('id')]
        resp = make_response(render_template('admin/create-course-package.html',form=form))
        return resp


@app.route('/admin/all-course-package')
@login_required
@admin_required
def all_course_package():

    try:
        course_package_list = Pac_course.query.order_by(Pac_course.id.desc()).all()
        resp = make_response(render_template('admin/all-course-package.html',course_package_list=course_package_list))  
        return resp
    except Exception as e:
        app.logger.error('Error: %s'%(str(e)))
        flash('Oops! something went wrong.','danger')
        return abort(500)



""" Update package details """
@app.route('/admin/package/update/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def update_package(id):

    if request.method == 'POST':
        course_id = request.form.getlist('course_id')
        seo_title = request.form.get('seo_title')
        expire_month = request.form.get('expire_month')
        expire_year = request.form.get('expire_year')
        cover_banner = request.files.get('cover_banner', None) #request.files['cover_banner_field']
        description = request.form.get('description')
        price = request.form.get('price')
        try:
            course_package = Pac_course.query.filter_by(id=id).first()
        except Exceptoin as e:
            app.logger.error(str(e))
            return abort(500)

        if course_package:
            if cover_banner:

                filename = secure_filename(cover_banner.filename)
                filetype, extension = splitext(filename)
                newfilename = str(randomkey(10)).lower() + extension
                cover_banner.save(os.path.join(PAC_COVER_BANNER, newfilename))
                cover_path = '/static/upload/package/' + newfilename

                course_package.course_id=course_id
                course_package.seo_title=seo_title
                course_package.cano_url=slugify(seo_title)+'-'+str(id)
                course_package.description=description
                course_package.price=price
                course_package.expire_month=expire_month
                course_package.expire_year=expire_year
                course_package.cover_banner = cover_path

                db.session.commit()
                db.session.close()
            else:


                course_package.course_id = course_id
                course_package.seo_title = seo_title
                course_package.cano_url = slugify(seo_title)+'-'+str(id)
                course_package.description = description
                course_package.price = price
                course_package.expire_month = expire_month
                course_package.expire_year = expire_year

                db.session.commit()
                db.session.close()
            flash('Package Updated.','success')
            return redirect(url_for('all_course_package'))
    else:
        try:
            course_package = Pac_course.query.filter_by(id=id).first()
            if course_package:
                form = CoursesMapper(obj=course_package)
                form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
                form.expire_month.choices = [(g.id, g.month_name) for g in Months.query.order_by('id')]
                return render_template('admin/update-package.html', form=form)
            else:
                flash('Sorry, course pacakge is not available.','danger')
                return redirect(url_for('all_course_package'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


@app.route('/admin/package/<int:pid>',methods=['GET','POST'])
@login_required
@admin_required
def package_details(pid):

    try:
        course_package=Pac_course.query.filter_by(id=pid).first()
    except Exception as e:
        app.logger.error(str(e))
        flash('Oops! something went wrong.','danger')
        return abort(500)

    if request.method=='POST':

        pac_course_id = request.form.get('pac_course_id')
        comp_subject_id = request.form.get('comp_subject_id')
        comp_price = request.form.get('comp_price') or 0
        opt_subject_id = request.form.get('opt_subject_id')
        opt_price = request.form.get('opt_price') or 0

        if opt_subject_id !='0':
            if db.session.query(Pac_optional_subjects.id).filter_by(pac_course_id=course_package.id,subject_id=opt_subject_id).scalar() is None:
                pac_opt=Pac_optional_subjects(pac_course_id=course_package.id,subject_id=opt_subject_id,price=opt_price)
                db.session.add(pac_opt)
                db.session.commit()
            else:
                flash('Dulplicate Entry','danger')
                return redirect(url_for('package_details',pid=pid))

        if comp_subject_id !='0':
            if db.session.query(Pac_compulsory_subjects.id).filter_by(pac_course_id=course_package.id,subject_id=comp_subject_id).scalar() is None:    
                pac_comp=Pac_compulsory_subjects(pac_course_id=course_package.id,subject_id=comp_subject_id,price=comp_price)
                db.session.add(pac_comp)
                db.session.commit()
            else:
                flash('Dulplicate Entry ','danger')
                return redirect(url_for('package_details',pid=pid))

        flash('Subjects are added to the package successfully.','success')
        return redirect(url_for('package_details',pid=pid))
    else:
        try:
            form = AddPackSubject()
            form.comp_subject_id.choices = [('0', 'select an Compulsory Subject')] +[(g.id, g.subject_name) for g in Subjects.query.order_by('subject_name')]
             
            form.opt_subject_id.choices = [('0', 'select an optional Subject')] +[ (g.id, g.subject_name) for g in Subjects.query.order_by('subject_name')]

            comp_sub_list = Pac_compulsory_subjects.query.filter_by(pac_course_id=pid).all()
            opt_sub_list = Pac_optional_subjects.query.filter_by(pac_course_id=pid).all()
            resp = make_response(render_template('admin/package-details.html',form=form,course_package=course_package,comp_sub_list=comp_sub_list,opt_sub_list=opt_sub_list))
            return resp
        except Exception as e:
            app.logger.error(str(e))
            flash('Oops! something went wrong.','danger')
            return abort(500)

@app.route('/admin/package/<int:pid>/<int:subid>/<string:subjectType>')
@login_required
@admin_required
def delete_package_details(pid,subid,subjectType):
    try:
        if subjectType=='comp':
            pac_comp_sub=Pac_compulsory_subjects.query.filter_by(pac_course_id=pid,subject_id=subid).delete()
            db.session.commit()
            flash('Delete successfully','success')
        elif subjectType=='opt':
            pac_opt_sub=Pac_optional_subjects.query.filter_by(pac_course_id=pid,subject_id=subid).delete()
            db.session.commit()
            flash('Delete successfully','success')
        else:
            flash('There is no details available','danger')
        return redirect(url_for('package_details',pid=pid))
    except Exception as e:
        app.logger.error(str(e))
        flash('Oops! something went wrong.','danger')
        return abort(500)

@app.route('/admin/update-course-pac-status',methods=['POST'])
@login_required
@admin_required
def update_course_pac_status():
    if request.method=='POST':

        pid = request.form.get('pid')
        status = ''
        if request.form.get('status')=='1': 
            status = True
        else: 
            status = False
        try:
            course_package = Pac_course.query.filter_by(id=pid).first()
            if course_package:
                course_package.is_active = status
                db.session.commit()
                info = {"error":0,"message":'status updated'}
                return jsonify(info)
            else:
                info =  {'error':1,'message':'course package is not available'}
                return jsonify(info)
        except Exception as e:
            app.logger.error('Error: %s'%(str(e)))
            info =  {'error':1,'message':'Oops! something went wrong.'}
            return jsonify(info)
    else:
        info =  {'error':1,'message':'method is not allowed.'}
        return jsonify(info)




        

# End of package












@app.route('/admin/add-teacher',methods=['GET','POST'])
@login_required
@admin_required
def add_teacher():

    if request.method=='POST':
        form = AddTeacher(request.form)
        if form.validate()== False:
            resp = make_response(render_template('admin/add-teacher.html', form=form))
            return resp
        else:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            gender = request.form.get('gender')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            parent_mobile = request.form.get('parent_mobile')
            password = request.form.get('password')
            user_role_id = 3
            ic_number = request.form.get('ic_number')
            zipcode = request.form.get('zipcode') or 0
            address = request.form.get('address')
            online_register=0

            try:
                user = Users(first_name=first_name,last_name=last_name,gender=gender,email=email,mobile=mobile,parent_mobile=parent_mobile,password=password,user_role_id=user_role_id,zipcode=zipcode,address=address, online_register=online_register)
                db.session.add(user)
                db.session.commit()
                if user.id:
                    flash('{} is registered successfully. '.format(first_name.title()),'success')
                    resp = make_response(redirect(url_for('add_teacher')))
                    return resp
                else:
                    flash('Oops! Fatal issue in processing. Please try after some time.','danger')
                    resp = make_response(redirect(url_for('add_teacher')))
                    return resp
            except Exception as e:
                app.logger.error('Error: %s'%(str(e)))
                return abort(500)
    else:
        try:
            form = AddTeacher()
            resp = make_response(render_template('admin/add-teacher.html',form=form))
            return resp
        except Exception as e:
            app.logger.error('Error: {}'.format(str(e)))
            return abort(500)

@app.route('/admin/delete-teacher/<int:id>')
@login_required
@admin_required
def delete_teacher(id):
    try:
        teacher=Users.query.filter_by(id=id,user_role_id=3).delete()
        db.session.commit()
        resp = make_response(redirect(url_for('teacher_list')))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/admin/teacher-list')
@login_required
@admin_required
def teacher_list():
    try:
        teacher_list = Users.query.filter_by(user_role_id=3).order_by(Users.id.desc()).all()
        resp = make_response(render_template('admin/teacher-list.html',teacher_list=teacher_list))
        return resp
    except Exception as e:
        app.logger.error('Error: {}'.format(str(e)))
        return abort(500)

@app.route('/admin/assign-course-teacher/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def assign_course_teacher(id):
    if request.method=='POST':
        try:
            user_id = id
            course_id = request.form.get('course_id')
            subject_id = request.form.get('subject_id') 
            if db.session.query(Teacher_assing_course.id).filter_by(user_id=user_id,course_id=course_id,subject_id=subject_id).scalar() is None:
                assing_course = Teacher_assing_course(user_id=user_id,course_id=course_id,subject_id=subject_id)
                db.session.add(assing_course)
                db.session.commit()
                flash("Course is assinged successfully.",'success')
                resp = make_response(redirect(url_for('assign_course_teacher',id=id)))
                return resp
            else:
                flash('Course is alreay assigned.','danger')
                resp = make_response(redirect(url_for('assign_course_teacher',id=id)))
                return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        try:
            user_id=id
            user = Users.query.filter_by(id=user_id).first()
            form = AssignTeacherCourse()
            form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
            form.subject_id.choices = [(g.id, g.subject_name) for g in Subjects.query.order_by('subject_name')]
            teacher_assing_course = Teacher_assing_course.query.filter_by(user_id=user_id).all()
            resp = make_response(render_template('admin/assign-course-teacher.html',form=form,user=user,teacher_assing_course=teacher_assing_course))
            return resp 
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)

@app.route('/admin/delete-assign-course/<int:id>/<int:tid>')
@login_required
@admin_required
def delete_assign_course(id,tid):
    try:
        delete_assign_course= Teacher_assing_course.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect(url_for('assign_course_teacher',id=tid))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/admin/add_student',methods=['GET','POST'])
@login_required
@admin_required
def add_student():

    if request.method=='POST':
        form = AddStudentForm(request.form)
        form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
        if form.validate()== False:

            resp = make_response(render_template('admin/add-student.html', form=form))
            return resp
        else:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            gender = request.form.get('gender')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            parent_mobile = request.form.get('parent_mobile') or 0
            password = request.form.get('password')
            user_role_id = 4
            zipcode = request.form.get('zipcode') or 0
            address = request.form.get('address')
            course_id = request.form.get('course_id')
            online_register=0

            try:
                user = Users.query.filter_by(mobile=mobile).first()
                if user:
                    flash(f'Sorry mobile number {mobile} is registered alreay. Please try with another mobile number.','danger')
                    form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
                    resp = make_response(render_template('admin/add-student.html',form=form))
                    return resp
                else:
                    user = Users(first_name=first_name,last_name=last_name,gender=gender,email=email,mobile=mobile,parent_mobile=parent_mobile,password=password,user_role_id=user_role_id,zipcode=zipcode,address=address,online_register=online_register)
                    db.session.add(user)
                    db.session.commit()
                    db.session.close()

                    if user.id:
                        stu_select_course=Student_select_course(user_id=user.id,course_id=course_id)
                        db.session.add(stu_select_course)
                        db.session.commit()
                        db.session.close()
                        flash('{} is registered successfully. '.format(first_name.title()),'danger')
                        resp = make_response(redirect(url_for('add_student')))
                        return resp
                    else:
                        flash('Oops! something went wrong.. Please try after some time.','danger')
                        resp = make_response(redirect(url_for('add_student')))
                        return resp
            except Exception as e:
                app.logger.error('Error: %s'%(str(e)))
                return abort(500)
    else:
        try:
            form = AddStudentForm()
            form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
            resp = make_response(render_template('admin/add-student.html',form=form))
            return resp
        except Exception as e:
            app.logger.error('Error: {}'.format(str(e)))
            return abort(500)

@app.route('/admin/student-list')
@login_required
@admin_required
def student_list():
    try:
        courses_list = Courses.query.filter_by(is_active=True).all()
        student_list = db.session.execute("SELECT users.*, student_select_course.course_id, courses.course_name FROM \
                    users JOIN student_select_course ON users.id=student_select_course.user_id JOIN courses ON\
                    courses.id=student_select_course.course_id WHERE users.user_role_id=4 order by users.id desc")
        resp = make_response(render_template('admin/student-list.html',student_list=student_list,courses_list=courses_list))
        return resp
    except Exception as e:
        app.logger.error('Error: {}'.format(str(e)))
        return abort(500)


@app.route('/admin/filter-student-list',methods=['POST'])
@login_required
@admin_required
def filter_student_list():
    try:
        course_id=request.form.get('course_id')
        student_list =db.session.execute("SELECT users.*, student_select_course.course_id, courses.course_name FROM \
                    users JOIN student_select_course ON users.id=student_select_course.user_id JOIN courses ON\
                    courses.id=student_select_course.course_id WHERE users.user_role_id=4 and courses.id=:param order by users.id desc",{"param":course_id})
        resp = '''
                {%for student in student_list%}
                    <tr>
                        <td>{{loop.index}}</td>
                        <td>{{student.course_name}}</td>
                        <td>{{student.first_name}} {{student.last_name}}</td>
                        <td>{{student.email}}</td>
                        <td>{{student.gender}}</td>
                        <td>{{student.mobile}}</td>
                        <td>
                            <a href="{{url_for('assign_course_student',id=student.id)}}">Assign</a>
                        </td>
                        <td>
                            <a href="{{url_for('delete_student', id=student.id)}}" onclick="return confirm('Are you sure?')"><i class="fa fa-times"></i></a>
                            <a href="{{url_for('edit_student', id=student.id)}}"">
                            <i class="fa fa-edit"></i></a>
                            <a href="{{url_for('update_student_password', id=student.id)}}"">
                                <i class="fa fa-key"></i></a>
                        </td>
                    </tr>
                {%endfor%}
                '''
        return render_template_string(resp,student_list=student_list)
        
    except Exception as e:
        app.logger.error('Error: {}'.format(str(e)))
        abort(500)

@app.route('/admin/delete-student/<int:id>')
@login_required
@admin_required
def delete_student(id):
    try:
        student=Users.query.filter_by(id=id,user_role_id=4).delete()
        db.session.commit()
        resp = make_response(redirect(url_for('student_list')))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/admin/update-student-password/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def update_student_password(id):
    if request.method=='POST':
        form =StudentResetPassForm(request.form)
        if form.validate()== False:
            resp = make_response(render_template('admin/security/update-student-password.html',form=form))
            return resp
        else:
            try:
                
                user = Users.query.filter_by(id=id).first()

                
                if user :
                    user.password=generate_password_hash(request.form.get('new_password'))
                    db.session.commit()
                    flash('{0}, Your password is updated succesfully.'.format(user.first_name.title()),'success')
                    return make_response(redirect(url_for('student_list')))
                else:
                    flash('User details is not valid','danger')
                    return redirect(url_for('update_student_password',id=id))
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
    else:
        form =StudentResetPassForm(request.form)
        resp = make_response(render_template('admin/security/update-student-password.html',form=form))
        return resp


@app.route('/admin/assign-course-student/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def assign_course_student(id):
    if request.method=='POST':
        try:
            user_id = id
            course_id = request.form.get('course_id')
            subject_id = request.form.get('subject_id') 
            if db.session.query(Student_subscribe_courses.id).filter_by(user_id=user_id,course_id=course_id,subject_id=subject_id).scalar() is None:
                assing_course = Student_subscribe_courses(user_id=user_id,course_id=course_id,subject_id=subject_id)
                db.session.add(assing_course)
                db.session.commit()
                db.session.close()
                flash("Course is assinged successfully.",'success')
                resp = make_response(redirect(url_for('assign_course_student',id=id)))
                return resp
            else:
                flash('Course is alreay assigned.','danger')
                resp = make_response(redirect(url_for('assign_course_student',id=id)))
                return resp
        except Exception as e:
            app.logger.error('Error: {}'.format(str(e)))
            return abort(500)
    else:
        try:
            user_id=id
            stu_sele_course = Student_select_course.query.filter_by(user_id=user_id).first()
            form = AssignStudentCourse()
            form.course_id.choices = [(g.id, g.course_name) for g in Courses.query.order_by('course_name')]
            form.subject_id.choices = [(g.id, g.subject_name) for g in Subjects.query.order_by('subject_name')]
            
            if stu_sele_course:
                student_course=db.session.execute('Select courses.course_name, student_select_course.course_id from courses join student_select_course on courses.id=student_select_course.course_id Where student_select_course.course_id=:param',{"param":stu_sele_course.course_id}).fetchone()
                form.course_id.default=stu_sele_course.course_id
            form.process()
            user = Users.query.filter_by(id=user_id).first()
            
            student_assing_course = Student_subscribe_courses.query.filter_by(user_id=user_id).all()
            resp = make_response(render_template('admin/assign-course-student.html',form=form,user=user,student_course=student_course, student_assing_course=student_assing_course))
            return resp 
        except Exception as e:
            app.logger.error('Error: {}'.format(str(e)))
            return abort(500)

@app.route('/admin/dashboard/delete-assing-course/<int:cid>/<int:sid>')
@login_required
@admin_required
def delete_assing_course(cid,sid):
    try:
        subs_course = Student_subscribe_courses.query.filter_by(id=cid).delete()
        db.session.commit()
        resp = make_response(redirect(url_for('assign_course_student',id=sid)))
        return resp 
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)
@app.route('/admin/edit-teacher/<int:id>',methods=['POST','GET'])
@login_required
@admin_required
def edit_teacher(id):
    
    user =Users.query.filter_by(id=id).first()
    form = AddTeacher(obj=user)
    if request.method=='POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        email = request.form.get('email')
        mobile = request.form.get('mobile') 
        ic_number = request.form.get('ic_number')

        user.first_name=first_name
        user.last_name=last_name
        user.gender=gender
        user.email=email
        user.mobile=mobile
        user.ic_number=ic_number
        
        db.session.commit()
        flash("{} has updated successfully".format(first_name.title()),'success')
        return redirect(url_for('teacher_list'))

    return render_template('admin/edit-teacher.html', form=form)

@app.route('/admin/edit-student/<int:id>',methods=['POST','GET'])
@login_required
@admin_required
def edit_student(id):

    user =Users.query.filter_by(id=id).first()
    form = AddStudentForm(obj=user)
    if request.method=='POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        email = request.form.get('email')
        mobile = request.form.get('mobile') 
        parent_mobile = request.form.get('parent_mobile')
        zipcode = request.form.get('zipcode')
        address = request.form.get('address')

        user.first_name=first_name
        user.last_name=last_name
        user.gender=gender
        user.email=email
        user.mobile=mobile
        user.parent_mobile=parent_mobile
        user.zipcode=zipcode
        user.address=address
        db.session.commit()
        flash("{} has updated successfully".format(first_name.title()),'success')
        return redirect(url_for('student_list'))
        
    return render_template('admin/edit-student.html', form=form)


@app.route('/admin/contact-queries')
@login_required
@admin_required
def contact_queries():
    try:
        contact_queries = Contact_us.query.order_by(Contact_us.id.desc()).all()
        resp = make_response(render_template('admin/contact-queries.html', contact_queries=contact_queries))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/admin/topics-list')
@login_required
@admin_required
def topics_list():
    try:
        topics_list = Online_classes.query.order_by(Online_classes.id.desc()).all()
        resp = make_response(render_template('admin/live-topics-list.html',topics_list=topics_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/admin/mark_as_complete_topic',methods=['POST'])
@login_required
@admin_required
def mark_as_complete_topic():
    if request.method=='POST':
        coid = request.form.get('coid')
        try:
            Livetopic = Online_classes.query.filter_by(id=coid,is_complete=False).first()
            if Livetopic:
                Livetopic.is_complete=True
                db.session.commit()
                return {'error':0,'message':'Mark as completed'}
            else:
                return {'error':1,'message':'Topic is already completed.'}
        except Exception as e:
            app.logger.error(str(e))
            return {'error':1,'message':'Oops something went wrong.'}
    else:
        return {'error':1,'message':'Method is not allowed.'}


@app.route('/admin/join-online-class/<int:id>')
@login_required
@admin_required
def join_online_class(id):
    try:
        Livetopic = Online_classes.query.filter_by(id=id).first()
        if Livetopic:
            subs_stu_course=Student_subscribe_courses.query.filter_by(course_id=Livetopic.course_id,subject_id=Livetopic.subject_id).order_by(Student_subscribe_courses.id.desc()).all()
            if subs_stu_course:
                resp = make_response(render_template('admin/student-join-class.html',subs_stu_course=subs_stu_course,Livetopic=Livetopic))
                return resp
            else:
                return redirect(url_for('topics_list'))
        else:
            return redirect(url_for('topics_list'))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)



@app.route('/demo_students')
@login_required
@admin_required
def demo_student_list():
    try:
        student_list = Users_demo.query.order_by(Users_demo.id.desc()).all()
        resp = make_response(render_template('admin/demo/student-list.html',student_list=student_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/demo-topics-list')
@login_required
@admin_required
def demo_topics_list():
    try:
        topics_list = Online_demo_classes.query.order_by(Online_demo_classes.id.desc()).all()
        resp = make_response(render_template('admin/demo/topic-list.html',topics_list=topics_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/admin/mark_as_complete_demo_topic',methods=['POST'])
@login_required
@admin_required
def mark_as_complete_demo_topic():
    if request.method=='POST':
        coid = request.form.get('coid')
        try:
            Livetopic = Online_demo_classes.query.filter_by(id=coid,is_complete=False).first()
            if Livetopic:
                Livetopic.is_complete=True
                db.session.commit()
                return {'error':0,'message':'Mark as completed'}
            else:
                return {'error':1,'message':'Topic is already completed.'}
        except Exception as e:
            app.logger.error(str(e))
            return {'error':1,'message':'Oops something went wrong.'}
    else:
        return {'error':1,'message':'Method is not allowed.'}

@app.route('/admin/join-online-demo-class/<int:id>')
@login_required
@admin_required
def join_online_demo_class(id):
    try:
        Livetopic = Online_demo_classes.query.filter_by(id=id).first()
        if Livetopic:
            # attendance = Demo_student_attendence.query.filter_by(topices_id=Livetopic.id).all()
            attendance = db.session.execute("SELECT demo_student_attendence.*, users_demo.first_name,users_demo.email,users_demo.mobile FROM demo_student_attendence JOIN users_demo on demo_student_attendence.student_id=users_demo.id where demo_student_attendence.topices_id=:param1",{"param1":Livetopic.id})
            resp = make_response(render_template('admin/demo/student-join-class.html',Livetopic=Livetopic, attendance_list=attendance))
            return resp   
        else:
            return redirect(url_for('demo_topics_list'))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/admin/add-member',methods=['GET','POST'])
@login_required
@admin_required
def add_member():

    if request.method=='POST':
        form = AddTeacher(request.form)
        if form.validate()== False:
            resp = make_response(render_template('admin/add-member.html', form=form))
            return resp
        else:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            gender = request.form.get('gender')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            parent_mobile = request.form.get('parent_mobile')
            password = request.form.get('password')
            user_role_id = request.form.get('user_role_id')
            zipcode = request.form.get('zipcode') or 0
            address = request.form.get('address') or ''

            try:
                user = Users(first_name=first_name,last_name=last_name,gender=gender,email=email,mobile=mobile,parent_mobile=parent_mobile,password=password,user_role_id=user_role_id,zipcode=zipcode,address=address,online_register=False)
                db.session.add(user)
                db.session.commit()
                db.session.close()
                if user.id:
                    flash('{} is registered successfully. '.format(first_name.title()),'success')
                    resp = make_response(redirect(url_for('add_member')))
                    return resp
                else:
                    flash('Oops! Fatal issue in processing. Please try after some time.','danger')
                    resp = make_response(redirect(url_for('add_member')))
                    return resp
            except Exception as e:
                app.logger.error(str(e))
                return str(e)
    else:
        try:
            form = AddTeacher()
            resp = make_response(render_template('admin/add-member.html',form=form))
            return resp
        except Exception as e:
            app.logger.error(str(e))
            return str(e)

@app.route('/admin/member-list')
@login_required
@admin_required
def member_list():
    try:
        # teacher_list = Users.query.filter_by(user_role_id=5).order_by(Users.id.desc()).all()
        member_list = db.session.execute("SELECT * FROM  users WHERE user_role_id in (2,5) and is_active=True").fetchall();
        resp = make_response(render_template('admin/member-list.html',member_list=member_list))
        return resp
    except Exception as e:
        app.logger.error('Error: {}'.format(str(e)))
        abort(500)

@app.route('/admin/delete-member/<int:id>')
@login_required
@admin_required
def delete_member(id):
    try:
        teacher=Users.query.filter_by(id=id).delete()
        db.session.commit()
        resp = make_response(redirect(url_for('member_list')))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        abort(500)


@app.route('/admin/subscription-students')
@login_required
@admin_required
def subscription_students():
    try:
        student_subs_pac_list = Student_package_subscription.query.filter_by(is_expired=False).order_by(Student_package_subscription.id.desc()).all()
        subs_pac_list=[]
        if student_subs_pac_list:
            for subs in student_subs_pac_list:
                filename, file_extension = splitext(subs.receipt)
                ist_time_str = subs.payment_date+datetime.timedelta(seconds=28800)
                payment_date = datetime.datetime.strptime(str(ist_time_str), "%Y-%m-%d %H:%M:%S")
                subs_pac_list.append({'id': subs.id, 'package_name': subs.package_name, 'student_name': subs.student_name, 'total_amount': subs.total_amount, \
                    'discount_amount': subs.discount_amount, 'total_payable_amount': subs.total_payable_amount, 'payment_date': payment_date, 'receipt': subs.receipt,\
                        'payment_status':subs.payment_status,'subs_status':subs.subs_status,'purpose':subs.purpose,'invoice':subs.invoice,'file_extension':file_extension.lower()})

        resp = make_response(render_template('admin/subscription-student-list.html',student_subs_pac_list=subs_pac_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/admin/update-stu-subs-pac-status',methods=['POST'])
@login_required
@admin_required
def update_stu_subs_pac_status():
    if request.method=='POST':

        pid = request.form.get('pid')
        status = ''
        if request.form.get('status')=='1':
            status = True
        else:
            status = False
        try:
            stu_pac_subs = Student_package_subscription.query.filter_by(id=pid).first()
            if stu_pac_subs:
                stu_pac_subs.subs_status = bool(status)
                db.session.commit()
                info = {"error":0,"message":'status updated'}
                return jsonify(info)
            else:
                info =  {'error':1,'message':'course package is not available'}
                return jsonify(info)
        except Exception as e:
            app.logger.error('Error: %s'%(str(e)))
            info =  {'error':1,'message':'Oops! something went wrong.'}
            return jsonify(info)
    else:
        info =  {'error':1,'message':'method is not allowed.'}
        return jsonify(info)


@app.route('/admin/update_stu_payment_status',methods=['POST'])
@login_required
@admin_required
def update_stu_payment_status():
    if request.method=='POST':

        pid = request.form.get('pid')
        status = ''
        if request.form.get('status')=='1':
            status = True
        else:
            status = False
        try:
            stu_pac_subs = Student_package_subscription.query.filter_by(id=pid).first()
            if stu_pac_subs:
                stu_pac_subs.payment_status = bool(status)
                db.session.commit()
                info = {"error":0,"message":'status updated'}
                return jsonify(info)
            else:
                info =  {'error':1,'message':'course package is not available'}
                return jsonify(info)
        except Exception as e:
            app.logger.error('Error: %s'%(str(e)))
            info =  {'error':1,'message':'Oops! something went wrong.'}
            return jsonify(info)
    else:
        info =  {'error':1,'message':'method is not allowed.'}
        return jsonify(info)


@app.route('/admin/online-register-students')
@login_required
@admin_required
def online_register_students():
    try:
        online_students_list = Users.query.filter_by(online_register=True).order_by(Users.id.desc()).all()
        resp = make_response(render_template('admin/online-register-students.html',online_students_list=online_students_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/admin/update_online_stu_status',methods=['POST'])
@login_required
@admin_required
def update_online_stu_status():
    if request.method=='POST':

        pid = request.form.get('pid')
        status = ''
        if request.form.get('status')=='1':
            status = True
        else:
            status = False
        try:
            stu_pac_subs = Users.query.filter_by(id=pid,online_register=True).first()
            if stu_pac_subs:
                stu_pac_subs.is_active = bool(status)
                db.session.commit()
                info = {"error":0,"message":'status updated'}
                return jsonify(info)
            else:
                info =  {'error':1,'message':'student is not available'}
                return jsonify(info)
        except Exception as e:
            app.logger.error('Error: %s'%(str(e)))
            info =  {'error':1,'message':'Oops! something went wrong.'}
            return jsonify(info)
    else:
        info =  {'error':1,'message':'method is not allowed.'}
        return jsonify(info)

""" Admin can see the details of subscribed package details """
@app.route('/admin/subs-pac-details/<int:id>')
@login_required
@admin_required
def subs_pac_details(id):
    try:
        stu_pac_subs = Student_package_subscription.query.filter_by(id=id).first()
        if stu_pac_subs:
            package_info = Pac_course.query.filter_by(id=stu_pac_subs.package_id).first()

            student_details = db.session.execute("SELECT users.*, school_details.school_name FROM users join school_details on \
                users.id=school_details.student_id WHERE users.id=:param",{"param":stu_pac_subs.student_id}).fetchone()

            if not student_details:
                student_details = Users.query.filter_by(id=stu_pac_subs.student_id).first()

            """ optional subjects for add more  """
            pack_optional_subjects = Pac_optional_subjects.query.filter_by(pac_course_id=package_info.id).all()


            """ Find the details of optional subjects """
            optional_subject_details=[]
            optional_sub_list = Student_subs_pac_optional.query.filter_by(stu_pac_subs_id=stu_pac_subs.id).all()
            for optional_subject in optional_sub_list:
                optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_subject.optional_subs).first()
                optional_subject_details.append({'price': optional_subject_info.price,'subject_name':optional_subject_info.subject_name})

            """ Find the details of compulsory subjects """
            compulsory_subject_details=[]
            comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=package_info.id).all()
            for cps in comp_sub: 
                compulsory_subject_details.append({'subject_name':cps.subject_name, 'price': cps.price})

            """ Find the details of subscription months """
            subs_months_details=[]
            subs_month_lists = Student_subs_pac_months.query.filter_by(stu_pac_subs_id=stu_pac_subs.id).all()
            for month in subs_month_lists:
            #     sub_month = Months.query.filter_by(id=month.id).first()
                subs_months_details.append({'month_name': month.month_name})

            resp = make_response(render_template('admin/subscribed-package-details.html', stu_pac_subs=stu_pac_subs, student_details=student_details,\
                    optional_subject_details=optional_subject_details, compulsory_subject_details=compulsory_subject_details,\
                    package_info=package_info,subs_months_details=subs_months_details,pack_optional_subjects=pack_optional_subjects))
            return resp
        else:
            flash('Package is not valid', 'danger')
            return redirect(url_for('subscription_students'))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)



""" Admin can add new optional subject to the subscribed student """
@app.route('/admin/add-optional-subject-subs-student',methods=['POST'])
@login_required
@admin_required
def add_optional_subject_subs_student():
    if request.method=='POST':
        try:
            stu_pac_subs_id = request.form.get('stu_pac_subs_id')
            pac_optional_id = request.form.get('pac_optional_id')
            optional_pac_info = Pac_optional_subjects.query.filter_by(id=pac_optional_id).first()
            student_subs_optonal_subjects = Student_subs_pac_optional.query.filter_by(stu_pac_subs_id=stu_pac_subs_id,optional_subs=pac_optional_id).first()

            if student_subs_optonal_subjects:
                flash('Already assigned {}'.format(optional_pac_info.subject_name),'danger')
                return redirect(url_for('subs_pac_details',id=stu_pac_subs_id))
            else:
                subs_new_opt = Student_subs_pac_optional(stu_pac_subs_id=stu_pac_subs_id,optional_subs=pac_optional_id)
                db.session.add(subs_new_opt)
                db.session.commit()
                db.session.close()
                flash('Assigned new optoinal subject {}'.format(optional_pac_info.subject_name),'success')
                return redirect(url_for('subs_pac_details',id=stu_pac_subs_id))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        return redirect(url_for('subscription_students'))


""" Add new seminar  """
@app.route('/admin/add-seminar', methods=['GET','POST'])
@login_required
@admin_required
def add_seminar():

    if request.method == 'POST':
        form = SeminarForm(request.form)
        if  form.validate()== False:
            return render_template('admin/add-seminar.html', form=form)
        else:
            title = request.form.get('title')
            canonical_url = request.form.get('title')
            description = request.form.get('description')
            price = request.form.get('price') or 0
            seminar_date = request.form.get('seminar_date')
            cover_banner = request.files['cover_banner']
            
            cover_path=''
            if cover_banner:
                filename = secure_filename(cover_banner.filename)
                filetype, extension = splitext(filename)
                newfilename = str(randomkey(10)).lower() + extension 
                cover_banner.save(os.path.join(SEMINAR_COVER_BANNER, newfilename))
                cover_path = '/static/upload/seminar/' + newfilename
            
            try:
                seminar = Seminars(title=title, canonical_url=canonical_url, description=description, price=price, seminar_date=seminar_date,cover_banner=cover_path)
                db.session.add(seminar)
                db.session.commit()

                if seminar.id:
                    seminar = Seminars.query.filter_by(id=seminar.id).first()
                    seminar.canonical_url = slugify(title) + '-' + str(seminar.id)
                    db.session.commit()
                    db.session.close()
                flash('Seminar is added successfully.', 'success')
                return redirect(url_for('add_seminar'))
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
            
    else:
        form = SeminarForm(request.form)
        resp = make_response(render_template('admin/add-seminar.html',form=form))
        return resp

""" Update the seminar information """
@app.route('/admin/edit-seminar/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_seminar(id):
    seminar = Seminars.query.filter_by(id=id).first()
    form = SeminarForm(obj=seminar)
    if request.method == 'POST':
        title = request.form.get('title')
        canonical_url = request.form.get('title')
        description = request.form.get('description')
        seminar_date = request.form.get('seminar_date')
        price = request.form.get('price')
        cover_banner = request.files['cover_banner']
        
        seminar.title = title
        seminar.canonical_url = canonical_url
        seminar.description = description
        seminar.price = price
        seminar.seminar_date = seminar_date

        if cover_banner:
            filename = secure_filename(cover_banner.filename)
            filetype, extension = splitext(filename)
            newfilename = str(randomkey(10)).lower() + extension 
            cover_banner.save(os.path.join(SEMINAR_COVER_BANNER, newfilename))
            cover_path = '/static/upload/seminar/' + newfilename
            seminar.cover_banner = cover_path

        db.session.commit()
        flash("{} has updated successfully".format(title.title()),'success')
        return redirect(url_for('seminar_list'))

    return render_template('admin/edit-seminar.html', form=form)

""" List all the seminars """
@app.route('/admin/seminar-list')
@login_required
@admin_required
def seminar_list():
    try:
        seminar_list = Seminars.query.order_by(Seminars.id.desc()).all()
        return render_template('admin/seminar-list.html',seminar_list=seminar_list)
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

""" Add seminar topics """
@app.route('/admin/add-seminar-topic/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def add_seminar_topic(id):


    if request.method == 'POST':

        seminar_id = id
        course_id = request.form.get('course_id')
        subject_id = request.form.get('subject_id')
        teacher_id = request.form.get('teacher_id')
        topic_title = request.form.get('topic_title')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        try:
            seminar_details = Seminar_details(seminar_id=seminar_id, course_id=course_id, \
                subject_id=subject_id, teacher_id=teacher_id, topic_titile=topic_title, start_time=start_time, end_time=end_time)
            db.session.add(seminar_details)
            db.session.commit()
            db.session.close()
            flash('Topic is added successfully.','success')
            return redirect(url_for('add_seminar_topic', id=id))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:    
        
        try:
            courses = Courses.query.filter_by(is_active=True).order_by(Courses.course_name.asc()).all()
            subjects = Subjects.query.filter_by(is_active=True).order_by(Subjects.subject_name.asc()).all()
            seminar = Seminars.query.filter_by(id=id).first()
            seminar_details = Seminar_details.query.filter_by(seminar_id=id).all()
            return render_template('admin/add-seminar-topoic.html', courses=courses, subjects=subjects, seminar=seminar,seminar_details=seminar_details)
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


""" Fetch the teacher list from the assing course """
@app.route('/admin/ajax_fetch_seminar_teacher/<int:course_id>/<int:subject_id>')
@login_required
@admin_required
def ajax_fetch_seminar_subjects(course_id,subject_id):

    try:
        assing_courses = Teacher_assing_course.query.filter_by(course_id=course_id,subject_id=subject_id).all()
        teacher_list=[]
        if assing_courses:
            for teacher in assing_courses:
                user = Users.query.filter_by(id=teacher.user_id).first()
                teacher_list.append({'teacher_id': teacher.user_id,'teacher_name':user.first_name})
            return jsonify({'error': 0, 'message': teacher_list})
        else:
            return jsonify({'error': 1, 'message': 'subject is not avalibale'})
    except Exception as e:
        return jsonify({'error':1,'message':str(e)})

""" Delete the topoic from the a seminar """
@app.route('/admin/delete_seminar_topic/<int:sem_id>/<int:id>')
@login_required
@admin_required
def delete_seminar_topic(sem_id, id):
    try:
        sem_topic = Seminar_details.query.filter_by(id=id).delete()
        db.session.commit()
        return redirect(url_for('add_seminar_topic',id=sem_id))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


""" seminar joined student list  """
@app.route('/admin/seminar-joined-students/<int:id>')
@login_required
@admin_required
def seminar_joined_students(id):
    try:
        seminar = Seminars.query.filter_by(id=id).first()
        if seminar:
            joined_student_list = db.session.execute(f"SELECT seminar_attend.*, users.first_name,users.last_name,users.email,users.mobile,users.address\
                from seminar_attend join users on seminar_attend.student_id=users.id where seminar_attend.seminar_id={id} order by id desc").fetchall()
        return render_template('admin/seminar-joined-students.html',seminar=seminar, joined_student_list=joined_student_list)
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

""" Approved who joind the seminar """
@app.route('/admin/approve-seminar-attend-student',methods=['POST'])
@login_required
@admin_required
def approve_seminar_attend_student():
    
    id = request.form.get('jo_sem_id')
    status = ''
    if request.form.get('status')=='1':
        status = True
    else:
        status = False
    try:
        joined_sem = Seminar_attend.query.filter_by(id=id).first()
        if joined_sem:
            if joined_sem.is_free==False:
                joined_sem.payment_status=True
                joined_sem.is_approved = bool(status)
                db.session.commit()
                db.session.close()
                info = {"error":0,"message":'status updated'}
                return jsonify(info)
            else:
                joined_sem.is_approved = bool(status)
                db.session.commit()
                db.session.close()
                info = {"error": 0, "message": 'status updated'}
                return jsonify(info)

        else:
            info =  {'error':1,'message':'Not joined seminar'}
            return jsonify(info)
    except Exception as e:
        app.logger.error(str(e))
        info = {"error":1,"message":'Oops! something went wrong.'}
        return jsonify(info)


""" switch on or off the seminar """
@app.route('/admin/switch-seminar',methods=['POST'])
@login_required
@admin_required
def switch_seminar():
    
    id = request.form.get('sid')
    status = ''
    if request.form.get('status')=='1':
        status = True
    else:
        status = False
    try:
        seminar = Seminars.query.filter_by(id=id).first()
        if seminar:
            seminar.is_active = bool(status)
            db.session.commit()
            info = {"error":0,"message":'status updated'}
            return jsonify(info)
        else:
            info =  {'error':1,'message':'seminar details are not valid.'}
            return jsonify(info)
    except Exception as e:
        app.logger.error(str(e))
        info = {"error":1,"message":'Oops! something went wrong.'}
        return jsonify(info)

""" Subscription Renewal List """
@app.route('/admin/subscription-renewal-list')
@login_required
@admin_required
def subscription_renewal_list():
    try:
        student_subs_pac_list = Subscription_trans_log.query.order_by(Subscription_trans_log.id.desc()).all()
        subs_pac_list=[]
        if student_subs_pac_list:
            for subs in student_subs_pac_list:
                filename, file_extension = splitext(subs.receipt)
                subs_pac_list.append({'id': subs.id,'package_id':subs.package_id, 'package_name': subs.package_name, 'student_name': subs.student_name, 'total_amount': subs.total_amount, \
                    'discount_amount': subs.discount_amount, 'total_payable_amount': subs.total_payable_amount,'trans_id':subs.transcation_id,'invoice':subs.invoice,'purpose':subs.purpose, 'payment_date': subs.payment_date, 'receipt': subs.receipt,\
                        'file_extension':file_extension.lower()})

        resp = make_response(render_template('admin/subscription-renewal-list.html',student_subs_pac_list=subs_pac_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)
        
""" class recording list """
@app.route('/admin/class-recording-list/<int:id>')
def class_recording_list(id):

    try:
        online_classes = Online_classes.query.filter_by(id=id).first()
        if online_classes:
            recording_list=Broadcast_classe_stream_records.query.filter_by(live_class_id=id).all()
            return render_template('admin/recordings.html',online_classes=online_classes,recording_list=recording_list)
        else:
            flash('Sorry, class details are not valid','danger')
            return redirect(url_for('topics_list'))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

""" Demo class recording list """
@app.route('/admin/demo-class-recording-list/<int:id>')
def demo_class_recording_list(id):

    try:
        online_classes = Online_demo_classes.query.filter_by(id=id).first()
        if online_classes:
            recording_list=Broadcast_demo_classe_stream_records.query.filter_by(live_class_id=id).all()
            return render_template('admin/demo/recordings.html',online_classes=online_classes,recording_list=recording_list)
        else:
            flash('Sorry, class details are not valid','danger')
            return redirect(url_for('demo_topics_list'))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

""" Renew packages list pending for approval """
@app.route('/admin/pending-subscription-approval')
def pending_subscription_approval():
    try:
        subs_approval_list=Student_package_subscription.query.filter_by(subs_status=False, is_expired=False).order_by(Student_package_subscription.id.desc()).all()
        subs_pac_list=[]
        if subs_approval_list:
            
            for subs in subs_approval_list:
                filename, file_extension = splitext(subs.receipt)

                ist_time_str = subs.payment_date+datetime.timedelta(seconds=28800)
                payment_date = datetime.datetime.strptime(str(ist_time_str), "%Y-%m-%d %H:%M:%S")

                subs_pac_list.append({'id': subs.id, 'package_name': subs.package_name, 'student_name': subs.student_name, 'total_amount': subs.total_amount, \
                    'discount_amount': subs.discount_amount, 'total_payable_amount': subs.total_payable_amount, 'payment_date': payment_date, 'receipt': subs.receipt,\
                        'payment_status':subs.payment_status,'subs_status':subs.subs_status,'purpose':subs.purpose,'invoice':subs.invoice,'file_extension':file_extension.lower()})

        resp = make_response(render_template('admin/pending-subscription-approval.html',student_subs_pac_list=subs_pac_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


""" Expired package list """
@app.route('/admin/expired-subscriptions')
@login_required
@admin_required
def expired_subscription():
    try:
        student_subs_pac_list = Student_package_subscription.query.filter_by(is_expired=True).order_by(Student_package_subscription.id.desc()).all()
        subs_pac_list=[]
        if student_subs_pac_list:
            
            for subs in student_subs_pac_list:
                filename, file_extension = splitext(subs.receipt)

                ist_time_str = subs.payment_date+datetime.timedelta(seconds=28800)
                payment_date = datetime.datetime.strptime(str(ist_time_str), "%Y-%m-%d %H:%M:%S")

                subs_pac_list.append({'id': subs.id, 'package_name': subs.package_name, 'student_name': subs.student_name, 'total_amount': subs.total_amount, \
                    'discount_amount': subs.discount_amount, 'total_payable_amount': subs.total_payable_amount, 'payment_date': payment_date, 'receipt': subs.receipt,\
                        'payment_status':subs.payment_status,'subs_status':subs.subs_status,'purpose':subs.purpose,'invoice':subs.invoice,'file_extension':file_extension.lower()})

        resp = make_response(render_template('admin/expired-subscription.html',student_subs_pac_list=subs_pac_list))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


""" Referral program  """
@app.route('/admin/referral/wallet')
@login_required
@admin_required
def ref_wallet_list():
    try:
        wallet_list = Wallet.query.order_by(Wallet.id.desc()).all()
    except Exception as e:
        app.logger.log(str(e))
    return make_response(render_template('admin/referral/wallet-list.html', wallet_list = wallet_list))


@app.route('/admin/referral/wallet/amt/request')
@login_required
@admin_required
def ref_wallet_amt_withd():
    try:
        withdraw_list = Wallet_withdrawal_request.query.order_by(Wallet_withdrawal_request.id.desc()).all()
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)
    return make_response(render_template('admin/referral/withdrawal-amount-list.html', withdraw_list = withdraw_list))


@app.route('/admin/referral/wallet/amt/request/submit',methods=['POST'])
@login_required
@admin_required
def ref_wallet_amt_withd_submit():

    if request.method=='POST':
        withdraw_req_id = request.form.get('withdraw_req_id')
        user_id = request.form.get('user_id')
        message = request.form.get('message')
        try:
            width_req = Wallet_withdrawal_request.query.filter_by(id=withdraw_req_id).first()
            if width_req:
                width_req.message = message
                width_req.approve_date = datetime.datetime.now()
                width_req.is_approved = 1
                db.session.commit()
                db.session.add(Wallet_trans_log(user_id = user_id, amount= width_req.amount, action='WITHDRAWAL',description= message))
                db.session.commit()
                wallet = Wallet.query.filter_by(user_id=user_id).first()
                if wallet:
                    wallet.amount = wallet.amount-width_req.amount
                    db.session.commit()
                db.session.close()
                flash('You have successfully update wallet withdrawal request.','success')
                return redirect(url_for('ref_wallet_amt_withd'))
            else:
                flash('Oops! something went wrong.','danger')
                return redirect(url_for('ref_wallet_amt_withd'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        return redirect(url_for('ref_wallet_amt_withd'))


@app.route('/admin/referral/setting',methods = ['GET','POST'])
def referral_setting():

    try:
        ref_setting = Referral_setting.query.filter_by(id=1).first()
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

    form = ReferralSettingForm(obj=ref_setting)
    if request.method == 'POST':
        if not form.validate():
            return render_template('admin/referral-setting.html', ref_setting=ref_setting, form=form)
        else:
            ref_setting = Referral_setting.query.filter_by(id=1).first() or 404()
            amount =  request.form.get('amount')
            dis_type = request.form.get('dis_type')
            ref_setting.amount =  amount
            ref_setting.dis_type = dis_type
            db.session.commit()
            db.session.close()

            flash('Referral setting is updated.', 'success')
            return render_template('admin/referral-setting.html', ref_setting=ref_setting, form=form)
    else:
        return render_template('admin/referral-setting.html', ref_setting=ref_setting, form=form)