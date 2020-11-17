from geniusapp import app,login_manager,db,logging,csrf
from flask import Flask,render_template,request,url_for,flash,session,\
    make_response,redirect,abort,json,jsonify,render_template_string,abort
from geniusapp.model.tables import User_roles, Users,Subjects,Courses,\
Broadcast_classe_stream_records, Teacher_assing_course,Online_classes,Student_subscribe_courses,Chat,\
    Ban_chat_users,Student_attendence,Online_demo_classes,Broadcast_demo_classe_stream_records,Demo_chat,\
    Seminars, Seminar_details,Seminar_start_teachers,Sem_chat,Ban_sem_chat,Sem_broad_streams_records

from flask_login import current_user,login_required
from geniusapp.dashboard.form import StudentSelectCourse
import datetime
from _ast import Param
from functools import wraps
import random
import string
from werkzeug.utils import secure_filename
import os
from os.path import splitext

basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAT_UPLOAD_CONTENTS = basedir+'/static/upload/chat_share_file/'


def randomkey(stringLength=10):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))

def chatMember_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.user_role_id == 5:
            return f(*args, **kwargs)
        else:
            abort(401)
    return wrap

@app.route('/dashboard/monitor-live-classes/<string:cano_url>')
@login_required
@chatMember_required
def monitor_live_class(cano_url):
    try:
        live_course = Online_classes.query.filter_by(canonical_url=cano_url).first()
        if live_course:
            chat_history = Chat.query.filter_by(online_class_id=live_course.id).all()
            broadcast_video_stream_record= Broadcast_classe_stream_records.query.filter_by(live_class_id=live_course.id).order_by(Broadcast_classe_stream_records.id.desc()).first()
            resp = make_response(render_template('dashboard/members/monitor-live-classes.html',live_course=live_course,chat_history=chat_history,\
                broadcast_video_stream_record=broadcast_video_stream_record,))
            return resp
        else:
            flash('Class is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/dashboard/mb-monitor-live-class/<string:cano_url>')
@login_required
@chatMember_required
def mb_monitor_live_class(cano_url):
    try:
        live_course = Online_classes.query.filter_by(canonical_url=cano_url).first()
        if live_course:
            chat_history = Chat.query.filter_by(online_class_id=live_course.id).all()
            broadcast_video_stream_record= Broadcast_classe_stream_records.query.filter_by(live_class_id=live_course.id).order_by(Broadcast_classe_stream_records.id.desc()).first()
            resp = make_response(render_template('dashboard/members/mb-monitor-live-class.html',live_course=live_course,chat_history=chat_history,\
                broadcast_video_stream_record=broadcast_video_stream_record,))
            return resp
        else:
            flash('Class is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)



@app.route('/dashboard/monitor-demo-classes/<string:cano_url>')
@login_required
@chatMember_required
def monitor_demo_class(cano_url):
    try:
        live_course = Online_demo_classes.query.filter_by(canonical_url=cano_url).first()
        if live_course:
            chat_history = Demo_chat.query.filter_by(online_class_id=live_course.id).all()
            broadcast_video_stream_record= Broadcast_demo_classe_stream_records.query.filter_by(live_class_id=live_course.id).order_by(Broadcast_demo_classe_stream_records.id.desc()).first()
            resp = make_response(render_template('dashboard/members/monitor-demo-classes.html',live_course=live_course,chat_history=chat_history,\
                broadcast_video_stream_record=broadcast_video_stream_record,))
            return resp
        else:
            flash('Class is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/dashboard/upload-chat-document',methods=['POST'])
@login_required
@chatMember_required
@csrf.exempt
def upload_chat_document():

    if request.method =='POST':    
        image_portfolio5 = request.files['show_gallery']
        filename = secure_filename(image_portfolio5.filename)
        filetype, extension = splitext(filename)
        newfilename =  str(randomkey(10)).lower() + extension
        image_portfolio5.save(os.path.join(CHAT_UPLOAD_CONTENTS, newfilename)) 
        file_path= '/static/upload/chat_share_file/'+newfilename
        resp = {'error':'0','message':'{} file uploaded successfully.'.format(newfilename),'file_path':file_path}
        return jsonify(resp)
    else:
        resp=  {'error':'1','message':'Sorry file was not uploaded.'}
        return jsonify(resp)


@app.route('/dashboard/block-student',methods=['POST'])
@login_required
@chatMember_required
def block_student():

    online_class_id = request.form.get('show_id')
    banned_user_id = request.form.get('sender_id')
    teacher_id = request.form.get('broadcaster_id')
    reason=request.form.get('reason') or ''
    try:
        banned_user = Users.query.filter_by(id=banned_user_id).first()
        if banned_user:
            ban_chat_user = Ban_chat_users(online_class_id=online_class_id,banned_user_id=banned_user_id,teacher_id=teacher_id,reason=reason)
            db.session.add(ban_chat_user)
            db.session.commit()
            return {'error':0,'message':'%s is muted successfully.'%(banned_user.first_name.title())}
        else:
            return {'error':1,'message':'User details are not valid.'}
    except Exception as e:
        app.logger.error(str(e))
        return {'error':1,'message':'Oops! something went wrong %s'%(str(e))}



""" All live seminar list """
@app.route('/genius-seminar-list')
def genius_seminar_list():
    try:
        seminars_list = Seminars.query.filter_by(is_active=True).all()
        return render_template('dashboard/members/seminar-list.html', seminars_list=seminars_list)
         
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/dashboard/monitor-live-seminar/<string:cano_url>')
@login_required
@chatMember_required
def monitor_live_seminar(cano_url):
    try:
        seminar = Seminars.query.filter_by(canonical_url=cano_url,is_active=True).first()
        if seminar:
            chat_history = Sem_chat.query.filter_by(seminar_id=seminar.id).all()
            sem_start_teacher = Seminar_start_teachers.query.filter_by(seminar_id=seminar.id).first()
            if sem_start_teacher:
                banned_user_form_chat = Ban_sem_chat.query.filter_by(seminar_id=seminar.id,banned_user_id=current_user.id).first()
                broadcast_video_stream_record= Sem_broad_streams_records.query.filter_by(seminar_id=seminar.id).order_by(Sem_broad_streams_records.id.desc()).first()
                resp = make_response(render_template('dashboard/seminar/monitor-live-seminar.html',seminar=seminar,banned_user_form_chat=banned_user_form_chat,\
                    broadcast_video_stream_record=broadcast_video_stream_record,chat_history=chat_history,sem_start_teacher=sem_start_teacher))
                return resp
            else:
                flash('Sorry, Please wait until seminar is not started.','danger')
                resp = make_response(redirect(url_for('dashboard')))
                return resp
        else:
            flash('Seminar is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)


@app.route('/dashboard/mb-monitor-live-seminar/<string:cano_url>')
@login_required
@chatMember_required
def mb_monitor_live_seminar(cano_url):
    try:
        seminar = Seminars.query.filter_by(canonical_url=cano_url,is_active=True).first()
        if seminar:
            chat_history = Sem_chat.query.filter_by(seminar_id=seminar.id).all()
            sem_start_teacher = Seminar_start_teachers.query.filter_by(seminar_id=seminar.id).first()
            if sem_start_teacher:
                banned_user_form_chat = Ban_sem_chat.query.filter_by(seminar_id=seminar.id,banned_user_id=current_user.id).first()
                broadcast_video_stream_record= Sem_broad_streams_records.query.filter_by(seminar_id=seminar.id).order_by(Sem_broad_streams_records.id.desc()).first()
                resp = make_response(render_template('dashboard/seminar/mb-monitor-live-seminar.html',seminar=seminar,banned_user_form_chat=banned_user_form_chat,\
                    broadcast_video_stream_record=broadcast_video_stream_record,chat_history=chat_history,sem_start_teacher=sem_start_teacher))
                return resp
            else:
                flash('Sorry, Please wait until seminar is not started.','danger')
                resp = make_response(redirect(url_for('dashboard')))
                return resp
        else:
            flash('Seminar is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)