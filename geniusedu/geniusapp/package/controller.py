from geniusapp import app, db, csrf, config, login_manager
from flask import current_app, render_template, url_for, abort, request, make_response, flash, redirect, jsonify, \
    session, json, send_from_directory
from geniusapp.home.form import ContactForm
from geniusapp.model.tables import Contact_us, Online_demo_classes, Pac_course, Pac_compulsory_subjects, \
    Subjects, Courses, Pac_optional_subjects, Coupon, Student_package_subscription, Student_subs_pac_months, \
    Student_subs_pac_optional, Months, Subscription_trans_log, Seminars, Seminar_details, Seminar_attend, \
    Referral_program, \
    Wallet, Wallet_trans_log
from _ast import Param
import datetime
import stripe
from flask_login import login_user, current_user, login_required
from functools import wraps
import random
import string
from werkzeug.utils import secure_filename
import os
from os.path import splitext
import hashlib
import urllib.parse
from geniusapp.home.controller import package_months, randomkey, student_required
from geniusapp.helper.ReferralController import referral_program, wallet_info, update_wallet

basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECEIPT_UPLOAD_CONTENTS = basedir + '/static/upload/receipt/'


@app.route('/test-wallet')
@login_required
def test_wallet():
    status = referral_program(500)
    return status


@app.route('/package/purchase/<string:cano_url>', methods=['GET', 'POST'])
def spec_purchase_package(cano_url):
    if request.method == 'POST':
        pcgd = request.form.get('pcgd')
        optional_subject = request.form.getlist('optional_subject')
        months = request.form.getlist('month')
        cano_url = request.form.get('cano')

        if session.get('spec_pac_id'):
            session.pop('spec_pac_id')
        if session.get('subs_optional_subjects'):
            session.pop('subs_optional_subjects')
        if session.get('subs_months'):
            session.pop('subs_months')
        if len(months) < 1:
            return redirect(url_for('spec_purchase_package', cano_url=cano_url))
        else:
            subs_month = []
            subs_opt_subjs = []

            for month in months:
                subs_month.append(month)

            for opt_sub in optional_subject:
                subs_opt_subjs.append(opt_sub)

            session['spec_pac_id'] = pcgd
            session['subs_optional_subjects'] = subs_opt_subjs  # subscribe_course_package
            session['subs_months'] = subs_month
            return redirect(url_for('spec_package_summery'))
    else:
        try:
            course_package = Pac_course.query.filter_by(cano_url=cano_url, is_active=True).first()
            if course_package:
                months = package_months(course_package.expire_month)
                comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=course_package.id).all()
                opt_sub = Pac_optional_subjects.query.filter_by(pac_course_id=course_package.id).all()
                total_comp_sub_price = 0
                if comp_sub:
                    for cps in comp_sub:
                        total_comp_sub_price = total_comp_sub_price + cps.price
                resp = make_response(
                    render_template('package/purchase-package.html', course_package=course_package, comp_sub=comp_sub,
                                    opt_sub=opt_sub, total_comp_sub_price=total_comp_sub_price, months=months))
                return resp
            else:
                redirect(url_for('packages'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


@app.route('/package/summery')
@login_required
def spec_package_summery():
    if session.get('spec_pac_id'):
        exists_pac_info = Student_package_subscription.query.filter_by(student_id=current_user.id,
                                                                       package_id=session.get('spec_pac_id')).first()
        if exists_pac_info:
            """ Unset all session of payments """
            if session.get('spec_pac_id'):
                session.pop('spec_pac_id')
            if session.get('subs_optional_subjects'):
                session.pop('subs_optional_subjects')
            if session.get('subs_months'):
                session.pop('subs_months')

            message = 'You have already subscribed this package.'
            return render_template('home/info.html', message=message)
        else:
            if current_user.online_register == True:
                try:
                    pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
                    if pac_course:
                        total_payable_amount = 0
                        current_month = datetime.datetime.now().month
                        current_year = datetime.datetime.now().year

                        """ Check that current month and year is not expired """
                        if pac_course.expire_month >= current_month and pac_course.expire_year >= current_year:
                            comp_subject_details = []
                            optional_subject_details = []
                            subs_months_details = []
                            """ Get the price of compulsory subjects """
                            comp_sub = Pac_compulsory_subjects.query.filter_by(
                                pac_course_id=session.get('spec_pac_id')).all()
                            if comp_sub:
                                for cps in comp_sub:
                                    total_payable_amount = total_payable_amount + cps.price
                                    comp_subject_details.append({'subject_name': cps.subject_name, 'price': cps.price})

                            """ Get the price of optional subjects  """
                            if len(session.get('subs_optional_subjects')) > 0:

                                for optional_sub in session.get('subs_optional_subjects'):
                                    optional_subject_info = Pac_optional_subjects.query.filter_by(
                                        id=optional_sub).first()

                                    optional_subject_details.append({'subject_name': optional_subject_info.subject_name,
                                                                     'price': optional_subject_info.price})
                                    total_payable_amount = total_payable_amount + optional_subject_info.price

                            if len(session.get('subs_months')) > 0:
                                for month in session.get('subs_months'):
                                    sub_month = Months.query.filter_by(id=month).first()
                                    subs_months_details.append({'month_name': sub_month.month_name})

                            total_payable_amount = pac_course.price * len(session.get('subs_months'))
                            subtotal = total_payable_amount

                            """ Discount on total payment amount """
                            discount_amt = 0

                            """ if wallet has amount """
                            wt_info = wallet_info(current_user.id).get_json()
                            if wt_info['error'] == 0:
                                wt_amt = wt_info['amount']
                            return render_template('package/payment-summery.html',
                                                   subtotal=subtotal,
                                                   discount_amt=discount_amt,
                                                   subs_months_details=subs_months_details,
                                                   comp_subject_details=comp_subject_details,
                                                   optional_subject_details=optional_subject_details,
                                                   total_payable_amount=total_payable_amount,
                                                   wt_amt=wt_amt
                                                   )
                        else:
                            return 'Package is expired'
                except Exception as e:
                    app.logger.error(str(e))
                    return abort(500)
            else:
                """ Unset all session of payments """
                if session.get('spec_pac_id'):
                    session.pop('spec_pac_id')
                if session.get('subs_optional_subjects'):
                    session.pop('subs_optional_subjects')
                if session.get('subs_months'):
                    session.pop('subs_months')

                message = 'Sorry, Genius Arena Tuition student cannot purchase this package. <br/> Please contact support for more information.'
                return render_template('home/info.html', message=message)
    else:
        return redirect(url_for('packages'))


@app.route('/package/payment-option', methods=['GET', 'POST'])
@login_required
def spec_payment_option():
    if session.get('spec_pac_id'):
        if request.method == 'POST':
            payment_option_select = request.form.get('payment_option_select')
            is_use_wallet = request.form.get('is_use_wallet')
            if is_use_wallet:
                session['is_use_wallet'] = is_use_wallet

            if payment_option_select == 'online':
                return redirect(url_for('spec_payment_online'))
            else:
                return redirect(url_for('spec_payment_offline'))
        else:
            try:
                wallet = Wallet.query.filter_by(user_id=current_user.id).first()
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)

            if wallet and  wallet.amount > 0:
                return render_template('package/payment-option.html', wallet=wallet)
            else:
                return render_template('package/payment-option.html')
    else:
        return redirect(url_for('packages'))


@app.route('/package/payment-offline', methods=['GET', 'POST'])
@login_required
def spec_payment_offline():
    if session.get('spec_pac_id'):
        if request.method == 'POST':
            try:
                pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
                if pac_course:
                    payment_receipt = request.files['payment_receipt']
                    filename = secure_filename(payment_receipt.filename)
                    filetype, extension = splitext(filename)
                    newfilename = str(randomkey(10)).lower() + extension
                    payment_receipt.save(os.path.join(RECEIPT_UPLOAD_CONTENTS, newfilename))
                    receipt_file_path = '/static/upload/receipt/' + newfilename

                    """ Upload payment receipt """
                    total_amount = (pac_course.price * len(session.get('subs_months')) + 1)  # 1 for notes
                    total_payable_amount = (pac_course.price * len(session.get('subs_months')) + 1)  # 1 for notes
                    """ Discount on total payment amount """
                    dis_amount = 0
                    exists_pac_info = Student_package_subscription.query.filter_by(student_id=current_user.id,
                                                                                   package_id=session.get(
                                                                                       'spec_pac_id')).first()
                    if exists_pac_info:
                        """ Unset all session of payments """
                        if session.get('spec_pac_id'):
                            session.pop('spec_pac_id')
                        if session.get('subs_optional_subjects'):
                            session.pop('subs_optional_subjects')
                        if session.get('subs_months'):
                            session.pop('subs_months')

                        message = 'You have already subscribed this package.'
                        return render_template('home/info.html', message=message)

                    else:
                        payment_mode = 'offline'
                        """ use wallet """
                        if session.get('is_use_wallet'):
                            wt_info = wallet_info(current_user.id).get_json()
                            if wt_info['error'] == 0:
                                wt_amt = wt_info['amount']
                                total_payable_amount = total_payable_amount - wt_amt
                                payment_mode = 'walletinc'

                        """ Store the information of subscription to the db """
                        subs_pac_info = Student_package_subscription(
                            student_id=current_user.id,
                            package_id=session.get('spec_pac_id'),
                            total_amount=total_amount,
                            coupon_code=None,
                            discount_amount=dis_amount,
                            total_payable_amount=total_payable_amount,
                            transcation_id='',
                            invoice='',
                            receipt=receipt_file_path,
                            payment_status=False,
                            payment_mode=payment_mode,
                            subs_status=False,
                            purpose=1  # new subscription
                        )
                        db.session.add(subs_pac_info)
                        db.session.commit()

                        subscription_trans_log = Subscription_trans_log(student_id=current_user.id,
                                                                        package_id=session.get('spec_pac_id'),
                                                                        total_amount=total_amount,
                                                                        coupon_code=None,
                                                                        discount_amount=dis_amount,
                                                                        total_payable_amount=total_payable_amount,
                                                                        transcation_id='', invoice='',
                                                                        receipt=receipt_file_path,
                                                                        payment_mode=payment_mode,
                                                                        purpose='Purchase new subscription.')
                        db.session.add(subscription_trans_log)
                        db.session.commit()

                        """Set referral program"""
                        referral_program(current_user.id, total_payable_amount,
                                         f'Amount affected during purchasing of package {pac_course.cano_url} by {current_user.first_name} has id {subs_pac_info.id}')

                        """ Add subscriptions month and optional subjects """
                        if len(session.get('subs_optional_subjects')) > 0:
                            for optional_sub in session.get('subs_optional_subjects'):
                                subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,
                                                                                   optional_subs=optional_sub)
                                db.session.add(subs_optional_sub_info)
                                db.session.commit()

                        if len(session.get('subs_months')) > 0:
                            for month in session.get('subs_months'):
                                student_subs_month = Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id,
                                                                             subs_month=month)
                                db.session.add(student_subs_month)
                                db.session.commit()
                        db.session.close()

                        """ Update wallet account """
                        if session.get('is_use_wallet'):
                            wt_info = wallet_info(current_user.id).get_json()
                            if wt_info['error'] == False:
                                wt_amt = wt_info['amount']
                                if wt_amt > 0:
                                    update_wallet(current_user.id, wt_amt,
                                                           'Purchase new package has package id {} using wallet account.'.format(
                                                               session.get('spec_pac_id')))


                        """ Unset all session of payments """
                        if session.get('is_use_wallet'):
                            session.pop('is_use_wallet')
                        if session.get('spec_pac_id'):
                            session.pop('spec_pac_id')
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
                pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
                amount = pac_course.price * len(session.get('subs_months')) + 1  # 1 for notes

                """ use wallet """
                if session.get('is_use_wallet'):
                    wt_info = wallet_info(current_user.id).get_json()
                    if wt_info['error'] == 0:
                        wt_amt = wt_info['amount']
                        if wt_amt >= amount:
                            return redirect(url_for('pac_subs_cou_wt'))
                        else:
                            amount = amount - wt_amt
                return render_template('package/payment-offline.html', payamount=amount)
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
    else:
        return redirect(url_for('packages'))


@app.route('/package/payment-online')
@login_required
def spec_payment_online():
    if session.get('spec_pac_id'):
        pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
        if pac_course:
            total_payable_amount = pac_course.price * len(session.get('subs_months')) + 1  # 1 for notes
            """ use wallet """
            if session.get('is_use_wallet'):
                wt_info = wallet_info(current_user.id).get_json()
                if wt_info['error'] == 0:
                    wt_amt = wt_info['amount']
                    if wt_amt >= total_payable_amount:
                        return redirect(url_for('pac_subs_cou_wt'))
                    else:
                        total_payable_amount = total_payable_amount - wt_amt

            merchant_id = str(app.config['MERCHANT_ID'])
            api = str(app.config['API'])
            invoice = 'GEN' + str(current_user.id) + '' + randomkey(6).upper()
            amount = str('%.2f' % float(total_payable_amount))
            payment_desc = 'Purchase_Course_Online'
            hashed_string = api + "|" + urllib.parse.quote(merchant_id) + "|" + urllib.parse.quote(
                invoice) + "|" + urllib.parse.quote(amount) + "|" + urllib.parse.quote(payment_desc)
            return render_template('package/payment-online.html', hashed_string=hashed_string, merchant_id=merchant_id,
                                   invoice=invoice, amount=amount, payment_desc=payment_desc)
        else:
            message = 'Package details are not correct'
            return render_template('home/info.html', message=message)
    else:
        return redirect(url_for('packages'))


""" if wallet has more amount than package amount """


@app.route('/package/subscribe/course/wallet')
@login_required
@student_required
def pac_subs_cou_wt():
    try:
        pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id'), is_active=True).first()
        if pac_course:
            total_payable_amount = pac_course.price * len(session.get('subs_months')) + 1
            subs_pac_info = Student_package_subscription(
                student_id=current_user.id,
                package_id=session.get('spec_pac_id'),
                total_amount=total_payable_amount,
                coupon_code=None,
                discount_amount=0,
                total_payable_amount=total_payable_amount,
                transcation_id='',
                invoice='',
                receipt='',
                payment_status=bool(str('True')),
                payment_mode='wallet',
                subs_status=True,
                purpose=1  # new subscription code
            )
            db.session.add(subs_pac_info)
            db.session.commit()
            subscription_trans_log = Subscription_trans_log(student_id=current_user.id,
                                                            package_id=session.get('spec_pac_id'),
                                                            total_amount=total_payable_amount,
                                                            coupon_code=None,
                                                            discount_amount=0,
                                                            total_payable_amount=total_payable_amount,
                                                            transcation_id='',
                                                            invoice='',
                                                            receipt='',
                                                            payment_mode='wallet',
                                                            purpose='Purchase new subscription.')
            db.session.add(subscription_trans_log)
            db.session.commit()
            if len(session.get('subs_optional_subjects')) > 0:
                for optional_sub in session.get('subs_optional_subjects'):
                    subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,
                                                                       optional_subs=optional_sub)
                    db.session.add(subs_optional_sub_info)
                    db.session.commit()
            if len(session.get('subs_months')) > 0:
                for month in session.get('subs_months'):
                    student_subs_month = Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id, subs_month=month)
                    db.session.add(student_subs_month)
                    db.session.commit()
            db.session.close()

            """ Update wallet account """
            if session.get('is_use_wallet'):
                wt_info = wallet_info(current_user.id).get_json()
                if wt_info['error'] == 0:
                    wt_amt = wt_info['amount']
                    if wt_amt > total_payable_amount:
                        update_wallet(current_user.id, total_payable_amount,
                                      'Purchase new package has package id {} using wallet account.'.format(
                                          session.get('spec_pac_id')))

            """ Unset all session of payments """
            if session.get('is_use_wallet'):
                session.pop('is_use_wallet')
            if session.get('spec_pac_id'):
                session.pop('spec_pac_id')
            if session.get('subs_optional_subjects'):
                session.pop('subs_optional_subjects')
            if session.get('subs_months'):
                session.pop('subs_months')
            return redirect(url_for('online_payment_success'))
        else:
            message = 'Sorry, Package is expired. Please contact with support team for more information.'
            return render_template('home/info.html', message=message)
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/package/callspecbackv1', methods=['POST'])
@csrf.exempt
def spec_payment_online_callback():
    try:
        pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
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
        total_amount = pac_course.price * len(session.get('subs_months')) + 1
        total_payable_amount = pac_course.price * len(session.get('subs_months')) + 1

        payment_mode = 'online'

        """ use wallet """
        if session.get('is_use_wallet'):
            wt_info = wallet_info(current_user.id).get_json()
            if wt_info['error'] == 0:
                wt_amt = wt_info['amount']
                total_payable_amount = total_payable_amount - wt_amt
                payment_mode = 'walletinc'

        if trx_id:
            """ Store the information of subscription to the db """
            subs_pac_info = Student_package_subscription(
                student_id=current_user.id,
                package_id=session.get('spec_pac_id'),
                total_amount=total_amount,
                coupon_code=None,
                discount_amount=0,
                total_payable_amount=total_payable_amount,
                transcation_id=trx_id,
                invoice=request.form.get('invoice_no'),
                receipt='',
                payment_status=bool(str('True')),
                payment_mode=payment_mode,
                subs_status=True,
                purpose=1  # new subscription code
            )
            db.session.add(subs_pac_info)
            db.session.commit()
            """Set referral program"""
            referral_program(current_user.id, total_payable_amount,
                             f'Amount affected during purchasing of package {pac_course.cano_url} by {current_user.first_name} has id {subs_pac_info.id}')

            subscription_trans_log = Subscription_trans_log(student_id=current_user.id,
                                                            package_id=session.get('spec_pac_id'),
                                                            total_amount=total_amount,
                                                            coupon_code=None,
                                                            discount_amount=0,
                                                            total_payable_amount=total_payable_amount,
                                                            transcation_id=trx_id,
                                                            invoice=request.form.get('invoice_no'),
                                                            receipt='',
                                                            payment_mode=payment_mode,
                                                            purpose='Purchase new subscription.')
            db.session.add(subscription_trans_log)
            db.session.commit()

            if len(session.get('subs_optional_subjects')) > 0:
                for optional_sub in session.get('subs_optional_subjects'):
                    subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,
                                                                       optional_subs=optional_sub)
                    db.session.add(subs_optional_sub_info)
                    db.session.commit()

            if len(session.get('subs_months')) > 0:
                for month in session.get('subs_months'):
                    student_subs_month = Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id, subs_month=month)
                    db.session.add(student_subs_month)
                    db.session.commit()

            db.session.close()
            """ Update wallet account """
            if session.get('is_use_wallet'):
                wt_info = wallet_info(current_user.id).get_json()
                if wt_info['error'] == 0:
                    wt_amt = wt_info['amount']
                    if wt_amt > 0:
                        update_wallet(current_user.id, wt_amt,
                                      'Purchase new package has package id {} using wallet account.'.format(
                                          session.get('spec_pac_id')))
            """ Unset all session of payments """
            if session.get('is_user_wallet'):
                session.pop('is_user_wallet')
            if session.get('spec_pac_id'):
                session.pop('spec_pac_id')
            if session.get('subs_optional_subjects'):
                session.pop('subs_optional_subjects')
            if session.get('subs_months'):
                session.pop('subs_months')
            return redirect(url_for('online_payment_success'))
        else:
            message = 'Sorry, your transaction is not completed Please contact with support team.'
            return render_template('home/info.html', message=message)

    except Exception as e:
        app.logger.error(str(e))
        return abort('500')


""" Renew Subscriptions"""


@app.route('/package/renew/subscription/<int:id>/<int:subs_id>', methods=['GET', 'POST'])
@login_required
@student_required
def spec_renew_subscription(id, subs_id):
    if request.method == 'POST':
        pcgd = request.form.get('pcgd')
        optional_subject = request.form.getlist('optional_subject')
        months = request.form.getlist('month')

        if len(months) < 1:
            return redirect(url_for('renew_subscription', id=id))
        else:

            subs_month = []
            subs_opt_subjs = []

            for month in months:
                subs_month.append(month)

            for opt_sub in optional_subject:
                subs_opt_subjs.append(opt_sub)

            session['spec_pac_id'] = pcgd
            session['subs_optional_subjects'] = subs_opt_subjs  # subscribe_course_package
            session['subs_months'] = subs_month
            return redirect(url_for('spec_renew_payment_process'))
    else:
        try:
            course_package = Pac_course.query.filter_by(id=id, is_active=True).first()
            if course_package:

                """ Package information like expired month, optional subjects and compulsory subjects """
                months = package_months(course_package.expire_month)
                comp_sub = Pac_compulsory_subjects.query.filter_by(pac_course_id=course_package.id).all()
                opt_sub = Pac_optional_subjects.query.filter_by(pac_course_id=course_package.id).all()

                """ Student subscribed optional subject list  """
                stu_sub_opt_sub = Student_package_subscription.query.filter_by(id=subs_id, package_id=id,
                                                                               student_id=current_user.id).first()
                student_subs_pac_opt = Student_subs_pac_optional.query.filter_by(
                    stu_pac_subs_id=stu_sub_opt_sub.id).all()

                subscribed_optional_subjects = []
                if student_subs_pac_opt:
                    for stu_subs_pac_opt in student_subs_pac_opt:
                        subscribed_optional_subjects.append(stu_subs_pac_opt.optional_subs)

                """ Student subscribed Months list """
                stu_sub_pac_all = Student_package_subscription.query.filter_by(package_id=id,
                                                                               student_id=current_user.id).all()
                subscribed_optional_months = []
                if stu_sub_pac_all:
                    for stu_subscription in stu_sub_pac_all:
                        student_subs_pac_month = Student_subs_pac_months.query.filter_by(
                            stu_pac_subs_id=stu_subscription.id).all()
                        if student_subs_pac_month:
                            for stu_subs_pac_mon in student_subs_pac_month:
                                subscribed_optional_months.append(stu_subs_pac_mon.subs_month)
                total_comp_sub_price = course_package.price
                resp = make_response(render_template('package/renew/subscription-details.html',
                                                     subscribed_optional_subjects=subscribed_optional_subjects, \
                                                     course_package=course_package, comp_sub=comp_sub, opt_sub=opt_sub,
                                                     total_comp_sub_price=total_comp_sub_price, months=months, \
                                                     subscribed_optional_months=subscribed_optional_months))
                return resp
            else:
                return redirect(url_for('dashboard'))
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)


@app.route('/package/renew/payment/process')
@login_required
@student_required
def spec_renew_payment_process():
    if session.get('spec_pac_id'):
        if current_user.online_register == True:
            try:
                pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
                if pac_course:
                    total_payable_amount = 0
                    current_month = datetime.datetime.now().month
                    current_year = datetime.datetime.now().year

                    """ Check that current month and year is not expired """
                    if pac_course.expire_month >= current_month and pac_course.expire_year >= current_year:
                        comp_subject_details = []
                        optional_subject_details = []
                        subs_months_details = []

                        """ Get the pirce of compuslory subjects """
                        comp_sub = Pac_compulsory_subjects.query.filter_by(
                            pac_course_id=session.get('spec_pac_id')).all()
                        if comp_sub:
                            for cps in comp_sub:
                                total_payable_amount = total_payable_amount + cps.price
                                comp_subject_details.append({'subject_name': cps.subject_name, 'price': cps.price})

                        if len(session.get('subs_optional_subjects')) > 0:

                            for optional_sub in session.get('subs_optional_subjects'):
                                optional_subject_info = Pac_optional_subjects.query.filter_by(id=optional_sub).first()
                                # subject= Subjects.query.filter_by(id=optional_sub).first()
                                optional_subject_details.append({'subject_name': optional_subject_info.subject_name,
                                                                 'price': optional_subject_info.price})
                                total_payable_amount = total_payable_amount + optional_subject_info.price

                        if len(session.get('subs_months')) > 0:
                            for month in session.get('subs_months'):
                                sub_month = Months.query.filter_by(id=month).first()
                                subs_months_details.append({'month_name': sub_month.month_name})

                        total_payable_amount = float(pac_course.price * len(session.get('subs_months')))
                        subtotal = total_payable_amount

                        """ if wallet has amount """
                        wt_info = wallet_info(current_user.id).get_json()
                        if wt_info['error'] == 0:
                            wt_amt = wt_info['amount']

                        return render_template(
                            'package/renew/payment-summery.html',
                            subtotal=subtotal,
                            subs_months_details=subs_months_details,
                            comp_subject_details=comp_subject_details,
                            optional_subject_details=optional_subject_details,
                            total_payable_amount=total_payable_amount,
                            wt_amt=wt_amt
                        )
                    else:
                        return 'Package is expired'
                else:
                    message = 'Sorry, Package details are not correct.'
                    return render_template('home/info.html', message=message)
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
        else:
            """ Unset all session of payments """
            if session.get('spec_pac_id'):
                session.pop('spec_pac_id')
            if session.get('subs_optional_subjects'):
                session.pop('subs_optional_subjects')
            if session.get('subs_months'):
                session.pop('subs_months')
            message = 'Sorry, Genius Arena Tuition student cannot purchase this package. <br/> Please contact support for more information.'
            return render_template('home/info.html', message=message)
    else:
        return redirect(url_for('packages'))


@app.route('/package/renew/payment/option', methods=['GET', 'POST'])
def spec_renew_payment_option():
    if session.get('spec_pac_id'):
        if request.method == 'POST':
            payment_option_select = request.form.get('payment_option_select')
            is_use_wallet = request.form.get('is_use_wallet')
            if is_use_wallet:
                session['is_use_wallet'] = is_use_wallet
            if payment_option_select == 'online':
                return redirect(url_for('spec_renew_payment_online'))
            else:
                return redirect(url_for('spec_renew_payment_offline'))
        else:
            try:
                wallet = Wallet.query.filter_by(user_id=current_user.id).first()
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
            if wallet and wallet.amount > 0:
                return render_template('package/renew/payment-option.html', wallet=wallet)
            else:
                return render_template('package/renew/payment-option.html')
    else:
        return render_template('dashboard')


@app.route('/package/renew/payment/offline', methods=['GET', 'POST'])
@login_required
def spec_renew_payment_offline():
    if session.get('spec_pac_id'):
        if request.method == 'POST':
            try:
                pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
                if pac_course:
                    payment_receipt = request.files['payment_receipt']
                    filename = secure_filename(payment_receipt.filename)
                    filetype, extension = splitext(filename)
                    newfilename = str(randomkey(10)).lower() + extension
                    payment_receipt.save(os.path.join(RECEIPT_UPLOAD_CONTENTS, newfilename))
                    receipt_file_path = '/static/upload/receipt/' + newfilename

                    """ Upload payment receipt """
                    total_amt = int(pac_course.price * len(session.get('subs_months'))) + 1
                    total_payable_amount = int(pac_course.price * len(session.get('subs_months'))) + 1
                    payment_mode = 'offline'

                    """ use wallet """
                    if session.get('is_use_wallet'):
                        wt_info = wallet_info(current_user.id).get_json()
                        if wt_info['error'] == 0:
                            wt_amt = wt_info['amount']
                            total_payable_amount = total_payable_amount - wt_amt
                            payment_mode = 'walletinc'

                    """ Store the information of subscription to the db """
                    subs_pac_info = Student_package_subscription(
                        student_id=current_user.id,
                        package_id=session.get('spec_pac_id'),
                        total_amount=total_amt,
                        coupon_code=None,
                        discount_amount=0,
                        total_payable_amount=total_payable_amount,
                        transcation_id='',
                        invoice='',
                        receipt=receipt_file_path,
                        payment_status=True,
                        payment_mode=payment_mode,
                        subs_status=False,
                        purpose=2  # renewal subscription code
                    )
                    db.session.add(subs_pac_info)
                    db.session.commit()

                    subscription_trans_log = Subscription_trans_log(student_id=current_user.id,
                                                                    package_id=session.get('spec_pac_id'),
                                                                    total_amount=total_amt,
                                                                    coupon_code=None,
                                                                    discount_amount=0,
                                                                    total_payable_amount=total_payable_amount,
                                                                    transcation_id='',
                                                                    invoice='',
                                                                    receipt=receipt_file_path,
                                                                    payment_mode=payment_mode,
                                                                    purpose='Purchase new subscription.')
                    db.session.add(subscription_trans_log)
                    db.session.commit()

                    if len(session.get('subs_optional_subjects')) > 0:
                        for optional_sub in session.get('subs_optional_subjects'):
                            subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,
                                                                               optional_subs=optional_sub)
                            db.session.add(subs_optional_sub_info)
                            db.session.commit()

                    if len(session.get('subs_months')) > 0:
                        for month in session.get('subs_months'):
                            student_subs_month = Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id,
                                                                         subs_month=month)
                            db.session.add(student_subs_month)
                            db.session.commit()
                    db.session.close()

                    """ Update wallet account """
                    if session.get('is_use_wallet'):
                        wt_info = wallet_info(current_user.id).get_json()
                        if wt_info['error'] == 0:
                            wt_amt = wt_info['amount']
                            if wt_amt > 0:
                                update_wallet(current_user.id, wt_amt,
                                              'Update package has package id {} using wallet account.'.format(
                                                  session.get('spec_pac_id')))

                    """ Unset all session of payments """
                    if session.get('is_use_wallet'):
                        session.pop('is_use_wallet')
                    if session.get('spec_pac_id'):
                        session.pop('spec_pac_id')
                    if session.get('subs_optional_subjects'):
                        session.pop('subs_optional_subjects')
                    if session.get('subs_months'):
                        session.pop('subs_months')
                    flash('You have successfully renew subscription.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Package details are not valid. Please contact to support team.', 'danger')
                    return redirect(url_for('dashboard'))
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
        else:
            try:
                pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
                if pac_course:
                    amount = pac_course.price * len(session.get('subs_months')) + 1

                    """Use wallet"""
                    if session.get('is_use_wallet'):
                        wt_info = wallet_info(current_user.id).get_json()
                        if wt_info['error'] == 0:
                            wt_amt = wt_info['amount']
                            if wt_amt >= amount:
                                return redirect(url_for('pac_renew_cou_wt'))
                            else:
                                amount = amount - wt_amt
                    return render_template('package/renew/payment-offline.html', payamount=amount)
                else:
                    message = 'Sorry, Package details are not correct.'
                    return render_template('home/info.html', message=message)
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
    else:
        return redirect(url_for('dashboard'))


@app.route('/package/renew/payment/online')
@login_required
@student_required
def spec_renew_payment_online():
    if session.get('spec_pac_id'):
        try:
            pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
            if pac_course:
                total_payable_amount = pac_course.price

                """ use wallet """
                if session.get('is_use_wallet'):
                    wt_info = wallet_info(current_user.id).get_json()
                    if wt_info['error'] == 0:
                        wt_amt = wt_info['amount']
                        if wt_amt >= total_payable_amount:
                            return redirect(url_for('pac_renew_cou_wt'))
                        else:
                            total_payable_amount = total_payable_amount - wt_amt

                amount = total_payable_amount * len(session.get('subs_months')) + 1
                merchant_id = str(app.config['MERCHANT_ID'])
                api = str(app.config['API'])
                invoice = 'GEN' + str(current_user.id) + '' + randomkey(4).upper()
                amount = str('%.2f' % float(amount))
                payment_desc = 'Renew_package'
                hashed_string = api + "|" + urllib.parse.quote(merchant_id) + "|" + urllib.parse.quote(
                    invoice) + "|" + urllib.parse.quote(amount) + "|" + urllib.parse.quote(payment_desc)

                return render_template('package/renew/payment-online.html', hashed_string=hashed_string,
                                       merchant_id=merchant_id, invoice=invoice, amount=amount,
                                       payment_desc=payment_desc)
            else:
                message = 'Sorry, Package details are not correct.'
                return render_template('home/info.html', message=message)
        except Exception as e:
            app.logger.error(str(e))
            return abort(500)
    else:
        return redirect(url_for('dashboard'))


@app.route('/package/renew/callbackv2', methods=['POST', 'GET'])
@csrf.exempt
def spec_renew_callbackv2():
    if session.get('spec_pac_id'):
        try:
            pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id')).first()
            if pac_course:
                total_amt = pac_course.price * len(session.get('subs_months')) + 1
                total_payable_amount = pac_course.price * len(session.get('subs_months')) + 1
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
                if trx_id:
                    """ use wallet """
                    payment_mode = 'online'
                    if session.get('is_use_wallet'):
                        wt_info = wallet_info(current_user.id).get_json()
                        if wt_info['error'] == 0:
                            wt_amt = wt_info['amount']
                            total_payable_amount = total_payable_amount - wt_amt
                            payment_mode = 'walletinc'

                    """ Store the information of subscription to the db """

                    subs_pac_info = Student_package_subscription(
                        student_id=current_user.id,
                        package_id=session.get('spec_pac_id'),
                        total_amount=total_amt,
                        coupon_code=None,
                        discount_amount=0,
                        total_payable_amount=total_payable_amount,
                        transcation_id=trx_id,
                        invoice=request.form.get('invoice_no'),
                        receipt='',
                        payment_status=bool(str('True')),
                        payment_mode=payment_mode,
                        subs_status=True,
                        purpose=2
                    )
                    db.session.add(subs_pac_info)
                    db.session.commit()

                    subscription_trans_log = Subscription_trans_log(student_id=current_user.id,
                                                                    package_id=session.get('spec_pac_id'),
                                                                    total_amount=total_amt,
                                                                    coupon_code=None,
                                                                    discount_amount=0,
                                                                    total_payable_amount=total_payable_amount,
                                                                    transcation_id=trx_id,
                                                                    invoice=request.form.get('invoice_no'),
                                                                    receipt='',
                                                                    payment_mode=payment_mode,
                                                                    purpose='R')
                    db.session.add(subscription_trans_log)
                    db.session.commit()

                    if len(session.get('subs_optional_subjects')) > 0:
                        for optional_sub in session.get('subs_optional_subjects'):
                            subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,
                                                                               optional_subs=optional_sub)
                            db.session.add(subs_optional_sub_info)
                            db.session.commit()

                    if len(session.get('subs_months')) > 0:
                        for month in session.get('subs_months'):
                            student_subs_month = Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id,
                                                                         subs_month=month)
                            db.session.add(student_subs_month)
                            db.session.commit()
                    db.session.close()

                    """ Update wallet account """
                    if session.get('is_use_wallet'):
                        wt_info = wallet_info(current_user.id).get_json()
                        if wt_info['error'] == 0:
                            wt_amt = wt_info['amount']
                            if wt_amt > 0:
                                update_wallet(current_user.id, wt_amt,
                                              'Purchase new package has package id {} using wallet account.'.format(
                                                  session.get('spec_pac_id')))
                    """ Unset all session of payments """
                    if session.get('is_use_wallet'):
                        session.pop('is_use_wallet')
                    if session.get('spec_pac_id'):
                        session.pop('spec_pac_id')
                    if session.get('subs_optional_subjects'):
                        session.pop('subs_optional_subjects')
                    if session.get('subs_months'):
                        session.pop('subs_months')
                    flash('Your payment is successful. Your subscription is updated.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    message = 'Sorry, your transaction is not completed Please contact with support team.'
                    return render_template('home/info.html', message=message)
            else:
                message = 'Sorry, Package details are not correct.'
                return render_template('home/info.html', message=message)
        except Exception as e:
            app.logger.error(str(e))
            return abort('500')
    else:
        return redirect(url_for('dashboard'))


""" if wallet has enough amount to update package """


@app.route('/package/renew/course/wallet')
@login_required
@student_required
def pac_renew_cou_wt():
    try:
        pac_course = Pac_course.query.filter_by(id=session.get('spec_pac_id'), is_active=True).first()
        if pac_course:
            total_payable_amount = pac_course.price * len(session.get('subs_months')) + 1
            subs_pac_info = Student_package_subscription(
                student_id=current_user.id,
                package_id=session.get('spec_pac_id'),
                total_amount=total_payable_amount,
                coupon_code=None,
                discount_amount=0,
                total_payable_amount=total_payable_amount,
                transcation_id='',
                invoice='',
                receipt='',
                payment_status=bool(str('True')),
                payment_mode='wallet',
                subs_status=True,
                purpose=1  # new subscription code
            )
            db.session.add(subs_pac_info)
            db.session.commit()
            subscription_trans_log = Subscription_trans_log(student_id=current_user.id,
                                                            package_id=session.get('spec_pac_id'),
                                                            total_amount=total_payable_amount,
                                                            coupon_code=None,
                                                            discount_amount=0,
                                                            total_payable_amount=total_payable_amount,
                                                            transcation_id='',
                                                            invoice='',
                                                            receipt='',
                                                            payment_mode='wallet',
                                                            purpose='Purchase new subscription.')
            db.session.add(subscription_trans_log)
            db.session.commit()
            if len(session.get('subs_optional_subjects')) > 0:
                for optional_sub in session.get('subs_optional_subjects'):
                    subs_optional_sub_info = Student_subs_pac_optional(stu_pac_subs_id=subs_pac_info.id,
                                                                       optional_subs=optional_sub)
                    db.session.add(subs_optional_sub_info)
                    db.session.commit()
            if len(session.get('subs_months')) > 0:
                for month in session.get('subs_months'):
                    student_subs_month = Student_subs_pac_months(stu_pac_subs_id=subs_pac_info.id, subs_month=month)
                    db.session.add(student_subs_month)
                    db.session.commit()
            db.session.close()

            """ Update wallet account """
            if session.get('is_use_wallet'):
                wt_info = wallet_info(current_user.id).get_json()
                if wt_info['error'] == 0:
                    wt_amt = wt_info['amount']
                    if wt_amt > total_payable_amount:
                        update_wallet(current_user.id, total_payable_amount,
                                      'Renew package has package id {} using wallet account.'.format(
                                          session.get('spec_pac_id')))

            """ Unset all session of payments """
            if session.get('is_use_wallet'):
                session.pop('is_use_wallet')
            if session.get('spec_pac_id'):
                session.pop('spec_pac_id')
            if session.get('subs_optional_subjects'):
                session.pop('subs_optional_subjects')
            if session.get('subs_months'):
                session.pop('subs_months')
            return redirect(url_for('online_payment_success'))
        else:
            message = 'Sorry, Package is expired. Please contact with support team for more information.'
            return render_template('home/info.html', message=message)
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)
