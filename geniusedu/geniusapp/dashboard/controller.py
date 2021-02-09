from geniusapp import app,login_manager,db,logging,csrf
from flask import Flask,render_template,request,url_for,flash,session,\
    make_response,redirect,abort,json,jsonify,render_template_string,abort
from geniusapp.model.tables import User_roles, Users,Subjects,Courses,Courses_mapper,\
Broadcast_classe_stream_records, Teacher_assing_course,Online_classes,\
Student_subscribe_courses,Chat,Ban_chat_users,Online_demo_classes,\
Pac_course,Pac_optional_subjects,Pac_compulsory_subjects,\
Student_package_subscription,Student_subs_pac_months,Student_subs_pac_optional,Months,Subscription_trans_log,Seminars, \
    Seminar_details,Seminar_attend, Wallet
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
RECEIPT_UPLOAD_CONTENTS = basedir+'/static/upload/receipt/'

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

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@app.route('/dashboard',methods=['POST','GET'])
# @login_required
def dashboard():

    # if student
    # if current_user.user_role_id==4: 
    #     stud_pac_sub =  db.session.execute("SELECT student_package_subscription.*,pac_course.seo_title,pac_course.cano_url,\
    #             pac_course.description,pac_course.price FROM student_package_subscription JOIN pac_course ON \
    #             student_package_subscription.package_id=pac_course.id  \
    #             WHERE student_package_subscription.subs_status=True and student_package_subscription.student_id=:param ORDER by student_package_subscription.id DESC",{"param":current_user.id}).fetchall()
        
        
    #     stu_subs_package = Student_package_subscription.query.filter_by(student_id=current_user.id).all()
    #     if stu_subs_package:
    #         current_month = datetime.datetime.now().month
            
    #         for stu_subs in stu_subs_package: 
    #             subs_months_list = Student_subs_pac_months.query.filter_by(stu_pac_subs_id=stu_subs.id).all()
    #             if subs_months_list:
    #                 subscribed_months_lst=[]
    #                 for sb_month in subs_months_list:
    #                     subscribed_months_lst.append(sb_month.subs_month)

    #                 # if current_month not in subscribed_months_lst:
    #                 #     pac_subs = Student_package_subscription.query.filter_by(student_id=current_user.id, id=stu_subs.id).first()
    #                 #     pac_subs.subs_status = False
    #                 #     pac_subs.is_expired = True
    #                 #     db.session.commit()

    #                 if current_month in subscribed_months_lst:
    #                     pac_subs = Student_package_subscription.query.filter_by(student_id=current_user.id, id=stu_subs.id).first()
    #                     pac_subs.subs_status = True
    #                     pac_subs.is_expired = False
    #                     db.session.commit()

    #         resp = make_response(render_template('dashboard/student/subs-package.html',course_package_info=stud_pac_sub))
    #         return resp
    #     else:
    #         subscribe_live_classes = db.session.execute("SELECT online_classes.user_id as teacher_id,online_classes.course_id, \
    #             online_classes.class_title,online_classes.canonical_url,online_classes.description,online_classes.create_date,\
    #             student_subscribe_courses.user_id as student_id, courses.course_name, subjects.subject_name FROM online_classes JOIN \
    #             student_subscribe_courses ON online_classes.course_id=student_subscribe_courses.course_id JOIN courses ON courses.id=online_classes.course_id \
    #             JOIN subjects on subjects.id=online_classes.subject_id \
    #             WHERE online_classes.subject_id=student_subscribe_courses.subject_id AND online_classes.is_active=1 \
    #             AND online_classes.is_complete=0 AND online_classes.is_approved=1 AND student_subscribe_courses.user_id=:param1",{"param1":current_user.id})
    #         resp = make_response(render_template('dashboard/student/home.html',subscribe_live_classes = subscribe_live_classes))
    #         return resp
    # elif current_user.user_role_id==3:
    #     try:
    #         demo_live_classes= Online_demo_classes.query.filter_by(user_id=current_user.id,is_active=True,is_complete=False).all()
    #         online_live_classes_list = Online_classes.query.filter_by(user_id=current_user.id,is_active=1,is_approved=1,is_complete=0).all()
    #         resp = make_response(render_template('dashboard/teacher/home.html',online_live_classes_list=online_live_classes_list,demo_live_classes=demo_live_classes))
    #         return resp
    #     except Exception as e:
    #         app.logger.error(str(e))
    #         return abort(500)
    # elif current_user.user_role_id==5:
    #     try:
    #         demo_live_classes= Online_demo_classes.query.filter_by(is_active=True,is_complete=False).all()
    #         online_live_classes_list = Online_classes.query.filter_by(is_active=True,is_complete=False).all()
    #         resp = make_response(render_template('dashboard/members/home.html',online_live_classes_list=online_live_classes_list,demo_live_classes=demo_live_classes))
    #         return resp
    #     except Exception as e:
    #         app.logger.error(str(e))
    #         return abort(500)
    # else:
        #resp = make_response(redirect(url_for('home')))
        resp =  render_template('dashboard/usersBoard/dashboard.html')
        return resp


@app.route('/content/<int:course_id>')
def contentDashboard(course_id):
    try:
        #course_topic_list = Courses.query.filter_by(id=course_id).first
        #course_topic_list = db.session.execute("Select * from Courses where id between :param1 and :param2",{'param1':current_month,'param2':expire_month}).fetchall()    
        course_topic_string = db.session.execute("SELECT courses.topics\
                    FROM courses WHERE \
                    courses.id=:param",{"param":course_id}).fetchall()
        if course_topic_string is None:
            return
        elif course_id == 5:
            return make_response(render_template('dashboard/serviceCategory/mental_health.html'))
        else:
            course_topic_list = [i[0] for i in course_topic_string][0].split(',')
            return make_response(render_template('dashboard/serviceCategory/availableService.html',
            course_name= course_topic_list))
        
    except Exception as e:
            app.logger.error(str(e))
            return abort(500)

    return resp

@app.route('/dashboard/add-new-class',methods=['GET','POST'])
@login_required
@teacher_required
def add_new_class():

    if request.method=='POST':
        user_id = current_user.id
        course_id = request.form.get('course')
        subject_id = request.form.get('subject')
        class_title = request.form.get('class_title')
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 12))
        canonical_url = slugify(class_title)+'-'+random_string
        description = request.form.get('description')
        create_date = request.form.get('create_date')
        try:
            online_classes = Online_classes(user_id=user_id,course_id=course_id,subject_id=subject_id,class_title=class_title,canonical_url=canonical_url,description=description,create_date=create_date)
            db.session.add(online_classes)
            db.session.commit()
            if online_classes:
                online_topics = Online_classes.query.filter_by(id=online_classes.id).first() or abort(500)
                online_topics.canonical_url=slugify(class_title)+'-'+str(online_classes.id)
                db.session.commit() 
            flash('Successfully added','success')
            resp = make_response(redirect(url_for('add_new_class')))
            return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:    
        try:
            courses = Courses.query.filter_by(is_active=True).all()
            resp = make_response(render_template('dashboard/teacher/add-new-class.html',courses=courses))
            return resp
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


@app.route('/dashboard/edit-new-class/<string:cano_url>',methods=['GET','POST'])
@login_required
@teacher_required
def edit_new_class(cano_url):
    if request.method=='POST':
        try:
            online_classes_details=Online_classes.query.filter_by(canonical_url=cano_url, is_complete=False).first()
            if online_classes_details:
                class_title = request.form.get('class_title')
                canonical_url = slugify(class_title)+'-'+str(online_classes_details.id)
                description = request.form.get('description')
                create_date = request.form.get('create_date')

                online_classes_details.class_title=class_title
                online_classes_details.canonical_url=canonical_url
                online_classes_details.description=description
                online_classes_details.create_date=create_date
                db.session.commit()
                flash("Topic details is updated successfully",'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Oops! Topic deails are not valid or completed.",'danger')
                return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        try:
            online_classes_details=Online_classes.query.filter_by(canonical_url=cano_url, is_complete=False).first()
            if online_classes_details:
                return make_response(render_template('dashboard/teacher/edit-topic.html',online_classes=online_classes_details))
            else:
                flash("Oops! Topic deails are not valid or completed.",'danger')
                return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)




@app.route('/dashboard/ajax-fetch-subjects/<int:course_id>')
@login_required
def ajax_fetch_subjects(course_id):
    try:
        subject_list = Teacher_assing_course.query.filter_by(course_id=course_id,user_id=current_user.id).all()
        if subject_list:
            resp= '''{%for subject in subject_list%}:
                        <option value='{{subject.subject_id}}'>{{subject.subject_name}}</option>
                    {%endfor%}'''
            return render_template_string(resp,subject_list=subject_list)
        else:
            return {'error':1,'message':'No subject assign'}        
    except Exception as e:
        app.logger.error(str(e))
        return {'error':1,'message':'Oops! something went wrong.{}'.format(str(e))}

@app.route('/dashboard/broadcast-online-class/<string:cano_url>')
@login_required
@teacher_required
def broadcast_online_class(cano_url):
    try:
        live_course = Online_classes.query.filter_by(canonical_url=cano_url,is_active=1,is_approved=1,is_complete=0).first()
        if live_course:
            chat_history = Chat.query.filter_by(online_class_id=live_course.id).all()
            resp = make_response(render_template('dashboard/teacher/broadcast-online-class.html',live_course=live_course,chat_history=chat_history))
            return resp
        else:
            resp = make_response(redirect(url_for('dashboard')))
            flash('Class is not avaliable or not active.','danger')
            return resp
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)

@app.route('/dashboard/mb-broadcast-online-class/<string:cano_url>')
@login_required
@teacher_required
def mb_broadcast_online_class(cano_url):
    try:
        live_course = Online_classes.query.filter_by(canonical_url=cano_url,is_active=1,is_approved=1,is_complete=0).first()
        if live_course:
            chat_history = Chat.query.filter_by(online_class_id=live_course.id).all()
            resp = make_response(render_template('dashboard/teacher/mb-broadcast-online-class.html',live_course=live_course,chat_history=chat_history))
            return resp
        else:
            resp =  make_response(redirect(url_for('dashboard')))
            flash('Class is not avaliable or not active.','danger')
            return resp
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)

@app.route('/dashboard/watch-classes/<string:cano_url>')
@login_required
@student_required
def watch_live_class(cano_url):
    try:
        live_course = Online_classes.query.filter_by(canonical_url=cano_url,is_active=1,is_approved=1,is_complete=0).first()
        if live_course:
            chat_history = Chat.query.filter_by(online_class_id=live_course.id).all()
            banned_user_form_chat = Ban_chat_users.query.filter_by(online_class_id=live_course.id,banned_user_id=current_user.id).first()
            broadcast_video_stream_record= Broadcast_classe_stream_records.query.filter_by(live_class_id=live_course.id).order_by(Broadcast_classe_stream_records.id.desc()).first()
            resp = make_response(render_template('dashboard/student/watch-classes.html',live_course=live_course,banned_user_form_chat=banned_user_form_chat,\
                broadcast_video_stream_record=broadcast_video_stream_record,chat_history=chat_history))
            return resp
        else:
            flash('Class is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)


@app.route('/dashboard/mb-watch-classes/<string:cano_url>')
@login_required
def mb_watch_live_class(cano_url):
    try:
        live_course = Online_classes.query.filter_by(canonical_url=cano_url,is_active=True,is_approved=True,is_complete=False).first()
        if live_course:
            chat_history = Chat.query.filter_by(online_class_id=live_course.id).all()
            banned_user_form_chat = Ban_chat_users.query.filter_by(online_class_id=live_course.id,banned_user_id=current_user.id).first()
            broadcast_video_stream_record = Broadcast_classe_stream_records.query.filter_by(live_class_id=live_course.id).order_by(Broadcast_classe_stream_records.id.desc()).first()
            resp = make_response(render_template('dashboard/student/mb-watch-classes.html',live_course=live_course,banned_user_form_chat=banned_user_form_chat,\
                broadcast_video_stream_record=broadcast_video_stream_record,chat_history=chat_history))
            return resp
        else:
            flash('Class is not avaliable or not active.','danger')
            resp = make_response(redirect(url_for('dashboard')))
            return resp
    except Exception as e:
        app.logger.error(str(e)) 
        return abort(500)

@app.route('/dashboard/send-chat-msg',methods=['POST'])
@login_required
@csrf.exempt
def send_chat_message():
    user_id =  request.form.get('user_id')
    online_class_id = request.form.get('show_id')
    sender_id = current_user.id
    receiver_id = request.form.get('receiver_id')
    message = request.form.get('chat_msg')
    # return {'user_id':user_id,'online_class_id':online_class_id,'sender_id':sender_id,'receiver_id':receiver_id,'message':message}
    try:
        if message:
            chat = Chat(user_id=user_id, online_class_id= online_class_id, sender_id = sender_id, receiver_id = receiver_id, message = message)
            db.session.add(chat)
            db.session.commit()
            db.session.close()
            return 'message added to the chat'
        else:
            return 'message is empty'        
    except Exception as e:
        app.logger.error(str(e)) 
        return str(e)

@app.route('/dashboard/store-live-records',methods=['POST'])
@login_required
def store_live_records():
    try:
        live_class_id = request.form.get('show_id')
        member_id = current_user.id
        stream_id = request.form.get('stream_id')
        sream_store = Broadcast_classe_stream_records(live_class_id=live_class_id, member_id=member_id, stream_id=stream_id) 
        db.session.add(sream_store)
        db.session.commit()
        return {'error':0,'message':'stream stored'} 
    except Exception as e:
        app.logger.error(str(e)) 
        return {'error':1,'message':'Oops! something went wrong %s'%(str(e))} 

def randomkey(stringLength=10):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength)) 

@app.route('/dashboard/generate-stream',methods=['POST'])
@login_required
def generate_stream():
    if request.method=='POST':
        return randomkey(20)

@app.route('/dashboard/block-chat-member',methods=['POST'])
@login_required
@teacher_required
def block_chat_member():

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


@app.route('/dashboard/complete-live-show',methods=['POST'])    
@login_required
@teacher_required
def complete_live_show():
    if request.method=='POST':
        try:
            online_class_id=request.form.get('sid')
            online_class_details = Online_classes.query.filter_by(id=online_class_id).first()

            if online_class_details:
                online_class_details.is_complete=True
                db.session.commit()
                db.session.close()
                return {'error':0,'message':'class is  marked as completed.'}
            else:
                return {'error':1,'message':'class detail are not valid.'}
        except Exception as e:
            return {'error':1,'message':'Oops! something went wrong. %s'%(str(e))}
    else:
       return {'error':1,'message':'Method is not allowed.'}

@app.route('/dashboard/upload-voice-note',methods=['POST'])
@login_required
@csrf.exempt
def upload_voice_notes():

    try:
        audio_random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 12))
        filename='./static/upload/chat_audio_notes/'+audio_random_str+'.wav'
        with open(filename, 'wb+') as destination:
            for chunk in request.files['audio_data']:
                destination.write(chunk)
        return{'error':0,'message':filename}
    except Exception as e:
        app.logger.error(str(e))
        return{'error':1,'message':str(e)}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/dashboard/upload-trailer-gallery',methods=['POST'])
@login_required
@teacher_required
@csrf.exempt
def upload_chat_content():

    if request.method =='POST':    
        image_portfolio5 = request.files['show_gallery']
        filename = secure_filename(image_portfolio5.filename)
        filetype, extension = splitext(filename)
        newfilename =  str(randomkey(10)).lower() + extension
        image_portfolio5.save(os.path.join(CHAT_UPLOAD_CONTENTS, newfilename)) 
        file_path= '/static/upload/chat_share_file/'+newfilename
        return {'error':'0','message':'{} file uploaded successfully.'.format(newfilename),'file_path':file_path}
    else:
        return  {'error':'1','message':'Sorry file was not uploaded.'}


#Online subscription courses

@app.route('/dashboard/subscribe-package')
@login_required
@student_required
def subscribe_package_details():

    if current_user.online_register==True:
        try:
            stud_pac_sub =  db.session.execute("SELECT student_package_subscription.*,pac_course.seo_title,pac_course.cover_banner,\
                pac_course.description FROM student_package_subscription JOIN pac_course ON \
                student_package_subscription.package_id=pac_course.id  \
                WHERE student_package_subscription.student_id=:param ORDER by student_package_subscription.id DESC",{"param":current_user.id}).fetchall()
            if stud_pac_sub:
                resp = make_response(render_template('dashboard/student/subs-package.html',course_package_info=stud_pac_sub))
                return resp
            else:
                flash('Your package subscription is expired. Please contact with Help team.','danger')
                return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        return redirect(url_for('dashboard'))


@app.route('/dashboard/subscription-info', methods=['POST'])
@login_required
@student_required
def subscription_info():

    if request.method=='POST':
        sbid=request.form.get('sbid')
        pcid= request.form.get('pcid')
        return sbid
        try:
            optional_subject_info = Student_subs_pac_optional.query.filter_by(stu_pac_subs_id=sbid).all()
            subs_months = Student_subs_pac_months.query.filter_by(stu_pac_subs_id=sbid).all()

            if optional_subject_info:
                resp = '''
                        <table class="table table-stripped">
                            <thead>
                                <tr>
                                    <th>Subject Name</thd>
                                    <th>Price</th>
                                </tr>
                            </thead>
                            <tbody>
                                {%for ob_sub in optional_subject_info%} 
                                    <tr>
                                        <td>{{ob_sub.subject_name}}</td>
                                        <td>{{ob_sub.price}}</td>
                                    </tr>
                                {%endfor%}
                            </tbody>
                        </table>
                        '''
            return  render_template_string(resp,optional_subject_info=optional_subject_info)
        except Exception as e:
            app.logger.error(str(e))
            return  {'error':1,'message':'Oops! something went wrong.'}
    else:
        return  {'error':1,'message':'method is not allowed.'}


@app.route('/dashboard/live-class/<cano_url>/<int:id>')
@login_required
@student_required
def subscription_live_class(cano_url,id):

    try:
        package_details = Pac_course.query.filter_by(cano_url=cano_url).first()

        if package_details:
            student_sub_pac = Student_package_subscription.query.filter_by(id=id,package_id=package_details.id, student_id=current_user.id,\
            subs_status=True,payment_status=True).first()
            if student_sub_pac:
                subs_optional_subject_list = db.session.execute("SELECT student_subs_pac_optional.optional_subs,pac_optional_subjects.subject_id\
                    FROM student_subs_pac_optional JOIN pac_optional_subjects on student_subs_pac_optional.optional_subs=pac_optional_subjects.id WHERE \
                    student_subs_pac_optional.stu_pac_subs_id=:param",{"param":student_sub_pac.id}).fetchall() 

                subs_live_class=[]
                if subs_optional_subject_list:
                    
                    for opt in subs_optional_subject_list:
                        online_live_class_list = Online_classes.query.filter_by(course_id=package_details.course_id,subject_id=opt.subject_id,is_active=True,is_approved=True,is_complete=False).all()
                        for live_class in online_live_class_list:
                            subs_live_class.append({'course_name':package_details.course_name,'subject_name':live_class.subject_name,'canonical_url': live_class.canonical_url, 'class_title': live_class.class_title, \
                                'create_date':live_class.create_date,'description':live_class.description})
                
                comp_sub_list = Pac_compulsory_subjects.query.filter_by(pac_course_id=package_details.id).all()
                
                if comp_sub_list:
                    for comp in comp_sub_list:
                        online_live_class_list = Online_classes.query.filter_by(course_id=package_details.course_id,subject_id=comp.subject_id,is_active=True,is_approved=True,is_complete=False).all()
                        for live_class in online_live_class_list:
                            subs_live_class.append({'course_name':package_details.course_name,'subject_name':live_class.subject_name,'canonical_url': live_class.canonical_url, 'class_title': live_class.class_title, \
                                'create_date': live_class.create_date, 'description': live_class.description})
                
                return render_template('dashboard/student/subs-online-live-class.html', optional_live_classes_list=subs_live_class)    
            else:
                flash('Your subscription is not active or expired. For more details contact with support team.','danger')
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard'))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/dashboard/mark_as_complete_topic',methods=['POST'])
@login_required
@teacher_required
def complete_topic_mark():
    if request.method=='POST':
        coid = request.form.get('coid')
        try:
            Livetopic = Online_classes.query.filter_by(id=coid,is_complete=False).first()
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

#watch recordings
@app.route('/dashboard/recordings-old/<cano_url>')
@login_required
@student_required
def recordings_old(cano_url):
    try:
        package_details = Pac_course.query.filter_by(cano_url=cano_url, is_active=True).first()
        if package_details:
            student_sub_pac = Student_package_subscription.query.filter_by(package_id=package_details.id, student_id=current_user.id,subs_status=True, payment_status=True).first()
            # return str(student_sub_pac.id)
            if student_sub_pac:
                currentDT = datetime.datetime.now()
                current_timeTT = currentDT.strftime("%Y-%m-%d %H:%M:%S")
                current_time = datetime.datetime.strptime(str(current_timeTT), "%Y-%m-%d %H:%M:%S")
                subs_optional_subject_list = db.session.execute("SELECT student_subs_pac_optional.optional_subs,pac_optional_subjects.subject_id FROM student_subs_pac_optional JOIN pac_optional_subjects on student_subs_pac_optional.optional_subs=pac_optional_subjects.id WHERE student_subs_pac_optional.stu_pac_subs_id=:param ",{"param":student_sub_pac.id}).fetchall()
                if subs_optional_subject_list:
                    today = student_sub_pac.payment_date
                    student_package_subs_month = today.month
                    subs_live_class=[]
                    for opt in subs_optional_subject_list:
                        online_live_class_list = db.session.execute("select online_classes.*, subjects.subject_name\
                            from online_classes join subjects on online_classes.subject_id=subjects.id \
                            where online_classes.course_id=:param1 AND online_classes.subject_id=:param2 AND online_classes.is_active=True AND \
                            online_classes.is_approved=True AND online_classes.is_complete=True And date_format(date(online_classes.create_date),'%m')>=:param3 order by online_classes.id desc",{"param1":package_details.course_id,"param2":opt.subject_id,"param3":student_package_subs_month }).fetchall()    
                        
                        if online_live_class_list:          
                            for live_class in online_live_class_list:
                                subs_live_class.append({'course_name':package_details.course_name,'subject_name':live_class.subject_name,'canonical_url':live_class.canonical_url,'class_title': live_class.class_title, 'create_date': live_class.create_date, 'description': live_class.description})
                                # record_exp_time = live_class.create_date+datetime.timedelta(seconds=86400) #one month seconds
                                # record_exp_time = datetime.datetime.strptime(str(record_exp_time), "%Y-%m-%d %H:%M:%S")
                                # if current_time<record_exp_time:
                                    # subs_live_class.append({'course_name':package_details.course_name,'subject_name':live_class.subject_name,'canonical_url':live_class.canonical_url,'class_title': live_class.class_title, 'create_date': live_class.create_date, 'description': live_class.description})
                    

                    return render_template('dashboard/student/recordings.html', package_details=package_details, records_class=subs_live_class)
                else:
                    flash('Sorry live class are not available. Please contact to support team for more details.','danger')
                    return redirect(url_for('dashboard'))
            else:
                flash('Your subscription is deactivated. Please contact to support team for more details.','danger')
                return redirect(url_for('dashboard'))
        else:
            flash('Sorry package is expired. Please contact to support team for more details.','danger')
            return redirect(url_for('dashboard'))

    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

#watch recordings
@app.route('/dashboard/recordings/<cano_url>')
@login_required
@student_required
def recordings(cano_url):
    try:
        package_details = Pac_course.query.filter_by(cano_url=cano_url).first()
        if package_details:
            student_sub_pac = Student_package_subscription.query.filter_by(package_id=package_details.id, student_id=current_user.id,subs_status=True, payment_status=True).order_by(Student_package_subscription.id.desc()).first()

            if student_sub_pac:
                currentDT = datetime.datetime.now()
                current_timeTT = currentDT.strftime("%Y-%m-%d %H:%M:%S")
                current_time = datetime.datetime.strptime(str(current_timeTT), "%Y-%m-%d %H:%M:%S")
                subs_optional_subject_list = db.session.execute("SELECT student_subs_pac_optional.optional_subs,pac_optional_subjects.subject_id FROM student_subs_pac_optional JOIN pac_optional_subjects on student_subs_pac_optional.optional_subs=pac_optional_subjects.id WHERE student_subs_pac_optional.stu_pac_subs_id=:param ",{"param":student_sub_pac.id}).fetchall()

                # sql =f"SELECT student_subs_pac_optional.optional_subs,pac_optional_subjects.subject_id FROM student_subs_pac_optional JOIN pac_optional_subjects on student_subs_pac_optional.optional_subs=pac_optional_subjects.id WHERE student_subs_pac_optional.stu_pac_subs_id={student_sub_pac.id}"
                #
                # return sql

                comp_sub_list = Pac_compulsory_subjects.query.filter_by(pac_course_id=package_details.id).all()
                subs_live_class = []
                today = student_sub_pac.payment_date
                student_package_subs_month = today.month 

                """ Compulsory subjects list """
                if comp_sub_list:
                    for comp in comp_sub_list:
                        online_live_class_list= db.session.execute("select online_classes.*, subjects.subject_name\
                            from online_classes join subjects on online_classes.subject_id=subjects.id\
                            where online_classes.course_id=:param1 AND online_classes.subject_id=:param2 AND online_classes.is_active=True AND\
                            online_classes.is_approved=True AND online_classes.is_complete=True And\
                                date_format(date(online_classes.create_date), '%m') >=:param3 order by\
                                    online_classes.id desc",{"param1":package_details.course_id,"param2":comp.subject_id,"param3":5}).fetchall()    
                        
                        if online_live_class_list:          
                            for live_class in online_live_class_list:
                                # record_exp_time = live_class.create_date+datetime.timedelta(seconds=604800) #86400
                                # record_exp_time = datetime.datetime.strptime(str(record_exp_time), "%Y-%m-%d %H:%M:%S")
                                # if current_time<record_exp_time:
                                subs_live_class.append({'course_name': package_details.course_name, 'subject_name': live_class.subject_name, \
                                    'canonical_url': live_class.canonical_url, 'class_title': live_class.class_title,\
                                        'create_date': live_class.create_date, 'description': live_class.description})          
                
                if subs_optional_subject_list:
                    for opt in subs_optional_subject_list:

                        sql=f"select online_classes.*, subjects.subject_name\
                            from online_classes join subjects on online_classes.subject_id=subjects.id \
                            where online_classes.course_id={package_details.course_id} AND online_classes.subject_id={opt.subject_id} AND online_classes.is_active=True AND \
                            online_classes.is_approved=True AND online_classes.is_complete=True And date_format(date(online_classes.create_date),'%m')>={student_package_subs_month}"

                        # subs_live_class.append(sql)

                        online_live_class_list = db.session.execute("select online_classes.*, subjects.subject_name\
                            from online_classes join subjects on online_classes.subject_id=subjects.id \
                            where online_classes.course_id=:param1 AND online_classes.subject_id=:param2 AND online_classes.is_active=True AND \
                            online_classes.is_approved=True AND online_classes.is_complete=True And date_format(date(online_classes.create_date),'%m')>=:param3 order by online_classes.id desc",{"param1":package_details.course_id,"param2":opt.subject_id,"param3":student_package_subs_month }).fetchall()

                        if online_live_class_list:
                            for live_class in online_live_class_list:
                                # record_exp_time = live_class.create_date+datetime.timedelta(seconds=604800) #86400
                                # record_exp_time = datetime.datetime.strptime(str(record_exp_time), "%Y-%m-%d %H:%M:%S")
                                # if current_time<record_exp_time:
                                subs_live_class.append({'course_name':package_details.course_name,'subject_name':live_class.subject_name,'canonical_url':live_class.canonical_url,'class_title': live_class.class_title, 'create_date': live_class.create_date, 'description': live_class.description})

                # return jsonify({'sql':sql})


                return render_template('dashboard/student/recordings.html', package_details=package_details, records_class=subs_live_class)
                """ else:
                    flash('Sorry live class are not available. Please contact to support team for more details.','danger')
                    return redirect(url_for('dashboard')) """
            else:
                flash('Your subscription is deactivated. Please contact to support team for more details.','danger')
                return redirect(url_for('dashboard'))
        else:
            flash('Sorry package is expired. Please contact to support team for more details.','danger')
            return redirect(url_for('dashboard'))

    except Exception as e:
        app.logger.error(str(e))
        return abort(500)



@app.route('/dashboard/watch-recording/<cano_url>')
@login_required
@student_required
def watch_recording(cano_url):
    try:
        online_live_class = Online_classes.query.filter_by(canonical_url=cano_url,is_active=True,is_approved=True,is_complete=True).first()
        if online_live_class:
            broadcast_classe_stream_records = Broadcast_classe_stream_records.query.filter_by(live_class_id=online_live_class.id).all()
            resp = make_response(render_template('dashboard/student/watch-record.html',online_live_class=online_live_class, broadcast_classe_stream_records=broadcast_classe_stream_records))
            return resp
        else:
            flash('Sorry, records are not availble ','danger')
            redirect(url_for('recordings',cano_url=cano_url))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)



""" Seminar List """
@app.route('/dashboard/seminar/list')
@login_required
def stu_joined_sem_list():
    try:
        sem_list = Seminar_attend.query.filter_by(student_id=current_user.id).all()
        seminars_list = []
        if sem_list:
            for sem in sem_list:
                seminar = Seminars.query.filter_by(id=sem.seminar_id, is_active=True).first()
                if seminar:
                    seminars_list.append(
                        {'seminar_id': seminar.id, 'title': seminar.title, 'canonical_url': seminar.canonical_url, \
                         'description': seminar.description, 'cover_banner': seminar.cover_banner,
                         'seminar_date': seminar.seminar_date}
                    )

            return render_template('dashboard/student/seminar-list.html', seminars_list=seminars_list)
        else:
            current_month = datetime.datetime.now().month
            stu_subs_packages = db.session.execute(f"SELECT student_package_subscription. *, \
                            student_subs_pac_months.subs_month, pac_course.course_id FROM student_package_subscription \
                            JOIN student_subs_pac_months ON student_package_subscription.id = student_subs_pac_months.stu_pac_subs_id \
                            JOIN pac_course ON pac_course.id = student_package_subscription.package_id  \
                            WHERE student_subs_pac_months.subs_month = {current_month} AND student_package_subscription.student_id = {current_user.id} AND student_package_subscription.purpose=2").fetchall()
            sem_list_sub = []
            if stu_subs_packages:
                subsription_courses_array = []
                for subs_pac in stu_subs_packages:
                    subsription_courses_array.append(subs_pac.course_id)
                if subsription_courses_array:
                    seminar_details = db.session.execute("SELECT seminars.*, seminar_details.course_id FROM seminars \
                                        JOIN seminar_details ON seminars.id = seminar_details.seminar_id WHERE seminars.is_active = TRUE and  \
                                        seminar_details.course_id in :param1 GROUP BY seminars.id",{"param1": subsription_courses_array}).fetchall()
                    if seminar_details:
                        for sem in seminar_details:
                            sem_list_sub.append(
                                {'seminar_id': sem.id, 'title': sem.title, 'canonical_url': sem.canonical_url, \
                                 'description': sem.description, 'cover_banner': sem.cover_banner,
                                 'seminar_date': sem.seminar_date})
              
            return render_template('dashboard/student/seminar-list.html', sem_list_sub=sem_list_sub)
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/dashboard/seminar/activate/<cano_url>')
@login_required
@student_required
def activate_seminar_watch(cano_url):
    try:
        seminar = Seminars.query.filter_by(canonical_url=cano_url, is_active=True).first()
        if seminar:
            attended_seminar_status = Seminar_attend.query.filter_by(seminar_id=seminar.id,
                                                                     student_id=current_user.id).first()
            if not attended_seminar_status:
                attend_sem = Seminar_attend(seminar_id=seminar.id, student_id=current_user.id, is_free=False,
                                            price=seminar.price)
                db.session.add(attend_sem)
                db.session.commit()

                sem_ = Seminar_attend.query.filter_by(id=attend_sem.id).first()
                sem_.activated_from_dash = True
                db.session.commit()
                db.session.close()

                flash('You have successfully activated seminar', 'success')
                return redirect(url_for('stu_joined_sem_list'))
            else:
                flash('You have aleray subscribed/activated the seminar', 'danger')
                return redirect(url_for('stu_joined_sem_list'))
        else:
            flash('Oops! Seminar details are not valid.', 'danger')
            return redirect(url_for('stu_joined_sem_list'))
    except Exception as e:
        app.logger.error(str(e))
        return abort('500')

""" Seminar List in teacher dashboard """
@app.route('/teacher-joined-sem-list')
def teacher_joined_sem_list():
    try:
        sem_topic_list = Seminar_details.query.filter_by(teacher_id=current_user.id).all()
        seminars_list=[]
        if sem_topic_list:
            for sem in sem_topic_list:
                seminar = Seminars.query.filter_by(id=sem.seminar_id,is_active=True).first()
                if seminar:
                    seminars_list.append({'course_name': sem.course_name, 'subject_name': sem.subject_name, 'topic_title': sem.topic_titile, \
                        'start_time':sem.start_time, 'end_time':sem.end_time, \
                        'seminar_id': seminar.id, 'title': seminar.title, 'canonical_url': seminar.canonical_url, \
                        'description':seminar.description,'cover_banner':seminar.cover_banner,'seminar_date':seminar.seminar_date})
            
        return render_template('dashboard/teacher/seminar-list.html', seminars_list=seminars_list)
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


""" student subscribed package details """
@app.route('/dashboard/subs-package-details/<int:subs_id>')
@login_required
def subs_package_details(subs_id):
    try:
        subscription_info =Student_package_subscription.query.filter_by(id=subs_id).first()
        if subscription_info:

            student_subscription_month_list=Student_subs_pac_months.query.filter_by(stu_pac_subs_id=subs_id).all()
            # student_subscription_optional_subjects=Student_subs_pac_optional.query.filter_by(stu_pac_subs_id=subs_id).all()
            # student_subscription_compulsory_subjects=Pac_compulsory_subjects.query.filter_by(pac_course_id=subscription_info.package_id).all()

            """ Find the details of optional subjects """
            optional_subject_details=[]
            optional_sub_list = Student_subs_pac_optional.query.filter_by(stu_pac_subs_id=subs_id).all()
            for optional_subject in optional_sub_list:
                optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_subject.optional_subs).first()
                optional_subject_details.append({'subject_name':optional_subject_info.subject_name})

            """ Find the details of compulsory subjects """
            compulsory_subject_details=[]
            
            comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=subscription_info.package_id).all()
            for cps in comp_sub: 
                compulsory_subject_details.append({'subject_name':cps.subject_name})

            resp = """
                    {%if student_subscription_month_list%}
                    {%for subs_month in student_subscription_month_list%}
                        <div class="badge badge-info">{{subs_month.month_name}}</div>
                    {%endfor%}
                    {%endif%}
                    {%if  optional_subject_details%}
                    <p>Optional</p>
                    <ul>
                    {%for subs_opt_subj in optional_subject_details %}
                        <li>{{subs_opt_subj.subject_name}}</li>
                    {%endfor%}
                    </ul>
                    {%endif%}
                    {%if  compulsory_subject_details%}
                     
                    <p>Compulsory</p>
                    <ul>
                    {%for comp_subj in compulsory_subject_details %}
                        <li>{{comp_subj.subject_name}}</li>
                    {%endfor%}
                    </ul>
                    {%endif%}



                    """
            
            return render_template_string(resp,student_subscription_month_list=student_subscription_month_list,
            optional_subject_details=optional_subject_details,compulsory_subject_details=compulsory_subject_details)
        else:
            return jsonify({'error':1,'message':'Sorry subscription details are not valid.'})
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({'error':1,'message':'Oops! something went wrong'})


""" Expired classes list """
@app.route('/dashboard/expired-classes')
@login_required
@student_required
def expired_subscribed_packages():

    stud_pac_sub=db.session.execute("SELECT student_package_subscription.*,pac_course.seo_title,pac_course.cano_url,\
                pac_course.description,pac_course.price FROM student_package_subscription JOIN pac_course ON \
                student_package_subscription.package_id=pac_course.id  \
                WHERE student_package_subscription.subs_status=False and student_package_subscription.student_id=:param ORDER by student_package_subscription.id DESC",{"param":current_user.id}).fetchall()
    
    return render_template('dashboard/student/expired-packages.html', course_package_info=stud_pac_sub)


"""Wallet Account"""
@app.route('/dashboard/wallet')
@login_required
@student_required
def wallet():
    try:
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    except Exceptoin as e:
        app.logger.error(str(e))
        return abort(500)
    return make_response(render_template('dashboard/student/wallet.html', wallet=wallet))


@app.route('/dashboard/teacher/wallet')
@login_required
@teacher_required
def teacher_wallet():
    try:
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
    except Exceptoin as e:
        app.logger.error(str(e))
        return abort(500)
    return make_response(render_template('dashboard/teacher/wallet.html', wallet=wallet))


@app.route('/admin/referral/wallet/withdrawal')
@login_required
def withdrawal_wat_amt():
    try:
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if wallet and wallet.amount> 0:
            db.session.add(Wallet_withdrawal_request(user_id = current_user.id, amount = wallet.amount))
            db.session.commit()
            db.session.close()
            flash('Your have successfully applied for withdrawal request.', 'success')
            return redirect(url_for('wallet'))
        else:
            flash('Sorry you have no sufficient amount in your wallet.', 'danger')
            return redirect(url_for('wallet'))
    except Exceptoin as e:
        app.logger.error(str(e))
        return abort(500)