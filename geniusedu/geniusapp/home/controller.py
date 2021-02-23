from geniusapp import app,db,csrf,config,login_manager
from flask import current_app,render_template,url_for, abort,request,make_response,flash,redirect,jsonify,session,json,send_from_directory
from geniusapp.home.form import ContactForm
from geniusapp.model.tables import Contact_us,Online_demo_classes, Pac_course,Pac_compulsory_subjects,\
    Subjects,Courses,Pac_optional_subjects,Coupon,Student_package_subscription,Student_subs_pac_months,\
    Student_subs_pac_optional,Months,Subscription_trans_log,Seminars,Seminar_details,Seminar_attend
from _ast import Param   
import datetime
import stripe
from flask_login import login_user,current_user,login_required
from flask_mail import Mail, Message
from functools import wraps
import random
import string
from werkzeug.utils import secure_filename
import os
from os.path import splitext
import hashlib
import urllib.parse
import re

# configuration of mail 
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] =587
app.config['MAIL_USERNAME'] = 'babakipathshaala.tech@gmail.com'
app.config['MAIL_PASSWORD'] = 'tech09871234'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app) 


stripe_keys = {
  'secret_key': 'sk_test_wi4psHh3LoBTiAkfwZKJiJo600sYCxeON3',
  'publishable_key': 'pk_test_JUiX8n2A3zlLoZ8HiMdF1VgF00iEQvMAgY'
}
stripe.api_key = stripe_keys['secret_key']

basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECEIPT_UPLOAD_CONTENTS = basedir+'/static/upload/receipt/'


def student_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.user_role_id == 4:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/maintance')
def homemaintance():
     return render_template('home/server-maintance.html')

@app.route('/')
def home():
    try:
        # demo_live_classes = Online_demo_classes.query.filter_by(is_active=True,is_complete=False).all()
        # seminars = Seminars.query.filter_by(is_active=True).order_by(Seminars.id.desc()).all()
         return render_template('home/home.html')
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)
        #  return render_template('home/home.html')

@app.route('/about')
def about_us():
    return render_template('home/about-us.html')

@app.route('/genius-tuition')
def genius_tution():
    return render_template('home/genius-tuition.html')

@app.route('/genius-online-tuition')
def genius_online_tuition():
    try:
        course_package = Pac_course.query.filter_by(is_active=True).order_by(Pac_course.id.desc()).all()
        resp = make_response(render_template('home/genius-online-tuition.html',course_package=course_package))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/genius-tuition-center')
def genius_tuition_center():
    return render_template('home/genius-tuition-center.html')


@app.route('/spm-seminar')
def free_spm_seminar():
    return render_template('home/free-spm-seminar.html')


@app.route('/contact',methods=['GET','POST'])
def contact():
    name = request.form.get('name')
    return str("hello")

    # if request.method == "POST":
    #     # form = ContactForm(request.form)
    #     name = request.form.get('name')
    #     email = request.form.get('email')
    #     subject = request.form.get('subject')
    #     message = request.form.get('message')
    #     msg = Message(subject=f"Message: {subject}", body=f"Name: {name}\nE-Mail: {email}\n\n{message}", sender='babakipathshaala.tecg@gmail.com', recipients=['nituverma279@gmail.com'])
    #     mail.send(msg)
    #     return render_template('/#contact',form=form, success=True)


    # if request.method=='POST':
    #     form = form = ContactForm(request.form)
    #     if form.validate()== False:
    #         flash('Shi')
    #         resp= make_response(render_template('/',form=form))
    #         return resp
    #     else:
    #         name = request.form.get('name')
    #         email = request.form.get('email')
    #         subject = request.form.get('subject')
    #         message = request.form.get('message')
    #         try:
    #             contact_us = Contact_us(name=name,email=email,subject=subject,message=message)
    #             db.session.add(contact_us)
    #             db.session.commit()
    #             db.session.close()
    #             flash('Soon we will get in your touch.','success')
    #             resp = make_response(redirect(url_for('contact')))
    #             return resp
    #         except Exception as e:
    #             app.logger.error(str(e))
    #             return abort(500)
    # else:
    #     try:
    #         form = ContactForm()
    #         resp= make_response(render_template('/',form=form))
    #         return resp
    #     except Exception as e:
    #         app.logger.error(str(e))
    #         return abort(500)


    # else:
    #      resp= make_response(render_template('/#contact',form=form))


@app.route('/packages')
def packages():
    try:
        
        # course_package = Pac_course.query.filter_by(is_active=True).order_by(Pac_course.id.desc()).all()
        resp = make_response(render_template('dashboard/usersBoard/dashboard.html'))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)

@app.route('/purchase-package/<string:cano_url>',methods=['GET','POST'])
def purchase_packages(cano_url):

    if request.method=='GET':
        try:
            course_package = Pac_course.query.filter_by(cano_url=cano_url,is_active=True).first()
            if course_package:
                months = package_months(course_package.expire_month)
                comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=course_package.id).all()
                opt_sub = Pac_optional_subjects.query.filter_by(pac_course_id=course_package.id).all()
                total_comp_sub_price = 0
                if comp_sub:
                    for cps in comp_sub:
                        total_comp_sub_price=total_comp_sub_price+cps.price
                resp = make_response(render_template('home/purchase-package.html', course_package=course_package, comp_sub=comp_sub, opt_sub=opt_sub, total_comp_sub_price=total_comp_sub_price,months=months))
                return resp
            else:
                return redirect(url_for('packages')) 
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        pcgd = request.form.get('pcgd')
        optional_subject = request.form.getlist('optional_subject')
        months = request.form.getlist('month')
        cano_url = request.form.get('cano')
        
        if session.get('subs_pac_id'):
            session.pop('subs_pac_id')

        if session.get('subs_optional_subjects'):
            session.pop('subs_optional_subjects')

        if session.get('subs_months'):
            session.pop('subs_months')    
        

        if len(months) < 1:
            return redirect(url_for('purchase_packages', cano_url=cano_url)) 
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
            return redirect(url_for('payment_process'))


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
        return {'error':'Oops! something went wrong.'}


@app.route('/payment-process',methods=['GET','POST'])
@login_required
def payment_process():

    if session.get('subs_pac_id'):

        # exists_pac_info = Student_package_subscription.query.filter_by(student_id=current_user.id, package_id=session.get('subs_pac_id')).first()
        # if exists_pac_info:
        #     """ Unset all session of payments """
        #     if session.get('subs_pac_id'):
        #         session.pop('subs_pac_id')
        #     if session.get('subs_optional_subjects'):
        #         session.pop('subs_optional_subjects')
        #     if session.get('subs_months'):
        #         session.pop('subs_months')
        #
        #     message = 'You have already subscribed this package.'
        #     return render_template('home/info.html', message=message)
        # else:
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


                        stripe_publishable_key = stripe_keys['publishable_key']
                        total_payable_amount=int(total_payable_amount*len(session.get('subs_months')))
                        subtotal= total_payable_amount

                        """ Discount on total payment amount """
                        discount_amt=0
                        if len(session.get('subs_optional_subjects'))==3:
                            """for crash course"""
                            if pac_course.is_crash_course:
                                discount_amt = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
                                total_payable_amount = total_payable_amount-discount_amt
                            else:
                                discount_amt = (total_payable_amount * 10) / 100
                                total_payable_amount = total_payable_amount - discount_amt

                        elif len(session.get('subs_optional_subjects'))>3:
                            """for crash course"""
                            if pac_course.is_crash_course:
                                discount_amt = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
                                total_payable_amount = total_payable_amount - discount_amt
                            else:
                                discount_amt=(total_payable_amount*20)/100
                                total_payable_amount=total_payable_amount-discount_amt

                        return render_template('home/payment-process.html',subtotal=subtotal,discount_amt=discount_amt,subs_months_details=subs_months_details, comp_subject_details=comp_subject_details,optional_subject_details=optional_subject_details, total_payable_amount=total_payable_amount,stripe_publishable_key=stripe_publishable_key)
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
        
@app.route('/payment-option',methods=['GET','POST'])
@login_required
def payment_option():
    if session.get('subs_pac_id'):
        if request.method == 'POST':
            payment_option_select = request.form.get('payment_option_select')
            if payment_option_select == 'online':
                return redirect(url_for('payment_online'))
            else:
                return redirect(url_for('payment_offline'))
        else:
            return render_template('home/payment-option.html')
    else:
        return redirect(url_for('packages'))



""" Online Payment process """
@app.route('/payment-online')
@login_required
def payment_online():
    pac_course = Pac_course.query.filter_by(id=session.get('subs_pac_id')).first_or_404()
    total_payable_amount = 0
    """ Get the pirce of compuslory subjects """
    comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=session.get('subs_pac_id')).all()
    for cps in comp_sub:
        total_payable_amount = total_payable_amount + cps.price
    

    """ Get the price of optional subjects  """
    for optional_sub in session.get('subs_optional_subjects'):
        optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
        total_payable_amount = total_payable_amount + optional_subject_info.price
    
    amount = int(total_payable_amount * len(session.get('subs_months')))

    """ Discount on total payment amount """
    dis_amount = 0
    if len(session.get('subs_optional_subjects'))==3:
        """for crash course"""
        if pac_course.is_crash_course:
            dis_amount = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
            amount = amount - dis_amount
        else:
            dis_amount = (amount * 10) / 100
            amount = amount - dis_amount
        
    elif len(session.get('subs_optional_subjects'))>3:
        """for crash course"""
        if pac_course.is_crash_course:
            dis_amount = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
            amount = amount - dis_amount
        else:
            dis_amount = (amount * 20) / 100
            amount = amount - dis_amount

    total_payable_amount = (amount+1)
    
    merchant_id = str(app.config['MERCHANT_ID'])
    api = str(app.config['API'] )
    invoice ='GEN'+str(current_user.id)+''+randomkey(6).upper()
    amount = str('%.2f' %float(total_payable_amount))
    payment_desc = 'Purchase_Course_Online'
    hashed_string = api+"|"+urllib.parse.quote(merchant_id)+"|"+urllib.parse.quote(invoice)+"|"+urllib.parse.quote(amount)+"|"+urllib.parse.quote(payment_desc)
    # hashcode_str = hashlib.md5(hashed_string.encode('utf-8'))
    
    return render_template('payment/process-form.html',hashed_string=hashed_string, merchant_id=merchant_id,invoice=invoice,amount=amount,payment_desc=payment_desc)


@app.route('/callbackv1', methods=['POST'])
@csrf.exempt
@login_required
def payment_online_callback():


    pac_course = Pac_course.query.filter_by(id=session.get('subs_pac_id')).first_or_404()
    total_payable_amount = 0
    """ Get the pirce of compuslory subjects """
    comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=session.get('subs_pac_id')).all()
    for cps in comp_sub:
        total_payable_amount = total_payable_amount + cps.price
        
    """ Get the price of optional subjects  """
    if session.get('subs_optional_subjects'):
        for optional_sub in session.get('subs_optional_subjects'):
            optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
            total_payable_amount = total_payable_amount + optional_subject_info.price

        amount = int(total_payable_amount * len(session.get('subs_months')))

    """ Discount on total payment amount """
    dis_amount = 0

    if session.get('subs_optional_subjects'):
        if len(session.get('subs_optional_subjects')) == 3:
            if pac_course.is_crash_course:
                dis_amount = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
                amount = amount - dis_amount
            else:
                dis_amount = (amount * 10) / 100
                amount = amount - dis_amount

        elif len(session.get('subs_optional_subjects')) > 3:
            if pac_course.is_crash_course:
                dis_amount = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
                amount = amount - dis_amount
            else:
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
            student_id = current_user.id,
            package_id=session.get('subs_pac_id'),
            total_amount=total_payable_amount*len(session.get('subs_months')),
            coupon_code=None,
            discount_amount=dis_amount,
            total_payable_amount=amount,
            transcation_id=trx_id,
            invoice=request.form.get('invoice_no'),
            receipt='',
            payment_status=bool(str('True')),
            payment_mode='online',
            subs_status=True,
            purpose=1 #new subscription code
            )
        db.session.add(subs_pac_info)
        db.session.commit()

        subscription_trans_log = Subscription_trans_log(student_id=current_user.id, package_id=session.get('subs_pac_id'), total_amount=total_payable_amount*len(session.get('subs_months')), coupon_code=None,discount_amount=dis_amount, total_payable_amount=amount,transcation_id=trx_id,invoice=request.form.get('invoice_no'),receipt='', payment_mode='online', purpose='Purchase new subscription.')
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
        # flash('Your payment is successfull.','success')
        return redirect(url_for('online_payment_success'))
    else:
        message = 'Sorry, your transaction is not completed Please contact with support team.'
        return render_template('home/info.html', message=message)

@app.route('/success')
def online_payment_success():
    return render_template('home/success.html')

@app.route('/payment-success')
def payment_success():
    return render_template('home/payment-success.html')

@app.route('/payment-fail',methods=['POST','GET'])
@csrf.exempt
def payment_fail():
    if request.method=='POST':
        """ Unset all session of payments """
        if session.get('subs_pac_id'):
            session.pop('subs_pac_id')
        if session.get('subs_optional_subjects'):
            session.pop('subs_optional_subjects')
        if session.get('subs_months'):
            session.pop('subs_months')
        return render_template('home/payment-fail.html')
    else:
        return render_template('home/payment-fail.html')

""" End of online payment process """


def randomkey(stringLength=10):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))

@app.route('/payment-offline',methods=['GET','POST'])
@login_required
def payment_offline():

    if session.get('subs_pac_id'):
        pac_course = Pac_course.query.filter_by(id=session.get('subs_pac_id')).first_or_404()
        if request.method=='POST':
            try:
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

                    amount = int(total_payable_amount*len(session.get('subs_months')))
                    # return str(amount)

                    """ Discount on total payment amount """
                    dis_amount=0
                    if len(session.get('subs_optional_subjects'))==3:
                        """for crash course"""
                        if pac_course.is_crash_course:
                            dis_amount = float(pac_course.discount_amt) * len(session.get('subs_optional_subjects'))
                            amount = amount - dis_amount
                        else:
                            dis_amount=(amount*10)/100
                            amount=amount-dis_amount
                    
                    elif len(session.get('subs_optional_subjects'))>3:
                        """for crash course"""
                        if pac_course.is_crash_course:
                            dis_amount = float(pac_course.discount_amt) * len(session.get('subs_optional_subjects'))
                            amount = amount - dis_amount
                        else:
                            dis_amount=(amount*20)/100
                            amount=amount-dis_amount
                    

                    # exists_pac_info = Student_package_subscription.query.filter_by( student_id=current_user.id,package_id=session.get('subs_pac_id')).first()
                    #
                    # if exists_pac_info:
                    #
                    #     """ Unset all session of payments """
                    #     if session.get('subs_pac_id'):
                    #         session.pop('subs_pac_id')
                    #     if session.get('subs_optional_subjects'):
                    #         session.pop('subs_optional_subjects')
                    #     if session.get('subs_months'):
                    #         session.pop('subs_months')
                    #
                    #     message = 'You have already subscribed this package.'
                    #     return render_template('home/info.html',message=message)
                    #
                    # else:
                    """ Store the information of subscription to the db """
                    subs_pac_info=Student_package_subscription(
                            student_id=current_user.id,
                            package_id=session.get('subs_pac_id'),
                            total_amount=total_payable_amount*len(session.get('subs_months')),
                            coupon_code=None,
                            discount_amount=dis_amount,
                            total_payable_amount=amount,
                            transcation_id='',
                            invoice='',
                            receipt=receipt_file_path,
                            payment_status=bool(False),
                            payment_mode='offline',
                            subs_status=False,
                            purpose=1 #new subscription
                        )
                    db.session.add(subs_pac_info)
                    db.session.commit()

                    subscription_trans_log = Subscription_trans_log(student_id=current_user.id, package_id=session.get('subs_pac_id'), total_amount=total_payable_amount*len(session.get('subs_months')), coupon_code=None,discount_amount=dis_amount, total_payable_amount=amount,transcation_id='',invoice='', receipt=receipt_file_path, payment_mode='online', purpose='Purchase new subscription.')
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
    
                    return redirect(url_for('payment_success'))
                else:
                    return redirect(url_for('package'))
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

                amount = int(total_payable_amount*len(session.get('subs_months')))
                """ Discount on total payment amount """
                dis_amount=0
                if len(session.get('subs_optional_subjects'))==3:
                    """ for crash course """
                    if pac_course.is_crash_course:
                        dis_amount = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
                        amount = amount - dis_amount
                    else:
                        dis_amount=(amount*10)/100
                        amount=amount-dis_amount
                
                elif len(session.get('subs_optional_subjects'))>3:
                    """for crash course"""
                    if pac_course.is_crash_course:
                        dis_amount = pac_course.discount_amt * len(session.get('subs_optional_subjects'))
                        amount = amount - dis_amount
                    else:
                        dis_amount=(amount*20)/100
                        amount=amount-dis_amount

                return render_template('home/payment-offline.html',payamount=amount+1)
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
    else:
        return redirect(url_for('packages'))



""" Seminar """
@app.route('/seminar')
def geniuse_seminar():
    try:
        seminars = Seminars.query.filter_by(is_active=True).order_by(Seminars.id.desc()).all()
        resp = make_response(render_template('seminar/index.html', seminars=seminars))
        return resp
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/seminar/<string:cano_url>', methods=['POST', 'GET'])
def seminar_topics_list(cano_url):
    try:
        seminar = Seminars.query.filter_by(canonical_url=cano_url, is_active=True).first()
        if seminar:
            seminar_topic_details = Seminar_details.query.filter_by(seminar_id=seminar.id).all()
            return render_template('seminar/seminar-topic.html', seminar=seminar, seminar_topic_details=seminar_topic_details)
        else:
            return redirect('/404')
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/join-seminar/<cano_url>')
@login_required
def join_seminar(cano_url):
    try:
        seminar = Seminars.query.filter_by(canonical_url=cano_url, is_active=True).first()
        if seminar:
            joined_sem = Seminar_attend.query.filter_by(seminar_id=seminar.id, student_id=current_user.id).first()
            if not joined_sem:
                if seminar.price==0:
                    attend_sem = Seminar_attend(seminar_id=seminar.id, student_id=current_user.id, is_free=True,price=0)
                    db.session.add(attend_sem)
                    db.session.commit()
                    db.session.close()
                    flash('You have join seminar ({}) successfully'.format(seminar.title), 'success')
                    return redirect(url_for('dashboard'))
                else:
                    session['purchased_sem_id'] = seminar.id
                    return redirect(url_for('seminar_payment_option'))
            else:
                flash('You have already joined the seminar ({})'.format(seminar.title), 'danger')
                return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('seminar_topics_list', cano_url=cano_url))
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


""" Choose payment option for seminar """
@app.route('/seminar/payment/option', methods=['GET', 'POST'])
@login_required
def seminar_payment_option():
    if session.get('purchased_sem_id'):
        if request.method == 'POST':
            payment_option = request.form.get('payment_option_select')
            if payment_option == 'online':
                return redirect(url_for('seminar_online_payment_process'))
            else:
                return redirect(url_for('seminar_offline_payment_process'))
        else:
            return render_template('seminar/payment-option.html')
    else:
        return redirect(url_for('/'))


@app.route('/seminar/payment/offline', methods=['GET', 'POST'])
@login_required
@student_required
def seminar_offline_payment_process():
    if session.get('purchased_sem_id'):
        if request.method == 'POST':
            seminar = Seminars.query.filter_by(id=session.get('purchased_sem_id')).first()
            if seminar:

                if seminar.price > 0:
                    attend_sem = Seminar_attend(seminar_id=seminar.id, student_id=current_user.id, is_free=False,price=seminar.price)
                    db.session.add(attend_sem)
                    db.session.commit()
                    
                    payment_receipt = request.files['payment_receipt']
                    filename = secure_filename(payment_receipt.filename)
                    filetype, extension = splitext(filename)
                    newfilename = str(randomkey(10)).lower() + extension
                    payment_receipt.save(os.path.join(RECEIPT_UPLOAD_CONTENTS, newfilename))

                    attend_sem_status = Seminar_attend.query.filter_by(id=attend_sem.id,student_id=current_user.id).first()

                    attend_sem_status.payment_method = 'offline'
                    attend_sem_status.receipt = '/static/upload/receipt/' + newfilename
                    db.session.commit()
                    db.session.close()
                    session.pop('purchased_sem_id')
                    flash('Seminar is successfully subscribed.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    return redirect('/')

            else:
                message = "Oops! Seminar details are not valid. Please contact with support team."
                return render_template('seminar/info.html', message=message)
        else:
            try:
                seminar = Seminars.query.filter_by(id=session.get('purchased_sem_id')).first()
                if seminar:
                    return render_template('seminar/payment-offline.html', pur_seminar=seminar)
                else:
                    message = "Oops! something went wrong. Please contact with support team."
                    return render_template('seminar/info.html', message=message)
            except Exception as e:
                app.logger.error(str(e))
                return abort('500')
    else:
        return redirect(url_for('/'))


@app.route('/seminar/payment/online')
@login_required
def seminar_online_payment_process():
    if session.get('purchased_sem_id'):
        try:
            seminar = Seminars.query.filter_by(id=session.get('purchased_sem_id')).first()
        except Exception as e:
            app.logger.error(str(e))
            return abort('500')
        if seminar:
            merchant_id = str(app.config['MERCHANT_ID'])
            api = str(app.config['API'])
            invoice = 'GES' + str(current_user.id) + '' + randomkey(6).upper()
            amount = str('%.2f' % float(seminar.price))
            payment_desc = 'Purchase_Seminar_Online'
            hashed_string = api + "|" + urllib.parse.quote(merchant_id) + "|" + urllib.parse.quote(
                invoice) + "|" + urllib.parse.quote(amount) + "|" + urllib.parse.quote(payment_desc)
            return render_template('seminar/payment-online.html', merchant_id=merchant_id, api=api, invoice=invoice,
                                   amount=amount, payment_desc=payment_desc, hashed_string=hashed_string)
        else:
            message = "Oops! something went wrong. Please try after some time."
            return render_template('seminar/info.html', message=message)
    else:
        return redirect(url_for('/'))

@app.route('/semcallbackv1', methods=['POST'])
@csrf.exempt
def seminar_payment_online_callback():

    seminar = Seminars.query.filter_by(id=session.get('purchased_sem_id')).first()
    if seminar:

        trx_id = ''
        if request.form.get('pay_method') == 'fpx':
            trx_id = request.form.get('fpx_fpxTxnId')
        elif request.form.get('pay_method') == 'paypal':
            trx_id = request.form.get('paypal_trx_id')
        elif request.form.get('pay_method') == 'mastercard':
            trx_id = request.form.get('mastercard_trx_id')
        elif request.form.get('pay_method') == 'others':
            trx_id = request.form.get['others_trx_id']
            # $_REQUEST['pay_method'] = $_REQUEST['trx_txt']; #EX: Boost eWallet and etc

        try:
            attend_sem = Seminar_attend(seminar_id=seminar.id, student_id=current_user.id, is_free=False,price=seminar.price)
            db.session.add(attend_sem)
            db.session.commit()
            seminar_attend_status = Seminar_attend.query.filter_by(id=attend_sem.id).first()
            if seminar_attend_status:
                seminar_attend_status.payment_method = 'online'
                seminar_attend_status.invoice = invoice=request.form.get('invoice_no'),
                seminar_attend_status.transcation_id = trx_id
                seminar_attend_status.payment_status = True
                seminar_attend_status.is_approved = True
                db.session.commit()
                db.session.close()
            flash('Seminar is successfully subscribed.', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(str(e))
            return abort('500')
    else:
        message = "Oops! Seminar details are not valid. Please contact with support team."
        return render_template('seminar/info.html', message=message)


""" For seo purpose """
@app.route('/lower-secondary-online-classes')
def lower_sec_online_classes():
    return render_template('home/lower-secondary-online-classes.html')

@app.route('/primary-school-english-classes')
def primary_school_english_classes():
    return render_template('home/primary-school-english-classes.html')

@app.route('/upper-secondary-online-classes')
def upper_secondary_online_classes():
    return render_template('home/upper-secondary-online-classes.html')

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

#seminar expert-panel
#@app.route('/')