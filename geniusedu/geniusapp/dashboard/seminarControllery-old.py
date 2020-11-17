from geniusapp import app,login_manager,db,logging,csrf
from flask import Flask,render_template,request,url_for,flash,session,\
    make_response,redirect,abort,json,jsonify,render_template_string,abort
from geniusapp.model.tables import User_roles, Users,Subjects,Courses,Courses_mapper,\
Broadcast_classe_stream_records, Teacher_assing_course,Online_classes,\
Student_subscribe_courses,Chat,Ban_chat_users,Online_demo_classes,\
Pac_course,Pac_optional_subjects,Pac_compulsory_subjects,\
Student_package_subscription,Student_subs_pac_months,Student_subs_pac_optional,Months,Subscription_trans_log,Seminars, \
    Seminar_details,Seminar_attend,Sem_broad_streams_records,Sem_chat,Ban_sem_chat
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

basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAT_UPLOAD_CONTENTS = basedir+'/static/upload/chat_share_file/'


def student_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.user_role_id == 4:
            return f(*args, **kwargs)
        else:
            abort(401)
    return wrap

def teacher_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.user_role_id == 3:
            return f(*args, **kwargs)
        else:
            abort(401)
    return wrap

""" Teacher broadcast seminar from there dashboard """
@app.route('/dashboard/broadcast-seminar/<string:cano_url>')
@login_required
@teacher_required
def broadcast_seminar(cano_url):
    try:
        seminar = Seminars.query.filter_by(canonical_url=cano_url, is_active=True).first()
        if seminar:
            seminar_topic = Seminar_details.query.filter_by(seminar_id=seminar.id, teacher_id=current_user.id).first()
            if seminar_topic:
                chat_history = Sem_chat.query.filter_by(seminar_id=seminar.id).all()
                resp = make_response(render_template('dashboard/seminar/broadcast-online-seminar.html', seminar=seminar, chat_history=chat_history))
                return resp
            else:
                flash('Sorry, Your course is not avaliable in the seminar.','danger')
                return redirect(url_for('teacher_joined_sem_list'))
        else:
            flash('Sorry, seminar is closed or not activated.','danger')
            return redirect(url_for('teacher_joined_sem_list'))
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)
     
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/dashboard/upload-sem-content',methods=['POST'])
@login_required
@teacher_required
@csrf.exempt
def upload_sem_chat_content():

    if request.method =='POST':    
        image_portfolio5 = request.files['show_gallery']
        filename = secure_filename(image_portfolio5.filename)
        filetype, extension = splitext(filename)
        newfilename =  str(randomkey(10)).lower() + extension
        image_portfolio5.save(os.path.join(CHAT_UPLOAD_CONTENTS, newfilename)) 
        file_path= '/static/upload/chat_share_file/'+newfilename
        return jsonify({'error':'0','message':'{} file uploaded successfully.'.format(newfilename),'file_path':file_path})
    else:
        return {'error': '1', 'message': 'Sorry file was not uploaded.'}
        

def randomkey(stringLength=10):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength)) 

@app.route('/dashboard/generate-sem-stream',methods=['POST'])
@login_required
def generate_sem_stream():
    if request.method=='POST':
        return randomkey(20)


@app.route('/dashboard/store-sem-live-records',methods=['POST'])
@login_required
def store_sem_live_records():
    try:
        seminar_id = request.form.get('seminar_id')
        teacher_id = current_user.id
        stream_id = request.form.get('stream_id')
        sream_store = Sem_broad_streams_records(seminar_id=seminar_id, teacher_id=teacher_id, stream_id=stream_id) 
        db.session.add(sream_store)
        db.session.commit()
        return {'error':0,'message':'stream stored'} 
    except Exception as e:
        app.logger.error(str(e)) 
        return {'error': 1, 'message': 'Oops! something went wrong.'}


""" Mark the seminar as completed. """
@app.route('/dashboard/complete-seminar',methods=['POST'])    
@login_required
@teacher_required
def complete_seminar():
    if request.method=='POST':
        try:
            seminar_id=request.form.get('sid')
            seminar = Online_classes.query.filter_by(id=seminar_id).first()

            if seminar:
                seminar.is_active=False
                db.session.commit()
                db.session.close()
                return {'error':0,'message':'class is  marked as completed.'}
            else:
                return {'error':1,'message':'class detail are not valid.'}
        except Exception as e:
            return {'error':1,'message':'Oops! something went wrong. %s'%(str(e))}
    else:
       return {'error': 1, 'message': 'Method is not allowed.'}



""" Banned seminar joined student if need """
@app.route('/dashboard/ban-seminar-joined-student',methods=['POST'])
@login_required
@teacher_required
def ban_seminar_joined_student():

    seminar_id = request.form.get('show_id')
    banned_user_id = request.form.get('sender_id')
    teacher_id = request.form.get('broadcaster_id')
    reason=request.form.get('reason') or ''
    try:
        banned_user = Users.query.filter_by(id=banned_user_id).first()
        if banned_user:
            ban_chat_user = Ban_sem_chat(seminar_id=seminar_id,banned_user_id=banned_user_id,teacher_id=teacher_id,reason=reason)
            db.session.add(ban_chat_user)
            db.session.commit()
            return {'error':0,'message':'%s is muted successfully.'%(banned_user.first_name.title())}
        else:
            return {'error':1,'message':'User details are not valid.'}
    except Exception as e:
        app.logger.error(str(e)) 
        return {'error': 1, 'message': 'Oops! something went wrong.'}
        
""" Save all the seminar chats  """
@app.route('/dashboard/send-sem-chat-msg',methods=['POST'])
@login_required
@csrf.exempt
def send_sem_chat_message():
    user_id =  request.form.get('user_id')
    seminar_id = request.form.get('show_id')
    sender_id = current_user.id
    receiver_id = request.form.get('receiver_id')
    message = request.form.get('chat_msg')
    try:
        if message:
            chat = Sem_chat(user_id=user_id, seminar_id= seminar_id, sender_id = sender_id, receiver_id = receiver_id, message = message)
            db.session.add(chat)
            db.session.commit()
            db.session.close()
            return 'message added to the chat'
        else:
            return 'message is empty'        
    except Exception as e:
        app.logger.error(str(e)) 
        return str(e)


""" student can watch live seminar  """
@app.route('/dashboard/watch-live-seminar/<string:cano_url>')
@login_required
@student_required
def watch_live_seminar(cano_url):
    try:
        seminar = Seminars.query.filter_by(canonical_url=cano_url,is_active=1).first()
        if seminar:
            chat_history = Sem_chat.query.filter_by(seminar_id=seminar.id).all()
            banned_user_form_chat = Ban_sem_chat.query.filter_by(seminar_id=seminar.id,banned_user_id=current_user.id).first()
            broadcast_video_stream_record= Sem_broad_streams_records.query.filter_by(seminar_id=seminar.id).order_by(Sem_broad_streams_records.id.desc()).first()
            resp = make_response(render_template('dashboard/seminar/watch-live-seminar.html',seminar=seminar,banned_user_form_chat=banned_user_form_chat,\
                broadcast_video_stream_record=broadcast_video_stream_record,chat_history=chat_history))
            return resp
        else:
            flash('Seminar is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)