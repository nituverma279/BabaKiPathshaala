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
import urllib.parse

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


""" Student can renew their subscribed package """
@app.route('/dashboard/renew-subscription/<int:id>/<int:subs_id>',methods=['GET','POST'])
@login_required
@student_required
def renew_subscription(id,subs_id):

    if request.method == 'POST':
        pcgd = request.form.get('pcgd')
        optional_subject = request.form.getlist('optional_subject')
        months = request.form.getlist('month')

        if len(months) < 1:
            return redirect(url_for('renew_subscription', id=id)) 
        else:
            subscribe_course_package=[]
            subs_month=[]
            subs_opt_subjs=[]

            for month in months:
                subs_month.append(month)

            for opt_sub in optional_subject:
                subs_opt_subjs.append(opt_sub)

            session['subs_pac_id']=pcgd
            session['subs_optional_subjects']=subs_opt_subjs #subscribe_course_package
            session['subs_months']=subs_month 
            return redirect(url_for('renew_payment_process'))
    else:
        try:
            course_package = Pac_course.query.filter_by(id=id,is_active=True).first()
            if course_package:

                """ Package infomation like expired month, optional subjects and compulsory subjects """
                months = package_months(course_package.expire_month)
                comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=course_package.id).all()
                opt_sub = Pac_optional_subjects.query.filter_by(pac_course_id=course_package.id).all()

                """ Student subscribed optional subject list  """
                
                stu_sub_opt_sub = Student_package_subscription.query.filter_by(id=subs_id,package_id=id,student_id=current_user.id).first()
                student_subs_pac_opt = Student_subs_pac_optional.query.filter_by(stu_pac_subs_id=stu_sub_opt_sub.id).all()

                subscribed_optional_subjects=[]
                if student_subs_pac_opt:
                    for stu_subs_pac_opt in student_subs_pac_opt:
                        subscribed_optional_subjects.append(stu_subs_pac_opt.optional_subs)

                """ Student subscribed Months list """ 
                stu_sub_pac_all = Student_package_subscription.query.filter_by(package_id=id,student_id=current_user.id).all()
                subscribed_optional_months=[]
                sql=[]
                if stu_sub_pac_all:
                    for stu_subscription in stu_sub_pac_all:
                        student_subs_pac_month = Student_subs_pac_months.query.filter_by(stu_pac_subs_id=stu_subscription.id).all()
                        query=f"Select * from Student_subs_pac_months where stu_pac_subs_id={stu_subscription.id}"
                        sql.append(query)
                        if student_subs_pac_month:
                            for stu_subs_pac_mon in student_subs_pac_month:
                                subscribed_optional_months.append(stu_subs_pac_mon.subs_month)
                
                # return jsonify(subscribed_optional_months)

                total_comp_sub_price = 0
                if comp_sub:
                    for cps in comp_sub:
                        total_comp_sub_price = total_comp_sub_price + cps.price
                        
                resp = make_response(render_template('dashboard/student/renew-subscription.html', subscribed_optional_subjects=subscribed_optional_subjects, \
                    course_package=course_package, comp_sub=comp_sub, opt_sub=opt_sub, total_comp_sub_price=total_comp_sub_price, months=months, \
                        subscribed_optional_months=subscribed_optional_months))
                return resp
            else:
                return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)

 
def package_months(expire_month):

    try:
        today = datetime.datetime.today()
        current_month = datetime.datetime.now().month
        total_months = db.session.execute("Select * from months where id between :param1 and :param2",{'param1':current_month,'param2':expire_month}).fetchall()
        pac_months=[]
        for month in total_months:
            pac_months.append({'id':month.id,'month_name':month.month_name})
        return pac_months
    except Exception as e:
        app.logger.error(str(e))
        return {'error': 'Oops! something went wrong.'}
        
@app.route('/dashboard/renew-payment-process')
@login_required
@student_required
def renew_payment_process():

    if session.get('subs_pac_id'):
        if current_user.online_register==True:
            try:
                pac_course = Pac_course.query.filter_by(id=session.get('subs_pac_id')).first()
                if pac_course:
                    total_payable_amount=0
                    current_month = datetime.datetime.now().month
                    current_year = datetime.datetime.now().year

                    """ Check that current month and year is not expired """
                    if pac_course.expire_month>=current_month and pac_course.expire_year>=current_year :
                        comp_subject_details=[]
                        optional_subject_details=[]
                        subs_months_details=[]
                        """ Get the pirce of compuslory subjects """
                        comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=session.get('subs_pac_id')).all()
                        if comp_sub:
                            
                            for cps in comp_sub:    
                                total_payable_amount=total_payable_amount+cps.price
                                comp_subject_details.append({'subject_name':cps.subject_name,'price':cps.price})

                        """ Get the price of optional subjects  """
                        if len(session.get('subs_optional_subjects'))>0:
                            
                            for optional_sub in session.get('subs_optional_subjects'):
                                optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
                                # subject= Subjects.query.filter_by(id=optional_sub).first()
                                optional_subject_details.append({'subject_name':optional_subject_info.subject_name,'price':optional_subject_info.price})
                                total_payable_amount=total_payable_amount+optional_subject_info.price

                        if len(session.get('subs_months'))>0:
                            for month in session.get('subs_months'):
                                sub_month = Months.query.filter_by(id=month).first()
                                subs_months_details.append({'month_name':sub_month.month_name})
                                

                         
                        total_payable_amount=int(total_payable_amount*len(session.get('subs_months')))
                        subtotal= total_payable_amount

                        """ Discount on total payment amount """
                        discount_amt=0
                        if len(session.get('subs_optional_subjects'))==3:
                            discount_amt=(total_payable_amount*10)/100
                            total_payable_amount=total_payable_amount-discount_amt
                        
                        elif len(session.get('subs_optional_subjects'))>3:
                            discount_amt=(total_payable_amount*20)/100
                            total_payable_amount = total_payable_amount - discount_amt

                          
                        return render_template(
                                'dashboard/student/payment-process.html',
                                subtotal=subtotal, discount_amt=discount_amt,
                                subs_months_details=subs_months_details,
                                comp_subject_details=comp_subject_details,
                                optional_subject_details=optional_subject_details,
                                total_payable_amount=total_payable_amount
                            )
                    else:
                        return 'Package is expired'
            except Exception as e:
                app.logger.error(str(e))
                return abort(500) 
        else:
            """ Unset all session of payments """
            if session.get('subs_pac_id'):
                session.pop('subs_pac_id')
            if session.get('subs_optional_subjects'):
                session.pop('subs_optional_subjects')
            if session.get('subs_months'):
                session.pop('subs_months')
            message = 'Sorry, Genius Arena Tuition student cannot purchase this package. <br/> Please contact support for more information.'
            return render_template('home/info.html',message=message)
    else:
        return redirect(url_for('packages'))


@app.route('/dashboard/renew-payment-option',methods=['GET','POST'])
def renew_payment_option():
    if session.get('subs_pac_id'):
        if request.method == 'POST':
            payment_option_select = request.form.get('payment_option_select')
            if payment_option_select == 'online':
                return redirect(url_for('renew_payment_online'))
            else:
                return redirect(url_for('renew_payment_offline'))
        else:
            return render_template('dashboard/student/payment-option.html')
    else:
        return render_template('dashboard')


@app.route('/dashboard/payment-online')
@login_required
def renew_payment_online():

    if session.get('subs_pac_id'):
        try:
            """ Upload payment receipt """
            total_payable_amount=0
            """ Get the pirce of compuslory subjects """
            comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=session.get('subs_pac_id')).all()
            for cps in comp_sub:
                total_payable_amount=total_payable_amount+cps.price

            """ Get the price of optional subjects  """
            for optional_sub in session.get('subs_optional_subjects'):
                optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
                total_payable_amount = total_payable_amount + optional_subject_info.price
            
            amount = int(total_payable_amount*len(session.get('subs_months')))

            """ Discount on total payment amount """
            dis_amount=0
            if len(session.get('subs_optional_subjects'))==3:
                dis_amount=(amount*10)/100
                amount=amount-dis_amount
            
            elif len(session.get('subs_optional_subjects'))>3:
                dis_amount=(amount*20)/100
                amount=amount-dis_amount

            merchant_id = str(app.config['MERCHANT_ID'])
            api = str(app.config['API'] )
            invoice ='GEN'+str(current_user.id)+''+randomkey(4).upper()
            amount = str('%.2f' %float(amount))
            payment_desc = 'Purchase_Course_Online'
            hashed_string = api+"|"+urllib.parse.quote(merchant_id)+"|"+urllib.parse.quote(invoice)+"|"+urllib.parse.quote(amount)+"|"+urllib.parse.quote(payment_desc)
            
            return render_template('dashboard/student/process-form.html',hashed_string=hashed_string, merchant_id=merchant_id,invoice=invoice,amount=amount,payment_desc=payment_desc)
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        return redirect(url_for('dashboard'))


@app.route('/dashboard/renew_callbackv2', methods=['POST','GET'])
@csrf.exempt
def renew_callbackv2():

    if session.get('subs_pac_id'):
        try:
            total_payable_amount = 0
            """ Get the pirce of compuslory subjects """
            comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=session.get('subs_pac_id')).all()
            for cps in comp_sub:
                total_payable_amount = total_payable_amount + cps.price
                
            """ Get the price of optional subjects  """
            for optional_sub in session.get('subs_optional_subjects'):
                optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
                total_payable_amount = total_payable_amount + optional_subject_info.price

            amount = int(total_payable_amount * len(session.get('subs_months'))) * 100

            """ Discount on total payment amount """
            dis_amount = 0
            
            if len(session.get('subs_optional_subjects')) == 3:
                dis_amount = (amount * 10) / 100
                amount = amount - dis_amount

            elif len(session.get('subs_optional_subjects')) > 3:
                dis_amount = (amount * 20) / 100
                amount = amount - dis_amount

            trx_id=''
            if request.form.get('pay_method') == 'fpx': 
                trx_id = request.form.get('fpx_fpxTxnId')
            elif request.form.get('pay_method') == 'paypal':
                trx_id = request.form.get('paypal_trx_id')
            elif request.form.get('pay_method') == 'mastercard':
                trx_id = request.form.get('mastercard_trx_id')
            elif request.form.get('pay_method') == 'others':
                trx_id = request.form.get['others_trx_id']
            #$_REQUEST['pay_method'] = $_REQUEST['trx_txt']; #EX: Boost eWallet and etc
                
            if trx_id:
                """ Store the information of subscription to the db """
                subs_pac_info=Student_package_subscription(
                        student_id=current_user.id,
                        package_id=session.get('subs_pac_id'),
                        total_amount=total_payable_amount*len(session.get('subs_months')),
                        coupon_code=None,
                        discount_amount=(dis_amount/100),
                        total_payable_amount=(amount/100),
                        transcation_id=trx_id,
                        invoice=request.form.get('invoice_no'),
                        receipt='',
                        payment_status=bool(str('True')),
                        payment_mode='online',
                        subs_status=True,
                        purpose=2
                    )
                db.session.add(subs_pac_info)
                db.session.commit()

                subscription_trans_log = Subscription_trans_log(student_id=current_user.id, package_id=session.get('subs_pac_id'), total_amount=total_payable_amount*len(session.get('subs_months')), coupon_code=None,discount_amount=(dis_amount/100), total_payable_amount=(amount/100),transcation_id=trx_id, invoice=request.form.get('invoice_no'), receipt='', payment_mode='online', purpose='R')
                db.session.add(subscription_trans_log)
                db.session.commit()

                if len(session.get('subs_optional_subjects'))>0:
                    for optional_sub in session.get('subs_optional_subjects'):
                        subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,optional_subs=optional_sub)
                        db.session.add(subs_optional_sub_info)
                        db.session.commit()

                if len(session.get('subs_months'))>0:
                    for month in session.get('subs_months'):
                        student_subs_month= Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id, subs_month=month)
                        db.session.add(student_subs_month)
                        db.session.commit()

                """ Unset all session of payments """
                if session.get('subs_pac_id'):
                    session.pop('subs_pac_id')
                if session.get('subs_optional_subjects'):
                    session.pop('subs_optional_subjects')
                if session.get('subs_months'):
                    session.pop('subs_months')
                flash('Your payment is successfull. Your subscription is updated','success')
                return redirect(url_for('dashboard'))
            else:
                message = 'Sorry, your transaction is not completed Please contact with support team.'
                return render_template('home/info.html', message=message)
        except Exception as e:
            app.logger.error(str(e))
    else:
        return redirect(url_for('dashboard'))

@app.route('/dashboard/payment-offline',methods=['GET','POST'])
@login_required
def renew_payment_offline():

    if session.get('subs_pac_id'):
        if request.method=='POST':
            try:
                pac_course = Pac_course.query.filter_by(id=session.get('subs_pac_id')).first()
                if pac_course:
                    payment_receipt = request.files['payment_receipt']
                    filename = secure_filename(payment_receipt.filename) 
                    filetype, extension = splitext(filename)
                    newfilename =  str(randomkey(10)).lower() + extension
                    payment_receipt.save(os.path.join(RECEIPT_UPLOAD_CONTENTS, newfilename)) 
                    receipt_file_path= '/static/upload/receipt/'+newfilename

                    """ Upload payment receipt """
                    total_payable_amount=0
                    """ Get the pirce of compuslory subjects """
                    comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=session.get('subs_pac_id')).all()
                    for cps in comp_sub:
                        total_payable_amount=total_payable_amount+cps.price

                    """ Get the price of optional subjects  """
                    for optional_sub in session.get('subs_optional_subjects'):
                        optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
                        total_payable_amount=total_payable_amount+optional_subject_info.price

                    amount = int(total_payable_amount*len(session.get('subs_months')))*100

                    """ Discount on total payment amount """
                    dis_amount=0
                    if len(session.get('subs_optional_subjects'))==3:
                        dis_amount=(amount*10)/100
                        amount=amount-dis_amount
                    
                    elif len(session.get('subs_optional_subjects'))>3:
                        dis_amount=(amount*20)/100
                        amount=amount-dis_amount
                    
                    
                    """ Store the information of subscription to the db """
                    subs_pac_info=Student_package_subscription(
                            student_id=current_user.id,
                            package_id=session.get('subs_pac_id'),
                            total_amount=total_payable_amount*len(session.get('subs_months')),
                            coupon_code=None,
                            discount_amount=(dis_amount/100),
                            total_payable_amount=(amount/100),
                            transcation_id='',
                            invoice='',
                            receipt=receipt_file_path,
                            payment_status=False,
                            payment_mode='online',
                            subs_status=False,
                            purpose=2 #renewal subscription code
                        )
                    db.session.add(subs_pac_info)
                    db.session.commit()

                    subscription_trans_log = Subscription_trans_log(student_id=current_user.id, package_id=session.get('subs_pac_id'), total_amount=total_payable_amount*len(session.get('subs_months')), coupon_code=None,discount_amount=(dis_amount/100), total_payable_amount=(amount/100),transcation_id='',invoice='', receipt=receipt_file_path, payment_mode='online', purpose='Purchase new subscription.')
                    db.session.add(subscription_trans_log)
                    db.session.commit()

                    if len(session.get('subs_optional_subjects'))>0:
                        for optional_sub in session.get('subs_optional_subjects'):
                            subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,optional_subs=optional_sub)
                            db.session.add(subs_optional_sub_info)
                            db.session.commit()

                    if len(session.get('subs_months'))>0:
                        for month in session.get('subs_months'):
                            student_subs_month= Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id, subs_month=month)
                            db.session.add(student_subs_month)
                            db.session.commit()

                    """ Unset all session of payments """
                    if session.get('subs_pac_id'):
                        session.pop('subs_pac_id')
                    if session.get('subs_optional_subjects'):
                        session.pop('subs_optional_subjects')
                    if session.get('subs_months'):
                        session.pop('subs_months')

                    flash('You have successfully renew subscription','success')
                    return redirect(url_for('dashboard')) 
                else:
                    flash('Package details are not valid. Please contact to support team.','danger')
                    return redirect(url_for('dashboard')) 
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
        else:
            try:
                """ Upload payment receipt """
                total_payable_amount=0
                """ Get the pirce of compuslory subjects """
                comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=session.get('subs_pac_id')).all()
                for cps in comp_sub:
                    total_payable_amount=total_payable_amount+cps.price

                """ Get the price of optional subjects  """
                for optional_sub in session.get('subs_optional_subjects'):
                    optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
                    total_payable_amount=total_payable_amount+optional_subject_info.price

                amount = int(total_payable_amount*len(session.get('subs_months')))*100

                """ Discount on total payment amount """
                dis_amount=0
                if len(session.get('subs_optional_subjects'))==3:
                    dis_amount=(amount*10)/100
                    amount=amount-dis_amount
                
                elif len(session.get('subs_optional_subjects'))>3:
                    dis_amount=(amount*20)/100
                    amount=amount-dis_amount
                return render_template('dashboard/student/payment-offline.html',payamount=amount)
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
    else:
        return redirect(url_for('dashboard'))

def randomkey(stringLength=10):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength)) 