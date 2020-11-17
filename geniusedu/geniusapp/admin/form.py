from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, PasswordField,RadioField, BooleanField, SubmitField,TextField,\
TextAreaField,SelectField,IntegerField,DecimalField
from wtforms.validators import DataRequired, InputRequired,EqualTo
from geniusapp import db
from geniusapp.model.tables import Courses, Subjects
from flask_wtf.file import FileField, FileRequired, FileAllowed

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AdminResetPassForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[InputRequired(),EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired()])
    submit = SubmitField('Update Password')


class AddSubjects(FlaskForm):
    subject_name = TextField('Subject Name',[InputRequired()])
    submit = SubmitField('Add Subject')

class AddCourse(FlaskForm):
    course_name = TextField('Course Name',[InputRequired()])
    submit = SubmitField('Add Subject')

class CoursesMapperOld(FlaskForm):
    course_id = SelectField('Course Name', coerce=int  )
    subject_id = SelectField('Course Name', coerce=int)
    submit = SubmitField('Add Subject')


class CoursesMapper(FlaskForm):
    seo_title = TextField('Seo Title',[InputRequired()])
    course_id = SelectField('Package Name', coerce=int)
    cover_banner = FileField('Cover banner',[FileRequired(),FileAllowed(['jpg','png','jpeg'], 'Images only!')]) 
    description = TextAreaField('Write something about package')
    price = DecimalField('Price')
    is_crash_course = BooleanField('Is this crash course')
    discount_amt = IntegerField('Discount Amount')
    expire_month = SelectField('Expire Month',coerce=int)
    expire_year = IntegerField('Expire Year',[InputRequired()])
    submit = SubmitField('Create package')

class AddPackSubject(FlaskForm):
    comp_subject_id = SelectField('Comp Subject Name', coerce=int)
    comp_price = DecimalField('Price',[InputRequired()])
    opt_subject_id = SelectField('Opt Subject Name', coerce=int)
    opt_price = DecimalField('Price',[InputRequired()])
    submit = SubmitField('Add subjects')



class AddTeacher(FlaskForm):
    first_name = TextField('First Name', [InputRequired()])
    last_name = TextField('Last Name')
    gender = SelectField('Gender',[InputRequired()], choices=[('Male', 'Male'),('Female','Female')])
    email = TextField('Email', [InputRequired()])
    mobile = IntegerField('Mobile', [InputRequired()]) #FormField(TelephoneForm)
    parent_mobile = TextField('Parent Mobile')
    ic_number = TextField('IC Number')
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', [InputRequired()])
    zipcode = TextField('Zip Code')
    address = TextAreaField('Address')
    submit = SubmitField('Register')

class AddStudentForm(FlaskForm):
    first_name = TextField('First Name', [InputRequired()])
    last_name = TextField('Last Name')
    gender = SelectField('Gender', choices=[('','Choose Gender'),('Male', 'Male'),('Female','Female')])
    email = TextField('Email')
    mobile = TextField('Mobile', [InputRequired()])
    parent_mobile = TextField('Parent Mobile')
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    course_id = SelectField('Course Name', coerce=int)
    confirm = PasswordField('Confirm Password', [InputRequired()])
    zipcode = TextField('Zip Code')
    address = TextAreaField('Address')
    submit = SubmitField('Add Student')


class StudentResetPassForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[InputRequired(),EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired()])
    submit = SubmitField('Update Password')

class AssignTeacherCourse(FlaskForm):

    course_id = SelectField('Course Name', coerce=int)
    subject_id = SelectField('Subject Name', coerce=int)
    submit = SubmitField('Assign Course')

class AssignStudentCourse(FlaskForm):

    course_id = SelectField('Course Name', coerce=int)
    subject_id = SelectField('Subject Name', coerce=int)
    submit = SubmitField('Assign course')


class SeminarForm(FlaskForm):
    title = TextField('Title',[InputRequired()]) 
    description = TextAreaField('Write something about seminar')
    seminar_date = TextField('Seminar Date', [InputRequired()])
    cover_banner = FileField('Cover banner',[FileAllowed(['.jpg','.png','.jpeg'], 'Images only!')]) 
    price = DecimalField('Price')
    submit = SubmitField('Create seminar')



class ReferralSettingForm(FlaskForm):
    amount = DecimalField('Amount', [InputRequired()])
    dis_type = SelectField('Method', [InputRequired()],
                           choices=[('', 'Choose Method'), ('percent', 'Percentage'), ('amount', 'Amount')])
    submit = SubmitField('Update')