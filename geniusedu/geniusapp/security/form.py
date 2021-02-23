from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, PasswordField,RadioField, BooleanField, SubmitField,TextField,TextAreaField,SelectField,IntegerField
from wtforms.validators import DataRequired, InputRequired,EqualTo,Email,length

class TelephoneForm(FlaskForm):
    country_code = IntegerField('Country Code', [InputRequired()])
    area_code    = IntegerField('Area Code/Exchange', [InputRequired()])
    number       = StringField('Number')

class RegistrationForm(FlaskForm):
    name = TextField('Name', [InputRequired('Name is required'),length(max=30)])
    email = TextField('Email', [InputRequired('Email is required'),Email()])
    mobile = IntegerField('Mobile', [InputRequired('Please enter your mobile number')]) 
    password = PasswordField('Password', [InputRequired('Password is required.'), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', [InputRequired('Confirm password is required.')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    #mobile = StringField('Hand Phone', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    # recaptcha = RecaptchaField()

class ForgetPasswordForm(FlaskForm):
    email = TextField('Email', [InputRequired(), Email()])
    submit = SubmitField('submit')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', [InputRequired()])
    submit = SubmitField('Update Password')

# class User_details(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(150), nullable=False)
#     last_name = db.Column(db.String(150),nullable=True)
#     email = db.Column(db.String(150),nullable=True)
#     mobile = db.Column(db.String(100),nullable=False) 
#     password = db.Column(db.String(250),nullable=False)
#     is_active = db.Column(db.Boolean, default=True)
    

#     def _init_(self, first_name, last_name, email,mobile, password):
#         self.first_name = first_name.title()
#         self.last_name = last_name.title()
#         self.email  = email.lower()
#         self.mobile=mobile
#         self.password = generate_password_hash(password)
