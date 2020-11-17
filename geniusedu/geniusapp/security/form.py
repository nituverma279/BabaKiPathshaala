from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, PasswordField,RadioField, BooleanField, SubmitField,TextField,TextAreaField,SelectField,IntegerField
from wtforms.validators import DataRequired, InputRequired,EqualTo,Email,length

class TelephoneForm(FlaskForm):
    country_code = IntegerField('Country Code', [InputRequired()])
    area_code    = IntegerField('Area Code/Exchange', [InputRequired()])
    number       = StringField('Number')

class RegistrationForm(FlaskForm):
    user_type=RadioField('You are ',[InputRequired('Please select one user type')], choices=[('stu', 'Student'),('prof','Professional')])
    first_name = TextField('First Name', [InputRequired('First name is required'),length(max=30)])
    last_name = TextField('Last Name', [InputRequired('Last name is required'),length(max=30)])
    gender = RadioField('Gender',[InputRequired('Please select your gender')], choices=[('Male', 'Male'),('Female','Female')])
    email = TextField('Email', [InputRequired('Email is required'),Email()])
    mobile = IntegerField('Mobile', [InputRequired('Please enter your hand mobile')]) #FormField(TelephoneForm)
    parent_mobile = StringField('Parent Mobile')
    password = PasswordField('Password', [InputRequired('Password is required.'), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', [InputRequired('Confirm password is required.')])
    school_name = TextField('School Name',[length(max=100)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    # email = StringField('Email', validators=[InputRequired()])
    mobile = StringField('Hand Phone', validators=[InputRequired()])
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