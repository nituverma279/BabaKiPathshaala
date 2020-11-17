from flask_wtf import FlaskForm,RecaptchaField
from wtforms import StringField, PasswordField,RadioField, BooleanField, SubmitField,TextField,TextAreaField,SelectField,IntegerField
from wtforms.validators import DataRequired, InputRequired,EqualTo,Email,length



class StudentSelectCourse(FlaskForm):
    course_id = RadioField('Course Name',[InputRequired()], coerce=int)
    ic_number = TextField('IC Number',[InputRequired()])
    submit = SubmitField('subscribe Course')

 