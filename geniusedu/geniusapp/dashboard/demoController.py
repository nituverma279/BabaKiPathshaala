from geniusapp import app,login_manager,db,logging,csrf
from flask import Flask,render_template,request,url_for,flash,session,\
    make_response,redirect,abort,json,jsonify,render_template_string,abort
from geniusapp.model.tables import User_roles, Users,Subjects,Courses,Courses_mapper,\
Broadcast_demo_classe_stream_records, Teacher_assing_course,Online_demo_classes,Student_subscribe_courses,Chat,\
    Ban_chat_demo_users,Student_attendence,Users_demo,Demo_chat,Demo_student_attendence,Pac_course
from geniusapp.dashboard.form import StudentSelectCourse
from flask_login import current_user,login_required
import datetime
from slugify import slugify
from _ast import Param
from functools import wraps
import random
import string
from werkzeug.utils import secure_filename
import os
from os.path import splitext

basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAT_UPLOAD_CONTENTS = basedir+'/static/upload/demo_class_banner/'


def randomkey(stringLength=10):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))

def teacher_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.user_role_id == 3:
            return f(*args, **kwargs)
        else:
            abort(401)
    return wrap


@app.route('/demo-class-login',methods=['POST','GET'])
def demo_login():
    if request.method == 'POST':
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 6))
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name') or ''
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = random_string
        gender = request.form.get('gender') or ''
        user_id = mobile[:6]+random_string
        try:
            exists_users=Users_demo.query.filter_by(mobile=mobile).first()
            if exists_users:

                session['first_name'] = exists_users.first_name
                session['demo_user_id']=exists_users.user_id
                session['email'] = exists_users.email
                session['id'] = exists_users.id
                session['user_role_id'] = exists_users.user_role_id
                session['used_for']='demo'
                session['is_login']=True
                next_page = request.form.get('watchurl')
                if  next_page == '':
                    next_page = make_response(redirect(url_for('home')))
                    return next_page
                else:
                    return redirect(next_page)
            else:
                user = Users_demo(user_id=user_id,first_name=first_name,last_name=last_name,gender=gender,email=email,password=password,mobile=mobile,user_role_id=4)
                db.session.add(user)
                db.session.commit()
                if user.id >0 :
                    session['first_name'] = user.first_name
                    session['demo_user_id']=user.user_id
                    session['email'] = user.email
                    session['id'] = user.id
                    session['user_role_id'] = user.user_role_id
                    session['used_for']='demo'
                    session['is_login']=True

                    next_page = request.form.get('watchurl')
                    if next_page == '':
                        next_page = make_response(redirect(url_for('home')))
                        return next_page
                    else:
                        return redirect(next_page)
                else:
                    flash(u"Oops! something went wrong.","danger")
                    resp = make_response(redirect(url_for('home')))
                    return resp
        except Exception as e:
            return str(e)
    else:
        return redirect('/')

@app.route('/demo/add-new-class',methods=['GET','POST'])
@login_required
@teacher_required
def demo_add_new_class():
    if request.method=='POST':
        user_id = current_user.id
        course_id = request.form.get('course')
        subject_id = request.form.get('subject')
        class_title = request.form.get('class_title')
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 12))
        canonical_url = slugify(class_title)+'-'+random_string
        description = request.form.get('description')
        create_date = request.form.get('create_date')
        cover_image = request.files['cover_image']
        try:
            filename = secure_filename(cover_image.filename)
            filetype, extension = splitext(filename)
            newfilename =  str(randomkey(10)).lower() + extension
            cover_image.save(os.path.join(CHAT_UPLOAD_CONTENTS, newfilename)) 
            cover_file_path= '/static/upload/demo_class_banner/'+newfilename

            online_classes = Online_demo_classes(user_id=user_id,course_id=course_id,subject_id=subject_id,class_title=class_title,canonical_url=canonical_url,description=description,cover_banner=cover_file_path,create_date=create_date)
            db.session.add(online_classes)
            db.session.commit()
            if online_classes:
                online_topics = Online_demo_classes.query.filter_by(id=online_classes.id).first() or abort(500)
                online_topics.canonical_url=slugify(class_title)+'-'+str(online_classes.id)
                db.session.commit()

            flash('Successfully added','success')
            resp = make_response(redirect(url_for('demo_add_new_class')))
            return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        try:
            courses = Courses.query.filter_by(is_active=True).all()
            resp = make_response(render_template('demo/add-new-class.html',courses=courses))
            return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


@app.route('/demo/broadcast-online-class/<string:cano_url>')
@login_required
@teacher_required
def demo_broadcast_online_class(cano_url):
    try:
        live_course = Online_demo_classes.query.filter_by(canonical_url=cano_url,is_complete=False,is_active=True).first()
        if live_course:
            live_course.is_start=1
            db.session.commit()
            chat_history = Demo_chat.query.filter_by(online_class_id=live_course.id).all()
            resp = make_response(render_template('demo/broadcast-online-class.html',live_course=live_course,chat_history=chat_history))
            return resp
        else:
            resp = make_response(redirect(url_for('dashboard')))
            flash('Class is not avaliable or not active.','danger')
            return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/demo/mb-broadcast-online-class/<string:cano_url>')
@login_required
@teacher_required
def demo_mb_broadcast_online_class(cano_url):
    try:
        live_course = Online_demo_classes.query.filter_by(canonical_url=cano_url,is_complete=False,is_active=True).first()
        if live_course:
            chat_history = Demo_chat.query.filter_by(online_class_id=live_course.id).all()
            resp = make_response(render_template('demo/mb-broadcast-online-class.html',live_course=live_course,chat_history=chat_history))
            return resp
        else:
            resp =  make_response(redirect(url_for('dashboard')))
            flash('Class is not avaliable or not active.','danger')
            return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


def make_demo_student_attendance(topices_id,student_id):
    try:
        attend_reprot_exists = Demo_student_attendence.query.filter_by(topices_id=topices_id,student_id=student_id).first()
        if attend_reprot_exists is None:
            attendance= Demo_student_attendence(topices_id=topices_id,student_id=student_id)
            db.session.add(attendance)
            db.session.commit()
            return {'error':0,'message':'Attendance is added successfully.'}
        else:
            return {'error':1,'message':'Attendance is already avaliable.'}
    except Exception as e:
        app.logger.error(str(e))
        return {'error':1,'message':'Oops! something went wrong. %s'%(str(e))}



@app.route('/demo/watch-classes/<string:cano_url>')
def demo_watch_live_class(cano_url):
    if session.get('is_login'):
        try:
            live_course = Online_demo_classes.query.filter_by(canonical_url=cano_url,is_complete=False,is_active=True).first()
            if live_course:
                topices_id = live_course.id
                student_id = session.get('id')
                response = make_demo_student_attendance(topices_id,student_id)
                if live_course.is_start==True:
                    student = Users_demo.query.filter_by(id=session.get('id')).first()
                    chat_history = Demo_chat.query.filter_by(online_class_id=live_course.id).all()
                    banned_user_form_chat = Ban_chat_demo_users.query.filter_by(online_class_id=live_course.id,banned_user_id=session.get('id')).first()
                    broadcast_video_stream_record= Broadcast_demo_classe_stream_records.query.filter_by(live_class_id=live_course.id).order_by(Broadcast_demo_classe_stream_records.id.desc()).first()
                    resp = make_response(render_template('demo/watch-classes.html',live_course=live_course,banned_user_form_chat=banned_user_form_chat,\
                        broadcast_video_stream_record=broadcast_video_stream_record,chat_history=chat_history,student=student))
                    return resp
                else:
                    return render_template('demo/class-info.html',live_class=live_course)
            else:
                flash('Class is not avaliable or not active.','danger')
                resp = make_response(redirect(url_for('home')))
                return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        return redirect('/')


@app.route('/demo/mb-watch-classes/<string:cano_url>')
def demo_mb_watch_live_class(cano_url):
    if session.get('is_login'):
        try:
            live_course = Online_demo_classes.query.filter_by(canonical_url=cano_url,is_complete=False,is_active=True).first()
            if live_course:
                topices_id = live_course.id
                student_id = session.get('id')
                response = make_demo_student_attendance(topices_id,student_id)
                if live_course.is_start==True:
                    student = Users_demo.query.filter_by(id=session.get('id')).first()
                    chat_history = Demo_chat.query.filter_by(online_class_id=live_course.id).all()
                    banned_user_form_chat = Ban_chat_demo_users.query.filter_by(online_class_id=live_course.id,banned_user_id=session.get('id')).first()
                    broadcast_video_stream_record = Broadcast_demo_classe_stream_records.query.filter_by(live_class_id=live_course.id).order_by(Broadcast_demo_classe_stream_records.id.desc()).first()
                    resp = make_response(render_template('demo/mb-watch-classes.html',live_course=live_course,banned_user_form_chat=banned_user_form_chat,\
                        broadcast_video_stream_record=broadcast_video_stream_record,chat_history=chat_history,student=student))
                    return resp
                else:
                    return render_template('demo/class-info.html',live_class=live_course)
            else:
                flash('Class is not avaliable or not active.','danger')
                resp = make_response(redirect(url_for('home')))
                return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        return redirect('/')


@app.route('/demo/logout')
def demo_logout():
    try:
        if session.get('is_login'):
            session.clear()
            return redirect('/')
        else:
            return redirect('/')
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/demo/complete-live-show',methods=['POST'])
@login_required
@teacher_required
def demo_complete_live_show():
    if request.method=='POST':
        try:
            online_class_id=request.form.get('sid')
            online_class_details = Online_demo_classes.query.filter_by(id=online_class_id).first()

            if online_class_details:
                online_class_details.is_complete=True
                db.session.commit()
                db.session.close()
                return {'error':0,'message':online_class_details.class_title +' is marked as completed.'}
            else:
                return {'error':1,'message':'class detail are not valid.'}
        except Exception as e:
            app.logger.error(str(e))
            return {'error':1,'message':'Oops! something went wrong.'}
    else:
       return {'error':1,'message':'Method is not allowed.'}

@app.route('/demo/send-chat-msg',methods=['POST'])
@csrf.exempt
def demo_send_chat_message():
    user_id =  request.form.get('user_id')
    online_class_id = request.form.get('show_id')
    sender_id =request.form.get('sender_id')
    receiver_id = request.form.get('receiver_id')
    message = request.form.get('chat_msg')
    # return {'user_id':user_id,'online_class_id':online_class_id,'sender_id':sender_id,'receiver_id':receiver_id,'message':message}
    try:
        if message:
            chat = Demo_chat(user_id=user_id, online_class_id= online_class_id, sender_id = sender_id, receiver_id = receiver_id, message = message)
            db.session.add(chat)
            db.session.commit()
            db.session.close()
            return 'message added to the chat'
        else:
            return 'message is empty'
    except Exception as e:
        app.logger.error(str(e))
        return str(e)


@app.route('/demo/store-demo-records',methods=['POST'])
@login_required
def store_demo_records():
    try:
        live_class_id = request.form.get('show_id')
        member_id = current_user.id
        stream_id = request.form.get('stream_id')
        sream_store = Broadcast_demo_classe_stream_records(live_class_id=live_class_id, member_id=member_id, stream_id=stream_id) 
        db.session.add(sream_store)
        db.session.commit()
        return {'error':0,'message':'stream stored'} 
    except Exception as e:
        app.logger.error(str(e)) 
        return {'error':1,'message':'Oops! something went wrong %s'%(str(e))}



@app.route('/demo/block-demo-chat-member',methods=['POST'])
@login_required
def block_demo_chat_member():

    online_class_id = request.form.get('show_id')
    banned_user_id = request.form.get('sender_id')
    teacher_id = request.form.get('broadcaster_id')
    reason=request.form.get('reason') or ''
    try:
        banned_user = Users_demo.query.filter_by(id=banned_user_id).first()
        if banned_user:
            ban_chat_user = Ban_chat_demo_users(online_class_id=online_class_id,banned_user_id=banned_user_id,teacher_id=teacher_id,reason=reason)
            db.session.add(ban_chat_user)
            db.session.commit()
            return {'error':0,'message':'%s is muted successfully.'%(banned_user.first_name.title())}
        else:
            return {'error':1,'message':'User details are not valid.'}
    except Exception as e:
        app.logger.error(str(e)) 
        return {'error':1,'message':'Oops! something went wrong %s'%(str(e))}


@app.route('/dashboard/mark_as_complete_demo_topic',methods=['POST'])
@login_required
@teacher_required
def complete_demo_topic_mark():
    if request.method=='POST':
        coid = request.form.get('coid')
        try:
            Livetopic = Online_demo_classes.query.filter_by(id=coid,is_complete=False).first()
            if Livetopic:
                Livetopic.is_complete=True
                db.session.commit()
                return jsonify({'error':0,'message':'Mark as completed'})
            else:
                return jsonify({'error':1,'message':'Topic is already completed.'})
        except Exception as e:
            app.logger.error(str(e))
            return jsonify({'error':1,'message':'Oops something went wrong.'})
    else:
        return jsonify({'error':1,'message':'Method is not allowed.'})


@app.route('/dashboard/user')
def usersDashboard():
    try:
        
        course_package = Pac_course.query.filter_by(is_active=True).order_by(Pac_course.id.desc()).all()
        resp = make_response(render_template('home/packages.html',course_package=course_package))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)