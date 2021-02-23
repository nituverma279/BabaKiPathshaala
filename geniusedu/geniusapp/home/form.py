from flask_wtf import FlaskForm,RecaptchaField
from wtforms import  SubmitField,TextField,TextAreaField,IntegerField
from wtforms.validators import InputRequired,Email,length


class ContactForm(FlaskForm):
    name = TextField('Name', [InputRequired(),length(max=30)])
    email = TextField('Email', [InputRequired(),Email(),length(max=80)])
    subject = TextField('Subject', [InputRequired(),length(max=50)])
    message = TextAreaField('Message',[InputRequired(),length(max=1000)])
    submit = SubmitField('Send')
 