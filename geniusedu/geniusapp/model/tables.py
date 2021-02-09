from geniusapp import db,app
from flask_login import UserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

class User_roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_titile = db.Column(db.String(150), nullable=False, unique=True)
    privileges = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean,default=True)
    
    def __repr__(self):
        return self.role_titile


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150),nullable=True)
    gender = db.Column(db.String(50),nullable=True)
    email = db.Column(db.String(150),nullable=True)
    mobile = db.Column(db.BigInteger,unique=True,nullable=False) 
    parent_mobile = db.Column(db.BigInteger,nullable=True)
    password = db.Column(db.String(250),nullable=False)
    user_role_id = db.Column(db.Integer,db.ForeignKey(User_roles.id))
    user_roles = relationship("User_roles",lazy=True)
    ic_number = db.Column(db.String(100),nullable=True)
    zipcode = db.Column(db.Integer,nullable=True)
    address = db.Column(db.String(1000), nullable=True)
    user_type = db.Column(db.String(50),default='stu')
    register_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    online_register = db.Column(db.Boolean,default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_mobile_verified = db.Column(db.Boolean, default=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    forget_password_key = db.Column(db.String(150), nullable=True)
    referral_code = db.Column(db.String(250), nullable=True)

    def __init__(self, first_name, last_name,gender, email, password, mobile, parent_mobile, user_role_id, zipcode, address,online_register):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.gender=gender
        self.email  = email.lower()
        self.password = generate_password_hash(password)
        self.mobile = mobile
        self.parent_mobile = parent_mobile
        self.user_role_id = user_role_id
        self.zipcode = zipcode
        self.address = address
        self.online_register = online_register
        self.is_active = True 

    def __repr__(self):
        return self.first_name+' '+self.last_name

    def check_password(self, password):
        return  check_password_hash(self.password, password) 

class User_session_log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(Users.id))
    user_name = relationship("Users")
    ip = db.Column(db.String(150), nullable=True)
    devices = db.Column(db.String(250), nullable=True)
    login_date = db.Column(db.Date, default=datetime.datetime.utcnow)

    def __init__(self,user_id, ip, devices):
        self.user_id = user_id
        self.ip = ip
        self.devices = devices

class Subjects(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    subject_name = db.Column(db.String(65),nullable=False,unique=True)
    is_active = db.Column(db.Boolean,default=True)

    def __init__(self,subject_name):
        self.subject_name=subject_name

    def __repr__(self):
        return self.subject_name

class Courses(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    course_name = db.Column(db.String(100),unique=True)
    is_active = db.Column(db.Boolean,default=True)
    topics = db.Column(db.String)

    def __init__(self, course_name):
        self.course_name = course_name
    
    def __repr__(self):
        return self.course_name

class Courses_mapper(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey(Courses.id), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id), nullable=False)
    course_name = relationship("Courses")
    subject_name = relationship("Subjects")
    is_active = db.Column(db.Boolean,default=True)

    def __init__(self,course_id,subject_id):
        self.course_id = course_id
        self.subject_id = subject_id 



class Months(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    month_name = db.Column(db.String(60),nullable=False,unique=True)
    is_active = db.Column(db.Boolean,default=True)

    def __init__(self,month_name):
        self.month_name=month_name

    def __repr__(self):
        return self.month_name.title()

class Pac_course(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey(Courses.id), nullable=False)
    seo_title = db.Column(db.String(150),nullable=False)
    cano_url = db.Column(db.String(250),nullable=False)
    cover_banner = db.Column(db.String(150),nullable=True)
    description = db.Column(db.Text,nullable=True)
    price = db.Column(db.Float,default=0)
    is_crash_course = db.Column(db.Boolean, default=False)
    discount_amt = db.Column(db.Float, nullable=True)
    expire_month = db.Column(db.Integer,db.ForeignKey(Months.id), nullable=False)
    expire_year = db.Column(db.Integer,nullable=False)
    course_name = relationship("Courses")
    month_name = relationship("Months")
    is_active = db.Column(db.Boolean,default=True)
    create_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)

    def __init__(self,course_id,seo_title,cano_url,cover_banner,description,price,is_crash_course, discount_amt,expire_month,expire_year):
        self.course_id = course_id
        self.seo_title = seo_title
        self.cano_url = cano_url
        self.cover_banner = cover_banner
        self.description = description
        self.price = price
        self.is_crash_course = is_crash_course
        self.discount_amt = discount_amt
        self.expire_month = expire_month
        self.expire_year = expire_year

    def __repr__(self):
        return self.seo_title
    
    
class Pac_compulsory_subjects(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    pac_course_id =  db.Column(db.Integer, db.ForeignKey(Pac_course.id), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id), nullable=False)
    price = db.Column(db.Float)
    subject_name = relationship("Subjects")
    is_active = db.Column(db.Boolean,default=True)

    def __init__(self,pac_course_id,subject_id,price):
        self.pac_course_id = pac_course_id
        self.subject_id = subject_id
        self.price = price

class Pac_optional_subjects(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    pac_course_id =  db.Column(db.Integer, db.ForeignKey(Pac_course.id), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id), nullable=False)
    price = db.Column(db.Float)
    subject_name = relationship("Subjects")
    is_active = db.Column(db.Boolean,default=True)

    def __init__(self,pac_course_id,subject_id,price):
        self.pac_course_id = pac_course_id
        self.subject_id = subject_id
        self.price = price

class Student_subscribe_courses(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    ic_number = db.Column(db.String(150),nullable=True)
    user_id = db.Column(db.Integer,db.ForeignKey(Users.id))
    course_id = db.Column(db.Integer,db.ForeignKey(Courses.id))
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id))
    is_upgraded = db.Column(db.Boolean,default=False)
    course_assign_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False) 
    user_name = relationship("Users")
    course_name = relationship("Courses")
    subject_name = relationship("Subjects")

    def __init__(self,user_id,course_id,subject_id=subject_id):
        self.user_id=user_id
        self.course_id=course_id
        self.subject_id = subject_id

class Teacher_assing_course(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(Users.id))
    course_id = db.Column(db.Integer,db.ForeignKey(Courses.id))
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id))
    is_active = db.Column(db.Boolean, default=False)
    user_name = relationship("Users")
    subject_name = relationship("Subjects")
    course_name = relationship("Courses")

    def __init__(self,user_id,course_id,subject_id):
        self.user_id = user_id  
        self.course_id = course_id
        self.subject_id = subject_id

class Online_classes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(Users.id))
    course_id = db.Column(db.Integer,db.ForeignKey(Courses.id))
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id))
    class_title = db.Column(db.String(200),nullable=False)
    canonical_url = db.Column(db.String(350),nullable=False,unique=True)
    description = db.Column(db.Text,nullable=False)
    create_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean,default=True)
    is_complete = db.Column(db.Boolean, default=False)
    teacher_name = relationship("Users")
    course_name = relationship("Courses")
    subject_name = relationship("Subjects")

    def __init__(self,user_id,course_id,subject_id,class_title,canonical_url,description,create_date):
        self.user_id = user_id  
        self.course_id = course_id
        self.subject_id = subject_id
        self.class_title = class_title
        self.canonical_url = canonical_url
        self.description = description
        self.create_date = create_date
    
    def __repr__(self):
        return self.class_title

class Chat(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(25),nullable=False)
    online_class_id=db.Column(db.Integer,db.ForeignKey(Online_classes.id),nullable=False)
    sender_id = db.Column(db.Integer,db.ForeignKey(Users.id),nullable=False)
    receiver_id = db.Column(db.Integer,db.ForeignKey(Users.id),nullable=False)
    message =db.Column(db.String(155))

    def __repr__(self,user_id, online_class_id,sender_id,receiver_id,message):
        self.user_id = user_id
        self.online_class_id = online_class_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message = message


class Ban_chat_users(db.Model):

    id              = db.Column(db.Integer,primary_key=True)
    online_class_id = db.Column(db.Integer,db.ForeignKey(Online_classes.id),nullable=False)
    banned_user_id  = db.Column(db.Integer,db.ForeignKey(Users.id),nullable=False)
    teacher_id      = db.Column(db.Integer,db.ForeignKey(Users.id),nullable=False)
    reason          = db.Column(db.String(500), nullable=True)
    baned_date      = db.Column(db.Date, default=datetime.datetime.utcnow)
    is_active       = db.Column(db.Boolean, default=True)

    def __repr__(self,online_class_id,baned_user_id,teacher_id,any_reason,baned_date):
        self.online_class_id=online_class_id
        self.banned_user_id=banned_user_id
        self.teacher_id = teacher_id
        self.reason=reason

class Contact_us(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(45), nullable=True)
    email = db.Column(db.String(60), nullable=True)
    mobile = db.Column(db.String(12),nullable=True)
    subject = db.Column(db.String(50), nullable=True)
    message = db.Column(db.String(300), nullable=True)
    created_date = db.Column(db.Date, default=datetime.datetime.utcnow)

    def __repr__(self,name,email,mobile,subject,message):
        self.name       = name
        self.email      = email
        self.mobile     = mobile
        self.subject    = subject
        self.message    = messag

class Broadcast_classe_stream_records(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    live_class_id = db.Column(db.Integer, db.ForeignKey(Online_classes.id))
    member_id =  db.Column(db.Integer, db.ForeignKey(Users.id))
    stream_id = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    live_class_name = relationship("Online_classes")
    user_name = relationship("Users")

    def __init__(self, live_class_id,member_id,stream_id):
        self.live_class_id = live_class_id
        self.member_id = member_id
        self.stream_id = stream_id

class Student_select_course(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    course_id = db.Column(db.Integer)


class Student_attendence(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    topices_id = db.Column(db.Integer, db.ForeignKey(Online_classes.id))
    student_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    is_join = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, default=datetime.datetime.utcnow)
    topic_name = relationship("Online_classes")
    student_name = relationship("Users")

    def __init__(self,topices_id,student_id,is_join):
        self.topices_id = topices_id
        self.student_id = student_id
        self.is_join = is_join


class Online_demo_classes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(Users.id))
    course_id = db.Column(db.Integer,db.ForeignKey(Courses.id))
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id))
    class_title = db.Column(db.String(200),nullable=False)
    canonical_url = db.Column(db.String(350),nullable=False,unique=True)
    description = db.Column(db.Text,nullable=False)
    cover_banner =db.Column(db.String(150),nullable=True)
    create_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean,default=True)
    is_complete = db.Column(db.Boolean, default=False)
    is_start = db.Column(db.Boolean,default=False)
    user_name = relationship("Users")
    course_name = relationship("Courses")
    subject_name = relationship("Subjects")

    def __init__(self,user_id,course_id,subject_id,class_title,canonical_url,description,cover_banner,create_date):
        self.user_id = user_id  
        self.course_id = course_id
        self.subject_id = subject_id
        self.class_title = class_title
        self.canonical_url = canonical_url
        self.description = description
        self.cover_banner = cover_banner
        self.create_date = create_date
    
    def __repr__(self):
        return self.class_title


class Users_demo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(40),nullable=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150),nullable=True)
    gender = db.Column(db.String(50),nullable=True)
    email = db.Column(db.String(150),nullable=True)
    mobile = db.Column(db.BigInteger,unique=True,nullable=False) 
    password = db.Column(db.String(250),nullable=False)
    user_role_id = db.Column(db.Integer,db.ForeignKey(User_roles.id))
    user_roles = relationship("User_roles",lazy=True)
    register_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    used_for = db.Column(db.String(10),default='demo')
    
    
    def __init__(self, user_id, first_name, last_name,gender, email, password, mobile, user_role_id):
        self.user_id=user_id.lower()
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.gender=gender
        self.email  = email.lower()
        self.password = generate_password_hash(password)
        self.mobile = mobile
        self.user_role_id = user_role_id
        self.is_active = True 

    def __repr__(self):
        return self.first_name+' '+self.last_name

    def check_password(self, password):
        return  check_password_hash(self.password, password) 


class Demo_chat(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(25),nullable=False)
    online_class_id=db.Column(db.Integer,nullable=False)
    sender_id = db.Column(db.Integer,nullable=False)
    receiver_id = db.Column(db.Integer,nullable=False)
    message =db.Column(db.String(155))



class Broadcast_demo_classe_stream_records(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    live_class_id = db.Column(db.Integer)
    member_id =  db.Column(db.Integer)
    stream_id = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)



class Ban_chat_demo_users(db.Model):

    id              = db.Column(db.Integer,primary_key=True)
    online_class_id = db.Column(db.Integer,nullable=False)
    banned_user_id  = db.Column(db.Integer,nullable=False)
    teacher_id      = db.Column(db.Integer,nullable=False)
    reason          = db.Column(db.String(500), nullable=True)
    baned_date      = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active       = db.Column(db.Boolean, default=True)


class Demo_student_attendence(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    topices_id = db.Column(db.Integer, db.ForeignKey(Online_demo_classes.id))
    student_id = db.Column(db.Integer, db.ForeignKey(Users_demo.id))
    date = db.Column(db.Date, default=datetime.datetime.utcnow)
    topic_name = relationship("Online_demo_classes")
    student_name = relationship("Users_demo")

    def __init__(self,topices_id,student_id):
        self.topices_id = topices_id
        self.student_id = student_id


class Coupon(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    coupon_name = db.Column(db.String(150),nullable=True)
    cano_url = db.Column(db.String(250),nullable=True)
    discount_type = db.Column(db.String(50) ,default='percentage')
    discount_amount = db.Column(db.Float,nullable=True)
    discount_percentage = db.Column(db.Integer,nullable=True)
    coupon_valid_start_date = db.Column(db.Date,nullable=False)
    coupon_valid_end_date = db.Column(db.Date,nullable=False)
    is_active = db.Column(db.Boolean,default=True)

    def __init__(self,coupon_name,cano_url,discount_type,discount_amount,discount_percentage,coupon_valid_start_date,coupon_valid_end_date):
        self.coupon_name=coupon_name
        self.cano_url=cano_url
        self.discount_type=discount_type
        self.discount_amount=discount_amount
        self.discount_percentage=discount_percentage
        self.coupon_valid_start_date=coupon_valid_start_date
        self.coupon_valid_end_date=coupon_valid_end_date

    def __repr__(self):
        return self.coupon_name

class Student_package_subscription(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey(Users.id))
    package_id = db.Column(db.Integer, db.ForeignKey(Pac_course.id))
    total_amount = db.Column(db.Float, nullable=False)
    coupon_code = db.Column(db.Integer,db.ForeignKey(Coupon.id), nullable=True)
    discount_amount = db.Column(db.Float, default=0)
    total_payable_amount = db.Column(db.Float, nullable=False)
    transcation_id = db.Column(db.String(450),nullable=True)
    invoice = db.Column(db.String(250),nullable=True)
    receipt = db.Column(db.String(250),nullable=True)
    payment_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    payment_status = db.Column(db.Boolean,nullable=False)
    payment_mode = db.Column(db.String(50), default="online")
    subs_status = db.Column(db.Boolean, default=True)
    purpose = db.Column(db.Integer,default=1)
    is_expired = db.Column(db.Boolean,default=False)
    student_name = relationship("Users")
    package_name= relationship("Pac_course")
    coupon_name = relationship("Coupon")

    def __init__(self,student_id,package_id,total_amount,coupon_code,discount_amount,total_payable_amount,transcation_id,invoice,receipt,payment_status,payment_mode,subs_status,purpose):
        self.student_id=student_id
        self.package_id=package_id
        self.total_amount=total_amount
        self.coupon_code=coupon_code
        self.discount_amount=discount_amount
        self.total_payable_amount=total_payable_amount
        self.transcation_id=transcation_id
        self.invoice = invoice
        self.receipt=receipt
        self.payment_status=payment_status
        self.payment_mode=payment_mode
        self.subs_status=subs_status
        self.purpose=purpose

class Subscription_trans_log(db.Model):

    id  = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    package_id = db.Column(db.Integer, db.ForeignKey(Pac_course.id))
    total_amount = db.Column(db.Float, nullable=False)
    coupon_code = db.Column(db.Integer,db.ForeignKey(Coupon.id), nullable=True)
    discount_amount = db.Column(db.Float, default=0)
    total_payable_amount = db.Column(db.Float, nullable=False)
    transcation_id = db.Column(db.String(450),nullable=True)
    invoice = db.Column(db.String(250),nullable=True)
    receipt = db.Column(db.String(250), nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    payment_mode = db.Column(db.String(50), default="online")
    purpose = db.Column(db.String(250),nullable=True)
    student_name = relationship("Users")
    package_name= relationship("Pac_course")
    coupon_name = relationship("Coupon")

    def __init__(self,student_id,package_id,total_amount,coupon_code,discount_amount,total_payable_amount,transcation_id,invoice,receipt,payment_mode,purpose):
        self.student_id=student_id
        self.package_id=package_id
        self.total_amount=total_amount
        self.coupon_code=coupon_code
        self.discount_amount=discount_amount
        self.total_payable_amount=total_payable_amount
        self.transcation_id=transcation_id
        self.invoice=invoice
        self.receipt=receipt 
        self.payment_mode = payment_mode
        self.purpose = purpose


class Student_subs_pac_optional(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    stu_pac_subs_id = db.Column(db.Integer, db.ForeignKey(Student_package_subscription.id))
    optional_subs = db.Column(db.Integer,db.ForeignKey(Pac_optional_subjects.id))
    
    def __inti__(self,stu_pac_subs_id, optional_subs):
        self.stu_pac_subs_id = stu_pac_subs_id
        self.optional_subs = optional_subs

class Student_subs_pac_months(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    stu_pac_subs_id = db.Column(db.Integer, db.ForeignKey(Student_package_subscription.id))
    subs_month = db.Column(db.Integer,db.ForeignKey(Months.id))
    month_name = relationship('Months')
    
    def __inti__(self,stu_pac_subs_id,subs_month):
        self.stu_pac_subs_id = stu_pac_subs_id
        self.subs_month = subs_month

class School_details(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    school_name = db.Column(db.String(150),nullable=True)
    student_name = relationship('Users')

    def __inti__(self,student_id,school_name):
        self.student_id = student_id
        self.school_name = school_name

    def __repr__(self):
        return self.school_name



class Seminars(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(150),nullable=False)
    canonical_url = db.Column(db.String(250),nullable=True)
    description = db.Column(db.String(1000),nullable=True)
    price = db.Column(db.Float)
    seminar_date = db.Column(db.DateTime,nullable=False)
    cover_banner = db.Column(db.String(250),nullable=True)
    is_active = db.Column(db.Boolean,default=True)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, title, canonical_url, description,price, seminar_date,cover_banner):
        self.title = title
        self.canonical_url = canonical_url
        self.description = description
        self.price = price
        self.seminar_date = seminar_date
        self.cover_banner = cover_banner

    def __repr__(self):
        return self.title.title()
    

class Seminar_details(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    seminar_id = db.Column(db.Integer, db.ForeignKey(Seminars.id))
    course_id = db.Column(db.Integer, db.ForeignKey(Courses.id))
    subject_id = db.Column(db.Integer, db.ForeignKey(Subjects.id))
    teacher_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    topic_titile = db.Column(db.String(250), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    course_name = relationship('Courses')
    subject_name = relationship("Subjects")
    teacher_name = relationship("Users")
    
    def __init__(self, seminar_id, course_id, subject_id, teacher_id, topic_titile, start_time, end_time):
        self.seminar_id = seminar_id
        self.course_id = course_id
        self.subject_id = subject_id
        self.teacher_id = teacher_id
        self.topic_titile = topic_titile
        self.start_time = start_time
        self.end_time = end_time



class Seminar_attend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seminar_id = db.Column(db.Integer, db.ForeignKey(Seminars.id))
    student_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    join_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    is_free = db.Column(db.Boolean,default=True)
    price = db.Column(db.Float,nullable=True)
    payment_method = db.Column(db.String(50))
    receipt = db.Column(db.String(250),nullable=True)
    invoice = db.Column(db.String(250),nullable=True)
    transcation_id = db.Column(db.String(450),nullable=True)
    payment_status = db.Column(db.Boolean,default=False)
    activated_from_dash = db.Column(db.Boolean,default=False)
    is_approved = db.Column(db.Boolean,default=False)
    seminar_name = relationship("Seminars")
    student_name = relationship("Users")

    def __init__(self, seminar_id, student_id, is_free,price):
        self.seminar_id = seminar_id
        self.student_id = student_id
        self.is_free = is_free
        self.price = price

""" seminar boradcast """

class Sem_broad_streams_records(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seminar_id = db.Column(db.Integer, db.ForeignKey(Seminars.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Users.id),  nullable=False)
    stream_id = db.Column(db.String(250), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    seminar_name = relationship("Seminars")
    teacher_name = relationship("Users")

    def __init__(self, seminar_id, teacher_id, stream_id):
        self.seminar_id = seminar_id
        self.teacher_id = teacher_id
        self.stream_id = stream_id



class Sem_chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seminar_id = db.Column(db.Integer, db.ForeignKey(Seminars.id), nullable=False)
    user_id = db.Column(db.String(150), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    message = db.Column(db.String(350), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, seminar_id, user_id, sender_id,receiver_id,message):
        self.seminar_id = seminar_id
        self.user_id = user_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message = message


class Ban_sem_chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seminar_id = db.Column(db.Integer, db.ForeignKey(Seminars.id), nullable=False)
    banned_user_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    reason =  db.Column(db.String(350), nullable=True)
    banned_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    seminar_name = relationship("Seminars")

    def __init__(self, seminar_id, banned_user_id, teacher_id, reason):
        self.seminar_id = seminar_id
        self.banned_user_id = banned_user_id
        self.teacher_id = teacher_id
        self.reason = reason

class Seminar_start_teachers(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    seminar_id = db.Column(db.Integer, db.ForeignKey(Seminars.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, seminar_id, teacher_id):
        self.seminar_id = seminar_id
        self.teacher_id = teacher_id



class Referral_program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_referral_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    registered_user_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    registered_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_used =  db.Column(db.Boolean, default=False)
    used_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, user_referral_id, registered_user_id):
        self.user_referral_id = user_referral_id
        self.registered_user_id = registered_user_id


class Wallet(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id,onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float,default=0)
    last_update_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    user_name = relationship("Users")

    def __init__(self,user_id,amount):
        self.user_id = user_id
        self.amount = amount

class Wallet_trans_log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id, onupdate='CASCADE', ondelete='CASCADE'))
    amount = db.Column(db.Float,default=0)
    action = db.Column(db.String(50),default='')
    description = db.Column(db.String(1000))
    create_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_name = relationship("Users")

    def __init__(self,user_id,amount,action,description):
        self.user_id=user_id
        self.amount=amount
        self.action=action
        self.description=description


class Referral_setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    dis_type = db.Column(db.String(150))


class Wallet_withdrawal_request(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id, onupdate='CASCADE', ondelete='CASCADE'))
    amount = db.Column(db.Float, default=0)
    message = db.Column(db.String(1000), nullable=True)
    request_date = db.Column(db.DateTime, default= datetime.datetime.utcnow)
    approve_date = db.Column(db.DateTime, nullable=True)
    is_approved = db.Column(db.Boolean, default= False)
    user_name = relationship("Users")

    def __init__(self, user_id, amount):
        self.user_id = user_id
        self.amount = amount