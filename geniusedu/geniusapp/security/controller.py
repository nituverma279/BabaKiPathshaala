from geniusapp import app, login_manager, db, logging
from flask import Flask, render_template, request, url_for, flash, session, make_response, redirect, abort
from geniusapp.model.tables import User_roles, Users, School_details, Referral_program,User_details
from flask_login import login_user, current_user, login_required, logout_user
from geniusapp.security.form import LoginForm, RegistrationForm, ForgetPasswordForm, ResetPasswordForm
from werkzeug.security import generate_password_hash
import random
import string
from geniusapp.helper.MailController import send_email
from urllib.parse import urlparse
import requests


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get((int(user_id)))

@app.route('/nitu')
def nitu():
	return render_template('New/nitu.html')


@app.route('/get-geo')
def get_geo_details():
    ip = request.remote_addr
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    response = requests.get('http://api.ipstack.com/' + ip + '?access_key=09bdbe0cbeb36ddde57ff7f16bd5499c')
    return response.json()


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate() == False:
            resp = make_response(render_template('security/login.html', form=form))
            return resp
        else:
            mobile = request.form.get('mobile')
            password = request.form.get('password')
            try:
                user = User_details.query.filter_by(mobile=mobile).first()
                if user and user.check_password(request.form['password']):
                    login_user(user)
                    # if session.get('subs_pac_id'):
                    #     return redirect(url_for('payment_process'))
                    # else:
                    next_page = request.args.get('next')
                    if not next_page or urlparse(next_page).netloc != '':
                        next_page = make_response(redirect(url_for('dashboard')))
                        return next_page
                    else:
                        return redirect(next_page)
                else:
                    flash(u"You have enter wrong mobile or passsord", "danger")
                    resp = make_response(redirect(url_for('login')))
                    return resp
            except Exception as e:
                return abort(500)
    else:
        try:
            form = LoginForm(request.form)
            resp = make_response(render_template('security/login.html', form=form))
            return resp
        except Exception as e:
            app.logger.error('Error: %s' % (str(e)))
            return abort(500)


@app.route('/register/<string:referral_code>', methods=['POST', 'GET'])
@app.route('/register', methods=['POST', 'GET'])
def register(referral_code=None):
    
    if request.method == 'POST':
        
        form = RegistrationForm(request.form)
        if form.validate() == True:
            resp = make_response(render_template('security/register.html', form=form))
            return resp
        else:
            

            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            
            email = request.form.get('email')
            mobile = request.form.get('mobile')
           
            password = request.form.get('password')
           
            # user = User_details(first_name=first_name, last_name=last_name,  email=email ,mobile=mobile,password=password)
            # db.session.add(user)
            # db.session.commit()
        
            try:
                user = User_details.query.filter_by(mobile=mobile).first()
                if user:
                   
                    flash(f'Sorry mobile {mobile} number is registered already. Please try with another number.', 'danger')
                    resp = make_response(render_template('security/register.html', form=form))
                    return resp
                else:
                   
                    user = User_details(first_name=first_name, last_name=last_name,  email=email, mobile=mobile,password=password)
                    db.session.add(user)
                    db.session.commit()
                    flash(f'Registration Successfully.', 'success')
                    resp = make_response(render_template('security/register.html', form=form))
                    return resp

                   
            except Exception as e:
                app.logger.error('Error: %s' % (str(e)))
                return abort(500)
    else:
        try:
            form = RegistrationForm()
            resp = make_response(render_template('security/register.html', form=form))
            return resp
        except Exception as e:
            app.logger.error('Error: {}'.format(str(e)))
            return abort(500)


@app.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        form = ForgetPasswordForm(request.form)

        if form.validate() == False:
            resp = make_response(render_template('security/forget-password.html', form=form))
            return resp
        else:
            email = request.form.get('email')
            try:
                users = Users.query.filter_by(email=email).first()
                if users:
                    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))
                    users.forget_password_key = random_string
                    db.session.commit()
                    subject = 'Reset Your Password'
                    html_content = '<h3>You can reset your password by following this link</h3><br/><a href="https://www.geniusedu.my/reset-password/{}">Reset password</a>'.format(
                        random_string)
                    message = html_content
                    receipent_email = [users.email]
                    send_email(subject, message, receipent_email)

                    flash('Success! You have received an email for password reset.', 'success')
                    return redirect(url_for('forget_password'))
                else:
                    flash('Sorry no user is registerd with {}'.format(email), 'danger')
                    return redirect(url_for('forget_password'))
            except Exception as e:
                app.logger.error(str(e))
                return abort(500)
    else:
        form = ForgetPasswordForm()
        resp = make_response(render_template('security/forget-password.html', form=form))
        return resp


@app.route('/reset-password/<string:forget_password_key>', methods=['GET', 'POST'])
def reset_password(forget_password_key):
    if request.method == 'POST':
        form = ResetPasswordForm(request.form)

        if form.validate() == False:
            return render_template('security/reset-password.html', form=form)
        else:
            password = request.form.get('password')
            user = Users.query.filter_by(forget_password_key=forget_password_key).first()
            if user:
                user.password = generate_password_hash(password)
                user.forget_password_key = None
                db.session.commit()
                flash('Your password is updated successfully.', 'success')
                return redirect(url_for('login'))
            else:
                message = "Oops! something went wrong. Please contact with support team."
                return render_template('security/info.html', message=message)
    try:
        user = Users.query.filter_by(forget_password_key=forget_password_key).first()
        if user:
            form = ResetPasswordForm()
            return render_template('security/reset-password.html', form=form)
        else:
            message = "Your link is not valid for updated password or expired. Please try again."
            return render_template('security/info.html', message=message)
    except Exception as e:
        app.logger.error(str(e))
        return abort(500)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are succesfully logout.', 'success')
    resp = make_response(redirect(url_for('login')))
    return resp
